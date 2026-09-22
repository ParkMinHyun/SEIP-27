import pickle, numpy as np, pandas as pd
from port import *
W = pickle.load(open('wb.pkl', 'rb'))
res = []
for (dev, cond), x in W.items():
    N = load_nodes(x)
    t = x['CaseStudyTrace']
    for run, g in t.groupby('runId'):
        pr = Predictor()
        for cap in g.sort_values('runShotIndex').captureIndex:
            rows = N[N.captureIndex == cap]
            decisions = {}
            durs = {}
            for _, r in rows.iterrows():
                seq = parse_seq(r.workloadSequenceKey)
                if not seq:
                    continue
                P, U, pm = pr.decide(seq)
                res.append((dev, cond, run, cap, r.workloadKey, P, U, r.sequencePredictedDurationMs, r.sequencePredictedUpperBoundMs))
                decisions[seq] = pm
                if r.workloadKey in OPTIONAL:
                    rsv = tuple(k for k in seq if k.startswith('ENCODING'))
                    if rsv:
                        _, _, pm2 = pr.decide(rsv)
                        decisions[rsv] = pm2
                if pd.notna(r.durationMs):
                    durs[r.workloadKey] = max(0, int(r.durationMs))
            pr.learn(durs, list(decisions.items()))
R = pd.DataFrame(res, columns=['dev', 'cond', 'run', 'cap', 'key', 'P', 'U', 'Prec', 'Urec'])
R['eP'] = (R.P - R.Prec).abs(); R['eU'] = (R.U - R.Urec).abs()
print(R.groupby(['dev', 'cond'])[['eP', 'eU']].describe(percentiles=[.5, .9, .99]).round(3).T.to_string())
R.to_pickle('validate.pkl')
