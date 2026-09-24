"""Part D follow-up: does a fixed widening of a naive or point forecast transfer
across conditions and stage groups the way the residual-calibrated U does?
Threshold-free ranking (AUC) and per-cell tuned margins on the RQ3 audit pool."""
import pickle, os
import numpy as np, pandas as pd
from audit_rescore import forecast, unsafe, cells, arm, HERE, RES
D = pickle.load(open(os.path.join(HERE, 'audit_decisions.pkl'), 'rb'))
pd.set_option('display.width', 250)
CELLS = [('12MP normal', 'Multi-frame'), ('12MP normal', 'Single-frame'),
         ('24MP memory', 'Multi-frame'), ('24MP memory', 'Single-frame')]
FAMS = {'U': None, 'P-hat only': ('P', 1, 'mean'), 'draft mean-3': ('draft', 3, 'mean'),
        'draft max-5': ('draft', 5, 'max'), 'stage mean-3': ('stage', 3, 'mean'), 'stage max-5': ('stage', 5, 'max')}


def score(d, f):
    """forecast - budget; cold start (no forecast) scores -inf (always admitted)."""
    if f is None:
        return d['bound'] - d['budget'] if d['P'] > 0 else -np.inf
    fc = forecast(d, *f)
    return -np.inf if fc is None else fc - d['budget']


def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    gt = (pos[:, None] > neg[None, :]).sum(); eq = (pos[:, None] == neg[None, :]).sum()
    return (gt + 0.5 * eq) / (len(pos) * len(neg))


for label in ('sel', 'allp'):
    decs = D[label]
    print(f'\n=== {label}: threshold-free ranking of unsafe vs feasible (AUC of forecast - budget)')
    rows = []
    for name, f in FAMS.items():
        r = dict(arm=name)
        for cell in CELLS + [('ALL', 'ALL')]:
            g = decs if cell[0] == 'ALL' else [d for d in decs if (d['cond'], d['group']) == cell]
            s = [score(d, f) for d in g]
            u = [x for x, d in zip(s, g) if unsafe(d)]; ok = [x for x, d in zip(s, g) if not unsafe(d)]
            r[f'{cell[0][:4]} {cell[1][:5]}'] = auc(u, ok)
        rows.append(r)
    print(pd.DataFrame(rows).round(3).to_string(index=False))

    print(f'\n=== {label}: per-cell margin each family needs to reach U\'s unsafe admits in that cell')
    rows = []
    for name, f in FAMS.items():
        if f is None:
            continue
        for cell in CELLS:
            g = [d for d in decs if (d['cond'], d['group']) == cell]
            fa_u, fs_u, ua_u, us_u = cells(g, arm('U'))
            best = None
            for m in range(0, 2001, 10):
                fa, fs, ua, us = cells(g, arm(*f, margin=float(m)))
                if ua <= ua_u:
                    best = (m, fs); break
            rows.append(dict(arm=name, cell=f'{cell[0][:4]} {cell[1]}', U_FS=fs_u, U_UA=ua_u,
                             margin=best[0] if best else None, FS_at_margin=best[1] if best else None))
    T = pd.DataFrame(rows)
    print(T.to_string(index=False))
    T.assign(pop=label).to_csv(os.path.join(RES, f'D_audit_cell_margin_{label}.csv'), index=False)

    print(f'\n=== {label}: one global margin, tuned on one condition, applied to the other')
    rows = []
    for name, f in FAMS.items():
        if f is None:
            continue
        for src, dst in (('12MP normal', '24MP memory'), ('24MP memory', '12MP normal')):
            gs = [d for d in decs if d['cond'] == src]; gd = [d for d in decs if d['cond'] == dst]
            ua_s = cells(gs, arm('U'))[2]; fa_d, fs_d, ua_d, us_d = cells(gd, arm('U'))
            m = next((m for m in range(0, 2001, 10) if cells(gs, arm(*f, margin=float(m)))[2] <= ua_s), None)
            fa, fs, ua, us = cells(gd, arm(*f, margin=float(m)))
            rows.append(dict(arm=name, tuned_on=src[:4], margin=m, applied_to=dst[:4],
                             FS=fs, UA=ua, U_FS=fs_d, U_UA=ua_d))
    X = pd.DataFrame(rows)
    print(X.to_string(index=False))
    X.assign(pop=label).to_csv(os.path.join(RES, f'D_audit_transfer_{label}.csv'), index=False)
