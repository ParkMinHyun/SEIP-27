"""RQ3 policy evidence: what the recorded traces can and cannot establish about
the pacing policy.

Companion to scripts/rq3_calibration_metrics.py, which computes the estimator
calibration currently shown in Table~\\ref{tab:rq3_pacing_calibration}.  This
script exists because that calibration answers a different question than the one
RQ3 asks.  It emits three blocks:

  variants()      four readings of "the required delay", to show what a
                  timeout-based criterion can and cannot discriminate;
  selectivity()   whether pacing fires where measured risk is, on quantiles and
                  with a burst-cluster bootstrap;
  sensitivity()   the margin-based removable-delay estimate, reported under every
                  aggregation unit because the unit changes the answer.

Read the caveats printed with each block before quoting anything.

Run:
    python scripts/rq3_policy_evidence.py [raw|original|sampling]
"""
import math
import random
import sys
import warnings

warnings.filterwarnings('ignore')

from rq3_calibration_metrics import (BANDS, CONDITIONS, SOURCES, load, med, pct_inc)

SEED = 20260806
BOOTSTRAP_REPS = 2000


def bursts(tx):
    out = {}
    for t in tx:
        out.setdefault(t['run'], []).append(t)
    return out


def boot_ci(runs, stat, reps=BOOTSTRAP_REPS):
    """Cluster bootstrap over bursts.  Transitions within a burst are strongly
    correlated, so resampling transitions would overstate precision."""
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


def variants(tx):
    """Four readings of the requirement.

    A is the deployed two-Draft admissibility condition re-solved on measured
    inputs -- the current table's d*.  B drops the prospective horizon to one
    Draft, i.e. "was this capture's own deadline threatened".  C inverts the
    realized margin: how much of the applied delay was load-bearing if 1 ms of
    delay is worth k ms of margin (k = 2 is the pacer's own model, k = 1 the
    conservative reading).

    C cannot serve as a sufficiency criterion: the eligible set contains no
    Capture Timeout, so coverage under C is 100% by construction.
    """
    def report(name, req_fn):
        req = [t for t in tx if req_fn(t) > 0]
        cov = [t for t in req if t['d'] >= req_fn(t)]
        deficits = [req_fn(t) - t['d'] for t in req if t['d'] < req_fn(t)]
        band = []
        for b in BANDS:
            rb = [t for t in req if t['band'] == b]
            cb = [t for t in rb if t['d'] >= req_fn(t)]
            band.append(f'{b} {100*len(cb)/len(rb):.0f}% [{len(rb)}]' if rb else f'{b} -- [0]')
        cover = 100 * len(cov) / len(req) if req else 100.0
        print(f'    {name:38s} n_req {len(req):4d}  cov {cover:5.1f}%  '
              f'worst {max(deficits) if deficits else 0:5.0f}   ' + '  '.join(band))

    print('  requirement variants')
    report('A  deployed   B + 2C - T  (current d*)',
           lambda t: math.ceil(max(0.0, t['B'] + 2*t['C'] - max(0.0, t['T'])) / 2))
    report('B  one-Draft  B + C - T',
           lambda t: math.ceil(max(0.0, t['B'] + t['C'] - max(0.0, t['T'])) / 2))
    for k in (2.0, 1.0):
        report(f'C  timeout    d - margin/{k:.0f}  (degenerate)',
               lambda t, k=k: max(0.0, math.ceil(t['d'] - (t['margin'] or 0) / k)))


def selectivity(tx):
    """Does pacing intervene where measured risk is?

    The online trigger score Bhat + 2*Chat - T is NOT reportable as evidence: the
    pacer applies a delay exactly when that score is positive, so activation
    against it is true by construction.  Only the measured proxy (which
    substitutes the observed backlog and Draft duration) and the realized margin
    carry information.

    Realized margin is itself endogenous -- pacing raises it -- but the bias runs
    against the finding: random intervention would over-populate the loose tail,
    not the tight one.
    """
    runs = bursts(tx)
    for t in tx:
        t['risk'] = t['B'] + 2*t['C'] - max(0.0, t['T'])
        t['score'] = t['Bhat'] + 2*t['Chat'] - max(0.0, t['T'])

    taut = sum(1 for t in tx if (t['d'] > 0) == (t['score'] > 0))
    print(f'  online score > 0 <=> d > 0 on {taut} of {len(tx)} '
          f'({100*taut/len(tx):.1f}%) -- circular, do not report as selectivity')

    s = sorted(tx, key=lambda t: t['risk'])
    deciles = []
    for i in range(10):
        d = s[len(s)*i//10:len(s)*(i+1)//10]
        deciles.append(100 * sum(1 for t in d if t['d'] > 0) / len(d))
    print('  activation by measured-risk decile (B+2C-T, low -> high):')
    print('    ' + '  '.join(f'D{i+1} {v:4.1f}%' for i, v in enumerate(deciles)))

    overall = 100 * sum(1 for t in tx if t['d'] > 0) / len(tx)
    have = [t for t in tx if t['margin'] is not None]
    for q in (0.05, 0.10, 0.25):
        def stat(pop, q=q):
            m = sorted([t for t in pop if t['margin'] is not None], key=lambda t: t['margin'])
            sub = m[:max(1, int(len(m) * q))]
            return 100 * sum(1 for t in sub if t['d'] > 0) / len(sub)
        lo, hi = boot_ci(runs, stat)
        n = max(1, int(len(have) * q))
        print(f'  tightest {q*100:4.0f}% by realized margin (n={n:4d}): '
              f'activation {stat(tx):5.1f}%  [95% CI {lo:.1f}, {hi:.1f}]  vs overall {overall:.1f}%')

    def gap(pop):
        a = med([t['B'] for t in pop if t['d'] > 0])
        b = med([t['B'] for t in pop if t['d'] == 0])
        return None if a is None or b is None else a - b
    lo, hi = boot_ci(runs, gap)
    print(f'  median backlog gap paced - unpaced: {gap(tx):+.0f} ms  [95% CI {lo:+.0f}, {hi:+.0f}]')


def sensitivity(tx):
    """Margin-based removable delay, under every aggregation unit.

    NOT a causal lower bound on necessary delay.  Reducing a delay also changes
    the drain of earlier Drafts, this capture's deadline, later queue state,
    admission decisions and predictor inputs, so this is a trace-conditioned
    local sensitivity estimate only.  Reported here because an earlier revision
    quoted the ratio-of-medians form as though it were a bound; the four rows
    differ by more than 30 points, which is why the unit has to be stated.
    """
    runs = bursts(tx)
    paced = [t for t in tx if t['d'] > 0]
    per_burst = [sum(min(t['d'], (t['margin'] or 0)/2) for t in v) / sum(t['d'] for t in v)
                 for v in runs.values() if sum(t['d'] for t in v) > 0]
    ratio_of_med = (med([sum(min(t['d'], (t['margin'] or 0)/2) for t in v) for v in runs.values()])
                    / med([sum(t['d'] for t in v) for v in runs.values()]))
    pooled = (sum(min(t['d'], (t['margin'] or 0)/2) for t in tx) / sum(t['d'] for t in tx))
    print('  removable delay (k=2), by aggregation unit:')
    print(f'    ratio of per-burst medians  {100*ratio_of_med:5.0f}%   <- not a statistic; do not quote')
    print(f'    median of per-burst ratios  {100*med(per_burst):5.0f}%   '
          f'(IQR {100*pct_inc(per_burst,0.25):.0f}-{100*pct_inc(per_burst,0.75):.0f})')
    print(f'    pooled delay-weighted       {100*pooled:5.0f}%')
    print(f'    median over paced transitions {100*med([min(t["d"], (t["margin"] or 0)/2)/t["d"] for t in paced]):3.0f}%')


def dispersion(tx):
    """Coverage is a mixture, not a level: report the run-level distribution."""
    per = []
    for v in bursts(tx).values():
        req = [t for t in v if t['required'] > 0]
        if req:
            per.append(100 * sum(1 for t in req if t['d'] >= t['required']) / len(req))
    per.sort()
    print(f'  run-level coverage over {len(per)} bursts with a requirement: '
          f'P25 {pct_inc(per,0.25):.0f}%  P50 {pct_inc(per,0.5):.0f}%  P75 {pct_inc(per,0.75):.0f}%  '
          f'({sum(1 for v in per if v == 0)} bursts at 0%, {sum(1 for v in per if v == 100)} at 100%)')


def main():
    source = (sys.argv[1:] or ['sampling'])[0]
    for cond in CONDITIONS:
        tx, _, _ = load(cond, SOURCES[source][cond])
        print('=' * 78)
        print(f'{cond}  ({len(tx)} transitions, {len(bursts(tx))} bursts, source={source})')
        variants(tx)
        selectivity(tx)
        sensitivity(tx)
        dispersion(tx)


if __name__ == '__main__':
    main()
