"""Stage-wise naive arms: remaining forecast = sum over the remaining stages of a
statistic of each stage's last N observed durations (same run, completed drafts)."""
import pickle, sys, random
import numpy as np, pandas as pd
from sim import run_arm
mode = sys.argv[1] if len(sys.argv) > 1 else 'late'
P = pickle.load(open(f'prep_{mode}.pkl', 'rb'))
ARMS = [('DEP', dict(arm='DEP')), ('DEP_P', dict(arm='DEP_P'))]
for N in (1, 3, 5, 10):
    ARMS.append((f'st_mean{N}', dict(arm='STAGE', N=N, stat='mean')))
for N in (3, 5, 10):
    ARMS.append((f'st_max{N}', dict(arm='STAGE', N=N, stat='max')))
ARMS.append(('st_mean3+ovh', dict(arm='STAGE', N=3, stat='mean', ovh=True)))
ARMS.append(('st_max5+ovh', dict(arm='STAGE', N=5, stat='max', ovh=True)))
for m in (50, 100, 150, 200, 300):
    ARMS.append((f'st_mean3+{m}', dict(arm='STAGE', N=3, stat='mean', margin=m)))
out = []
for k, prep in P.items():
    for name, kw in ARMS:
        seeds = [None] if kw['arm'] == 'DEP' else [None] + list(range(5))
        for sd in seeds:
            rng = None if sd is None else random.Random(sd)
            d = run_arm(prep, rng=rng, **kw)
            d['dev'], d['cond'], d['armname'], d['seed'] = k[0], k[1], name, (-1 if sd is None else sd)
            out.append(d)
        for imp in ('min5', 'med5'):
            if kw['arm'] == 'DEP':
                continue
            d = run_arm(prep, rng=imp, **kw)
            d['dev'], d['cond'], d['armname'], d['seed'] = k[0], k[1], name, imp
            out.append(d)
R = pd.concat(out, ignore_index=True)
R['seed'] = R.seed.astype(str)
R.to_pickle(f'arms_stage_{mode}.pkl')
rows = []
for (cond, arm), d in R.groupby(['cond', 'armname']):
    b = d[d.seed == '-1']
    sd = d[d.seed.isin([str(i) for i in range(5)])].groupby('seed').apply(lambda x: (x.margin < 0).sum(), include_groups=False)
    mn = d[d.seed == 'min5']; md = d[d.seed == 'med5']
    rows.append(dict(cond=cond, arm=arm, miss=(b.margin < 0).sum(), miss_runs=b[b.margin < 0].groupby(['dev', 'run']).ngroups,
                     seeds=f'{sd.min()}-{sd.max()}' if len(sd) else '', min5=(mn.margin < 0).sum() if len(mn) else '',
                     med5=(md.margin < 0).sum() if len(md) else '', thin70=(b.margin < 70).sum(), min_margin=b.margin.min(),
                     M=100 * b.bokeh.mean(), S=100 * b.filt.mean()))
S = pd.DataFrame(rows)
order = [a for a, _ in ARMS]
S['o'] = S.arm.map({a: i for i, a in enumerate(order)})
S = S.sort_values(['cond', 'o']).drop(columns='o')
S.to_csv(f'summary_stage_{mode}.csv', index=False)
pd.set_option('display.width', 250)
print(S.round(1).to_string(index=False))
