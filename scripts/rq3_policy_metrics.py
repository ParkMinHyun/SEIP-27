"""RQ3 pacing policy: selectivity, boundary diagnosis and admission-aware delay
sizing.

Emits everything Table~\\ref{tab:rq3_pacing_policy} and
Figure~\\ref{fig:rq3_pacing_policy} report, into data/rq3/policy/.

Scope, and how it relates to the two sibling scripts
----------------------------------------------------
scripts/rq3_selectivity_metrics.py asks where the pacer fires and what the
intervention costs.  scripts/rq3_calibration_metrics.py asks how badly the
controller prices its own reserve.  This script asks the two questions neither
answers:

  1. Why do the two boundary mismatches happen?  Some transitions were paced
     although the retrospective trace later showed more than 40% of the budget
     spare, and some projected an overrun retrospectively yet received no delay.
     Both groups are diagnosed against the controller's own estimation error, the
     admission demotions that preceded the decision, and the thermal drift over
     the target's queue residence.
  2. Is the applied delay the right SIZE for what admission left behind?  The
     deployed delay is

         d = ceil( max(0, Bhat + 2*Chat_adm - max(0,T)) / 2 )

     which is the least integer delay that closes the predicted deficit under the
     deployed two-Draft model: waiting d ms drains d ms of outstanding backlog
     and shifts the next capture's deadline by d ms, so the residual deficit
     falls by 2d.  The script checks the recorded delay against that value and
     measures how much of the applied delay overlapped outstanding work.

Loader, populations and intervals are inherited rather than reimplemented: the
eligible transition set comes from rq3_calibration_metrics.load, and the binning
and cluster bootstrap come from rq3_selectivity_metrics.  Every population count
printed here therefore matches those scripts exactly, and the interval for the
projected-overrun band is the same number as the "overrun >= 0% of budget" row of
Table~\\ref{tab:rq3_pacing_selectivity} rather than merely compatible with it.

What may and may not be reported
--------------------------------
Activation is d > 0.  The pacer applies a delay exactly when its own online score
Bhat + 2*Chat_adm - max(0,T) is positive, so activation against that score is true
by construction and is NOT evidence of selectivity.  The orderings used here are
ones the controller did not observe: the retrospective pressure B + 2C - max(0,T)
computed from the measured backlog and the Draft as it actually ran, the measured
backlog itself, and the burst's elapsed time.

Units.  Risk quantities are shares of the Capture Timeout budget and never
milliseconds, so that no rendered cell or axis discloses the budget; the backlog
estimation error is therefore reported in points of budget.  The budget is a
single constant across every analyzed transition (asserted below), so normalising
per transition and by the pooled value are the same operation.  Durations that are
not budget-normalised anywhere -- the reserve errors and the queue residence --
stay in milliseconds.

Signs.  Every estimation-error quantity is signed estimate minus realized, so a
positive number always means the controller reserved more than it turned out to
need.  The workbook records the target and queued-ahead reserve errors with the
opposite sense (realized minus reserved); they are negated here.

Definitions
-----------
  B          measured backlog at the decision (RQ3Pacing.realBacklogMs)
  C          realized duration of the admitted Draft sequence
  T          window left on the newest committed capture's deadline
  Bhat       the controller's backlog estimate at the decision
  Chat_adm   reserved duration of the sequence admission selected, i.e. the
             post-admission reserve and not that of the sequence first planned
  pressure   B + 2C - max(0,T), as a share of the budget; negative is spare
  safe but paced      pressure < -40% of budget with d > 0
  overrun, unpaced    pressure >= 0 with d = 0
  demotion   the executed sequence's class ranks below the planned class, on
             Bokeh+Filter > Filter only > Encoding only.  NOTE this is not
             load()'s 'demoted' field, which compares the two workload keys for
             equality; the keys also differ on watermark and format changes that
             remove no optional work, and the two definitions disagree on 19 of
             the 3,781 analyzed transitions.  Use seqDemoted, never demoted.
  ahead task a Draft sequence of the same burst that ends after the decision and
             starts before the target's own Draft.  Reconstructed over the
             analyzed transitions of that burst, so Draft work belonging to shots
             1--2 or to a watchdog-dropped capture is invisible to it; the counts
             are lower bounds for that reason.
  decision-proximal thermal snapshot
             the thermal triple recorded for the most recently started Draft
             sequence at the decision timestamp.  A trace-derived proxy for the
             thermal state the controller decided under, not a reading taken at
             the decision.  Every thermal statement from it is an association.

Limits inherited from the sibling exhibits, both of which apply unchanged: the
population is survival-conditioned because the source export had already filtered
the Capture-Timeout sessions out, and the 12MP thermal rows carry the RQ1(a)
balancing-trim bias.  See tables/tab_rq3_pacing_selectivity.tex.

Run:
    python scripts/rq3_policy_metrics.py sampling
    python scripts/rq3_policy_metrics.py sampling --no-write
"""
import csv
import math
import os
import sys
import warnings

warnings.filterwarnings('ignore')

from rq3_calibration_metrics import (CONDITIONS, SOURCES, load, med, pct_inc,
                                     read)
from rq3_selectivity_metrics import bin_stats, boot_bins, bursts, ecdf

PAPER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PAPER, 'data', 'rq3', 'policy')

# The pressure bands.  Twenty points wide rather than the ten of
# Figure~\ref{fig:rq3_pacing_selectivity}(a), because what this pair supports is a
# threshold claim and not a shape claim, and because the two boundary classes are
# defined on the outer two bands.  Half-open [lo, hi); the last is open at its
# lower edge and is exactly the required set of the calibration exhibit.
BANDS = ((-10 ** 9, -40.0, 'spare_over_40'),
         (-40.0, -20.0, 'spare_20_40'),
         (-20.0, 0.0, 'spare_0_20'),
         (0.0, 0.0, 'projected_overrun'))
# bin_stats takes (lo, hi) pairs and ignores the last hi under open_top, so the
# band names travel separately.
BAND_EDGES = [(lo, hi) for lo, hi, _ in BANDS]
BAND_NAMES = [name for _, _, name in BANDS]
# The safe-but-paced cut, i.e. the lower edge of the loosest band.
SAFE_SPARE_PCT = -40.0
# How close to the deadline projection a crossing has to be to count as shallow.
BOUNDARY_NEAR_PCT = 10.0
# Quantiles of the backlog error drawn as the marginal strip in panel (b).
MARGINAL_QUANTILES = (0.05, 0.25, 0.50, 0.75, 0.95)

# Optional-work ranking of a workload sequence.  Bokeh is the multi-frame stage
# admission drops first, Filter the single-frame stage it drops next; the encoding
# pass is mandatory and cannot be dropped, so an encoding-only sequence is the
# floor.
SEQUENCE_CLASS = ('Encoding only', 'Filter only', 'Bokeh+Filter')


def sequence_rank(key):
    k = '' if key is None else str(key)
    return 2 if 'BOKEH' in k else 1 if 'FILTER' in k else 0


def fnum(v):
    return None if v is None else float(v)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def enrich(condition, files):
    """The analyzed transitions of one condition, plus the fields the boundary
    diagnosis needs and load() does not keep.

    load() owns run and transition eligibility; this function only joins extra
    RQ3Pacing columns onto the set it returns, keyed by (run, runShotIndex), and
    then reconstructs the per-burst queue relations.  A KeyError here would mean
    the two passes disagree on the key, which is a bug rather than a data
    condition, so it is deliberately not caught.
    """
    kept, _, audit = load(condition, files)
    shots = {}
    for part, path in enumerate(files, start=1):
        for r in read(path, 'RQ3Pacing'):
            if r['runId'] is None or r['runShotIndex'] is None:
                continue
            shots[(f'{part}#{int(r["runId"])}', int(r['runShotIndex']))] = r

    tx = []
    for t in kept:
        r = shots[(t['run'], t['shot'])]
        t = dict(t)
        planned = sequence_rank(r['plannedWorkloadSequenceKey'])
        executed = sequence_rank(r['executedWorkloadSequenceKey'])
        t.update({
            'condition': condition,
            'captureIndex': int(r['captureIndex']),
            'decision': fnum(r['decisionUptimeMs']),
            'draftStart': fnum(r['draftStartUptimeMs']),
            'draftEnd': fnum(r['draftEndUptimeMs']),
            'plannedRank': planned,
            'seqRank': executed,
            'plannedClass': SEQUENCE_CLASS[planned],
            'executedClass': SEQUENCE_CLASS[executed],
            # Rank demotion, not the key inequality load() records.  See the
            # module docstring.
            'seqDemoted': executed < planned,
            'headroom': fnum(r['shotThermalHeadroom']),
            'status': fnum(r['shotThermalStatus']),
            'overheat': fnum(r['shotOverheatLevel']),
        })
        t['risk'] = t['B'] + 2 * t['C'] - max(0.0, t['T'])
        t['riskPct'] = 100 * t['risk'] / t['budget']
        # Estimate minus realized throughout: positive means over-reserved.
        t['backlogError'] = t['Bhat'] - t['B']
        t['backlogErrorPct'] = 100 * t['backlogError'] / t['budget']
        t['reserveError'] = t['Chat'] - t['C']
        t['wait'] = (None if t['draftStart'] is None or t['decision'] is None
                     else t['draftStart'] - t['decision'])
        tx.append(t)

    budgets = {t['budget'] for t in tx}
    assert len(budgets) == 1, f'{condition}: captureTimeoutMs is not constant: {budgets}'

    for group in bursts(tx).values():
        order = sorted(group, key=lambda t: t['captureIndex'])
        for t in order:
            # Decision-proximal thermal proxy: the most recently started Draft at
            # the decision timestamp.  The target's own Draft starts after its
            # decision on every analyzed transition, so excluding it changes
            # nothing; it is excluded anyway because the intent is a prior state.
            proxy = None
            for o in order:
                if (o is t or o['draftStart'] is None or t['decision'] is None
                        or o['draftStart'] > t['decision']):
                    continue
                if proxy is None or o['draftStart'] > proxy['draftStart']:
                    proxy = o
            t['proxy'] = proxy
            t['headroomDelta'] = (None if proxy is None or proxy['headroom'] is None
                                  or t['headroom'] is None
                                  else t['headroom'] - proxy['headroom'])
            t['statusDelta'] = (None if proxy is None or proxy['status'] is None
                                or t['status'] is None
                                else t['status'] - proxy['status'])
            t['overheatDelta'] = (None if proxy is None or proxy['overheat'] is None
                                  or t['overheat'] is None
                                  else t['overheat'] - proxy['overheat'])
            # Queued-ahead work: ends after the decision, starts before the
            # target's own Draft.
            t['ahead'] = [o for o in order
                          if o is not t
                          and o['draftEnd'] is not None and t['decision'] is not None
                          and o['draftEnd'] > t['decision']
                          and o['draftStart'] is not None and t['draftStart'] is not None
                          and o['draftStart'] < t['draftStart']]
            t['aheadReserveError'] = sum(o['reserveError'] for o in t['ahead'])
    return tx, audit


def boundary_class(t):
    if t['riskPct'] < SAFE_SPARE_PCT and t['d'] > 0:
        return 'safe_but_paced'
    if t['riskPct'] >= 0 and t['d'] == 0:
        return 'overrun_but_unpaced'
    return 'other'


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def analyse(condition, files):
    tx, audit = enrich(condition, files)
    runs = bursts(tx)
    paced = [t for t in tx if t['d'] > 0]

    bands = bin_stats(tx, 'riskPct', BAND_EDGES, open_top=True)
    band_ci, _ = boot_bins(runs, 'riskPct', BAND_EDGES, open_top=True)
    assert all(b is not None for b in bands), f'{condition}: an empty pressure band'
    for b, ci in zip(bands, band_ci):
        b['actLo'], b['actHi'] = ci

    # --- admission-aware sizing ------------------------------------------
    # The model delay, recomputed from the controller's own inputs.  A mismatch
    # would mean the recorded delay is not the deployed formula's output, which is
    # the one claim in this block that is not a measurement.
    matches = sum(1 for t in tx
                  if t['d'] == math.ceil(max(0.0, t['Bhat'] + 2 * t['Chat']
                                             - max(0.0, t['T'])) / 2))
    # Work conservation: the share of applied delay that ran while at least that
    # much Draft work was still outstanding.  min(d, B) is the overlap; a wait
    # longer than the backlog it drains is idle for the remainder.
    applied = sum(t['d'] for t in paced)
    overlap = sum(min(t['d'], t['B']) for t in paced)
    outlast = [t for t in paced if t['d'] > t['B']]
    ratio = [100 * t['d'] / t['B'] for t in paced if t['B'] > 0]

    # --- responsiveness cost ---------------------------------------------
    shares = [100 * sum(t['d'] for t in v) / sum(t['shotToShot'] for t in v)
              for v in runs.values()]

    return {
        'condition': condition, 'tx': tx, 'audit': audit, 'runs': runs,
        'bands': bands,
        'nAnalyzed': len(tx), 'nBursts': len(runs), 'nPaced': len(paced),
        'activation': 100 * len(paced) / len(tx),
        'formulaMatches': matches,
        'overlapPercent': 100 * overlap / applied if applied else None,
        'outlast': len(outlast),
        'ratio': ratio,
        'ratioP50': med(ratio), 'ratioP95': pct_inc(ratio, 0.95),
        'delayP50': med([t['d'] for t in paced]),
        'delayP95': pct_inc([t['d'] for t in paced], 0.95),
        'shares': shares,
        'shareP50': med(shares), 'shareP95': pct_inc(shares, 0.95),
        'neverPaced': sum(1 for s in shares if s == 0),
        'safeButPaced': [t for t in tx if boundary_class(t) == 'safe_but_paced'],
        'overrunButUnpaced': [t for t in tx if boundary_class(t) == 'overrun_but_unpaced'],
    }


def mechanism(cases, group):
    """The mechanism rates the two boundary groups report.

    Pooled over both conditions on purpose: the groups hold 15 and 62 cases, and a
    rate over 6 of them would not be a summary of anything.
    """
    n = len(cases)
    ahead = [o for t in cases for o in t['ahead']]
    headroom = [t for t in cases if t['headroomDelta'] is not None]
    if group == 'safe':
        rows = [
            ('target_sequence_demoted', sum(1 for t in cases if t['seqDemoted']), n),
            ('queued_ahead_work_demoted', sum(1 for o in ahead if o['seqDemoted']), len(ahead)),
            ('backlog_over_estimated', sum(1 for t in cases if t['backlogError'] > 0), n),
        ]
    else:
        rows = [
            ('backlog_under_estimated', sum(1 for t in cases if t['backlogError'] < 0), n),
            ('thermal_headroom_rose', sum(1 for t in headroom if t['headroomDelta'] > 0), len(headroom)),
            ('thermal_status_rose',
             sum(1 for t in cases if t['statusDelta'] is not None and t['statusDelta'] > 0), n),
        ]
    return rows


def boundary_stats(cases):
    """The per-group medians and counts the table prints."""
    ahead = [o for t in cases for o in t['ahead']]
    headroom = [t for t in cases if t['headroomDelta'] is not None]
    return {
        'n': len(cases),
        'byCondition': {c: sum(1 for t in cases if t['condition'] == c) for c in CONDITIONS},
        'demoted': sum(1 for t in cases if t['seqDemoted']),
        'aheadTasks': len(ahead),
        'aheadDemoted': sum(1 for o in ahead if o['seqDemoted']),
        'backlogOver': sum(1 for t in cases if t['backlogError'] > 0),
        'backlogUnder': sum(1 for t in cases if t['backlogError'] < 0),
        'backlogErrorP50Pct': med([t['backlogErrorPct'] for t in cases]),
        'reserveErrorP50Ms': med([t['reserveError'] for t in cases]),
        'aheadReserveErrorP50Ms': med([t['aheadReserveError'] for t in cases]),
        'waitP50Ms': med([t['wait'] for t in cases if t['wait'] is not None]),
        'headroomN': len(headroom),
        'headroomRose': sum(1 for t in headroom if t['headroomDelta'] > 0),
        'headroomDeltaP50': med([t['headroomDelta'] for t in headroom]),
        'statusRose': sum(1 for t in cases
                          if t['statusDelta'] is not None and t['statusDelta'] > 0),
        'overheatRose': sum(1 for t in cases
                            if t['overheatDelta'] is not None and t['overheatDelta'] > 0),
        'nearBoundary': sum(1 for t in cases if abs(t['riskPct']) <= BOUNDARY_NEAR_PCT),
        'riskP50Pct': med([t['riskPct'] for t in cases]),
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def report(res):
    c = res['condition']
    print('=' * 78)
    print(f'{c}  ({res["nAnalyzed"]} analyzed transitions, {res["nBursts"]} bursts)')
    print(f'  activation (d > 0): {res["nPaced"]} of {res["nAnalyzed"]} '
          f'= {res["activation"]:.1f}%')
    print('  activation by retrospective pressure band (negative = spare time):')
    for b, name in zip(res['bands'], BAND_NAMES):
        if b is None:
            continue
        print(f'    {name:18s} n={b["n"]:4d}  activation {b["activation"]:5.1f}% '
              f'[{b["actLo"]:.1f}, {b["actHi"]:.1f}]')
    print(f'  delay-formula matches: {res["formulaMatches"]} of {res["nAnalyzed"]}')
    print(f'  applied delay inside outstanding backlog: {res["overlapPercent"]:.1f}%  '
          f'({res["outlast"]} of {res["nPaced"]} waits outlast it)')
    print(f'  delay / backlog (%): P50 {res["ratioP50"]:.1f}  P95 {res["ratioP95"]:.1f}  '
          f'max {max(res["ratio"]):.1f}')
    print(f'  applied delay when paced (ms): P50 {res["delayP50"]:.0f}  '
          f'P95 {res["delayP95"]:.0f}')
    print(f'  per-burst delay share (%): P50 {res["shareP50"]:.1f}  '
          f'P95 {res["shareP95"]:.1f}   ({res["neverPaced"]} of {res["nBursts"]} never paced)')
    print(f'  boundary: {len(res["safeButPaced"])} safe-but-paced, '
          f'{len(res["overrunButUnpaced"])} overrun-but-unpaced')


def report_boundary(name, cases):
    s = boundary_stats(cases)
    print('-' * 78)
    print(f'{name}: {s["n"]} cases  ' +
          '  '.join(f'{k} {v}' for k, v in s['byCondition'].items()))
    print(f'  target sequence demoted        {s["demoted"]} of {s["n"]}')
    print(f'  queued-ahead tasks demoted     {s["aheadDemoted"]} of {s["aheadTasks"]}')
    print(f'  backlog over / under-estimated {s["backlogOver"]} / {s["backlogUnder"]} '
          f'of {s["n"]}')
    print(f'  median Bhat - B                {s["backlogErrorP50Pct"]:+.1f} points of budget')
    print(f'  median Chat_adm - C, target    {s["reserveErrorP50Ms"]:+.0f} ms')
    print(f'  median queued-ahead reserve    {s["aheadReserveErrorP50Ms"]:+.0f} ms')
    print(f'  median decision-to-Draft-start {s["waitP50Ms"]:.0f} ms')
    print(f'  thermal headroom rose          {s["headroomRose"]} of {s["headroomN"]} '
          f'(median delta {s["headroomDeltaP50"]:+.3f})')
    print(f'  thermal status / level rose     {s["statusRose"]} / {s["overheatRose"]} '
          f'of {s["n"]}')
    print(f'  within {BOUNDARY_NEAR_PCT:.0f} points of projection  '
          f'{s["nearBoundary"]} of {s["n"]}')
    print(f'  median retrospective pressure  {s["riskP50Pct"]:+.1f}% of budget')


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def write(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


CASE_COLUMNS = ('boundaryClass', 'condition', 'run', 'shot', 'captureIndex', 'level',
                'plannedClass', 'executedClass', 'seqDemoted', 'riskPct', 'd',
                'B', 'Bhat', 'backlogError', 'backlogErrorPct', 'C', 'Chat',
                'reserveError', 'wait', 'headroom', 'headroomDelta',
                'statusDelta', 'overheatDelta', 'aheadCount', 'aheadDemotedCount',
                'aheadReserveError', 'aheadCaptureIndices')


def case_row(cls, t):
    return [cls, t['condition'], t['run'], t['shot'], t['captureIndex'], t['level'],
            t['plannedClass'], t['executedClass'], t['seqDemoted'],
            round(t['riskPct'], 4), round(t['d']),
            round(t['B']), round(t['Bhat']), round(t['backlogError']),
            round(t['backlogErrorPct'], 4), round(t['C']), round(t['Chat']),
            round(t['reserveError']),
            '' if t['wait'] is None else round(t['wait']),
            '' if t['headroom'] is None else round(t['headroom'], 6),
            '' if t['headroomDelta'] is None else round(t['headroomDelta'], 6),
            '' if t['statusDelta'] is None else round(t['statusDelta']),
            '' if t['overheatDelta'] is None else round(t['overheatDelta']),
            len(t['ahead']), sum(1 for o in t['ahead'] if o['seqDemoted']),
            round(t['aheadReserveError']),
            '|'.join(str(o['captureIndex']) for o in t['ahead'])]


def write_all(results, safe, overrun):
    os.makedirs(OUT, exist_ok=True)
    every = [t for res in results.values() for t in res['tx']]

    for cond, res in results.items():
        slug = cond
        # slot descends so the loosest band sits at the top of a horizontal
        # rendering; band_index ascends left to right, which is what the figure
        # plots.
        write(f'band_activation_{slug}.csv',
              ['slot', 'band_index', 'band', 'n', 'n_paced', 'activation_pct',
               'act_lo_pct', 'act_hi_pct', 'err_lo_pct', 'err_hi_pct'],
              [[len(BANDS) - 1 - i, i, name, b['n'], b['nPaced'],
                round(b['activation'], 2), round(b['actLo'], 2), round(b['actHi'], 2),
                round(b['activation'] - b['actLo'], 2),
                round(b['actHi'] - b['activation'], 2)]
               for i, (b, name) in enumerate(zip(res['bands'], BAND_NAMES))])
        write(f'delay_backlog_ecdf_{slug}.csv', ['delay_backlog_pct', 'cdf'],
              [[round(x, 4), round(c, 5)] for x, c in ecdf(res['ratio'])])

    # slot descends from the top so the first mechanism listed reads first.
    mech = [('safe', row) for row in mechanism(safe, 'safe')]
    mech += [('overrun', row) for row in mechanism(overrun, 'overrun')]
    write('boundary_mechanism.csv',
          ['slot', 'group', 'mechanism', 'rate_pct', 'numerator', 'denominator'],
          [[len(mech) - i, group, name, round(100 * num / den, 2), num, den]
           for i, (group, (name, num, den)) in enumerate(mech)])

    for name, cases in (('safe_paced', safe), ('overrun_unpaced', overrun)):
        write(f'boundary_{name}.csv',
              ['backlog_error_pts', 'pressure_pct', 'condition'],
              [[round(t['backlogErrorPct'], 2), round(t['riskPct'], 2), t['condition']]
               for t in cases])

    write('boundary_case_details.csv', list(CASE_COLUMNS),
          [case_row('safe_but_paced', t) for t in safe]
          + [case_row('overrun_but_unpaced', t) for t in overrun])

    # The population behind the marginal strip of panel (b), and the five
    # quantiles the figure draws from it.
    write('pressure_cloud.csv', ['backlog_error_pts', 'pressure_pct'],
          [[round(t['backlogErrorPct'], 2), round(t['riskPct'], 2)] for t in every])
    write('backlog_error_quantiles.csv', ['quantile', 'backlog_error_pts', 'n'],
          [[q, round(pct_inc([t['backlogErrorPct'] for t in every], q), 2), len(every)]
           for q in MARGINAL_QUANTILES])


def write_summary(results, safe, overrun):
    rows = []
    for cond, res in results.items():
        def put(metric, value, den=''):
            rows.append([cond, metric, value, den])
        put('analyzedTransitions', res['nAnalyzed'])
        put('bursts', res['nBursts'])
        put('pacedTransitions', res['nPaced'])
        put('activationPercent', round(res['activation'], 2), res['nAnalyzed'])
        for b, name in zip(res['bands'], BAND_NAMES):
            put(f'activationPercent band {name}', round(b['activation'], 2), b['n'])
        put('safeButPaced', len(res['safeButPaced']), res['bands'][0]['n'])
        put('overrunButUnpaced', len(res['overrunButUnpaced']), res['bands'][-1]['n'])
        put('delayFormulaMatches', res['formulaMatches'], res['nAnalyzed'])
        put('backlogDrainingDelaySharePercent', round(res['overlapPercent'], 2))
        put('waitsOutlastingBacklog', res['outlast'], res['nPaced'])
        put('delayOverBacklogPercent P50', round(res['ratioP50'], 2), res['nPaced'])
        put('delayOverBacklogPercent P95', round(res['ratioP95'], 2), res['nPaced'])
        put('appliedDelayMs P50', round(res['delayP50'], 1), res['nPaced'])
        put('appliedDelayMs P95', round(res['delayP95'], 1), res['nPaced'])
        put('burstDelaySharePercent P50', round(res['shareP50'], 2), res['nBursts'])
        put('burstDelaySharePercent P95', round(res['shareP95'], 2), res['nBursts'])
        put('burstsNeverPaced', res['neverPaced'], res['nBursts'])

    for name, cases in (('safeButPaced', safe), ('overrunButUnpaced', overrun)):
        s = boundary_stats(cases)
        for metric, value, den in (
                ('cases', s['n'], ''),
                ('targetDemoted', s['demoted'], s['n']),
                ('aheadTasksDemoted', s['aheadDemoted'], s['aheadTasks']),
                ('backlogOverEstimated', s['backlogOver'], s['n']),
                ('backlogUnderEstimated', s['backlogUnder'], s['n']),
                ('medianBacklogErrorBudgetPoints', round(s['backlogErrorP50Pct'], 2), s['n']),
                ('medianAdmittedReserveErrorMs', round(s['reserveErrorP50Ms'], 1), s['n']),
                ('medianAheadReserveErrorMs', round(s['aheadReserveErrorP50Ms'], 1), s['n']),
                ('medianDecisionToDraftStartMs', round(s['waitP50Ms'], 1), s['n']),
                ('headroomRose', s['headroomRose'], s['headroomN']),
                ('medianHeadroomDelta', round(s['headroomDeltaP50'], 6), s['headroomN']),
                ('thermalStatusRose', s['statusRose'], s['n']),
                ('overheatLevelRose', s['overheatRose'], s['n']),
                (f'within{BOUNDARY_NEAR_PCT:.0f}BudgetPointsOfBoundary', s['nearBoundary'], s['n']),
                ('medianRetrospectivePressurePct', round(s['riskP50Pct'], 2), s['n'])):
            rows.append(['pooled', f'{name} {metric}', value, den])

    write('summary.csv', ['condition', 'metric', 'value', 'denominator'], rows)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    source = (args or ['sampling'])[0]
    results = {c: analyse(c, SOURCES[source][c]) for c in CONDITIONS}
    for res in results.values():
        report(res)
    safe = [t for res in results.values() for t in res['safeButPaced']]
    overrun = [t for res in results.values() for t in res['overrunButUnpaced']]
    report_boundary('safe but paced', safe)
    report_boundary('overrun but unpaced', overrun)
    if '--no-write' not in sys.argv[1:]:
        os.makedirs(OUT, exist_ok=True)
        write_all(results, safe, overrun)
        write_summary(results, safe, overrun)
        print('-' * 78)
        print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
