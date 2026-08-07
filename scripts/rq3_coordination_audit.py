"""Audit admission action and mandatory-floor misses for compact RQ3.

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
            "wait_ms": None if decision is None or draft_start is None else float(draft_start) - float(decision),
            "headroom_delta": headroom_delta,
            "floor_gap_ms": max(0.0, item["d_mand"] - item["d"]),
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
        ]

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


if __name__ == "__main__":
    main()
