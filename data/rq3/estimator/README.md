# RQ3 Estimator Artifact

Generated evidence for the compact RQ3 pair: what each pacing decision
required, what it got, and where the difference came from. Do not edit
generated CSV cells by hand.

## Generator

`scripts/rq3_estimator_metrics.py`, run from the repository root:

```text
python3 scripts/rq3_estimator_metrics.py
```

It uses only the Python standard library and reads the values-only XLSX exports
through ZIP/XML, reusing the loader and eligibility rules of
`scripts/rq3_coordination_metrics.py`.

## Why this directory exists beside `coordination/`

`coordination/` answers *which* decisions pacing covered. This directory answers
*why* the rest did not, and it recomputes the partition itself so that both
halves of the table come from one population and one pass. The two agree by
construction on the counts (79/140 required, 53/83 covered, 26/43 left to
admission, 0/14 below the floor); `coordination/` remains the source for the
admission-action and margin-decomposition audits.

## Quantities

All errors are signed **estimate minus realized**, so a positive value means the
controller reserved more than the pipeline used.

| Symbol | Meaning | Source column |
|---|---|---|
| \(d\) | applied pacing delay | `PacingReplay.beforeAppliedDelayMs` |
| \(B\) | measured Draft backlog at the decision | `RQ3Pacing.realBacklogMs` |
| \(T\) | budget left in the deadline window | `beforeTimeToDeadlineMs` |
| \(C\) | realized duration of the admitted Draft sequence | `draftSequenceDurationMs` |
| \(\hat{B}\) | the controller's backlog clock | `beforeBacklogMs` |
| \(\hat{C}\) | the Draft reserve | `beforeDraftSequenceReservedDurationMs` |

Derived:

```text
required delay        d*      = ceil( [B + 2C - max(0,T)]^+ / 2 )
mandatory floor       d*_mand = the same on C with skippable optional work removed
backlog error                 = Bhat - B
Draft reserve error           = Chat - C
Draft pricing error           = (beforeWorkloadSequencePredictedDurationMs
                                 + beforeDraftSequenceOverheadDurationMs)
                                - draftSequenceDurationMs
queued Draft pricing error    = the Draft pricing error summed over the Drafts
                                that had not finished at the decision and
                                started before the target's own Draft
```

Away from the `max(0, .)` clip the first three close an identity,

```text
d - d*  =  (Chat - C)  +  (Bhat - B) / 2
```

which the generator asserts on every decision carrying both a positive applied
and a positive required delay. It holds to 0.50 ms at 12MP and 0.76 ms at 24MP,
which is the two ceilings in the formulas; a residual above 1 ms aborts the run
and means a delay, backlog, or deadline field in the export changed meaning.

## Outcome classes

The four classes partition every analyzed decision. The last three partition the
decisions that required a delay.

```text
no_delay_required   d* = 0
covered             d >= d*
flexible            d*_mand <= d < d*
below_floor         d <  d*_mand
```

`flexible` is a joint-control interpretation of an outcome measured after the
run, not a record of an intent expressed at the decision.

## Generated files

| File | Contents |
|---|---|
| `summary.csv` | Scalars: populations, both error distributions, the identity check, the floor block, and the floor repricing |
| `outcome_matrix.csv` | One row per (condition, class): every cell the table prints, plus `skipped_either_pct` and `deadline_margin_under_1pct`, which it does not |
| `queued_pricing_scatter.csv` | One row per decision with a reconstructible queue: the two axes of figure panels (b) and (c) |
| `scatter_<condition>_<class>.csv` | The same rows split per mark style, which is what pgfplots consumes |
| `draft_pricing_ecdf_<condition>.csv` | ECDF of the per-Draft pricing error, thinned to at most 360 points with both endpoints kept |
| `reserve_error_ecdf_<condition>.csv` | ECDF of the Draft reserve error, thinned the same way |

Percentiles printed in the table are computed on the whole population; the
thinning affects only what the figure draws.

## Validity and interpretation

Timeout-measurement-error records are invalid observations rather than actual
Capture Timeout outcomes. No valid analyzed run timed out. Do not describe this
population as survival-conditioned.

The queued Draft pricing error is **not** recoverable time and **not** a
counterfactual. Pacing is closed-loop: a clock that priced the queue differently
would have changed later arrival times, backlog, admission decisions, thermal
state, and realized Draft durations. The same rule forbids mechanically scaling
the recorded delay column by 0.5 or 0.75.

`floorMissRepricedAtOrAboveFloor` substitutes the measured backlog into the
deployed formula on the recorded row. It says what the controller would have
computed at that instant with an exact backlog clock, on 11 of the 14 floor
misses. It does not say what the run would have done.

The relation the figure plots between the backlog error and the queued pricing
error is close to definitional, because the backlog clock is that sum. Its value
is that it localises the whole backlog error in the per-Draft price and rules
out other contributions, and that the outcome classes separate along it. The
queue is reconstructed offline from the Draft timeline rather than read out of
the controller's FIFO, so the regression slope is 0.84 and 0.79 rather than 1.

The mandatory floor is a sufficient retrospective reservation condition, not the
timeout boundary. Because it already excludes optional work, a demotion in a
floor-miss case records admission action but does not remove the remaining
deficit.

See `docs/rq3-current.md` for the full paper-level interpretation and current
artifact inventory, and `data/rq3/coordination/README.md` for the admission
action and margin decomposition.
