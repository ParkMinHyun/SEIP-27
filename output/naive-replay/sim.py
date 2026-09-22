"""Part B: closed-loop ADMISSION replay with capture arrivals pinned to the
recorded trace (so the recorded pacing delays are frozen into every arm).

Every arm runs the same single-FIFO draft worker, the same sticky group
demotion that resets when the draft queue drains, and the same stage
durations; only the estimator inside the admission test differs.
  FACT    recorded effective admits (mechanics check: must reproduce the trace)
  DEP     ported DraftSequenceExecutionPredictor, admit iff P==0 or U<=T
  DEP_P   same model, point estimate only: admit iff P==0 or P<=T
  NAIVE   statistic of the last N completed draft walls in the run, minus the
          time already spent in the current draft; admit iff no history or <=T
  ALWAYS  admit every optional stage
Stage durations: recorded when the stage ran in the trace, otherwise imputed
from the nearest executed capture of the same stage in the same run.
"""
import pickle, os, sys, math, random
import numpy as np, pandas as pd
from port import Predictor, load_nodes, parse_seq, OPTIONAL, GROUP

HERE = os.path.dirname(os.path.abspath(__file__))
IDLE_GAP = 60.0


def tf(v):
    return str(v).strip().lower() in ('true', '1', '1.0', 'yes')


def prepare(x, lead_mode):
    N = load_nodes(x)
    t = x['CaseStudyTrace'].copy()
    runs = x['RQ1Runs']
    t['runStatus'] = t.runId.map(dict(zip(runs.runId, runs.runStatus)))
    t = t[t.runStatus.eq('COMPLETE_30')]
    sid = dict(zip(x['Capture'].captureIndex, x['Capture'].pacerSessionId))
    t['req'] = t.timeoutDeadlineUptimeMs - t.captureTimeoutMs
    t = t.sort_values(['runId', 'runShotIndex'])
    t['prevEnd'] = t.groupby('runId').draftEndUptimeMs.shift()
    t['gap'] = t.draftStartUptimeMs - t.prevEnd
    idle = t[(t.gap > IDLE_GAP) | t.prevEnd.isna()]
    lead_p5 = float((idle.draftStartUptimeMs - idle.req).quantile(0.05))
    busy_gap = float(t[t.gap <= IDLE_GAP].gap.median())
    byc = {c: g for c, g in N.groupby('captureIndex')}
    out = {}
    for run, g in t.groupby('runId'):
        caps = []
        for _, r in g.iterrows():
            nodes = byc[r.captureIndex].sort_values('nodeOrder')
            ds = r.draftStartUptimeMs
            acc, lst = 0.0, []
            last_end = ds
            for _, n in nodes.iterrows():
                d = float(n.durationMs) if pd.notna(n.durationMs) and n.durationMs > 0 else None
                pre = (n.nodeStartUptimeMs - ds) - acc
                lst.append(dict(key=n.workloadKey, fdur=d, pre=pre, fadmit=tf(n.admit),
                                seq=parse_seq(n.workloadSequenceKey)))
                acc += (d or 0.0)
                last_end = max(last_end, n.nodeStartUptimeMs + (d or 0.0))
            post = (r.draftEndUptimeMs - ds) - acc   # all non-node time in the draft
            busy = pd.notna(r.gap) and r.gap <= IDLE_GAP
            if not busy:
                ready = r.draftStartUptimeMs
            elif lead_mode == 'early':
                ready = min(r.draftStartUptimeMs - r.gap, r.req + lead_p5)
            else:  # 'late': never earlier than the recorded start allowed
                ready = r.draftStartUptimeMs - r.gap
            caps.append(dict(cap=r.captureIndex, shot=r.runShotIndex, req=r.req,
                             D=r.timeoutDeadlineUptimeMs, fstart=ds, fend=r.draftEndUptimeMs,
                             gap=(r.gap if busy else busy_gap), ready=ready, post=post, nodes=lst,
                             level=r.shotOverheatLevel, fmargin=r.timeoutMarginMs,
                             sid=sid.get(r.captureIndex)))
        # configured sequence = keys of the node list (full planned chain)
        # imputation tables
        ex = {}
        for c in caps:
            for n in c['nodes']:
                if n['fdur']:
                    ex.setdefault(n['key'], []).append((c['shot'], n['fdur']))
        out[run] = dict(caps=caps, ex=ex)
    return out, lead_p5, busy_gap


def impute(ex, key, shot, rng=None, k=5):
    lst = ex.get(key)
    if not lst:
        return None
    srt = sorted(lst, key=lambda v: (abs(v[0] - shot), v[0] > shot))
    if rng is None:
        return srt[0][1]
    if rng == 'min5':
        return min(v[1] for v in srt[:k])
    if rng == 'med5':
        return float(np.median([v[1] for v in srt[:k]]))
    return rng.choice(srt[:k])[1]


class Sticky:
    def __init__(self):
        self.g = {}

    def reset(self):
        self.g = {}

    def demoted(self, key):
        grp = GROUP.get(key)
        return grp is not None and self.g.get(grp) == 'D'

    def admit(self, key, model_admit):
        if self.demoted(key):
            return False
        grp = GROUP.get(key)
        if grp is not None:
            if model_admit:
                self.g.setdefault(grp, 'R')
            else:
                self.g[grp] = 'D'
        return model_admit

    def resolve(self, seq):
        if 'D' not in self.g.values():
            return seq
        r = tuple(k for k in seq if not self.demoted(k))
        return r if r else seq


def run_arm(prep, arm, N=3, stat='mean', margin=0.0, rng=None, ovh=False, scale=1.0, log=None):
    rows = []
    for run, R in prep.items():
        caps, ex = R['caps'], R['ex']
        pr = Predictor()
        sh = Predictor() if log is not None else None   # shadow: deployed model on this arm's own trajectory
        pol = Sticky()
        walls = []   # (end, wall)
        stage_hist = {}  # key -> [(end, dur)] per executed occurrence
        ovh_hist = []    # (end, non-node time of the draft)
        prev_end = None
        cur_sid = None
        for i, c in enumerate(caps):
            if pd.notna(c['sid']):
                if cur_sid is not None and c['sid'] != cur_sid:
                    pol.reset()
                cur_sid = c['sid']
            start = c['ready'] if prev_end is None else max(c['ready'], prev_end + c['gap'])
            if arm == 'FACT':
                start = c['fstart'] if prev_end is None else max(c['ready'], prev_end + c['gap'])
            cum = 0.0
            decisions = {}
            durs = {}
            executed = {}
            adm_log = []
            comp_so_far = []
            node_durs = []
            sh_dec = {}
            pend = []
            full_seq = tuple(n['key'] for n in c['nodes'])
            for j, n in enumerate(c['nodes']):
                t_node = start + n['pre'] + cum
                T = c['D'] - t_node
                key = n['key']
                seq = pol.resolve(full_seq[j:])
                fc = np.nan
                if sh is not None:
                    sP, sU, spm = sh.decide(seq)
                    sh_dec[seq] = spm
                    if seq[0] in OPTIONAL:
                        rsv = tuple(k for k in seq if k.startswith('ENCODING'))
                        if rsv:
                            sh_dec[rsv] = sh.decide(rsv)[2]
                if arm in ('DEP', 'DEP_P'):
                    P, U, pm = pr.decide(seq)
                    decisions[seq] = pm
                    head_opt = seq[0] in OPTIONAL
                    if head_opt:
                        rsv = tuple(k for k in seq if k.startswith('ENCODING'))
                        if rsv:
                            _, _, pm2 = pr.decide(rsv)
                            decisions[rsv] = pm2
                        m_adm = (P <= 0) or ((U if arm == 'DEP' else P) <= T)
                    else:
                        m_adm = True
                elif arm in ('NAIVE', 'NAIVE_C'):
                    if key in OPTIONAL:
                        hist = [w for e, w, cp in walls if e <= t_node][-N:]
                        if arm == 'NAIVE_C':
                            target = tuple(comp_so_far) + tuple(k for k in pol.resolve(full_seq[j:]) if not pol.demoted(k))
                            hc = [w for e, w, cp in walls if e <= t_node and cp == target][-N:]
                            if hc:
                                hist = hc
                        if not hist:
                            m_adm = True
                        else:
                            s = np.mean(hist) if stat == 'mean' else max(hist)
                            fc = s + margin - (t_node - start)
                            m_adm = fc <= T
                    else:
                        m_adm = True
                elif arm == 'STAGE':
                    if key in OPTIONAL:
                        def est(k):
                            h = [d_ for e_, d_ in stage_hist.get(k, []) if e_ <= t_node][-N:]
                            if not h:
                                return 0.0
                            return float(np.mean(h)) if stat == 'mean' else float(max(h))
                        rem = pol.resolve(full_seq[j:])
                        f = sum(est(k) for k in rem)
                        if f <= 0:
                            m_adm = True
                        else:
                            if ovh:
                                oh = [o for e_, o in ovh_hist if e_ <= t_node][-N:]
                                f += float(np.mean(oh)) if oh else 0.0
                            fc = f * scale + margin
                            m_adm = fc <= T
                    else:
                        m_adm = True
                elif arm == 'ALWAYS':
                    m_adm = True
                elif arm == 'FACT':
                    m_adm = n['fadmit'] if key in OPTIONAL else True
                was_demoted = pol.demoted(key)
                if key in OPTIONAL:
                    adm = pol.admit(key, m_adm) if arm != 'FACT' else m_adm
                else:
                    adm = True
                if adm and key in OPTIONAL:
                    adm_log.append((key, j, T))
                if sh is not None and key in OPTIONAL:
                    pend.append(dict(run=run, shot=c['shot'], key=key[:6], T=T, f=fc, sP=sP, sU=sU, adm=adm,
                                     sticky=was_demoted, t_node=t_node))
                if adm:
                    d = n['fdur']
                    if d is None and not n['fadmit'] and key in OPTIONAL:
                        d = impute(ex, key, c['shot'], rng)
                    d = d or 0.0
                else:
                    d = 0.0
                executed[key] = executed.get(key, False) or (adm and d > 0)
                if d > 0:
                    durs[key] = int(round(d))
                    node_durs.append((key, d))
                if adm:
                    comp_so_far.append(key)
                cum += d
            end = start + c['post'] + cum
            wall = end - start
            if arm in ('DEP', 'DEP_P'):
                pr.learn(durs, list(decisions.items()))
            if sh is not None:
                sh.learn(durs, list(sh_dec.items()))
                for r_ in pend:
                    r_['G'] = end - r_['t_node']; r_['margin'] = c['D'] - end
                    log.append(r_)
            walls.append((end, wall, tuple(comp_so_far)))
            for k_, d_ in node_durs:
                stage_hist.setdefault(k_, []).append((end, d_))
            ovh_hist.append((end, c['post']))
            prev_end = end
            rows.append(dict(run=run, shot=c['shot'], cap=c['cap'], level=c['level'],
                             margin=c['D'] - end, fmargin=c['fmargin'], end=end, fend=c['fend'],
                             bokeh=executed.get('BOKEH()', False), filt=executed.get('FILTER()', False),
                             adm_keys='|'.join(k[:6] for k, _, _ in adm_log),
                             last_adm_T=(adm_log[-1][2] if adm_log else np.nan),
                             last_adm_key=(adm_log[-1][0][:6] if adm_log else ''),
                             wait=start - c['req']))
    return pd.DataFrame(rows)
