"""Build admission--pacing coordination evidence for the RQ3 summary.

The standard-library XLSX reader evaluates transitions with a positive
retrospective realized-work envelope and partitions them into:

  full_covered       d >= d_exec
  admission_flexible d_mand <= d < d_exec
  below_mandatory    d < d_mand

d_exec uses the realized admitted Draft duration. d_mand replaces skippable
work with DynamicFunction + Encoding and Draft overhead. The 2C term spans the
post-decision Draft and the next capture's Draft released by the delay.

Timeout-labelled records removed here are known invalid measurements, not
actual timeout outcomes; no valid analyzed run timed out. The reconstructed
envelopes are trace diagnostics, not 0.5x/0.75x counterfactual trajectories.
Mechanically scaling recorded delay is invalid because pacing changes later
backlog, admission, thermal state, and realized work. See docs/rq3-current.md.
"""

from __future__ import annotations

import csv
import math
import os
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/rq3/coordination"
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"

CONDITIONS = {
    "12mp_normal": [ROOT / f"data/ablation_sampling/48U_metrics_12MP_normal_0803_{i}.xlsx"
                     for i in (1, 2)],
    "24mp_memory": [ROOT / f"data/ablation_sampling/48U_metrics_24MP_memory_0803_{i}.xlsx"
                     for i in (1, 2)],
}
LABEL = {"12mp_normal": "12MP normal", "24mp_memory": "24MP memory pressure"}


def column_index(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref).group(0)
    value = 0
    for ch in letters:
        value = value * 26 + ord(ch) - 64
    return value - 1


def sheet_targets(zf: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    targets = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall(f"{PKG_REL_NS}Relationship")}
    return {s.attrib["name"]: "xl/" + targets[s.attrib[f"{REL_NS}id"]]
            for s in workbook.find(f"{NS}sheets")}


def cell_value(cell):
    if cell.attrib.get("t") == "inlineStr":
        node = cell.find(f"{NS}is/{NS}t")
        return "" if node is None else node.text or ""
    node = cell.find(f"{NS}v")
    if node is None or node.text is None:
        return None
    text = node.text
    if cell.attrib.get("t") == "b":
        return text == "1"
    try:
        value = float(text)
        return int(value) if value.is_integer() else value
    except ValueError:
        return text


def read_sheet(path: Path, name: str) -> list[dict]:
    with zipfile.ZipFile(path) as zf:
        target = sheet_targets(zf).get(name)
        if target is None:
            return []
        header, output = None, []
        with zf.open(target) as stream:
            for _, row in ET.iterparse(stream, events=("end",)):
                if row.tag != f"{NS}row":
                    continue
                cells = {column_index(c.attrib["r"]): cell_value(c)
                         for c in row.findall(f"{NS}c")}
                if header is None:
                    width = max(cells) + 1
                    header = [cells.get(i) for i in range(width)]
                else:
                    record = {h: cells.get(i) for i, h in enumerate(header) if h}
                    if any(v is not None for v in record.values()):
                        output.append(record)
                row.clear()
        return output


def truthy(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "1.0"}


def percentile(values, q):
    values = sorted(float(v) for v in values)
    if not values:
        return None
    rank = (len(values) - 1) * q
    lo, hi = math.floor(rank), math.ceil(rank)
    return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (rank - lo)


def load(condition, files):
    transitions = []
    for part, path in enumerate(files, start=1):
        pacing = read_sheet(path, "RQ3Pacing")
        replay = {r["captureIndex"]: r for r in read_sheet(path, "PacingReplay")}
        dyn = {r["captureIndex"]: r["durationMs"] for r in read_sheet(path, "DynamicFunctionNode")}
        enc = {r["captureIndex"]: r["durationMs"] for r in read_sheet(path, "SecImageCodecNode")
               if str(r.get("workloadKey", "")).startswith("ENCODING")}
        by_run = {}
        for row in pacing:
            by_run.setdefault(row["runId"], []).append(row)
        for summary in read_sheet(path, "RQ3Summary"):
            shots = sorted(by_run.get(summary["runId"], []), key=lambda r: r["runShotIndex"])
            level = int(summary["startingOverheatLevel"])
            if not truthy(summary["isComplete30ShotRun"]):
                continue
            # Known timeout-measurement errors are invalid observations. This
            # is data-quality filtering, not survival conditioning; no valid
            # analyzed run experienced an actual Capture Timeout.
            if any(truthy(r.get("captureTimedOut")) for r in shots):
                continue
            if condition == "24mp_memory" and level <= 4:
                head = [r.get("sizeBucket") for r in shots if r["runShotIndex"] in (1, 2)]
                if head and all(size == "MP12" for size in head):
                    continue
            for row in shots:
                if not 2 <= row["runShotIndex"] <= 30:
                    continue
                if not (truthy(row.get("pacingDecisionRecorded"))
                        and truthy(row.get("realTraceCompleteBeforeDelay"))):
                    continue
                if truthy(row.get("captureWatchdogFailed")):
                    continue
                pr = replay.get(row["captureIndex"])
                if pr is None:
                    continue
                keys = ("beforeAppliedDelayMs", "draftSequenceDurationMs",
                        "beforeTimeToDeadlineMs", "workloadSequenceDurationMs")
                if any(pr.get(k) is None for k in keys) or row.get("realBacklogMs") is None:
                    continue
                if dyn.get(row["captureIndex"]) is None or enc.get(row["captureIndex"]) is None:
                    continue
                d = float(pr["beforeAppliedDelayMs"])
                backlog = float(row["realBacklogMs"])
                duration = float(pr["draftSequenceDurationMs"])
                time_left = max(0.0, float(pr["beforeTimeToDeadlineMs"]))
                overhead = duration - float(pr["workloadSequenceDurationMs"])
                mandatory_duration = float(dyn[row["captureIndex"]]) + float(enc[row["captureIndex"]]) + overhead
                d_exec = math.ceil(max(0.0, backlog + 2 * duration - time_left) / 2)
                d_mand = math.ceil(max(0.0, backlog + 2 * mandatory_duration - time_left) / 2)
                if d_exec <= 0:
                    continue
                if d_mand > d_exec:
                    raise AssertionError(f"mandatory envelope exceeds executed envelope: {path} {row['captureIndex']}")
                if d < d_mand:
                    category = "below_mandatory"
                elif d < d_exec:
                    category = "admission_flexible"
                else:
                    category = "full_covered"
                transitions.append({
                    "condition": condition,
                    "run": f"{part}#{int(summary['runId'])}",
                    "shot": int(row["runShotIndex"]),
                    "d": d,
                    "d_exec": d_exec,
                    "d_mand": d_mand,
                    "category": category,
                    "potential_avoided_ms": max(0.0, d_exec - d),
                    "margin_ms": row.get("timeoutMarginMs"),
                    # The Capture Timeout budget is an internal constant and must
                    # not be printed in the manuscript, so every rendered
                    # quantity derived from it is a share of it.  Carried per
                    # decision rather than hard-coded; main() checks it is one
                    # value across the whole condition.
                    "budget_ms": float(pr["captureTimeoutMs"]),
                    # Raw terms of the two floor formulas, carried so that
                    # rq3_coordination_audit.py can decompose the realized
                    # deadline margin without recomputing them here.
                    "backlog_ms": backlog,
                    "time_left_ms": time_left,
                    "c_exec_ms": duration,
                    "c_mand_ms": mandatory_duration,
                })
    return transitions


def swarm(values, row):
    ordered = sorted(enumerate(values), key=lambda pair: (pair[1], pair[0]))
    last_x, lane = None, 0
    lanes = [0, 1, -1, 2, -2, 3, -3, 4, -4]
    output = []
    for _, value in ordered:
        if last_x is None or value - last_x > 22:
            lane = 0
        else:
            lane += 1
        output.append((value, row + 0.055 * lanes[lane % len(lanes)]))
        last_x = value
    return output


def write_csv(path, header, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(values)


def main():
    results = {condition: load(condition, files) for condition, files in CONDITIONS.items()}
    summary_rows, envelope_rows = [], []
    row_slot = {"12mp_normal": 1, "24mp_memory": 0}
    for condition, transitions in results.items():
        budgets = {t["budget_ms"] for t in transitions}
        assert len(budgets) == 1, f"{condition}: captureTimeoutMs is not constant: {budgets}"
        total = len(transitions)
        counts = {category: sum(t["category"] == category for t in transitions)
                  for category in ("full_covered", "admission_flexible", "below_mandatory")}
        flexible = [t for t in transitions if t["category"] == "admission_flexible"]
        below = [t for t in transitions if t["category"] == "below_mandatory"]
        avoided = [t["potential_avoided_ms"] for t in flexible]
        envelope_rows.append([
            condition, row_slot[condition], total,
            round(100 * counts["full_covered"] / total, 2),
            round(100 * counts["admission_flexible"] / total, 2),
            round(100 * counts["below_mandatory"] / total, 2),
            counts["full_covered"], counts["admission_flexible"],
            counts["below_mandatory"],
        ])
        metrics = [
            ("realizedWorkEnvelopePositive", total, total),
            ("realizedWorkEnvelopeCovered", counts["full_covered"], total),
            ("admissionFlexibleBand", counts["admission_flexible"], total),
            ("belowMandatoryFloor", counts["below_mandatory"], total),
            ("potentialAvoidedDelayMsP50", round(percentile(avoided, 0.5), 1) if avoided else "", len(avoided)),
            ("potentialAvoidedDelayMsP95", round(percentile(avoided, 0.95), 1) if avoided else "", len(avoided)),
            ("belowMandatoryMarginMsMin", round(min(t["margin_ms"] for t in below), 1) if below else "", len(below)),
        ]
        for metric, value, denominator in metrics:
            summary_rows.append([condition, metric, value, denominator])
        write_csv(
            OUT / f"avoided_delay_{condition}.csv",
            ["avoided_ms", "y"],
            [[round(value, 2), round(y, 3)] for value, y in swarm(avoided, row_slot[condition])],
        )
        # Every positive-envelope transition, ordered by the delay its realized
        # Draft work would have needed.  The figure draws the two envelopes as
        # curves over this order and the applied delay as marks against them, so
        # the three categories become regions rather than three counts.  Sorting
        # by (d_exec, d_mand, d) makes the upper curve monotone and the order
        # reproducible.
        ordered = sorted(transitions, key=lambda t: (t["d_exec"], t["d_mand"], t["d"]))
        write_csv(
            OUT / f"envelope_ladder_{condition}.csv",
            ["rank", "mandatory_ms", "realized_ms", "applied_ms", "category"],
            [[index, int(t["d_mand"]), int(t["d_exec"]), int(round(t["d"])), t["category"]]
             for index, t in enumerate(ordered, start=1)],
        )
        # The category is not emitted as separate mark files on purpose: the
        # figure draws one mark style and lets the regions carry the category,
        # so a per-category split would be data nothing reads.  The category
        # column of the ladder file keeps it auditable.
        print(f"{LABEL[condition]}: n={total}, full={counts['full_covered']}, "
              f"flexible={counts['admission_flexible']}, below mandatory={counts['below_mandatory']}, "
              f"avoided P50/P95={percentile(avoided, 0.5):.1f}/{percentile(avoided, 0.95):.1f} ms")

    write_csv(
        OUT / "envelope_share.csv",
        ["condition", "slot", "n", "full_covered_pct", "admission_flexible_pct",
         "below_mandatory_pct", "full_count", "flexible_count", "below_count"],
        envelope_rows,
    )
    write_csv(OUT / "summary.csv", ["condition", "metric", "value", "denominator"], summary_rows)


if __name__ == "__main__":
    main()
