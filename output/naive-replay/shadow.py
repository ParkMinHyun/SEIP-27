"""At every optional-stage admission of a naive arm, also evaluate the deployed
model (ported, learning from the arm's own trajectory) as a shadow.  For the
admissions that ended in a deadline miss, ask whether the point estimate and
the residual-calibrated upper estimate would each have rejected the stage."""
import pickle
import numpy as np, pandas as pd
from sim import run_arm
P = pickle.load(open('prep_late.pkl', 'rb'))
ARMS = {'draft mean3': dict(arm='NAIVE', N=3, stat='mean'),
        'stage mean3': dict(arm='STAGE', N=3, stat='mean'),
        'stage mean3+ovh': dict(arm='STAGE', N=3, stat='mean', ovh=True)}
rows = []
for name, kw in ARMS.items():
    for k, prep in P.items():
        log = []
        run_arm(prep, log=log, **kw)
        L = pd.DataFrame(log); L['dev'], L['cond'], L['arm'] = k[0], k[1], name
        rows.append(L)
L = pd.concat(rows, ignore_index=True)
L.to_pickle('shadow_log.pkl')
# model decisions only (not forced by sticky demotion), naive admitted, forecast known
A = L[~L.sticky & L.adm & L.f.notna()].copy()
A['unsafe'] = A.G > A['T']            # admitted stage whose remaining work overran the live budget
A['U_rej'] = A.sU > A['T']; A['P_rej'] = A.sP > A['T']
out = []
for (arm, cond), d in A.groupby(['arm', 'cond']):
    u = d[d.unsafe]
    out.append(dict(arm=arm, cond=cond, admits=len(d), unsafe=len(u),
                    unsafe_U_rejects=int(u.U_rej.sum()), unsafe_P_rejects=int(u.P_rej.sum()),
                    safe_U_rejects=int(d[~d.unsafe].U_rej.sum()),
                    under_med=(u.G - u.f).median(), U_minus_P_med=(u.sU - u.sP).median()))
S = pd.DataFrame(out); S.to_csv('results/B_shadow_residual.csv', index=False)
pd.set_option('display.width', 250)
print(S.round(0).to_string(index=False))
# coverage on all naive-admitted decisions
for (arm, cond), d in A.groupby(['arm', 'cond']):
    print(arm, cond, 'naive cov %.1f  shadowP cov %.1f  shadowU cov %.1f' % (100*(d.G<=d.f).mean(), 100*(d.G<=d.sP).mean(), 100*(d.G<=d.sU).mean()))
