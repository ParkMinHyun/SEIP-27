# Current RQ3 Design and Interpretation

This document is the authoritative handoff for the current RQ3 candidate. It
supersedes the earlier four-policy RQ3 design still retained as historical
material in `docs/rq1-rq3-metrics-guide.md`.

## Research question

RQ3 asks whether the Context-Aware Draft Sequence Controller computes an
appropriately sized capture-availability delay for the Draft backlog and the
remaining Capture Timeout budget.

The current evaluation does not compare the controller against pacing methods
transplanted from unrelated domains. Such methods optimize different signals
and would not isolate whether this controller sizes its own intervention
appropriately. RQ3 instead evaluates four properties of the deployed control
structure, in the order the exhibits present them:

1. how much of the delay the realized Draft work required each decision
   actually applied;
2. what happened to the captures where it applied less — whether admission
   absorbed the remainder and whether the deadline still held;
3. where the difference between applied and required delay comes from, which is
   an exact decomposition into the errors of the two estimators the controller
   builds; and
4. whether the resulting wait drains measured backlog at bounded user-visible
   cost.

Property 3 is the one earlier revisions were missing. They could report that the
short-fall decisions under-estimated backlog but not what produced the
under-estimate, which reads as a model-quality complaint rather than as a
mechanism. It is now measured, and it is the finding an industrial reader can
act on.

### No threshold the reader cannot recompute

Every population in the current pair is cut by the required delay \(d^{*}\)
itself. The exhibits print no band edge, no "over 40% budget left", and no
constant that is not derivable from the two formulas below. An earlier revision
printed a 40% cut inherited from the historical selectivity exhibit, which the
compact pair does not ship; a reader had no way to know where it came from.

## Current artifacts

The current main-paper candidates are:

- `tables/tab_rq3_pacing_compact.tex`;
- `figures/fig_rq3_pacing_compact.tex`.

The earlier policy, selectivity, and calibration TeX pairs are retained and
must not be deleted or silently overwritten. They are historical alternatives,
not additional exhibits to ship beside the compact pair.

Both are `table*`/`figure*` floats: the table is a matrix whose rows are the
four outcome classes and whose columns include the estimator diagnostics, and
the figure carries the two distributional claims the table can only summarise at
P50. Review them from a real `pdflatex` render; the browser-preview route that
earlier revisions used is no longer maintained, and the preview PNGs it produced
are not in the repository.

## Printed terminology

The compact table and figure print only terms the manuscript already uses
elsewhere. This document, the generated CSVs, and `scripts/rq3_coordination_*.py`
keep the older analysis vocabulary, so use this map when moving between them.

| Printed in the exhibits | Used in this document, the CSVs, and the scripts |
|---|---|
| pacing decision | transition (one shot-to-shot interval; a 30-capture run holds 29) |
| run | burst (one complete 30-capture session) |
| required delay | envelope, \(d^{*}\) |
| missing delay | \(d^{*}-d\): potential avoided delay (flexible band), `shortfall_ms` (mandatory-floor block) |
| skipped optional work | demotion (Bokeh+Filter → Filter only → Encoding only) |
| deadline margin | realized margin |
| this / next Draft | target / next |
| Draft reserve error | `draftSequenceReserveErrorMs`, \(\hat{C}-C\) |
| backlog error | `backlogEstimateErrorMs`, \(\hat{B}-B\) |
| Draft pricing error | derived from `draftOccupancyUnderpriceMs`; see below |
| queued Draft pricing error | the same, summed over the Drafts queued ahead |

The three error names are new because the quantities are new. Each is named
after the implementation column it comes from, and all three are signed
**estimate minus realized**, so a positive value always means the controller
reserved more than the pipeline used. Do not flip the sign of one of them for
local convenience.

*Budget left* is no longer printed. It named the negated pressure that the
withdrawn 40% band was cut on, and the current pair states the same information
as the required delay itself.

The printed terms are anchored in the rest of the paper: *budget* is in the
paper title and Section~2.4, *run* and *capture* are the units of the RQ1
tables, *Skipped* is RQ2's column, *deadline margin* is the case-study table's
row, and *Draft*, *optional work*, and *mandatory* come from Section~2.3.
Do not reintroduce *spare*, *transition*, *burst*, *target*, *demotion*,
*shortfall*, *envelope*, or *retrospective* into printed labels or body text.

## Population and data-quality rule

The compact analysis uses the Full controller workbooks:

- `data/ablation_sampling/48U_metrics_12MP_normal_0803_{1,2}.xlsx`;
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_{1,2}.xlsx`.

The timeout labels removed from this collection are known invalid measurements,
not actual Capture Timeout outcomes. Their removal is data-quality filtering,
not outcome-based survival conditioning. No valid analyzed run experienced an
actual Capture Timeout. Future manuscript revisions must not call this
population survival-conditioned. The final paper should identify the timeout
measurement fault and exclusion manifest wherever the experiment-validity
protocol is described; do not invent those details if the implementation or
manifest is unavailable.

Complete 30-shot runs are required. The current compact population contains 70
12MP-normal bursts and 69 24MP-memory-pressure bursts, producing 1,920 and
1,861 analyzed transitions. A transition additionally requires a recorded
pacing decision and a complete prior-Draft timeline. Watchdog-truncated
transitions lack a complete realized Draft duration and are excluded from the
envelope reconstruction for that reason.

## Envelope definitions

For one transition, let:

- \(d\) be the applied pacing delay;
- \(B\) be measured Draft backlog at the decision;
- \(T\) be the remaining deadline window;
- \(C_{exec}\) be the realized duration of the admitted Draft sequence; and
- \(C_{mand}\) contain DynamicFunction, Encoding, and measured Draft overhead,
  excluding admission-skippable optional work.

The retrospective pacing-only envelopes are:

\[
d^*_{exec}=\left\lceil\frac{[B+2C_{exec}-\max(0,T)]^+}{2}\right\rceil
\]

and

\[
d^*_{mand}=\left\lceil\frac{[B+2C_{mand}-\max(0,T)]^+}{2}\right\rceil.
\]

The factor \(2C\) is the deployed prospective horizon: (i) the Draft that
begins after the pacing decision and (ii) the Draft of the next capture released
by that delay. Waiting one millisecond both drains one millisecond of backlog
and shifts the next deadline by one millisecond, hence division by two.

## The outcome matrix

Every analyzed decision falls into exactly one of four classes. The first is the
complement of the required set; the other three partition it. The table prints
them as rows so both sums are visible without arithmetic on the reader's part.

| Class | Condition | 12MP | 24MP |
|---|---|---:|---:|
| No delay was required | \(d^{*}_{exec}=0\) | 1,841 | 1,721 |
| Covered by pacing alone | \(d\ge d^{*}_{exec}\) | 53 | 83 |
| Part left to admission | \(d^{*}_{mand}\le d<d^{*}_{exec}\) | 26 | 43 |
| Below the mandatory floor | \(d<d^{*}_{mand}\) | 0 | 14 |

1,841 + 53 + 26 + 0 = 1,920 and 1,721 + 83 + 43 + 14 = 1,861; the last three add
to the 79 and 140 decisions that required a delay.

"Part left to admission" is a joint-control interpretation of an outcome
measured after the run, not a record of an intent expressed at the decision. In
these decisions the mandatory work fit without the missing delay, and the
optional work that did not fit either was skipped by admission or ran to
completion and still met the deadline: the minimum realized margin in the class
is 1.91% and 0.51% of the budget, and neither is the tightest margin in the
table.

A positive missing delay is an unmet **prospective** reservation over the \(2C\)
horizon, not an observed overrun. Never describe these decisions as near-misses
without the margin column beside them.

### The overrun population is strict

Retained because `scripts/rq3_policy_metrics.py` still emits it for the
historical selectivity exhibit; the current pair no longer prints a pressure
band at all.

"No budget left" and "required a delay" must be the same set. Pressure is
\(B+2C-\max(0,T)\) and \(d^{*}_{exec}=\lceil \text{pressure}/2\rceil\), so a
decision at exactly zero pressure needs no delay and is not an overrun. Both
populations are therefore **pressure > 0**: 79 at 12MP and 140 at 24MP.

`rq3_policy_metrics.py` keeps its half-open `[0, inf)` pressure *band* unchanged,
because the historical exhibit bins a shape and must leave no value unbinned,
and carries a separate strict cut `OVERRUN_PCT` for everything else. The two
forms differ on one decision in this collection, 24MP run 2#27 capture 28 at
pressure 0.0 ms; a revision that mixed them printed 141 against 140 in one
table.

## Where the applied and required delay differ

This is the section earlier revisions did not have, and it is what makes the
under-estimate a mechanism instead of an observation.

Away from the `max(0, .)` clip — on the 61 and 97 decisions carrying both a
positive applied delay and a positive required delay —

\[
d-d^{*}=(\hat{C}-C)+\frac{\hat{B}-B}{2}
\]

holds identically, where \(\hat{C}\) is
`beforeDraftSequenceReservedDurationMs` and \(\hat{B}\) is `beforeBacklogMs`.
`scripts/rq3_estimator_metrics.py` asserts it; it closes to 0.50 ms at 12MP and
0.76 ms at 24MP, which is the two ceilings in the formulas.

The two terms are the errors of two estimators the controller builds by
different conventions, and each owns one failure mode.

**The Draft reserve over-covers, by design.**
`CaptureAvailablePacingSession.getMaxDraftSequenceDurationMs` prices \(\hat{C}\)
at the session's observed **maximum** Draft duration for the capture's size
bucket, re-projected onto the admitted sequence, and the delay formula uses it
twice. A maximum priced against a typical realized duration necessarily
over-covers: the median reserve error is +230 ms and +250 ms on decisions that
required no delay at all. That is why pacing also fires on 19.0% and 21.7% of
those decisions — 350 and 374 of them, at a median 377 ms and 252 ms. State this
as a design choice with a measured price, not as an unexplained excess.

**The backlog clock under-covers in its tail, because a point price is summed.**
`CaptureAvailablePacingSession.queuePacingDecision` advances \(\hat{B}\) by each
queued Draft's **point** prediction plus one learned between-node overhead. Per
Draft that is nearly right — the pricing error is +16 ms and +19 ms at P50 — but
widely dispersed, −135 ms and −293 ms at P05. Unlike the reserve it is summed
over the queue, so the dispersion accumulates. Summing the per-Draft pricing
error over the Drafts queued ahead of a decision reproduces that decision's
backlog error at Pearson \(r=0.95\) and \(0.88\).

The class contrast is the evidence:

| Class | Queued pricing error P50 | Backlog error P50 | Reserve error P50 |
|---|---:|---:|---:|
| No delay was required | +27 / +9 ms | −19 / −43 ms | +230 / +250 ms |
| Covered by pacing alone | +25 / −46 ms | −4 / −68 ms | +308 / +487 ms |
| Part left to admission | −627 / −930 ms | −677 / −980 ms | +80 / −9 ms |
| Below the mandatory floor | — / −1,278 ms | — / −1,392 ms | — / +31 ms |

The decisions pacing covered look exactly like the population. The decisions
where it fell short are the ones whose queue accumulated 0.6–1.3 s of optimism.

### The asymmetry is the actionable finding

The controller already knows to price a single Draft by a conservative
statistic, and prices a whole queue by a central one. A central statistic is the
right thing to charge for one Draft and the wrong thing to sum over a queue.
That is the design lever this evaluation identifies; it is not a claim that
changing it would have prevented anything, which the closed-loop objection below
forbids.

### Two limits on this decomposition

- The relation between the backlog error and the queued pricing error is close
  to **definitional**, because the backlog clock is that sum. Its value is that
  it localises the whole backlog error in the per-Draft price and rules out
  other contributions, and that the outcome classes separate along it. Do not
  present \(r\) as a discovery.
- The queue is reconstructed offline from the Draft timeline rather than read
  out of the controller's FIFO, so the regression slope is 0.84 and 0.79 rather
  than 1. The vertical spread in the figure is what that reconstruction does not
  capture.

## Actual admission-action audit

Demotion ranks optional-work classes as:

```text
Bokeh+Filter > Filter only > Encoding only
```

The compact table reports two observed actions for admission-flexible
transitions:

- **target:** admission demoted the Draft directly associated with the pacing
  transition;
- **target-or-next:** admission demoted either that target or the next capture's
  Draft, matching the two-Draft prospective horizon.

Target-or-next is a horizon audit. It must not be phrased as causal attribution
of the next admission decision to the current delay.

Observed flexible-band demotion is:

| Condition | Target | Target or next |
|---|---:|---:|
| 12MP normal | 7/26 (26.9%) | 21/26 (80.8%) |
| 24MP memory pressure | 17/43 (39.5%) | 31/43 (72.1%) |

The flexible-band realized target-margin minimum/P5 is 134/183 ms in 12MP and
36/84 ms in 24MP.

### Only the target rate is printed, and why

Admission demotion is **session-sticky**: once a run skips optional work, the
shots after it mostly skip too. Pooled over the analyzed decisions, this-Draft
and next-Draft skips co-occur 807 and 779 times against 2 and 5 this-Draft-only;
the 50 and 51 next-Draft-only cases are the onset shots, which is why the
required-delay classes show a much larger gap between the two rates than the
population does.
The two-Draft rate is therefore close to "had this run already entered the
demoted regime", which needs a paragraph of qualification to read correctly, and
a single ambiguous column is worse than a narrower unambiguous one.

The table prints the this-Draft rate alone. `skipped_either_pct` in
`data/rq3/estimator/outcome_matrix.csv` keeps the two-Draft rate for every
class, not only the flexible band. Note that at 12MP the flexible band's
this-Draft rate, 26.9%, is **below** the 42.4% population rate: admission did not
step in more often there. Report that plainly — the deadline held anyway, which
is what the margin column is for — rather than selecting the horizon that makes
the coordination claim look stronger.

## Mandatory-floor audit

No 12MP transition fell below \(d^*_{mand}\). Fourteen of 140 positive-envelope
24MP transitions did, clustered in four bursts:

- 11/14 received zero delay;
- admission demoted 14/14 target Drafts;
- online backlog was below subsequently realized backlog in 14/14, by a median
  of 1,392 ms, against a queued pricing error of −1,278 ms;
- thermal headroom rose during queue residence in 12/14;
- median decision-to-Draft-start queue residence was 4.78 s;
- the minimum realized margin was **4.39% of the budget**, and the class P5 is
  4.53% — the *largest* minimum of any class in the table; and
- 0/14 produced an actual Capture Timeout.

The floor is a retrospective sufficient reservation condition, not the actual
timeout boundary, and the margin row is the direct evidence: the decisions that
missed the floor are the ones that finished with the most budget to spare.
Because \(d^*_{mand}\) already excludes optional work, target demotion documents
coordination but does not itself erase the mandatory-floor deficit. Backlog
under-estimation and rising headroom are observationally consistent with
queue/thermal drift after the online decision; do not claim causality from this
trace split.

### The floor repricing

Substituting the measured backlog \(B\) for \(\hat{B}\) in the deployed formula
on the recorded row prices **at or above the mandatory floor on 11 of the 14**
misses, at a median 428 ms. This is emitted as
`floorMissRepricedAtOrAboveFloor` in `data/rq3/estimator/summary.csv`.

Read it as: with an exact backlog clock at that instant, the deployed formula
would have reached the floor in 11 of 14 cases. It is **not** a claim about how
the run would have gone. Pacing is closed-loop, so a different delay changes
later arrivals, backlog, admission, thermal state, and realized Draft duration —
the same objection that forbids a mechanically scaled delay column. Always print
the repricing with that qualification attached.

### Where the retained margin came from

Retained as a verified result of `scripts/rq3_coordination_audit.py`. The
current figure no longer plots it — it plots the estimator errors instead — but
the identity below is still asserted on every analyzed decision on every run of
that script, and it is the accounting behind the floor block's margin row.

Substituting the floor's own definition, \(2d^{*}_{mand}=B+2C_{mand}-T\), into
\(\text{margin}=(\text{deadline}-\text{decision})-\text{wait}-C_{exec}\) makes
the realized margin an identity over three separately measured terms:

\[
\text{margin}=\underbrace{\varepsilon}_{\text{deadline reference}}
+\underbrace{(2C_{mand}-C_{exec})}_{\text{horizon reserve}}
+\underbrace{(B-\text{wait})}_{\text{backlog residual}}
-2d^{*}_{mand}
\]

| Term | What it is | 14 floor misses (min / P50 / max) |
|---|---|---|
| deadline reference \(\varepsilon\) | The controller prices the remaining window from `backlogDeadlineMs`, "the deadline of whatever entered the backlog last, which is the one the whole queue has to fit inside" (`CaptureAvailablePacingSession.timeToDeadlineMsAt`). \(\varepsilon\) is the budget between that deadline and the capture's own timeout timestamp. | 0 / 845 / 1,323 ms |
| horizon reserve | The \(2C\) horizon reserves a second Draft for the next capture; this capture's own deadline covers only its own. | 56 / 629 / 1,109 ms |
| backlog residual | \(B-\text{wait}\): how well the measured backlog predicted the wait actually served. | −92 / −28 / −14 ms |

`scripts/rq3_coordination_audit.py` asserts the identity on every analyzed
decision, not only these 14. It closes to **1.0 ms**, which is the two ceilings
in the floor formulas; a residual above 2 ms aborts the run and means a
deadline or wait field in the export changed meaning. The emitted columns are
`deadlineRefMs`, `horizonReserveMs`, `backlogResidualMs`, `unmetFloorMs`, and
`uncountedBudgetMs`.

Two limits on this decomposition:

- It is **arithmetic on the realized trace, not a counterfactual**. It accounts
  for the margin that was observed and says nothing about the margin a
  different delay would have produced. The closed-loop objection below still
  applies in full.
- \(\varepsilon\ge 0\) holds on 14/14 floor misses but **not** on the whole
  population (12MP 56/79, 24MP 130/140). Do not write that the binding deadline
  is always earlier than the capture's own.

The near-zero backlog residual is itself a result worth stating: the measured
backlog predicted the realized wait to within 92 ms on every floor miss, so the
retained margin did not come from the backlog clock.

## Why no alternative-policy or scaled-delay baseline is required

RQ3 must not be reframed around Thermal LUT, CoDel-inspired, or other
domain-mismatched pacing methods unless the user explicitly changes the
research question. Those comparisons ask which foreign controller performs
better, not whether the proposed controller sizes delay appropriately for its
Draft backlog and deadline model.

Likewise, multiplying each recorded delay by 0.5 or 0.75 on the same trace is
not a valid counterfactual. Pacing is closed-loop: changing one delay changes
later arrival times, backlog, admission decisions, thermal state, throttling,
and realized Draft durations. The existing factual dataset therefore cannot
answer what the 0.5x or 0.75x trajectory would have been. A defensible scaling
study would require new matched factual runs or a validated closed-loop replay
or simulator; mechanically rescaling the recorded column is prohibited.

This limitation does not invalidate the current RQ3. It limits the supported
claim to trace-derived targeting, envelope coverage, coordination, work
conservation, and observed cost. Do not claim global optimality, a universally
minimal delay, or a counterfactual end-to-end speedup.

## Reproduction

Run from the repository root:

```text
python3 scripts/rq3_policy_metrics.py sampling  # requires openpyxl
python3 scripts/rq3_coordination_metrics.py
python3 scripts/rq3_coordination_audit.py
python3 scripts/rq3_estimator_metrics.py
make                                            # requires pdflatex
```

The first command regenerates targeting and boundary-mechanism inputs, including
the cost block the table prints. The second produces the envelope partition. The
third joins actual admission actions, audits mandatory-floor misses, and asserts
the margin identity. The fourth produces everything else the compact pair prints:
the outcome matrix, both estimator error distributions, the scatter inputs, and
the floor repricing. Only the first needs `openpyxl`; the rest use the standard
library.

Review the result from the `pdflatex` render. The build must stay free of
overfull and underfull boxes; both exhibits currently produce none.

Detailed generated-file definitions are in `data/rq3/estimator/README.md` and
`data/rq3/coordination/README.md`. The complete transfer checklist is
`docs/rq3-file-manifest.md`.

## Supported manuscript conclusion

The current evidence supports the following bounded conclusion:

> Of the pacing decisions whose realized Draft work required a delay, the
> controller applied enough on its own for 67% and 59%, and left part of the
> remainder to admission without any capture losing its deadline. Where it
> applied too little, the cause is a single measurable one: the backlog clock
> charges each queued Draft a point price, and summing a central estimate over a
> queue accumulates its dispersion. Where it applied more than the realized work
> needed, the cause is the complementary choice on the other estimator, whose
> maximum-based Draft reserve over-covers by construction, at a bounded and
> reported responsiveness cost.

It does not support `globally optimal`, `minimum necessary under every
counterfactual`, a causal thermal claim, or any statement about what a different
backlog clock would have produced end to end.

### What a reviewer should be able to check without asking

- every population is cut by \(d^{*}\), and the four classes sum to the analyzed
  total in the printed column;
- the identity \(d-d^{*}=(\hat{C}-C)+(\hat{B}-B)/2\) is asserted in the
  generator and closes to 0.8 ms;
- the class contrast in the queued pricing error is the mechanism, and the
  figure shows it is not an artefact of medians;
- every count in the exhibits is reproducible from the four commands above; and
- each claim that could be read as counterfactual — the repricing, the missing
  delay, the queued pricing error — carries its qualification in the caption,
  not only in this document.
