"""Collect every number the report quotes into CSVs under ./out."""
import os, pickle, numpy as np, pandas as pd
os.makedirs('out', exist_ok=True)
W = pickle.load(open('wb.pkl', 'rb'))
# ---------- Part A admission forecast accuracy ----------
A = pd.read_pickle('adm.pkl')
sd = []
for (dev, cond), x in W.items():
    for sh, st in [('SecDualBokehNode', 'Bokeh'), ('SecFilterNode', 'Filter')]:
        n = x[sh][['captureIndex', 'durationMs']].rename(columns={'captureIndex': 'cap', 'durationMs': 'sdur'})
        sd.append(n.assign(dev=dev, cond=cond, stage=st))
A = A.merge(pd.concat(sd), on=['dev', 'cond', 'stage', 'cap'], how='left')
O = A[A.observed & A.admit & (A.hist_n > 0) & (A.Phat > 0)].copy()
rows = []
for (c, s), d in O.groupby(['cond', 'stage']):
    for e, lab in [('U', 'current: U (upper)'), ('Phat', 'current: P-hat (point)'), ('mean3', 'naive mean3'),
                   ('mean10', 'naive mean10'), ('max5', 'naive max5')]:
        err = d.G - d[e]
        rows.append(dict(cond=c, stage=s, estimator=lab, n=len(d), coverage_pct=100 * (err <= 0).mean(),
                         under_p95_ms=err.quantile(.95), over_median_ms=(-err).median()))
pa = pd.DataFrame(rows); pa.to_csv('out/A_admission_forecast.csv', index=False)
# Filter point vs Bokeh overrun
B = A[A.stage == 'Bokeh'][['dev', 'cond', 'run', 'cap', 'sdur']].rename(columns={'sdur': 'bdur'}).sort_values(['dev', 'cond', 'run', 'cap'])
B['btyp'] = B.groupby(['dev', 'cond', 'run']).bdur.transform(lambda s: s.shift().rolling(3, min_periods=1).mean())
F = A[A.stage == 'Filter'].merge(B, on=['dev', 'cond', 'run', 'cap'])
F = F[F.observed & F.admit & (F.hist_n > 0) & (F.Phat > 0) & (F.bdur > 0)].copy()
F['over'] = F.bdur - F.btyp
F['bin'] = pd.cut(F.over, [-1e9, -50, 50, 150, 1e9], labels=['faster (<-50ms)', 'typical (+-50ms)', 'overrun 50-150ms', 'overrun >150ms'])
rows = []
for (c, b), d in F.groupby(['cond', 'bin'], observed=True):
    for e, lab in [('U', 'current: U'), ('mean3', 'naive mean3'), ('max5', 'naive max5')]:
        err = d.G - d[e]
        rows.append(dict(cond=c, bokeh=b, estimator=lab, n=len(d), coverage_pct=100 * (err <= 0).mean(), under_p95_ms=err.quantile(.95)))
pf = pd.DataFrame(rows); pf.to_csv('out/A_filter_point_vs_bokeh_overrun.csv', index=False)
Fc = F.dropna(subset=['over'])
corr = dict(mean3=np.corrcoef(Fc.over, Fc.G - Fc.mean3)[0, 1], U=np.corrcoef(Fc.over, Fc.G - Fc.U)[0, 1])
# ---------- Part B ----------
for m in ('late', 'early'):
    pd.read_csv(f'summary_{m}.csv').to_csv(f'out/B_closed_loop_admission_{m}.csv', index=False)
# ---------- Part C pacing ----------
Pall = pd.read_pickle('pac.pkl'); Pall = Pall[Pall.hist_n > 0]
for c in Pall.columns:
    if c not in ('dev', 'cond'): Pall[c] = pd.to_numeric(Pall[c], errors='coerce')
# one-step delay under the manuscript rule eq:pacing, inputs swapped
P = Pall.dropna(subset=['two_true', 'T', 'B_dep', 'C_dep']).copy()
Tt = P['T']
rule = lambda B, C: np.ceil(np.maximum(0, B + 2 * C - np.maximum(Tt, 0)) / 2)
P['d_dep'] = rule(P.B_dep, P.C_dep); P['d_m3'] = rule(P.B_mean3, P.C_mean3)
P['d_x5'] = rule(P.B_max5, P.C_max5); P['d_h'] = rule(P.B_true, P.two_true / 2)
rows = []
for c, d in Pall.groupby('cond'):
    for e, lab in [('B_dep', 'current: backlog clock'), ('B_mean3', 'naive: count x mean3'), ('B_max5', 'naive: count x max5')]:
        err = d.B_true - d[e]
        rows.append(dict(cond=c, estimator=lab, n=err.notna().sum(), coverage_pct=100 * (err <= 0).mean(),
                         under_p95_ms=err.quantile(.95), mae_ms=err.abs().mean()))
pd.DataFrame(rows).to_csv('out/C_backlog_forecast.csv', index=False)
rows = []
for c, d in P.groupby('cond'):
    need = d.d_h > 0
    for e, lab in [('d_dep', 'current inputs'), ('d_m3', 'naive mean3 inputs'), ('d_x5', 'naive max5 inputs')]:
        rows.append(dict(cond=c, inputs=lab, n=len(d), engaged=(d[e] > 0).sum(), hindsight_engaged=need.sum(),
                         not_engaged_when_needed=((d[e] == 0) & need).sum(),
                         not_engaged_pct=100 * ((d[e] == 0) & need).sum() / need.sum(),
                         shortfall_s=np.maximum(0, d.d_h - d[e]).sum() / 1000, excess_s=np.maximum(0, d[e] - d.d_h).sum() / 1000))
pd.DataFrame(rows).to_csv('out/C_pacing_one_step.csv', index=False)
print(pa.round(1).to_string(index=False)); print(pf.round(1).to_string(index=False)); print(corr)
print(pd.read_csv('out/C_backlog_forecast.csv').round(1).to_string(index=False))
print(pd.read_csv('out/C_pacing_one_step.csv').round(1).to_string(index=False))
# population
R = pd.read_pickle('arms_late.pkl'); R = R[(R.seed == -1) & (R.armname == 'DEP')]
print(R.groupby(['cond', 'dev']).agg(runs=('run', 'nunique'), caps=('shot', 'size')))
