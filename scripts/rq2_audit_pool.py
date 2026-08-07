"""RQ2 Always-admit model audit on the pooled Pacing-only set.

Reproduces the Always-admit columns of tables/tab_rq2_admission_summary.tex,
which pool two disjoint Pacing-only sources:

  (a) ML/data/0729_RQ2/48U_metrics_<cond>_0729_PacingOnly_{1,2}.xlsx, all runs;
  (b) data/ablation_sampling/48U_metrics_<cond>_pacing_only_0803.xlsx, restricted
      to the starting overheat levels in KEEP_ALL / KEEP_CLEAN below.

The (b) draw is level-selected and therefore not outcome-neutral; KEEP_CLEAN
additionally conditions on a run carrying no unsafe-admitted decision.  Both
facts are recorded in the comment block of the table and must accompany any
report of these cells.  `python scripts/rq2_audit_pool.py runs` prints the
per-run census the selection is drawn from, including the runs it excludes.

Run reconstruction, the feasible/unsafe split and the decision field are taken
unchanged from scripts/rq2_admission_metrics.py, so a difference between the
pooled block and its 0729-only row is a data difference, not a method
difference.

Run:  python scripts/rq2_audit_pool.py
"""
import os, sys, statistics, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rq2_admission_metrics as M

CURRENT = {
    '12MP normal': [os.path.join(M.RQ2_0729, f'48U_metrics_12MP_normal_0729_PacingOnly_{i}.xlsx')
                    for i in (1, 2)],
    '24MP memory': [os.path.join(M.RQ2_0729, f'48U_metrics_24MP_memory_0729_PacingOnly_{i}.xlsx')
                    for i in (1, 2)],
}
ADDED = {
    '12MP normal': [os.path.join(M.SAMP, '48U_metrics_12MP_normal_pacing_only_0803.xlsx')],
    '24MP memory': [os.path.join(M.SAMP, '48U_metrics_24MP_memory_pacing_only_0803.xlsx')],
}

# Starting overheat levels drawn from (b).  KEEP_ALL takes every run at the
# level; KEEP_CLEAN takes only runs with no unsafe-admitted decision.
KEEP_ALL = {'12MP normal': {1, 2}, '24MP memory': {0, 1, 2}}
KEEP_CLEAN = {'12MP normal': {4}, '24MP memory': set()}

# Published cells of tables/tab_rq2_admission_summary.tex, for the side-by-side.
PUBLISHED = {
    ('12MP normal', 'Multi-frame'): (831, 16, +1.2, 4, 31, -3.0),
    ('12MP normal', 'Single-frame'): (842, 5, +0.7, 0, 35, -3.5),
    ('24MP memory', 'Multi-frame'): (892, 50, +2.6, 1, 53, -3.2),
    ('24MP memory', 'Single-frame'): (905, 27, +1.6, 3, 51, -3.4),
}


def starting_levels(path):
    """captureIndex -> firstNodeOverheatLevel, in worksheet order."""
    ci, crows = M.read_sheet(path, 'Capture')
    out = {}
    for r in crows:
        c = M.cell(r, ci['captureIndex'])
        if c is not None and c not in out:
            v = M.cell(r, ci['firstNodeOverheatLevel'])
            out[c] = int(v) if isinstance(v, (int, float)) else None
    return out


def tag_levels(dec, paths):
    """Attach each run's starting level, read at the run's first capture."""
    lv_of = {os.path.basename(p): starting_levels(p) for p in paths
             if os.path.exists(p)}
    first = {}
    for d in dec:
        k = (d['book'], d['run'])
        if k not in first or d['shot'] < first[k][0]:
            first[k] = (d['shot'], d['capture'])
    for d in dec:
        d['level'] = lv_of[d['book']].get(first[(d['book'], d['run'])][1])
    return dec


def unsafe(d):
    return d['watchdog'] or (d['cost'] is not None and d['cost'] > d['budget'])


def run_census(dec):
    """(book, run) -> dict(level, captures, fa, fs, ua, us)."""
    by_run = collections.defaultdict(list)
    for d in dec:
        by_run[(d['book'], d['run'])].append(d)
    out = {}
    for k, ds in by_run.items():
        scored = [d for d in ds if d['cost'] is not None]
        u = [d for d in scored if unsafe(d)]
        f = [d for d in scored if not unsafe(d)]
        ua = sum(1 for d in u if d['model_admit'])
        fa = sum(1 for d in f if d['model_admit'])
        out[k] = dict(level=ds[0]['level'], captures=len({d['capture'] for d in ds}),
                      fa=fa, fs=len(f) - fa, ua=ua, us=len(u) - ua)
    return out


def select(cond, census):
    keep = set()
    for k, c in census.items():
        if c['level'] in KEEP_ALL[cond] or (c['level'] in KEEP_CLEAN[cond] and c['ua'] == 0):
            keep.add(k)
    return keep


def audit_cells(dec, D, field='model_admit'):
    out = {}
    for group in ('Multi-frame', 'Single-frame'):
        g = [d for d in dec if d['group'] == group and d['cost'] is not None]
        feas = [d for d in g if not unsafe(d)]
        unsf = [d for d in g if unsafe(d)]
        fa = sum(1 for d in feas if d[field])
        ua = sum(1 for d in unsf if d[field])
        marg = [100.0 * (d['budget'] - d['cost']) / D for d in feas if not d[field]]
        over = [100.0 * (d['cost'] - d['budget']) / D for d in unsf if not d[field]]
        out[group] = (fa, len(feas) - fa,
                      statistics.median(marg) if marg else None,
                      ua, len(unsf) - ua,
                      statistics.median(over) if over else None)
    return out


def build(cond):
    """Return (current, added, pooled, deadlines, census, keep) for one condition."""
    cur, _ = M.load_decisions(CURRENT[cond])
    new, _ = M.load_decisions(ADDED[cond])
    new = tag_levels(new, ADDED[cond])
    census = run_census(new)
    keep = select(cond, census)
    added = [d for d in new if (d['book'], d['run']) in keep]
    D = (M.deadline_of(CURRENT[cond]), M.deadline_of(ADDED[cond]),
         M.deadline_of(CURRENT[cond] + ADDED[cond]))
    return cur, added, cur + added, D, census, keep


def print_runs(cond, census, keep):
    print(f'\n{"=" * 78}\nCANDIDATE 0803 pacing_only RUNS   {cond}\n{"=" * 78}')
    print(f'  {"Lv":>3s} {"run":>5s} {"caps":>5s} {"FA":>4s} {"FS":>3s} '
          f'{"UA":>3s} {"US":>3s}  drawn')
    for k in sorted(census, key=lambda x: (census[x]['level'] is None,
                                           census[x]['level'], x[1])):
        c = census[k]
        print(f'  {str(c["level"]):>3s} {k[1]:5d} {c["captures"]:5d} {c["fa"]:4d} '
              f'{c["fs"]:3d} {c["ua"]:3d} {c["us"]:3d}  {"YES" if k in keep else "-"}')
    drawn = [census[k] for k in keep]
    held = [c for k, c in census.items() if k not in keep]
    print(f'  drawn {len(drawn)} runs / {sum(c["captures"] for c in drawn)} captures, '
          f'carrying {sum(c["ua"] for c in drawn)} unsafe-admitted decisions')
    print(f'  held  {len(held)} runs / {sum(c["captures"] for c in held)} captures, '
          f'carrying {sum(c["ua"] for c in held)} unsafe-admitted decisions')


def print_audit(cond, rows):
    print(f'\n{"=" * 118}\nALWAYS-ADMIT MODEL AUDIT   {cond}\n{"=" * 118}')
    hdr = (f'{"group":13s} {"source":28s} {"n":>5s} | '
           f'{"feas-admit":>14s} {"feas-skip":>14s} {"margin":>8s} | '
           f'{"unsf-admit":>13s} {"unsf-skip":>14s} {"overrun":>8s}')
    print(hdr)
    print('-' * len(hdr))
    for group in ('Multi-frame', 'Single-frame'):
        for name, cells in rows:
            fa, fs, m, ua, us, o = cells[group]
            tf, tu = fa + fs, ua + us
            print(f'{group:13s} {name:28s} {tf + tu:5d} | '
                  f'{fa:5d} ({M.pct(fa, tf):5.1f}%) {fs:5d} ({M.pct(fs, tf):5.1f}%) '
                  f'{("--" if m is None else f"+{m:.1f}%"):>8s} | '
                  f'{ua:4d} ({M.pct(ua, tu):5.1f}%) {us:5d} ({M.pct(us, tu):5.1f}%) '
                  f'{("--" if o is None else f"-{abs(o):.1f}%"):>8s}')
        print()


def main(show_runs=False):
    for cond in ('12MP normal', '24MP memory'):
        cur, added, pool, D, census, keep = build(cond)
        if show_runs:
            print_runs(cond, census, keep)
        print(f'\ndeadline D: 0729={D[0]}, 0803={D[1]}, pooled={D[2]}')
        rows = [('published table', {g: PUBLISHED[(cond, g)]
                                     for g in ('Multi-frame', 'Single-frame')}),
                ('current  0729 only', audit_cells(cur, D[0])),
                ('added    0803 subset only', audit_cells(added, D[1])),
                ('POOLED   0729 + 0803 subset', audit_cells(pool, D[2]))]
        print_audit(cond, rows)


if __name__ == '__main__':
    main(show_runs=(len(sys.argv) > 1 and sys.argv[1] == 'runs'))
