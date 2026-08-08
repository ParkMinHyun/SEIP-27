"""Shared RQ3 selectivity, binning, and bootstrap support.

The current summary pipeline imports this module's burst, binning, and
cluster-bootstrap helpers. It also emits the retained data/rq3/selectivity/
diagnostics describing where the controller intervenes and what it costs.

Scope.  This script answers "does pacing fire selectively under high measured
backlog pressure, and what responsiveness cost does that impose", which is a
different question from the estimator calibration computed by
scripts/rq3_calibration_metrics.py.  The two share their loader, their run and
transition eligibility, and their source workbooks, so every population count
printed here matches that script exactly.

What may and may not be reported
--------------------------------
Activation is d > 0, i.e. the deployed pacer applied a delay.  The pacer applies
one exactly when its own online score

    Bhat + 2*Chat - max(0,T)

is positive, so activation against that score is true by construction -- it holds
on 100% of the analyzed transitions in both conditions -- and is NOT evidence of
anything.  Only orderings the controller did not observe carry information:

    measured risk   B + 2*C - max(0,T)   the same condition on measured inputs
    realized margin timeoutMarginMs      how close the capture came to the deadline
    measured backlog B                   RQ3Pacing.realBacklogMs

Realized margin is endogenous -- pacing raises the margin of the captures it
delays -- but the bias runs against the finding: an intervention placed at random
would over-populate the loose tail, not the tight one, so an activation rate that
rises as the margin tightens cannot be manufactured by that endogeneity.

Coverage against the measured requirement d* is deliberately absent here.  It
measures estimator error rather than policy fit, and it belongs with the
calibration diagnostics.

Uncertainty.  Every interval is a 95% percentile bootstrap over 2,000 replicates
resampling *bursts*, not transitions: the 29 transitions of one 30-shot run share
a thermal trajectory and a queue, so a transition-level resample would overstate
precision by roughly the square root of the cluster size. The fixed seed and
stable resampling order keep regenerated intervals deterministic.

Run:
    python scripts/rq3_selectivity_metrics.py sampling
    python scripts/rq3_selectivity_metrics.py raw --no-write   # old source, for deltas
"""
import csv
import os
import random
import sys
import warnings

warnings.filterwarnings('ignore')

from rq3_calibration_metrics import (BANDS, CONDITIONS, LABEL, SOURCES, load,
                                     med, pct_inc)

PAPER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PAPER, 'data', 'rq3', 'selectivity')

SEED = 20260806
BOOTSTRAP_REPS = 2000

# The margin quantiles the cumulative sweep covers.  The table quotes 5, 10, 25%.
SWEEP = [round(0.05 * i, 2) for i in range(1, 21)]
TABLE_QUANTILES = (0.05, 0.10, 0.25)

# ---------------------------------------------------------------------------
# Binning, and why it is by value rather than by rank
# ---------------------------------------------------------------------------
# An earlier revision cut both orderings into deciles.  Equal-count bins keep
# every point equally precise, but they cost the axis its physical meaning: "D3"
# names a rank group, not an amount, so the reader cannot tell what pressure the
# controller was actually under, cannot read a threshold off the curve, and has to
# be taught the vocabulary first.  Rank binning was adopted out of a concern that
# the value distributions were skewed enough to leave most of the data in one bin;
# they are not.  On fixed 10-point-of-budget bins every populated bin below the
# top holds 90 to 480 transitions in both conditions.
#
# Both orderings are expressed as a share of the Capture Timeout budget rather
# than in milliseconds, so no exhibit discloses the budget itself.  The budget is
# a single constant (checked: captureTimeoutMs takes exactly one value across all
# analyzed transitions in both conditions), so normalising per transition and
# normalising by the pooled value are the same operation.
#
# Anything derived from these two orderings must stay in budget-relative units for
# the same reason.  In particular the paced-minus-unpaced backlog gap is reported
# in points of budget, not milliseconds: quoting the two backlog medians as
# percentages and their difference in milliseconds makes the budget recoverable by
# division, which is exactly the disclosure the percentages exist to prevent.
BIN_WIDTH_PCT = 10
# Projected overrun = B + 2C - max(0,T), as a share of budget.  Negative is spare
# time.  The top bin is open at 0 rather than continuing in 10-point steps: past
# zero the counts thin out fast, and "at or past the projection" is the boundary
# that matters -- the strictly positive part of this bin is exactly the current
# summary's required-delay set (79 and 140 transitions; the 24MP bin holds one
# more, whose overrun is exactly zero).
# The range stops at 0 inclusive, so with open_top the final entry is [0, inf).
OVERRUN_BINS = [(lo, lo + BIN_WIDTH_PCT) for lo in range(-90, 1, BIN_WIDTH_PCT)]
MARGIN_BINS = [(lo, lo + BIN_WIDTH_PCT) for lo in range(0, 90, BIN_WIDTH_PCT)]
# Where activation is reported as effectively extinguished.  Stated as one
# aggregate row in the table because the individual loose bins are all at or near
# zero and listing them separately would spend four rows on one fact.
MARGIN_QUIET_FROM_PCT = 50

# Smallest paced count for which a bin's median applied delay is plotted or
# quoted.  Below it the median is not a summary of anything.  The value is still
# written to the CSV and printed by report(), so the cut is auditable.
DELAY_PLOT_MIN_N = 10


def bursts(tx):
    """Transitions grouped by run. Insertion order matters because the bootstrap
    draws from list(bursts(tx)) with a fixed seed."""
    out = {}
    for t in tx:
        out.setdefault(t['run'], []).append(t)
    return out


def boot_ci(runs, stat, reps=BOOTSTRAP_REPS):
    rng = random.Random(SEED)
    keys = list(runs)
    vals = []
    for _ in range(reps):
        sample = [t for k in (rng.choice(keys) for _ in keys) for t in runs[k]]
        v = stat(sample)
        if v is not None:
            vals.append(v)
    vals.sort()
    return pct_inc(vals, 0.025), pct_inc(vals, 0.975)


def margin_activation(pop, q):
    """Activation rate over the tightest q share of the population by realized
    margin.  Ties are broken by the population's own order, which is why the
    bootstrap has to reuse the loader's ordering to reproduce an interval."""
    m = sorted([t for t in pop if t['margin'] is not None], key=lambda t: t['margin'])
    if not m:
        return None
    sub = m[:max(1, int(len(m) * q))]
    return 100 * sum(1 for t in sub if t['d'] > 0) / len(sub)


def boot_margin_sweep(runs, quantiles, reps=BOOTSTRAP_REPS):
    """All quantiles from one pass of resamples.

    Drawing once and evaluating every quantile on the same replicate gives the
    identical interval a per-quantile boot_ci would, because boot_ci re-seeds and
    walks the same key list on each call; it just avoids paying for the resample
    twenty times over.
    """
    rng = random.Random(SEED)
    keys = list(runs)
    draws = {q: [] for q in quantiles}
    for _ in range(reps):
        sample = [t for k in (rng.choice(keys) for _ in keys) for t in runs[k]]
        m = sorted([t for t in sample if t['margin'] is not None],
                   key=lambda t: t['margin'])
        if not m:
            continue
        # One prefix scan serves every quantile.
        cum, run = [], 0
        for t in m:
            run += 1 if t['d'] > 0 else 0
            cum.append(run)
        for q in quantiles:
            k = max(1, int(len(m) * q))
            draws[q].append(100 * cum[k - 1] / k)
    return {q: (pct_inc(sorted(v), 0.025), pct_inc(sorted(v), 0.975))
            for q, v in draws.items()}


def bin_stats(pop, key, bins, open_top=False):
    """Activation per fixed-width bin and, among paced only, median applied delay.

    Bins are half-open [lo, hi).  With open_top the last entry collects everything
    at or above its lower edge, which is how the projected-overrun series ends.
    Bins with no transition are returned as None so a caller can skip them without
    inventing a zero.
    """
    out = []
    for i, (lo, hi) in enumerate(bins):
        last = open_top and i == len(bins) - 1
        ch = [t for t in pop if t[key] is not None
              and (lo <= t[key] if last else lo <= t[key] < hi)]
        if not ch:
            out.append(None)
            continue
        paced = [t['d'] for t in ch if t['d'] > 0]
        out.append({
            'lo': lo, 'hi': None if last else hi,
            'mid': lo + BIN_WIDTH_PCT / 2,
            'n': len(ch), 'nPaced': len(paced),
            'activation': 100 * len(paced) / len(ch),
            'delay': med(paced) if paced else None,
        })
    return out


def boot_bins(runs, key, bins, open_top=False, reps=BOOTSTRAP_REPS):
    """Cluster-bootstrap CIs for a binned series, from one pass of resamples.

    Fixed bins make this cheaper than the rank version it replaced: a replicate
    only has to be recounted into edges that do not move, so no per-replicate sort
    is needed and the bin a transition falls in never depends on the resample.
    """
    rng = random.Random(SEED)
    keys = list(runs)
    act = [[] for _ in bins]
    dly = [[] for _ in bins]
    for _ in range(reps):
        sample = [t for k in (rng.choice(keys) for _ in keys) for t in runs[k]]
        for i, b in enumerate(bin_stats(sample, key, bins, open_top)):
            if b is None:
                continue
            act[i].append(b['activation'])
            if b['delay'] is not None:
                dly[i].append(b['delay'])
    def ci(v):
        return (None, None) if not v else (pct_inc(sorted(v), 0.025), pct_inc(sorted(v), 0.975))
    return [ci(a) for a in act], [ci(d) for d in dly]


def ecdf(values):
    """(value, cumulative fraction) at each distinct value, ties collapsed."""
    v = sorted(values)
    n = len(v)
    rows = []
    for i, x in enumerate(v, start=1):
        if i == n or v[i] != x:
            rows.append((x, i / n))
    return rows


def analyse(condition, files):
    tx, _, audit = load(condition, files)
    runs = bursts(tx)
    budget = med([t['budget'] for t in tx])

    for t in tx:
        t['risk'] = t['B'] + 2 * t['C'] - max(0.0, t['T'])
        t['score'] = t['Bhat'] + 2 * t['Chat'] - max(0.0, t['T'])
        # Budget-relative forms.  Everything the exhibits plot or quote from these
        # two orderings uses these, never the millisecond originals.
        t['overrunPct'] = 100 * t['risk'] / t['budget']
        t['marginPct'] = None if t['margin'] is None else 100 * t['margin'] / t['budget']
        t['backlogPct'] = 100 * t['B'] / t['budget']

    paced = [t for t in tx if t['d'] > 0]
    unpaced = [t for t in tx if t['d'] == 0]
    activation = 100 * len(paced) / len(tx)

    # --- selectivity ------------------------------------------------------
    tautology = sum(1 for t in tx if (t['d'] > 0) == (t['score'] > 0))

    overrun = bin_stats(tx, 'overrunPct', OVERRUN_BINS, open_top=True)
    ov_act, _ = boot_bins(runs, 'overrunPct', OVERRUN_BINS, open_top=True)
    for b, a in zip(overrun, ov_act):
        if b is not None:
            b['actLo'], b['actHi'] = a

    have_margin = [t for t in tx if t['margin'] is not None]
    ci = boot_margin_sweep(runs, SWEEP)
    sweep = []
    for q in SWEEP:
        lo, hi = ci[q]
        sweep.append({'q': q, 'n': max(1, int(len(have_margin) * q)),
                      'activation': margin_activation(tx, q), 'lo': lo, 'hi': hi})

    mbins = bin_stats(tx, 'marginPct', MARGIN_BINS)
    mb_act, mb_dly = boot_bins(runs, 'marginPct', MARGIN_BINS)
    for b, a, y in zip(mbins, mb_act, mb_dly):
        if b is not None:
            b['actLo'], b['actHi'] = a
            # A resampled bin can contain paced transitions where the observed one
            # has none, so the bootstrap yields a delay interval for a bin with no
            # delay to summarise.  Drop it: an interval without a point estimate
            # reads as a measurement.
            b['delayLo'], b['delayHi'] = y if b['delay'] is not None else (None, None)

    # Points of budget, not milliseconds.  See the note on BIN_WIDTH_PCT: the two
    # backlog medians are reported as percentages, so a millisecond gap would make
    # the budget recoverable by division.
    def gap(pop):
        a = med([t['backlogPct'] for t in pop if t['d'] > 0])
        b = med([t['backlogPct'] for t in pop if t['d'] == 0])
        return None if a is None or b is None else a - b
    gap_lo, gap_hi = boot_ci(runs, gap)

    # --- responsiveness cost ---------------------------------------------
    # Delay is charged inside the shot-to-shot interval it gates, so the share
    # below is the fraction of burst wall-clock spent waiting on the pacer.  It
    # is not the time a burst would save without pacing: the queued Drafts would
    # still have to drain, and admission would face a deeper backlog.
    burst_delay, burst_share, burst_activation = [], [], []
    for v in runs.values():
        total = sum(t['d'] for t in v)
        wall = sum(t['shotToShot'] for t in v if t['shotToShot'])
        burst_delay.append(total)
        if wall:
            burst_share.append(100 * total / wall)
        burst_activation.append(100 * sum(1 for t in v if t['d'] > 0) / len(v))
    burst_activation.sort()

    s2s_paced = [t['shotToShot'] for t in paced if t['shotToShot']]
    s2s_unpaced = [t['shotToShot'] for t in unpaced if t['shotToShot']]

    return {
        'condition': condition, 'tx': tx, 'runs': runs, 'audit': audit,
        'budget': budget,
        'nAnalyzed': len(tx), 'nBursts': len(runs),
        'nRuns': sum(1 for a in audit if a['included']),
        'nPaced': len(paced), 'activation': activation,
        'tautology': tautology,
        'bandActivation': [
            {'band': b,
             'n': sum(1 for t in tx if t['band'] == b),
             'activation': 100 * sum(1 for t in tx if t['band'] == b and t['d'] > 0)
                           / sum(1 for t in tx if t['band'] == b)}
            for b in BANDS if any(t['band'] == b for t in tx)],
        'overrunBins': overrun, 'sweep': sweep, 'marginBins': mbins,
        'marginQuiet': {
            'n': sum(1 for t in have_margin if t['marginPct'] >= MARGIN_QUIET_FROM_PCT),
            'nPaced': sum(1 for t in have_margin
                          if t['marginPct'] >= MARGIN_QUIET_FROM_PCT and t['d'] > 0),
            'activation': 100 * sum(1 for t in have_margin
                                    if t['marginPct'] >= MARGIN_QUIET_FROM_PCT and t['d'] > 0)
                          / sum(1 for t in have_margin
                                if t['marginPct'] >= MARGIN_QUIET_FROM_PCT)},
        'backlogPaced': med([t['backlogPct'] for t in paced]),
        'backlogUnpaced': med([t['backlogPct'] for t in unpaced]),
        'backlogGap': gap(tx), 'backlogGapCI': (gap_lo, gap_hi),
        'backlogPacedP95': pct_inc([t['backlogPct'] for t in paced], 0.95),
        'backlogUnpacedP95': pct_inc([t['backlogPct'] for t in unpaced], 0.95),
        'delayP50': med([t['d'] for t in paced]),
        'delayP95': pct_inc([t['d'] for t in paced], 0.95),
        'delayMax': max(t['d'] for t in paced),
        'burstDelayP50': med(burst_delay), 'burstDelayP95': pct_inc(burst_delay, 0.95),
        'burstShareP50': med(burst_share), 'burstShareP95': pct_inc(burst_share, 0.95),
        'burstActivation': burst_activation,
        's2sPaced': med(s2s_paced), 's2sUnpaced': med(s2s_unpaced),
        's2sAll': med([t['shotToShot'] for t in tx if t['shotToShot']]),
        'marginP5': pct_inc([t['marginPct'] for t in have_margin], 0.05),
        'marginMin': min(t['marginPct'] for t in have_margin),
        'paced': paced, 'unpaced': unpaced,
    }


def report(res):
    print(f'=== {LABEL[res["condition"]]}')
    print(f'  {res["nRuns"]} eligible runs, {res["nBursts"]} bursts, '
          f'{res["nAnalyzed"]} analyzed transitions')
    print(f'  activation (d > 0): {res["nPaced"]} of {res["nAnalyzed"]} '
          f'= {res["activation"]:.1f}%')
    print(f'  online score > 0 <=> d > 0 on {res["tautology"]} of {res["nAnalyzed"]} '
          f'-- circular, never report as selectivity')

    print('  activation by starting thermal band:')
    for b in res['bandActivation']:
        print(f'    {b["band"]:7s} {b["activation"]:5.1f}%  [{b["n"]:4d} transitions]')

    def edge(b):
        return f'>= {b["lo"]:+4.0f}' if b['hi'] is None else f'[{b["lo"]:+4.0f},{b["hi"]:+4.0f})'

    print('  activation by projected overrun, B + 2C - T as % of budget '
          '(negative = spare time):')
    for b in res['overrunBins']:
        if b is None:
            continue
        print(f'    {edge(b):>13s}%  n={b["n"]:4d}  activation {b["activation"]:5.1f}% '
              f'[{b["actLo"]:.1f}, {b["actHi"]:.1f}]')

    print('  activation among the tightest realized margins (cumulative prefixes):')
    for q in TABLE_QUANTILES:
        r = next(x for x in res['sweep'] if abs(x['q'] - q) < 1e-9)
        print(f'    tightest {q*100:3.0f}% (n={r["n"]:4d}): {r["activation"]:5.1f}%  '
              f'[95% CI {r["lo"]:.1f}, {r["hi"]:.1f}]   vs overall {res["activation"]:.1f}%')

    print('  activation and applied delay by realized margin, % of budget:')
    for b in res['marginBins']:
        if b is None:
            continue
        act = f'{b["activation"]:5.1f}% [{b["actLo"]:.1f}, {b["actHi"]:.1f}]'
        dly = ('--' if b['delay'] is None
               else f'{b["delay"]:4.0f} ms [{b["delayLo"]:.0f}, {b["delayHi"]:.0f}]  n={b["nPaced"]}'
               + ('' if b['nPaced'] >= DELAY_PLOT_MIN_N else '  <- below min n, not quotable'))
        print(f'    {edge(b):>13s}%  n={b["n"]:4d}  {act:>22s}  {dly}')
    quiet = [b for b in res['marginBins'] if b and b['nPaced'] == 0]
    if quiet:
        n = sum(b['n'] for b in quiet)
        print(f'    bins with no pacing at all: '
              + ', '.join(f'{b["lo"]:.0f}-{b["hi"]:.0f}%' for b in quiet)
              + f' ({n} transitions)')
    q = res['marginQuiet']
    print(f'    margin >= {MARGIN_QUIET_FROM_PCT}% of budget: '
          f'{q["activation"]:.1f}% activation ({q["nPaced"]} of {q["n"]} transitions)')

    lo, hi = res['backlogGapCI']
    print('  measured backlog at the decision (% of budget): '
          f'paced P50 {res["backlogPaced"]:.1f}, unpaced P50 {res["backlogUnpaced"]:.1f}')
    print(f'    gap {res["backlogGap"]:+.1f} points  [95% CI {lo:+.1f}, {hi:+.1f}]   '
          f'P95 paced {res["backlogPacedP95"]:.1f} vs unpaced {res["backlogUnpacedP95"]:.1f}')

    print(f'  applied delay when paced (ms): P50 {res["delayP50"]:.0f}  '
          f'P95 {res["delayP95"]:.0f}  max {res["delayMax"]:.0f}')
    print(f'  cumulative delay per burst: P50 {res["burstDelayP50"]/1000:.2f} s  '
          f'P95 {res["burstDelayP95"]/1000:.2f} s  '
          f'= {res["burstShareP50"]:.1f}% / {res["burstShareP95"]:.1f}% of burst wall-clock')
    print(f'  shot-to-shot P50 (ms): paced {res["s2sPaced"]:.0f}  '
          f'unpaced {res["s2sUnpaced"]:.0f}  all {res["s2sAll"]:.0f}')

    b = res['burstActivation']
    print(f'  per-burst activation rate over {len(b)} bursts: '
          f'P25 {pct_inc(b,0.25):.1f}%  P50 {pct_inc(b,0.5):.1f}%  P75 {pct_inc(b,0.75):.1f}%  '
          f'(min {b[0]:.1f}%, max {b[-1]:.1f}%, {sum(1 for v in b if v == 0)} at 0%)')
    print(f'  realized margin (% of budget): P5 {res["marginP5"]:.1f}  '
          f'min {res["marginMin"]:.1f}  (no eligible run recorded a Capture Timeout, '
          f'so margin is the only realized-risk ordering available)')


def emit(res):
    os.makedirs(OUT, exist_ok=True)
    cond = res['condition']

    def write(name, header, rows):
        with open(os.path.join(OUT, name), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    # Panel (a).  x is the bin midpoint, so the series plots as a line whose
    # points sit inside the intervals they summarise; bin_lo/bin_hi carry the
    # actual edges, with an empty bin_hi marking the open top bin.
    write(f'overrun_bins_{cond}.csv',
          ['bin_mid_pct', 'bin_lo_pct', 'bin_hi_pct', 'n', 'n_paced',
           'activation_pct', 'act_lo_pct', 'act_hi_pct'],
          [[b['mid'], b['lo'], '' if b['hi'] is None else b['hi'], b['n'], b['nPaced'],
            round(b['activation'], 2), round(b['actLo'], 2), round(b['actHi'], 2)]
           for b in res['overrunBins'] if b is not None])

    # Panel (b), plus the delay magnitude the table quotes.  Two delay columns on
    # purpose.  delay_p50_ms is the full record for every bin that has any paced
    # transition; delay_quote_ms blanks the bins whose paced count falls below
    # DELAY_PLOT_MIN_N, because a "median" of five values is not one and its
    # bootstrap interval spans an order of magnitude.  The blanked bins stay in
    # this file and in the printed report, so the cut is visible rather than
    # silent.  Bins with no paced transition at all are blank in both columns.
    write(f'margin_bins_{cond}.csv',
          ['bin_mid_pct', 'bin_lo_pct', 'bin_hi_pct', 'n', 'n_paced',
           'activation_pct', 'act_lo_pct', 'act_hi_pct',
           'delay_p50_ms', 'delay_lo_ms', 'delay_hi_ms', 'delay_quote_ms'],
          [[b['mid'], b['lo'], '' if b['hi'] is None else b['hi'], b['n'], b['nPaced'],
            round(b['activation'], 2), round(b['actLo'], 2), round(b['actHi'], 2),
            '' if b['delay'] is None else round(b['delay']),
            '' if b['delayLo'] is None else round(b['delayLo']),
            '' if b['delayHi'] is None else round(b['delayHi']),
            '' if b['delay'] is None or b['nPaced'] < DELAY_PLOT_MIN_N else round(b['delay'])]
           for b in res['marginBins'] if b is not None])

    write(f'margin_sweep_{cond}.csv',
          ['quantile_pct', 'n', 'activation_pct', 'ci_lo_pct', 'ci_hi_pct'],
          [[round(100 * r['q']), r['n'], round(r['activation'], 2),
            round(r['lo'], 2), round(r['hi'], 2)] for r in res['sweep']])

    # Backlog as a share of the Capture Timeout budget, the unit the rest of the
    # paper uses for queue state.
    for group in ('paced', 'unpaced'):
        write(f'backlog_ecdf_{cond}_{group}.csv', ['backlog_pct', 'cdf'],
              [[round(x, 4), round(c, 5)]
               for x, c in ecdf(t['backlogPct'] for t in res[group])])

    write(f'burst_delay_ecdf_{cond}.csv', ['delay_s', 'cdf'],
          [[round(x / 1000, 4), round(c, 5)]
           for x, c in ecdf(sum(t['d'] for t in v) for v in res['runs'].values())])

    # The same cost as a share of the burst's elapsed time.  Seconds is the more
    # concrete unit but its 24MP tail reaches 18.5 s on a single burst, which
    # either clips or compresses the mass every other burst sits in; the share is
    # bounded by the data at 53% and needs no clipping.
    write(f'burst_share_ecdf_{cond}.csv', ['delay_share_pct', 'cdf'],
          [[round(x, 4), round(c, 5)]
           for x, c in ecdf(100 * sum(t['d'] for t in v)
                            / sum(t['shotToShot'] for t in v if t['shotToShot'])
                            for v in res['runs'].values()
                            if any(t['shotToShot'] for t in v))])


def write_summary(results):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'summary.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['condition', 'metric', 'value', 'ciLo', 'ciHi', 'n'])
        for res in results:
            c = LABEL[res['condition']]
            w.writerow([c, 'activationPercent', round(res['activation'], 1),
                        '', '', res['nAnalyzed']])
            for b in res['bandActivation']:
                w.writerow([c, f'activationPercent {b["band"]}',
                            round(b['activation'], 1), '', '', b['n']])
            for b in res['overrunBins']:
                if b is None:
                    continue
                name = (f'overrunGe{b["lo"]:+d}pct' if b['hi'] is None
                        else f'overrun{b["lo"]:+d}to{b["hi"]:+d}pct')
                w.writerow([c, f'activationPercent {name}', round(b['activation'], 1),
                            round(b['actLo'], 1), round(b['actHi'], 1), b['n']])
            for b in res['marginBins']:
                if b is None:
                    continue
                w.writerow([c, f'activationPercent margin{b["lo"]:d}to{b["hi"]:d}pct',
                            round(b['activation'], 1), round(b['actLo'], 1),
                            round(b['actHi'], 1), b['n']])
                if b['delay'] is not None and b['nPaced'] >= DELAY_PLOT_MIN_N:
                    w.writerow([c, f'pacedDelayP50Ms margin{b["lo"]:d}to{b["hi"]:d}pct',
                                round(b['delay']), round(b['delayLo']),
                                round(b['delayHi']), b['nPaced']])
            for q in TABLE_QUANTILES:
                r = next(x for x in res['sweep'] if abs(x['q'] - q) < 1e-9)
                w.writerow([c, f'activationPercent tightest{round(100*q)}pct',
                            round(r['activation'], 1), round(r['lo'], 1),
                            round(r['hi'], 1), r['n']])
            lo, hi = res['backlogGapCI']
            w.writerow([c, 'backlogPacedP50Percent', round(res['backlogPaced'], 1),
                        '', '', res['nPaced']])
            w.writerow([c, 'backlogUnpacedP50Percent', round(res['backlogUnpaced'], 1),
                        '', '', res['nAnalyzed'] - res['nPaced']])
            w.writerow([c, 'backlogGapPoints', round(res['backlogGap'], 1),
                        round(lo, 1), round(hi, 1), res['nAnalyzed']])
            w.writerow([c, 'delayP50Ms', round(res['delayP50']), '', '', res['nPaced']])
            w.writerow([c, 'delayP95Ms', round(res['delayP95']), '', '', res['nPaced']])
            w.writerow([c, 'burstDelayP50Ms', round(res['burstDelayP50']),
                        '', '', res['nBursts']])
            w.writerow([c, 'burstDelaySharePercent', round(res['burstShareP50'], 1),
                        '', '', res['nBursts']])
            q = res['marginQuiet']
            w.writerow([c, f'activationPercent marginGe{MARGIN_QUIET_FROM_PCT}pct',
                        round(q['activation'], 1), '', '', q['n']])
            b = res['burstActivation']
            for q, name in ((0.25, 'P25'), (0.5, 'P50'), (0.75, 'P75')):
                w.writerow([c, f'burstActivationPercent {name}',
                            round(pct_inc(b, q), 1), '', '', len(b)])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    source = args[0] if args else 'sampling'
    results = [analyse(c, SOURCES[source][c]) for c in CONDITIONS]
    print(f'source: {source}\n')
    for res in results:
        report(res)
        print()
    if '--no-write' not in sys.argv[1:]:
        for res in results:
            emit(res)
        write_summary(results)
        print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
