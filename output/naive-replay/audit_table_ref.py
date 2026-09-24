"""Part D against the printed RQ3 cells: U's unsafe admits taken as the table's
5 (12MP M 2, 12MP S 0, 24MP M 1, 24MP S 2), at the author's direction, instead
of the 8 this export reproduces.  Feasible skips are the table's and this
export's alike (16 / 5 / 50 / 27).  The naive arms do not depend on the
disputed field, so only the reference moves."""
import pickle, os
import numpy as np, pandas as pd
from audit_rescore import cells, arm, HERE, RES
sel = pickle.load(open(os.path.join(HERE, 'audit_decisions.pkl'), 'rb'))['sel']
pd.set_option('display.width', 250)
UREF = {('12MP normal', 'Multi-frame'): (16, 2), ('12MP normal', 'Single-frame'): (5, 0),
        ('24MP memory', 'Multi-frame'): (50, 1), ('24MP memory', 'Single-frame'): (27, 2)}
FAMS = {'P-hat only': ('P', 1, 'mean'), 'draft mean-3': ('draft', 3, 'mean'), 'draft max-5': ('draft', 5, 'max'),
        'stage mean-3': ('stage', 3, 'mean'), 'stage max-5': ('stage', 5, 'max')}
MARGINS = range(0, 2001, 10)


def ref(cond=None):
    ks = [k for k in UREF if cond is None or k[0] == cond]
    return sum(UREF[k][0] for k in ks), sum(UREF[k][1] for k in ks)


def first_margin(decs, f, ua_max):
    for m in MARGINS:
        fa, fs, ua, us = cells(decs, arm(*f, margin=float(m)))
        if ua <= ua_max:
            return m, fs, ua
    return None, None, None


rows = []
fs_u, ua_u = ref()
for name, f in FAMS.items():
    fa, fs, ua, us = cells(sel, arm(*f))
    m, fs_m, ua_m = first_margin(sel, f, ua_u)
    ok = [c for c in (cells(sel, arm(*f, margin=float(mm))) for mm in MARGINS) if c[1] <= fs_u]
    best_ua = min(c[2] for c in ok) if ok else None
    rows.append(dict(arm=name, UA=ua, FS=fs, margin_for_UA_le_5=m, FS_at_that_margin=fs_m, UA_at_that_margin=ua_m,
                     best_UA_with_FS_le_98=best_ua))
G = pd.DataFrame(rows); print(f'U reference: FS {fs_u}, UA {ua_u}'); print(G.to_string(index=False))

rows = []
for name, f in FAMS.items():
    for k, (fsr, uar) in UREF.items():
        g = [d for d in sel if (d['cond'], d['group']) == k]
        m, fs_m, ua_m = first_margin(g, f, uar)
        rows.append(dict(arm=name, cell=f'{k[0][:4]} {k[1]}', U_FS=fsr, U_UA=uar, margin=m, FS=fs_m, UA=ua_m))
C = pd.DataFrame(rows); print(C.to_string(index=False))

rows = []
for name, f in FAMS.items():
    for src, dst in (('12MP normal', '24MP memory'), ('24MP memory', '12MP normal')):
        gs = [d for d in sel if d['cond'] == src]; gd = [d for d in sel if d['cond'] == dst]
        m, _, _ = first_margin(gs, f, ref(src)[1])
        fa, fs, ua, us = cells(gd, arm(*f, margin=float(m)))
        rows.append(dict(arm=name, tuned_on=src[:4], margin=m, applied_to=dst[:4], FS=fs, UA=ua,
                         U_FS=ref(dst)[0], U_UA=ref(dst)[1]))
X = pd.DataFrame(rows); print(X.to_string(index=False))
pd.concat([G.assign(block='global'), C.assign(block='per cell'), X.assign(block='transfer')]).to_csv(
    os.path.join(RES, 'D_audit_table_ref.csv'), index=False)
