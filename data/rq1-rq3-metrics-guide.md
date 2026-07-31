# RQ1--RQ3 Measurement and Excel Aggregation Guide

## 1. Purpose and scope

This document defines what RQ1--RQ3 evaluate, what each reported metric
means, and how to derive the paper tables and figures from workbooks produced
by `CaptureMetricsExcelExporter`.

The definitions were checked against:

- paper commit `d181dea3ce5bfbe37bb4568edeade3b6aa9101e6`;
- implementation commit `1904ec0098fd203ed7f34e9375e4e66ece4b4118`;
- `CaptureMetricsExcelExporter.kt`;
- `data/rq1_metrics_aggregation.md`;
- `data/rq2_metrics_aggregation.md`.

The exporter intentionally does not store an RQ3 policy name. The experiment
operator must identify each workbook as `no_pacing`, `static_lut`,
`queue_dynamic`, or `ours` when supplying it for aggregation. That
operator-provided mapping is the authoritative policy label.

## 2. Research-question overview

| RQ | Research question | Main evidence |
|---|---|---|
| RQ1 | Does the coordinated controller prevent Capture Timeout while preserving optional Draft functionality at acceptable intervention cost? | End-to-end ablation and full-controller behavior |
| RQ2 | Does admission retain optional work that can safely complete and reject work that would exceed its remaining budget? | Factual admitted outcomes and an Always-admit audit |
| RQ3 | Does the pacing policy control Draft backlog and queue depth with an objectively justified amount of user-visible delay? | Four-policy pacing comparison under a fixed admitted workload |

The intended argument is:

1. **RQ1 establishes end-to-end effectiveness.**
2. **RQ2 isolates the quality of workload control (admission).**
3. **RQ3 isolates the quality of arrival control (pacing).**

## 3. Common definitions and aggregation rules

### 3.1 Workload notation

- \(M\): the lightweight multi-frame Draft stage, operationalized by the
  Bokeh/PORTRAIT admission group.
- \(S\): optional single-frame Draft processing, operationalized in the
  current RQ1 aggregation by the Filter completion marker and in RQ2 by the
  selected Filter admission-decision row.
- \(B\): the remaining deadline budget at an admission decision.
- \(C\): the factual remaining wall time from the selected Bokeh or Filter
  node start to Draft completion.
- \(d_i\): the pacing delay associated with shot \(i\). In the current
  aggregation convention, this delay gates the transition to shot \(i+1\).
- \(B_i^{real}\): the measured Draft backlog at a pacing decision.
- \(Q_i^{real}\): the measured number of earlier Drafts waiting to start at a
  pacing decision.

### 3.2 Experiment-run reconstruction

Process rows in worksheet order. Start a new run whenever the current
`ppSequenceId` is less than or equal to the preceding value:

```text
current_run = []
previous_pp = none

for capture in worksheet order:
    if current_run is not empty and capture.ppSequenceId <= previous_pp:
        emit current_run
        current_run = []
    append capture to current_run
    previous_pp = capture.ppSequenceId

emit current_run
```

`RQ3Pacing.runId` and `RQ3Summary.runId` already apply this rule. Do not use a
runtime pacer-session reset as an RQ3 trial boundary because the Draft queue
may drain inside one 30-shot experiment.

### 3.3 Shot-to-transition mapping

A 30-shot run has 29 reportable transitions. The delay associated with the
final shot is excluded from:

- pacing activation rate;
- positive-delay percentiles;
- cumulative session delay.

The exporter provides `delayAppliesBeforeShotIndex` and
`transitionDelayMs` so this mapping does not need to be inferred again.

### 3.4 Percentiles

Use inclusive percentile interpolation, equivalent to Excel
`PERCENTILE.INC`. Do not calculate a displayed percentile from previously
rounded values.

### 3.5 Valid-run policy

- Use complete 30-shot runs unless a separately documented protocol defines
  an exception.
- Maintain an explicit invalid-run manifest. Do not exclude a run merely
  because it contains an unfavorable outcome.
- Before concatenating workbooks, deduplicate exact cross-workbook trials by
  their ordered per-capture identity and timestamp sequence. Count each unique
  run once and record which workbook contained the duplicate copy.
- Retain Capture Timeout and watchdog events unless the predeclared protocol
  says otherwise.
- Do not mix devices, capture conditions, starting thermal levels, or pacing
  policies in one aggregate.
- Record the number of attempted, included, invalid, incomplete, timeout, and
  watchdog-bearing runs.

### 3.6 Workbook manifest

Record the following metadata before reading result values:

| Field | Example |
|---|---|
| Workbook basename | `device_a_metrics_01.xlsx` |
| Device | `Device A` |
| Policy | `no_pacing` |
| Capture condition | `12MP normal` |
| Starting thermal level | `3` |
| Attempted runs | experiment record |
| Invalid-run indices and reasons | predeclared manifest or `none` |

The policy value comes from the experiment operator, not from an Excel
column.

## 4. RQ1: End-to-end controller effectiveness

### 4.1 Research question

> Does coordinating remaining-work admission and capture pacing prevent
> Capture Timeout while retaining optional Draft functionality and limiting
> pacing intervention?

RQ1 has two parts.

### 4.2 RQ1(a): Controller ablation

The four configurations are:

| Configuration | Admission | Pacing | Interpretation |
|---|---:|---:|---|
| Baseline | Off | Off | No controller |
| Admission only | On | Off | Controls current service demand only |
| Pacing only | Off | On | Controls future arrivals only |
| Ours | On | On | Coordinated workload and arrival control |

Each table cell reports the first Capture Timeout onset as `E/M`:

- `E`: earliest first-timeout shot across repeated runs;
- `M`: Kaplan--Meier median first-timeout shot, with runs without a timeout
  right-censored at shot 30;
- `--`: the statistic was not reached within 30 shots.

For example, `13/18` means that the earliest run first timed out at shot 13
and the median first-timeout onset was shot 18.

This ablation determines whether either control loop is sufficient alone or
whether their coordination is necessary.

### 4.3 RQ1(b): Full-controller behavior

This table explains when the full controller intervenes and what it preserves.

| Metric | Definition | Interpretation |
|---|---|---|
| Baseline `(E/M)` | Earliest and Kaplan--Meier median first-timeout shot without the controller | Reference failure point |
| Admission-skip onset `(E/M)` | First shot with `bokehAdmitted != true` or `filterAdmitted != true` | Whether workload reduction begins before baseline failure |
| Pacing-delay onset `(E/M)` | Shot following the first transition decision with applied delay \(>0\) | Whether arrival control begins before baseline failure |
| Slack P5 `(%)` | Inclusive fifth percentile of `timeoutMarginMs`, normalized by the product Capture Timeout deadline | Lower-tail deadline safety margin |
| \(M+S\) completed `(%)` | Per-run rate of `bokehCompleted && filterCompleted`, then macro-averaged across runs | Retention of the full optional Draft configuration |
| \(M\) completed `(%)` | Per-run rate of `bokehCompleted`, then macro-averaged across runs | Retention of the target multi-frame stage |
| Pacing activated `(%)` | Positive transition delays divided by all eligible transitions | Frequency of user-visible pacing |
| Pacing delay `(ms)` | Median of positive applied delays, following the RQ1 run-level aggregation protocol | Typical nonzero intervention magnitude |

For the current percentage-form Slack column, calculate each eligible
capture's normalized margin before taking P5:

```text
slackPercent = 100 * timeoutMarginMs / captureTimeoutMs
```

`captureTimeoutMs` may be used internally for aggregation but must not be
printed as a product constant in the manuscript.

`@5/@30` reports the same metric over the first 5 and first 30 shots. For a
prefix of \(k\) shots, pacing metrics use at most \(k-1\) transitions.

### 4.4 RQ1 workbook mapping

Primary sheets:

- `Capture`
- `PacingReplay`

Join them by `captureIndex`.

| Purpose | Sheet | Columns |
|---|---|---|
| Run reconstruction | `Capture` | `captureIndex`, `ppSequenceId` |
| Starting level | `Capture` | `firstNodeOverheatLevel` |
| Timeout outcome | `Capture` | `isTimeout` |
| Watchdog audit | `Capture` | `hasWatchdogTimeout` |
| Deadline slack | `Capture`, `PacingReplay` | `timeoutMarginMs`, `captureTimeoutMs` |
| \(M\) decision/completion | `Capture` | `bokehAdmitted`, `bokehCompleted` |
| \(S\) decision/completion | `Capture` | `filterAdmitted`, `filterCompleted` |
| Applied pacing | `PacingReplay` | `beforeAppliedDelayMs` |

The detailed historical aggregation convention is recorded in
`data/rq1_metrics_aggregation.md` in the ML implementation repository.

## 5. RQ2: Admission decision quality

### 5.1 Research question

> Does admission execute optional work when it can finish within the remaining
> budget and reject it when execution would exceed that budget?

RQ2 selects:

- **Multi-frame:** the exact Bokeh admission-decision row;
- **Single-frame:** the exact Filter admission-decision row.

Exactly one selected decision row per capture contributes to the capture-level
admission metrics.

### 5.2 Controller-enforced metrics

#### Admit rate

```text
Admit rate
    = 100 * effective admits / all selected decisions
```

This measures feature availability, not correctness by itself.

#### Admit result: successful / unsafe

For each factual admitted decision:

```text
B = beforeBudgetMs
C = draftEndUptimeMs - nodeStartUptimeMs

successful:
    no watchdog and C <= B

unsafe:
    watchdog invoked, or
    no watchdog and C > B
```

The successful and unsafe percentages use all effective admits in that group
as their denominator. A watchdog-contained execution is unsafe for admission
quality even if the watchdog prevents the end-to-end Capture Timeout.

### 5.3 Always-admit audit metrics

The audit forces optional work to execute while a shadow controller records
the decision it would have made. This supplies factual outcomes for work the
controller would normally skip.

#### All-decision confusion matrix

```text
                         Shadow decision
                     admit             skip
Factual feasible     feasible-admit    feasible-skip
Factual unsafe       unsafe-admit      unsafe-skip
```

Here, feasible means \(C \le B\). Unsafe means \(C > B\) or watchdog
intervention. The table reports the four counts for each condition and
optional-work group. The feasible-admission and unsafe-rejection rates can be
derived as:

```text
feasible-admission rate
    = feasible-admit / (feasible-admit + feasible-skip)

unsafe-rejection rate
    = unsafe-skip / (unsafe-admit + unsafe-skip)
```

The confusion matrix uses every capture-level selected Bokeh or Filter
decision; it is not restricted to the first skip in a run.

#### P50 effect of skipped work

Use the same capture-level shadow-skipped decisions reported by the confusion
matrix. Let \(D\) denote the product Capture Timeout deadline. For a feasible
skip, calculate the normalized unused-budget magnitude:

```text
unusedPercent = 100 * (B - C) / D
```

For an unsafe skip, calculate the normalized avoided-overrun magnitude:

```text
avoidedPercent = 100 * (C - B) / D
```

The table reports the median (P50) within each positive-magnitude class, then
prefixes `+` to unused budget and `-` to avoided overrun to expose their
opposite directions. A large positive value indicates severe
over-conservatism, whereas a larger-magnitude negative value indicates that
the rejection prevented a substantial deadline violation. The deadline
constant is internal and must not appear in the manuscript; report only the
normalized percentage, consistently with RQ1's Slack P5.

Because the confusion matrix already reports the feasible and unsafe skip
counts, the table does not repeat their proportions or sample sizes in the P50
cells. These P50 values describe the typical capture-level decision effect; they
are not inferential estimates over independent runs.

### 5.4 RQ2 workbook mapping

Primary sheet:

- `AdmissionReplay`

Supporting completion timestamps may also be read from `PacingReplay`.

| Purpose | Sheet | Columns |
|---|---|---|
| Run and capture identity | `AdmissionReplay` | `captureIndex`, `ppSequenceId` |
| Selected decision row | `AdmissionReplay` | `admissionStage` (`Bokeh` or `Filter`), `nodeOrder`, `workloadKey` |
| Factual decision | `AdmissionReplay` | `beforeEffectiveAdmit` |
| Shadow/audit decision | `AdmissionReplay` | `afterEffectiveAdmit` |
| Remaining budget \(B\) | `AdmissionReplay` | `beforeBudgetMs` |
| Selected decision time | `AdmissionReplay` | `nodeStartUptimeMs` |
| Timeout deadline | `AdmissionReplay` | `timeoutDeadlineUptimeMs` |
| Watchdog outcome | `AdmissionReplay` | `beforeWatchdogTimedOut`, `beforeCaptureWatchdogFailed` |
| Capture Timeout outcome | `AdmissionReplay` | `beforeCaptureTimedOut` |
| Decision audit labels | `AdmissionReplay` | `beforeDecisionOutcome`, `beforeDecisionObservationStatus`, `afterDecisionOutcome`, `afterObservationStatus` |
| Draft completion | `PacingReplay` | `captureIndex`, `draftEndUptimeMs` |

Do not use `beforeSequenceActualDurationMs` as \(C\). It sums node durations
and does not include the whole remaining wall-clock path to Draft completion.

The detailed historical aggregation convention is recorded in
`data/rq2_metrics_aggregation.md` in the ML implementation repository.

## 6. RQ3: Pacing-delay appropriateness

### 6.1 Research question

> Under the same admitted workload, does the proposed policy keep the Draft
> backlog and queue bounded with less and better-targeted delay than alternative
> pacing policies?

The controlled setup is:

- 12MP normal;
- starting thermal level 3;
- 30 shots per run;
- the same admitted workload across policies;
- separate factual runs for `no_pacing`, `static_lut`, `queue_dynamic`, and
  `ours`;
- results stratified by device.

RQ3 deliberately excludes First Timeout, Slack, shot-to-shot time,
M-retained, safe-burst, and drain metrics. Those either belong to the
end-to-end evaluation or require admission to interpret. RQ3 isolates pacing
cost and backlog control.

### 6.2 RQ3 summary-table metrics

#### Paced (%)

```text
Paced
    = 100 * count(transitionDelayMs > 0)
            / count(nonblank transitionDelayMs)
```

Zeros remain in the denominator. For complete 30-shot runs, the denominator is
29 transitions per run.

#### \(d_{50}/d_{95}\) (ms)

The inclusive median and 95th percentile of positive
`transitionDelayMs` values. Zero-delay transitions are represented by
`Paced (%)` and are excluded from the conditional delay-magnitude
distribution. Pool the positive transitions from all included runs within one
device-policy pair. If every observed transition delay is zero, report `0/0`;
use `--` only when the required observations are missing.

#### \(\sum d\) (s)

The sum of all 29 `transitionDelayMs` values in a run, converted from
milliseconds to seconds:

```text
total delay (s) = sum(transitionDelayMs) / 1000
```

For a device-policy table row with repeated complete runs, report the median
of the run-level totals. Retain the full run-level distribution for audit.

#### \(B_{\max}\) (s)

At a decision timestamp \(t_i\), the exporter reconstructs:

```text
realBacklogMs_i
    = max(draftEndUptimeMs of unfinished earlier Drafts) - t_i
```

If no earlier Draft is unfinished, backlog is zero. \(B_{\max}\) is the
maximum valid `realBacklogMs` observed across all included runs for that
device-policy pair, converted to seconds.

Use measured Draft timestamps, not `controllerBacklogMs`, for the paper
outcome.

#### \(Q_{\max}\)

At a decision timestamp, `realQueueDepth` counts unfinished earlier Drafts
whose `draftStartUptimeMs` is later than the timestamp. It therefore counts
Drafts waiting to start and excludes a Draft that is already running.

\(Q_{\max}\) is the maximum valid `realQueueDepth` observed across all
included runs for that device-policy pair.

`realOutstandingDraftCount` includes the running Draft as well, but it is an
audit column rather than the paper's \(Q\) metric.

### 6.3 RQ3 figure metrics

For every `(device, policy, shot)` group, compute the inclusive P10, median,
and P90 of:

- `realBacklogMs`;
- `realQueueDepth`;
- `transitionDelayMs`.

The policy CSV schema is:

```text
shot,
backlog_median,backlog_p10,backlog_p90,
queue_depth_median,queue_depth_p10,queue_depth_p90,
delay_median,delay_p10,delay_p90
```

The panels mean:

| Panel | Metric | Interpretation |
|---|---|---|
| Backlog vs. shot | Per-shot real-backlog distribution | Whether queued processing time accumulates during the burst |
| Queue depth vs. shot | Per-shot waiting-Draft distribution | How many Drafts are waiting for service |
| Pacing delay vs. shot | Per-shot applied-delay distribution | When and how strongly each policy intervenes |
| Backlog vs. cumulative delay | Session pacing cost against maximum real backlog | Whether backlog reduction justifies the added delay |

The current LaTeX plot reads only each `*_median` series even though the CSV
schema retains P10 and P90. Add bands or error bars before claiming that the
figure displays variability.

### 6.4 Cost--backlog panel

With exactly one calibrated configuration per policy, this panel contains one
point per policy:

```text
x = median run-level cumulative delay (s)
y = maximum observed real backlog (s)
```

This is a cost--backlog scatter comparison, not a frontier. Calling it a
frontier requires multiple parameter settings per policy and separate factual
runs for each setting.

The current `backlog_cost.csv` schema is:

```text
no_pacing_delay_s,no_pacing_max_backlog_s,
static_delay_s,static_max_backlog_s,
queue_dynamic_delay_s,queue_dynamic_max_backlog_s,
ours_delay_s,ours_max_backlog_s
```

### 6.5 RQ3 workbook mapping

Primary sheets:

- `RQ3Pacing`: per-shot and per-transition values;
- `RQ3Summary`: run-level audit and preliminary summaries.

| Paper/figure value | Preferred source |
|---|---|
| Device | `RQ3Pacing.deviceModel` |
| Run | `RQ3Pacing.runId` |
| Shot | `RQ3Pacing.runShotIndex` |
| Complete-run check | `RQ3Pacing.runShotCount` or `RQ3Summary.isComplete30ShotRun` |
| Starting level | `RQ3Pacing.startingOverheatLevel` |
| Resolution bucket | `RQ3Pacing.sizeBucket` |
| Memory condition | `RQ3Pacing.isLowMemory` |
| Applied transition delay | `RQ3Pacing.transitionDelayMs` |
| Cumulative delay | `RQ3Pacing.cumulativeTransitionDelayMs` |
| Real backlog | `RQ3Pacing.realBacklogMs` |
| Real queue depth | `RQ3Pacing.realQueueDepth` |
| Trace validity | `RQ3Pacing.realTraceCompleteBeforeDelay` |
| Timeout/watchdog audit | `RQ3Pacing.captureTimedOut`, `captureWatchdogFailed` |
| Run-level delay audit | `RQ3Summary.totalDelayMs`, `positiveDelayP50Ms`, `positiveDelayP95Ms` |
| Run-level maxima | `RQ3Summary.maxRealBacklogMs`, `maxRealQueueDepth` |
| Coverage audit | `RQ3Summary.pacingDecisionCoveragePercent`, `realTraceCoveragePercent` |

Use `RQ3Pacing` to produce final cross-run percentiles. `RQ3Summary` is useful
for validation, but its run-level P50/P95 values must not be pooled or averaged
to approximate the event-level P50/P95.

## 7. Mandatory pre-collection checks for RQ3

These checks determine whether an exported workbook can factually populate the
RQ3 table and figure.

### 7.1 Persist the delay that was actually scheduled

`RQ3Pacing.appliedDelayMs` currently comes from
`CaptureAvailablePacingMetrics.appliedDelayMs`, which is produced from the
queued `CaptureAvailablePacingDecision`.

If `CaptureAvailableApmPolicy` calculates a different local scheduler delay
without updating the persisted decision, the workbook will contain the
original pacer delay rather than the delay actually experienced by the user.
In that case:

- `transitionDelayMs` is incorrect;
- `cumulativeTransitionDelayMs` is incorrect;
- `releaseUptimeMs` is incorrect;
- backlog/queue values reconstructed at release are incorrect.

Before collecting each policy, verify that the decision persisted into
`CaptureAvailablePacingMetrics` contains exactly the delay passed to the
scheduler.

### 7.2 Preserve an observation timestamp for No pacing

The No-pacing run still needs a decision/observation timestamp with an applied
delay of zero. If the decider path is bypassed entirely,
`decisionUptimeMs` is absent and the exporter cannot reconstruct comparable
decision-time `realBacklogMs` or `realQueueDepth`.

No pacing should therefore mean:

```text
observe the same decision point
record applied delay = 0
schedule immediately
```

It should not mean removing the measurement point.

### 7.3 Require complete Draft timelines

For a non-initial row to contribute factual backlog and queue depth, every
earlier Draft relevant to that snapshot must contain both:

- `draftStartUptimeMs`;
- `draftEndUptimeMs`.

If an earlier Draft timeline is incomplete, the exporter intentionally leaves
the real-backlog and real-queue fields blank instead of treating them as zero.

### 7.4 Keep admission fixed

The four pacing policies must receive the same admitted workload sequence.
Otherwise, a policy may appear to control backlog simply because Admission
removed more work, and RQ3 would no longer isolate pacing ability.

## 8. Output files to populate

### Paper tables

- `tables/tab_rq1_ablation.tex`
- `tables/tab_rq1_result.tex`
- `tables/tab_rq2_admission_summary.tex`
- `tables/tab_rq3_pacing_summary.tex`

### RQ3 figure

- `figures/fig_rq3_pacing_trajectories.tex`
- `data/rq3/<device>/no_pacing.csv`
- `data/rq3/<device>/static_lut.csv`
- `data/rq3/<device>/queue_dynamic.csv`
- `data/rq3/<device>/ours.csv`
- `data/rq3/<device>/backlog_cost.csv`

## 9. Current manuscript issues to resolve before final submission

1. `_4_experiments.tex` still contains unrelated placeholder research
   questions and is disabled in `paper.tex`; the actual RQ1--RQ3 wording must
   be added to the manuscript.
2. The current RQ3 table and figure name S26 Ultra and S26. If the evaluation
   uses Device A/B/C, both artifacts and their data directories must be
   updated consistently.
3. The RQ3 CSVs contain P10/P90 columns, but the current plot renders median
   lines only.
4. The current figure caption calls the cost--backlog panel a frontier. With
   one configuration per policy it must instead be described as a scatter
   comparison, or the experiment must add parameter sweeps.
5. The historical RQ1 aggregation note describes Slack P5 in milliseconds,
   whereas the current paper table labels and comments define a
   deadline-normalized percentage. This guide follows the current paper:
   normalize each event first and then calculate P5.
6. Any deviation from the aggregation rules in this document must be recorded
   before inspecting comparative outcomes.

## 10. Data handoff checklist

When providing a new workbook for table or figure population, state:

```text
Device:
Policy:
Capture condition:
Starting thermal level:
Number of intended 30-shot runs:
Known invalid runs and reasons:
```

The aggregation pass should then:

1. verify the required sheets and columns;
2. reconstruct and audit runs;
3. apply only predeclared exclusions;
4. validate actual-delay and real-trace coverage;
5. compute unrounded event- and run-level results;
6. generate the table cells and RQ3 CSV files;
7. compare every changed cell against the source aggregate;
8. build and visually inspect the paper PDF.
