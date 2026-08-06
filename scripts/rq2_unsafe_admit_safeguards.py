"""RQ2: for every unsafe fresh-model admit, which shipped safeguard would have
prevented the overrun.

Python port of data/rq2_spike_anatomy.mjs (ML implementation repository,
commit 99aae0a), re-pointed at data/ablation_sampling.  Same definitions:

  suffix        per-node rows with nodeOrder >= the decision node's
  skipsModel(r) r carries an admission decision the fresh model rejected
  droppedMs     work in the suffix the model itself would not have run
                (the decision under test always stays in the sum)
  budgetGainMs  work BEFORE the decision the model would have skipped, which
                shortens the path to it and so raises its budget
  C_model = C - droppedMs      B_model = B + budgetGainMs

  W  the per-node watchdog would have cut the decision node first
     (durationMs > watchdogTimeoutMs)
  B  the decision fits once the model's own skips are honoured on both sides
     (C_model <= B_model)

Run:  python scripts/rq2_unsafe_admit_safeguards.py
"""
import os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rq2_admission_metrics import (SAMP, RQ2_0729, MANIFEST_DROP, GROUP,
                                   read_sheet, cell, truthy, num)

NODE_SHEETS = ['DynamicFunctionNode', 'SecDualBokehNode', 'SecFilterNode',
               'SecImageCodecNode', 'WatermarkNode']

SETS = {
    'new  data/ablation_sampling  pacing_only_0803': {
        '12MP normal': [os.path.join(SAMP, '48U_metrics_12MP_normal_pacing_only_0803.xlsx')],
        '24MP memory': [os.path.join(SAMP, '48U_metrics_24MP_memory_pacing_only_0803.xlsx')],
    },
    'current  0729 PacingOnly': {
        '12MP normal': [os.path.join(RQ2_0729, '48U_metrics_12MP_normal_0729_PacingOnly_1.xlsx'),
                        os.path.join(RQ2_0729, '48U_metrics_12MP_normal_0729_PacingOnly_2.xlsx')],
        '24MP memory': [os.path.join(RQ2_0729, '48U_metrics_24MP_memory_0729_PacingOnly_1.xlsx'),
                        os.path.join(RQ2_0729, '48U_metrics_24MP_memory_0729_PacingOnly_2.xlsx')],
    },
}


def selected(paths, max_shot=30):
    """Every capture-level selected decision, with its node suffix resolved."""
    out, seen = [], set()
    for p in paths:
        if not os.path.exists(p):
            print(f'  !! missing {p}')
            continue
        base = os.path.basename(p)
        ai, arows = read_sheet(p, 'AdmissionReplay')
        pi, prows = read_sheet(p, 'PacingReplay')
        draft_end = {cell(r, pi['captureIndex']): num(cell(r, pi['draftEndUptimeMs']))
                     for r in prows}

        nodes_by = {}
        for name in NODE_SHEETS:
            ni, nrows = read_sheet(p, name)
            if not ni:
                continue
            for r in nrows:
                nodes_by.setdefault(cell(r, ni['captureIndex']), []).append(dict(
                    order=num(cell(r, ni['nodeOrder'])),
                    name=cell(r, ni['nodeName']),
                    dur=num(cell(r, ni['durationMs'])) or 0.0,
                    wd=num(cell(r, ni['watchdogTimeoutMs'])),
                    cpu=num(cell(r, ni['cpuTimeMs'])) or 0.0,
                    wall=num(cell(r, ni['wallTimeMs'])) or 0.0))
        for v in nodes_by.values():
            v.sort(key=lambda r: r['order'])

        order, pp = [], {}
        for r in arows:
            c = cell(r, ai['captureIndex'])
            if c not in pp:
                order.append(c)
                pp[c] = cell(r, ai['ppSequenceId'])
        runs, cur, prev = [], [], None
        for c in order:
            if cur and prev is not None and pp[c] is not None and pp[c] <= prev:
                runs.append(cur)
                cur = []
            cur.append(c)
            prev = pp[c]
        if cur:
            runs.append(cur)

        by_cap = {}
        for r in arows:
            by_cap.setdefault(cell(r, ai['captureIndex']), []).append(r)

        for k, run in enumerate(runs, start=1):
            if (base, k) in MANIFEST_DROP:
                continue
            sig = tuple((pp[c], cell(by_cap[c][0], ai['nodeStartUptimeMs']),
                         cell(by_cap[c][0], ai['timeoutDeadlineUptimeMs'])) for c in run)
            if sig in seen:
                continue
            seen.add(sig)
            for shot, c in enumerate(run[:max_shot], start=1):
                decisions = sorted(by_cap[c], key=lambda r: (num(cell(r, ai['nodeOrder'])) or 0))
                nodes = nodes_by.get(c, [])

                def skips_model(nrow):
                    m = next((x for x in decisions
                              if num(cell(x, ai['nodeOrder'])) == nrow['order']), None)
                    return bool(m and cell(m, ai['admissionStage'])
                                and not truthy(cell(m, ai['afterModelAdmit'])))

                for stage, group in GROUP.items():
                    d = next((r for r in decisions
                              if cell(r, ai['admissionStage']) == stage), None)
                    if d is None:
                        continue
                    o = num(cell(d, ai['nodeOrder']))
                    b = num(cell(d, ai['beforeBudgetMs']))
                    start = num(cell(d, ai['nodeStartUptimeMs']))
                    end = draft_end.get(c)
                    cost = end - start if (end is not None and start is not None) else None

                    suffix = [r for r in nodes if r['order'] >= o]
                    dropped = sum(r['dur'] for r in suffix
                                  if r['order'] != o and skips_model(r))
                    gain = sum(r['dur'] for r in nodes
                               if r['order'] < o and skips_model(r))
                    dnode = next((r for r in nodes if r['order'] == o), None)
                    wall = sum(r['wall'] for r in suffix)
                    cpu = sum(r['cpu'] for r in suffix)
                    out.append(dict(
                        book=base, run=k, shot=shot, capture=c, group=group,
                        budget=b, cost=cost,
                        watchdog=truthy(cell(d, ai['beforeWatchdogTimedOut'])) or
                                 truthy(cell(d, ai['beforeCaptureWatchdogFailed'])),
                        model_admit=truthy(cell(d, ai['afterModelAdmit'])),
                        eff_admit=truthy(cell(d, ai['beforeEffectiveAdmit'])),
                        node_dur=None if dnode is None else dnode['dur'],
                        node_wd=None if dnode is None else dnode['wd'],
                        dropped=dropped, gain=gain,
                        cost_model=None if cost is None else cost - dropped,
                        budget_model=None if b is None else b + gain,
                        cpu=cpu, wall=wall,
                        cores=cpu / wall if wall else None,
                        overheat=num(cell(d, ai['overheatLevel'])),
                        thermal=num(cell(d, ai['thermalStatus'])),
                        outcome=cell(d, ai['afterDecisionOutcome'])))
    return out


def report(label, sets):
    print(f'\n{"=" * 112}\n{label}\n{"=" * 112}')
    rows = []
    for cond, paths in sets.items():
        dec = selected(paths)
        events = [d for d in dec if d['model_admit'] and d['cost'] is not None
                  and (d['watchdog'] or d['cost'] > d['budget'])]
        for e in events:
            pool = sorted([s for s in dec if s['book'] == e['book'] and s['run'] == e['run']
                           and s['group'] == e['group'] and s['shot'] < e['shot']],
                          key=lambda s: s['shot'])
            e['cond'] = cond
            e['prev'] = pool[-1] if pool else None
            rows.append(e)

    rows.sort(key=lambda r: (r['group'], -(r['cost'] / r['prev']['cost'])
                             if r['prev'] and r['prev']['cost'] else 0))
    m = s = 0
    for r in rows:
        if r['group'] == 'Multi-frame':
            m += 1
            r['id'] = f'M{m}'
        else:
            s += 1
            r['id'] = f'S{s}'

    print(f'{"id":4s} {"condition":12s} {"grp":6s} {"run/shot":9s} '
          f'{"B":>6s} {"C":>6s} {"C-B":>5s} | '
          f'{"nodeDur/wd":>12s} {"watchdog?":>14s} | '
          f'{"C_mod/B_mod":>12s} {"(later-,earlier+)":>18s} {"fits?":>6s} | verdict')
    print('-' * 130)
    for r in rows:
        trips = r['node_wd'] is not None and r['node_dur'] is not None and r['node_dur'] > r['node_wd']
        fits = r['cost_model'] is not None and r['cost_model'] <= r['budget_model']
        tag = '+'.join([t for t in ('W' if trips else None, 'B' if fits else None) if t]) or 'NONE'
        wtxt = ('cut +%.0f' % (r['node_dur'] - r['node_wd']) if trips
                else 'no, %.0f spare' % ((r['node_wd'] or 0) - (r['node_dur'] or 0)))
        where = '%d/%d' % (r['run'], r['shot'])
        skips = '(-%.0f, +%.0f)' % (r['dropped'], r['gain'])
        print(f'{r["id"]:4s} {r["cond"]:12s} {r["group"][:5]:6s} {where:9s} '
              f'{r["budget"]:6.0f} {r["cost"]:6.0f} {r["cost"] - r["budget"]:5.0f} | '
              f'{r["node_dur"]:5.0f}/{r["node_wd"]:6.0f} {wtxt:>14s} | '
              f'{r["cost_model"]:5.0f}/{r["budget_model"]:6.0f} {skips:>18s} '
              f'{("yes" if fits else "no"):>6s} | {tag}')
    print(f'\n  W = the per-node watchdog would have cut it first.')
    print(f'  B = it fits once the model\'s own skips are honoured on both sides.')
    covered = sum(1 for r in rows
                  if (r['node_wd'] is not None and r['node_dur'] > r['node_wd'])
                  or (r['cost_model'] is not None and r['cost_model'] <= r['budget_model']))
    print(f'  {covered} of {len(rows)} unsafe admits are covered by at least one safeguard.')

    print('\n  ratios to the preceding capture of the same run and group '
          '(for figures/fig_rq2_unsafe_spike_anatomy.tex)')
    print(f'  {"id":4s} {"prev shot":>9s} {"latency":>8s} {"CPU":>8s} {"cores":>8s} '
          f'{"C_prev":>7s} {"UB/B":>6s} {"overheat":>9s}')
    for r in rows:
        p = r['prev']
        if not p or not p['wall'] or not p['cpu'] or not p['cores']:
            print(f'  {r["id"]:4s} {"--":>9s}  (no usable preceding capture)')
            continue
        heat = '%.0f->%.0f' % (p['overheat'], r['overheat'])
        print(f'  {r["id"]:4s} {p["shot"]:9d} {r["wall"] / p["wall"]:8.2f} '
              f'{r["cpu"] / p["cpu"]:8.2f} {r["cores"] / p["cores"]:8.2f} '
              f'{p["cost"]:7.0f} {"--":>6s} {heat:>9s}')


if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for label, sets in SETS.items():
        if only and not label.startswith(only):
            continue
        report(label, sets)
