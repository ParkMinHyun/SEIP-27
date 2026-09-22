"""Stage-wise mean-3 (+ recent overhead) with a fixed multiplicative factor."""
import pickle
import numpy as np, pandas as pd
from sim import run_arm
P = pickle.load(open('prep_late.pkl', 'rb'))
rows = []
for k, prep in P.items():
    for sc in (1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 2.0):
        for imp in (None, 'min5', 'med5'):
            d = run_arm(prep, arm='STAGE', N=3, stat='mean', scale=sc, rng=imp, ovh=True)
            rows.append(dict(dev=k[0], cond=k[1], scale=sc, imp=str(imp), miss=(d.margin < 0).sum(),
                             runs=d[d.margin < 0].run.nunique(), M=d.bokeh.sum(), S=d.filt.sum(), n=len(d)))
R = pd.DataFrame(rows); R.to_csv('stage_scale_sweep.csv', index=False)
g = R.groupby(['cond', 'scale', 'imp'])[['miss', 'runs', 'M', 'S', 'n']].sum()
g['M%'] = 100 * g.M / g.n; g['S%'] = 100 * g.S / g.n
pd.set_option('display.width', 250)
print(g[['miss', 'runs', 'M%', 'S%']].round(1).unstack('imp').to_string())
print(R[R.imp == 'None'].pivot_table(index=['cond', 'scale'], columns='dev', values='miss', aggfunc='sum').to_string())
