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
structure, in the order the table presents them:

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

Every population in the current table is cut by the required delay \(d^{*}\)
itself. It prints no band edge, no "over 40% budget left", and no constant that
is not derivable from the two formulas below. An earlier revision printed a 40%
cut inherited from the historical selectivity exhibit, which the current table
does not ship; a reader had no way to know where it came from.

## Current artifacts

The current main-paper exhibit is `tables/tab_rq3_pacing_compact.tex`, and it
is the only one: `figures/fig_rq3_pacing_compact.tex` was deleted.

The earlier policy, selectivity, and calibration TeX pairs are retained and
must not be deleted or silently overwritten. They are historical alternatives,
not additional exhibits to ship beside the current table.

The table is a single-column `table` float carrying two blocks, and **each block
has its own population**, which is the point of the split:

- **(a) When a reservation was required, how much did pacing cover?** Population
  \(d^{*}>0\) — 79 and 140. Rows are the three coverage classes; every column is
  a count or a median over *all* decisions in the class, paced or not, so *did
  pacing fire* is a column rather than a filter.
- **(b) Where pacing fired, was the delay conservative but work-conserving?**
  Population \(d>0\). Every column is a median over exactly those decisions.

Each paired quantity is split into its own sub-columns under a `\cmidrule` group,
except (b)'s `Delay P50`, where `0 → 377` stays one cell because the arrow
carries its own reading order and required-against-applied is the comparison the
block exists to make.

Review the result from a real `pdflatex` render; the browser-preview route that
earlier revisions used is no longer maintained, and the preview PNGs it produced
are not in the repository.

### Why (a) prints no "none required" row, and how the totals stay checkable

An earlier revision made (a) a partition of every analyzed decision, so its first
row was the complement of the required set. That kept a visible sum but cost the
thing (a) exists to measure: with 1,920 as the denominator the under-sized tail
reads as 0.8% of decisions, which buries it. Against the population where a
reservation *was* required it is 10.0%, and that is the number a reviewer needs.

Verifiability survives without the row, but it now takes one addition. The block
labels used to print 79/1,920 and 140/1,861; they carry the condition alone, so
the required-set size is (a)'s own row sum — 53 + 26 + 0 = 79 and
83 + 43 + 14 = 140 — and the analyzed total is that plus (b)'s `n`:
1,841 + 79 = 1,920 and 1,721 + 140 = 1,861. **Do not remove (b)'s `n` column** —
with the labels reduced it is the last printed trace of the analyzed totals.

The 4.1% and 7.5% shares left with the labels. They are the first sentence of the
RQ3 narrative — pacing addresses a tail rather than charging every capture a
fixed delay — and the prose owns them now; the table never printed them as a
cell, only as label prose.

### Layout constraints that are easy to re-break

Every `p{}` width in both blocks is the measured maximum of that column's own
data *and* its own header, taken with `\settowidth` at `\scriptsize` against
`\columnwidth = 252pt`. Two failure modes bit earlier drafts:

- a header line wider than its `p{}` value **inside a `\makecell` overflows**
  rather than wrapping (`What the realized` is 54.9pt, which overflowed a 54pt
  column by exactly the 0.89pt the log reported);
- a plain-text or math cell wider than its `p{}` value **silently wraps to two
  lines**, and no overfull warning reports it. The old `Less than mandatory`
  label wrapped at 54pt against its 59.7pt; more recently `\(188\to685\)`
  wrapped in (b)'s delay column at 32pt against its 33.7pt. Check that column by
  eye after any change to it.

So: re-measure before changing any label, and use `\fittabcolsep` rather than a
hardcoded `\tabcolsep`. A fixed value leaves the two blocks at different natural
widths — 237pt and 229pt for the values one draft used — so they sit unaligned
inside the column.

`\multirow` is used for the first column of **both** blocks, with a `-2.7pt`
centring correction and `\centering` inside it. Both headers are three lines
tall — row one holds two-line group labels, row two single-line sub-labels — so
the box `\multirow[c]{2}` computes from twice the standard row height is shorter
than the header, and the residue is half of row two.

An earlier draft could not use `\multirow` in (b): it reported an overfull
`\vbox` on every `\fittabcolsep` iteration whatever offset it was given, and the
label was left sitting in header row one, top-aligned. That failure needs row
two's first cell to be **empty**; once the spanning cells are given their offset
and row two is filled, the same construct works in both blocks. Re-derive the
offset if either row changes its line count.

### Block (b): why "enough" is not the whole claim

Block (a) answers whether the delay was *sufficient*. It cannot answer whether
it was *more than sufficient*, because it prints no applied delay, and
"appropriately sized" is a two-sided claim. Block (b) supplies the second side
on the only two populations where the comparison is defined:

The two error columns print per cent, not milliseconds; both forms are in
`sizing_summary.csv` and the millisecond pair is given here in brackets.

| Population | n | Required \(d^{*}\) P50 | Applied \(d\) P50 | \(\hat{C}-C\) P50 | \(\hat{B}-B\) P50 | \(d/B\) P50 | inside \(B\) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12MP, none required | 350 | 0 | 377 | +87.0% [+555 ms] | +11.9% [+445 ms] | 10.8% | 100.0% |
| 12MP, full requirement | 53 | 80 | 432 | +41.4% [+308 ms] | −0.1% [−4 ms] | 9.5% | 100.0% |
| 24MP, none required | 374 | 0 | 252 | +90.8% [+653 ms] | +6.7% [+231 ms] | 7.3% | 98.3% |
| 24MP, full requirement | 83 | 188 | 685 | +44.4% [+487 ms] | −1.6% [−68 ms] | 20.3% | 99.6% |

Both populations are subsets of the decisions where pacing acted, so the printed
`n` is smaller than the matching class count in (a). The row labels are (a)'s
own, because these are (a)'s first two rows restricted to the paced: the
`covered` population is the whole of (a)'s *The full requirement* class, so 53
and 83 agree, and 350 and 374 are (a)'s top-row *Paced* counts. Required against
applied, both estimator errors, \(d/B\) and *inside \(B\)* are all columns of this
block, which is what lets it answer the over-pacing question without a backward
jump. Only the per-run cost sits in the note, because it is not a per-decision
quantity; see *The block labels carry only the condition* below.

#### The two error columns appear in both blocks on purpose

They are the same two quantities under the same header on two different
populations, and printing them twice is what makes each block's claim
population-correct. (a) needs the whole class, because a decision that received
no delay still belongs to the class whose coverage the row reports. (b) needs
the paced decisions alone, because its question is why the delay that *was*
applied exceeded the requirement.

Reserve / backlog error P50, as the table prints them (per cent), with the
millisecond pair in brackets:

|  | (a), whole class | (b), paced only |
|---|---:|---:|
| None was required, 12MP | +38.2 / −1.3 [+230 / −19 ms] | **+87.0 / +11.9** [+555 / +445 ms] |
| None was required, 24MP | +36.4 / −2.8 [+250 / −43 ms] | **+90.8 / +6.7** [+653 / +231 ms] |
| The full requirement, both | +41.4 / −0.1 and +44.4 / −1.6 | identical |

*The full requirement* class is 100% paced, so its row is the same in both
blocks. That is the control that makes the top row's difference legible, and the
difference is not a refinement: **the backlog error changes sign.** Read on the
class, the over-shoot looks like the Draft reserve acting alone against a roughly
correct backlog clock. Read on the 350 and 374 decisions pacing actually acted
on, both estimates were conservative at once, and after the \(/2\) the clock
contributes +222 and +116 ms of the over-shoot beside the reserve's +555 and
+653.

Two rules follow. **Never quote (a)'s error cells as the explanation of the
`Paced` count on the same row** — 350 of 1,841 and 374 of 1,721 were paced, so a
class-wide median describes the 81% and 78% that were not, and an earlier
revision wrote exactly that attribution. And do not expect the identity
\(d-d^{*}=(\hat{C}-C)+(\hat{B}-B)/2\) to close on the *none was required* rows:
\(d^{*}\) is clipped at zero there, so the two errors are what the controller
held, not a decomposition of a positive \(d^{*}\).

Read left to right, the block makes two statements and needs both.

**The delay is several multiples of the minimum sufficient reservation.** Where
it covers the requirement it is 5.4x and 3.6x that requirement at the median.
With the short-fall rows of (a), whose median applied delay is zero, the sizing
is **bimodal**: pacing either over-covers by multiples or does not fire, and
rarely lands near \(d^{*}\). The two estimator conventions produce that shape,
and (b)'s own error columns are the ones to cite for it. State it plainly — it is
what converts an unverifiable self-assessment into a measured cost with a named
cause.

**That is not the same as arbitrary, and the \(d/B\) column is why.**
\(d^{*}\) is a *residual*, \((B+2C-T)/2\), so it falls to zero whenever the
deadline window is wide however much Draft work is queued; being a multiple of
it says nothing about whether the wait was large in absolute terms. Priced
instead against the Draft work actually outstanding when it was applied, the
same delay is 7 to 20 per cent of the backlog, and 98.3 to 100 per cent of every
millisecond of it ran while at least that much work was still in the pipeline.
Only 0 of 403 waits at 12MP and 8 of 457 at 24MP outlast the backlog they drain
(`waits_outlasting_backlog`; the denominators are this block's two populations,
350+53 and 374+83, not the 411 and 471 paced decisions, because the short-fall
rows are not in it). The wait is not created by pacing; it is moved from after
the shutter to before it.

Do **not** upgrade this into a claim that the queue would have been unstable
without pacing. This block is arithmetic on the realized trace. The
controller-off and pacing-only arms of the RQ1 ablation are where that
comparison lives, and the RQ3 prose should cross-refer to them.

An earlier revision printed the over-applied difference \(d-d^{*}\) at P50/P95
instead of the two backlog columns. It was replaced because *Required* against
*Applied* already shows the over-shoot, and because the difference of the two
printed medians is not the median difference (432 − 80 = 352, while the median
of \(d-d^{*}\) is 320). Both are still emitted.

#### The block labels carry only the condition

Both blocks label a condition with its name and nothing else. Two quantities have
been evicted from these labels in turn: the per-run responsiveness cost —
18.1/24.5 and 9.8/29.7 per cent of a run's elapsed time at P50/P95 — and then the
required-set share. Neither is a per-decision quantity, so neither belongs in a
row of per-decision medians, and **both are now the RQ3 prose's**. Say the cost
is "visible but bounded"; never "negligible".

There is a mechanical reason too. A block label is a single unwrappable line in
an `l` multicolumn spanning every column, so its natural width is a floor on
`sum(p-widths) + 2n·tabcolsep`. A label approaching `\columnwidth` drives
`\fittabcolsep` to a tabcolsep near zero and every data cell in the block then
touches its group rule; an earlier revision carried the cost on (b)'s labels and
did exactly that.

Emitted as `data/rq3/estimator/sizing_summary.csv`, except the per-run cost,
which is `burstDelaySharePercent` in `data/rq3/policy/summary.csv`.

### Why there is no figure

The deleted figure had three panels. Its two scatter panels plotted the queued
pricing error against the backlog error, which is a relation this document
already calls close to definitional, and the class separation they showed is
printed directly by the table's estimator-error column. Its ECDF panel carried
the one claim the table could not: the two estimators differ in **shape**, not
only at P50. That claim now lives in the table note as the population
P05/P50/P95 of both errors, which makes it checkable without the plot.

Do not write that the Draft reserve error sits almost entirely above zero. Its
24MP P05 is \(-129\) ms, so that phrasing holds for 12MP only.

## Printed terminology

The table prints only terms the manuscript already uses elsewhere. This document, the generated CSVs, and `scripts/rq3_coordination_*.py`
keep the older analysis vocabulary, so use this map when moving between them.

| Printed in the table | Used in this document, the CSVs, and the scripts |
|---|---|
| pacing decision | transition (one shot-to-shot interval; a 30-capture run holds 29) |
| run | burst (one complete 30-capture session) |
| required delay | envelope, \(d^{*}\) |
| unapplied \(d^{*}-d\) | potential avoided delay (flexible band), `shortfall_ms` (mandatory-floor block) |
| skipped optional work (no longer printed) | demotion (Bokeh+Filter → Filter only → Encoding only) |
| \(d>0,\ d^{*}=0\) | the *no_delay_required* class. Printed in (b) only. Was *None required* |
| \(d\ge d^{*}\) | the *covered* class. Was *Full requirement*, and *Covered in full* before that |
| \(d^{*}_{\mathrm{man}}\le d<d^{*}\) | the *flexible* band. Was *Mandatory work*, and *Left to admission* before that |
| \(d<d^{*}_{\mathrm{man}}\) | the mandatory-floor block. Was *Less than mandatory* |
| decision-time error | the two estimator errors, \(\hat{C}-C\) and \(\hat{B}-B\); printed as a share of \(C\) and of \(B\), kept in ms in this document and in both CSVs |
| inside \(B\) | the share of the applied delay overlapping outstanding backlog |
| Slack | realized margin |
| this / next Draft | target / next |
| Draft reserve error | `draftSequenceReserveErrorMs`, \(\hat{C}-C\) |
| backlog error | `backlogEstimateErrorMs`, \(\hat{B}-B\) |
| Draft pricing error | derived from `draftOccupancyUnderpriceMs`; see below |
| queued Draft pricing error (no longer printed) | the same, summed over the Drafts queued ahead |

The three error names are new because the quantities are new. Each is named
after the implementation column it comes from, and all three are signed
**estimate minus realized**, so a positive value always means the controller
reserved more than the pipeline used. Do not flip the sign of one of them for
local convenience.

*Budget left* is no longer printed. It named the negated pressure that the
withdrawn 40% band was cut on, and the current table states the same
information as the required delay itself.

The printed terms are anchored in the rest of the paper: *budget* is in the
paper title and Section~2.4, *run* and *capture* are the units of the RQ1
tables, *Skipped* is RQ2's column, and *Draft*, *optional work*, and *mandatory*
come from Section~2.3.
Do not reintroduce *spare*, *transition*, *burst*, *target*, *demotion*,
*shortfall*, *envelope*, or *retrospective* into printed labels or body text.

**Slack, not deadline margin.** Table~\ref{tab:rq1_end_to_end_summary} already
prints this quantity as `Slack P5 (%)`, and an earlier revision of the RQ3 table
called the same quantity `Deadline margin`, which gave one quantity two printed
names in one paper. Every printed instance is now `Slack`: RQ3, the case-study
table's row label in `tables/tab_casestudy_selection.tex`, and the margin panel's
axis in `figures/fig_casestudy_12mp.tex`. *Deadline margin* survives only as the
name used in this document and in the CSV column `deadline_margin_p5_pct`. Do not
reintroduce it into a label.

**No Greek for the overlap share.** A draft briefly printed \(\rho_B\) for the
share of \(d\) that elapsed against outstanding backlog. \(\rho\) appears nowhere
else in the manuscript or in `macros.tex`, so it put a new symbol, defined only
in a `\tiny` note, on a quantity the words already name. The column is headed
`inside B`.

**The classes are no longer named at all.** Column one of both blocks prints the
inequality that defines the row. Successive revisions argued over what each name
asserted — *Left to admission* claimed a hand-off the table shows no evidence
for, *Below the mandatory floor* sent a reader out of the table to find out what
the floor was — and an inequality asserts exactly the cut and nothing else. It
also deletes three glosses from the note. This document and the CSVs keep the
`covered` / `flexible` / `below_floor` keys and the *floor* vocabulary; the map
above is the bridge. Use `\mathrm` for the subscript in LaTeX: `d^{*}_{man}` sets
*m*, *a*, *n* as three math variables and measures 7pt wider.

Units live in the group headers, `(ms)` and `(%)`. **\(d^{*}\) is no longer
defined in the table** — the caption is one line, and the RQ3 prose carries
\(d^{*}=\lceil[B+2C-\max(0,T)]^{+}/2\rceil\). That prose must introduce it before
the table is read; if it ever drops the formula, put it back in the note beside
\(d^{*}_{\mathrm{man}}\), not in the caption.

**The note's admission rule.** It carries only what a printed cell cannot be read
without, which is now four things: the gloss on \(d^{*}_{\mathrm{man}}\), which
appears as a row label; what the two `(%)` error columns are a share of, and that
each ratio is per decision before the median; which population each error column
is a median over, class-wide in (a) and paced-only in (b); and \(d/B\) with
*inside* \(B\). That is the whole note — three sentences.

A finding is not a reading aid. If a cell stays legible without the sentence, the
sentence is prose — that test evicted the per-run pacing cost, the "no analyzed
run produced an observed Capture Timeout" clause, and finally the thin-slack
tail, and it is what took this note from nine lines to three. Anything readded
has to pass it.

**The thin tail was the hard case, and it left.** It was kept through one round
on the argument that it is how `Slack P5` is read rather than a finding beside
the table. That argument does not survive checking which population the number
belongs to. The 0.11% is the minimum of the *no-delay-required* class, which (a)
excludes and (b) prints no Slack column for — so it is the minimum of **no column
the table prints**, and 6 of the 11 sub-1% decisions sit in that same unprinted
class. On the rows (a) does print, P5 understates the class minimum by 1.03x to
4.1x:

| Printed row | class min | `Slack P5` |
|---|---:|---:|
| 12MP \(d\ge d^{*}\) | 0.31 | 1.03 |
| 12MP \(d^{*}_{\mathrm{man}}\le d<d^{*}\) | 1.91 | 2.61 |
| 24MP \(d\ge d^{*}\) | 0.61 | 2.48 |
| 24MP \(d^{*}_{\mathrm{man}}\le d<d^{*}\) | 0.51 | 1.20 |
| 24MP \(d<d^{*}_{\mathrm{man}}\) | 4.39 | 4.53 |

The 65x gap that once justified keeping it — 0.11 against 7.20 — is min against
P5 *within the unprinted class*, not a gap in anything the reader sees. So the
printed column is not being misread without the sentence, and the tail is a
finding. It is still an important one: `AGENTS.md` now puts it in the RQ3 prose
with the saturation context and the claim limit attached, and the requirement
that it never stand as a bare number.

**Which quantity gets which unit.** The rule protects one thing: the Capture
Timeout budget is an internal constant and must not be recoverable, which it
becomes the moment a single quantity is printed both in milliseconds and as a
share of the budget. So: delays in ms, slack as a share of the budget, the two
estimator errors as shares of \(C\) and \(B\), \(d/B\) and *inside* \(B\) as
shares of the backlog, pacing cost as a share of run time. A share of \(C\) or
\(B\) is not a leak — neither is the budget, and neither is printed absolutely
anywhere in the paper — which is why the errors could move to per cent while
*Unapplied* stayed in ms. *Slack* may never gain a millisecond column.

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
complement of the required set; the other three partition it. `outcome_matrix.csv`
carries one row per class. The table does **not** print all four as rows: (a) is
the required set alone, so its percentages are not diluted by the complement, and
the complement appears only in (b), restricted to the paced. The totals stay
checkable from the denominators the two blocks print — see *Why (a) prints no
"none required" row, and how the totals stay checkable* above.

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
over-covers: across the class that required no delay at all the median reserve
error is +230 ms and +250 ms, and on the 350 and 374 of them that pacing did act
on it is **+555 ms and +653 ms**, at a median applied delay of 377 ms and 252 ms.
Quote the second pair when explaining why pacing fires on 19.0% and 21.7% of
decisions that required nothing — the first pair is a median over a population
that is 81% and 78% unpaced. State this as a design choice with a measured price,
not as an unexplained excess.

**The backlog clock under-covers in its tail, because a point price is summed.**
`CaptureAvailablePacingSession.queuePacingDecision` advances \(\hat{B}\) by each
queued Draft's **point** prediction plus one learned between-node overhead. Per
Draft that is nearly right — the pricing error is +16 ms and +19 ms at P50 — but
widely dispersed, −135 ms and −293 ms at P05. Unlike the reserve it is summed
over the queue, so the dispersion accumulates. Summing the per-Draft pricing
error over the Drafts queued ahead of a decision reproduces that decision's
backlog error at Pearson \(r=0.95\) and \(0.88\).

The class contrast is the evidence. Every value below is a median over the
**whole class**, which is the population for the question "why did this class
receive less than it required"; for the complementary question, see the paced-only
figures above. Milliseconds here, per cent in the table; the normalised gradient
is in the last column and it survives the change of units.

| Class | Queued pricing error P50 | Backlog error P50 | Reserve error P50 | Backlog error P50, printed |
|---|---:|---:|---:|---:|
| No delay was required | +27 / +9 ms | −19 / −43 ms | +230 / +250 ms | −1.3 / −2.8% |
| Covered by pacing alone | +25 / −46 ms | −4 / −68 ms | +308 / +487 ms | −0.1 / −1.6% |
| Part left to admission | −627 / −930 ms | −677 / −980 ms | +80 / −9 ms | −12.8 / −19.8% |
| Below the mandatory floor | — / −1,278 ms | — / −1,392 ms | — / +31 ms | — / −29.6% |

The decisions pacing covered look exactly like the population. The decisions
where it fell short are the ones whose queue accumulated 0.6–1.3 s of optimism.
Read down the backlog column the gradient is the mechanism — −19, −4, −677,
−1,392 ms — and the top row is the only one where restricting to the paced
changes it materially, because it is the only class that is mostly unpaced.

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

The table no longer prints a skip column at all; see "Why no skip column is
printed" below. The audit is still generated, and these are its two observed
actions for admission-flexible transitions:

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

### Why no skip column is printed

An earlier revision printed the this-Draft rate as a table column. It was
removed for three reasons, in order of weight.

**It cannot answer the question it appears to answer.** The question a reader
puts to the floor row is why 11 of its 14 decisions went unpaced. The floor is
defined on \(C_{mand}\), which already excludes optional work, so a skip cannot
close a mandatory-floor deficit — yet printed beside "Paced 3" a 100% skip rate
invites exactly that inference. The row already answers the question without it:
"Paced 3" beside a backlog error of \(-1{,}392\) ms says the backlog clock was
1.4 s low, and the estimator column reads \(-19\), \(-4\), \(-677\),
\(-1{,}392\) down the rows, so the mechanism is a visible gradient rather than an
assertion.

**It argued against its own claim at 12MP.** The flexible band's this-Draft
rate, 26.9%, is *below* the 42.4% population rate: admission did not step in
more often there. That must be reported plainly — the deadline held anyway,
which is what the margin column is for — rather than by selecting the horizon
that makes coordination look stronger.

**Both horizons are ambiguous.** Demotion is **session-sticky**: pooled over the
analyzed decisions, this-Draft and next-Draft skips co-occur 807 and 779 times
against 2 and 5 this-Draft-only, and the 50 and 51 next-Draft-only cases are the
onset shots. The two-Draft rate is therefore close to "had this run already
entered the demoted regime", and the 100% on the floor row is largely that.

`skipped_this_pct` and `skipped_either_pct` in
`data/rq3/estimator/outcome_matrix.csv` keep both rates for every class. If a
reviewer asks whether admission was engaged on the floor misses, the answer is
14/14 target Drafts demoted, and it belongs in prose with the "does not close the
deficit" clause attached.

## The thin deadline-margin tail, and why the minimum stays printed

The minimum realized margin on the largest class is **0.11% of the budget**.
Printed alone that reads as "no Capture Timeout was luck", so the tail has to be
characterised rather than trimmed. A proposal to drop the minimum and keep only
P5 was rejected: on the largest class the two are 0.11% and 7.20% — a factor of
65 — so P5 alone hides the worst observation in the collection, while on the
14-decision floor block they are 4.39 and 4.53 and the minimum adds nothing.
Which statistic carries the tail depends on \(n\), and an industrial reader asks
for the worst case first.

**Where it is printed.** The class rows carry P5 only; the minimum is stated in
the table note, as the *tightest* of the eleven sub-1% decisions, in the same
sentence as the tail count and the backlog context that explains it. That is the
resolution of the two constraints, and both halves are binding: the redesign
brief asked for the min *column* to go, because per class it is one execution and
is not always the statistic that carries the tail, while `AGENTS.md` requires the
worst observation itself to stay printed. A sentence can carry a number together
with the condition under which it is informative; a column cannot. Do not restore
the column, and do not drop the 0.11% from the note.

Eleven of the 3,781 analyzed decisions finished under 1% of the budget — 6 at
12MP and 5 at 24MP; the per-class counts are `deadline_margin_under_1pct` in
`outcome_matrix.csv`. On all eleven:

- the backlog \(B\) at the decision was **42–79% of the budget**, and the queue
  wait alone consumed **31–75%** of it, so the margin is thin because the
  pipeline was already nearly full of budget-consuming work;
- **ten of eleven were paced**, at 288 to 921 ms; and
- **eleven of eleven had pacing or an optional-work skip engaged.** There is no
  case in this tail where neither control acted.

The tightest is 8 ms at 12MP, run 2#21 shot 10 at overheat level 5: 785 ms of
pacing applied *and* optional work skipped, with a required delay of zero. The
reservation was satisfied; the rest of the budget went to a 2,614 ms wait against
a 3,369 ms backlog. The eleven are not a random draw either — they are the
saturated states, either late in a burst (24MP run 1#2 shots 29 and 30, backlog
at 79% and 76% of the budget) or at overheat 5–6.

Do **not** claim from this that the realized margin was bounded, that the
controller guaranteed the deadline, or that a baseline would have timed out on
these eleven. The last is an RQ1 question and belongs to the controller-off and
pacing-only arms of the RQ1 ablation. The supportable statement is that the thin
tail is 0.29% of decisions, that it coincides with a nearly exhausted budget
rather than with controller inaction, and that both controls were engaged
throughout it. **The RQ3 prose has to make that statement itself** — the table
note carried a short form of it through one revision and no longer does, for the
population reason given under *The note's admission rule* above. Do not weaken it
into "negligible", and do not let the 0.11% appear without the saturation context
in the same breath.

### Where the thin tail sits relative to the guard-bypassed baseline

There is one further observation, and it is the strongest available answer to
"then no timeout was luck" — but it must be stated as an association across arms,
never as a matched counterfactual.

All six 12MP thin-margin decisions sit at or within two captures of the *earliest
first-timeout index* that the guard-bypassed baseline reaches at their own
starting overheat level in Table~\ref{tab:timeout_index} (M+S, normal capture):

| Overheat | Baseline earliest / median first timeout | Thin-margin decisions here |
|---|---:|---|
| Lv3 | 13 / 18 | capture 13 |
| Lv5 | 8 / 10 | captures 8, 9, 10, 10 |
| Lv6 | 7 / 9 | capture 9 |

So the thin tail is not scattered: it lands exactly on the states where the
uncontrolled pipeline fails outright, and there the controlled runs completed
instead — the tightest with 8 ms in hand.

The caveats are load-bearing. The two populations are **different arms**: the
Table~\ref{tab:timeout_index} figures are guard-bypassed trials without the
controller, and the RQ3 population is Full-controller runs. The correspondence is
therefore between *shot index and overheat level*, not between paired executions.
Write it as "the thin tail coincides with the states where the guard-bypassed
baseline first times out", and leave the causal claim to the RQ1 ablation arms.
Do not write that any of the eleven "would have" timed out.

All eleven are emitted, one row each, as
`data/rq3/estimator/thin_margin_tail.csv`, so every number in the paragraph above
is checkable without rerunning an ad-hoc query. The generator asserts that the row
count matches the sum of `deadline_margin_under_1pct` across the classes.

## Mandatory-floor audit

No 12MP transition fell below \(d^*_{mand}\). Fourteen of 140 positive-envelope
24MP transitions did, clustered in four bursts:

- 11/14 received zero delay;
- admission demoted 14/14 target Drafts;
- online backlog was below subsequently realized backlog in 14/14, by a median
  of 1,392 ms, against a queued pricing error of −1,278 ms;
- thermal headroom rose during queue residence in 12/14;
- median decision-to-Draft-start queue residence was 4.71 s
  (`floorMissWaitMsP50`; an earlier revision of this document printed 4.78 s,
  which the generator does not produce);
- the minimum realized margin was **4.39% of the budget**, and the class P5 is
  4.53% — the *largest* minimum of any class in `outcome_matrix.csv`, and the
  largest P5 of the three classes the table prints; and
- 0/14 produced an actual Capture Timeout.

The floor is a retrospective sufficient reservation condition, not the actual
timeout boundary, and the margin row is the direct evidence: the decisions that
missed the floor are the ones that finished with the most budget to spare.
Because \(d^*_{mand}\) already excludes optional work, target demotion documents
coordination but does not itself erase the mandatory-floor deficit. Backlog
under-estimation and rising headroom are observationally consistent with
queue/thermal drift after the online decision; do not claim causality from this
trace split.

### The 11 that received no delay at all

`data/rq3/estimator/floor_zero_delay_account.csv` accounts for these row by row,
and it is the direct answer to why pacing did not act. What the deployed formula
was given at the decision, \(\hat{B}+2\hat{C}-T\), is **non-positive on 11 of
11** (\(-46\) to \(-1{,}729\) ms): zero was that formula's correct output for
its inputs, not a failure to evaluate it. The difference between that view and
the realized mandatory pressure decomposes exactly into \((B-\hat{B})\) and
\(2(C_{mand}-\hat{C})\), and the generator asserts the three sum back to
\(2d^{*}_{mand}\) within 2 ms. Correcting the backlog clock alone flips the
sign on 11/11 and reaches the floor on 9/11.

Do **not** explain these decisions with the skipped-optional-work column. The
floor is defined on \(C_{mand}\), which already excludes optional work, so a
skip cannot close a floor deficit; and the 14 misses fall in four bursts of a
session-sticky demotion regime, which is most of what the 100% rate is
measuring. The estimator terms are the explanation; the margin row is why
nothing broke.

An earlier column named `backlog_term_sufficient` tested
`backlog_term > -(saw + reserve_term)`, which reduces to `account > 0` and is
true for every below-floor decision by the class definition. It was replaced by
`backlog_flips_sign`. Do not reinstate a tautology as evidence.

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
the margin identity. The fourth produces everything else the table prints:
the outcome matrix, the block (b) sizing comparison, both estimator error
distributions, the floor repricing, and the row-by-row account of the zero-delay
floor misses. Only the first needs `openpyxl`; the rest use the standard
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

- every population is cut by \(d^{*}\), and the analyzed totals are recoverable
  from the denominators the two blocks print: 1,841 + 79 = 1,920 in (b) and (a)'s
  12MP label, 1,721 + 140 = 1,861 for 24MP;
- the identity \(d-d^{*}=(\hat{C}-C)+(\hat{B}-B)/2\) is asserted in the
  generator and closes to 0.8 ms, and the caption states it;
- the class contrast in the estimator-error columns is the mechanism, and the
  population P05/P50/P95 — which the RQ3 prose carries, not the note — shows the
  two estimators differ in shape and not only at P50;
- every count in the exhibits is reproducible from the four commands above; and
- each claim that could be read as counterfactual — the repricing, the missing
  delay, the queued pricing error — carries its qualification in the caption,
  not only in this document.
