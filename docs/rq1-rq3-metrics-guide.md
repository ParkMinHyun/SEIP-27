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

The current RQ3 no longer uses the four-policy comparison as its main-paper design.
The authoritative RQ3 handoff is `docs/rq3-current.md`, and the generated
coordination-artifact dictionary is `data/rq3/coordination/README.md`. Legacy
`pacingPolicy` fields and four-policy aggregation material remain below only as
historical collection notes; do not use them to frame or regenerate the current
compact RQ3 exhibits.

## 2. Research-question overview

| RQ | Research question | Main evidence |
|---|---|---|
| RQ1 | Does the coordinated controller prevent Capture Timeout while preserving optional Draft functionality at acceptable intervention cost? | End-to-end ablation and full-controller behavior |
| RQ2 | Does admission retain optional work that can safely complete and reject work that would exceed its remaining budget? | Factual admitted outcomes and an Always-admit audit |
| RQ3 | Does the controller compute an appropriately sized pacing delay for the Draft backlog and Capture Timeout budget? | Targeting, boundary diagnosis, admission-aware envelope partition, actual admission action, work conservation, and responsiveness cost |

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
- \(C_{\mathrm{model}}\), \(B_{\mathrm{model}}\): \(C\) and \(B\) with the fresh
  model's own skips honoured. They are **never** the classifier — every reported
  cell uses \(C\) and \(B\) — and exist only for the outcome interpretation in
  section 5.4, which asks whether a shipped build would have emitted the
  overrun. They coincide with \(C\) and \(B\) outside the always-admit audit.
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

### 4.2 RQ1(a): Full-controller behavior

This table explains when the full controller intervenes and what it preserves.

| Metric | Definition | Interpretation |
|---|---|---|
| Controller-off baseline `(E/M)` | Earliest and Kaplan--Meier median first-timeout shot without the controller | Historical failure reference, visually separated from the proposed implementation |
| Full-controller timeout outcome | Capture Timeout count among retained full-controller runs through shot 30 | Deadline-safety audit after applying the predeclared invalid-run manifest |
| Slack P5 `(%)` | Inclusive fifth percentile of `timeoutMarginMs`, normalized by the product Capture Timeout deadline | Lower-tail deadline safety margin |
| \(M+S\) completed `(%)` | Per-run rate of `bokehCompleted && filterCompleted`, then macro-averaged across runs | Retention of the full optional Draft configuration |
| \(M\) completed `(%)` | Per-run rate of `bokehCompleted`, then macro-averaged across runs | Retention of the target multi-frame stage |
| \(S\) completed `(%)` | Per-run rate of `filterCompleted`, then macro-averaged across runs | Retention of optional single-frame Draft processing |
| Pacing activated `(%)` | Positive transition delays divided by all eligible transitions | Frequency of user-visible pacing |
| Pacing delay `(ms)` | Median of positive applied delays, following the RQ1 run-level aggregation protocol | Typical nonzero intervention magnitude |
| Cumulative pacing delay `(s)` | Median across runs of the delay accumulated within the reported prefix | Total responsiveness cost paid by a burst |

The controller-off baseline is a reference and must not share a top-level
header with the full-controller columns.  RQ1(a) explains retained Draft
functionality and intervention cost across starting levels, whereas RQ1(b)
establishes the comparative outcome.  Do not reintroduce signed differences
between a
controller-off timeout shot and a full-controller action onset: admission and
pacing alter one another's later trajectories, and capture indices do not imply
timestamp order under overlapping deadlines.

For the current percentage-form Slack column, calculate each eligible
capture's normalized margin before taking P5:

```text
slackPercent = 100 * timeoutMarginMs / captureTimeoutMs
```

`captureTimeoutMs` may be used internally for aggregation but must not be
printed as a product constant in the manuscript.

`@5/@30` reports the same metric over the first 5 and first 30 shots. For a
prefix of \(k\) shots, pacing metrics use at most \(k-1\) transitions.

Two aggregation rules that the cells depend on, each verified by reproducing the
whole table (14 rows, 20 columns) from the workbooks:

- `N`, Slack P5 and every pacing column use **all** retained runs.
- Completion percentages drop a watchdog-bearing run from the average for the
  horizon the watchdog falls inside, while the run stays in `N`. The exclusion
  is therefore horizon-aware: a watchdog at shot 13 leaves `@5` eligible and
  `@30` ineligible. Two 24MP cells (Lv2, Lv4) contain one such run each, so
  their `@30` completion averages run over 9 of the 10 runs.

Retention is measured by **execution**, as in section 4.3. In this arm that
agrees with the exporter's `Completed` flag; the two diverge only in the
forced-execution arms of RQ1(b).

Every cell reports a balanced `N = 10`; the protocol and its bias are in
section 4.3.1.

### 4.3 RQ1(b): Controller ablation

The four configurations are:

| Configuration | Admission | Pacing | Interpretation |
|---|---:|---:|---|
| No control | Off | Off | No controller |
| Pacing only | Off | On | Controls future arrivals only |
| Admission only | On | Off | Controls current service demand only |
| Ours (Full) | On | On | Coordinated workload and arrival control |

The ablation table reports two conditions, each a (capture condition, starting
overheat level) pair: 12MP normal and 24MP memory pressure at starting level 4.
Within a condition the four configurations are listed in the order above, so
the listing itself walks the Admission-by-Pacing factorial; the table does not
carry separate On/Off columns, because the configuration name already states
them.

`S(30)` alone is **not** sufficient and must never be the only reported column.
An arm can reach zero timeouts trivially by discarding optional Draft work, and
Pacing only can execute all optional work before failure while surviving only
one run per condition. Each row therefore also reports effective retained work,
the incidence of pacing, and the conditional magnitude of the applied delay.
RQ3 separately evaluates whether that delay is appropriately sized.

| Column | Printed as | Definition |
|---|---|---|
| `S(30)` | Survived runs | Runs completing 30 captures with no Capture Timeout, over included runs; the denominator carries `N` |
| \(M\) `(%)` | Work completion | Per-run Bokeh execution rate over the first 30 captures, set to zero when the run does not survive 30 captures without Capture Timeout, then macro-averaged across all included runs |
| \(S\) `(%)` | Work completion | Per-run Filter execution rate over the first 30 captures, set to zero when the run does not survive 30 captures without Capture Timeout, then macro-averaged across all included runs |
| Activated `(%)` | Pacing cost | Percentage of observed eligible outgoing-shot intervals with `transitionDelayMs > 0`; structurally zero when the pacer is off |
| Applied delay P50 `(ms)` | Pacing cost | Inclusive median of positive `transitionDelayMs` values over observed eligible outgoing-shot intervals; `--` when pacing is off |

\(M\) and \(S\) must be measured by **execution** — the node has a positive observed
duration — and *not* by the exporter's `bokehCompleted`/`filterCompleted` flags.
Per ReplayNotes "Recommendation vs execution", `Completed` additionally requires
`recommendedAdmit = true`, and the recommendation is still recorded in the two
forced-execution arms. First compute the execution rate within each run; then
multiply it by the run's `S(30)` indicator before macro-averaging. Thus a failed
run contributes zero even if the node executed on every observed capture. This
gives 0% for No control and 10% for each N=10 Pacing-only cell, where only one
run survives.

Activated uses the same convention as RQ1(a):

```text
Activated (%)
    = 100 * count(transitionDelayMs > 0)
            / count(nonblank transitionDelayMs)
```

The denominator includes zero-delay intervals. Applied delay P50 excludes them
and reports intervention magnitude conditional on pacing having activated.
Together, the two Pacing cost columns report incidence and magnitude; RQ3
evaluates the required versus applied delay and its calibration.

24MP is a requested-mode label: only the first one or two captures are 24MP and
the remaining captures are 12MP.  Starting-level 5--6 runs use the product's
12MP fallback and must not be presented as 24MP ablation evidence.

The sessions previously described as Full-arm Capture Timeout outcomes are now
known to contain an invalid timeout measurement. They are removed as invalid
observations, not as unfavorable outcomes. No valid Full-arm run experienced an
actual Capture Timeout; preserve the measurement-fault and invalid-run manifest
when reporting the valid-run denominator.

### 4.3.1 Data sources and balancing

All four arms live in this repository. `data/ablation_original/` is the untouched source
of record; `data/ablation_sampling/` is the balanced copy the tables read.

| Arm | Workbooks (`48U_metrics_<condition>_…`) |
|---|---|
| No control | `…_baseline_0803.xlsx` |
| Pacing only | `…_pacing_only_0803.xlsx` |
| Admission only | `…_admit_only_0803.xlsx` |
| Full | `…_0803_1.xlsx` **and** `…_0803_2.xlsx` |

The Full arm pools both parts, which is the run set RQ1(a) has always used. Both
parts carry the same policy label (`ReplayScope`: `RECORDED_RUNTIME` /
`FACTUAL_RECORDED_TARGET` / `M+S`) and the deployed pacing formula reproduces
`beforeAppliedDelayMs` on 100% of recorded decisions in each, so they are one
arm.

**Balancing protocol.** RQ1(a) cells held 10–14 runs. Oversized cells (12MP
Lv2–Lv6, 24MP Lv1 and Lv3) are levelled to `N = 10` by scoring each run with the
Euclidean norm of its robust z across \(M+S\)@30, \(\Sigma d\), Slack P5 and
burst span — `z = (x − median) / (1.4826 · MAD)`, a zero-MAD metric contributing
nothing — and dropping the `N − 10` highest. 16 runs are removed;
`data/ablation_sampling/sampling_selection_audit.csv` records every run with its
metrics, z values, score and KEEP/DROP.

**The protocol is not outcome-neutral and this must be disclosed.** The score
reads reported outcomes, so where a cell is bimodal it deletes a mode rather
than measurement error. At 12MP / Lv4 four of fourteen runs retained all
optional Draft work (100%) against 23–40% for the rest; all four are dropped and
the cell moves 53.1% → 34.3%. Lv3 moves 53.6% → 44.3%. Outcome-neutral
alternatives, for reference: first-ten-by-collection-order gives 48.3/55.0 and
scoring on Slack P5 alone gives 54.3/56.3.

Only the Full arm was balanced by rewriting workbooks. For the displayed
24MP / Lv4 Pacing-only cell, RQ1(b) additionally takes the first ten eligible
runs in workbook collection order after `includedForRq1` filtering: run ids 5,
6, 7, 8, 14, 15, 16, 17, 18 and 19. This reporting-time selection makes every
displayed ablation cell `N = 10` without modifying the source workbook.

**Timeout-measurement data-quality rule.** Full-arm run ids 12MP 9 and 24MP
35--36 were previously labelled as Capture Timeout sessions, but those labels
come from the known measurement fault rather than actual timeout outcomes. Their
removal is invalid-observation filtering, not survival conditioning. Record the
fault, the affected ids, and the exclusion rule in the final artifact; no valid
Full-arm run timed out.

`scripts/rq1_ablation_metrics.py` predates this reorganization: its workbook
paths point at a different machine and at the retired 0729 campaign, and it
computes \(M+S\) from the `Completed` flags. Re-point it at
`data/ablation_sampling/` and switch it to execution before reusing it.

### 4.4 RQ1 workbook mapping

Primary sheets:

- `Capture`
- `PacingReplay`
- `RQ1Runs`
- `RQ3Pacing`

Join `Capture` and `PacingReplay` by `captureIndex`. For RQ1(b), select runs
from `RQ1Runs` and join their per-shot records in `RQ3Pacing` by `runId`.

| Purpose | Sheet | Columns |
|---|---|---|
| Run reconstruction | `Capture` | `captureIndex`, `ppSequenceId` |
| RQ1(b) run inclusion | `RQ1Runs` | `runId`, `includedForRq1`, `startingOverheatLevel`, `isComplete30ShotRun`, `timeoutEventObserved` |
| Starting level | `Capture` | `firstNodeOverheatLevel` |
| Timeout outcome | `Capture` | `isTimeout` |
| Watchdog audit | `Capture` | `hasWatchdogTimeout` |
| Deadline slack | `Capture`, `PacingReplay` | `timeoutMarginMs`, `captureTimeoutMs` |
| \(M\) decision/completion | `Capture` | `bokehAdmitted`, `bokehCompleted` |
| \(S\) decision/completion | `Capture` | `filterAdmitted`, `filterCompleted` |
| Applied pacing | `PacingReplay` | `beforeAppliedDelayMs` |
| RQ1(b) \(M\)/\(S\) execution | `RQ3Pacing` | `bokehExecuted`, `filterExecuted` |
| RQ1(b) pacing activation | `RQ3Pacing` | `transitionDelayMs` |
| RQ1(b) applied delay P50 | `RQ3Pacing` | `transitionDelayMs` |

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

`beforeBudgetMs` is the time left until the Capture Timeout deadline at that
node, so \(C > B\) and the capture timing out are the same event. In the three
audit workbooks every one of the 154 over-budget decisions belongs to a capture
that timed out. Do not present the unsafe-admit count as a proxy for timeouts;
it is the timeout attributed to the decision that caused it.

#### The controller-enforced run set

Record this for the same reason as the audit set below. The current cells come
from the balanced Full arm,
`data/ablation_sampling/48U_metrics_<condition>_0803_{1,2}.xlsx`, with:

- both parts pooled, which is the run set RQ1(a) uses, per section 4.3.1;
- runs delimited by a `ppSequenceId` reset, per section 3.2;
- identical run signatures counted once;
- shots after 30 of each run excluded.

That yields 70 runs / 2,100 captures at 12MP normal and 73 runs / 2,116 captures
at 24MP memory pressure; two 24MP captures carry no Filter decision, so the
Single-frame denominator is 2,114. `scripts/rq2_admission_metrics.py` regenerates
the cells.

These replace an earlier unbalanced pool of `ML/data/0727/` workbooks whose
timeout-bearing runs were dropped, and the two are not directly comparable: the
Full arm holds ten runs per starting overheat level Lv0–Lv6 while the 0727 pool
was weighted towards the hot levels. Standardizing on an equal weight per level,
the Multi-frame admit rate moves 72.1% → 59.9% at 12MP and 56.0% → 60.5% at 24MP,
so the change is not only a change of level mix. The Full export carries no
Capture-Timeout session, per the collection gap in section 4.3.1, so the
successful-admit denominator counts only the sessions present in the export.

### 5.3 Always-admit audit metrics

The audit forces optional work to execute while a shadow controller records
the fresh model decision it would make before applying session-sticky
demotion. This supplies factual outcomes for both model-admitted and
model-skipped work without attributing later policy-carried skips to the model.

#### Score the decision as measured

Every cell in the audit block uses \(C\) and \(B\) exactly as recorded. Forcing
every optional node is part of the condition being measured, not an error to net
out: RQ2 scores the model's judgement on the decision it made, and the forced
suffix is the workload that decision was taken against.

It is tempting to subtract the work the same model rejected, since the audit ran
it anyway. Do not make that the label. It answers a different question — was the
whole decision set safe end to end — and a reviewer will read a metric that was
redefined in the model's favour. Report it instead as the outcome
interpretation of section 5.4, per decision, where it belongs and where the
counterfactual is visible as a counterfactual.

State plainly what the label does and does not mean. An unsafe-admitted decision
here is a model misjudgement under the audit condition. It is not a Capture
Timeout a shipped build would emit, because that build both enforces admission
and arms the per-node watchdog, and the audit does neither.

#### All-decision confusion matrix

```text
                      Shadow model decision
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

The confusion matrix uses `afterModelAdmit` for every capture-level selected
Bokeh or Filter decision; it is not restricted to the first skip in a run.
It does not use `afterEffectiveAdmit`, because that field carries an earlier
group demotion through the remainder of the burst and would attribute
session-policy state to the fresh model decision.

#### The audit decision set

Record this explicitly, because the counts cannot be reproduced without it and
a later recomputation that silently uses a different set is indistinguishable
from a data change. The current cells come from
`48U_metrics_12MP_normal_0729_PacingOnly_{1,2}.xlsx` and
`48U_metrics_24MP_memory_0729_PacingOnly_{1,2}.xlsx` with:

- runs delimited by `ppSequenceId` reset, per section 3.2;
- shots after 30 of each run excluded;
- identical run signatures counted once, since the updated 12MP workbook 1
  contains every run of workbook 2;
- one manifest exclusion, source run 16 of the 24MP workbook 1, which was
  invalid/incomplete.

That yields 659 captures from 34 unique 12MP runs and 827 captures from 53
included 24MP runs. Any change to this set must be recorded here before the
cells are regenerated.

#### Median margin and overrun for model-skipped work

Use the same capture-level model-skipped decisions
(`afterModelAdmit == false`) reported by the confusion matrix. Let \(D\)
denote the product Capture Timeout deadline. For a feasible skip, calculate
the normalized remaining-margin magnitude:

```text
feasibleSkipMarginPercent = 100 * (B - C) / D
```

For an unsafe skip, calculate the normalized budget-overrun magnitude:

```text
unsafeSkipOverrunPercent = 100 * (C - B) / D
```

The table reports the median (P50) within each positive-magnitude class, then
prefixes `+` to the feasible-skip margin and `-` to the unsafe-skip overrun to
expose their opposite directions. A large positive margin indicates severe
over-conservatism, whereas a larger-magnitude negative overrun indicates that
the rejection prevented a substantial deadline violation. The deadline
constant is internal and must not appear in the manuscript; report only the
normalized percentage, consistently with RQ1's Slack P5.

Because the confusion matrix already reports the feasible and unsafe skip
counts, the table does not repeat their proportions or sample sizes in the
median cells. These median values describe the typical capture-level decision effect; they
are not inferential estimates over independent runs.

### 5.4 RQ2 figure metrics: unsafe-admit spike anatomy

`figures/fig_rq2_unsafe_spike_anatomy.tex` characterizes every decision in the
unsafe-admit cell of the confusion matrix: factually unsafe, model-admitted,
drawn from the included runs only. It answers two questions per decision — how
far the measured cost exceeded the preceding capture and the model's own
bound, and which `PostExecutionMetrics` quantity accounts for that excess.

#### Preceding-capture baseline

For each unsafe admit, take the selected decision from the same workbook,
`runId`, and optional-work group with the largest `runShotIndex` below the
event's — that is, the capture immediately before it. Holding the run and group
fixed also holds the device, resolution, and memory condition fixed, so the
comparison isolates within-burst variation. Do not substitute a pooled or
global average.

The single preceding capture is the right baseline because the question the
figure asks is what the controller could have known: the predicted bound is
formed from what it had just observed, so averaging three earlier decisions
smooths away exactly the local state the model was reacting to. It also makes
panel (b) a comparison of two real captures rather than of one capture against
a synthetic mean, which keeps the decomposition below exactly equal to a
measured wall-time difference.

Record whether that preceding capture was itself a safe admit. If it was not,
the baseline carries an earlier overrun and the growth factor understates the
spike; say so rather than silently skipping to an earlier safe capture. In the
current workbooks all eight preceding captures are safe admits.

#### Node suffix

Every per-node quantity is summed over the *remaining* nodes of the capture:
node rows whose `nodeOrder` is at least the selected decision's `nodeOrder`,
taken in `nodeOrder` order. This is the suffix that \(C\) measures in wall time,
so the panels and the label describe the same execution.

#### Panel (a): overshoot against the budget

Plot three x values per decision, each divided by that decision's own
`beforeBudgetMs`:

```text
baseline = C of the preceding capture
bound    = beforeSequencePredictedUpperBoundMs
event    = C
```

Draw the bound marker after the baseline marker. Where the two nearly coincide
the bound must stay visible, because that coincidence is the figure's sharpest
evidence that the model had no warning.

with \(C\) as defined in section 5.2. Normalize by \(B\), not
by the deadline \(D\): this places the admission criterion at exactly 1.0 and
keeps the internal deadline constant out of the figure. Because \(B\) is the
time left to the deadline, every event past 1.0 is also a Capture Timeout. The
annotated growth factor is
`event C / preceding-capture C`.

#### Panels (b) and (c): the two measured quantities behind the latency

Panel (a) shows that the remaining sequence took longer. Panels (b) and (c)
answer why by plotting the two measured quantities whose quotient is that
latency, each before and after, using the same previous/this-capture markers as
panel (a).

Over the node suffix:

```text
cpu   = sum(cpuTimeMs)            panel (b): how much CPU work it needed
wall  = sum(wallTimeMs)
cores = cpu / wall                panel (c): how many cores served it
wall  = cpu / cores               identically
```

`cores` is average busy cores: CPU time consumed per unit of wall time. Below
1.0 the remaining sequence progressed no faster than a single-threaded
execution, so mark 1.0 on the axis. Node wall time covers 97.5 to 99.0 percent
of the panel (a) latency in the current workbooks, so the two panels account
for essentially all of the increase; report that coverage whenever the
workbooks change.

**Plot the measured quantities, not a decomposition of the time difference.**
An earlier version of this figure plotted the exact additive split

```text
cpuTerm  = (cpu_e - cpu_p) / cores_p
coreTerm = cpu_e * (1 / cores_e - 1 / cores_p)

cpuTerm + coreTerm = wall_e - wall_p
```

as a stacked bar in milliseconds. The identity is correct and the numbers are
worth keeping in the figure's comment header for the prose, but "the time added
by getting a smaller share of the cores" is a counterfactual construct, not
something the trace recorded, and readers stall on it. CPU time went from
1,687 ms to 2,379 ms and the cores serving it went from 1.96 to 1.18 needs no
such explanation.

This formulation needs no machine core count. `cpuUtilizationRatio` is recorded
as `cpuTimeMs / (wallTimeMs * cores)`, so the physical core count only rescales
`cores` uniformly; recover it as
`round(cpuTimeMs / (wallTimeMs * cpuUtilizationRatio))` if a utilization
percentage is wanted for the text. The S26 Ultra workbooks give 8.

Take the suffix sums from the **per-node sheets**, not from `AdmissionReplay`.
`AdmissionReplay` holds a row only for nodes that carried an admission
decision, so summing it silently omits, for example, `DynamicFunctionNode` and
the second `SecImageCodecNode` pass, and understates both `cpu` and `wall`.

#### What `cpuTimeMs` covers

`CpuProcessingTracker` documents its run-queue and context-switch counters as
thread-level and its CPU-usage counter as not thread-level. Consistently with
that, `cpuTimeMs` regularly exceeds `wallTimeMs` for the same node (2,117 ms of
CPU over a 1,669 ms window in the largest Multi-frame spike). Read `cpuTimeMs`
as the camera process's total CPU consumption during the node window, not as
the node thread's own work, and read `cpuTerm` as added CPU demand inside the
process — which includes concurrently executing Draft work.

#### Control signals to recompute, not assume

Report the same baseline-versus-event comparison for `overheatLevel`,
`thermalStatus`, `blockingGcTimeMs`, `runQueueWaitMs`, and
`nonvoluntaryCtxSwitches`. In the current workbooks the first three separate
nothing — thermal state is identical to the baseline in all eight cases and
blocking GC time is zero throughout — while the last two move in both
directions. That asymmetry is the figure's argument and the reason a static
thermal threshold cannot anticipate these decisions, so it must be recomputed
whenever the workbooks change rather than carried forward.

#### Outcome interpretation: would this have shipped as a timeout?

\(B\) is the time left to the deadline, so an unsafe admit is a capture that
overran its deadline in the recording. A shipped build would not necessarily
have emitted it, because the audit removes two safeguards at once. Report both
per decision, as an annotation on the figure rather than as a change to the
label:

**W — the per-node watchdog.** The audit suppresses it so that admitted work can
be measured to completion, but `onWatchdogArmed` still records the budget, so
this is a comparison, not a guess. The watchdog wraps one OPTIONAL node with
`budgetMs` less the predicted upper bound of the sequence's RESERVED work:

```text
W  <=>  decision node durationMs > that node's watchdogTimeoutMs
```

Test the node that carried the decision under test. Ignore nodes the model would
have skipped: their recorded budget is often zero only because the forced prefix
had already consumed the deadline, and they would not run at all.

**B — the model's own decision set.** Honour the fresh model's skips on both
sides of the comparison. Work it rejected after the decision leaves the cost;
work it rejected *before* the decision shortens the path to it and therefore
raises that decision's budget:

```text
C_model = C - durations of guarded nodes after  the decision that the model skipped
B_model = B + durations of guarded nodes before the decision that the model skipped
B       <=>  C_model <= B_model
```

Removing a node also removes its contention, so `C_model` is an upper bound and
`B_model` a lower bound: a B verdict is conservative. Neither correction
propagates to the queue the earlier shots left behind, which only a sequential
replay would model, so a decision carrying neither W nor B is not proof of a
shipped timeout — only the absence of these two defences.

In the current workbooks every one of the eight unsafe admits carries at least
one verdict, and the three carrying only W are the three that are over budget
even on the model's own decision set.

#### Row labels

Rows are `M1`--`Mn` for Multi-frame and `S1`--`Sn` for Single-frame decisions,
ordered by growth factor descending within each group. The labels are
positional and will move if the data changes, so record the
(workbook, `runId`, `runShotIndex`) triple for each label in the figure's
comment header, together with the implementation commit the workbooks came
from.

### 5.5 RQ2 workbook mapping

Primary sheet:

- `AdmissionReplay`

Supporting completion timestamps may also be read from `PacingReplay`. The
section 5.4 figure additionally reads the per-node sheets, one per node class
(`SecDualBokehNode`, `DynamicFunctionNode`, `SecFilterNode`,
`SecImageCodecNode`, `WatermarkNode`) — that is, every sheet other than
`AdmissionReplay`, `PacingReplay`, `RQ3Pacing`, `RQ3Summary`, `ReplayNotes`,
and `Capture`.

| Purpose | Sheet | Columns |
|---|---|---|
| Run and capture identity | `AdmissionReplay` | `captureIndex`, `ppSequenceId` |
| Selected decision row | `AdmissionReplay` | `admissionStage` (`Bokeh` or `Filter`), `nodeOrder`, `workloadKey` |
| Factual decision | `AdmissionReplay` | `beforeEffectiveAdmit` |
| Shadow model decision | `AdmissionReplay` | `afterModelAdmit` |
| Shadow effective-policy decision (not used by the RQ2 audit) | `AdmissionReplay` | `afterEffectiveAdmit` |
| Remaining budget \(B\) | `AdmissionReplay` | `beforeBudgetMs` |
| Selected decision time | `AdmissionReplay` | `nodeStartUptimeMs` |
| Timeout deadline | `AdmissionReplay` | `timeoutDeadlineUptimeMs` |
| Watchdog outcome | `AdmissionReplay` | `beforeWatchdogTimedOut`, `beforeCaptureWatchdogFailed` |
| Capture Timeout outcome | `AdmissionReplay` | `beforeCaptureTimedOut` |
| Decision audit labels | `AdmissionReplay` | `beforeDecisionOutcome`, `beforeDecisionObservationStatus`, `afterDecisionOutcome`, `afterObservationStatus` |
| Draft completion | `PacingReplay` | `captureIndex`, `draftEndUptimeMs` |
| Predicted bound, section 5.4 panel (a) | `AdmissionReplay` | `beforeSequencePredictedUpperBoundMs` |
| Node suffix selection, section 5.4 | per-node sheets | `captureIndex`, `nodeOrder`, `nodeName` |
| Latency decomposition, section 5.4 panel (b) | per-node sheets | `wallTimeMs`, `cpuTimeMs`, `cpuUtilizationRatio` |
| Control signals, section 5.4 | per-node sheets | `runQueueWaitMs`, `nonvoluntaryCtxSwitches`, `blockingGcTimeMs`, `overheatLevel`, `thermalStatus` |

Do not use `beforeSequenceActualDurationMs` as \(C\). It sums node durations
and does not include the whole remaining wall-clock path to Draft completion.

The detailed historical aggregation convention is recorded in
`data/rq2_metrics_aggregation.md` in the ML implementation repository.

## 6. RQ3: Coordination-aware pacing-delay appropriateness

### 6.1 Current research question and evidence

> Does the controller compute an appropriately sized pacing delay for the Draft
> backlog and Capture Timeout budget?

The current main-paper design evaluates the deployed controller rather than
ranking it against pacing methods transplanted from unrelated domains. The
compact evidence chain is: targeted activation, trace-level boundary diagnosis,
an admission-aware envelope partition, observed admission action within the
two-Draft horizon, work conservation, and responsiveness cost. The authoritative
handoff is `docs/rq3-current.md`.

For measured backlog $B$, remaining deadline window $T$, realized admitted-Draft
duration $C_{exec}$, and mandatory-only duration $C_{mand}$:

```text
d_exec = ceil(max(0, B + 2*C_exec - max(0,T)) / 2)
d_mand = ceil(max(0, B + 2*C_mand - max(0,T)) / 2)
```

Positive realized-work envelopes are partitioned into pacing-covered
($d >= d_exec$), admission-flexible ($d_mand <= d < d_exec$), and below-floor
($d < d_mand$) transitions. The $2C$ horizon comprises the Draft that begins
after the pacing decision and the next capture's Draft released by that delay.
Accordingly, target-or-next demotion audits actual admission action on either
Draft in the horizon; it does not causally attribute the next admission decision
to the current delay.

Timeout-labelled records removed from the current collection are known invalid
measurements, not actual timeout outcomes. No valid analyzed run experienced an
actual Capture Timeout, so this population must not be called
survival-conditioned. Watchdog-truncated transitions are omitted from envelope
reconstruction because they lack a complete realized Draft duration.

The existing factual trace cannot support a valid 0.5x or 0.75x scaled-delay
counterfactual: changing one delay changes later backlog, admission, thermal
state, throttling, and realized work. Such a study requires new matched runs or
a validated closed-loop replay/simulator. Do not mechanically rescale the delay
column. Do not make domain-mismatched policy comparison the default RQ3 baseline.

Current artifacts are `tables/tab_rq3_pacing_compact.tex`,
`figures/fig_rq3_pacing_compact.tex`, and the generated CSVs documented in
`data/rq3/coordination/README.md`. The older policy, selectivity, calibration,
trajectory, and four-policy aggregation material below is retained only as
historical design context and must not drive the current manuscript.

### 6.H Historical four-policy RQ3 material (retired)

Everything from this heading through the historical RQ3 workbook mapping is
retained for provenance only. It does not define the current RQ3.
#### 6.H1 Historical summary-table metrics


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

#### Real backlog

At a decision timestamp \(t_i\), the exporter reconstructs:

```text
realBacklogMs_i
    = max(draftEndUptimeMs of unfinished earlier Drafts) - t_i
```

If no earlier Draft is unfinished, backlog is zero. Use measured Draft
timestamps, not `controllerBacklogMs`, for the paper outcome.

The artifact retains \(B_{\max}\), the maximum valid `realBacklogMs` across all
included runs, for audit. The main table omits it because a non-failing run
cannot exceed the Capture Timeout budget and therefore forces the maximum to
saturate just below that budget.

#### \(Q_{\max}\)

At a decision timestamp, `realQueueDepth` counts unfinished earlier Drafts
whose `draftStartUptimeMs` is later than the timestamp. It therefore counts
Drafts waiting to start and excludes a Draft that is already running.

\(Q_{\max}\) is the maximum valid `realQueueDepth` observed across all
included runs for that device-policy pair.

`realOutstandingDraftCount` includes the running Draft as well, but it is an
audit column rather than the paper's \(Q\) metric.

#### \(\bar{B}\), \(B_{50}\), \(B_{95}\), \(\bar{Q}\), and deadline-risk exposure

\(B_{\max}\) and \(Q_{\max}\) are extreme-value statistics. With eight or nine
runs per policy each is decided by one run, and real backlog cannot exceed the
Capture Timeout budget without the capture failing. The main table therefore
replaces \(B_{\max}\) with \(B_{50}\). It retains \(Q_{\max}\) because the
maximum number of waiting Drafts is a direct integer-valued queue bound.

Report the backlog distribution pooled over every included shot of a
device-policy pair:

```text
Bmean = mean(realBacklogMs)
B50   = PERCENTILE.INC(realBacklogMs, 0.50)
B95   = PERCENTILE.INC(realBacklogMs, 0.95)
Qmean = mean(realQueueDepth)
RiskExposure = 100 * count(realBacklogMs > 0.8 * captureTimeoutMs)
                   / count(realBacklogMs)
```

Report \(B_{\mathrm{mean}}\), \(B_{50}\), and \(B_{95}\) in milliseconds in
the main table.

`RiskExposure` is the share of the burst spent in the deadline-risk region.
Take
`captureTimeoutMs` from `PacingReplay`; do not hard-code the budget. State the
0.8 fraction in the table notes because it is a reporting choice, not a
measured constant.

#### Slack P5 and S2S P95

```text
Slack P5 = PERCENTILE.INC(timeoutMarginMs, 0.05)
S2S P95  = PERCENTILE.INC(shotToShotTimeMs, 0.95)   # shots 2..30
```

Also record the 30-shot span, `sum(shotToShotTimeMs)` over shots 2..30 per run,
as a run-level median. Comparing the span difference against the median `sum d`
separates delay from any other source of slowdown: if the two agree, the whole
measured responsiveness cost is the pacing delay itself.

#### 6.H2 Historical audit-only diagnostics

The following diagnostics are retained in `rq3_metrics.json` for artifact
inspection. They are not reported in a main-paper table because they do not
provide a baseline comparison and require substantial explanation to interpret.

**Targeting.** Split the transitions of one policy by `transitionDelayMs > 0`
and compare the state each group saw:

```text
B paced/unpaced = median(realBacklogMs | paced),
                  median(realBacklogMs | unpaced)
sum d at B>=P75 = 100 * sum(transitionDelayMs where realBacklogMs >= P75)
                       / sum(transitionDelayMs)
trigger B/L     = count of beforeDominantDeficit over paced transitions
```

A state-blind policy produces equal paced and unpaced medians and spreads its
delay evenly across backlog quartiles.

**Magnitude.** `realQueueWaitMs` is the measured time until the Draft pipeline
is next free, so it is the physical quantity the delay is trying to cover:

```text
d/w = PERCENTILE.INC(transitionDelayMs / realQueueWaitMs, 0.50)
      over paced transitions
```

A value below one means the policy defers the next capture by less than the
pipeline actually needs, which is the direct evidence against over-pacing.

**Estimator calibration.** The delay is derived from the controller's own
occupancy estimate, so report that estimate's error against the measured value:

```text
clock error = beforeBacklogMs + beforeShutterElapsedMs - realQueueWaitMs
```

A positive median means the estimate is conservative. **A build whose pacer does
not run never maintains `beforeBacklogMs`** — every AdmitOnly transition records
0 — so leave the calibration cells undefined for such an arm rather than
reporting a disabled estimator as a policy property. Check
`beforeBacklogMs` for all-zero before computing this row.

#### 6.H3 Historical figure metrics

For every `(device, policy, shot)` group, compute the inclusive P10, median,
and P90 of:

- `realBacklogMs`;
- `realQueueDepth`;
- `transitionDelayMs`.

For the pacing-activation panel, compute one percentage per shot:

```text
activationRate_i
    = 100 * count(transitionDelayMs_i > 0)
            / count(nonblank transitionDelayMs_i)
```

Zeros remain in the denominator. This is a cross-run rate for one outgoing
shot transition, not the magnitude of the applied delay.

For cumulative delay, first compute the cost experienced within each run:

```text
cumulativeDelay_i = sum(transitionDelayMs_j) / 1000
                    for j = 1, ..., i - 1
```

The shot-\(i\) value excludes the delay recorded on shot \(i\), because that
delay gates shot \(i+1\). After this within-run accumulation, compute the
cross-run median, P25, and P75 for each shot.

The policy CSV schema is:

```text
shot,
backlog_median,backlog_p10,backlog_p90,
queue_depth_median,queue_depth_p10,queue_depth_p90,
delay_median,delay_p10,delay_p90,
activation_rate_percent,
cumulative_delay_median,cumulative_delay_p25,cumulative_delay_p75
```

The panels mean:

| Panel | Metric | Interpretation |
|---|---|---|
| Backlog vs. shot | Per-shot real-backlog median | Whether queued processing time accumulates during the burst |
| Pacing activation vs. shot | Per-shot share of runs with positive delay | When and how consistently each policy intervenes |
| Cumulative delay vs. shot | Within-run cumulative applied delay | How much user-visible pacing cost has accumulated by each shot |
| Total delay vs. backlog P95 | One point per complete run | Whether lower tail backlog requires excessive pacing cost |

The backlog panel draws medians only. Queue-depth and applied-delay P10/P50/P90
columns remain available in the CSVs and summary artifact, but queue depth is
not repeated as a trajectory panel because it conveys the same accumulation
pattern as backlog in the space-constrained `0.215\textwidth` panel. The
pacing-activation panel instead exposes when a policy actually intervenes.

**This rule is scoped to the cross-run trajectory panels and does not carry to
the case-study figure.** Pooling medians over runs is what makes backlog and
queue depth look alike: the two accumulate together on average. Within a single
session they separate, because admission and pacing act on different terms.
Backlog is the *time* queued and falls when admission makes each Draft cheaper;
queue depth is the *count* queued and falls only when arrivals stop outrunning
service. In the selected 12MP session the two part company over captures
23--30, immediately after the \(S\) demotion: real backlog drops from 63.8% to
27.6% of the deadline while the queue stays at five or six. Backlog
alone reads as "the session recovered"; the pair shows that the queue never
shortened and only became cheaper to serve, which is the coordination claim the
case study exists to make. `figures/fig_casestudy_12mp.tex` therefore carries a
queue-depth strip, reading the `queue_depth` column of
`data/case_study/<condition>_backlog.csv`. Keep
the strip in any case-study figure that shows a demotion; drop it only if a
future session shows the two moving together throughout.

That column counts the Draft in service as well as those waiting -- the
`realOutstandingDraftCount` convention noted under \(Q_{\max}\) in section 6.2,
not `realQueueDepth`, which excludes the running Draft and therefore reads one
lower wherever one is running (four or five over the same captures). The
committed file is not reproduced by `scripts/export_casestudy.py`: the exporter
can only write the waiting-only count, and it also has no value for the shot-2
backlog the file carries, so it leaves an existing backlog CSV in place unless
`CASESTUDY_WRITE_BACKLOG=1` is set. Quote five or six for the figure and four
or five for `realQueueDepth`, and name the column whenever the number appears.
The cumulative-delay panel draws policy medians and IQR bands for the arms
whose traces are currently available because run-to-run pacing cost is central
to its interpretation. After all four arms are populated, verify that four
bands remain legible; if they do not, retain all policy medians in the figure
and move every policy's IQR to the artifact rather than showing uncertainty
for only a subset of policies.

`transitionDelayMs` and `activation_rate_percent` are blank at shot 30, because
the delay recorded on shot i gates shot i+1 and shot 30's outgoing transition
falls outside the 30-shot window. Only over-length runs carry a delay there, so
emit `nan` for both shot-30 fields rather than pooling a different set of runs
at the last point. The cumulative-delay value at shot 30 nevertheless remains
defined: it is the sum of the 29 eligible delays on shots 1--29. Backlog and
queue depth also remain defined at shot 30.

#### 6.H4 Historical run-level cost--tail trade-off panel

This panel reports one point per included complete run:

```text
RunTotalDelay
    = sum(transitionDelayMs_i, i = 1, ..., 29) / 1000

RunBacklogP95
    = PERCENTILE.INC({realBacklogMs_i | i = 1, ..., 30}, 0.95) / 1000
```

Use the same run inclusion and deduplication rules as the summary table. Every
point must therefore contain 30 real-backlog observations and exactly 29
eligible outgoing-transition delays.

The per-policy artifact schema is:

```text
run,total_delay_s,backlog_p95_s
```

Plot total delay in seconds on the x-axis and run backlog P95 in seconds on the
y-axis. Movement toward the lower left indicates a better cost--tail trade-off.
Do not claim policy dominance from an arbitrary scalarization of the two axes,
or from unmatched admitted workloads.

This continuous panel remains discriminative when timeout and fixed-threshold
risk rates collapse to zero for every paced policy. The pooled thresholded
deadline-risk metric remains in Table VI, and its per-run values remain in
`risk_exposure_runs.csv` and the generated JSON under `nearDeadlinePercent` for
artifact compatibility and run-level statistical analysis.

`backlog_cost.csv` remains in the artifact for secondary cost--backlog
inspection, but it is not plotted in the main paper figure. Its schema is:

```text
no_pacing_delay_s,no_pacing_max_backlog_s,
thermal_lut_delay_s,thermal_lut_max_backlog_s,
codel_inspired_delay_s,codel_inspired_max_backlog_s,
ours_delay_s,ours_max_backlog_s
```

#### 6.H5 Historical RQ3 workbook mapping

Primary sheets:

- `RQ3Pacing`: per-shot and per-transition values;
- `RQ3Summary`: run-level audit and preliminary summaries;
- `PacingReplay`: decision-time context, joined to `RQ3Pacing` by
  `captureIndex`, for the outcome and decision-quality metrics.

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
| Deadline budget | `PacingReplay.captureTimeoutMs` |
| Delivered margin | `PacingReplay.timeoutMarginMs` |
| Measured time-to-free | `PacingReplay.realQueueWaitMs` |
| Controller occupancy estimate | `PacingReplay.beforeBacklogMs`, `beforeShutterElapsedMs` |
| Delay trigger | `PacingReplay.beforeDominantDeficit` |
| Shot-to-shot time | `RQ3Pacing.shotToShotTimeMs` |

Use `RQ3Pacing` to produce final cross-run percentiles. `RQ3Summary` is useful
for validation, but its run-level P50/P95 values must not be pooled or averaged
to approximate the event-level P50/P95.

## 7. Historical four-policy pre-collection checks (retired)

These checks are retained for the retired comparison design. Current compact-RQ3 validity and regeneration rules are in `docs/rq3-current.md`.

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

### 7.4 Keep admission fixed (historical comparison only)

The four pacing policies must receive the same admitted workload sequence.
Otherwise, a policy may appear to control backlog simply because Admission
removed more work, and RQ3 would no longer isolate pacing ability.

## 8. Output files to populate

### Paper tables

- `tables/tab_rq1_ablation.tex`
- `tables/tab_rq1_result.tex`
- `tables/tab_rq2_admission_summary.tex`
- `tables/tab_rq3_pacing_compact.tex`

### RQ2 figure

- `figures/fig_rq2_unsafe_spike_anatomy.tex` — self-contained; the per-decision
  values and the decomposition inputs are recorded in its comment header, so no
  companion CSV is emitted. Regenerate it from section 5.4 whenever the RQ2
  workbook set changes.

`tables/tab_rq2_admission_summary.tex`, come from `data/rq2_spike_anatomy.mjs`
in the ML implementation repository, which is the single place the
\(C_{\mathrm{model}}\) rule of section 5.3 is implemented:

```text
node data/rq2_spike_anatomy.mjs
```

### Current RQ3 figure and generated evidence

- `figures/fig_rq3_pacing_compact.tex`
- `docs/tab_rq3_pacing_compact_preview.png`
- `docs/fig_rq3_pacing_compact_preview.png`
- `data/rq3/coordination/summary.csv`
- `data/rq3/coordination/envelope_share.csv`
- `data/rq3/coordination/action_summary.csv`
- `data/rq3/coordination/flexible_cases.csv`
- `data/rq3/coordination/mandatory_floor_cases.csv`
- `data/rq3/coordination/avoided_delay_12mp_normal.csv`
- `data/rq3/coordination/avoided_delay_24mp_memory.csv`

Regenerate the current RQ3 evidence from the repository root:

```text
python3 scripts/rq3_policy_metrics.py sampling  # requires openpyxl
python3 scripts/rq3_coordination_metrics.py
python3 scripts/rq3_coordination_audit.py
python3 scripts/render_rq3_compact_preview.py
```

Do not edit generated CSV cells by hand. See
`data/rq3/coordination/README.md` for their schemas and interpretation.
The complete cross-session transfer checklist is `docs/rq3-file-manifest.md`.

## 9. Current manuscript issues to resolve before final submission

1. `_4_experiments.tex` still contains unrelated placeholder research
   questions and is disabled in `paper.tex`; the actual RQ1--RQ3 wording must
   be added to the manuscript.
2. The current RQ3 table and figure name S26 Ultra and S26. If the evaluation
   uses Device A/B/C, both artifacts and their data directories must be
   updated consistently.
3. The known timeout-measurement fault and invalid-record manifest must be
   described in the final evaluation protocol. No valid analyzed run timed out;
   do not characterize the filtering as survival conditioning.
4. The historical RQ1 aggregation note describes Slack P5 in milliseconds,
   whereas the current paper table labels and comments define a
   deadline-normalized percentage. This guide follows the current paper:
   normalize each event first and then calculate P5.
5. Any deviation from the aggregation rules in this document must be recorded
   before inspecting comparative outcomes.
6. The RQ1 `N = 10` balancing protocol (section 4.3.1) was applied *after* the
   outcomes were known and scores runs on those outcomes. It must be presented
   as a post-hoc balancing choice with its direction of bias stated, not as a
   predeclared exclusion — or replaced with an outcome-neutral rule.
7. Full-arm timeout-labelled records affected by the known measurement fault are
   invalid observations, not actual Capture Timeout sessions. Preserve the
   invalid-record manifest and do not present their removal as outcome filtering.

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
