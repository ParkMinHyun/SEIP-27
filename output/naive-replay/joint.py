"""Joint closed-loop replay: admission and pacing estimators swapped separately or together.

STATUS: built, not usable for results.  The mechanics reproduce the recorded
trace (recorded delays + recorded admits: starts/ends within 7 ms, margins
exact), but with the deployed pacer deciding for itself the baseline breaks
(12MP misses 3 / 15 against 0 / 0 recorded).  The cause is draft readiness for
captures that queued in the trace, which is only bounded from above; see the
README section "Joint closed-loop replay".

Arrival model.  The ADB loop presses the shutter as soon as captureAvailable
arrives (4_1_setup.tex), and the trace shows the chain directly:

    req_j --L_j--> callback --d--> release --eps_j--> req_{j+1}

L_j (request to next callback) and eps_j (release to next request) are
camera/app latencies recorded per transition; in 12MP normal they are tight
(L: 235-296 / 200-247 ms, eps: 266-442 / 132-340 ms, p10-p90, S26U / S26), the
request after a release is always the very next capture, and each transition
carries one recorded callback or none (session bootstrap).  d is the pacer's
delay.  With the recorded delay the chain reproduces every recorded request.

Draft side, as sim.py: one FIFO worker, sticky group demotion, recorded stage
durations (imputed from the nearest executed capture when a stage was skipped),
recorded non-stage time.  A capture's draft becomes ready `lead` after its
request; for drafts that queued in the trace only an upper bound is observed,
so `lead_mode` late takes that bound and early caps it at the device's p5 idle
lead, the same bracket sim.py uses.

Pacing session: `session='pin'` ends it at the end of the draft that ended it
in the trace (recorded pacerSessionId), with the sticky demotion state reset on
the same drain; `'drain'` uses the simulator's own queue instead and finds far
fewer mid-run drains than were recorded on S26U.  Deadline: `lag='pin'` uses
the capture deadline each recorded decision actually priced against (a
camera-side race); an integer lag registers deadlines that many captures late.
"""
import heapq, os, pickle, sys
import numpy as np, pandas as pd
from port import Predictor, load_nodes, parse_seq, OPTIONAL
from port_pacer import (PacingEstimator, Pacer, PacingSession, Decision,
                        compute_pacing_delay_ms)
from sim import Sticky, impute, tf

HERE = os.path.dirname(os.path.abspath(__file__))
IDLE_GAP = 60.0
HALVE = {('S26U', '12MP'): True, ('S26', '12MP'): True,
         ('S26U', '24MP'): True, ('S26', '24MP'): False}
RESERVE = {('S26U', '12MP'): 'max', ('S26', '12MP'): 'expmax',
           ('S26U', '24MP'): 'max', ('S26', '24MP'): 'max'}


# ----------------------------------------------------------------------------- prep
def prepare(x):
    sid = dict(zip(x['Capture'].captureIndex, x['Capture'].pacerSessionId))
    N = load_nodes(x)
    byc = {c: g.sort_values('nodeOrder') for c, g in N.groupby('captureIndex')}
    t = x['CaseStudyTrace'].copy()
    runs = x['RQ1Runs']
    t['st'] = t.runId.map(dict(zip(runs.runId, runs.runStatus)))
    t = t[t.st.eq('COMPLETE_30')].copy()
    for c in ['decisionUptimeMs', 'appliedDelayMs', 'timeoutDeadlineUptimeMs', 'captureTimeoutMs',
              'draftStartUptimeMs', 'draftEndUptimeMs', 'runShotIndex', 'timeoutMarginMs',
              'timeToDeadlineMs']:
        t[c] = pd.to_numeric(t[c], errors='coerce')
    t['req'] = t.timeoutDeadlineUptimeMs - t.captureTimeoutMs
    t = t.sort_values(['runId', 'runShotIndex'])
    t['prevEnd'] = t.groupby('runId').draftEndUptimeMs.shift()
    t['gap'] = t.draftStartUptimeMs - t.prevEnd
    idle = t[(t.gap > IDLE_GAP) | t.prevEnd.isna()]
    lead_p5 = float((idle.draftStartUptimeMs - idle.req).quantile(0.05))
    busy_gap = float(t[t.gap <= IDLE_GAP].gap.median())
    dec = t[t.decisionUptimeMs.notna() & t.pacingDecisionRecorded.map(tf)]

    # callback latency when a transition carries no recorded callback
    Ls = []
    for run, g in t.groupby('runId'):
        req = g.req.values
        for c in dec[dec.runId == run].decisionUptimeMs.values:
            j = np.searchsorted(req, c, side='right') - 1
            if j >= 0:
                Ls.append(c - req[j])
    L_med = float(np.median(Ls))

    out = {}
    for run, g in t.groupby('runId'):
        g = g.reset_index(drop=True)
        req = g.req.values
        caps = []
        for i, r in g.iterrows():
            nodes = byc[r.captureIndex]
            ds, acc, lst = r.draftStartUptimeMs, 0.0, []
            for _, n in nodes.iterrows():
                d = float(n.durationMs) if pd.notna(n.durationMs) and n.durationMs > 0 else None
                pre = (n.nodeStartUptimeMs - ds) - acc
                lst.append(dict(key=n.workloadKey, fdur=d, pre=pre, fadmit=tf(n.admit),
                                seq=parse_seq(n.workloadSequenceKey)))
                acc += (d or 0.0)
            busy = pd.notna(r.gap) and r.gap <= IDLE_GAP
            caps.append(dict(cap=r.captureIndex, shot=int(r.runShotIndex), req=float(r.req),
                             timeout=float(r.captureTimeoutMs), fstart=float(ds),
                             fend=float(r.draftEndUptimeMs), post=float(r.draftEndUptimeMs - ds) - acc,
                             gap=(float(r.gap) if busy else busy_gap), busy=busy,
                             lead_hi=float(ds - r.req), nodes=lst, level=r.shotOverheatLevel,
                             fmargin=float(r.timeoutMarginMs)))
        # transitions j -> j+1: recorded callback between the two requests, by time
        rd = dec[dec.runId == run]
        cb_t, cb_d, cb_T = rd.decisionUptimeMs.values, rd.appliedDelayMs.values, rd.timeToDeadlineMs.values
        dl = g.timeoutDeadlineUptimeMs.values
        trans = []
        for j in range(len(caps) - 1):
            R = req[j + 1] - req[j]
            k = np.where((cb_t >= req[j]) & (cb_t < req[j + 1]))[0]
            if len(k):
                c, d, T = cb_t[k[0]], cb_d[k[0]], cb_T[k[0]]
                # which committed capture's deadline this decision priced against,
                # as an offset back from capture j (the newest committed one)
                back = None
                if pd.notna(T) and 0 < T < caps[j]['timeout']:
                    m = int(np.argmin(np.abs(dl - (c + T))))
                    if abs(dl[m] - (c + T)) <= 1 and m <= j:
                        back = j - m
                trans.append(dict(L=c - req[j], d=float(d), eps=req[j + 1] - (c + d), rec=True, back=back))
            else:
                L = min(L_med, R)
                trans.append(dict(L=L, d=0.0, eps=R - L, rec=False, back=None))
        sids = [sid.get(c['cap']) for c in caps]
        for k in range(len(caps)):
            caps[k]['last_in_session'] = k + 1 < len(caps) and sids[k + 1] != sids[k]
        ex = {}
        for c in caps:
            for n in c['nodes']:
                if n['fdur']:
                    ex.setdefault(n['key'], []).append((c['shot'], n['fdur']))
        out[run] = dict(caps=caps, trans=trans, ex=ex)
    return out, dict(lead_p5=lead_p5, busy_gap=busy_gap, L_med=L_med)


# ------------------------------------------------------------------ admission arms
def stat_of(v, stat):
    return float(np.mean(v)) if stat == 'mean' else float(np.max(v))


class RunState:
    """Everything one run's estimators and pacer read: completed walls, per-stage
    durations, non-stage time, and the live capture timeline."""

    def __init__(self):
        self.walls = []         # (end, wall)
        self.stage_hist = {}    # key -> [(end, dur)]
        self.req = {}           # j -> simulated request time
        self.start = {}         # j -> simulated draft start
        self.end = {}           # j -> simulated draft end

    def naive_draft_estimate(self, now, stat, N, unit, chain):
        if unit == 'draft':
            h = [w for e, w in self.walls if e <= now][-N:]
            return stat_of(h, stat) if h else 0.0
        m = 0.0
        for k in chain:
            h = [d for e, d in self.stage_hist.get(k, []) if e <= now][-N:]
            if h:
                m += stat_of(h, stat)
        return m

    def naive_backlog(self, now, m, upto):
        B = 0.0
        for j in range(upto + 1):
            if j not in self.req or self.req[j] > now:
                continue
            if j in self.end and self.end[j] <= now:
                continue
            if j in self.start and self.start[j] <= now:
                B += max(0.0, m - (now - self.start[j]))
            else:
                B += m
        return B


class NaivePacer(Pacer):
    """Same session, deadline clock, growth term and decision formula as the
    deployed pacer; only the backlog B and the reserve C come from a recent-N
    statistic instead of the backlog clock and the session reserve."""

    def __init__(self, est, rs, stat, N, unit, chain, **kw):
        super().__init__(est, **kw)
        self.rs, self.stat, self.N, self.unit, self.chain = rs, stat, N, unit, chain
        self.upto = 0

    def decide_delay(self, now, timeout_ms=None, **_):
        if self.session is None:
            self.session = PacingSession(now)
        s = self.session
        if s.snapshot is None:
            return None
        ttd = s.ttd_at(now, timeout_ms)
        m = self.rs.naive_draft_estimate(now, self.stat, self.N, self.unit, self.chain)
        B = self.rs.naive_backlog(now, m, self.upto)
        growth = s.observe_growth(B)
        delay = compute_pacing_delay_ms(B, growth, ttd, m, self.halve_growth)
        d = Decision(delay, B, growth, s.queued, s.queued_work, ttd, now, s.snapshot)
        s.queue(d)
        return d


# ------------------------------------------------------------------------ simulate
def simulate(prep, dev, cond, meta, adm, pac, lag='pin', lead_mode='late', rng=None, fact=False,
             fact_adm=None, fact_pac=None, session='pin'):
    """adm / pac: ('DEP',) or ('NAIVE', stat, N, unit).  fact=True replays the
    recorded delays and recorded admits (mechanics check); fact_adm / fact_pac
    replay only one of them.  session='pin' ends a pacing session at the end of
    the draft that ended it in the trace, 'drain' when no requested capture is
    left unstarted."""
    fact_adm = fact if fact_adm is None else fact_adm
    fact_pac = fact if fact_pac is None else fact_pac
    rows, trows = [], []
    for run, R in prep.items():
        caps, trans, ex = R['caps'], R['trans'], R['ex']
        n = len(caps)
        pr = Predictor()
        est = PacingEstimator(pr)
        pol = Sticky()
        rs = RunState()
        chain = tuple(nd['key'] for nd in caps[0]['nodes'])
        kw = dict(resolve=lambda k: pol.resolve(k), halve_growth=HALVE[(dev, cond)],
                  reserve_stat=RESERVE[(dev, cond)])
        if pac[0] == 'DEP':
            pacer = Pacer(est, **kw)
        else:
            pacer = NaivePacer(est, rs, pac[1], pac[2], pac[3], chain, **kw)

        ev, seq_no = [], [0]

        def push(t_, pr_, kind, j):
            seq_no[0] += 1
            heapq.heappush(ev, (t_, pr_, seq_no[0], kind, j))

        D, ready = {}, {}
        rs.req[0] = caps[0]['req']
        push(caps[0]['req'], 1, 'req', 0)
        next_start, worker_free, last_end = 0, True, None
        delays = {}
        while ev:
            now, _, _, kind, j = heapq.heappop(ev)
            c = caps[j] if j < n else None
            if kind == 'req':
                D[j] = now + c['timeout']
                if lag != 'pin' and j - lag >= 0:
                    pacer.set_deadline(D[j - lag])
                lead = c['lead_hi'] if (lead_mode == 'late' or not c['busy']) else min(c['lead_hi'], meta['lead_p5'])
                push(now + lead, 3, 'ready', j)
                if j + 1 < n:
                    push(now + trans[j]['L'], 2, 'cb', j + 1)
            elif kind == 'cb':
                if isinstance(pacer, NaivePacer):
                    pacer.upto = j - 1
                ttd = None
                if lag == 'pin' and pacer.session is not None:
                    back = trans[j - 1]['back']
                    m = (j - 1) - (1 if back is None else back)
                    if m >= 0 and m in D:
                        ttd = min(max(D[m] - now, 0), c['timeout'])
                d = pacer.decide_delay(now, timeout_ms=c['timeout'], ttd_override=ttd)
                delay = trans[j - 1]['d'] if fact_pac else (d.delay if d else 0)
                delays[j] = delay
                rs.req[j] = now + delay + trans[j - 1]['eps']
                push(rs.req[j], 1, 'req', j)
            elif kind == 'ready':
                ready[j] = now
            elif kind == 'start':
                pass  # handled inline below
            elif kind == 'end':
                worker_free, last_end = True, now
                if session == 'pin':
                    drained = caps[j]['last_in_session']
                else:   # no requested capture left unstarted
                    drained = not any(k in rs.req and rs.req[k] <= now for k in range(next_start, n))
                if drained:
                    pacer.clear()
                    pol.reset()
            # try to start the next draft
            if worker_free and next_start < n and next_start in ready:
                k = next_start
                ck = caps[k]
                st = ready[k] if last_end is None else max(ready[k], last_end + ck['gap'])
                if st > now:
                    push(st, 4, 'start', k)
                    worker_free = False   # reserved; actual run happens at 'start'
                    next_start = -1 - k   # sentinel: pending start
                else:
                    _run_draft(k, now, caps, ex, pr, est, pol, pacer, rs, D, adm, rng, fact_adm, push, rows,
                               dev, cond, run)
                    worker_free, next_start = False, k + 1
            if kind == 'start':
                _run_draft(j, now, caps, ex, pr, est, pol, pacer, rs, D, adm, rng, fact_adm, push, rows,
                           dev, cond, run)
                worker_free, next_start = False, j + 1
        span = rs.req[n - 1] - rs.req[0] if (n - 1) in rs.req else np.nan
        trows.append(dict(dev=dev, cond=cond, run=run, delay_sum=sum(delays.values()),
                          span=span, rec_span=caps[-1]['req'] - caps[0]['req'],
                          rec_delay_sum=sum(tr['d'] for tr in trans),
                          engaged=sum(1 for v in delays.values() if v > 0), transitions=len(delays)))
    return pd.DataFrame(rows), pd.DataFrame(trows)


def _run_draft(k, start, caps, ex, pr, est, pol, pacer, rs, D, adm, rng, fact, push, rows, dev, cond, run):
    c = caps[k]
    rs.start[k] = start
    full = tuple(nd['key'] for nd in c['nodes'])
    pacer.start_draft(full, 0)
    cum, decisions, durs, executed, node_durs = 0.0, {}, {}, {}, []
    for jn, nd in enumerate(c['nodes']):
        t_node = start + nd['pre'] + cum
        T = D[k] - t_node
        key = nd['key']
        seq = pol.resolve(full[jn:])
        P, U, pm = pr.decide(seq)
        decisions[seq] = pm
        if seq[0] in OPTIONAL:
            rsv = tuple(q for q in seq if q.startswith('ENCODING'))
            if rsv:
                decisions[rsv] = pr.decide(rsv)[2]
        if key in OPTIONAL:
            if fact:
                m_adm = nd['fadmit']
            elif adm[0] == 'DEP':
                m_adm = (P <= 0) or (U <= T)
            else:
                _, stat, N, unit = adm
                if unit == 'draft':
                    h = [w for e, w in rs.walls if e <= t_node][-N:]
                    m_adm = True if not h else (stat_of(h, stat) - (t_node - start) <= T)
                else:
                    f = rs.naive_draft_estimate(t_node, stat, N, 'stage', pol.resolve(full[jn:]))
                    m_adm = True if f <= 0 else (f <= T)
            adm_ = m_adm if fact else pol.admit(key, m_adm)
        else:
            adm_ = True
        if adm_:
            d = nd['fdur']
            if d is None and key in OPTIONAL:
                d = impute(ex, key, c['shot'], rng)
            d = d or 0.0
        else:
            d = 0.0
        executed[key] = executed.get(key, False) or (adm_ and d > 0)
        if d > 0:
            durs[key] = int(round(d))
            node_durs.append((key, d))
        cum += d
    end = start + c['post'] + cum
    wall = end - start
    rs.end[k] = end
    pr.learn(durs, list(decisions.items()))
    est.overhead.observe(sum(durs.values()), wall)
    pacer.end_draft(end, wall)
    rs.walls.append((end, wall))
    for key, d in node_durs:
        rs.stage_hist.setdefault(key, []).append((end, d))
    push(end, 0, 'end', k)
    rows.append(dict(dev=dev, cond=cond, run=run, shot=c['shot'], margin=D[k] - end, fmargin=c['fmargin'],
                     end=end, fend=c['fend'], start=start, fstart=c['fstart'], req=rs.req.get(k),
                     bokeh=executed.get('BOKEH()', False), filt=executed.get('FILTER()', False)))


if __name__ == '__main__':
    W = pickle.load(open(os.path.join(HERE, 'wb.pkl'), 'rb'))
    P = {k: prepare(x) for k, x in W.items() if k[1] == '12MP'}
    pickle.dump(P, open(os.path.join(HERE, 'joint_prep.pkl'), 'wb'))
    for k, (prep, meta) in P.items():
        print(k, 'runs', len(prep), meta)
