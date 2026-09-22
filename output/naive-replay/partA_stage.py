"""Open-loop: stage-wise mean-3 forecast at recorded Bokeh/Filter admission points,
against realized time to draft end; compared with the recorded U, and the size of
U's implicit margin (U - P-hat) by stage position and condition."""
import pickle
import numpy as np, pandas as pd
P = pickle.load(open('prep_late.pkl', 'rb'))
W = pickle.load(open('wb.pkl', 'rb'))
rows = []
for (dev, cond), prep in P.items():
    ar = W[(dev, cond)]['AdmissionReplay'].set_index(['captureIndex', 'nodeOrder'])
    for run, R in prep.items():
        hist = {}; ovh = []
        for c in R['caps']:
            cum = 0.0
            executed = {n['key'] for n in c['nodes'] if n['fdur']}
            for j, n in enumerate(c['nodes']):
                t_node = c['fstart'] + n['pre'] + cum
                if n['key'] in ('BOKEH()', 'FILTER()') and n['fdur'] and all(k in executed for k in n['seq']):
                    def est(k, N=3):
                        h = [d for e, d in hist.get(k, []) if e <= t_node][-N:]
                        return float(np.mean(h)) if h else 0.0
                    f = sum(est(k) for k in n['seq'])
                    oh = [o for e, o in ovh if e <= t_node][-3:]
                    try:
                        a = ar.loc[(c['cap'], j + 1)]
                        U, Ph, T = a.beforeSequencePredictedUpperBoundMs, a.beforeSequencePredictedDurationMs, a.beforeBudgetMs
                    except KeyError:
                        U = Ph = T = np.nan
                    if f > 0 and pd.notna(Ph) and Ph > 0:
                        rows.append(dict(dev=dev, cond=cond, run=run, shot=c['shot'], stage=n['key'][:6], level=c['level'],
                                         G=c['fend'] - t_node, st=f, st_ovh=f + (np.mean(oh) if oh else 0), U=U, Ph=Ph, T=T))
                cum += n['fdur'] or 0.0
            for n in c['nodes']:
                if n['fdur']:
                    hist.setdefault(n['key'], []).append((c['fend'], n['fdur']))
            ovh.append((c['fend'], c['post']))
D = pd.DataFrame(rows)
D.to_pickle('partA_stage.pkl')
pd.set_option('display.width', 250)
out = []
for (cond, stage), d in D.groupby(['cond', 'stage']):
    r = dict(cond=cond, stage=stage, n=len(d))
    for e, v in [('U', d.U), ('P-hat', d.Ph), ('stage mean3', d.st), ('stage mean3+ovh', d.st_ovh),
                 ('+300', d.st_ovh + 300), ('+500', d.st_ovh + 500)]:
        r[e] = 100 * (d.G <= v).mean()
    r['need_p85'] = (d.G - d.st_ovh).quantile(.85)   # additive margin needed for 85% coverage
    r['need_p95'] = (d.G - d.st_ovh).quantile(.95)
    r['U-Ph med'] = (d.U - d.Ph).median(); r['U-Ph p90'] = (d.U - d.Ph).quantile(.9)
    r['rem med'] = d.st_ovh.median()
    out.append(r)
print(pd.DataFrame(out).round(1).to_string(index=False))
# U implicit margin vs thermal level
print((D.assign(m=D.U - D.Ph).groupby(['cond', 'level']).m.median().unstack().round(0)).to_string())
print((D.assign(m=D.G - D.st_ovh).groupby(['cond', 'level']).m.quantile(.9).unstack().round(0)).to_string())
