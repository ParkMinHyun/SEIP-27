# RQ3 Estimator Artifact

Generated evidence for the RQ3 summary table: the retrospective matched-policy
target for each pacing decision, what it got, and where the difference came from. Do not edit
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
matched-policy target d*      = ceil( [B + 2C - max(0,T)]^+ / 2 )
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

Here `required` in existing CSV fields and class keys is a compatibility name
for this retrospective heuristic target, not a physical minimum or an optimal
counterfactual delay.

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
| `outcome_matrix.csv` | One row per (condition, class): every cell the table prints, plus `skipped_either_pct` and `deadline_margin_under_1pct`, which it does not. The two estimator errors are carried both ways — `*_p50_ms` and `*_p50_pct` — and the table prints the **pct** pair; the ratio is formed per decision before the median, so the two are not convertible into each other |
| `sizing_summary.csv` | The two populations on which applied-against-required is defined: decisions paced although none was required, and decisions whose requirement the delay covered. Feeds block (b) of the table. Carries its **own** `reserve_error_p50_ms` and `backlog_error_p50_ms`, and the matching `_pct` pair, recomputed on the paced subset rather than read from `outcome_matrix.csv`; on `paced_none_required` the two differ by more than a rounding (+555/+653 ms against +230/+250, and the backlog error changes sign), because that class is 81% and 78% unpaced |
| `floor_zero_delay_account.csv` | One row per below-the-floor decision that received no delay at all (11, all 24MP): what the controller priced online and how that differs from the realized mandatory pressure. See below |
| `thin_margin_tail.csv` | One row per decision that finished under 1% of the budget (11 of 3,781): the backlog and queue wait that consumed the budget, the delay applied, and whether either control was engaged. Backs the table note's characterisation of the printed minimum margin, so the minimum can be published without reading as a lucky escape. Row count is asserted against `deadline_margin_under_1pct` |
| `queued_pricing_scatter.csv` | One row per decision with a reconstructible queue |
| `scatter_<condition>_<class>.csv` | The same rows split per class |
| `draft_pricing_ecdf_<condition>.csv` | ECDF of the per-Draft pricing error, thinned to at most 360 points with both endpoints kept |
| `reserve_error_ecdf_<condition>.csv` | ECDF of the Draft reserve error, thinned the same way |

The last four backed an earlier RQ3 figure, which was deleted. They are still
generated and are still the fastest way to check the population P05/P50/P95 the
RQ3 prose has to quote, but nothing in the manuscript reads them directly.

### `floor_zero_delay_account.csv`

The 11 rows are the decisions a reader asks about first: pacing applied nothing
although the mandatory work provably did not fit. The file is an identity, not
an explanation of intent. With \(\hat{B}\), \(\hat{C}\), \(B\), \(T\) as above
and \(C_{mand}\) the mandatory part of the realized Draft duration,

- `controller_saw_ms` \(=\hat{B}+2\hat{C}-T\), what the deployed formula was
  given at the decision. It is **non-positive on 11/11** (\(-46\) to
  \(-1{,}729\) ms), so zero was that formula's correct output;
- `backlog_term_ms` \(=B-\hat{B}\) and `reserve_term_ms` \(=2(C_{mand}-\hat{C})\)
  are the two ways the online view differed from the realized one;
- `account_ms` is their sum with `controller_saw_ms`, and the generator asserts
  it equals \(2d^{*}_{mand}\) within 2 ms — that assertion is the file's
  correctness check;
- `repriced_reaches_floor` is `repriced_ms` \(\ge\) `mandatory_floor_ms`, true on
  **9/11** (and 11/14 over all floor misses, `floorMissRepricedAtOrAboveFloor`);
- `backlog_flips_sign` is `controller_saw_ms + backlog_term_ms > 0`, true on
  **11/11**: correcting the backlog clock alone would have made the controller
  see positive pressure at that instant.

A previous version of this column was named `backlog_term_sufficient` and tested
`backlog_term > -(saw + reserve_term)`, which reduces to `account > 0` and is
therefore true for every below-floor decision by the class definition. It
carried no information and must not be reinstated. Neither the repricing nor the
sign flip says what the run would have done: pacing is closed-loop.

Percentiles quoted anywhere are computed on the whole population; the ECDF
thinning affects only those two files.

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

The relation between the backlog error and the queued pricing error is close to
definitional, because the backlog clock is that sum. Its value
is that it localises the whole backlog error in the per-Draft price and rules
out other contributions, and that the outcome classes separate along it. The
queue is reconstructed offline from the Draft timeline rather than read out of
the controller's FIFO, so the regression slope is 0.84 and 0.79 rather than 1.

The mandatory floor is a sufficient retrospective reservation condition, not the
timeout boundary. Because it already excludes optional work, a demotion in a
floor-miss case records admission action but does not remove the remaining
deficit.

See `docs/rq-evidence.md` (Part 1) for the full paper-level interpretation and current
artifact inventory, and `data/rq3/coordination/README.md` for the admission
action and margin decomposition.
