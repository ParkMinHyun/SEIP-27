"""Part C, arm sweep: the manuscript pacing rule with its inputs swapped.

At every recorded pacing decision, eq:pacing is evaluated three ways -- with the
deployed inputs, with a naive recent-N statistic, and with the realized inputs
(retrospective matched-policy reference).  Only the inputs change; arrival
times, realized draft durations and the recorded delays stay pinned to the
trace.  This is a one-step open-loop swap, not a pacing counterfactual.

    python partA.py && python partC_pacing_arms.py   -> results/C_pacing_arms.csv
"""
import os
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results', 'C_pacing_arms.csv')

P = pd.read_pickle(os.path.join(HERE, 'pac.pkl'))
P = P[P.hist_n > 0].copy()
for c in P.columns:
    if c not in ('dev', 'cond'):
        P[c] = pd.to_numeric(P[c], errors='coerce')

# eq:pacing in its manuscript form: no backlog-growth term, no cap.
rule = lambda B, C, T: np.ceil(np.maximum(0, B + 2 * C - np.maximum(T, 0)) / 2)

D = P.dropna(subset=['two_true', 'T', 'B_dep', 'C_dep']).copy()
D['d_ref'] = rule(D.B_true, D.two_true / 2, D['T'])

ARMS = [('current', 'B_dep', 'C_dep')]
ARMS += [(f'mean{N}', f'B_mean{N}', f'C_mean{N}') for N in (1, 3, 5, 10)]
ARMS += [(f'max{N}', f'B_max{N}', f'C_max{N}') for N in (3, 5, 10)]

rows = []
for cond, d in D.groupby('cond'):
    runs = d.groupby(['dev', 'run']).ngroups   # runIds repeat across devices
    need = d.d_ref > 0
    for arm, bc, cc in ARMS:
        x = rule(d[bc], d[cc], d['T'])
        pos = x[x > 0]
        berr = d[bc] - d.B_true            # > 0: estimate above realized backlog
        rows.append(dict(
            cond=cond, arm=arm, n=len(d), runs=runs,
            engaged=int((x > 0).sum()), engaged_pct=100 * (x > 0).mean(),
            delay_s_per_run=x.sum() / 1000 / runs,
            total_delay_s=x.sum() / 1000, per_decision_ms=x.mean(),
            pos_median_ms=pos.median() if len(pos) else 0,
            pos_p95_ms=pos.quantile(.95) if len(pos) else 0,
            ref_engaged=int(need.sum()),
            not_engaged_when_ref_did=int(((x == 0) & need).sum()),
            not_engaged_pct=100 * ((x == 0) & need).sum() / need.sum(),
            engaged_when_ref_did_not=int(((x > 0) & ~need).sum()),
            shortfall_s=np.maximum(0, d.d_ref - x).sum() / 1000,
            excess_s=np.maximum(0, x - d.d_ref).sum() / 1000,
            backlog_err_median_ms=berr.median(), backlog_mae_ms=berr.abs().mean(),
            backlog_cover_pct=100 * (berr >= 0).mean(),
            reserve_median_ms=d[cc].median(),
            reserve_pctile_vs_realized=100 * (d[cc] > d.two_true / 2).mean(),
            engage_agree_recorded_pct=100 * ((x > 0) == (d.d_app > 0)).mean(),
        ))

R = pd.DataFrame(rows)
R.to_csv(OUT, index=False)
pd.set_option('display.width', 240)
print(R.round(1).to_string(index=False))
print('\nrecorded applied delay, s per run:',
      (D.groupby('cond').apply(lambda g: g.d_app.sum() / 1000 / g.groupby(['dev', 'run']).ngroups,
                               include_groups=False)).round(2).to_dict())
print('wrote', OUT)
