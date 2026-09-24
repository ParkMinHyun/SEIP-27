"""Part D: naive estimators scored on the RQ3 always-admit audit.

Open-loop, factual.  Every optional stage in these runs executed (admission was
recorded but not enforced), so each capture-level Bokeh / Filter decision has a
realized remaining-sequence duration C = draftEnd - nodeStart and a live budget
B read at the decision.  A decision is unsafe if C > B or the watchdog fired,
feasible otherwise -- the RQ3 definition.  Here only the estimator that turns
history into a forecast changes; nothing is imputed and nothing is replayed.

Arms (admit iff forecast <= B, or no history / zero forecast = cold start):
  U        recorded afterModelAdmit (the RQ3 table's decision field)
  P        recorded point estimate P-hat alone ("current - residual")
  draft    statistic of the last N completed draft walls in the same run,
           minus the time already spent in the current draft
  stage    sum over the recorded remaining sequence of each key's last-N
           statistic (per occurrence, same run); unobserved keys count 0
  stage+r  stage, plus the mean of the last N non-stage remainders
           (C minus the remaining stages' durations) at the same group's
           admission point
History is the same run's completed drafts only, matching the force-stop and
relaunch before every run.

Population: the RQ3 audit pool, rebuilt with the level-selection rule of the
deleted scripts/rq2_audit_pool.py (recovered from d135b2e^), and the
unselected union of the same two sources as a sensitivity check.

Run:  python audit_load.py   (once; caches audit_wb.pkl)
      python audit_rescore.py
"""
import os, sys, pickle, collections, statistics
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PAPER, 'scripts'))
import rq3_admission_quality_metrics as M          # run split, dedup, manifest, fields

M.SAMP = os.path.join(PAPER, 'data', 'U_ablation_sampling')   # folder renamed since the script
W = pickle.load(open(os.path.join(HERE, 'audit_wb.pkl'), 'rb'))
RES = os.path.join(HERE, 'results')

CURRENT = {c: [os.path.join(M.RQ2_0729, f'48U_metrics_{k}_0729_PacingOnly_{i}.xlsx') for i in (1, 2)]
           for c, k in (('12MP normal', '12MP_normal'), ('24MP memory', '24MP_memory'))}
ADDED = {c: [os.path.join(M.SAMP, f'48U_metrics_{k}_pacing_only_0803.xlsx')]
         for c, k in (('12MP normal', '12MP_normal'), ('24MP memory', '24MP_memory'))}
KEEP_ALL = {'12MP normal': {1, 2}, '24MP memory': {0, 1, 2}}   # rq2_audit_pool.py
KEEP_CLEAN = {'12MP normal': {4}, '24MP memory': set()}
NODE_SHEETS = ['DynamicFunctionNode', 'SecDualBokehNode', 'SecFilterNode', 'SecImageCodecNode', 'WatermarkNode']
STAGE = {'Multi-frame': 'Bokeh', 'Single-frame': 'Filter'}


def unsafe(d):
    return d['watchdog'] or d['cost'] > d['budget']


# ------------------------------------------------------------ population

def runs_of(book):
    """Capture lists per run, split exactly as M.load_decisions splits them."""
    a = W[book]['AdmissionReplay']
    order, pp = [], {}
    for c, p in zip(a.captureIndex, a.ppSequenceId):
        if c not in pp:
            order.append(c)
            pp[c] = p
    runs, cur, prev = [], [], None
    for c in order:
        if cur and prev is not None and pd.notna(pp[c]) and pp[c] <= prev:
            runs.append(cur)
            cur = []
        cur.append(c)
        prev = pp[c]
    if cur:
        runs.append(cur)
    return runs


def population(cond):
    cur, _ = M.load_decisions(CURRENT[cond])
    new, _ = M.load_decisions(ADDED[cond])
    cap = W[os.path.basename(ADDED[cond][0])]['Capture']
    lv = dict(zip(cap.captureIndex, cap.firstNodeOverheatLevel))
    first = {}
    for d in new:
        k = (d['book'], d['run'])
        if k not in first or d['shot'] < first[k][0]:
            first[k] = (d['shot'], d['capture'])
    ua = collections.Counter((d['book'], d['run']) for d in new
                             if d['cost'] is not None and unsafe(d) and d['model_admit'])
    keep = {k for k, (_, c) in first.items()
            if lv.get(c) in KEEP_ALL[cond] or (lv.get(c) in KEEP_CLEAN[cond] and ua[k] == 0)}
    for d in cur:
        d['cond'], d['level'] = cond, None
    for d in new:
        d['cond'], d['level'] = cond, lv.get(first[(d['book'], d['run'])][1])
    sel = cur + [d for d in new if (d['book'], d['run']) in keep]
    return sel, cur + new


# ------------------------------------------------------------ features

def attach(decs):
    """Add nodeStart, P-hat, remaining keys and the run's completed-draft history."""
    per_book = {}
    for book in {d['book'] for d in decs}:
        x = W[book]
        pr = x['PacingReplay'].drop_duplicates('captureIndex').set_index('captureIndex')
        N = pd.concat([x[s] for s in NODE_SHEETS], ignore_index=True).sort_values(['captureIndex', 'nodeOrder'])
        nodes = {c: list(zip(g.workloadKey, g.durationMs.fillna(0.0), g.nodeStartUptimeMs, g.nodeOrder))
                 for c, g in N.groupby('captureIndex')}
        a = x['AdmissionReplay']
        a = a[a.admissionStage.isin(['Bokeh', 'Filter'])].sort_values(['captureIndex', 'nodeOrder'])
        arow = {(c, s): r for (c, s), r in a.groupby(['captureIndex', 'admissionStage']).head(1)
                .set_index(['captureIndex', 'admissionStage']).iterrows()}
        per_book[book] = dict(pr=pr, nodes=nodes, arow=arow, runs=runs_of(book))

    def rest_after(c, order, book):
        """Non-stage time between this node's start and draft end, for a completed capture."""
        B = per_book[book]
        ns = B['nodes'].get(c, [])
        start = next((s for k, du, s, o in ns if o == order), None)
        if start is None:
            return None
        stages = sum(du for k, du, s, o in ns if o >= order)
        return (B['pr'].loc[c, 'draftEndUptimeMs'] - start) - stages

    for d in decs:
        B = per_book[d['book']]
        stage = STAGE[d['group']]
        r = B['arow'][(d['capture'], stage)]
        run = B['runs'][d['run'] - 1]
        assert run[d['shot'] - 1] == d['capture'], (d['book'], d['run'], d['shot'])
        t = r.nodeStartUptimeMs
        d.update(t=t, P=float(r.beforeSequencePredictedDurationMs or 0.0),
                 seq=tuple(str(r.workloadSequenceKey).split('>')),
                 elapsed=t - B['pr'].loc[d['capture'], 'draftStartUptimeMs'])
        walls, stage_h, rest_h = [], collections.defaultdict(list), []
        for c in run[:d['shot'] - 1]:
            end = B['pr'].loc[c, 'draftEndUptimeMs']
            if not (end <= t):
                continue
            walls.append(end - B['pr'].loc[c, 'draftStartUptimeMs'])
            for k, du, s, o in B['nodes'].get(c, []):
                if du > 0:
                    stage_h[k].append(du)
            ra = B['arow'].get((c, stage))
            if ra is not None:
                rv = rest_after(c, ra.nodeOrder, d['book'])
                if rv is not None:
                    rest_h.append(rv)
        d.update(walls=walls, stage_h=dict(stage_h), rest_h=rest_h)
    return decs


def forecast(d, fam, N, stat):
    f = np.mean if stat == 'mean' else np.max
    if fam == 'P':
        return d['P'] if d['P'] > 0 else None
    if fam == 'draft':
        h = d['walls'][-N:]
        return f(h) - d['elapsed'] if h else None
    if fam in ('stage', 'stage+r'):
        s = sum(f(d['stage_h'][k][-N:]) for k in d['seq'] if d['stage_h'].get(k))
        if s <= 0:
            return None
        if fam == 'stage+r' and d['rest_h']:
            s += float(np.mean(d['rest_h'][-N:]))
        return s
    raise ValueError(fam)


# ------------------------------------------------------------ scoring

def cells(decs, admit):
    """admit: decision -> bool.  Returns FA, FS, UA, US."""
    fa = fs = ua = us = 0
    for d in decs:
        a = admit(d)
        if unsafe(d):
            ua += a; us += not a
        else:
            fa += a; fs += not a
    return fa, fs, ua, us


def arm(fam, N=3, stat='mean', margin=0.0, scale=1.0):
    def admit(d):
        if fam == 'U':
            return d['model_admit']
        if fam == 'U_before':
            return d['model_admit_before']
        fc = forecast(d, fam, N, stat)
        return True if fc is None else fc * scale + margin <= d['budget']
    return admit


FAMILIES = [('P', 1, 'mean')] + [('draft', n, s) for s in ('mean', 'max') for n in (1, 3, 5, 10)] \
    + [('stage', n, s) for s in ('mean', 'max') for n in (1, 3, 5, 10)] + [('stage+r', 3, 'mean'), ('stage+r', 5, 'max')]


def name(fam, N, stat):
    return 'P-hat only' if fam == 'P' else f'{fam} {stat}-{N}'


def table(decs, label):
    rows = []
    for arm_name, adm in [('U (recorded, table field)', arm('U')), ('U (runtime decision)', arm('U_before'))] + \
            [(name(*f), arm(*f)) for f in FAMILIES]:
        for cond in ('12MP normal', '24MP memory'):
            for group in ('Multi-frame', 'Single-frame'):
                g = [d for d in decs if d['cond'] == cond and d['group'] == group]
                fa, fs, ua, us = cells(g, adm)
                rows.append(dict(pop=label, arm=arm_name, cond=cond, group=group, FA=fa, FS=fs, UA=ua, US=us))
        fa, fs, ua, us = cells(decs, adm)
        rows.append(dict(pop=label, arm=arm_name, cond='ALL', group='ALL', FA=fa, FS=fs, UA=ua, US=us))
    T = pd.DataFrame(rows)
    T['FS%'] = 100 * T.FS / (T.FA + T.FS)
    T['UA%'] = 100 * T.UA / (T.UA + T.US)
    return T


def frontier(decs, label):
    """Additive and multiplicative widening of each family; overall FS / UA."""
    rows = []
    fams = [('P', 1, 'mean'), ('draft', 3, 'mean'), ('draft', 5, 'max'), ('stage', 3, 'mean'),
            ('stage', 5, 'max'), ('stage+r', 3, 'mean')]
    for f in fams:
        for m in range(0, 1501, 10):
            fa, fs, ua, us = cells(decs, arm(*f, margin=float(m)))
            rows.append(dict(pop=label, arm=name(*f), knob='margin', value=m, FA=fa, FS=fs, UA=ua, US=us))
        for s in np.round(np.arange(1.0, 3.001, 0.01), 2):
            fa, fs, ua, us = cells(decs, arm(*f, scale=float(s)))
            rows.append(dict(pop=label, arm=name(*f), knob='scale', value=s, FA=fa, FS=fs, UA=ua, US=us))
    return pd.DataFrame(rows)


def best_at(F, ref_fs, ref_ua):
    out = []
    for (a, knob), g in F.groupby(['arm', 'knob'], sort=False):
        ok = g[g.UA <= ref_ua]
        fs_at_ua = int(ok.FS.min()) if len(ok) else None
        ok2 = g[g.FS <= ref_fs]
        ua_at_fs = int(ok2.UA.min()) if len(ok2) else None
        out.append(dict(arm=a, knob=knob, FS_needed_for_UA_le_ref=fs_at_ua,
                        knob_value=(ok.sort_values('FS').value.iloc[0] if len(ok) else None),
                        UA_at_FS_le_ref=ua_at_fs))
    return pd.DataFrame(out)


if __name__ == '__main__':
    pd.set_option('display.width', 250)
    sel, allp = [], []
    for cond in ('12MP normal', '24MP memory'):
        s, a = population(cond)
        sel += [d for d in s if d['cost'] is not None]
        allp += [d for d in a if d['cost'] is not None]
    attach(allp)                         # sel shares the dict objects
    print(f'selected pool: {len(sel)} decisions; unselected union: {len(allp)}')

    T = pd.concat([table(sel, 'RQ3 pool'), table(allp, 'unselected union')])
    T.to_csv(os.path.join(RES, 'D_audit_arms.csv'), index=False)
    print(T[T.cond == 'ALL'].round(1).to_string(index=False))
    print(T[(T.pop == 'RQ3 pool') & T.arm.isin(['U (recorded, table field)', 'U (runtime decision)', 'P-hat only',
                                                 'draft mean-3', 'stage mean-3', 'stage+r mean-3'])]
          .round(1).to_string(index=False))

    F = pd.concat([frontier(sel, 'RQ3 pool'), frontier(allp, 'unselected union')])
    F.to_csv(os.path.join(RES, 'D_audit_frontier.csv'), index=False)
    for label, decs in (('RQ3 pool', sel), ('unselected union', allp)):
        fa, fs, ua, us = cells(decs, arm('U'))
        print(f'\n{label}: U reference FS {fs}, UA {ua}')
        print(best_at(F[F['pop'] == label], fs, ua).to_string(index=False))
    pickle.dump(dict(sel=sel, allp=allp), open(os.path.join(HERE, 'audit_decisions.pkl'), 'wb'))
