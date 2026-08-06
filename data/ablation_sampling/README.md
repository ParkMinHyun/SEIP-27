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

Each is standardised robustly within the cell,
`z = (x - median) / (1.4826 * MAD)`, and a metric whose MAD is zero contributes
nothing. The deviation score is the Euclidean norm of the four `z` values, and
the `N - 10` runs with the largest score are dropped. Ties break by workbook
part, then run id, so the selection is deterministic.

`sampling_selection_audit.csv` records every run of every trimmed cell with its
four metrics, its four `z` values, its score, and `KEEP`/`DROP`.

## Known bias -- read before quoting these numbers

The score is computed on **reported outcome metrics**, so the trim is not
outcome-neutral, and in one cell it removes a real mode rather than measurement
error. At 12MP normal / Lv4 the M+S distribution is bimodal: four of the
fourteen runs retained all optional Draft work (100%) while the rest sat at
23-40%. Those four runs are furthest from the median and are all dropped, so
the cell moves 53.1% to 34.3%. The same effect, smaller, applies at Lv3
(53.6% to 44.3%).

Effect on the RQ1(a) cells that changed:

| Cell | M+S@30 | Sigma-d P50 (s) | Slack P5 (%) | Activated@30 (%) |
|---|---|---|---|---|
| 12MP Lv2 | 88.7 -> 89.3 | 1.3 -> 1.1 | 5.1 -> 4.3 | 15.1 -> 13.8 |
| 12MP Lv3 | 53.6 -> 44.3 | 3.2 -> 3.1 | 4.1 -> 4.0 | 35.3 -> 27.9 |
| 12MP Lv4 | 53.1 -> 34.3 | 4.5 -> 3.5 | 5.7 -> 5.0 | 44.8 -> 33.8 |
| 12MP Lv5 | 32.9 -> 27.3 | 3.9 -> 3.9 | 3.9 -> 3.4 | 32.8 -> 29.3 |
| 12MP Lv6 | 30.3 -> 27.7 | 4.4 -> 4.3 | 5.2 -> 5.3 | 32.0 -> 32.8 |
| 24MP Lv1 | 97.3 -> 97.0 | 0.2 -> 0.2 | 8.3 -> 7.7 | 6.3 -> 6.9 |
| 24MP Lv3 | 43.6 -> 46.7 | 4.1 -> 4.2 | 4.4 -> 4.3 | 34.8 -> 36.9 |

If these workbooks are used for a published table, the protocol has to be
predeclared and the direction of the bias stated. Two outcome-neutral
alternatives were computed for comparison: keeping the first ten runs by
collection order gives 12MP Lv3/Lv4 M+S of 48.3/55.0, and scoring deviation on
Slack P5 alone gives 54.3/56.3.

## Cells still above N = 10

Only the Full arm was balanced. Two RQ1(b) cells in other arms remain uneven
and were left alone because they were not in scope:

- 12MP normal / Lv3 / Pacing only -- 11 runs
- 24MP memory / Lv4 / Pacing only -- 13 runs

The current RQ1(b) table reports only Lv4. For its 24MP/Lv4 Pacing-only cell,
the table takes the first ten eligible runs in workbook collection order after
`includedForRq1` filtering (run ids 5, 6, 7, 8, 14, 15, 16, 17, 18 and 19).
This reporting-time selection leaves the source workbook unchanged and makes
all eight displayed RQ1(b) cells `N = 10`.

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
