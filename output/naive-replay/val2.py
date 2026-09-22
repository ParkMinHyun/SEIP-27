import pickle, numpy as np, pandas as pd
from sim import run_arm
for mode in ['late', 'early']:
    P = pickle.load(open(f'prep_{mode}.pkl', 'rb'))
    for k, prep in P.items():
        f = run_arm(prep, 'FACT')
        d = run_arm(prep, 'DEP')
        e = (f.end - f.fend).abs()
        m = d.merge(f[['run', 'shot', 'bokeh', 'filt', 'margin']], on=['run', 'shot'], suffixes=('', '_f'))
        agreeB = (m.bokeh == m.bokeh_f).mean(); agreeF = (m.filt == m.filt_f).mean()
        me = (m.margin - m.fmargin)
        print(mode, k, 'FACT |end err| max %.1f p99 %.1f' % (e.max(), e.quantile(.99)),
              '| DEP agree B %.3f F %.3f' % (agreeB, agreeF),
              '| DEP margin err p50 %.0f p95abs %.0f' % (me.median(), me.abs().quantile(.95)),
              '| DEP misses %d, min margin %.0f (fact min %.0f) | B exec dep %.3f fact %.3f' % ((d.margin < 0).sum(), d.margin.min(), d.fmargin.min(), d.bokeh.mean(), m.bokeh_f.mean()))
