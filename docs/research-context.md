# Research Context

This document is the shared research context for writing the paper. Use it before drafting or revising the motivation, preliminaries, approach, methodology, and implementation discussion.

## Core Framing

This research is a prototype for preventing Capture Timeout in the Android Camera Framework.

The target is the portrait-mode Draft Sequence. In portrait mode, the framework generates a draft image before the final post-processing result is ready, so the app or user can receive a fast intermediate result. Depending on the situation, this draft path may include Bokeh, Dynamic Function, Filter, Watermark, and Encoding.

The central problem is not reducing the average execution time of one image-processing stage. The problem is tail-latency-based Capture Timeout: multiple ordered stages must finish within a strict deadline, but device state and runtime variability can cause normally acceptable stages to spike and miss the deadline.

The implementation studies this problem through a Context-Aware Draft Sequence Admission Controller.

The key question is not whether the current stage alone is fast on average. The key question is whether the remaining workload sequence from the current point can finish before the timeout deadline under a conservative upper-bound estimate.

## Motivation

Capture Timeout is a release-blocking failure. In a mobile camera system, even a rare timeout can block product release if it is reproducible. From the user's perspective, it can appear as shooting failure, camera freeze, camera crash, failure of subsequent captures in continuous shooting, or missing capture results. This makes the problem a product stability and release-readiness issue, not merely a performance optimization issue.

The remaining Capture Timeout problem is closer to a tail-latency problem than an average-latency problem. Many obvious optimizations may already be applied, such as splitting bottleneck paths into separate threads, early return, early initialization, lazy processing, logic simplification, zero-copy paths, removing unnecessary decode or encode, and removing duplicated work. The remaining failures are often caused by state-dependent runtime factors, including thermal throttling, CPU scheduling delay, DVFS changes, memory pressure, blocking GC, storage or I/O delay, DB insert delay, provider return delay, lower-service response delay, and continuous-capture backlog.

Existing defenses are often accumulated as scattered guards rather than designed as a centralized policy. A typical pattern is a thermal-level guard such as:

```kotlin
if (thermalLevel >= 4) {
    return
}
```

Thermal level is useful, but it is an imperfect proxy for timeout risk. The same thermal level can imply different risks depending on storage condition, previous encode latency, background workload, throttling behavior, and device class. This causes both false negatives, where a low thermal level still times out, and false positives, where a high thermal level unnecessarily skips a feature.

Thermal-guard conservatism can also spread fleet-wide. A guard introduced for one low-performing or high-risk model can become a common-path restriction that also applies to high-performing devices. This creates fleet-wide over-conservatism and unnecessary feature skip.

Draft Sequence makes over-conservatism especially visible. The draft image is often the first result the user sees after capture. If Filter or Bokeh is skipped in the draft but appears later in the final image, the user observes draft-final inconsistency. In continuous capture, independent per-shot decisions can also create shot-to-shot decision jitter, where similar shots unexpectedly have different effects.

Draft features should not be judged independently. The stages have an order and a cost relationship. The correct admission question is:

```text
If the current stage is executed,
can the remaining Draft processing sequence complete
before the timeout deadline?
```

Therefore, this research treats Capture Timeout prevention as a runtime control problem over ordered workload sequences, not as a per-stage latency prediction problem.

## Writing the Motivation

When turning the motivation above into manuscript text:

- Present the motivation as an academic problem, not as a personal anecdote.
- Connect the motivation to limitations of average-latency optimization, single-stage decisions, and thermal-only guards.
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
deadlineMs = 7000ms
elapsedMs = currentTime - captureStartTime
remainingBudgetMs = deadlineMs - elapsedMs
```

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
- cold start uses admit-first observation rather than immediate thermal-guard skip;
- same-type workload priors and global residual priors mitigate sparse samples;
- watchdog fallback protects mandatory completion workload as a second line of defense.

Do not write paper claims that exceed what the implementation or user-provided context supports.
