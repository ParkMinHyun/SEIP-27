import pickle, sys, random
import numpy as np, pandas as pd
from sim import run_arm
mode = sys.argv[1]
P = pickle.load(open(f'prep_{mode}.pkl', 'rb'))
ARMS = [('DEP', dict(arm='DEP')), ('DEP_P', dict(arm='DEP_P')), ('ALWAYS', dict(arm='ALWAYS'))]
for N in (1, 3, 5, 10):
    ARMS.append((f'mean{N}', dict(arm='NAIVE', N=N, stat='mean')))
for N in (3, 5, 10):
    ARMS.append((f'max{N}', dict(arm='NAIVE', N=N, stat='max')))
ARMS.append(('cmean3', dict(arm='NAIVE_C', N=3, stat='mean')))
ARMS.append(('cmax5', dict(arm='NAIVE_C', N=5, stat='max')))
for m in (50, 100, 150, 200, 300):
    ARMS.append((f'mean3+{m}', dict(arm='NAIVE', N=3, stat='mean', margin=m)))
out = []
for k, prep in P.items():
    for name, kw in ARMS:
        seeds = [None] if kw['arm'] in ('DEP',) else [None] + list(range(5))
        for sd in seeds:
            rng = None if sd is None else random.Random(sd)
            d = run_arm(prep, rng=rng, **kw)
            d['dev'], d['cond'], d['armname'], d['seed'] = k[0], k[1], name, (-1 if sd is None else sd)
            out.append(d)
R = pd.concat(out, ignore_index=True)
R.to_pickle(f'arms_{mode}.pkl')
print(len(R))
