# Implementation map

Where the manuscript gets its implementation facts. The implementation lives in the
private repository `https://github.com/ParkMinhyun/ML`; the Section 3 source map
below was read at commit `cdd524f`. Re-verify against the latest accessible working tree
before writing new implementation-derived text, and record the hash you used.

`AGENTS.md` gives the lookup order for the working tree (`external/ML/`, then a
sibling `../ML/`, then a path in `LOCAL_CONTEXT.md`).

## Section 2 rewrite verification (2026-09-05)

The rewrite of Sections 2.2-2.4 used the local paper at
`ef180d31a776581491f33d77e9b976ba49931aa8` and the clean implementation working
tree at `bb27a0fdc145ab0d6ba7883039a84a1024b951c9`. No synchronization was
performed, as requested by the user. The style source is separately recorded
in `docs/writing-style.md`.

- `external/draftSaving/SavingDraftImageTaskManager.java` creates a single-thread
  scheduled executor and submits Draft tasks to it. This verifies serialized
  Draft execution in the normal processing flow.
- `external/ProcessingPhotoMakerBase.java` receives the HAL capture-availability
  callback; `external/PhotoMakerBase.java` routes its delivery toward the
  application, including the pacing policy. This is separate from Draft task
  completion. The common outstanding-capture limit is not a claim of unlimited
  parallel capture.
- `WorkloadKey.kt` identifies optional Bokeh, Filter, overlay Watermark, and
  conditional Decoding stages, and the mandatory Encoding tail through Draft
  saving. The manuscript's optional single-frame stages do not imply that every
  Watermark variant is optional.
- Draft/post-processing introduction history, foreground deferral for selected
  modes, the visual gap in Portrait mode, the production level-4 safeguard,
  model-selection rationale, and the motivating failure and trial protocol
  remain author-reported facts from the existing manuscript. The accessible
  implementation excerpt does not independently establish those product and
  validation-history claims.
- On 2026-09-05, the author clarified the development history: the original
  Draft Sequence saved incoming JPEG input without decoding or re-encoding;
  the subsequent extension decoded JPEG input to apply single-frame stages
  before encoding and saving; the multi-frame extension received multiple YUV
  inputs for lightweight multi-frame composition. This chronology is
  author-reported. The clean implementation at
  `bb27a0fdc145ab0d6ba7883039a84a1024b951c9` contains compatible JPEG
  passthrough (`SavingDraftImageTask.java`, `SavingSingleDraftImageTask.java`),
  decoding (`WorkloadKey.kt`), and multi-frame processing paths, but does not
  independently establish their introduction order. Encoding is mandatory for
  the extended configurations in the motivating experiment, not a stage that
  the original JPEG-saving sequence necessarily executed.
  At the author's request, Section 2.3 presents this evolution through the
  added processing stages; image formats and conversion steps remain here
  as verification detail rather than background exposition.
- The author also confirmed on 2026-09-05 that the motivating experiment
  used the same ADB request protocol described in `4_1_setup.tex`: request
  each subsequent capture as soon as the application permits it through
  capture availability. This is author-confirmed experimental procedure,
  not an inference from controller-evaluation traces.
- `tables/tab_timeout_index.tex` supplies the existing motivating measurements.
  Its entries are earliest timeout indices across ten trials grouped by
  **starting** thermal level, not the level at failure. The prose comparison of
  configurations concerns these reported earliest indices, not paired outcomes
  for individual trials. The trial-level exports are unavailable in the local
  evidence collection, as documented in `docs/rq-evidence.md`; no new statistics
  were derived for this rewrite.

## Section 3.2 wording verification (2026-09-15)

The wording reviews on 2026-09-15 and 2026-09-16 used the clean local implementation at
`27d296795eab702ff3c4f38da64ac8720cd082cf`, without synchronization.
`DraftSequenceExecutionPredictor.kt` verifies the update order: baseline
observations are divided by the shared factor available before the update,
and the new factor uses observed-to-baseline ratios computed from the
baselines available before the update. Only existing positive baselines
contribute ratios; without any ratios, the shared factor remains unchanged.

`external/draftSaving/SavingDraftImageTaskManager.java` retains the predictor
across queue drains while resetting admission and pacing state. At the author's
request, Section 3.2 omits this lifetime detail and the forward reference to
admission, and condenses the update explanation to the cumulative baseline
average, the median factor update, and the median's purpose. The
previous statement that histories are discarded only after application close
and completion of all queued Draft Sequences was removed: the accessible
manager does not explicitly clear the predictor, and its shutdown can stop
waiting before all queued work completes. The full application-close path
is not present in this implementation excerpt.

## Section 3.3 residual eligibility verification (2026-09-15)

Rechecked on 2026-09-15 and 2026-09-16 against the clean local implementation at
`27d296795eab702ff3c4f38da64ac8720cd082cf`, without synchronization.
`DraftSequenceExecutionPredictor.kt` first filters observations to positive
durations, then restricts each recorded decision sequence to those measured
keys. It computes a residual only when the recorded predictions for that
measured sequence have a positive sum, and keys the sample by that sequence.
The manuscript's residual formula therefore uses the measured sequence as
`\(\mathcal K\)`; the previous condition requiring every key of the original
decision sequence to have a positive observation was too restrictive.
Within one capture, `distinctBy` retains the first factor for each measured
sequence before inserting it into the sequence history and global pool.

The 2026-09-16 wording review also checked `DraftSequenceExecutionSession.kt`:
the watchdog bounds the wait before fallback, and timed-out execution can
continue detached. Section 3.3 therefore describes the framework's waiting
interval rather than a hard limit on stage execution. The fallback uses the
preserved original input; the accessible code does not establish a separate
copy-allocation step. The empirical quantile selector's role in setting the
target percentile is distinguished from decay's role in reducing the influence
of older observations.

## Section 3.4 pacing update verification (2026-09-15)

The Section 3.4 reviews on 2026-09-15 and 2026-09-16 use the clean local implementation at
`27d296795eab702ff3c4f38da64ac8720cd082cf`, without synchronization.
Compared with the earlier `cdd524f` reference:

- `CaptureAvailablePacingSession.observeBacklogGrowthMs` learns signed
  differences between successive backlog estimates with a recency-weighted
  mean, then clips that mean at zero. It returns zero before any difference
  is available. Negative differences are retained in the history.
- `CaptureAvailablePacer.computePacingDelayMs` adds this growth once to the
  two-sequence projection and caps the rounded half-deficit at the floor of
  one reserve plus growth, in milliseconds. The timeout window is already
  clamped to its valid range by the session.
- The duration reserve now reads `RecencyWeightedDistribution.expectedMaximum`:
  a weighted quantile at `n_eff / (n_eff + 1)`, using the effective sample size
  of the positive whole-sequence duration observations. This is an
  empirical quantile, not the largest observation or a guaranteed bound.
  The empty history reads zero. All these histories use weight decay `0.90`.
  Its lifetime changed on 2026-09-16; see the note below.
- The reserve floor and backlog occupancy include the predictor's overhead
  estimate. `DraftSequenceExecutionPredictor` learns it as the recency-weighted
  mean of nonnegative whole-sequence duration minus measured stage time.
  The provisional clock adds the ceiling of stage time plus overhead from
  the last start snapshot, rounding the sum once.
- Starts refresh the snapshot and consume the pending decision. Completion
  updates the predictor before `endDraftSequence` rebuilds the clock from
  the current time and pending decisions. It uses current duration estimates
  for their recorded stage compositions, adds current overhead per sequence,
  and rounds the total once. It does not reapply current admission demotion
  to the queued compositions. A skipped sequence consumes its pending
  decision; clock correction waits until completion.

The 2026-09-16 prose revision explicitly distinguishes recording
`\(\hat P^{\mathrm{last}}\)` at sequence start from reconstructing
`\(t^{\mathrm{end}}\)` at completion. A queued entry's recorded composition
comes from the snapshot used for its pacing decision; reconstruction uses
updated duration estimates for those recorded keys, not newly resolved
compositions for the queued sequences.

On 2026-09-16, the author requested removing the backlog-growth symbol,
formula, and explanations from Section 3.4, including the growth term and
the entire one-reserve-plus-growth cap from `eq:pacing`. The displayed delay
is now the ceiling of half the positive deficit computed from backlog plus
two sequence reserves. This supersedes the same day's notation change that
grouped backlog and growth under `eq:backlog`. The implementation still
includes growth and the cap described above; this is a manuscript omission,
not a code change.

At the author's subsequent request, Section 3.4 omits the separate overhead
symbol and all related prose. Its displayed reserve and backlog-update formulas
show only the stage-time point estimates; the implementation still adds the
overhead described above. The definition of `\(\hat P\)` in Section 3.2 is unchanged.

The growth history ends when the pacing session is cleared; the predictor's
overhead estimate survives queue drains. This source check updates the method
description only and does not establish which controller version produced the
existing evaluation workbooks.

### Duration-reserve history lifetime (2026-09-16)

At the author's direction, the whole-sequence duration history behind
`\(C_\tau\)` moved from `CaptureAvailablePacingSession` to
`DraftSequenceExecutionPredictor` in `ML@80cd230`, the child of `27d2967`.
The author judged clearing the history when the queue empties unjustified.

- `DraftSequenceExecutionPredictor.learnFromCapture` records each positive
  whole-sequence duration, with the same decay-then-add update as before, and
  `estimateReservedDraftSequenceDurationMs` returns its `expectedMaximum`.
  `learnFromCapture` runs exactly once per completion of a draft that started,
  because `ModelUpdateBuffer.drainOnce` returns its samples only on the first
  call. `DraftSequenceExecutionProfiler.completeDraftSequenceExecution` skips
  it when `initialize` never ran (a capture completed on a watchdog drain
  without starting a draft), which previously passed a zero duration with no
  workload samples and taught nothing. The positive-duration guards were
  removed accordingly; the overhead trend still ignores a sequence with no
  measured stage time.
- `CaptureAvailablePacer.clear()`, called at queue drain and at pipeline
  close, still drops the session (FIFO, backlog clock, deadline, growth
  history) but no longer affects the duration history. The history lives as
  long as the predictor, which `SavingDraftImageTaskManager` owns as a final
  field, alongside the residual histories and overhead estimate.
- A completion now records its duration even when no pacing session is open.
  `CaptureAvailablePacer.endDraftSequence` takes no argument and only rebases
  the clock.
- `startDraftSequence` reads the predictor's estimate. The reserve still
  subtracts the stages excluded by the current demotion state, which now also
  re-projects durations measured under an earlier run's demotions.
- Section 3.4 defines `\(C_\tau\)` over completed draft sequence durations,
  with no queue-drain scope.
- The exporter's `observedMaxDraftMs` diagnostic still reconstructs a
  session-scoped observed maximum. It already described the superseded
  observed-maximum reserve and was not changed.
- Evaluation runs collected before this change used the session-scoped
  history, so Section 3.4 differs from those runs in this respect until the
  experiments are repeated.

## Section 3.5 integration verification (2026-09-16)

The merged rewrite of `3_5_implementation.tex` was checked against the clean local
implementation at `80cd230`, without synchronization.

- **Watchdog threading corrected.** Both earlier drafts described a
  "watchdog-fallback thread" that processes the preserved original input. The
  code does the reverse: `DraftSequenceExecutionSession.executeOnWorker` creates
  a single-thread executor for each admitted optional stage and the draft
  worker waits on it with the watchdog timeout. On expiry the draft worker
  itself continues to fallback while the stage keeps running detached. The
  manuscript therefore says "a worker thread created for that stage" and no
  longer counts "two threads". The late output is released through
  `releaseTimedOutResult`, and `DraftNodeChainLifecycle.deferUntil` defers
  stage-chain deinitialization until the detached stage finishes.
- **Callback delivery.** `CaptureAvailableApmPolicy` computes the delay on the
  calling thread and posts the callback to `SingleThreadDelayedScheduler`, one
  dedicated thread per policy instance. The interface is the single-method
  `CaptureAvailablePacingDecider`. `SavingDraftImageTaskManager.addRequest`
  republishes it through `AdaptivePerformanceManager.updateData` when a draft
  sequence is queued, not when it starts. The returned decision also carries a
  snapshot, but that snapshot is used only for logging. The manuscript's
  unavailable-interface sentence rests on `PhotoMakerBase`, where a missing or
  uninitialized policy runs the callback directly, and on the policy, which
  applies zero delay when no decider has been published.
- **Extensibility.** `WorkloadKey.policy` declares whether a key is optional.
  A new optional stage also needs node-to-key resolution in the profiler and
  membership in `AdmissionGroup.of`, whose exhaustive `when` enforces it; the
  manuscript condenses this to "defined and assigned to an admission group".
- **Device independence.** Thermal, memory, and storage snapshots enter
  `PreExecutionMetrics` as observability inputs only; neither the predictor nor
  the pacer reads them. `RecencyWeightedDistribution.WEIGHT_DECAY = 0.90` is a
  single constant, and no device-model branch exists in the controller sources.
- **Not established by the excerpt.** The predictor is an in-memory final field
  of the manager and is never persisted, but the manager's creation site is not
  in the excerpt, so a session-scoped learning claim would be author-reported.
  The sentence carrying it (fixed decay, reserve horizon, and halving versus
  per-session learning) was removed at the author's request on 2026-09-16;
  its fixed values remain stated in Sections 3.3 and 3.4. The product-branch
  and release-validation sentence is author-reported. The "cannot be cancelled once it enters native image processing"
  wording is likewise author-reported. The code agrees with it: interruption
  does not stop the detached stage.

## Section 3 sources

| Subsection | Sources | What they establish |
|---|---|---|
| 3.1 overview (`sec:objective`) | `DraftSequenceExecutionPredictor.kt`, `CaptureAvailablePacer.kt`, `DraftSequenceExecutionProfiler.kt` (`completeDraftSequenceExecution`) | The two modules, that neither passes numeric state to the other, and that both models are updated from measured durations at Draft Sequence completion |
| 3.2 workload model (`sec:model`) | `DraftSequenceExecutionPredictor.kt`, `WorkloadKey.kt`, `WorkloadSequenceKey.kt` | Key taxonomy, cumulative base duration, the shared condition factor updated from the latest sequence's median ratio, cold-start handling; reverified in the 2026-09-15 note above |
| 3.3 admission (`sec:admission`) | `DraftSequenceExecutionPredictor.kt` (residual factor, Kish selector, watchdog), `DraftSequenceAdmissionPolicy.kt` (sticky group demotion), `DraftSequenceExecutionProfiler.kt` (where a decision is taken) | Equations for the residual factor, upper estimate, admission test, and watchdog window |
| 3.4 pacing (`sec:pacing`) | `CaptureAvailablePacer.kt`, `CaptureAvailablePacingSession.kt`, `RecencyWeightedDistribution.kt`, `DraftSequenceExecutionPredictor.kt` | Backlog growth and completion-time rebase, weighted duration reserve, per-sequence overhead, and capped delay over the two-sequence horizon; reverified in the 2026-09-15 note above |
| 3.5 integration (`sec:implementation`) | `external/draftSaving/SavingDraftImageTaskManager.java` (ownership, single-thread executor, queue-drain boundary, decider publication), `external/apm/policy/CaptureAvailableApmPolicy.java` and `external/apm/util/SingleThreadDelayedScheduler.java` (callback release), `external/apm/data/PacingDeciderApmData.java` and `external/apm/repository/PacingDataRepository.java` (interface publication and reset), `external/PhotoMakerBase.java` (fail-open and immediate callback paths), `DraftSequenceExecutionSession.kt` and `DraftSequenceExecutionProfiler.kt` (per-stage watchdog worker, deferred deinitialization), `WorkloadKey.kt` and `DraftSequenceAdmissionPolicy.kt` (extension points) | Where the controller attaches, what it costs, which paths bypass it; reverified in the 2026-09-16 note above |
| Instrumentation | `CaptureMetrics.kt` and the `CaptureMetrics*` store/export classes | What a recorded decision contains, and that the metrics store is study-only |

`DraftSequenceExecutionProfiler.kt` also carries the stage classification that
decides which stages are optional, so it backs both 3.3 and the \(M\)/\(S\)
notation 2.4 introduces.

## These names stay out of the manuscript

The table above is provenance, not vocabulary. No class, field, or method name
from it may appear in printed manuscript text -- prose, table cells, figure
labels, or captions. Section 3.5 once transliterated the ownership graph
(`the Draft-saving manager owns the predictor, the admission policy, and the
pacer`); it was rewritten on 2026-08-20. For current writing guidance, consult
`docs/writing-style.md` and the terminology rules in `AGENTS.md`; the old
section-specific style instructions have been removed.

Two identifiers are deliberate exceptions, because the manuscript needs to name
the interface it paces rather than an internal component:

- `captureAvailable`, set in `\texttt{}` in 2.2 and 3.1. It is the HAL-to-
  application callback the controller defers, and 2.2's argument does not work
  without naming it.
- Nothing else. In particular the overview figure
  (`figures/fig_controller_interaction.pdf`) still carries `decideDelay` and
  `decideAdmission` as the labels above the two module boxes; those are real
  method names (`CaptureAvailablePacer.kt:16`,
  `DraftSequenceExecutionPredictor.kt:28`). Neither string appears in any `.tex`
  file, so a reader meets them in the figure with nothing in the prose to
  attach them to -- which is the whole reason for this rule.

  Replace them with `delay sizing` and `live-budget admission`. Both are
  verbatim run-in headings from 3.4 and 3.3, so the figure names each operation
  with the title of the subsection that explains it. Use `stage admission` for
  the right-hand one if the longer label has to wrap. Do not reuse the outcome
  wording already on the arrows: the labels above the modules name the
  operation, while `delay` on the capture timeline and `admit / skip` at the
  optional stages name what arrives. The deck is maintained as
  `figures/fig_controller_interaction.pptx` and exported to
  `fig_controller_interaction.pdf`, which is what `3_1_overview.tex` includes;
  editing the labels therefore needs the export redone, not just a text change.
  (`scripts/build_controller_figure.ps1`, named here until 2026-08-21, does not
  exist.)
