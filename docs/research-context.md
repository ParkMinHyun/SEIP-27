# Research Context

This document is the shared research context for writing the paper. Use it before drafting or revising the motivation, preliminaries, approach, methodology, and implementation discussion.

## Core Framing

This research is a prototype for preventing Capture Timeout in the Android Camera Framework.

The Draft Sequence was introduced together with the full post-processing pipeline. It saves and publishes an early image while final processing continues, and it provides a recovery result if final processing fails. It is not a later workaround added because final processing became slow.

The target is the portrait-mode Draft Sequence. As post-processing became more compute- and memory-intensive, selected expensive shot modes began deferring full composition until the camera application entered the background to protect foreground usability. This made the draft visible for longer. Portrait final composition originally ran in the foreground, but the introduction of lightweight multi-frame Draft Bokeh made it possible to expose an approximate portrait early and defer the heavier final portrait composition to the background. Depending on the situation, the draft path may include Bokeh, Dynamic Function, Filter, Watermark, and Encoding.

The central problem is not reducing the average execution time of one image-processing stage. The problem is tail-latency-based Capture Timeout: multiple ordered stages must finish within a strict deadline, but device state and runtime variability can cause normally acceptable stages to spike and miss the deadline.

The implementation studies this problem through a Context-Aware Draft Sequence Controller with two control points. Remaining-sequence admission changes how much optional work the current capture executes. Capture-availability pacing delays the opportunity for the next capture so admitted draft backlog can drain. Pacing improves future budget but increases shot-to-shot latency, which must be reported as an explicit trade-off.

The key question is not whether the current stage alone is fast on average. The key question is whether the queued and remaining Draft work can finish before the timeout deadline under a conservative upper-bound estimate, and whether a model-derived pacing delay is needed before admitting another capture.

## Motivation

Capture Timeout is a release-blocking failure. The fail-fast mechanism is active in both development and production builds, so a violation crashes the camera application. User-reported crashes from deployed products are analyzed and corrected. Even a rare timeout can block product release if it is reproducible. From the user's perspective, it can appear as shooting failure, camera freeze, camera crash, failure of subsequent captures in continuous shooting, or missing capture results. This makes the problem a product stability and release-readiness issue, not merely a performance optimization issue.

Draft processing evolved in three steps:

1. The initial Draft Sequence performed no imaging effect; it encoded and saved selected input for early access and recovery.
2. Single-frame Filter and Watermark were added because untreated drafts differed visibly from final results with those effects. An initial safeguard skipped optional Draft work at level 5 and above after timeouts clustered at high overheat levels. Later, during pre-release validation of one model, a device at level 4 experienced a Capture Timeout after thermal throttling delayed one single-frame Draft stage. The timeout recurred at the same level despite workload reduction and code optimization. Rather than special-case that stage, engineers lowered the common cutoff to level 4 and disabled all optional Draft stages at and above that level. Because the Draft control path is shared across models and the policy has no model-specific condition, every model inherited the same cutoff. The framework reevaluates the guard at each Draft Sequence start, so a sequence beginning after the level rises to 4 skips all optional image-processing stages. Level 4 can arise under common conditions, including repeated capture, high ambient temperatures, charging, and preceding device workloads.
3. Increasingly heavy post-processing made background-deferred composition more important and kept the draft visible longer. Portrait was selected for lightweight multi-frame Draft Bokeh because its before-after difference is large. The richer draft also enabled heavy final portrait composition to move from foreground runtime to background-deferred execution. The multi-frame stage was implemented for supported models, but the timeout behavior in the Section 2.4 trials prevented safe production enablement under the current framework architecture. In the manuscript, describe it as a developed production candidate without directly discussing its release status unless that distinction is required for accuracy.

The remaining Capture Timeout problem is closer to a tail-latency problem than an average-latency problem. Many obvious optimizations may already be applied, such as splitting bottleneck paths into separate threads, early return, early initialization, lazy processing, logic simplification, zero-copy paths, removing unnecessary decode or encode, and removing duplicated work. The remaining failures are often caused by state-dependent runtime factors, including thermal throttling, CPU scheduling delay, DVFS changes, memory pressure, blocking GC, storage or I/O delay, DB insert delay, provider return delay, lower-service response delay, and continuous-capture backlog.

Existing defenses are often accumulated as scattered guards rather than designed as a centralized policy. A typical pattern is a thermal-level guard such as:

```kotlin
if (thermalLevel >= 4) {
    return
}
```

Thermal level is useful, but it is an imperfect proxy for timeout risk. The same thermal level can imply different risks depending on storage condition, previous encode latency, background workload, throttling behavior, and device class. This causes both false negatives, where a low thermal level still times out, and false positives, where a high thermal level unnecessarily skips a feature.

Thermal-guard conservatism can also spread fleet-wide. In this project, an initial level-5 guard was tightened to level 4 after a lower-tier Filter timeout and became a common-path restriction that also applies to flagship devices. This historical guard did not cause the Draft Bokeh enablement failure. Rather, it demonstrates that the existing policy is not a viable enablement policy for the new workload: every sequence beginning at level 4 or above loses all optional Draft processing, even though some captures can complete that work. Conversely, the forced-on trials show that simply removing the guard and always executing the workload is unsafe.

Draft Sequence makes over-conservatism especially visible. The draft image is often the first result the user sees after capture. If Filter or Bokeh is skipped in the draft but appears later in the final image, the user observes draft-final inconsistency. In continuous capture, independent per-shot decisions can also create shot-to-shot decision jitter, where similar shots unexpectedly have different effects.

Draft features should not be judged independently. The stages have an order and a cost relationship. The correct admission question is:

```text
If the current stage is executed,
can the remaining Draft processing sequence complete
before the timeout deadline?
```

Admission alone cannot recover budget already consumed by queueing. Capture pacing can let backlog drain before the next capture begins, preserving more optional processing, but it increases the shot-to-shot interval. Therefore, this research treats Capture Timeout prevention as coordinated runtime control over ordered workload sequences and capture arrivals, not as a per-stage latency prediction problem.

## Static-Guard Motivation Experiment

The Section 2.4 motivation table characterizes the two limitations that must be resolved to make the lightweight multi-frame Draft stage M eligible across the full thermal range. The static guard unconditionally removes optional work from every Draft Sequence beginning at level 4 or above, while an always-on alternative can time out as parallel capture accumulates backlog at the single Draft worker. The table uses S948U, the highest-performing model in the evaluation, to test the always-on risk even on the most capable hardware. This model's parallel-capture path has no additional queue-length cap. The table reports ten 30-shot continuous-capture trials for each combination of starting Overheat Level (0--6), resolution, memory condition, and Draft Sequence configuration. In the level-4 incident, the backlog reached 12 pending Draft Sequences at approximately the 20th continuous capture; the 30-capture horizon covers that observed state with a conservative margin. A validation build forces M to execute and bypasses the deployed guard condition so the candidate workload runs at every starting level. Memory-pressure trials launch the camera while the memory-stress workload in AnTuTu Benchmark 11.1.4 is active; record the reset procedure before submission.

Each table cell reports the earliest and median first-timeout indices. A `--/--` entry means that no timeout occurred within the 30-capture horizon. The measured 12MP M+S medians are computed from all trial blocks in `8U_metrics_NEW.xlsx`, grouped by starting Overheat Level, and displayed as nearest-integer indices; the number of recorded trials varies by level. M-only and 24MP medians are provisional, not directly measured: they apply the measured 12MP M+S median-to-earliest ratio for the same memory condition and starting level to the cell's retained earliest value, then round half up. Normal Levels 0--1 use the nearest available Normal ratio at Level 2, and memory-pressure Level 0 uses the Level 1 ratio. A `>30` estimate is right-censored at the measurement horizon. Pending Draft count and worker waiting vary by resolution and memory condition, so the 30-capture length is a common sustained-load horizon, not a fixed proxy for backlog count or cost.

The table rows record the Overheat Level at trial start, not necessarily the level at the failing capture. During continuous capture, the level can rise and impose additional throttling before a later capture reaches the Draft worker. Because the guard is bypassed, a trial that begins below the cutoff characterizes forced-on workload risk rather than a failure that the deployed guard would necessarily admit. Do not describe a failure as occurring below the deployed cutoff unless a per-capture log confirms that the reported level remained below the cutoff at failure.

The product-level timeout contract was described by the author as beginning with the application's accepted capture request and ending after frame and metadata collection and Draft-image generation. The currently accessible `ML` prototype at commit `21397f966b53d2266152a5776c8400cc04a8e8a8` anchors its recorded timeout timestamp at the shutter callback. Treat this as a product-contract versus prototype-instrumentation distinction that must be reconciled in the methodology rather than silently assuming the timestamps are identical.

## Writing the Motivation

When turning the motivation above into manuscript text:

- Present the motivation as an academic problem, not as a personal anecdote.
- State accurately that Draft and final post-processing were introduced together.
- Treat the level-5-to-level-4 guard chronology as internal context only; do not include it in the manuscript. Describe the deployed level-4 guard as a pragmatic release safeguard that does not scale to flagship Draft Bokeh, and do not claim that the guard caused the Bokeh enablement failure.
- Connect the motivation to limitations of average-latency optimization, single-stage decisions, thermal-only guards, and admission-only control under accumulated backlog.
- Treat pacing delay and the resulting shot-to-shot slowdown as an explicit cost, not as a free stability improvement.
- Make the gap concrete before introducing the proposed technique.
- Do not invent origin stories, experimental evidence, or reviewer/advisor comments.
- If the motivation is still incomplete, ask the user for the missing concrete trigger before writing a full introduction.

## Device State And Runtime Observation

A natural first idea is to use device state directly as prediction features, such as overheatLevel, thermalStatus, thermalHeadroom, ramAvailablePercent, javaHeapUsedPercent, nativeHeapAllocatedPercent, vmRssPercent, and isLowMemory.

However, the target is a framework-level predictor that must work across many Android device models. Direct device-state prediction has limitations:

- the meaning of the same thermal level differs across devices;
- thermal throttling and DVFS behavior are nonlinear;
- a snapshot before a stage cannot explain events that occur during the stage;
- per-model feature engineering is hard to maintain in common framework code.

For this reason, device state is important for logging and offline analysis, but the primary runtime prediction signal is observed workload execution history: actual workload durations and residuals.

## Key Preliminaries

Capture Timeout is the situation where a capture request or draft result delivery fails to complete within a deadline.

```text
deadlineMs = internal product deadline
elapsedMs = currentTime - captureStartTime
remainingBudgetMs = deadlineMs - elapsedMs
```

The numeric Capture Timeout deadline is an internal product policy and must not be disclosed in the manuscript. Refer to it as a fixed product deadline. Describe Capture Timeout compliance as one of the product line's highest-priority camera reliability KPIs and a hard release gate: a reproducible violation blocks launch until the affected feature is fixed, restricted, or removed.

Draft Image is the intermediate image generated before the final post-processing result. It is not merely a preview; it is close to the first capture result the user sees.

Draft Sequence is the ordered processing path used to produce the draft image. Representative stages include:

```text
- Bokeh
- Dynamic Function
- Filter
- Watermark
- Encoding
```

Workload Policy divides workloads into three roles:

```text
ADMIT:
- workload requiring an admission decision before execution
- examples: Bokeh, Filter

OBSERVE:
- workload that runs and whose duration is observed
- examples: Dynamic Function, Watermark

COMPLETE:
- mandatory workload required to complete the draft sequence
- example: Encoding
```

Workload Key identifies the unit used to model stage duration. Representative keys include:

```text
Bokeh(sizeBucket)
DynamicFunction(sizeBucket)
Filter(sizeBucket)
Watermark(sizeBucket)
Encoding(sizeBucket, imageFormat, isPendingRequest)
```

`sizeBucket` groups resolutions into megapixel tiers such as MP12, MP24, MP50, MP108, and MP200. This avoids making samples too sparse by modeling every exact width and height separately.

Workload Sequence Key is an ordered sequence of workload keys. For example, from the Bokeh decision point:

```text
Bokeh(MP12)
-> DynamicFunction(MP12)
-> Filter(MP12)
-> Watermark(MP12)
-> Encoding(MP12, JPEG, false)
```

From the Filter decision point, the suffix sequence may become:

```text
Filter(MP12)
-> Watermark(MP12)
-> Encoding(MP12, JPEG, false)
```

Remaining Budget is the time left until the Capture Timeout deadline. Admission should compare the predicted upper bound of the remaining workload sequence against this budget.

Queueing Delay is the time between the start of a capture's timeout clock and the start of its Draft Sequence on the single Draft worker. Under parallel capture, queueing delay can consume substantial budget before the capture's own draft work begins.

Draft processing nodes are not shared across captures. The single-worker design is a production backpressure choice. To preserve the user-visible shooting order, Draft completion and storage must follow capture order. Concurrent Draft execution would require a reorder layer: later results that finish processing first would remain buffered until earlier Draft Sequences completed. It would therefore move waiting into a memory-resident reorder queue while making multiple Draft workloads compete with preview and capture. Serial execution preserves order and bounds active Draft compute and memory to one sequence. Do not claim that Draft Sequences are serialized because they share node instances, because the nodes are inherently not thread-safe, or because parallel execution is theoretically impossible.

Capture-Availability Pacing delays the `captureAvailable` callback that enables a subsequent shot. It uses the larger of two predicted deficits: the preferred-path shortage observed at the most recent Draft start and the shortage created by the backlog of callback-admitted captures. This lets already released capture work drain before the next capture starts. The delay is model-derived and zero when sufficient budget exists, but any nonzero delay postpones the earliest next-shot opportunity and can increase shot-to-shot latency. Applied callback delay and observed inter-shot timing must be evaluated separately.

The deadline relationship can be expressed as:

```text
queueingDelay(capture_i)
+ draftExecutionTime(capture_i, admittedWork)
<= captureTimeoutDeadline
```

Admission controls the execution-time term for the current capture. Pacing controls the future queueing term for subsequent captures.

## Prediction And Calibration

EWMA, or Exponentially Weighted Moving Average, is used as the point prediction for each workload:

```text
prediction(workload)
= exponentially weighted average of recent observed durations
```

EWMA tracks the current latency level from observed runtime behavior. Its purpose is not to explicitly model thermal curves, but to adapt to how slow the workload is becoming in practice.

Sequence point prediction is the sum of workload-level EWMA predictions:

```text
prediction(sequence)
= sum(prediction(workload_i))
```

This point prediction is not enough for timeout prevention because the important risk is how much actual duration can exceed the prediction.

Residual score captures that underprediction:

```text
score = max(0, ln(actualMs / predictedMs))
```

The score is positive only when actual duration exceeds predicted duration. The log-ratio form is preferred over absolute error because it is less sensitive to workload scale.

Residuals are recorded at the decision sequence level, not merely per workload. If an admission decision is made for a remaining sequence, the actual duration and residual should also be computed for that sequence. Contributions may be clamped as:

```text
contribution = max(decisionTimePrediction, actualDuration)
```

This prevents one stage's overrun from being hidden by another stage's underrun.

The upper-bound prediction combines EWMA and residual calibration:

```text
rawUpperBound(sequence)
= predictedMs(sequence) * exp(calibratedScore(sequence))
```

EWMA provides the current latency level, and residual calibration provides tail-risk adjustment.

Residual samples are time-decayed so old samples gradually lose influence:

```text
newWeight = oldWeight * decay
```

Effective sample size is computed as:

```text
ESS = (sum(w)^2) / sum(w^2)
```

The adaptive quantile can then be selected as:

```text
q = 1 - 1 / (ESS + 1)
```

This avoids overtrusting a high quantile when few effective samples exist, while allowing stronger tail-risk calibration as samples accumulate.

## Cold Start, Sparse Samples, And Watchdog

Cold Start means the predictor does not yet have enough runtime samples. Sparse Samples means a specific workload or workload sequence has too few samples. These situations occur after app start, after boot, on early builds of a new model, on first execution of a new feature, or on rare image size and format combinations.

If a sequence has no point prediction, the implementation should generally admit it first to collect actual duration and residual samples:

```text
if sequencePrediction.isColdStart:
    admit = true
```

This is not a claim that the feature is always safe. It is bootstrap observation: if the system always skips unknown workloads, it can never learn their actual cost.

When possible, sparse samples can be mitigated with priors:

```text
Exact workload model missing:
- use the slowest same-type workload prediction

Same workload type also missing:
- prediction = 0
- cold-start admit
- bootstrap after actual execution
```

If sequence-level residual samples are missing, a global residual prior can be used:

```text
sequence residual samples exist:
- use sequence-specific residual tail

sequence residual samples missing:
- use global residual tail
```

Watchdog fallback is still necessary, but it is a second line of defense. Admission decides whether to start an optional workload. Watchdog protects mandatory completion work if execution becomes too slow after a workload has started.

For ADMIT workloads, the watchdog should reserve budget for the remaining COMPLETE workload:

```text
watchdogTimeoutMs
= remainingBudgetMs - predictedUpperBoundMs(reserved COMPLETE sequence)
```

Watchdog-only is insufficient because native stages such as Bokeh may consume unrecoverable time once started. The paper should emphasize that admission before expensive optional work and watchdog during execution are complementary.

## Implementation Consistency Checks

When analyzing Kotlin source files from the private `ML` implementation, verify whether the implementation matches this direction:

- device state is not used as a strong direct prediction feature;
- workload-level EWMA provides point prediction;
- residual score calibrates sequence-level upper bounds;
- admission decisions are based on the remaining workload sequence, not a single workload only;
- pacing consumes the same draft-path predictions used by admission rather than an independent fixed interval;
- pacing accounts for the backlog of callback-admitted captures and delays `captureAvailable` only by the predicted deficit;
- pacing metrics include the applied delay so evaluation can report the shot-to-shot responsiveness cost;
- cold start uses admit-first observation rather than immediate thermal-guard skip;
- same-type workload priors and global residual priors mitigate sparse samples;
- watchdog fallback protects mandatory completion workload as a second line of defense.

Do not write paper claims that exceed what the implementation or user-provided context supports.
