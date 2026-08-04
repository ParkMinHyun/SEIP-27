"""Export the case-study traces used by figures/fig_casestudy_*.tex.

Source workbooks are produced by CaptureMetricsExcelExporter in the private ML
implementation (commit 99aae0a) and are not committed to this repository.
Set CASESTUDY_SRC to the directory that holds the two workbooks, or pass it as
the first argument.  Sessions that recorded a Capture Timeout are excluded.

The session shown in each figure is not hand-picked: it is the unique session
that survives the mechanism-coverage filter implemented in `select()` below.
"""

import os
import sys
import numpy as np
import pandas as pd

SRC = (sys.argv[1] if len(sys.argv) > 1
       else os.environ.get('CASESTUDY_SRC',
                           r'C:\Users\sal_eunki\Desktop\ML\data\0803_FULL'))
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'data', 'casestudy')

CONDITIONS = {
    '12mp_normal': dict(
        workbook='SM-S948U_metrics_12MP_normal_0803.xlsx',
        # the 12MP condition never leaves the MP12 bucket
        require_size=None,
    ),
    '24mp_memory': dict(
        workbook='SM-S948U_metrics_24MP_memory_0803.xlsx',
        # exclude the Lv5-6 production MP12 resolution fallback
        require_size='MP24',
    ),
}


def zero_blocks(shots, delay):
    blocks, start = [], None
    for i, v in enumerate(delay):
        if v == 0:
            start = shots[i] if start is None else start
        elif start is not None:
            blocks.append((start, shots[i - 1]))
            start = None
    if start is not None:
        blocks.append((start, shots[-1]))
    return blocks


def evaluate(d):
    """Apply the mechanism-coverage criteria to one session."""
    d = d.sort_values('runShotIndex')
    s = d.runShotIndex.values
    delay = d.appliedDelayMs.fillna(0).values.astype(float)
    bokeh = d.bokehExecuted.fillna(True).values.astype(bool)
    filt = d.filterExecuted.fillna(True).values.astype(bool)
    first = lambda m: int(s[m].min()) if m.any() else None

    r = dict(shots=int(s.max()),
             timeout=bool(d.captureTimedOut.fillna(False).any()),
             watchdog=bool(d.captureWatchdogFailed.fillna(False).any()),
             pacing=first(delay > 0),
             bokehSkip=first(~bokeh),
             filterSkip=first(~filt),
             sizeBucket=d.sizeBucket.iloc[0],
             startLevel=int(d.startingOverheatLevel.iloc[0]))

    # C1 complete, timeout-free session
    r['c1'] = r['shots'] == 30 and not r['timeout'] and not r['watchdog']
    # C2 pacing activates before the first optional-stage demotion
    r['c2'] = bool(r['pacing'] and r['bokehSkip'] and r['pacing'] < r['bokehSkip'])
    # C3 Bokeh and Filter are demoted at distinct, ordered captures
    r['c3'] = bool(r['bokehSkip'] and r['filterSkip'] and r['bokehSkip'] < r['filterSkip'])
    r['c4'] = r['c5'] = False
    r['relax'] = r['relaxEnd'] = r['react'] = None
    if r['c2'] and r['c3']:
        win = (s >= r['bokehSkip']) & (s < r['filterSkip'])
        for a, b in zero_blocks(s[win], delay[win]):
            if b - a + 1 < 2:
                continue
            after = (s > b) & (s < r['filterSkip'])
            if (delay[after] > 0).any():
                # C4 pacing relaxes to zero for >= 2 captures after the demotion
                # C5 pacing reactivates before the second demotion
                r['relax'], r['relaxEnd'] = int(a), int(b)
                r['react'] = int(s[after][delay[after] > 0][0])
                r['c4'] = r['c5'] = True
                break
    r['eligible'] = all(r[c] for c in ('c1', 'c2', 'c3', 'c4', 'c5'))
    return r


def select(trace, require_size):
    rows = []
    for run, d in trace.groupby('runId'):
        r = evaluate(d)
        r['run'] = int(run)
        rows.append(r)
    R = pd.DataFrame(rows)
    funnel = []
    keep = pd.Series(True, index=R.index)
    for c in ('c1', 'c2', 'c3', 'c4', 'c5'):
        keep &= R[c]
        funnel.append((c, int(keep.sum()), sorted(R.run[keep].tolist())))
    if require_size:
        keep &= (R.sizeBucket == require_size)
        funnel.append(('size==%s' % require_size, int(keep.sum()),
                       sorted(R.run[keep].tolist())))
    return R[keep], funnel, R


def write(path, df):
    df.to_csv(path, index=False, float_format='%.0f')
    print('  wrote', os.path.relpath(path, OUT), len(df), 'rows')


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, cfg in CONDITIONS.items():
        book = os.path.join(SRC, cfg['workbook'])
        trace = pd.read_excel(book, sheet_name='CaseStudyTrace')
        summary = pd.read_excel(book, sheet_name='RQ3Summary')
        chosen, funnel, allruns = select(trace, cfg['require_size'])

        print('=== %s (%s)' % (name, cfg['workbook']))
        print('  sessions: %d' % allruns.run.nunique())
        for c, n, runs in funnel:
            print('  after %-14s -> %2d %s' % (c, n, runs))
        if len(chosen) != 1:
            raise SystemExit('expected exactly one eligible session, got %s'
                             % sorted(chosen.run.tolist()))
        sel = chosen.iloc[0]
        run = int(sel.run)
        print('  selected run %d (start Lv%d, %s)'
              % (run, sel.startLevel, sel.sizeBucket))
        print('  pacing@%s bokehSkip@%s relax %s-%s react@%s filterSkip@%s'
              % (sel.pacing, sel.bokehSkip, sel.relax, sel.relaxEnd,
                 sel.react, sel.filterSkip))

        d = trace[trace.runId == run].sort_values('runShotIndex')
        out = pd.DataFrame({
            'shot': d.runShotIndex.values,
            'delay_ms': d.appliedDelayMs.fillna(0).values,
            'backlog_ms': d.realBacklogMs.values,
            'queue_depth': d.realQueueDepth.values,
            'margin_ms': d.timeoutMarginMs.values,
            'overheat': d.shotOverheatLevel.values,
            's2s_ms': d.shotToShotTimeMs.values,
            'draft_ms': d.draftSequenceDurationMs.values,
            'width_px': d.resultImageWidth.values,
        })
        write(os.path.join(OUT, '%s_delay.csv' % name), out[['shot', 'delay_ms']])
        write(os.path.join(OUT, '%s_backlog.csv' % name),
              out.loc[out.backlog_ms.notna(), ['shot', 'backlog_ms', 'queue_depth']])
        write(os.path.join(OUT, '%s_margin.csv' % name), out[['shot', 'margin_ms']])

        # stage-execution strip: lane 2 = Bokeh (multi-frame), lane 1 = Filter
        stages = {'bokeh': (d.bokehExecuted.fillna(True).values.astype(bool), 2),
                  'filter': (d.filterExecuted.fillna(True).values.astype(bool), 1)}
        for stage, (executed, lane) in stages.items():
            for label, mask in (('exec', executed), ('skip', ~executed)):
                write(os.path.join(OUT, '%s_%s_%s.csv' % (name, stage, label)),
                      pd.DataFrame({'shot': out.shot[mask], 'lane': lane}))

        # peer comparison: same condition, complete + timeout-free, same start
        # level and same size bucket as the selected session
        to = trace.groupby('runId').captureTimedOut.any()
        S = summary[(summary.isComplete30ShotRun == True)
                    & (~summary.runId.map(to).fillna(False))]
        peers = S[(S.startingOverheatLevel == sel.startLevel)
                  & (S.sizeBucket == sel.sizeBucket)]
        tr = S[S.runId == run].iloc[0]
        metrics = ['totalDelayMs', 'pacedPercent', 'timeoutMarginP5Ms',
                   'burstSpanMs', 'bokehExecutionPercent', 'filterExecutionPercent']
        cmp = pd.DataFrame([dict(metric=m,
                                 selected=float(tr[m]),
                                 peer_median=float(peers[m].median()),
                                 peer_min=float(peers[m].min()),
                                 peer_max=float(peers[m].max()),
                                 peer_n=int(len(peers)))
                            for m in metrics])
        cmp.to_csv(os.path.join(OUT, '%s_peer_comparison.csv' % name),
                   index=False, float_format='%.1f')
        print('  peers (Lv%d, %s): %s' % (sel.startLevel, sel.sizeBucket,
                                          sorted(peers.runId.tolist())))
        print(cmp.to_string(index=False))
        print()


if __name__ == '__main__':
    main()
