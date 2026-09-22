import pickle, pandas as pd, numpy as np
from sim import run_arm
P = pickle.load(open('prep_late.pkl', 'rb'))
arms = [('DEP_P', dict(arm='DEP_P')), ('mean3', dict(arm='NAIVE', N=3, stat='mean')), ('max5', dict(arm='NAIVE', N=5, stat='max')),
        ('max10', dict(arm='NAIVE', N=10, stat='max')), ('mean3+100', dict(arm='NAIVE', N=3, stat='mean', margin=100)),
        ('mean3+300', dict(arm='NAIVE', N=3, stat='mean', margin=300))]
out = []
for k, prep in P.items():
    for name, kw in arms:
        for mode in ['min5', 'med5']:
            d = run_arm(prep, rng=mode, **kw)
            out.append(dict(cond=k[1], dev=k[0], arm=name, imp=mode, miss=(d.margin < 0).sum(),
                            miss_runs=d[d.margin < 0].run.nunique(), M=d.bokeh.sum(), S=d.filt.sum(), n=len(d)))
R = pd.DataFrame(out).groupby(['cond', 'arm', 'imp'])[['miss', 'miss_runs', 'M', 'S', 'n']].sum()
R['M%'] = 100 * R.M / R.n; R['S%'] = 100 * R.S / R.n
print(R[['miss', 'miss_runs', 'M%', 'S%']].round(1).unstack('imp').to_string())
