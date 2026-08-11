"""RQ1 full-controller summary: per-run capture and transition counts.

Reproduces the M, S, Activated and d P50 columns of
tables/tab_rq1_end_to_end_summary.tex from the balanced Full arm in
data/ablation_sampling/, and prints the percentage form the table used before
the 2026-08-11 revision beside the count form it uses now.  Both forms come from
the same pass, so the printout is also the proof that the unit change moved no
underlying number.

  M / S       captures in the first H on which the node EXECUTED
              (positive observed duration), averaged over the ten runs.
              Denominator H = 5 or 30.
  Activated   observed eligible outgoing-shot intervals with
              transitionDelayMs > 0, averaged over the ten runs.  A H-capture
              prefix holds at most H-1 transitions, so the base is 4 or 29 --
              NOT 5 or 30.
  d P50       inclusive median of the positive transitionDelayMs values,
              pooled over decisions rather than averaged over runs.

Run:  python scripts/rq1_summary_counts.py
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMP = os.path.join(ROOT, 'data', 'ablation_sampling')
BASE = os.path.join(SAMP, '48U_metrics_{cond}_0803_{i}.xlsx')
CONDITIONS = ['12MP_normal', '24MP_memory']
HORIZONS = (5, 30)


def truthy(s):
    """12MP workbooks store TRUE/FALSE strings, 24MP workbooks store 1.0/0.0."""
    return s.astype(str).str.strip().str.lower().isin(['true', '1', 'yes', '1.0'])


def load(cond):
    """Both parts of the condition, with runId namespaced by part."""
    runs, pacing = [], []
    for i in (1, 2):
        path = BASE.format(cond=cond, i=i)
        for sheet, sink in (('RQ1Runs', runs), ('RQ3Pacing', pacing)):
            df = pd.read_excel(path, sheet_name=sheet)
            df['key'] = f'{i}-' + df['runId'].astype(str)
            sink.append(df)
    return pd.concat(runs, ignore_index=True), pd.concat(pacing, ignore_index=True)


def cell(pacing, keys, horizon):
    n_runs = len(keys)
    prefix = pacing[pacing['runShotIndex'] <= horizon]
    out = {}
    for name, col in (('M', 'bokehExecuted'), ('S', 'filterExecuted')):
        executed = int(truthy(prefix[col]).sum())
        out[name] = (executed / n_runs, 100.0 * executed / (n_runs * horizon))
    delay = pd.to_numeric(prefix['transitionDelayMs'], errors='coerce')
    eligible, positive = delay.notna(), (delay > 0) & delay.notna()
    out['A'] = (int(positive.sum()) / n_runs,
                100.0 * positive.sum() / eligible.sum() if eligible.sum() else float('nan'))
    values = delay[positive]
    out['d'] = float(np.percentile(values, 50)) if len(values) else float('nan')
    out['base'] = int(eligible.sum()) // n_runs
    return out


def main():
    for cond in CONDITIONS:
        runs, pacing = load(cond)
        runs = runs[truthy(runs['includedForRq1'])]
        print(f'\n=== {cond}')
        print(f'{"lv":>3} {"N":>3} | ' + ' | '.join(
            f'{f"M@{h}":>12} {f"S@{h}":>12} {f"A@{h}":>12} {f"d@{h}":>7}' for h in HORIZONS))
        for level, group in runs.groupby('startingOverheatLevel'):
            keys = set(group['key'])
            part = pacing[pacing['key'].isin(keys)]
            assert part['key'].nunique() == len(keys), (cond, level)
            line = f'{int(level):>3} {len(keys):>3} | '
            chunks = []
            for h in HORIZONS:
                c = cell(part, keys, h)
                chunks.append(' '.join(
                    f'{c[k][0]:>5.1f} ({c[k][1]:>4.1f}%)' for k in ('M', 'S', 'A')) +
                    f' {c["d"]:>7.1f}')
            print(line + ' | '.join(chunks))
        print('   printed as: count (the percentage the table used before 2026-08-11);'
              ' Activated base is 4 @5 and 29 @30.')


if __name__ == '__main__':
    main()
