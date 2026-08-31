# `ablation_sampling` -- Full arm balanced to N = 10 per cell

Derived from `data/ablation_original/`, which stays the untouched source of
record. Only the **Full** (admission + pacing) workbooks are modified; the
No-control, Pacing-only and Admission-only workbooks are byte-for-byte copies.

## What changed

The RQ1(a) design was unbalanced: the Full arm had 10-14 runs per
(condition, starting overheat level) cell. Cells with more than ten runs were
trimmed to ten by removing the runs furthest from the cell's own centre.

| Condition | Levels trimmed | N before | N after |
|---|---|---|---|
| 12MP normal | Lv2, Lv3, Lv4, Lv5, Lv6 | 13, 12, 14, 14, 11 | 10 each |
| 24MP memory pressure | Lv1, Lv3 | 11, 11 | 10 each |

Every other cell already had exactly ten runs and is unchanged. 16 runs were
removed in total: 14 from 12MP normal, 2 from 24MP memory pressure.

## Selection rule

For each over-sized cell, over the runs eligible for RQ1(a) -- included,
complete 30-shot, Capture-Timeout-free -- four run-level metrics are collected:

| Metric | Source |
|---|---|
| `msExecPercent` | M+S@30, per-run rate of Bokeh **and** Filter executed over the first 30 captures |
| `totalDelayMs` | Sigma-d, applied pacing delay summed over the 29 transitions |
| `slackP5Ms` | inclusive fifth percentile of `timeoutMarginMs` within the run |
| `burstSpanMs` | `RQ3Summary.burstSpanMs` |

`sampling_selection_audit.csv` records every run of every trimmed cell with its
four metrics, its four `z` values, its score, and `KEEP`/`DROP`.

## Workbook fidelity

The four rewritten workbooks are re-emitted values-only: cell values, types and
positions are preserved, cell formatting is not. Sheets keyed by
`captureIndex` are filtered on the dropped runs' captures; sheets keyed by
`runId` only (`RQ1Runs`, `RQ3Summary`, `ReplayScope`) are filtered on run id.
`ReplayNotes` is carried over unchanged.

`RQ1Conditions` is a per-condition aggregate of the **source** export and
cannot be filtered row-wise, so it is renamed **`RQ1Conditions_SOURCE`** in the
rewritten workbooks. It describes `data/ablation_original`, not this folder.
Recompute it from `RQ1Runs` if it is needed.
