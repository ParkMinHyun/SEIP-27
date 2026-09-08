"""RQ4 evidence: pacing response to Draft queue pressure, and coverage of the
captures that still finished close to the deadline.

Emits the inputs of tables/tab_rq4_pacing_sizing.tex.  See docs/exhibits.md for
that entry.  RQ4 ships no figure: a capture-aligned episode figure was drafted
and withdrawn because fig_casestudy_12mp already plots a per-capture trace of
the same shape.  The episode pass is kept because the prose quotes the per-run
peak backlog it produces; episode_aligned.csv is a by-product and nothing reads
it.

Row semantics, from the workbooks' own ReplayNotes sheet
--------------------------------------------------------
The pacing decision persisted on shot i was dequeued when shot i's Draft
started, so it is the decision that gated shot i's release.  One CaseStudyTrace
row therefore carries a complete (state, action, outcome) triple:

  state    realBacklogMs, realQueueDepth, timeToDeadlineMs, shotOverheatLevel
           -- read at the decision, reconstructed from the completed trace
  action   appliedDelayMs, and whether admission skipped an optional stage
  outcome  timeoutSlackPercent, the realized deadline margin of shot i

What the bands are, and what they are not
-----------------------------------------
Queue pressure is the MEASURED backlog at the decision as a percentage of the
Capture Timeout budget: realBacklogMs is reconstructed from the completed trace
as max(draftEndUptimeMs) over unfinished earlier Draft Sequences minus the
decision time.  It is not the controller's own online estimate, and it carries
neither the growth term nor the two-Draft reserve of the pacing equation.
Banding on the controller's score would make activation true by construction;
banding on measured backlog does not, but the axis still shares the dominant
term of the rule, so the selectivity columns describe the deployed response
rather than testing it independently.  The columns that do carry independent
content are the outcome ones: the realized margin per band, the coverage of the
thin-margin captures, and the margin of the decisions the controller left alone.

Claim limits
------------
Coverage is measured against the REALIZED margin, which is an outcome after the
intervention, so it bounds missed interventions and says nothing about
unnecessary ones; the factual trace cannot expose the second, because no
counterfactual of an unpaced release exists on a closed loop.  The cost of the
intervention is bounded separately by the delay columns and by RQ1.

Population
----------
The four full-controller workbooks, pooled by capture condition over the two
devices.  Runs whose runStatus is CAPTURE_TIMEOUT are excluded: the author
confirmed on 2026-09-08 that they are operator test captures, not evaluation
runs.  Rows without a recorded pacing decision, or without a reconstructed
backlog, are excluded per decision, not per run.

Run:  python scripts/rq4_pacing_sizing_metrics.py
      python scripts/rq4_pacing_sizing_metrics.py --no-write
"""
import os
import sys
import warnings

warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'rq4')

SOURCES = {
    ('S26 Ultra', '12MP normal'): 'data/S26_Ultra/SM-S948U_metrics_12MP_normal_0906.xlsx',
    ('S26 Ultra', '24MP memory'): 'data/S26_Ultra/SM-S948U_metrics_24MP_memory_0906.xlsx',
    ('S26', '12MP normal'):       'data/S26/SM-S942B_metrics_12MP_normal_0906.xlsx',
    ('S26', '24MP memory'):       'data/S26/SM-S942B_metrics_24MP_memory_0829.xlsx',
}
CONDITIONS = ('12MP normal', '24MP memory')

# Queue-pressure bands, as percentages of the Capture Timeout budget.  Half-open
# [lo, hi); the last band is [50, infinity).
BANDS = ((0.0, 10.0, '<10'), (10.0, 30.0, '10-30'),
         (30.0, 50.0, '30-50'), (50.0, 1e9, '>=50'))
# Realized-margin thresholds the coverage panel reports, in percent of budget.
THIN = (5.0, 10.0, 20.0)
# Margin below which a decision joins the tail the prose has to characterize.
TAIL = 1.0
# A pressure episode opens when measured backlog reaches ON percent of the
# budget and closes when it falls below OFF.  ON sits above the band where the
# response saturates and OFF below the band where it is quiescent.
EPISODE_ON, EPISODE_OFF = 40.0, 20.0
# Capture offsets the episode pass reports, relative to the onset.
ALIGN = range(-5, 11)


def truthy(s):
    """12MP workbooks store TRUE/FALSE strings, 24MP workbooks store 1.0/0.0."""
    return s.astype(str).str.strip().str.lower().isin(['true', '1', 'yes', '1.0'])


def load():
    """One row per gating pacing decision, pooled over the four workbooks."""
    frames = []
    for (device, condition), rel in SOURCES.items():
        path = os.path.join(ROOT, rel)
        trace = pd.read_excel(path, sheet_name='CaseStudyTrace')
        runs = pd.read_excel(path, sheet_name='RQ1Runs')
        trace['device'] = device
        trace['condition'] = condition
        trace['run'] = f'{device}/{condition}/' + trace['runId'].astype(str)
        trace['runStatus'] = trace['runId'].map(dict(zip(runs['runId'], runs['runStatus'])))
        frames.append(trace)
    d = pd.concat(frames, ignore_index=True)
    d = d[d['runStatus'].ne('CAPTURE_TIMEOUT')]
    d = d[truthy(d['pacingDecisionRecorded'])]

    d['delay'] = pd.to_numeric(d['appliedDelayMs'], errors='coerce').fillna(0.0)
    d['paced'] = d['delay'] > 0
    d['skipped'] = ~truthy(d['bokehExecuted']) | ~truthy(d['filterExecuted'])
    d['either'] = d['paced'] | d['skipped']
    d['pressure'] = 100.0 * pd.to_numeric(d['realBacklogMs'], errors='coerce') \
        / pd.to_numeric(d['captureTimeoutMs'], errors='coerce')
    d['slack'] = pd.to_numeric(d['timeoutSlackPercent'], errors='coerce')
    return d.dropna(subset=['pressure', 'slack']).sort_values(['run', 'runShotIndex'])


def band_of(p):
    return next(name for lo, hi, name in BANDS if lo <= p < hi)


def cell(x):
    """Every delay statistic is taken over the PACED decisions of the group, so
    its denominator is pacedCount and not n.

    dOverBacklogP50Percent  per-decision d_i / B_i, a proportionality readout:
                            how much of the outstanding Draft work the delay
                            asks the user to wait for.
    overlapPercent          sum(min(d_i, B_i)) / sum(d_i), a ratio of sums and
                            therefore NOT the same statistic.  It is the share
                            of applied delay that elapsed while Draft work was
                            still outstanding, so it says the delay did not idle
                            the worker.  Keep the two apart in prose.

    The absolute delay is deliberately absent from the RQ4 table: RQ1 and RQ2
    both print d P50, RQ1 per thermal level, so repeating it here would spend a
    column on a number the reader already has.
    """
    paced = x[x['paced']]
    d_i, b_i = paced['delay'], paced['realBacklogMs']
    return {
        'n': len(x),
        'pacedCount': len(paced),
        'pacedPercent': 100.0 * x['paced'].mean(),
        'dOverBacklogP50Percent': (100.0 * d_i / b_i).median() if len(paced) else np.nan,
        'overlapPercent': 100.0 * np.minimum(d_i, b_i).sum() / d_i.sum() if d_i.sum() else np.nan,
        'delayP50Ms': d_i.median() if len(paced) else np.nan,
        'slackP5Percent': x['slack'].quantile(0.05),
        'slackMinPercent': x['slack'].min(),
        # Admission is RQ3's subject, and none of the four below are printed by
        # the RQ4 table.  They stay in the CSV because the coordination note
        # and the thin-margin prose need them, and because delayP50Ms and
        # slackP5Percent remain the cross-check against RQ1.
        'skippedPercent': 100.0 * x['skipped'].mean(),
        'eitherPercent': 100.0 * x['either'].mean(),
    }


def response(d):
    """Panel (a): the deployed response across the queue-pressure bands."""
    rows = []
    for condition in CONDITIONS:
        part = d[d['condition'] == condition]
        for _, _, name in BANDS:
            rows.append({'condition': condition, 'band': name,
                         **cell(part[part['band'] == name])})
    return pd.DataFrame(rows)


def coverage(d):
    """Panel (b): what the controller was doing on the captures that still
    finished close to the deadline, and how the untouched decisions ended."""
    rows = []
    for condition in CONDITIONS:
        part = d[d['condition'] == condition]
        for threshold in THIN:
            x = part[part['slack'] < threshold]
            rows.append({'condition': condition, 'group': 'slack<%g' % threshold,
                         **cell(x), 'noActionCount': int((~x['either']).sum())})
        x = part[~part['either']]
        rows.append({'condition': condition, 'group': 'no intervention',
                     **cell(x), 'noActionCount': len(x)})
    return pd.DataFrame(rows)


def lead(d):
    """How far ahead of a run's first thin capture the controller had acted."""
    rows = []
    for run, g in d.groupby('run'):
        g = g.reset_index(drop=True)
        thin = g.index[g['slack'] < 10.0]
        if not len(thin):
            continue
        first = thin.min()
        paced = g.index[g['paced']]
        rows.append({
            'run': run, 'condition': g['condition'].iloc[0],
            'pacedBefore': bool(len(paced) and paced.min() < first),
            'leadCaptures': (g.loc[first, 'runShotIndex'] - g.loc[paced.min(), 'runShotIndex'])
            if len(paced) and paced.min() <= first else np.nan})
    return pd.DataFrame(rows)


def episodes(d, condition=None):
    """Maximal windows of sustained queue pressure, and the capture-aligned
    mean trajectory around their onset.

    Pass a condition to restrict the windows to it.  The figure currently reads
    the pooled series; the per-condition series are emitted beside it so that
    scoping the figure to one condition is a one-line change at its \\addplot
    sites rather than a re-derivation."""
    if condition is not None:
        d = d[d['condition'] == condition]
    spans, aligned = [], []
    for _, g in d.groupby('run'):
        g = g.reset_index(drop=True)
        open_at = None
        for i, p in enumerate(g['pressure']):
            if open_at is None and p >= EPISODE_ON:
                open_at = i
            elif open_at is not None and p < EPISODE_OFF:
                spans.append((g, open_at))
                open_at = None
        if open_at is not None:
            spans.append((g, open_at))
    for g, start in spans:
        for off in ALIGN:
            j = start + off
            if 0 <= j < len(g):
                r = g.iloc[j]
                aligned.append({'offset': off, 'pressure': r['pressure'], 'slack': r['slack'],
                                'delay': r['delay'], 'paced': float(r['paced']),
                                'skipped': float(r['skipped'])})
    a = pd.DataFrame(aligned).groupby('offset').agg(
        n=('pressure', 'size'), pressure=('pressure', 'mean'), slack=('slack', 'mean'),
        delay=('delay', 'mean'), pacedPercent=('paced', lambda x: 100 * x.mean()),
        skippedPercent=('skipped', lambda x: 100 * x.mean())).reset_index()
    peaks = d.groupby(['condition', 'run']).agg(
        peakPressure=('pressure', 'max'), maxQueueDepth=('realQueueDepth', 'max'),
        minSlack=('slack', 'min'))
    return len(spans), a, peaks


def tail(d, condition):
    """The sub-1% decisions of one condition, with the saturation context the
    prose is required to carry beside the minimum.  AGENTS.md forbids letting
    the number stand bare: it reads as a lucky escape without the state that
    produced it and without the claim limit."""
    x = d[(d['condition'] == condition) & (d['slack'] < TAIL)].copy()
    if not len(x):
        return 'no decision under %g%% of the budget' % TAIL
    wait = (pd.to_numeric(x['draftStartUptimeMs'], errors='coerce')
            - pd.to_numeric(x['decisionUptimeMs'], errors='coerce'))
    x['waitPercent'] = 100.0 * wait / x['captureTimeoutMs']
    budget = x['captureTimeoutMs'].iloc[0]
    lines = ['%d decisions under %g%% of the budget; the tightest kept %.2f%% (%d ms)'
             % (len(x), TAIL, x['slack'].min(), round(x['slack'].min() / 100.0 * budget)),
             '  queued Draft work %.0f-%.0f%%, queue wait %.0f-%.0f%%, overheat level %d-%d'
             % (x['pressure'].min(), x['pressure'].max(), x['waitPercent'].min(),
                x['waitPercent'].max(), x['shotOverheatLevel'].min(),
                x['shotOverheatLevel'].max()),
             '  paced %d, optional stage skipped %d, either %d, neither %d'
             % (x['paced'].sum(), x['skipped'].sum(), x['either'].sum(),
                (~x['either']).sum())]
    for _, r in x[~x['either']].iterrows():
        run = d[(d['run'] == r['run'])].sort_values('runShotIndex')
        before = run[run['runShotIndex'].between(r['runShotIndex'] - 3, r['runShotIndex'] - 1)]
        after = run[run['runShotIndex'] > r['runShotIndex']]
        lines.append('  untouched: run %s capture %d, slack %.2f%%; the three preceding '
                     'captures were paced %s ms; admission skipped from capture %s onward'
                     % (r['runId'], r['runShotIndex'], r['slack'],
                        '/'.join('%d' % v for v in before['delay']),
                        after.loc[after['skipped'], 'runShotIndex'].min()
                        if after['skipped'].any() else 'never'))
    return '\n'.join(lines)


def regulation(d):
    """Change in queue pressure over the next capture, paced against unpaced,
    within a pressure band.  An association: pacing is not randomly assigned."""
    x = d.copy()
    x['nextPressure'] = x.groupby('run')['pressure'].shift(-1)
    x = x.dropna(subset=['nextPressure'])
    x['step'] = x['nextPressure'] - x['pressure']
    return x.groupby(['band', 'paced'])['step'].agg(['size', 'mean', 'median']).round(2)


def main():
    write = '--no-write' not in sys.argv
    d = load()
    d['band'] = d['pressure'].map(band_of)

    print('%d gating decisions over %d runs (%d devices, %d capture conditions); '
          '%d timed out.' % (len(d), d['run'].nunique(), d['device'].nunique(),
                             len(CONDITIONS), int((d['captureTimedOut'] == True).sum())))

    resp, cov = response(d), coverage(d)
    print('\n=== panel (a) response by Draft queue pressure ===')
    print(resp.round(1).to_string(index=False))
    print('\n=== panel (b) coverage of the thin-margin captures ===')
    print(cov.round(1).to_string(index=False))

    ld = lead(d)
    print('\n=== lead over the first capture of a run under 10% margin ===')
    print(ld.groupby('condition').agg(runs=('run', 'size'),
                                      pacedBefore=('pacedBefore', 'mean'),
                                      leadP50=('leadCaptures', 'median')).round(2).to_string())

    count, aligned, peaks = episodes(d)
    print('\n=== %d queue-pressure episodes, capture-aligned on the onset ===' % count)
    print(aligned.round(2).to_string(index=False))
    print('\nper-run peak queue pressure (%% of budget):')
    print(peaks.groupby('condition').agg(
        runs=('peakPressure', 'size'), p50=('peakPressure', 'median'),
        p95=('peakPressure', lambda x: x.quantile(.95)), max=('peakPressure', 'max'),
        over80=('peakPressure', lambda x: int((x > 80).sum())),
        maxQueueDepth=('maxQueueDepth', 'max')).round(1).to_string())

    print('\n=== change in queue pressure over the next capture (association) ===')
    print(regulation(d).to_string())

    print('\n=== thin-margin tail, per condition ===')
    for condition in CONDITIONS:
        print('%s: %s' % (condition, tail(d, condition)))

    if write:
        # Only the two frames behind the printed cells are written.  No .tex
        # reads them -- the table's values are typed in -- so they exist as the
        # provenance of those values, one row per printed row, cheap to diff.
        # The episode and per-run peak frames stay on stdout: the prose quotes
        # three numbers from them and the frames themselves are not worth
        # carrying in the repository.
        os.makedirs(OUT, exist_ok=True)
        resp.to_csv(os.path.join(OUT, 'pressure_response.csv'), index=False)
        cov.to_csv(os.path.join(OUT, 'thin_margin_coverage.csv'), index=False)
        print('\nwrote %s' % OUT)


if __name__ == '__main__':
    main()
