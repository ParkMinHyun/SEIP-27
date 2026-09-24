"""Validate the pacer's own bookkeeping by replaying the recorded event stream.

val_pacer.py fed the backlog and the reserve from the trace and checked only the
delay formula.  Here the pacer computes both itself: the only things taken from
the trace are the event timestamps, the planned sequence keys, the realized node
and draft durations, and each capture's deadline.  Simulated backlog, reserve,
queue depth, queued work and delay are compared against the recorded columns.

Events are replayed in timestamp order, not capture order, because captures
overlap: a decision for capture i can land while capture i-1 is still running.
"""
import math, os, pickle, sys
import numpy as np, pandas as pd
from port import Predictor, load_nodes, parse_seq, OPTIONAL, GROUP
from port_pacer import PacingEstimator, Pacer
from sim import Sticky, tf

ANCHOR = '--anchor' in sys.argv   # advance the backlog clock on the recorded delay
OWN_DL = '--own-deadline' in sys.argv  # use the port's own deadline clock instead of recorded T
# How many captures late the pacer registers a capture's deadline.  The live
# hook races the callback, so this is a modelled lag, swept rather than assumed.
DL_LAG = int(([a for a in sys.argv if a.startswith('--lag=')] or ['--lag=0'])[0].split('=')[1])
RESERVE = ([a for a in sys.argv if a.startswith('--reserve=')] or ['--reserve=max'])[0].split('=')[1]
HERE = os.path.dirname(os.path.abspath(__file__))
W = pickle.load(open(os.path.join(HERE, 'wb.pkl'), 'rb'))

# Reserve statistic by workbook, chosen by fit like the delay form.  S26U is the
# session running maximum to within 10 ms on 97-99% of decisions; on S26 neither
# form is exact, and the 44a9a32 expectedMaximum fits 12MP better (66% vs 36%
# within 10 ms) while the running maximum fits 24MP better.
RESERVE_AUTO = {('S26U', '12MP'): 'max', ('S26U', '24MP'): 'max',
                ('S26', '12MP'): 'expmax', ('S26', '24MP'): 'max'}

# which delay form each workbook was recorded with (val_pacer.py decides this)
HALVE = {('S26U', '12MP'): True, ('S26U', '24MP'): True,
         ('S26', '12MP'): True, ('S26', '24MP'): False}

PRIO = {'end': 0, 'session': 1, 'deadline': 2, 'decide': 3, 'start': 4}
NUM = ['decisionUptimeMs', 'draftStartUptimeMs', 'draftEndUptimeMs', 'draftSequenceDurationMs',
       'timeoutDeadlineUptimeMs', 'captureTimeoutMs', 'draftSequenceBudgetMs',
       'controllerBacklogMs', 'draftSequenceReservedDurationMs', 'timeToDeadlineMs',
       'appliedDelayMs', 'controllerQueuedDraftCount', 'controllerQueuedPredictedWorkMs',
       'draftSequenceOverheadDurationMs', 'workloadSequencePredictedDurationMs']

rows = []
for (dev, cond), x in W.items():
    N = load_nodes(x)
    byc = {c: g.sort_values('nodeOrder') for c, g in N.groupby('captureIndex')}
    t = x['CaseStudyTrace'].copy()
    r = x['RQ1Runs']
    t['st'] = t.runId.map(dict(zip(r.runId, r.runStatus)))
    t = t[t.st.ne('CAPTURE_TIMEOUT')].copy()
    t['sid'] = t.captureIndex.map(dict(zip(x['Capture'].captureIndex, x['Capture'].pacerSessionId)))
    for c in NUM:
        t[c] = pd.to_numeric(t[c], errors='coerce')
    t = t.sort_values(['runId', 'runShotIndex'])

    for run, g in t.groupby('runId'):
        pred = Predictor()
        est = PacingEstimator(pred)
        pol = Sticky()
        pacer = Pacer(est, resolve=lambda k: pol.resolve(k), halve_growth=HALVE[(dev, cond)],
                      reserve_stat=(RESERVE_AUTO[(dev, cond)] if RESERVE == 'auto' else RESERVE))
        cap_rows = {r_.captureIndex: r_ for _, r_ in g.iterrows()}
        order = list(g.captureIndex)
        reqs = {r_.captureIndex: (r_.timeoutDeadlineUptimeMs - r_.captureTimeoutMs)
                for _, r_ in g.iterrows()
                if pd.notna(r_.timeoutDeadlineUptimeMs) and pd.notna(r_.captureTimeoutMs)}

        def deadline_time(ci):
            """When the pacer registers capture ci's deadline: the request time of
            the capture DL_LAG positions later, so lag 0 is 'newest committed'."""
            j = order.index(ci) + DL_LAG
            return reqs.get(order[j]) if j < len(order) else None

        ev = []
        for _, c in g.iterrows():
            ci = c.captureIndex
            if pd.notna(c.timeoutDeadlineUptimeMs) and pd.notna(c.captureTimeoutMs):
                # the session boundary stays at this capture's own request time;
                # only the deadline registration is lagged
                ev.append((c.timeoutDeadlineUptimeMs - c.captureTimeoutMs, PRIO['session'], ci, 'session'))
                _dt = deadline_time(ci)
                if _dt is not None:
                    ev.append((_dt, PRIO['deadline'], ci, 'deadline'))
            # Every captureAvailable callback is an event, including the ones the
            # export carries no decision for (SESSION_BOOTSTRAP_ZERO /
            # NO_GATING_DECISION_ZERO).  They queue nothing, but the first of them
            # is what opens the pacing session, and without it the session opens a
            # capture late and the whole FIFO is shifted by one.
            if pd.notna(c.decisionUptimeMs) and tf(c.pacingDecisionRecorded):
                ev.append((c.decisionUptimeMs, PRIO['decide'], ci, 'decide'))
            elif pd.notna(c.timeoutDeadlineUptimeMs) and pd.notna(c.captureTimeoutMs):
                ev.append((c.timeoutDeadlineUptimeMs - c.captureTimeoutMs, PRIO['decide'], ci, 'unrec'))
            if pd.notna(c.draftStartUptimeMs):
                ev.append((c.draftStartUptimeMs, PRIO['start'], ci, 'start'))
            if pd.notna(c.draftEndUptimeMs):
                ev.append((c.draftEndUptimeMs, PRIO['end'], ci, 'end'))
        ev.sort(key=lambda e: (e[0], e[1], e[2]))

        cur_sid = None
        for now, _, ci, kind in ev:
            c = cap_rows[ci]
            if kind == 'session':
                if pd.notna(c.sid) and cur_sid is not None and c.sid != cur_sid:
                    pacer.clear()
                    pol.reset()
                if pd.notna(c.sid):
                    cur_sid = c.sid
            elif kind == 'deadline':
                pacer.set_deadline(c.timeoutDeadlineUptimeMs)
            elif kind == 'unrec':
                pacer.decide_delay(now, timeout_ms=c.captureTimeoutMs)
            elif kind == 'decide':
                d = pacer.decide_delay(now, timeout_ms=c.captureTimeoutMs,
                                       ttd_override=(None if OWN_DL else c.timeToDeadlineMs),
                                       delay_override=(c.appliedDelayMs if ANCHOR else None))
                rows.append(dict(
                    dev=dev, cond=cond, run=run, cap=ci,
                    sim_B=(d.backlog if d else np.nan), rec_B=c.controllerBacklogMs,
                    sim_C=(d.snapshot.reserved_ms if d else np.nan), rec_C=c.draftSequenceReservedDurationMs,
                    sim_T=(d.ttd if d else np.nan), rec_T=c.timeToDeadlineMs,
                    sim_q=(d.queued if d else np.nan), rec_q=c.controllerQueuedDraftCount,
                    sim_w=(d.queued_work if d else np.nan), rec_w=c.controllerQueuedPredictedWorkMs,
                    sim_oh=(d.snapshot.overhead_ms if d else np.nan), rec_oh=c.draftSequenceOverheadDurationMs,
                    sim_ws=(d.snapshot.workload_ms if d else np.nan), rec_ws=c.workloadSequencePredictedDurationMs,
                    sim_d=(d.computed_delay if d else np.nan), rec_d=c.appliedDelayMs,
                    sim_key=('>'.join(d.snapshot.key) if d else ''),
                    rec_key=str(c.controllerDraftSequenceKey)))
            elif kind == 'start':
                # The full configured chain, from the node rows -- not the trace's
                # plannedWorkloadSequenceKey, which is already the demoted
                # projection.  Passing the demoted key makes resolve() a no-op, so
                # estimateDemotedWorkloadDurationMs returns 0 and the reserve keeps
                # work the draft will not run.
                nd = byc.get(ci)
                full = tuple(n.workloadKey for _, n in nd.iterrows()) if nd is not None else ()
                pacer.start_draft(full if full else None, c.draftSequenceBudgetMs)
            else:  # end
                nd = byc.get(ci)
                decisions, durs = {}, {}
                if nd is not None:
                    for _, n in nd.iterrows():
                        seq = parse_seq(n.workloadSequenceKey)
                        if not seq:
                            continue
                        _, _, pm = pred.decide(seq)
                        decisions[seq] = pm
                        if n.workloadKey in OPTIONAL:
                            rsv = tuple(k for k in seq if k.startswith('ENCODING'))
                            if rsv:
                                decisions[rsv] = pred.decide(rsv)[2]
                            pol.admit(n.workloadKey, bool(tf(n.admit)))
                        if pd.notna(n.durationMs) and n.durationMs > 0:
                            durs[n.workloadKey] = int(n.durationMs)
                pred.learn(durs, list(decisions.items()))
                est.overhead.observe(sum(durs.values()), c.draftSequenceDurationMs)
                pacer.end_draft(now, c.draftSequenceDurationMs)

D = pd.DataFrame(rows).dropna(subset=['sim_B'])
pd.set_option('display.width', 250)
print(f"n = {len(D)}\n")
print(f"{'workbook':<16}" + ''.join(f'{c:>12}' for c in ['backlog', 'reserve', 'ttd', 'queued', 'qWork', 'overhead', 'wsPred', 'delay']))
for (dev, cond), d in D.groupby(['dev', 'cond']):
    out = []
    for a, b, tol in [('sim_B', 'rec_B', 1), ('sim_C', 'rec_C', 1), ('sim_T', 'rec_T', 1),
                      ('sim_q', 'rec_q', 0), ('sim_w', 'rec_w', 1), ('sim_oh', 'rec_oh', 1),
                      ('sim_ws', 'rec_ws', 1), ('sim_d', 'rec_d', 1)]:
        out.append(f"{100 * ((d[a] - d[b]).abs() <= tol).mean():>11.1f}%")
    print(f"{str((dev, cond)):<16}" + ''.join(out))
print()
for (dev, cond), d in D.groupby(['dev', 'cond']):
    print(f"{str((dev, cond)):<16} snapshot key matches recorded: {100*(d.sim_key == d.rec_key).mean():.1f}%")
D.to_pickle(os.path.join(HERE, 'val_pacer_clock.pkl'))
