"""Validate port_pacer against the recorded trace, in two steps.

1. Formula structure: does the recorded estimatedCompletionTime / deadlineDeficit
   equal what computePacingDelayMs builds from the recorded B, C, T?
2. Growth estimator + full delay: replay RecencyWeightedDistribution over the
   recorded per-decision backlog sequence inside each pacer session, and compare
   the resulting delay with the recorded appliedDelayMs.

Step 2 exercises everything in the decision path except the backlog clock and
the reserve, which are fed from the trace here and validated separately.
"""
import math, pickle, os
import numpy as np, pandas as pd
from port_pacer import RWD, compute_pacing_delay_ms

HALVE = {}  # workbook -> which delay form reproduces it; decided below, not assumed

HERE = os.path.dirname(os.path.abspath(__file__))
W = pickle.load(open(os.path.join(HERE, 'wb.pkl'), 'rb'))
NUM = ['controllerBacklogMs', 'draftSequenceReservedDurationMs', 'timeToDeadlineMs',
       'appliedDelayMs', 'sharedDeficitFormulaDelayMs', 'deadlineDeficitMs',
       'estimatedCompletionTimeMs', 'decisionUptimeMs', 'captureTimeoutMs']

print(f"{'workbook':<16}{'n':>6}{'estComp':>9}{'deficit':>9}{'delay==':>9}{'engage':>9}{'|err|p90':>10}   form")
for k, x in W.items():
    t = x['CaseStudyTrace'].copy()
    r = x['RQ1Runs']
    t['st'] = t.runId.map(dict(zip(r.runId, r.runStatus)))
    t = t[t.st.ne('CAPTURE_TIMEOUT')]
    t['sid'] = t.captureIndex.map(dict(zip(x['Capture'].captureIndex, x['Capture'].pacerSessionId)))
    t = t[t.pacingDecisionRecorded.astype(str).str.strip().str.lower().isin(['true', '1', '1.0'])]
    for c in NUM:
        t[c] = pd.to_numeric(t[c], errors='coerce')
    d = t.dropna(subset=['controllerBacklogMs', 'draftSequenceReservedDurationMs',
                         'timeToDeadlineMs', 'appliedDelayMs', 'decisionUptimeMs']).copy()
    d = d.sort_values(['runId', 'decisionUptimeMs'])

    # 1. structure
    est = d.controllerBacklogMs + 2 * d.draftSequenceReservedDurationMs
    def_ = est - d.timeToDeadlineMs.clip(lower=0)
    ok_est = (est - d.estimatedCompletionTimeMs).abs() <= 1
    ok_def = (def_ - d.deadlineDeficitMs).abs() <= 1

    # 2. growth replayed per pacer session, then the full delay
    delays = {False: np.empty(len(d)), True: np.empty(len(d))}
    i = 0
    for _, g in d.groupby(['runId', 'sid'], dropna=False, sort=False):
        rwd, last = RWD(), None
        for _, row in g.iterrows():
            b = row.controllerBacklogMs
            if last is not None:
                rwd.decay()
                rwd.add(float(b - last))
            last = b
            growth = max(rwd.mean(), 0.0)
            for h in (False, True):
                delays[h][i] = compute_pacing_delay_ms(b, growth, row.timeToDeadlineMs,
                                                       row.draftSequenceReservedDurationMs, h)
            i += 1
    A = d.appliedDelayMs.values
    hits = {h: 100 * (np.abs(delays[h] - A) <= 1).mean() for h in (False, True)}
    best = max(hits, key=hits.get)
    HALVE[k] = best
    err = np.abs(delays[best] - A)
    print(f"{str(k):<16}{len(d):>6}{100*ok_est.mean():>8.1f}%{100*ok_def.mean():>8.1f}%"
          f"{hits[best]:>8.1f}%{100*((delays[best] > 0) == (A > 0)).mean():>8.1f}%"
          f"{np.quantile(err, .9):>10.0f}   {'(deficit+G)/2' if best else 'deficit/2+G'}"
          f"   other form {hits[not best]:.1f}%")

print()
print('form by workbook:', {str(k): ('(deficit+G)/2' if h else 'deficit/2+G') for k, h in HALVE.items()})
