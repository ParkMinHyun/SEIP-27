"""Audit admission action and mandatory-floor misses for the RQ3 summary.

The audit joins the envelope partition to factual planned/executed optional-work
classes. Target-or-next means that admission demoted either the post-decision
Draft or the next capture's Draft released by the delay, matching the deployed
two-Draft horizon; it is not causal attribution to the current delay.

The script also reconstructs backlog-estimation error, queue residence, and
thermal-headroom change for the floor audit. Timeout-measurement-error records
are invalid observations, and no valid analyzed run timed out. The mandatory
floor is a sufficient retrospective reservation condition, not the timeout
boundary. See docs/rq3-current.md.
"""

from __future__ import annotations

import csv
from pathlib import Path

import rq3_coordination_metrics as coord


OUT = coord.OUT
SEQUENCE_CLASS = ("Encoding only", "Filter only", "Bokeh+Filter")


def rank(key):
    text = "" if key is None else str(key)
    return 2 if "BOKEH" in text else 1 if "FILTER" in text else 0


def percentile(values, q):
    return coord.percentile([v for v in values if v is not None], q)


def write_csv(path: Path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def enrich(condition, files):
    transitions = coord.load(condition, files)
    shots, replay = {}, {}
    for part, path in enumerate(files, start=1):
        for row in coord.read_sheet(path, "RQ3Pacing"):
            if row.get("runId") is None or row.get("runShotIndex") is None:
                continue
            key = (f"{part}#{int(row['runId'])}", int(row["runShotIndex"]))
            shots[key] = row
        for row in coord.read_sheet(path, "PacingReplay"):
            replay[(part, row["captureIndex"])] = row

    by_run = {}
    for (run, _), row in shots.items():
        by_run.setdefault(run, []).append(row)
    for run in by_run:
        by_run[run].sort(key=lambda row: row["runShotIndex"])

    output = []
    for transition in transitions:
        item = dict(transition)
        key = (item["run"], item["shot"])
        row = shots[key]
        part = int(item["run"].split("#", 1)[0])
        pr = replay[(part, row["captureIndex"])]
        planned, executed = rank(row.get("plannedWorkloadSequenceKey")), rank(row.get("executedWorkloadSequenceKey"))
        # The next capture is the second slot of the deployed 2C horizon.
        # Counting it audits observed coordination; it does not say the current
        # pacing delay caused the next admission decision.
        next_row = shots.get((item["run"], item["shot"] + 1))
        next_demoted = False
        if next_row is not None:
            next_demoted = rank(next_row.get("executedWorkloadSequenceKey")) < rank(next_row.get("plannedWorkloadSequenceKey"))

        decision = row.get("decisionUptimeMs")
        draft_start = row.get("draftStartUptimeMs")
        proxy = None
        if decision is not None:
            for candidate in by_run[item["run"]]:
                start = candidate.get("draftStartUptimeMs")
                if start is None or start > decision:
                    continue
                if proxy is None or start > proxy.get("draftStartUptimeMs"):
                    proxy = candidate
        headroom = row.get("shotThermalHeadroom")
        proxy_headroom = None if proxy is None else proxy.get("shotThermalHeadroom")
        headroom_delta = None if headroom is None or proxy_headroom is None else float(headroom) - float(proxy_headroom)

        target_demoted = executed < planned
        next_margin = None if next_row is None else next_row.get("timeoutMarginMs")

        # ------------------------------------------------------------------
        # Where the realized deadline margin came from.
        # ------------------------------------------------------------------
        # Substituting the floor's own definition, 2*d_mand = B + 2*C_mand - T,
        # into margin = (deadline - decision) - wait - C_exec gives an identity
        # in three separately measured terms:
        #
        #   margin = deadline_ref + horizon_reserve + backlog_residual
        #            - 2*d_mand
        #
        # It is exact arithmetic on the realized trace, NOT a counterfactual: it
        # accounts for the margin that was observed and says nothing about what
        # a different delay would have produced.  main() asserts it closes.
        #
        #   deadline_ref      the controller prices the remaining window from
        #                     the queue's binding deadline -- backlogDeadlineMs,
        #                     "the deadline of whatever entered the backlog
        #                     last, which is the one the whole queue has to fit
        #                     inside" (CaptureAvailablePacingSession.kt, and
        #                     timeToDeadlineMsAt); this is the budget between
        #                     that deadline and the capture's own timeout
        #                     timestamp, which the floor never counted
        #   horizon_reserve   2*C_mand - C_exec: the 2C horizon reserves a
        #                     second Draft for the next capture, while this
        #                     capture's own deadline has to cover only its own
        #   backlog_residual  B - wait: how well the measured backlog predicted
        #                     the wait this capture actually served
        wait = None if decision is None or draft_start is None else float(draft_start) - float(decision)
        deadline = pr.get("timeoutDeadlineUptimeMs")
        deadline_ref = (None if deadline is None or decision is None
                        else (float(deadline) - float(decision)) - item["time_left_ms"])
        horizon_reserve = 2 * item["c_mand_ms"] - item["c_exec_ms"]
        backlog_residual = None if wait is None else item["backlog_ms"] - wait
        # Unmet: the floor's demand that was not applied, in budget rather than
        # in delay, because one millisecond of delay both drains the backlog and
        # moves the next deadline.  Uncounted: the same budget the floor never
        # charged for.  Their difference is the margin, so on the figure the
        # diagonal is the deadline itself.
        unmet = 2 * (item["d_mand"] - item["d"])
        uncounted = (None if deadline_ref is None or backlog_residual is None
                     else deadline_ref + horizon_reserve + backlog_residual - 2 * item["d"])
        item.update({
            "capture_index": int(row["captureIndex"]),
            "planned_class": SEQUENCE_CLASS[planned],
            "executed_class": SEQUENCE_CLASS[executed],
            "target_demoted": target_demoted,
            "next_demoted": next_demoted,
            "target_or_next_demoted": target_demoted or next_demoted,
            "next_margin_ms": next_margin,
            "capture_timed_out": coord.truthy(row.get("captureTimedOut")),
            "watchdog_failed": coord.truthy(row.get("captureWatchdogFailed")),
            "backlog_ms": float(row["realBacklogMs"]),
            "estimated_backlog_ms": float(pr["beforeBacklogMs"]),
            "backlog_error_ms": float(pr["beforeBacklogMs"]) - float(row["realBacklogMs"]),
            "wait_ms": wait,
            "headroom_delta": headroom_delta,
            "floor_gap_ms": max(0.0, item["d_mand"] - item["d"]),
            "deadline_ref_ms": deadline_ref,
            "horizon_reserve_ms": horizon_reserve,
            "backlog_residual_ms": backlog_residual,
            "unmet_floor_ms": unmet,
            "uncounted_budget_ms": uncounted,
        })
        output.append(item)
    return output


def metric(rows, name, value, denominator):
    return [rows[0]["condition"] if rows else "", name, value, denominator]


def main():
    all_rows = {condition: enrich(condition, files) for condition, files in coord.CONDITIONS.items()}
    summary = []
    flexible_detail, floor_detail = [], []
    detail_header = [
        "condition", "run", "shot", "captureIndex", "category", "plannedClass", "executedClass",
        "targetDemoted", "nextDemoted", "targetOrNextDemoted", "appliedDelayMs", "realizedEnvelopeMs",
        "mandatoryFloorMs", "floorGapMs", "potentialAvoidedMs", "marginMs", "nextMarginMs",
        "backlogMs", "estimatedBacklogMs", "backlogErrorMs", "waitMs", "headroomDelta",
        "captureTimedOut", "watchdogFailed",
        "deadlineRefMs", "horizonReserveMs", "backlogResidualMs",
        "unmetFloorMs", "uncountedBudgetMs",
    ]

    def detail(row):
        return [
            row["condition"], row["run"], row["shot"], row["capture_index"], row["category"],
            row["planned_class"], row["executed_class"], row["target_demoted"], row["next_demoted"],
            row["target_or_next_demoted"], round(row["d"]), round(row["d_exec"]), round(row["d_mand"]),
            round(row["floor_gap_ms"]), round(row["potential_avoided_ms"]), row["margin_ms"],
            row["next_margin_ms"], round(row["backlog_ms"]), round(row["estimated_backlog_ms"]),
            round(row["backlog_error_ms"]), "" if row["wait_ms"] is None else round(row["wait_ms"]),
            "" if row["headroom_delta"] is None else round(row["headroom_delta"], 4),
            row["capture_timed_out"], row["watchdog_failed"],
            "" if row["deadline_ref_ms"] is None else round(row["deadline_ref_ms"]),
            round(row["horizon_reserve_ms"]),
            "" if row["backlog_residual_ms"] is None else round(row["backlog_residual_ms"]),
            round(row["unmet_floor_ms"]),
            "" if row["uncounted_budget_ms"] is None else round(row["uncounted_budget_ms"]),
        ]

    def check_identity(rows):
        """margin = uncountedBudget - unmetFloor, exactly.

        The two ceilings in the floor formulas cost at most 1 ms each, so a
        residual above 2 ms means a term stopped meaning what it is named after
        -- most likely a changed deadline or wait field in the export.
        """
        worst = 0.0
        for row in rows:
            if row["uncounted_budget_ms"] is None or row["margin_ms"] is None:
                continue
            if row["time_left_ms"] <= 0 or row["d_mand"] <= 0:
                continue  # the max(0,.) clip breaks the substitution
            residual = float(row["margin_ms"]) - (row["uncounted_budget_ms"] - row["unmet_floor_ms"])
            worst = max(worst, abs(residual))
            if abs(residual) > 2.0:
                raise AssertionError(
                    f"margin decomposition does not close: {row['condition']} "
                    f"{row['run']} shot {row['shot']} residual {residual:.1f} ms")
        return worst

    worst_residual = max(check_identity(rows) for rows in all_rows.values())
    print(f"margin decomposition closes to {worst_residual:.1f} ms (two ceilings)")

    for condition, transitions in all_rows.items():
        flexible = [row for row in transitions if row["category"] == "admission_flexible"]
        floor = [row for row in transitions if row["category"] == "below_mandatory"]
        flexible_detail.extend(detail(row) for row in flexible)
        floor_detail.extend(detail(row) for row in floor)

        actual_target = sum(row["target_demoted"] for row in flexible)
        actual_next = sum(row["next_demoted"] for row in flexible)
        actual_either = sum(row["target_or_next_demoted"] for row in flexible)
        summary.extend([
            [condition, "flexibleTransitions", len(flexible), len(flexible)],
            [condition, "flexibleTargetDemoted", actual_target, len(flexible)],
            [condition, "flexibleNextDemoted", actual_next, len(flexible)],
            [condition, "flexibleTargetOrNextDemoted", actual_either, len(flexible)],
            [condition, "flexibleMarginMsP5", round(percentile([r["margin_ms"] for r in flexible], .05), 1), len(flexible)],
            [condition, "flexibleMarginMsMin", round(min(r["margin_ms"] for r in flexible), 1), len(flexible)],
        ])

        if floor:
            summary.extend([
                [condition, "floorMissTransitions", len(floor), len(floor)],
                [condition, "floorMissDistinctBursts", len({r["run"] for r in floor}), len(floor)],
                [condition, "floorMissDelayZero", sum(r["d"] == 0 for r in floor), len(floor)],
                [condition, "floorMissTargetDemoted", sum(r["target_demoted"] for r in floor), len(floor)],
                [condition, "floorMissTargetOrNextDemoted", sum(r["target_or_next_demoted"] for r in floor), len(floor)],
                [condition, "floorMissBacklogUnderestimated", sum(r["backlog_error_ms"] < 0 for r in floor), len(floor)],
                [condition, "floorMissHeadroomRose", sum(r["headroom_delta"] is not None and r["headroom_delta"] > 0 for r in floor), sum(r["headroom_delta"] is not None for r in floor)],
                [condition, "floorMissWaitMsP50", round(percentile([r["wait_ms"] for r in floor], .5), 1), len(floor)],
                [condition, "floorMissGapMsP50", round(percentile([r["floor_gap_ms"] for r in floor], .5), 1), len(floor)],
                [condition, "floorMissGapMsMax", round(max(r["floor_gap_ms"] for r in floor), 1), len(floor)],
                [condition, "floorMissMarginMsMin", round(min(r["margin_ms"] for r in floor), 1), len(floor)],
                [condition, "floorMissMarginMsP5", round(percentile([r["margin_ms"] for r in floor], .05), 1), len(floor)],
                [condition, "floorMissNextMarginMsMin", round(min(r["next_margin_ms"] for r in floor if r["next_margin_ms"] is not None), 1), len(floor)],
                [condition, "floorMissActualTimeouts", sum(r["capture_timed_out"] for r in floor), len(floor)],
                [condition, "floorMissWatchdogs", sum(r["watchdog_failed"] for r in floor), len(floor)],
                # Where the retained margin came from; see enrich().
                [condition, "floorMissDeadlineRefMsP50", round(percentile([r["deadline_ref_ms"] for r in floor], .5), 1), len(floor)],
                [condition, "floorMissDeadlineRefMsMax", round(max(r["deadline_ref_ms"] for r in floor), 1), len(floor)],
                [condition, "floorMissHorizonReserveMsP50", round(percentile([r["horizon_reserve_ms"] for r in floor], .5), 1), len(floor)],
                [condition, "floorMissBacklogResidualMsMin", round(min(r["backlog_residual_ms"] for r in floor), 1), len(floor)],
                [condition, "floorMissBacklogResidualMsMax", round(max(r["backlog_residual_ms"] for r in floor), 1), len(floor)],
                [condition, "floorMissUnmetFloorMsMax", round(max(r["unmet_floor_ms"] for r in floor), 1), len(floor)],
                [condition, "floorMissUncountedBudgetMsMin", round(min(r["uncounted_budget_ms"] for r in floor), 1), len(floor)],
            ])

        print(f"{coord.LABEL[condition]} flexible n={len(flexible)}: target demoted {actual_target}, "
              f"next demoted {actual_next}, either {actual_either}, margin min/P5 "
              f"{min(r['margin_ms'] for r in flexible):.0f}/{percentile([r['margin_ms'] for r in flexible], .05):.0f} ms")
        if floor:
            print(f"  floor misses n={len(floor)} across {len({r['run'] for r in floor})} bursts: "
                  f"backlog underestimated {sum(r['backlog_error_ms'] < 0 for r in floor)}, "
                  f"headroom rose {sum(r['headroom_delta'] is not None and r['headroom_delta'] > 0 for r in floor)}, "
                  f"margin min/P5 {min(r['margin_ms'] for r in floor):.0f}/"
                  f"{percentile([r['margin_ms'] for r in floor], .05):.0f} ms")

    write_csv(OUT / "action_summary.csv", ["condition", "metric", "value", "denominator"], summary)
    write_csv(OUT / "flexible_cases.csv", detail_header, flexible_detail)
    write_csv(OUT / "mandatory_floor_cases.csv", detail_header, floor_detail)

    # Plot-ready view of the floor misses, split by what admission left running
    # so the figure can give each class its own mark without filtering on a
    # string column.  The burst id also loses its "#", which pgfplots' table
    # reader treats as a TeX parameter character and refuses to read.
    run_col = detail_header.index("run")
    shot_col = detail_header.index("shot")
    gap_col = detail_header.index("floorGapMs")
    margin_col = detail_header.index("marginMs")
    next_col = detail_header.index("nextMarginMs")
    exec_col = detail_header.index("executedClass")
    # Shares of the Capture Timeout budget, not milliseconds: the budget is an
    # internal constant that must not be recoverable from a rendered axis, so the
    # figure plots the share and never the absolute value.  The ms columns stay
    # for the audit trail.
    budgets = {row["budget_ms"] for rows in all_rows.values() for row in rows}
    assert len(budgets) == 1, f"captureTimeoutMs is not constant: {budgets}"
    budget = budgets.pop()
    share = lambda value: round(100 * float(value) / budget, 3)

    # unmet_floor and uncounted_budget are the figure's two axes.  Their
    # difference is the realized margin by the identity checked above, so the
    # panel's diagonal is the deadline itself and the vertical distance to it is
    # the margin -- which the earlier margin-against-shortfall pair could not
    # show, because that diagonal marked nothing physical.
    unmet_col = detail_header.index("unmetFloorMs")
    uncounted_col = detail_header.index("uncountedBudgetMs")
    plot_header = ["burst", "shot", "shortfall_ms", "margin_ms", "next_margin_ms",
                   "shortfall_pct", "margin_pct", "next_margin_pct",
                   "unmet_floor_ms", "uncounted_budget_ms",
                   "unmet_floor_pct", "uncounted_budget_pct"]

    def plot_rows(executed):
        return [[str(row[run_col]).replace("#", "-"), row[shot_col],
                 row[gap_col], row[margin_col], row[next_col],
                 share(row[gap_col]), share(row[margin_col]), share(row[next_col]),
                 row[unmet_col], row[uncounted_col],
                 share(row[unmet_col]), share(row[uncounted_col])]
                for row in floor_detail if row[exec_col] == executed]

    for executed, name in (("Filter only", "filter"), ("Encoding only", "encoding")):
        write_csv(OUT / f"floor_miss_{name}.csv", plot_header, plot_rows(executed))


if __name__ == "__main__":
    main()
