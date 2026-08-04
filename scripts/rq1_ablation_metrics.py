"""RQ1(b) expanded ablation: 2 conditions x starting Lv3/Lv4 x 4 arms.

Follows docs/rq1-rq3-metrics-guide.md sections 3.2 (run reconstruction),
3.4 (inclusive percentiles), 3.5 (valid-run policy / dedup) and 4.3.
"""
import openpyxl, warnings, os, statistics
warnings.filterwarnings('ignore')

PAPER = r'C:/Users/sal_eunki/Desktop/SEIP-27'
ML    = r'C:/Users/sal_eunki/Desktop/ML'

ARMS = {
    ('12MP normal', 'No control'):     [],  # no accessible controller-off workbook
    ('12MP normal', 'Admission only'): [PAPER+'/data/48U_metrics_12MP_normal_0729_AdmitOnly_1.xlsx',
                                        PAPER+'/data/48U_metrics_12MP_normal_0729_AdmitOnly_2.xlsx'],
    ('12MP normal', 'Pacing only'):    [PAPER+'/data/48U_metrics_12MP_normal_0729_PacingOnly_1.xlsx',
                                        PAPER+'/data/48U_metrics_12MP_normal_0729_PacingOnly_2.xlsx'],
    ('12MP normal', 'Full'):           [ML+'/data/0803_FULL/SM-S948U_metrics_12MP_normal_0803.xlsx'],
    ('24MP memory', 'No control'):     [ML+'/data/0803_FULL/SM-S948U_metrics_24MP_memory_baseline_0803.xlsx'],
    ('24MP memory', 'Admission only'): [PAPER+'/data/48U_metrics_24MP_memory_0729_AdmitOnly_1.xlsx',
                                        PAPER+'/data/48U_metrics_24MP_memory_0729_AdmitOnly_2.xlsx'],
    ('24MP memory', 'Pacing only'):    [PAPER+'/data/48U_metrics_24MP_memory_0729_PacingOnly_1.xlsx',
                                        PAPER+'/data/48U_metrics_24MP_memory_0729_PacingOnly_2.xlsx'],
    ('24MP memory', 'Full'):           [ML+'/data/0803_FULL/SM-S948U_metrics_24MP_memory_0803.xlsx'],
}


def read_sheet(path, name):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    if name not in wb.sheetnames:
        wb.close(); return None, []
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    hdr = next(it)
    idx = {}
    for i, h in enumerate(hdr):
        if h and h not in idx:
            idx[h] = i
    rows = [r for r in it if any(c is not None for c in r)]
    wb.close()
    return idx, rows


def cell(r, i):
    return r[i] if (i is not None and len(r) > i) else None


def truthy(v):
    if v is None: return False
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v != 0
    return str(v).strip().lower() in ('true', 'yes', '1', 'y')


def split_runs(rows, ppi):
    runs, cur, prev = [], [], None
    for r in rows:
        pp = cell(r, ppi)
        if cur and prev is not None and pp is not None and pp <= prev:
            runs.append(cur); cur = []
        cur.append(r)
        prev = pp
    if cur:
        runs.append(cur)
    return runs


def pctl_inc(vals, q):
    """Excel PERCENTILE.INC."""
    if not vals: return None
    s = sorted(vals)
    if len(s) == 1: return s[0]
    pos = (len(s) - 1) * q
    lo = int(pos); hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def load_arm(paths):
    """Return list of run dicts, deduplicated across workbooks."""
    seen, out = set(), []
    for p in paths:
        if not os.path.exists(p):
            print(f'  !! missing {p}'); continue
        ci, crows = read_sheet(p, 'Capture')
        runs = split_runs(crows, ci['ppSequenceId'])
        # per-run pacing totals from RQ3Summary, joined positionally (the
        # exporter applies the same run rule) and validated by shot count.
        si, srows = read_sheet(p, 'RQ3Summary')
        summ = srows if si else []
        for k, run in enumerate(runs):
            sig = tuple((cell(r, ci['captureIndex']), cell(r, ci['ppSequenceId']),
                         cell(r, ci['shotToShotTimeMs']),
                         cell(r, ci['draftSequenceDurationMs'])) for r in run)
            if sig in seen:
                continue
            seen.add(sig)
            pref = run[:30]
            lvl = cell(run[0], ci['firstNodeOverheatLevel'])
            to_pos = None
            for j, r in enumerate(pref):
                if truthy(cell(r, ci['isTimeout'])):
                    to_pos = j + 1; break
            def rate(col):
                vals = [1.0 if truthy(cell(r, ci[col])) else 0.0 for r in pref]
                return 100.0 * sum(vals) / len(vals) if vals else None
            ms = [1.0 if (truthy(cell(r, ci['bokehCompleted'])) and
                          truthy(cell(r, ci['filterCompleted']))) else 0.0 for r in pref]
            slack = []
            for r in pref:
                m = cell(r, ci['timeoutMarginMs'])
                if isinstance(m, (int, float)):
                    slack.append(float(m))
            tot_delay = None; paced_pct = None
            if summ and k < len(summ):
                srow = summ[k]
                if cell(srow, si['shotCount']) in (len(run), len(run) - 1, len(run) + 1):
                    td = cell(srow, si['totalDelayMs'])
                    tot_delay = float(td) if isinstance(td, (int, float)) else None
                    pp = cell(srow, si['pacedPercent'])
                    paced_pct = float(pp) if isinstance(pp, (int, float)) else None
            out.append(dict(lvl=None if lvl is None else int(lvl), n=len(run),
                            reached30=len(run) >= 30, timeout_at=to_pos,
                            ms=100.0 * sum(ms) / len(ms) if ms else None,
                            m=rate('bokehCompleted'), s=rate('filterCompleted'),
                            slack=slack, total_delay=tot_delay, paced=paced_pct,
                            src=os.path.basename(p)))
    return out


CTO = {}  # captureTimeoutMs per workbook, for slack normalization
for cond, arm in ARMS:
    for p in ARMS[(cond, arm)]:
        if not os.path.exists(p) or p in CTO: continue
        pi, prows = read_sheet(p, 'PacingReplay')
        if pi and 'captureTimeoutMs' in pi:
            vs = [float(cell(r, pi['captureTimeoutMs'])) for r in prows
                  if isinstance(cell(r, pi['captureTimeoutMs']), (int, float))]
            CTO[p] = statistics.median(vs) if vs else None

print('captureTimeoutMs per workbook:')
for k, v in CTO.items():
    print(f'  {os.path.basename(k):55s} {v}')
print()

DEADLINE = statistics.median([v for v in CTO.values() if v]) if CTO else None

hdr = (f"{'condition':13s} {'arm':15s} {'Lv':>2s} {'N':>3s} {'S30':>6s} "
       f"{'E':>3s} {'Med':>5s} {'M+S%':>6s} {'M%':>6s} {'slackP5%':>8s} "
       f"{'SdelayP50s':>10s} {'paced%':>7s}")
print(hdr); print('-' * len(hdr))

for (cond, arm), paths in ARMS.items():
    runs = load_arm(paths)
    for lv in (3, 4):
        g = [r for r in runs if r['lvl'] == lv]
        if not g:
            print(f'{cond:13s} {arm:15s} {lv:2d}   --  (no accessible source)')
            continue
        n = len(g)
        s30 = sum(1 for r in g if r['reached30'] and r['timeout_at'] is None)
        tos = [r['timeout_at'] for r in g if r['timeout_at'] is not None]
        E = min(tos) if tos else None
        Med = statistics.median(tos) if len(tos) * 2 >= n else None  # censored otherwise
        ms = [r['ms'] for r in g if r['ms'] is not None]
        mm = [r['m'] for r in g if r['m'] is not None]
        allslack = [v for r in g for v in r['slack']]
        p5 = pctl_inc(allslack, 0.05)
        p5pct = 100.0 * p5 / DEADLINE if (p5 is not None and DEADLINE) else None
        td = [r['total_delay'] for r in g if r['total_delay'] is not None]
        tdp50 = statistics.median(td) / 1000.0 if td else None
        pc = [r['paced'] for r in g if r['paced'] is not None]
        f = lambda v, d=1: ('--' if v is None else f'{v:.{d}f}')
        print(f'{cond:13s} {arm:15s} {lv:2d} {n:3d} {s30:2d}/{n:<3d} '
              f'{("--" if E is None else str(E)):>3s} {f(Med):>5s} '
              f'{f(sum(ms)/len(ms)) if ms else "--":>6s} '
              f'{f(sum(mm)/len(mm)) if mm else "--":>6s} '
              f'{f(p5pct):>8s} {f(tdp50,2):>10s} {f(sum(pc)/len(pc)) if pc else "--":>7s}')
    print()
