# Naive recent-N baseline replay (2026-09-22)

Question (advisor): what goes wrong if the controller simply uses the mean of
the last N completed draft sequences instead of the current method?

Sources: the four full-controller workbooks that RQ4 uses
(`data/S26_Ultra/SM-S948U_metrics_12MP_normal_0906.xlsx`,
`data/S26_Ultra/SM-S948U_metrics_24MP_memory_0906.xlsx`,
`data/S26/SM-S942B_metrics_12MP_normal_0906.xlsx`,
`data/S26/SM-S942B_metrics_24MP_memory_0829.xlsx`).
The predictor port follows `ML@b6712a0` (working tree, with a local change to
`CaptureAvailablePacer.kt` only; the predictor files were clean).

## Run order

```
python load.py          # workbooks -> wb.pkl
python partA.py         # open-loop forecasts at every recorded decision -> adm.pkl, pac.pkl
python validate.py      # port reproduces recorded P-hat and U
python runsim.py late   # per-run capture timelines -> prep_late.pkl
python runsim.py early
python val2.py          # simulator + ported controller reproduce the recorded trace
python arms.py late     # closed-loop admission replay, all estimators
python arms.py early
python summarize.py late early
python sens.py          # imputation sensitivity (min / median of 5 nearest)
python tables.py        # CSVs under out/  (copies are in results/)
# follow-up: stage-wise naive (sum of each remaining stage's recent-N statistic)
python arms_stage.py late          # summary_stage_late.csv (kept as results/B_stage_naive_arms.csv)
python arms_stage_margin.py        # additive margin sweep (results/B_stage_naive_margin_sweep.csv)
python arms_stage_scale.py         # multiplicative factor sweep (results/B_stage_naive_scale_sweep.csv)
python partA_stage.py              # open-loop coverage, and U/P-hat by condition
python shadow.py                   # shadow U / P-hat at naive admissions that ended in a miss
# follow-up: the same estimators as pacing inputs
python partC_pacing_arms.py        # eq:pacing with swapped inputs (results/C_pacing_arms.csv)
python partC_pacing_stage.py       # stage-wise naive as a pacing input (results/C_pacing_stage.csv)
# pacer port and joint replay
python val_pacer.py                # delay formula per workbook (100% on 6,135 decisions)
python val_pacer_clock.py --reserve=auto [--own-deadline --lag=N]   # pacer bookkeeping
python joint.py                    # joint closed-loop prep -> joint_prep.pkl (not usable, see below)
```

`naive-brief.html` is the short version for the advisor. It rests the case on
admission's residual (Part B, the residual case and the 40 / 42 shadow count)
and presents pacing as designed around admission -- the shared predictor and
the half-deficit division -- rather than as more accurate than naive pacing:
with B and C estimated separately (draft mean-3 backlog, draft max-5 reserve)
a naive pacer matches the deployed inputs on the one-step comparison
(`results/C_pacing_factorial.csv`). `naive-summary.html` carries the detail.

## What each layer is and is not

- Part A (open loop): forecasts scored against realized time-to-draft-end
  (`draftEnd - nodeStart`) or realized backlog on the recorded trace. No
  counterfactual.
- Part B (closed-loop admission replay): capture requests, draft-ready times,
  pacing delays, session boundaries (`pacerSessionId`) and non-stage time are
  pinned to the trace; only the admission estimator changes. Stages the recorded
  controller skipped take the nearest executed duration of that stage in the same
  run. COMPLETE_30 runs only (226 runs, 6,780 captures). This is a
  TRACE_CONDITIONED_ESTIMATE in the workbook's own terminology, not a factual
  arm. Pacing is frozen at the recorded delays, which were sized for the recorded
  workload; thermal feedback and the watchdog are not modeled.
- Part C (pacing, one step): the manuscript's `eq:pacing` evaluated with swapped
  inputs at each recorded decision. A closed-loop pacing comparison is not
  identifiable from these exports (the app cadence and the gate cannot be
  separated), so no pacing counterfactual outcome is claimed.
  `partC_pacing_arms.py` runs the same estimator grid as Part B through the rule
  and reports engagement, delay per run, and the backlog/reserve decomposition.
  Three limits: the rule is the manuscript form (no growth term, no cap), so even
  the deployed inputs reproduce the recorded delay only in engagement (94.7% /
  91.2%) and undershoot its magnitude (2.6 / 3.6 s per run against a recorded
  3.8 / 5.7); the `not_engaged_when_ref_did` reference is the same rule fed
  realized backlog and realized two-sequence durations, i.e. a retrospective
  matched-policy target, never a required or minimum delay, and its inputs were
  measured under the deployed pacing; and the admission miss counts it is plotted
  against in `naive-summary.html` come from the Part B closed-loop replay
  (114 / 112 runs), a different layer from these pacing decisions (116 / 116 runs). Runs are
  counted per (device, runId): runIds repeat across the two devices, and an
  earlier count by runId alone (63 / 67) inflated every per-run delay by
  about 1.8x; ratios between arms were unaffected.
  `partC_pacing_stage.py` adds the stage-wise estimator in the same two slots.
  A stage sum is not a draft wall, so it needs two extra choices that the
  draft-unit statistic never has to make -- which composition to assume for a
  sequence that has not run, and what to do about non-stage time -- and the
  script sweeps both. The planned chain prices in stages admission will skip
  (backlog +457 ms median at 24MP) and the newest executed composition inherits
  skips that already happened (-135 ms); both leave 28-34% of the reference
  engagements unmet, so the error is in targeting rather than level. Restoring
  non-stage time on the executed composition reproduces the draft-unit arm to
  within 0.1 s per run, which is the point: the decomposition that fixes
  admission buys nothing here. It recomputes the draft-unit arms itself so the
  whole table shares one population (2,947 / 3,000 decisions; 2 decisions fewer
  at 24MP than `C_pacing_arms.csv`, which lacks node rows).

## Pacer port (added for the joint naive arm)

`port_pacer.py` ports CaptureAvailablePacer and CaptureAvailablePacingSession;
`val_pacer.py` validates it. `port.py` covers the admission path only, so there
was no deployed pacing baseline before this.

Structure follows `ML@bb27a0f`. Two differences from the current implementation
matter and must not be read back into it. There is **no delay cap** (`27d2967`
added one). And the per-draft reserve is an upper statistic of the session's
observed draft walls whose exact form differs by device: on S26U it is the
running **maximum** (reproduced within 10 ms on 97.5-98.5% of decisions), while
on S26 neither the running maximum nor the recency-weighted `expectedMaximum`
that `44a9a32` introduced reproduces it cleanly -- `expectedMaximum` fits S26 12MP
better (66% vs 36% within 10 ms) and the running maximum fits S26 24MP better.
`port_pacer.Pacer(reserve_stat=...)` carries both. The reserve history is
session-scoped, as `AGENTS.md` already notes for runs collected before
`ML@80cd230`.

**The delay formula differs between workbooks, and not the way the file names
suggest.** Determined by measurement, not by commit date:

| workbook | delay form | reproduces |
|---|---|---|
| S26U 12MP 0906, S26U 24MP 0906, S26 12MP 0906 | `ceil((deficit + growth) / 2)` | 100.0% |
| S26 24MP 0829 | `ceil(deficit / 2 + growth)` | 100.0% |

The second form is the post-`8d5e55d` one ("Stop halving the queue growth with
the deficit", 2026-09-03), so the 0829-named workbook carries the *newer*
formula and the 0906-named ones the older. Whatever the file names mean, they
are not the build date. Each form reproduces only its own workbooks (the other
form scores 54-63%), so the split is measured, not fitted.

Validation, on all 6,135 recorded decisions across the four workbooks:
`estimatedCompletionTimeMs` and `deadlineDeficitMs` reproduce at 100% from the
recorded B, C and T; replaying the growth estimator over the recorded
per-decision backlog sequence within each `pacerSessionId` reproduces
`appliedDelayMs` exactly at 100%, p90 error 0 ms. Only the decision path is
covered -- the backlog clock and the reserve are fed from the trace here and
need their own event replay.

Consequence for scoping: **12MP normal is formula-clean across both devices;
the 24MP condition pools two different delay formulas.** Anything that treats
the deployed pacing as one system should be scoped to 12MP, which is also the
condition `AGENTS.md` scopes RQ4 to.

### Event replay of the pacer's own bookkeeping (`val_pacer_clock.py`)

`val_pacer.py` fed the backlog and the reserve from the trace, so it validated
only the delay formula. `val_pacer_clock.py` replays the recorded event stream
and makes the pacer compute them itself; the trace supplies only timestamps,
node chains, realized durations and capture deadlines.

Four bugs in the replay harness, not in the port, accounted for nearly all of
the first-pass gap (engagement 23.6% simulated against 37.0% recorded). Each
was found by splitting the error rather than by guessing:

1. **Every captureAvailable callback is an event**, including the 216 + 23 the
   export marks `SESSION_BOOTSTRAP_ZERO` / `NO_GATING_DECISION_ZERO` and carries
   no decision for. They queue nothing, but the first of them opens the pacing
   session; without it the session opened a capture late and the whole FIFO was
   shifted by one. Queue depth went from 22-62% exact to 94-99%. The tell: with
   depth exact, backlog error was already 6 ms median, so all of it came from the
   short queue.
2. **`startDraftSequence` takes the full configured chain**, read from the node
   rows -- not the trace's `plannedWorkloadSequenceKey`, which is already the
   demoted projection. Passing the demoted key makes `resolveDraftSequenceKey` a
   no-op, so `estimateDemotedWorkloadDurationMs` returns 0. The tell: reserve
   error was 2 ms median on undemoted sequences and +450 ms on demoted ones.
3. **The session boundary and the deadline registration are separate events.**
   An earlier harness cleared the session inside the deadline handler, so lagging
   the deadline also lagged the clear.
4. **The pacer registers a capture's deadline one capture late** (below). The
   live hook races the callback and the export does not record the outcome.

The snapshot sequence key (sticky demotion + snapshot timing) matched throughout
(98.8-100%), and the predictor point estimate and learned overhead sit within
2-3 ms of the recorded columns (~0.4%).

With the recorded `timeToDeadlineMs` fed in and the reserve statistic chosen per
workbook, 12MP normal (3,050 decisions): queue depth exact 98.1%, backlog error
median 8 ms / p90 15 ms, reserve 1 / 45 ms, delay p90 15 ms, and engagement
agreeing on **99.1%** of decisions (34.4% simulated against 34.7% recorded).
Advancing the backlog clock on the recorded delay instead (`--anchor`) changes
nothing, so none of this is feedback from the port's own delay.

Running the port's own deadline clock instead, over the registration lag:

| lag | ttd err med / p90 | delay err p90 | engagement agreement | engaged |
|---|---|---|---|---|
| 0 | 694 / 1,885 ms | 464 ms | 75.0% | 10.1% |
| 1 | 0 / 1,286 ms | 191 ms | 90.0% | 26.3% |
| 2 | 623 / 1,244 ms | 519 ms | 88.5% | 37.8% |

against 34.7% recorded. The backlog, reserve and queue columns are identical
across the three, as they should be. Lag 1 is the best single model, and **lags
1 and 2 bracket the recorded engagement rate**. The race is not recoverable as
a rule; `joint.py` pins the recorded choice per transition instead, which is
defensible because both sides of the race are camera-side timing.

24MP is worse because of one workbook: S26 24MP (the 0829 one) reproduces at
90.6% engagement agreement with backlog p90 918 ms, while S26U 24MP is at 96.9%
and 44 ms; pooled 24MP is 93.9%. It also pools two delay formulas, so the joint
replay was run on 12MP only.

### Joint closed-loop replay (`joint.py`): built, not usable

`joint.py` swaps the admission and pacing estimators separately or together in
one event-driven simulator, so the three cases would share one metric set.

What is identified. The ADB loop presses the shutter as soon as
`captureAvailable` arrives (`4_1_setup.tex`), and the trace shows the chain
directly: request -> camera latency L (12MP median 271 / 207 ms, S26U / S26,
p10-p90 within ~60 ms) -> callback and pacing decision -> delay d -> release ->
eps (362 / 281 ms) -> the very next capture's request (100%). Each pair of
consecutive requests carries one recorded callback, or none at a session
bootstrap. Replaying the recorded delays and recorded admits reproduces every
request, draft start and draft end to within 7 ms and every margin exactly.
The deadline a decision prices against is a camera-side race (capture commit vs
callback), so the recorded choice is pinned per transition.

What is not. With the deployed pacer deciding for itself, the baseline breaks:

| 12MP, S26U / S26 | miss | delay per run |
|---|---|---|
| recorded delays + recorded admits | 0 / 0 | 3.9 / 3.6 s |
| deployed admission + recorded delays | 0 / 0 | 3.9 / 3.6 s |
| recorded admits + deployed pacer | 99 / 102 | 4.3 / 4.0 s |
| deployed admission + deployed pacer | 3 / 15 | 2.9 / 3.1 s |

against 0 / 0 recorded. The cause is draft readiness: a capture that queued
behind the previous draft has only an upper bound on when its frames were
ready. Taking the bound (`lead_mode='late'`) means extra delay can never let
that capture start sooner after its request, so shortfalls ratchet into misses;
capping it at the idle-lead p5 (`'early'`) sends the stage execution rates to
88-99% against a recorded 68-70%. One unobserved quantity decides the result,
so no joint number is reported. `naive-brief.html` case 3 pairs case 1's miss
with case 2's delay for the same setting instead, and says so.

**Retraction.** An earlier version of this file and of `naive-summary.html`
said that 68-86% of paced captures had "pass-through 1", i.e. that the delay
became the shot-to-shot interval one-for-one. That was not a measurement. The
exporter defines `shotToShotWithoutRecordedPacingMs` as the measured interval
minus the delay, clipped at 0 (`CaptureMetricsExcelExporter.kt`), and its own
ReplayNote says it "is not a factual no-pacing arrival trace" after the first
divergence. The ratio was only the share of rows whose interval is at least
the delay. The arrival chain above replaces it.
