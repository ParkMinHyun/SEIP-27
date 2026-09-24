"""Part C, stage-wise naive as a pacing input.

The draft-unit arms in partC_pacing_arms.py take a statistic of whole draft
sequence durations.  This script builds the same per-draft quantity the
stage-wise admission arm uses -- the sum over the sequence's stages of a
statistic of each stage's last N observed durations -- and feeds it to
eq:pacing as the backlog and reserve input, exactly as the draft-unit arms do.

Two construction choices are swept, because a stage sum is not a draft wall:
  chain   'planned'  = the decision capture's configured stage chain
          'executed' = the executed composition of the newest completed draft
  ovh     add the recent-N mean of non-stage time in a draft (the stage sum
          alone cannot see it; a draft-unit statistic includes it for free)

Same one-step open-loop swap as partC_pacing_arms.py: arrivals, realized
durations and the recorded delays stay pinned to the trace.

    python partC_pacing_stage.py   -> results/C_pacing_stage.csv
"""
import os, pickle
import numpy as np, pandas as pd
from port import load_nodes, parse_seq

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results', 'C_pacing_stage.csv')
W = pickle.load(open(os.path.join(HERE, 'wb.pkl'), 'rb'))
NS = (1, 3, 5, 10)
rule = lambda B, C, T: np.ceil(np.maximum(0, B + 2 * C - np.maximum(T, 0)) / 2)


def tf(s):
    return s.astype(str).str.strip().str.lower().isin(['true', '1', '1.0', 'yes'])


def stat_of(vals, stat):
    return float(np.mean(vals)) if stat == 'mean' else float(np.max(vals))


ARMS = []
for stat, Ns in (('mean', NS), ('max', (3, 5, 10))):
    for N in Ns:
        for chain in ('planned', 'executed'):
            for ovh in (False, True):
                ARMS.append((stat, N, chain, ovh))
# draft-unit arms recomputed here so the whole table shares one population
DARMS = [('mean', N) for N in NS] + [('max', N) for N in (3, 5, 10)]

rows = []
for (dev, cond), x in W.items():
    t = x['CaseStudyTrace'].copy()
    runs = x['RQ1Runs']
    t['runStatus'] = t.runId.map(dict(zip(runs.runId, runs.runStatus)))
    t = t[t.runStatus.ne('CAPTURE_TIMEOUT')].copy()
    t['dur'] = t.draftSequenceDurationMs.astype(float)
    t = t.sort_values(['runId', 'runShotIndex'])
    N_nodes = load_nodes(x)
    byc = {c: g.sort_values('nodeOrder') for c, g in N_nodes.groupby('captureIndex')}

    for run, g in t.groupby('runId'):
        caps = []
        for _, r in g.iterrows():
            nd = byc.get(r.captureIndex)
            if nd is None:
                caps.append(None)
                continue
            durs = [(n.workloadKey, float(n.durationMs) if pd.notna(n.durationMs) and n.durationMs > 0 else 0.0)
                    for _, n in nd.iterrows()]
            acc = sum(d for _, d in durs)
            caps.append(dict(cap=r.captureIndex, shot=r.runShotIndex,
                             fstart=float(r.draftStartUptimeMs), fend=float(r.draftEndUptimeMs),
                             dur=float(r.dur), durs=durs,
                             planned=tuple(k for k, _ in durs),
                             executed=tuple(k for k, d in durs if d > 0),
                             post=float(r.draftEndUptimeMs - r.draftStartUptimeMs) - acc))
        caps = [c for c in caps if c is not None]
        if not caps:
            continue
        # completion-ordered history
        done = sorted(caps, key=lambda c: c['fend'])
        ends = np.array([c['fend'] for c in done])
        hist = {}                       # stage key -> list of durations in completion order
        hist_at = {}                    # stage key -> list of the index in `done` it was appended at
        for i, c in enumerate(done):
            for k, d in c['durs']:
                if d > 0:
                    hist.setdefault(k, []).append(d)
                    hist_at.setdefault(k, []).append(i)
        posts = np.array([c['post'] for c in done])

        gi = g.set_index('captureIndex')
        p = g[tf(g.pacingDecisionRecorded) & g.decisionUptimeMs.notna()]
        for _, r in p.iterrows():
            t_dec = float(r.decisionUptimeMs)
            ndone = int(np.searchsorted(ends, t_dec, side='right'))   # drafts completed at/before t_dec
            if ndone == 0:
                continue
            earlier = [c for c in caps if c['cap'] < r.captureIndex and c['fend'] > t_dec]
            B_true = max((c['fend'] for c in earlier), default=t_dec) - t_dec
            nxt = [c for c in caps if r.captureIndex <= c['cap'] <= r.captureIndex + 1]
            two = sum(c['dur'] for c in nxt) if len(nxt) == 2 else np.nan
            me = gi.loc[r.captureIndex]
            chains = dict(planned=byc[r.captureIndex].workloadKey.tolist(),
                          executed=list(done[ndone - 1]['executed']))
            rec = dict(dev=dev, cond=cond, run=run, cap=r.captureIndex, shot=r.runShotIndex,
                       T=float(r.timeToDeadlineMs), B_true=B_true, two_true=two,
                       B_dep=float(r.controllerBacklogMs), C_dep=float(r.draftSequenceReservedDurationMs),
                       d_app=float(r.appliedDelayMs), ndone=ndone)
            for stat, n, chain, ovh in ARMS:
                miss = 0
                m = 0.0
                for k in chains[chain]:
                    idx = hist_at.get(k)
                    if not idx:
                        miss += 1
                        continue
                    cut = int(np.searchsorted(idx, ndone - 1, side='right'))
                    if cut == 0:
                        miss += 1
                        continue
                    m += stat_of(hist[k][max(0, cut - n):cut], stat)
                if ovh:
                    m += stat_of(posts[max(0, ndone - n):ndone], stat)
                B = 0.0
                for c in earlier:
                    B += max(0.0, m - (t_dec - c['fstart'])) if c['fstart'] <= t_dec else m
                tag = f'st_{stat}{n}' + ('+ovh' if ovh else '') + ('' if chain == 'planned' else '@exec')
                rec[f'B|{tag}'] = B
                rec[f'C|{tag}'] = m
                rec[f'miss|{tag}'] = miss
            walls = [c['dur'] for c in done[:ndone]]
            for stat, n in DARMS:
                m = stat_of(walls[max(0, ndone - n):ndone], stat)
                B = 0.0
                for c in earlier:
                    B += max(0.0, m - (t_dec - c['fstart'])) if c['fstart'] <= t_dec else m
                tag = f'dr_{stat}{n}'
                rec[f'B|{tag}'] = B
                rec[f'C|{tag}'] = m
                rec[f'miss|{tag}'] = 0
            rows.append(rec)

D = pd.DataFrame(rows)
D = D.dropna(subset=['two_true', 'T', 'B_dep', 'C_dep']).copy()
D['d_ref'] = rule(D.B_true, D.two_true / 2, D['T'])
print('decisions', len(D), D.groupby('cond').size().to_dict())

out = []
for cond, d in D.groupby('cond'):
    runs_n = d.groupby(['dev', 'run']).ngroups   # runIds repeat across devices
    need = d.d_ref > 0
    tags = [('current', 'B_dep', 'C_dep')]
    tags += [(f'dr_{s}{n}', None, None) for s, n in DARMS]
    tags += [(f'st_{s}{n}' + ('+ovh' if o else '') + ('' if c == 'planned' else '@exec'), None, None)
             for s, n, c, o in ARMS]
    for tag, bc, cc in tags:
        bcol, ccol = (bc, cc) if bc else (f'B|{tag}', f'C|{tag}')
        x = rule(d[bcol], d[ccol], d['T'])
        pos = x[x > 0]
        berr = d[bcol] - d.B_true
        out.append(dict(
            cond=cond, arm=tag, n=len(d), runs=runs_n,
            engaged_pct=100 * (x > 0).mean(), delay_s_per_run=x.sum() / 1000 / runs_n,
            ref_engaged=int(need.sum()),
            engage_agree_recorded_pct=100 * ((x > 0) == (d.d_app > 0)).mean(),
            recorded_delay_s_per_run=d.d_app.sum() / 1000 / runs_n,
            pos_median_ms=pos.median() if len(pos) else 0,
            not_engaged_pct=100 * ((x == 0) & need).sum() / need.sum(),
            engaged_when_ref_did_not=int(((x > 0) & ~need).sum()),
            excess_s=np.maximum(0, x - d.d_ref).sum() / 1000,
            shortfall_s=np.maximum(0, d.d_ref - x).sum() / 1000,
            backlog_err_median_ms=berr.median(), backlog_cover_pct=100 * (berr >= 0).mean(),
            reserve_median_ms=d[ccol].median(),
            reserve_pctile_vs_realized=100 * (d[ccol] > d.two_true / 2).mean(),
            stages_without_history=(d[f'miss|{tag}'].mean() if bc is None else np.nan),
        ))
R = pd.DataFrame(out)
R.to_csv(OUT, index=False)
pd.set_option('display.width', 250)
print(R.round(1).to_string(index=False))
print('\nwrote', OUT)

# ---------------------------------------------------------------- B x C factorial
# B is a measurement, C a reservation, so a naive controller gets the chance to
# pick each separately: B from the draft or the stage unit (mean-3), C from
# either unit as a mean-3 or a max-N.  Same one-step swap, same population.
FAC_OUT = os.path.join(HERE, 'results', 'C_pacing_factorial.csv')
B_OPTS = [('draft', 'dr_mean3'), ('stage', 'st_mean3')]
C_OPTS = [('draft mean-3', 'dr_mean3'), ('stage mean-3', 'st_mean3')]
C_OPTS += [(f'draft max-{n}', f'dr_max{n}') for n in (3, 5, 10)]
C_OPTS += [(f'stage max-{n}', f'st_max{n}') for n in (3, 5, 10)]
fac = []
for cond, d in D.groupby('cond'):
    runs_n = d.groupby(['dev', 'run']).ngroups
    need = d.d_ref > 0
    cur = rule(d.B_dep, d.C_dep, d['T'])
    fac.append(dict(cond=cond, B='current', C='current', engaged_pct=100 * (cur > 0).mean(),
                    delay_s_per_run=cur.sum() / 1000 / runs_n,
                    not_engaged_pct=100 * ((cur == 0) & need).sum() / need.sum(),
                    reserve_cover_pct=100 * (d.C_dep > d.two_true / 2).mean(),
                    backlog_err_median_ms=(d.B_dep - d.B_true).median()))
    for bl, bt in B_OPTS:
        for cl, ct in C_OPTS:
            x = rule(d[f'B|{bt}'], d[f'C|{ct}'], d['T'])
            fac.append(dict(cond=cond, B=bl, C=cl, engaged_pct=100 * (x > 0).mean(),
                            delay_s_per_run=x.sum() / 1000 / runs_n,
                            not_engaged_pct=100 * ((x == 0) & need).sum() / need.sum(),
                            reserve_cover_pct=100 * (d[f'C|{ct}'] > d.two_true / 2).mean(),
                            backlog_err_median_ms=(d[f'B|{bt}'] - d.B_true).median()))
F = pd.DataFrame(fac)
F.to_csv(FAC_OUT, index=False)
print(F.round(2).to_string(index=False))
print('wrote', FAC_OUT)
