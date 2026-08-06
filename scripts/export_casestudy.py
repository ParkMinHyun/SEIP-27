"""Export the case-study traces used by figures/fig_casestudy_*.tex.

The workbooks are produced by CaptureMetricsExcelExporter in the private ML
implementation (commit 99aae0a).  They now live in this repository, so the
default source is data/ablation_sampling/ -- the balanced copy the RQ1 tables
report from, which keeps the case study's peer statistics computed over the
same runs as those tables.  data/ablation_original/ holds the untrimmed source
and can be passed as the first argument (or through CASESTUDY_SRC) to see what
the trim costs; the peer set there is larger, so the numbers differ and the
table that quotes them has to say which folder it used.

Each condition is split across two workbook parts that number their runs
independently, so runs are keyed "<part>:<runId>" throughout.  Sessions that
recorded a Capture Timeout are excluded.

The session shown in each figure is not hand-picked: it is the unique session
that survives the mechanism-coverage filter implemented in `select()` below.
A condition that no longer yields exactly one such session is reported and
skipped rather than exported from -- see main().

One committed artifact is deliberately NOT reproduced here.  The queue depth in
data/case_study/12mp_normal_backlog.csv counts the Draft currently being
processed as well as those waiting, which the workbook column `realQueueDepth`
does not: on the plotted run the file is that column plus one at every capture
except 1, 5, 16 and 30, where nothing is in service.  The file also carries a
shot-2 backlog of 650 ms that `realBacklogMs` leaves empty.  Rewriting it from
these workbooks therefore drops a capture and lowers the staircase by one, so
the writer below leaves an existing backlog CSV alone; set
CASESTUDY_WRITE_BACKLOG=1 to overwrite it on purpose.
"""

import os
import sys
import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = (sys.argv[1] if len(sys.argv) > 1
       else os.environ.get('CASESTUDY_SRC',
                           os.path.join(REPO, 'data', 'ablation_sampling')))
OUT = os.path.join(REPO, 'data', 'case_study')
WRITE_BACKLOG = bool(os.environ.get('CASESTUDY_WRITE_BACKLOG'))

CONDITIONS = {
    '12mp_normal': dict(
        workbooks=['48U_metrics_12MP_normal_0803_1.xlsx',
                   '48U_metrics_12MP_normal_0803_2.xlsx'],
        # the 12MP condition never leaves the MP12 bucket
        require_size=None,
    ),
    '24mp_memory': dict(
        workbooks=['48U_metrics_24MP_memory_0803_1.xlsx',
                   '48U_metrics_24MP_memory_0803_2.xlsx'],
        # exclude the Lv5-6 production MP12 resolution fallback
        require_size='MP24',
    ),
}


def read_condition(cfg):
    """Concatenate the workbook parts, keying every run by "<part>:<runId>"."""
    traces, summaries = [], []
    for part, book in enumerate(cfg['workbooks'], start=1):
        path = os.path.join(SRC, book)
        t = pd.read_excel(path, sheet_name='CaseStudyTrace')
        s = pd.read_excel(path, sheet_name='RQ3Summary')
        for df in (t, s):
            df['runKey'] = '%d:' % part + df.runId.astype(str)
        traces.append(t)
        summaries.append(s)
    return (pd.concat(traces, ignore_index=True),
            pd.concat(summaries, ignore_index=True))


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
    for key, d in trace.groupby('runKey'):
        r = evaluate(d)
        r['run'] = key
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
    skipped = []
    print('source: %s\n' % SRC)
    for name, cfg in CONDITIONS.items():
        trace, summary = read_condition(cfg)
        chosen, funnel, allruns = select(trace, cfg['require_size'])

        print('=== %s (%s)' % (name, ', '.join(cfg['workbooks'])))
        print('  sessions: %d' % allruns.run.nunique())
        for c, n, runs in funnel:
            print('  after %-14s -> %2d %s' % (c, n, runs))
        if len(chosen) != 1:
            # The single surviving session is what makes the case study a
            # filter result rather than a pick, so an ambiguous condition is
            # left unexported instead of resolved by a tie-break here.
            print('  !! expected exactly one eligible session, got %s'
                  '  -- nothing exported for this condition'
                  % sorted(chosen.run.tolist()))
            skipped.append(name)
            print()
            continue
        sel = chosen.iloc[0]
        run = sel.run
        print('  selected run %s (start Lv%d, %s)'
              % (run, sel.startLevel, sel.sizeBucket))
        print('  pacing@%s bokehSkip@%s relax %s-%s react@%s filterSkip@%s'
              % (sel.pacing, sel.bokehSkip, sel.relax, sel.relaxEnd,
                 sel.react, sel.filterSkip))

        d = trace[trace.runKey == run].sort_values('runShotIndex')
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
        # queue_depth here is the waiting count only; the committed file counts
        # the Draft in service too (module docstring), so an existing one is
        # kept rather than silently downgraded.
        backlog = os.path.join(OUT, '%s_backlog.csv' % name)
        if WRITE_BACKLOG or not os.path.exists(backlog):
            write(backlog,
                  out.loc[out.backlog_ms.notna(), ['shot', 'backlog_ms', 'queue_depth']])
        else:
            print('  kept  %s_backlog.csv (in-service queue-depth convention; '
                  'CASESTUDY_WRITE_BACKLOG=1 to replace)' % name)
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
        to = trace.groupby('runKey').captureTimedOut.any()
        S = summary[(summary.isComplete30ShotRun == True)
                    & (~summary.runKey.map(to).fillna(False))]
        peers = S[(S.startingOverheatLevel == sel.startLevel)
                  & (S.sizeBucket == sel.sizeBucket)]
        tr = S[S.runKey == run].iloc[0]
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
        print('  peers (Lv%d, %s), n=%d: %s'
              % (sel.startLevel, sel.sizeBucket, len(peers),
                 sorted(peers.runKey.tolist())))
        print(cmp.to_string(index=False))
        print()

    if skipped:
        raise SystemExit('no unique eligible session for: %s' % ', '.join(skipped))


if __name__ == '__main__':
    main()
