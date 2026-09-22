"""Stage-wise mean-3 with larger fixed margins, per device, three imputation modes."""
import pickle, random
import numpy as np, pandas as pd
from sim import run_arm
P = pickle.load(open('prep_late.pkl', 'rb'))
rows = []
for k, prep in P.items():
    for m in (0, 150, 300, 400, 500, 700, 1000):
        for imp in (None, 'min5', 'med5'):
            d = run_arm(prep, arm='STAGE', N=3, stat='mean', margin=m, rng=imp, ovh=True)
            rows.append(dict(dev=k[0], cond=k[1], margin=m, imp=str(imp), miss=(d.margin < 0).sum(),
                             runs=d[d.margin < 0].run.nunique(), M=d.bokeh.sum(), S=d.filt.sum(), n=len(d)))
    d = run_arm(prep, arm='DEP')
    rows.append(dict(dev=k[0], cond=k[1], margin='DEP', imp='None', miss=(d.margin < 0).sum(), runs=0, M=d.bokeh.sum(), S=d.filt.sum(), n=len(d)))
R = pd.DataFrame(rows)
R.to_csv('stage_margin_sweep.csv', index=False)
pd.set_option('display.width', 250)
g = R.groupby(['cond', 'margin', 'imp'])[['miss', 'runs', 'M', 'S', 'n']].sum()
g['M%'] = 100 * g.M / g.n; g['S%'] = 100 * g.S / g.n
print(g[['miss', 'runs', 'M%', 'S%']].round(1).unstack('imp').to_string())
print(R[R.imp == 'None'].pivot_table(index=['cond', 'margin'], columns='dev', values='miss', aggfunc='sum').to_string())
