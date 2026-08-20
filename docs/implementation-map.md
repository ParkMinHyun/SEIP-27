# Implementation map

Where each part of Section 3 gets its facts. The implementation lives in the
private repository `https://github.com/ParkMinhyun/ML`; every claim below was
read at commit `cdd524f`. Re-verify against the latest accessible working tree
before writing new implementation-derived text, and record the hash you used.

`AGENTS.md` gives the lookup order for the working tree (`external/ML/`, then a
sibling `../ML/`, then a path in `LOCAL_CONTEXT.md`).

## Section 3 sources

| Subsection | Sources | What they establish |
|---|---|---|
| 3.1 overview (`sec:objective`) | `DraftSequenceExecutionPredictor.kt`, `CaptureAvailablePacer.kt` | The two modules, and that neither passes numeric state to the other |
| 3.2 workload model (`sec:model`) | `DraftSequenceExecutionPredictor.kt`, `WorkloadKey.kt`, `WorkloadSequenceKey.kt`, `RecencyWeightedDistribution.kt` | Key taxonomy, cumulative base duration, the shared condition factor and its `0.90` decay, cold-start handling |
| 3.3 admission (`sec:admission`) | `DraftSequenceExecutionPredictor.kt` (residual factor, Kish selector, watchdog), `DraftSequenceAdmissionPolicy.kt` (sticky group demotion), `DraftSequenceExecutionProfiler.kt` (where a decision is taken) | Equations for the residual factor, upper estimate, admission test, and watchdog window |
| 3.4 pacing (`sec:pacing`) | `CaptureAvailablePacer.kt`, `CaptureAvailablePacingSession.kt` | Backlog clock and its rebase, the reserve refresh, the delay formula and its `2C` horizon |
| 3.5 integration (`sec:implementation`) | `external/draftSaving/SavingDraftImageTaskManager.java` (ownership, single-thread executor, queue-drain boundary), `external/apm/policy/CaptureAvailableApmPolicy.java` and `external/apm/util/SingleThreadDelayedScheduler.java` (callback release), `external/PhotoMakerBase.java` (fail-open and immediate callback paths) | Where the controller attaches, what it costs, which paths bypass it |
| Instrumentation | `CaptureMetrics.kt` and the `CaptureMetrics*` store/export classes | What a recorded decision contains, and that the metrics store is study-only |

`DraftSequenceExecutionProfiler.kt` also carries the stage classification that
decides which stages are optional, so it backs both 3.3 and the \(M\)/\(S\)
notation 2.4 introduces.

## These names stay out of the manuscript

The table above is provenance, not vocabulary. No class, field, or method name
from it may appear in printed manuscript text -- prose, table cells, figure
labels, or captions. Section 3.5 once transliterated the ownership graph
(`the Draft-saving manager owns the predictor, the admission policy, and the
pacer`); it was rewritten on 2026-08-20. `docs/writing-style.md`, section
"Section 3.5, naming the integration points", records the full removal list and
the replacement wording rule.

Two identifiers are deliberate exceptions, because the manuscript needs to name
the interface it paces rather than an internal component:

- `captureAvailable`, set in `\texttt{}` in 2.2 and 3.1. It is the HAL-to-
  application callback the controller defers, and 2.2's argument does not work
  without naming it.
- Nothing else. In particular the overview figure
  (`figures/fig_controller_interaction.pdf`) still carries `decideDelay` and
  `decideAdmission` as region labels; those are real method names
  (`CaptureAvailablePacer.kt:16`, `DraftSequenceExecutionPredictor.kt:28`) and
  should be replaced with action wording when the deck is next rebuilt with
  `scripts/build_controller_figure.ps1`.
