"""What each pacing decision required, what it got, and where the difference came from.

The compact RQ3 pair reports four outcome classes -- decisions that required no
delay, decisions whose required delay pacing covered, decisions that left part of
it to admission, and decisions that fell below the mandatory floor -- and the
previous revision could show that the last two under-estimated backlog without
showing what produced the under-estimate.  This generator supplies that
mechanism, and emits every cell of the outcome matrix so the table and the figure
are driven by one population.

The controller prices two quantities with two different conventions, and the
difference between the applied and the required delay is exactly their two
errors.  Away from the max(0, .) clip -- on decisions carrying both a positive
applied delay and a positive required delay --

    d - d*  =  (Chat - C)  +  (Bhat - B) / 2                              (1)

holds identically; the assertion below checks it and it closes to 0.8 ms, which
is the two ceilings in the formulas.

Chat is CaptureAvailablePacingSession.getMaxDraftSequenceDurationMs, the
session's observed MAXIMUM Draft duration for the capture's size bucket,
re-projected onto the admitted sequence.  A maximum priced against a typical
realized duration over-covers, and the reserve enters the formula twice, so the
reserve error is the term that makes pacing conservative.

Bhat is the backlog clock, which CaptureAvailablePacingSession.queuePacingDecision
advances by each queued Draft's POINT prediction plus one learned between-node
overhead.  A point estimate priced against a real pipeline occupancy is right in
the middle of the distribution and short in its tail, and unlike the reserve it
is summed over the queue, so its tail accumulates.  The per-Draft form of that
error is

    Draft pricing error = (beforeWorkloadSequencePredictedDurationMs
                           + beforeDraftSequenceOverheadDurationMs)
                          - draftSequenceDurationMs                       (2)

i.e. what the backlog clock charged for the Draft minus what the Draft's real
pipeline occupancy turned out to be, signed like every other error here so that
positive means conservative.  Summing (2) over the Drafts queued ahead of a
decision reproduces that decision's backlog estimate error to Pearson r = 0.95
and 0.88, which is what makes the under-estimate a mechanism rather than an
association.

Nothing here is a counterfactual.  (1) is an identity, (2) is a difference of two
recorded numbers, and the correlation is measured over the analyzed decisions.
In particular the queued pricing error does NOT say what the delay would have
been under a different clock: pacing is closed-loop, so a different delay changes
later arrivals, backlog, admission, thermal state and realized Draft duration.
The one repricing this script does emit -- floorMissRepricedAtOrAboveFloor -- is
labelled and bounded in the same way: it substitutes the measured backlog into
the deployed formula on the recorded row, which says what the controller would
have priced with an exact clock at that instant, not what the run would have
done.  See docs/rq3-current.md.

Run from the repository root:

    python3 scripts/rq3_estimator_metrics.py
"""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import rq3_coordination_metrics as coord


ROOT = coord.ROOT
OUT = ROOT / "data/rq3/estimator"
LABEL = coord.LABEL

# Row slot of each condition in the figure, matching envelope_share.csv.
SLOT = {"12mp_normal": 1, "24mp_memory": 0}

# The four outcome classes partition every analyzed pacing decision: the first is
# the complement of the required set and the other three partition that set, so
# the four counts add to the analyzed total and the last three add to the
# required total.  The table prints them in this order and relies on both sums.
CLASSES = ("no_delay_required", "covered", "flexible", "below_floor")


def rank(key):
    """Optional-work rank of a workload sequence.

    Bokeh is the multi-frame stage admission drops first and Filter the
    single-frame stage it drops next; the encoding pass is mandatory, so an
    encoding-only sequence is the floor.
    """
    text = "" if key is None else str(key)
    return 2 if "BOKEH" in text else 1 if "FILTER" in text else 0


def pct(values, q):
    return coord.percentile([v for v in values if v is not None], q)


def rel_pct(sel, error_key, base_key):
    """Median relative estimator error, in per cent of the realized quantity.

    The table prints the two decision-time errors normalised: the Draft reserve
    against the realized Draft duration it was reserving for, and the backlog
    clock against the backlog it was measuring.  Each ratio is formed PER
    DECISION and only then taken at P50, because the median of a ratio is not the
    ratio of the medians -- these values therefore cannot be derived from the two
    millisecond columns beside them, and both are emitted.

    A decision whose denominator is zero is dropped.  That is 1 and 4 of the
    analyzed decisions for the backlog and none at all for the Draft duration,
    and none of them was paced, so every population the table prints keeps all of
    its members.
    """
    vals = [100.0 * r[error_key] / r[base_key] for r in sel if r[base_key]]
    return round(pct(vals, .5), 1) if vals else ""


def load(condition, files):
    """Every shot of every eligible run, with the pricing terms joined on.

    Run and decision eligibility follow scripts/rq3_coordination_metrics.py, but
    the filter is recorded per row instead of applied while reading: the queue
    reconstruction needs Drafts that are not analyzable decisions themselves,
    because a Draft queued ahead of a decision occupies the pipeline whether or
    not its own row carries a pacing decision.
    """
    rows = []
    for part, path in enumerate(files, start=1):
        pacing = coord.read_sheet(path, "RQ3Pacing")
        replay = {r["captureIndex"]: r for r in coord.read_sheet(path, "PacingReplay")}
        dyn = {r["captureIndex"]: r["durationMs"]
               for r in coord.read_sheet(path, "DynamicFunctionNode")}
        enc = {r["captureIndex"]: r["durationMs"]
               for r in coord.read_sheet(path, "SecImageCodecNode")
               if str(r.get("workloadKey", "")).startswith("ENCODING")}
        by_run = {}
        for row in pacing:
            by_run.setdefault(row["runId"], []).append(row)
        for summary in coord.read_sheet(path, "RQ3Summary"):
            shots = sorted(by_run.get(summary["runId"], []),
                           key=lambda r: r["runShotIndex"])
            level = int(summary["startingOverheatLevel"])
            if not coord.truthy(summary["isComplete30ShotRun"]):
                continue
            # Known timeout-measurement errors are invalid observations, not
            # actual Capture Timeout outcomes.
            if any(coord.truthy(r.get("captureTimedOut")) for r in shots):
                continue
            if condition == "24mp_memory" and level <= 4:
                head = [r.get("sizeBucket") for r in shots if r["runShotIndex"] in (1, 2)]
                if head and all(size == "MP12" for size in head):
                    continue
            for row in shots:
                pr = replay.get(row["captureIndex"]) or {}
                item = {
                    "condition": condition,
                    "run": f"{part}#{int(summary['runId'])}",
                    "shot": int(row["runShotIndex"]),
                    "capture_index": int(row["captureIndex"]),
                    "level": level,
                    "draft_start": pr.get("draftStartUptimeMs"),
                    "draft_end": pr.get("draftEndUptimeMs"),
                    "decision": row.get("decisionUptimeMs"),
                    "queue_depth": row.get("realQueueDepth"),
                    "wait_ms": pr.get("realQueueWaitMs"),
                    "wall_lag_ms": pr.get("freshestWallLagErrorMs"),
                    "in_flight": pr.get("inFlightDraftCountAtDecision"),
                    "margin_ms": row.get("timeoutMarginMs"),
                    "planned_rank": rank(row.get("plannedWorkloadSequenceKey")),
                    "executed_rank": rank(row.get("executedWorkloadSequenceKey")),
                    "analyzable": (2 <= row["runShotIndex"] <= 30
                                   and coord.truthy(row.get("pacingDecisionRecorded"))
                                   and coord.truthy(row.get("realTraceCompleteBeforeDelay"))
                                   and not coord.truthy(row.get("captureWatchdogFailed"))),
                }

                # (2), signed so that positive means the clock charged more than
                # the Draft occupied.
                wall = pr.get("draftSequenceDurationMs")
                point = pr.get("beforeWorkloadSequencePredictedDurationMs")
                overhead = pr.get("beforeDraftSequenceOverheadDurationMs")
                item["priced_ms"] = (None if None in (point, overhead)
                                     else float(point) + float(overhead))
                item["pricing_error_ms"] = (None if wall is None or item["priced_ms"] is None
                                            else item["priced_ms"] - float(wall))

                keys = ("beforeAppliedDelayMs", "beforeTimeToDeadlineMs",
                        "workloadSequenceDurationMs", "beforeBacklogMs",
                        "beforeDraftSequenceReservedDurationMs", "captureTimeoutMs")
                complete = (wall is not None and row.get("realBacklogMs") is not None
                            and all(pr.get(k) is not None for k in keys))
                if complete:
                    backlog = float(row["realBacklogMs"])
                    duration = float(wall)
                    time_left = max(0.0, float(pr["beforeTimeToDeadlineMs"]))
                    node_ms = float(pr["workloadSequenceDurationMs"])
                    item.update({
                        "d": float(pr["beforeAppliedDelayMs"]),
                        "backlog_ms": backlog,
                        "duration_ms": duration,
                        "time_left_ms": time_left,
                        "budget_ms": float(pr["captureTimeoutMs"]),
                        "estimated_backlog_ms": float(pr["beforeBacklogMs"]),
                        "reserved_ms": float(pr["beforeDraftSequenceReservedDurationMs"]),
                        "backlog_error_ms": float(pr["beforeBacklogMs"]) - backlog,
                        "reserve_error_ms":
                            float(pr["beforeDraftSequenceReservedDurationMs"]) - duration,
                        "required_ms": math.ceil(
                            max(0.0, backlog + 2 * duration - time_left) / 2),
                    })
                    dyn_ms, enc_ms = dyn.get(row["captureIndex"]), enc.get(row["captureIndex"])
                    if dyn_ms is not None and enc_ms is not None:
                        mandatory = float(dyn_ms) + float(enc_ms) + (duration - node_ms)
                        item["mandatory_duration_ms"] = mandatory
                        item["mandatory_ms"] = math.ceil(
                            max(0.0, backlog + 2 * mandatory - time_left) / 2)
                    else:
                        item["mandatory_duration_ms"] = None
                        item["mandatory_ms"] = None
                else:
                    for key in ("d", "backlog_ms", "duration_ms", "time_left_ms",
                                "budget_ms", "estimated_backlog_ms", "reserved_ms",
                                "backlog_error_ms", "reserve_error_ms", "required_ms",
                                "mandatory_duration_ms", "mandatory_ms"):
                        item[key] = None
                rows.append(item)
    return rows


def attach_queue(rows):
    """Per decision: the admission action over the 2C horizon, and the pricing
    error of the Drafts occupying the pipeline ahead of it.

    A Draft is ahead of a decision when it had not finished at the decision
    timestamp and started before the target's own Draft -- the set the backlog
    clock was carrying.  The sum is left blank when any member is missing a
    pricing term, so a partial queue never masquerades as a small error.
    """
    by_run = {}
    for row in rows:
        by_run.setdefault((row["condition"], row["run"]), []).append(row)
    for group in by_run.values():
        group.sort(key=lambda r: r["capture_index"])
        by_shot = {r["shot"]: r for r in group}
        for target in group:
            # The 2C horizon reserves for two Drafts: the one that begins after
            # this decision and the next capture's, released by the delay.
            # Counting the second audits observed coordination over that horizon;
            # it does not attribute the next admission decision to this delay.
            target["skipped_this"] = target["executed_rank"] < target["planned_rank"]
            following = by_shot.get(target["shot"] + 1)
            target["skipped_next"] = (following is not None
                                      and following["executed_rank"] < following["planned_rank"])
            target["skipped_either"] = target["skipped_this"] or target["skipped_next"]

            ahead = [o for o in group
                     if o is not target
                     and None not in (o["draft_end"], target["decision"],
                                      o["draft_start"], target["draft_start"])
                     and o["draft_end"] > target["decision"]
                     and o["draft_start"] < target["draft_start"]]
            target["queued_drafts"] = len(ahead)
            errors = [o["pricing_error_ms"] for o in ahead
                      if o["pricing_error_ms"] is not None]
            target["queued_pricing_error_ms"] = (sum(errors)
                                                 if len(errors) == len(ahead) else None)


def classify(row):
    if row["required_ms"] is None:
        return None
    if row["required_ms"] <= 0:
        return "no_delay_required"
    if row["mandatory_ms"] is None:
        return None
    if row["d"] < row["mandatory_ms"]:
        return "below_floor"
    if row["d"] < row["required_ms"]:
        return "flexible"
    return "covered"


def pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return cov / (sx * sy)


def ecdf(values, cap=360):
    """Thinned ECDF: at most `cap` points, both endpoints always kept."""
    values = sorted(float(v) for v in values)
    n = len(values)
    if n == 0:
        return []
    step = max(1, n // cap)
    keep = list(range(0, n, step))
    if keep[-1] != n - 1:
        keep.append(n - 1)
    return [(values[i], 100.0 * (i + 1) / n) for i in keep]


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def analyse(condition, files):
    rows = load(condition, files)
    attach_queue(rows)
    analyzed = [r for r in rows if r["analyzable"] and r["required_ms"] is not None]
    for row in analyzed:
        row["class"] = classify(row)
    unclassified = [r for r in analyzed if r["class"] is None]
    assert not unclassified, f"{condition}: {len(unclassified)} decisions without a class"

    exact = [r for r in analyzed if r["d"] > 0 and r["required_ms"] > 0]
    identity = [(r["d"] - r["required_ms"])
                - (r["reserve_error_ms"] + r["backlog_error_ms"] / 2) for r in exact]
    assert max(abs(v) for v in identity) <= 1.0, f"{condition}: identity (1) does not close"

    return dict(rows=rows, analyzed=analyzed, exact=exact, identity=identity,
                paced=[r for r in analyzed if r["d"] > 0],
                required=[r for r in analyzed if r["required_ms"] > 0],
                priced=[r for r in rows if r["pricing_error_ms"] is not None],
                joined=[r for r in analyzed
                        if r["queued_pricing_error_ms"] is not None and r["queued_drafts"] > 0],
                budget=statistics.median(r["budget_ms"] for r in analyzed))


def class_row(condition, name, sel, budget):
    """One printed row of the outcome matrix.

    Every column is defined on every class, so the matrix carries no placeholder
    cells: where a quantity is structurally zero -- a missing delay on decisions
    that required none -- the row prints that zero.
    """
    if not sel:
        return [condition, name, 0] + [""] * 16
    queued = [r["queued_pricing_error_ms"] for r in sel
              if r["queued_pricing_error_ms"] is not None]
    paced = [r for r in sel if r["d"] > 0]
    missing = [max(0.0, r["required_ms"] - r["d"]) for r in sel]
    margins = [100.0 * r["margin_ms"] / budget for r in sel if r["margin_ms"] is not None]
    return [
        condition, name, len(sel), len(paced),
        round(100 * len(paced) / len(sel), 1),
        round(pct([r["d"] for r in paced], .5), 1) if paced else "",
        round(pct(missing, .5), 1), round(max(missing), 1),
        round(100 * sum(r["skipped_this"] for r in sel) / len(sel), 1),
        round(100 * sum(r["skipped_either"] for r in sel) / len(sel), 1),
        # Minimum and P5 together: the minimum alone reads as a near-miss with
        # no sense of how isolated it is, and P5 alone hides the tail.
        round(min(margins), 2) if margins else "",
        round(pct(margins, .05), 2) if margins else "",
        sum(v < 1.0 for v in margins),
        round(pct([r["reserve_error_ms"] for r in sel], .5), 1),
        round(pct([r["backlog_error_ms"] for r in sel], .5), 1),
        # The table prints these two, not the millisecond pair above them.
        rel_pct(sel, "reserve_error_ms", "duration_ms"),
        rel_pct(sel, "backlog_error_ms", "backlog_ms"),
        round(pct(queued, .5), 1) if queued else "",
        sum(r["backlog_error_ms"] < 0 for r in sel),
    ]


def main():
    summary, class_rows, scatter_rows, zero_delay_rows = [], [], [], []
    sizing_rows, thin_rows = [], []
    report = {}

    for condition, files in coord.CONDITIONS.items():
        data = analyse(condition, files)
        report[condition] = data
        analyzed, paced = data["analyzed"], data["paced"]
        required, priced, joined = data["required"], data["priced"], data["joined"]
        budget = data["budget"]

        def put(metric, value, denominator=""):
            summary.append([condition, metric, value, denominator])

        put("analyzedDecisions", len(analyzed))
        put("pacedDecisions", len(paced), len(analyzed))
        put("requiredDelayDecisions", len(required), len(analyzed))
        put("requiredAndPaced", sum(r["d"] > 0 for r in required), len(required))
        put("noRequirementDecisions", len(analyzed) - len(required), len(analyzed))
        put("noRequirementAndPaced", len(paced) - sum(r["d"] > 0 for r in required),
            len(analyzed) - len(required))

        # --- the two terms of (1) ---------------------------------------------
        put("identityDecisions", len(data["exact"]), len(analyzed))
        put("identityResidualMsMaxAbs", round(max(abs(v) for v in data["identity"]), 2),
            len(data["exact"]))
        for name, values in (
                ("reserveErrorMs", [r["reserve_error_ms"] for r in analyzed]),
                ("backlogErrorMs", [r["backlog_error_ms"] for r in analyzed])):
            for label, q in (("P05", .05), ("P50", .5), ("P95", .95)):
                put(f"{name}{label}", round(pct(values, q), 1), len(analyzed))

        # --- (2), the per-Draft pricing error ---------------------------------
        errors = [r["pricing_error_ms"] for r in priced]
        for label, q in (("P05", .05), ("P50", .5), ("P95", .95)):
            put(f"draftPricingErrorMs{label}", round(pct(errors, q), 1), len(priced))
        put("draftPricingErrorNegative", sum(v < 0 for v in errors), len(priced))
        put("queuedPricingErrorPearsonR",
            round(pearson([r["queued_pricing_error_ms"] for r in joined],
                          [r["backlog_error_ms"] for r in joined]), 3), len(joined))
        put("backlogUnderEstimated", sum(r["backlog_error_ms"] < 0 for r in analyzed),
            len(analyzed))

        # --- why an observed-Draft-wall clock is not the free fix --------------
        put("inFlightAtDecision", sum((r["in_flight"] or 0) > 0 for r in analyzed),
            len(analyzed))
        for label, q in (("P50", .5), ("P95", .95)):
            put(f"freshestWallLagMs{label}",
                round(pct([r["wall_lag_ms"] for r in analyzed], q), 1), len(analyzed))

        # --- what was applied against what was required -------------------------
        # The outcome matrix says whether the delay was ENOUGH; it cannot say
        # whether it was more than enough, because it prints no applied delay.
        # These two populations are the ones where pacing acted and a comparison
        # is therefore defined: decisions that required nothing and got a delay
        # anyway, and decisions whose requirement the delay covered.  Each
        # percentile is taken on its own quantity, so the over-applied column is
        # the median of d - d* and NOT the difference of the two medians.
        for name, sel in (
                ("paced_none_required",
                 [r for r in analyzed if r["required_ms"] == 0 and r["d"] > 0]),
                ("covered", [r for r in analyzed if r["class"] == "covered"])):
            if not sel:
                continue
            over = [r["d"] - r["required_ms"] for r in sel]
            # What the conservatism is bounded BY.  d/B prices the delay against
            # the Draft work already outstanding when it was applied, and the
            # absorbed share is sum(min(d, B))/sum(d): the part of the wait that
            # ran while at least that much work was still in the pipeline.  A
            # wait longer than the backlog it drains is idle for the remainder,
            # and `outlast` counts those.  Both are arithmetic on the realized
            # trace and neither says what a different delay would have done.
            ratio = [100 * r["d"] / r["backlog_ms"] for r in sel if r["backlog_ms"] > 0]
            applied = sum(r["d"] for r in sel)
            overlap = sum(min(r["d"], r["backlog_ms"]) for r in sel)
            # WHY THE TWO ERRORS ARE RECOMPUTED HERE INSTEAD OF READ OFF THE
            # OUTCOME MATRIX.  The matrix's error columns are medians over a whole
            # class, which is the right population for its own question -- why a
            # class received less than it required -- because a decision that got
            # no delay still belongs to the class.  It is the wrong population for
            # THIS question.  paced_none_required is 350 of 1,841 and 374 of
            # 1,721, so a class-wide median describes the 81% and 78% that were
            # never paced, and the difference is not a refinement:
            #
            #                       class-wide      this population
            #   reserve error       +230 / +250      +555 / +653 ms
            #   backlog error        -19 /  -43      +445 / +231 ms
            #
            # The backlog error changes SIGN.  Read class-wide, the over-shoot
            # looks like the Draft reserve acting alone against a roughly correct
            # backlog clock; read on the decisions pacing actually acted on, both
            # estimates were conservative at once.  Never quote the matrix's error
            # cells as the explanation of its Paced count.
            sizing_rows.append([
                condition, name, len(sel),
                round(pct([r["required_ms"] for r in sel], .5), 1),
                round(pct([r["d"] for r in sel], .5), 1),
                round(pct(over, .5), 1), round(pct(over, .95), 1),
                round(pct([r["reserve_error_ms"] for r in sel], .5), 1),
                round(pct([r["backlog_error_ms"] for r in sel], .5), 1),
                rel_pct(sel, "reserve_error_ms", "duration_ms"),
                rel_pct(sel, "backlog_error_ms", "backlog_ms"),
                round(pct(ratio, .5), 1), round(pct(ratio, .95), 1),
                round(100 * overlap / applied, 1) if applied else "",
                sum(1 for r in sel if r["d"] > r["backlog_ms"]),
            ])

        # --- the thin deadline-margin tail --------------------------------------
        # The table prints the minimum realized margin, and on the largest class
        # that minimum is 0.11% of the budget.  Printed alone it reads as "no
        # Capture Timeout was luck", so the tail is emitted decision by decision
        # and the note characterises it instead: on all eleven the backlog was
        # already 42-79% of the budget, ten were paced, and every one had pacing
        # or an optional-work skip engaged.  Nothing here says a baseline would
        # have timed out on them; that is an RQ1 question.
        thin = sorted((r for r in analyzed
                       if r["margin_ms"] is not None
                       and 100 * r["margin_ms"] / budget < 1.0),
                      key=lambda r: r["margin_ms"])
        expected = sum(1 for r in analyzed if r["margin_ms"] is not None
                       and 100 * r["margin_ms"] / budget < 1.0)
        assert len(thin) == expected, f"{condition}: thin-tail count is unstable"
        for r in thin:
            thin_rows.append([
                condition, r["run"], r["shot"], r["capture_index"], r["level"],
                r["class"], round(r["margin_ms"], 1),
                round(100 * r["margin_ms"] / budget, 2),
                round(r["d"], 1), round(r["required_ms"], 1),
                round(r["backlog_ms"], 1), round(100 * r["backlog_ms"] / budget, 1),
                round(r["wait_ms"], 1) if r["wait_ms"] is not None else "",
                round(100 * r["wait_ms"] / budget, 1) if r["wait_ms"] is not None else "",
                round(r["duration_ms"], 1),
                "yes" if r["skipped_this"] else "no",
                "yes" if (r["d"] > 0 or r["skipped_this"]) else "no",
            ])
        put("marginUnder1PctDecisions", len(thin), len(analyzed))
        put("marginUnder1PctPaced", sum(1 for r in thin if r["d"] > 0), len(thin))
        put("marginUnder1PctEitherControl",
            sum(1 for r in thin if r["d"] > 0 or r["skipped_this"]), len(thin))

        # --- the outcome matrix ------------------------------------------------
        for name in CLASSES:
            sel = [r for r in analyzed if r["class"] == name]
            class_rows.append(class_row(condition, name, sel, budget))
            for row in sel:
                if row["queued_pricing_error_ms"] is None:
                    continue
                scatter_rows.append([
                    condition, SLOT[condition], name,
                    round(row["queued_pricing_error_ms"] / 1000.0, 4),
                    round(row["backlog_error_ms"] / 1000.0, 4),
                ])

        # --- the floor block ---------------------------------------------------
        floor = [r for r in analyzed if r["class"] == "below_floor"]
        if floor:
            put("floorMissDecisions", len(floor), len(floor))
            put("floorMissRuns", len({r["run"] for r in floor}), len(floor))
            put("floorMissZeroDelay", sum(r["d"] == 0 for r in floor), len(floor))
            put("floorMissWaitMsP50", round(pct([r["wait_ms"] for r in floor], .5), 1),
                len(floor))
            put("floorMissQueuedDraftsP50",
                round(pct([r["queued_drafts"] for r in floor], .5), 1), len(floor))
            # What the deployed formula would have priced on the same recorded
            # row with an exact backlog clock.  A repricing at the decision
            # instant, not a claim about how the run would have gone.
            repriced = [math.ceil(max(0.0, r["backlog_ms"] + 2 * r["reserved_ms"]
                                      - r["time_left_ms"]) / 2) for r in floor]
            put("floorMissRepricedAtOrAboveFloor",
                sum(v >= r["mandatory_ms"] for v, r in zip(repriced, floor)), len(floor))
            put("floorMissRepricedMsP50", round(pct(repriced, .5), 1), len(floor))

            # --- the zero-delay floor misses, row by row -----------------------
            # These are the decisions the controller left unpaced although the
            # mandatory work provably did not fit, so they are the ones a reader
            # asks about first.  The account below is an identity, not an
            # explanation of intent: what the controller priced online,
            #
            #     saw = Bhat + 2*Chat - T,
            #
            # is non-positive on every one of them, which is why the deployed
            # formula returned zero.  The realized mandatory pressure is
            # B + 2*C_mand - T, and the difference between the two is exactly
            #
            #     (B - Bhat)  +  2*(C_mand - Chat),
            #
            # the backlog term and the reserve term.  The assertion checks that
            # the three sum back to the floor the class was cut on; it closes to
            # the ceiling in the floor formula.
            for r in sorted((x for x in floor if x["d"] == 0),
                            key=lambda x: (x["run"], x["shot"])):
                saw = r["estimated_backlog_ms"] + 2 * r["reserved_ms"] - r["time_left_ms"]
                backlog_term = r["backlog_ms"] - r["estimated_backlog_ms"]
                reserve_term = 2 * (r["mandatory_duration_ms"] - r["reserved_ms"])
                account = saw + backlog_term + reserve_term
                assert abs(account - 2 * r["mandatory_ms"]) <= 2.0, (
                    f"{condition} {r['run']}#{r['shot']}: "
                    "zero-delay account does not close")
                repriced_one = math.ceil(max(0.0, r["backlog_ms"] + 2 * r["reserved_ms"]
                                             - r["time_left_ms"]) / 2)
                zero_delay_rows.append([
                    condition, r["run"], r["shot"], r["capture_index"],
                    round(saw), round(backlog_term), round(reserve_term), round(account),
                    r["mandatory_ms"], repriced_one,
                    "yes" if repriced_one >= r["mandatory_ms"] else "no",
                    # Whether correcting the backlog clock alone would have made
                    # the controller see positive pressure at the decision.  The
                    # reserve term is left at its recorded value, so this is a
                    # statement about that instant and not about the run.
                    "yes" if saw + backlog_term > 0 else "no",
                    r["queued_drafts"],
                    "" if r["wait_ms"] is None else round(r["wait_ms"]),
                ])
            put("floorMissZeroDelayBacklogFlipsSign",
                sum(1 for row in zero_delay_rows
                    if row[0] == condition and row[11] == "yes"),
                sum(1 for row in zero_delay_rows if row[0] == condition))

    write_csv(OUT / "summary.csv", ["condition", "metric", "value", "denominator"], summary)
    write_csv(OUT / "outcome_matrix.csv",
              ["condition", "class", "n", "paced", "paced_pct", "applied_delay_p50_ms",
               "missing_delay_p50_ms", "missing_delay_max_ms", "skipped_this_pct",
               "skipped_either_pct", "deadline_margin_min_pct",
               "deadline_margin_p5_pct", "deadline_margin_under_1pct",
               "reserve_error_p50_ms", "backlog_error_p50_ms",
               "reserve_error_p50_pct", "backlog_error_p50_pct",
               "queued_pricing_error_p50_ms", "backlog_under_estimated"],
              class_rows)
    write_csv(OUT / "sizing_summary.csv",
              ["condition", "population", "n", "required_p50_ms",
               "applied_p50_ms", "over_applied_p50_ms", "over_applied_p95_ms",
               "reserve_error_p50_ms", "backlog_error_p50_ms",
               "reserve_error_p50_pct", "backlog_error_p50_pct",
               "delay_over_backlog_p50_pct", "delay_over_backlog_p95_pct",
               "delay_absorbed_by_backlog_pct", "waits_outlasting_backlog"],
              sizing_rows)
    write_csv(OUT / "thin_margin_tail.csv",
              ["condition", "run", "shot", "captureIndex", "level", "class",
               "margin_ms", "margin_pct_of_budget", "applied_delay_ms",
               "required_delay_ms", "backlog_ms", "backlog_pct_of_budget",
               "queue_wait_ms", "queue_wait_pct_of_budget", "draft_duration_ms",
               "optional_work_skipped", "either_control_engaged"],
              thin_rows)
    write_csv(OUT / "floor_zero_delay_account.csv",
              ["condition", "run", "shot", "captureIndex", "controller_saw_ms",
               "backlog_term_ms", "reserve_term_ms", "account_ms",
               "mandatory_floor_ms", "repriced_ms", "repriced_reaches_floor",
               "backlog_flips_sign", "queued_drafts", "queue_wait_ms"],
              zero_delay_rows)
    write_csv(OUT / "queued_pricing_scatter.csv",
              ["condition", "slot", "class", "queued_pricing_error_s", "backlog_error_s"],
              scatter_rows)
    # One file per (condition, class): pgfplots needs a separate \addplot per
    # mark style, and filtering 3,500 rows inside the figure would be slower to
    # compile than reading four short tables.
    for condition in coord.CONDITIONS:
        for name in CLASSES:
            write_csv(OUT / f"scatter_{condition}_{name}.csv",
                      ["queued_pricing_error_s", "backlog_error_s"],
                      [[r[3], r[4]] for r in scatter_rows
                       if r[0] == condition and r[2] == name])
    for condition, data in report.items():
        write_csv(OUT / f"draft_pricing_ecdf_{condition}.csv", ["ms", "cdf_pct"],
                  [[round(v, 1), round(c, 3)]
                   for v, c in ecdf([r["pricing_error_ms"] for r in data["priced"]])])
        write_csv(OUT / f"reserve_error_ecdf_{condition}.csv", ["ms", "cdf_pct"],
                  [[round(v, 1), round(c, 3)]
                   for v, c in ecdf([r["reserve_error_ms"] for r in data["analyzed"]])])

    # Positional, so it must track the column order of class_row exactly; the
    # two percentage columns the table prints sit between the millisecond pair
    # and the queued pricing error.
    header = ("class", "n", "paced", "paced%", "delay", "miss50", "missMax",
              "skip", "skipEither", "margMin", "margP5", "marg<1%", "reserve",
              "backlog", "reserve%", "backlog%", "queued")
    for condition, data in report.items():
        analyzed = data["analyzed"]
        print(f"{LABEL[condition]}: analyzed {len(analyzed)}, paced {len(data['paced'])}, "
              f"required {len(data['required'])}, identity |residual| max "
              f"{max(abs(v) for v in data['identity']):.2f} ms over {len(data['exact'])}")
        print(f"  Draft pricing error P05/P50/P95 "
              f"{pct([r['pricing_error_ms'] for r in data['priced']], .05):+.0f} / "
              f"{pct([r['pricing_error_ms'] for r in data['priced']], .5):+.0f} / "
              f"{pct([r['pricing_error_ms'] for r in data['priced']], .95):+.0f} ms;  "
              f"queued vs backlog r = "
              f"{pearson([r['queued_pricing_error_ms'] for r in data['joined']], [r['backlog_error_ms'] for r in data['joined']]):.3f}")
        print("    " + "".join(f"{h:>12s}" for h in header))
        for name in CLASSES:
            sel = [r for r in analyzed if r["class"] == name]
            row = class_row(condition, name, sel, data["budget"])
            print("    " + f"{name:>12s}" + "".join(f"{str(v):>12s}" for v in row[2:18]))


if __name__ == "__main__":
    main()
