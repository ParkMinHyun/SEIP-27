# SM-S942B Metrics Recovery Notes

Created on 2026-08-29 from facts inspected before the workbook at the original path was replaced. This file records only values that were directly observed in the original workbook, recovered from its pre-replacement PDF rendering, or derived deterministically from those records.

## Important scope

- The records below describe the original `/home/minhyun/Downloads/metrics/SM-S942B_metrics.xlsx` inspected at 13:56 JST.
- The workbook later found at that path is a different, smaller device export. Do not treat it as the 60-session source.
- No `INCOMPLETE` deletion was executed against the 60-session workbook before it was replaced.
- Shot indices in this note are 1-based.

## Original workbook identity

| Field | Value |
|---|---|
| File size | 3,799,841 bytes |
| Local modification time observed | 2026-08-29 13:56:44.115607987 +0900 |
| SHA-256 | `e539e4cf6bd48e4278c0ab02287f7e99c4c576d34235d5b0cc731d24f8a67995` |
| RQ1Runs records | 60 sessions plus header |
| Capture records | 912 captures plus header |
| Status counts | `CAPTURE_TIMEOUT=53`, `INCOMPLETE=5`, `COMPLETE_30=2` |
| RQ1 included | 55 sessions |
| Complete/timeout overlap | runId 40: complete 30-shot run and first timeout at shot 30 |

## Workbook sheet inventory

Row counts include the header row.

| Sheet | Rows |
|---|---:|
| AdmissionReplay | 4,543 |
| PacingReplay | 913 |
| ReplayScope | 301 |
| RQ1Runs | 61 |
| RQ1Conditions | 11 |
| CaseStudyTrace | 907 |
| RQ3Pacing | 913 |
| RQ3Summary | 61 |
| ReplayNotes | 28 |
| Capture | 913 |
| DynamicFunctionNode | 913 |
| SecDualBokehNode | 913 |
| SecFilterNode | 904 |
| SecImageCodecNode | 2,728 |
| WatermarkNode | 913 |

## RQ1 session aggregation before deletion

`30-shot complete` and `Capture Timeout` are not mutually exclusive. runId 40 belongs to both.

| Starting overheat level | Total sessions | 30-shot complete | Capture Timeout | Other incomplete (`runStatus=INCOMPLETE`) | RQ1 included |
|---:|---:|---:|---:|---:|---:|
| 0 | 5 | 1 | 5 | 0 | 5 |
| 1 | 6 | 2 | 3 | 1 | 5 |
| 2 | 6 | 0 | 5 | 1 | 5 |
| 3 | 12 | 0 | 10 | 2 | 10 |
| 4 | 11 | 0 | 10 | 1 | 10 |
| 5 | 10 | 0 | 10 | 0 | 10 |
| 6 | 10 | 0 | 10 | 0 | 10 |
| **Total** | **60** | **3** | **53** | **5** | **55** |

## Expected aggregation after deleting all INCOMPLETE sessions

| Starting overheat level | Total sessions | 30-shot complete | Capture Timeout | Other incomplete | RQ1 included |
|---:|---:|---:|---:|---:|---:|
| 0 | 5 | 1 | 5 | 0 | 5 |
| 1 | 5 | 2 | 3 | 0 | 5 |
| 2 | 5 | 0 | 5 | 0 | 5 |
| 3 | 10 | 0 | 10 | 0 | 10 |
| 4 | 10 | 0 | 10 | 0 | 10 |
| 5 | 10 | 0 | 10 | 0 | 10 |
| 6 | 10 | 0 | 10 | 0 | 10 |
| **Total** | **55** | **3** | **53** | **0** | **55** |

## INCOMPLETE sessions selected for deletion

| runId | Starting level | Source/analyzed shots | Size/configuration | CaptureIndex range |
|---:|---:|---:|---|---|
| 4 | 4 | 6 | MP12, M+S | 41–46 |
| 20 | 2 | 9 | MP12, M | 195–203 |
| 47 | 3 | 8 | MP24, M+S | 592–599 |
| 52 | 3 | 1 | MP24, M+S | 700 |
| 58 | 1 | 25 | MP12, M+S | 836–860 |

The five sessions account for 49 captures.

### Rows associated with those sessions

| Sheet | Rows to remove | Match key |
|---|---:|---|
| AdmissionReplay | 227 | CaptureIndex |
| PacingReplay | 49 | CaptureIndex |
| ReplayScope | 25 | runId |
| RQ1Runs | 5 | runId |
| CaseStudyTrace | 49 | runId |
| RQ3Pacing | 49 | runId |
| RQ3Summary | 5 | runId |
| Capture | 49 | CaptureIndex |
| DynamicFunctionNode | 49 | CaptureIndex |
| SecDualBokehNode | 49 | CaptureIndex |
| SecFilterNode | 40 | CaptureIndex |
| SecImageCodecNode | 138 | CaptureIndex |
| WatermarkNode | 49 | CaptureIndex |

`RQ1Conditions` has no runId. The incomplete-only rows for level 1/MP12/M+S, level 2/MP12/M, and level 4/MP12/M+S should disappear. In the level 3/MP24/M+S row, `sourceRunCount` and the sheet's `incompleteRunCount` should change from 12 to 10. Other included-run metrics remain unchanged because all five target sessions had `includedForRq1=false`.

## Capture Timeout occurrence points

The list contains each timeout session's `firstTimeoutShot`. In this collection it matched the terminal analyzed shot for every `CAPTURE_TIMEOUT` session.

| Starting level | Timeout sessions | First-timeout shots, sorted | Earliest shot | RQ1 Kaplan–Meier median shot |
|---:|---:|---|---:|---:|
| 0 | 5 | 23, 27, 27, 27, 30 | 23 | 27 |
| 1 | 3 | 21, 25, 26 | 21 | 26 |
| 2 | 5 | 19, 21, 25, 28, 28 | 19 | 25 |
| 3 | 10 | 9, 10, 13, 19, 21, 21, 23, 24, 27, 28 | 9 | 21 |
| 4 | 10 | 6, 11, 12, 12, 13, 13, 13, 14, 15, 17 | 6 | 13 |
| 5 | 10 | 3, 3, 7, 7, 8, 8, 8, 8, 11, 11 | 3 | 8 |
| 6 | 10 | 6, 6, 7, 7, 7, 7, 8, 8, 9, 10 | 6 | 7 |

Level 1's raw median among only the three timeout sessions is shot 25. Its RQ1 Kaplan–Meier median is shot 26 because the two completed 30-shot runs are included as censored observations.

### Timeout runId to shot mapping

| Level | runId:firstTimeoutShot |
|---:|---|
| 0 | 19:27, 40:30, 51:27, 54:23, 60:27 |
| 1 | 1:21, 49:26, 59:25 |
| 2 | 41:19, 44:28, 46:28, 53:21, 55:25 |
| 3 | 2:13, 21:10, 22:21, 23:23, 37:24, 42:9, 43:21, 45:27, 48:19, 50:28 |
| 4 | 3:6, 5:17, 6:13, 24:14, 25:13, 26:12, 32:13, 36:11, 38:15, 39:12 |
| 5 | 7:8, 8:8, 27:8, 28:3, 29:3, 30:11, 31:11, 33:8, 34:7, 35:7 |
| 6 | 9:8, 10:7, 11:7, 12:9, 13:7, 14:8, 15:7, 16:10, 17:6, 18:6 |

## Selected RQ1 condition summary

The `incompleteRunCount` field in `RQ1Conditions` means `isComplete30ShotRun=false`; it is not the count of `runStatus=INCOMPLETE`. It therefore includes Capture Timeout runs.

| Level / condition | Source runs | Included | Complete30 | Not-complete30 | Timeout | Earliest timeout | KM median timeout | Slack samples | Slack P5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 / MP24 / M+S | 5 | 5 | 1 | 4 | 5 | 23 | 27 | 134 | 1.910714% |
| 1 / MP12 / M+S | 1 | 0 | 0 | 1 | 0 | — | — | 0 | — |
| 1 / MP24 / M+S | 5 | 5 | 2 | 3 | 3 | 21 | 26 | 132 | 7.410000% |
| 2 / MP12 / M | 1 | 0 | 0 | 1 | 0 | — | — | 0 | — |
| 2 / MP24 / M+S | 5 | 5 | 0 | 5 | 5 | 19 | 25 | 121 | 1.685714% |
| 3 / MP24 / M+S | 12 | 10 | 0 | 12 | 10 | 9 | 21 | 195 | -0.361429% |
| 4 / MP12 / M+S | 1 | 0 | 0 | 1 | 0 | — | — | 0 | — |
| 4 / MP24 / M+S | 10 | 10 | 0 | 10 | 10 | 6 | 13 | 126 | -3.307143% |
| 5 / MP12 / M+S | 10 | 10 | 0 | 10 | 10 | 3 | 8 | 74 | -5.874286% |
| 6 / MP12 / M+S | 10 | 10 | 0 | 10 | 10 | 6 | 7 | 75 | -6.745714% |

## Recovered RQ1Runs basic records

| runId | Source shots | Analyzed shots | Complete30 | runStatus | RQ1 included | Starting level |
|---:|---:|---:|---|---|---|---:|
| 1 | 21 | 21 | FALSE | CAPTURE_TIMEOUT | TRUE | 1 |
| 2 | 13 | 13 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 3 | 6 | 6 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 4 | 6 | 6 | FALSE | INCOMPLETE | FALSE | 4 |
| 5 | 17 | 17 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 6 | 13 | 13 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 7 | 8 | 8 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 8 | 8 | 8 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 9 | 8 | 8 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 10 | 7 | 7 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 11 | 7 | 7 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 12 | 9 | 9 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 13 | 7 | 7 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 14 | 8 | 8 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 15 | 7 | 7 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 16 | 10 | 10 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 17 | 6 | 6 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 18 | 6 | 6 | FALSE | CAPTURE_TIMEOUT | TRUE | 6 |
| 19 | 27 | 27 | FALSE | CAPTURE_TIMEOUT | TRUE | 0 |
| 20 | 9 | 9 | FALSE | INCOMPLETE | FALSE | 2 |
| 21 | 10 | 10 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 22 | 21 | 21 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 23 | 23 | 23 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 24 | 14 | 14 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 25 | 13 | 13 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 26 | 12 | 12 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 27 | 8 | 8 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 28 | 3 | 3 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 29 | 3 | 3 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 30 | 11 | 11 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 31 | 11 | 11 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 32 | 13 | 13 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 33 | 8 | 8 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 34 | 7 | 7 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 35 | 7 | 7 | FALSE | CAPTURE_TIMEOUT | TRUE | 5 |
| 36 | 11 | 11 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 37 | 24 | 24 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 38 | 15 | 15 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 39 | 12 | 12 | FALSE | CAPTURE_TIMEOUT | TRUE | 4 |
| 40 | 30 | 30 | TRUE | CAPTURE_TIMEOUT | TRUE | 0 |
| 41 | 19 | 19 | FALSE | CAPTURE_TIMEOUT | TRUE | 2 |
| 42 | 9 | 9 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 43 | 21 | 21 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 44 | 28 | 28 | FALSE | CAPTURE_TIMEOUT | TRUE | 2 |
| 45 | 27 | 27 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 46 | 28 | 28 | FALSE | CAPTURE_TIMEOUT | TRUE | 2 |
| 47 | 8 | 8 | FALSE | INCOMPLETE | FALSE | 3 |
| 48 | 19 | 19 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 49 | 26 | 26 | FALSE | CAPTURE_TIMEOUT | TRUE | 1 |
| 50 | 28 | 28 | FALSE | CAPTURE_TIMEOUT | TRUE | 3 |
| 51 | 27 | 27 | FALSE | CAPTURE_TIMEOUT | TRUE | 0 |
| 52 | 1 | 1 | FALSE | INCOMPLETE | FALSE | 3 |
| 53 | 21 | 21 | FALSE | CAPTURE_TIMEOUT | TRUE | 2 |
| 54 | 23 | 23 | FALSE | CAPTURE_TIMEOUT | TRUE | 0 |
| 55 | 25 | 25 | FALSE | CAPTURE_TIMEOUT | TRUE | 2 |
| 56 | 33 | 30 | TRUE | COMPLETE_30 | TRUE | 1 |
| 57 | 33 | 30 | TRUE | COMPLETE_30 | TRUE | 1 |
| 58 | 25 | 25 | FALSE | INCOMPLETE | FALSE | 1 |
| 59 | 25 | 25 | FALSE | CAPTURE_TIMEOUT | TRUE | 1 |
| 60 | 27 | 27 | FALSE | CAPTURE_TIMEOUT | TRUE | 0 |

## Replacement file found at the original path

| Field | Value |
|---|---|
| File size | 249,295 bytes |
| Local modification time | 2026-08-29 14:03:08.885375469 +0900 |
| SHA-256 | `e4d1b198d0a9c85085e905f45c202c2524709a0378f4ab7b49220289c1f3ab3d` |
| RQ1Runs records | 3 sessions plus header |
| Capture records | 58 captures plus header |
| Device export timestamp inside workbook | 2026-05-28 13:26 |

The connected device's current `capture_metrics.db` also contained only 58 capture records when inspected. It is not a copy of the original 60-session dataset.

## Preserved rendering of the original

The original workbook was rendered immediately before the path changed. The preserved PDF has 1,789 pages, size 4,692,324 bytes, and SHA-256 `45f6b43f8c5f728a00e00f65813800930bf4db25a8dab42b19847332c5372947`.

The PDF preserves displayed values and was used to recover the run-level table and timeout points above, but it is not an exact replacement for the original XLSX because displayed numeric values may be formatted or rounded.

## Older backups found but not equivalent

- Trash: `SM-S942B_metrics.before-delete-runs-1-39-40.xlsx`, 5,754,828 bytes, modified 09:23.
- Trash: `SM-S942B_metrics_sampling.xlsx`, 5,420,679 bytes, modified 09:40.

These belong to earlier dataset lineages and must not be substituted for the 60-session workbook without an explicit comparison.
