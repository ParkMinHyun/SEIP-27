# RQ evidence

Single reference for the evaluation evidence layer: how every RQ number is
measured, what the current pacing analysis established, what the 2026-08-11
restructure removed, and which files have to travel together.

This file replaces four separate documents, which are preserved below as parts
in their original wording. Cross-references between them now read "Part N of
this document".

| | Part | Covers | Replaces |
| --- | --- | --- | --- |
| Part 1 | [Current RQ3 Design and Interpretation](#part-1--current-rq3-design-and-interpretation) | the current pacing handoff | was `docs/rq3-current.md` |
| Part 2 | [RQ1--RQ3 Measurement and Excel Aggregation Guide](#part-2--rq1--rq3-measurement-and-excel-aggregation-guide) | the measurement guide | was `docs/rq1-rq3-metrics-guide.md` |
| Part 3 | [RQ restructure of 2026-08-11 — what changed and how to put it back](#part-3--rq-restructure-of-2026-08-11--what-changed-and-how-to-put-it-back) | the restructure record | was `docs/rq-restructure-2026-08-11.md` |
| Part 4 | [RQ3 File Manifest](#part-4--rq3-file-manifest) | the transfer manifest | was `docs/rq3-file-manifest.md` |

## Reading the RQ numbers

The manuscript has four research questions. Everything under `docs/`, `data/`
and `scripts/` — including the part titles below — still uses the older
three-RQ numbering as internal compatibility names, the same treatment the CSV
fields containing `required` get. Translate as you read; do not rename.

| Manuscript | Question | Called here |
| --- | --- | --- |
| RQ1 | End-to-end effectiveness | RQ1(a) |
| RQ2 | Control-loop contribution | RQ1(b) |
| RQ3 | Admission decision quality | RQ2 |
| RQ4 | Pacing-delay sizing | RQ3 |

`AGENTS.md` is the authority for the project rules that govern this evidence.
Where a statement here conflicts with it, `AGENTS.md` wins.

Where a passage below sends you to an exhibit's "comment header", read that as
its section in `docs/exhibits.md`. The `tables/` and `figures/` sources no
longer carry commentary; each holds a single pointer line instead.

## Part 1 — Current RQ3 Design and Interpretation

This document is the authoritative handoff for the current RQ3 design. It
supersedes the earlier four-policy design documented in historical collection
notes in Part 2 of this document.

### Research question

RQ3 asks whether the Budget-Aware Draft Controller computes an
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
4. whether the resulting wait drains measured backlog at a reported
   user-visible cost.

Property 3 is the one earlier revisions were missing. They could report that the
short-fall decisions under-estimated backlog but not what produced the
under-estimate, which reads as a model-quality complaint rather than as a
mechanism. It is now measured, and it is the finding an industrial reader can
act on.

#### No threshold the reader cannot recompute

Every population in the current table is cut by the retrospective matched-policy
target \(d^{*}\)
itself. It prints no band edge, no "over 40% budget left", and no constant that
is not derivable from the two formulas below. An earlier revision printed a 40%
cut inherited from the historical selectivity exhibit, which the current table
does not ship; a reader had no way to know where it came from.

### Current artifacts

The current main-paper exhibit is `tables/tab_rq4_pacing_selectivity.tex`, and
it is the only RQ3 exhibit; RQ3 ships no figure. It replaced
`tables/tab_rq4_pacing_summary.tex` on 2026-08-13, which stays on disk
unreferenced; an earlier generation of policy, selectivity, and calibration TeX
pairs — not the current selectivity table — was removed outright. The blocks
described in the rest of this part were written for the summary table; read
them as the analysis behind the RQ4 claim, not as a description of the printed
exhibit.

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

#### Why (a) prints no "none required" row, and how the totals stay checkable

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

#### Layout constraints that are easy to re-break

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

#### Block (b): why "enough" is not the whole claim

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

##### The two error columns appear in both blocks on purpose

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

##### The block labels carry only the condition

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

#### Why there is no figure

The deleted figure had three panels. Its two scatter panels plotted the queued
pricing error against the backlog error, which is a relation this document
already calls close to definitional, and the class separation they showed is
printed directly by the table's estimator-error column. Its ECDF panel carried
the one claim the table could not: the two estimators differ in **shape**, not
only at P50. That claim now lives in the table note as the population
P05/P50/P95 of both errors, which makes it checkable without the plot.

Do not write that the Draft reserve error sits almost entirely above zero. Its
24MP P05 is \(-129\) ms, so that phrasing holds for 12MP only.

### Printed terminology

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

### Population and data-quality rule

The summary analysis uses the Full controller workbooks:

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

Complete 30-shot runs are required. The current summary population contains 70
12MP-normal bursts and 69 24MP-memory-pressure bursts, producing 1,920 and
1,861 analyzed transitions. A transition additionally requires a recorded
pacing decision and a complete prior-Draft timeline. Watchdog-truncated
transitions lack a complete realized Draft duration and are excluded from the
envelope reconstruction for that reason.

### Envelope definitions

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
by that delay. The policy deliberately applies half of the positive projected
deficit so pacing does not convert all residual pressure into user-visible
delay, relying on node-time admission to skip optional work when its suffix
bound exceeds the live budget. This is an intuitive coordination heuristic, not an
exact fixed-point derivation or a literal transfer of a half-deficit value to
admission.

Accordingly, \(d^{*}\) is the retrospective target obtained by applying the
deployed heuristic to realized \(B\) and \(C\). It is not a physically required,
minimum, or globally optimal delay. Generated fields and class keys that contain
`required` retain their historical names for artifact compatibility.

### The outcome matrix

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

#### The overrun population is strict

Retained because `scripts/rq3_pacing_summary_metrics.py` still emits it for the
historical selectivity exhibit; the current pair no longer prints a pressure
band at all.

"No budget left" and "required a delay" must be the same set. Pressure is
\(B+2C-\max(0,T)\) and \(d^{*}_{exec}=\lceil \text{pressure}/2\rceil\), so a
decision at exactly zero pressure needs no delay and is not an overrun. Both
populations are therefore **pressure > 0**: 79 at 12MP and 140 at 24MP.

`rq3_pacing_summary_metrics.py` keeps its half-open `[0, inf)` pressure *band* unchanged,
because the historical exhibit bins a shape and must leave no value unbinned,
and carries a separate strict cut `OVERRUN_PCT` for everything else. The two
forms differ on one decision in this collection, 24MP run 2#27 capture 28 at
pressure 0.0 ms; a revision that mixed them printed 141 against 140 in one
table.

### Where the applied and required delay differ

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

#### The asymmetry is the actionable finding

The controller already knows to price a single Draft by a conservative
statistic, and prices a whole queue by a central one. A central statistic is the
right thing to charge for one Draft and the wrong thing to sum over a queue.
That is the design lever this evaluation identifies; it is not a claim that
changing it would have prevented anything, which the closed-loop objection below
forbids.

#### Two limits on this decomposition

- The relation between the backlog error and the queued pricing error is close
  to **definitional**, because the backlog clock is that sum. Its value is that
  it localises the whole backlog error in the per-Draft price and rules out
  other contributions, and that the outcome classes separate along it. Do not
  present \(r\) as a discovery.
- The queue is reconstructed offline from the Draft timeline rather than read
  out of the controller's FIFO, so the regression slope is 0.84 and 0.79 rather
  than 1. The vertical spread in the figure is what that reconstruction does not
  capture.

### Actual admission-action audit

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

#### Why no skip column is printed

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

### The thin deadline-margin tail, and why the minimum stays printed

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

#### Where the thin tail sits relative to the guard-bypassed baseline

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

### Mandatory-floor audit

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

#### The 11 that received no delay at all

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

#### The floor repricing

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

#### Where the retained margin came from

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

### Why no alternative-policy or scaled-delay baseline is required

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

### Reproduction

Run from the repository root:

```text
python3 scripts/rq3_pacing_summary_metrics.py sampling  # requires openpyxl
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
Part 4 of this document.

### Supported manuscript conclusion

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

#### What a reviewer should be able to check without asking

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

## Part 2 — RQ1--RQ3 Measurement and Excel Aggregation Guide

> **This document uses the pre-2026-08-11 RQ numbering throughout.** The
> manuscript now has four research questions. Translate as you read:
> RQ1(a) → **RQ1**, RQ1(b) → **RQ2**, RQ2 → **RQ3**, RQ3 → **RQ4**. The names
> here are kept as internal compatibility names so they continue to match the
> script and CSV field names they document; see the numbering table in
> `AGENTS.md`.
>
> Two metric definitions below are also superseded for the manuscript, though
> they remain correct as definitions and the values are still recoverable:
> RQ1(a) no longer prints Slack P5, the M+S pair, the cumulative-delay pair, or
> the Kaplan–Meier median first-timeout index — its Timeout onset column is now
> the earliest index alone — and it prints M, S and Activated as per-run counts
> rather than percentages. Every removed value, and the reason the requested
> arithmetic-mean onset could not be computed, is in
> Part 3 of this document.

### 1. Purpose and scope

This document defines what RQ1--RQ3 evaluate, what each reported metric
means, and how to derive the paper tables and figures from workbooks produced
by `CaptureMetricsExcelExporter`.

The definitions were checked against:

- paper commit `d181dea3ce5bfbe37bb4568edeade3b6aa9101e6`;
- implementation commit `cdd524fbd86e390446cbbd15c0e4f7923d4f1c58`;
- `CaptureMetricsExcelExporter.kt`;
- `data/rq1_metrics_aggregation.md`;
- `data/rq2_metrics_aggregation.md`.

The current RQ3 no longer uses the four-policy comparison as its main-paper design.
The authoritative RQ3 handoff is Part 1 of this document, and the generated
coordination-artifact dictionary is `data/rq3/coordination/README.md`. Legacy
`pacingPolicy` fields and four-policy aggregation material remain below only as
historical collection notes; do not use them to frame or regenerate the current
RQ3 summary.

### 2. Research-question overview

| RQ | Research question | Main evidence |
|---|---|---|
| RQ1 | Does the coordinated controller prevent Capture Timeout while preserving optional Draft functionality at acceptable intervention cost? | End-to-end ablation and full-controller behavior |
| RQ2 | Does admission retain optional work that can safely complete and reject work that would exceed its remaining budget? | Factual admitted outcomes and an Always-admit audit |
| RQ3 | Does the controller compute an appropriately sized pacing delay for the Draft backlog and Capture Timeout budget? | Targeting, boundary diagnosis, admission-aware envelope partition, actual admission action, work conservation, and responsiveness cost |

The intended argument is:

1. **RQ1 establishes end-to-end effectiveness.**
2. **RQ2 isolates the quality of workload control (admission).**
3. **RQ3 isolates the quality of arrival control (pacing).**

### 3. Common definitions and aggregation rules

#### 3.1 Workload notation

- \(M\): the lightweight multi-frame Draft stage, operationalized by the
  Bokeh/PORTRAIT admission group.
- \(S\): optional single-frame Draft processing, operationalized in the
  current RQ1 aggregation by the Filter completion marker and in RQ2 by the
  selected Filter admission-decision row.
- \(B\): the remaining deadline budget at an admission decision.
- \(C\): the factual remaining wall time from the selected Bokeh or Filter
  node start to Draft completion.
- \(C_{\mathrm{model}}\), \(B_{\mathrm{model}}\): \(C\) and \(B\) with the
  model's own skips honoured. They are **never** the classifier — every reported
  cell uses \(C\) and \(B\) — and exist only for the outcome interpretation in
  section 5.4, which asks whether a shipped build would have emitted the
  overrun. They coincide with \(C\) and \(B\) outside the always-admit audit.
- \(d_i\): the pacing delay associated with shot \(i\). In the current
  aggregation convention, this delay gates the transition to shot \(i+1\).
- \(B_i^{real}\): the measured Draft backlog at a pacing decision.
- \(Q_i^{real}\): the measured number of earlier Drafts waiting to start at a
  pacing decision.

#### 3.2 Experiment-run reconstruction

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

#### 3.3 Shot-to-transition mapping

A 30-shot run has 29 reportable transitions. The delay associated with the
final shot is excluded from:

- pacing activation rate;
- positive-delay percentiles;
- cumulative session delay.

The exporter provides `delayAppliesBeforeShotIndex` and
`transitionDelayMs` so this mapping does not need to be inferred again.

#### 3.4 Percentiles

Use inclusive percentile interpolation, equivalent to Excel
`PERCENTILE.INC`. Do not calculate a displayed percentile from previously
rounded values.

#### 3.5 Valid-run policy

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

#### 3.6 Workbook manifest

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

### 4. RQ1: End-to-end controller effectiveness

#### 4.1 Research question

> Does coordinating remaining-work admission and capture pacing prevent
> Capture Timeout while retaining optional Draft functionality and limiting
> pacing intervention?

RQ1 has two parts.

#### 4.2 RQ1(a): Full-controller behavior

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

#### 4.3 RQ1(b): Controller ablation

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
one run per condition. Each row therefore also reports retained optional work,
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

#### 4.3.1 Data sources and balancing

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

#### 4.4 RQ1 workbook mapping

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

### 5. RQ2: Admission decision quality

#### 5.1 Research question

> Does admission execute optional work when it can finish within the remaining
> budget and reject it when execution would exceed that budget?

RQ2 selects:

- **Multi-frame:** the exact Bokeh admission-decision row;
- **Single-frame:** the exact Filter admission-decision row.

Exactly one selected decision row per capture contributes to the capture-level
admission metrics.

#### 5.2 Controller-enforced metrics

##### Run share

```text
Run share
    = 100 * decisions that run / all selected decisions
```

This measures feature availability, not correctness by itself.

##### Model-decision path and skip shortfall

Each selected decision belongs to exactly one admission-path leaf:

```text
run:
    beforeEffectiveAdmit == true

model skip:
    beforeAdmissionSkipReason == "upper bound"

policy skip:
    beforeAdmissionSkipReason == "session demotion"
```

The table omits a separate total column because the three path counts reconstruct
it. Each count carries its share of the row total; run, model skip, and
policy-skip counts must sum to that total in every row. A session demotion is
sticky policy state inherited from an earlier decision; it is not a new
upper-bound test at the current decision. A model admit is the recommendation
before session policy and equals run plus policy skip.

For each model skip, let (U) be `beforeSequencePredictedUpperBoundMs`, (B) be
`beforeBudgetMs`, and (D) be the configured Capture Timeout deadline:

```text
modelSkipShortfallPct = 100 * (U - B) / D
```

The `Shortfall` column reports the median of this positive, deadline-normalized
quantity over model skips only. It excludes session demotions. This is the
severity of the controller's predicted rejection, not a realized overrun:
skipped work has no factual suffix cost in the controller-enforced run.

##### Run outcome: safe / watchdog containment

For each decision that ran:

```text
safe:
    no watchdog and C <= B

watchdog-contained:
    watchdog invoked
```

Here, `B = beforeBudgetMs` and
`C = draftEndUptimeMs - nodeStartUptimeMs`. The table's separate `Safe` and `WD`
columns report the two counts within Run. The current controller-enforced set
has neither a missing `C` nor a non-watchdog `C > B`, so the two counts partition
Run. A watchdog-contained Run is an admission-safety exception even when the
capture retains positive deadline margin. Report it as shipped containment, not
as proof that the watchdog counterfactually prevented a Capture Timeout.

`beforeBudgetMs` is the time left until the Capture Timeout deadline at that
node, so \(C > B\) and the capture timing out are the same event. In the three
audit workbooks every one of the 154 over-budget decisions belongs to a capture
that timed out. Do not present the unsafe-admit count as a proxy for timeouts;
it is the timeout attributed to the decision that caused it.

##### The controller-enforced run set

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

#### 5.3 Always-admit audit metrics

The audit forces optional work to execute while a shadow controller records
the model decision it would make before applying session-sticky
demotion. This supplies factual outcomes for both model-admitted and
model-skipped work without attributing later policy-carried skips to the model.

##### Score the decision as measured

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

##### All-decision confusion matrix

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
session-policy state to the model decision.

##### The audit decision set

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

##### Median margin and overrun for model-skipped work

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

The table labels the two severity columns `Margin` and `Overrun`; its common
note defines both as P50 magnitudes. The factual-class header and the divider
after `Admitted` establish that both columns describe model-skipped work, so the
cells print unsigned magnitudes without repeating `residual`, `prevented`, or
`P50` in every header. A large margin indicates severe over-conservatism,
whereas a large overrun indicates that the rejection identified a substantial
deadline violation. The deadline
constant is internal and must not appear in the manuscript; report only the
normalized percentage, consistently with RQ1's Slack P5.

Because the confusion matrix already reports the feasible and unsafe skip
counts, the table does not repeat their proportions or sample sizes in the
median cells. These median values describe the typical capture-level decision effect; they
are not inferential estimates over independent runs.

#### 5.4 RQ2 figure metrics: unsafe-admit spike anatomy

`figures/fig_rq3_unsafe_spike_anatomy.tex` characterizes every decision in the
unsafe-admit cell of the confusion matrix: factually unsafe, model-admitted,
drawn from the included runs only. It answers two questions per decision — how
far the measured cost exceeded the preceding capture and the model's own
bound, and which `PostExecutionMetrics` quantity accounts for that excess.

##### Preceding-capture baseline

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

##### Node suffix

Every per-node quantity is summed over the *remaining* nodes of the capture:
node rows whose `nodeOrder` is at least the selected decision's `nodeOrder`,
taken in `nodeOrder` order. This is the suffix that \(C\) measures in wall time,
so the panels and the label describe the same execution.

##### Panel (a): overshoot against the budget

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

##### Panels (b) and (c): the two measured quantities behind the latency

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

##### What `cpuTimeMs` covers

`CpuProcessingTracker` documents its run-queue and context-switch counters as
thread-level and its CPU-usage counter as not thread-level. Consistently with
that, `cpuTimeMs` regularly exceeds `wallTimeMs` for the same node (2,117 ms of
CPU over a 1,669 ms window in the largest Multi-frame spike). Read `cpuTimeMs`
as the camera process's total CPU consumption during the node window, not as
the node thread's own work, and read `cpuTerm` as added CPU demand inside the
process — which includes concurrently executing Draft work.

##### Control signals to recompute, not assume

Report the same baseline-versus-event comparison for `overheatLevel`,
`thermalStatus`, `blockingGcTimeMs`, `runQueueWaitMs`, and
`nonvoluntaryCtxSwitches`. In the current workbooks the first three separate
nothing — thermal state is identical to the baseline in all eight cases and
blocking GC time is zero throughout — while the last two move in both
directions. That asymmetry is the figure's argument and the reason a static
thermal threshold cannot anticipate these decisions, so it must be recomputed
whenever the workbooks change rather than carried forward.

##### Outcome interpretation: would this have shipped as a timeout?

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

**B — the model's own decision set.** Honour the model's skips on both
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

##### Row labels

Rows are `M1`--`Mn` for Multi-frame and `S1`--`Sn` for Single-frame decisions,
ordered by growth factor descending within each group. The labels are
positional and will move if the data changes, so record the
(workbook, `runId`, `runShotIndex`) triple for each label in the figure's
comment header, together with the implementation commit the workbooks came
from.

#### 5.5 RQ2 workbook mapping

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
| Shadow controller action (not used by the RQ2 audit) | `AdmissionReplay` | `afterEffectiveAdmit` |
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

### 6. RQ3: Coordination-aware pacing-delay appropriateness

#### 6.1 Current research question and evidence

> Does the controller compute an appropriately sized pacing delay for the Draft
> backlog and Capture Timeout budget?

The current main-paper design evaluates the deployed controller rather than
ranking it against pacing methods transplanted from unrelated domains. The
compact evidence chain is: targeted activation, trace-level boundary diagnosis,
an admission-aware envelope partition, observed admission action within the
two-Draft horizon, work conservation, and responsiveness cost. The authoritative
handoff is Part 1 of this document.

For measured backlog $B$, remaining deadline window $T$, realized admitted-Draft
duration $C_{exec}$, and mandatory-only duration $C_{mand}$:

```text
d_exec = ceil(max(0, B + 2*C_exec - max(0,T)) / 2)
d_mand = ceil(max(0, B + 2*C_mand - max(0,T)) / 2)
```

These are retrospective matched-policy targets: they apply the deployed
two-Draft heuristic to realized work. The controller halves positive projected
pressure to limit user-visible delay and relies on admission to shed optional
work under the residual pressure. They are not physical minima or optimal
counterfactual delays.

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

The current artifact is `tables/tab_rq4_pacing_selectivity.tex` alone, with the
generated CSVs documented in `data/rq3/coordination/README.md` and
`data/rq3/estimator/README.md`; RQ3 ships no figure. An earlier generation of
policy, selectivity, and calibration TeX exhibits — not the current selectivity
table — has been deleted. Historical
trajectory and four-policy aggregation material below remains only as
collection context and must not drive the current manuscript.

#### 6.H Historical four-policy RQ3 material (retired)

Everything from this heading through the historical RQ3 workbook mapping is
retained for provenance only. It does not define the current RQ3.
##### 6.H1 Historical summary-table metrics


##### Paced (%)

```text
Paced
    = 100 * count(transitionDelayMs > 0)
            / count(nonblank transitionDelayMs)
```

Zeros remain in the denominator. For complete 30-shot runs, the denominator is
29 transitions per run.

##### \(d_{50}/d_{95}\) (ms)

The inclusive median and 95th percentile of positive
`transitionDelayMs` values. Zero-delay transitions are represented by
`Paced (%)` and are excluded from the conditional delay-magnitude
distribution. Pool the positive transitions from all included runs within one
device-policy pair. If every observed transition delay is zero, report `0/0`;
use `--` only when the required observations are missing.

##### \(\sum d\) (s)

The sum of all 29 `transitionDelayMs` values in a run, converted from
milliseconds to seconds:

```text
total delay (s) = sum(transitionDelayMs) / 1000
```

For a device-policy table row with repeated complete runs, report the median
of the run-level totals. Retain the full run-level distribution for audit.

##### Real backlog

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

##### \(Q_{\max}\)

At a decision timestamp, `realQueueDepth` counts unfinished earlier Drafts
whose `draftStartUptimeMs` is later than the timestamp. It therefore counts
Drafts waiting to start and excludes a Draft that is already running.

\(Q_{\max}\) is the maximum valid `realQueueDepth` observed across all
included runs for that device-policy pair.

`realOutstandingDraftCount` includes the running Draft as well, but it is an
audit column rather than the paper's \(Q\) metric.

##### \(\bar{B}\), \(B_{50}\), \(B_{95}\), \(\bar{Q}\), and deadline-risk exposure

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

##### Slack P5 and S2S P95

```text
Slack P5 = PERCENTILE.INC(timeoutMarginMs, 0.05)
S2S P95  = PERCENTILE.INC(shotToShotTimeMs, 0.95)   # shots 2..30
```

Also record the 30-shot span, `sum(shotToShotTimeMs)` over shots 2..30 per run,
as a run-level median. Comparing the span difference against the median `sum d`
separates delay from any other source of slowdown: if the two agree, the whole
measured responsiveness cost is the pacing delay itself.

##### 6.H2 Historical audit-only diagnostics

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

##### 6.H3 Historical figure metrics

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

##### 6.H4 Historical run-level cost--tail trade-off panel

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

##### 6.H5 Historical RQ3 workbook mapping

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

### 7. Historical four-policy pre-collection checks (retired)

These checks are retained for the retired comparison design. Current RQ3-summary validity and regeneration rules are in Part 1 of this document.

These checks determine whether an exported workbook can factually populate the
RQ3 table and figure.

#### 7.1 Persist the delay that was actually scheduled

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

#### 7.2 Preserve an observation timestamp for No pacing

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

#### 7.3 Require complete Draft timelines

For a non-initial row to contribute factual backlog and queue depth, every
earlier Draft relevant to that snapshot must contain both:

- `draftStartUptimeMs`;
- `draftEndUptimeMs`.

If an earlier Draft timeline is incomplete, the exporter intentionally leaves
the real-backlog and real-queue fields blank instead of treating them as zero.

#### 7.4 Keep admission fixed (historical comparison only)

The four pacing policies must receive the same admitted workload sequence.
Otherwise, a policy may appear to control backlog simply because Admission
removed more work, and RQ3 would no longer isolate pacing ability.

### 8. Output files to populate

#### Paper tables

- `tables/tab_rq2_ablation.tex`
- `tables/tab_rq1_end_to_end_summary.tex`
- `tables/tab_rq3_admission_summary.tex`
- `tables/tab_rq4_pacing_selectivity.tex`

#### RQ2 figure

- `figures/fig_rq3_unsafe_spike_anatomy.tex` — self-contained; the per-decision
  values and the decomposition inputs are recorded in its comment header, so no
  companion CSV is emitted. Regenerate it from section 5.4 whenever the RQ2
  workbook set changes.

`tables/tab_rq3_admission_summary.tex`, come from `data/rq2_spike_anatomy.mjs`
in the ML implementation repository, which is the single place the
\(C_{\mathrm{model}}\) rule of section 5.3 is implemented:

```text
node data/rq2_spike_anatomy.mjs
```

#### Current RQ3 generated evidence

RQ3 no longer ships a figure, and the preview PNGs this section used to list are
no longer produced; review from a `pdflatex` render.

- `data/rq3/coordination/summary.csv`
- `data/rq3/coordination/envelope_share.csv`
- `data/rq3/coordination/action_summary.csv`
- `data/rq3/coordination/flexible_cases.csv`
- `data/rq3/coordination/mandatory_floor_cases.csv`
- `data/rq3/coordination/avoided_delay_12mp_normal.csv`
- `data/rq3/coordination/avoided_delay_24mp_memory.csv`

Regenerate the current RQ3 evidence from the repository root:

```text
python3 scripts/rq3_pacing_summary_metrics.py sampling  # requires openpyxl
python3 scripts/rq3_coordination_metrics.py
python3 scripts/rq3_coordination_audit.py
python3 scripts/rq3_estimator_metrics.py
```

Do not edit generated CSV cells by hand. See
`data/rq3/coordination/README.md` for their schemas and interpretation.
The complete cross-session transfer checklist is Part 4 of this document.

### 9. Current manuscript issues to resolve before final submission

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

### 10. Data handoff checklist

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

## Part 3 — RQ restructure of 2026-08-11 — what changed and how to put it back

Advisor meeting of 2026-08-11. Five columns left RQ1, two left the admission
table, the ablation became its own research question, and everything downstream
renumbered. **Nothing recorded here was deleted because it was wrong.** Every
removed value is printed below in the form it was published in, so any of it can
be restored without re-deriving it from the workbooks.

Read this before reinstating any column. Each section states the values, the
LaTeX that carried them, and what else has to move with them.

---

### 1. Numbering map

The manuscript now has four research questions. The evidence layer does not
follow the renumbering — see §5.

| New | Question | Was | Exhibit |
|---|---|---|---|
| RQ1 | End-to-end effectiveness | RQ1(a) | `tables/tab_rq1_end_to_end_summary.tex` |
| RQ2 | Control-loop contribution | RQ1(b) | `tables/tab_rq2_ablation.tex` |
| RQ3 | Admission decision quality | RQ2 | `tables/tab_rq3_admission_summary.tex` |
| RQ4 | Pacing-delay sizing | RQ3 | `tables/tab_rq4_pacing_summary.tex` |

#### File renames (`git mv`, history preserved)

| Old | New |
|---|---|
| `tables/tab_rq1_ablation.tex` | `tables/tab_rq2_ablation.tex` |
| `tables/tab_rq2_admission_summary.tex` | `tables/tab_rq3_admission_summary.tex` |
| `tables/tab_rq3_pacing_summary.tex` | `tables/tab_rq4_pacing_summary.tex` |
| `figures/fig_rq2_unsafe_spike_anatomy.tex` | `figures/fig_rq3_unsafe_spike_anatomy.tex` |

#### Label renames

| Old | New |
|---|---|
| `tab:rq1_ablation` | `tab:rq2_ablation` |
| `tab:rq2_admission_audit` | `tab:rq3_admission_audit` |
| `tab:rq3_pacing_summary` | `tab:rq4_pacing_summary` |
| `fig:rq2_unsafe_spike_anatomy` | `fig:rq3_unsafe_spike_anatomy` |

`tab:rq1_controller_behavior` and its alias `tab:rq1_preventive_alignment` are
unchanged: that table stayed RQ1.

`_4_experiments.tex` gained a fourth item in the RQ list, *Control-loop
contribution*, and a `\subsection{RQ2: Control-Loop Contribution}` that now owns
the ablation table. RQ1 ships one table where it used to ship two.

---

### 2. RQ1 — five columns removed, three changed unit

`tables/tab_rq1_end_to_end_summary.tex`. The table went from 20 columns to 14.

#### 2.1 Removed: Timeout onset **M** (Kaplan–Meier median first-timeout capture)

The onset column no longer splits Earliest / Kaplan–Meier median. **The value
still printed is E, the earliest first-timeout capture.** Only the median
sub-column is gone. Neither number was recomputed; the revision only chose which
of the published pair stays.

Removed — the KM median:

| Condition | Lv0 | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 | Lv6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12MP normal | -- | -- | 27 | 18 | 12 | 10 | 9 |
| 24MP mem. pressure | 30 | 22 | 21 | 11 | 9 | 8 | 7 |

Still printed — the earliest index:

| Condition | Lv0 | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 | Lv6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12MP normal | -- | -- | 24 | 13 | 8 | 8 | 7 |
| 24MP mem. pressure | 26 | 19 | 14 | 5 | 3 | 4 | 3 |

Both rows are also in `tables/tab_timeout_index.tex` (Table I), `M+S` columns,
*normal capture / 12MP* and *memory-pressure capture / 24MP* — earliest/median in
that order — so that table is a second copy of the whole record.

**One caveat the prose must respect.** The earliest index is exact under
censoring, which is why it needs no estimator caveat where the median carries
one. But it is a **minimum over ten trials**, so it must never be described as
where an uncontrolled burst typically fails. If the prose needs a typical onset,
restore the median column beside it rather than reinterpreting the minimum.

**The requested arithmetic mean was not computed, and this is deliberate.** Two
reasons, both of which still apply if the question comes back:

1. The per-trial first-timeout indices belong to the Section 2 motivation
   campaign (guard bypassed, ten 30-capture trials per level). That raw export
   is in neither this repository nor the `ML` clone; the only surviving
   statistics are the earliest and the KM median. `data/ablation_sampling/…_baseline_0803.xlsx`
   carries per-run `firstTimeoutShot`, but only for Lv3 and Lv4 at 12MP, so it
   cannot fill 14 rows.
2. Several cells are right-censored — no timeout within 30 captures — which
   leaves an arithmetic mean undefined unless a censoring convention is fixed
   first. The KM median already handles censoring correctly, which is why it is
   the value that stayed.

To supply a mean later: recover the per-trial indices for both conditions across
Lv0–Lv6, decide how a censored trial contributes, and add the column beside the
earliest index rather than replacing it — a mean and a minimum answer different
questions, and the minimum is the one the case-study band depends on (§2.6).

#### 2.2 Removed: Slack P5 (%)

Inclusive fifth percentile of `timeoutMarginMs` normalized by the Capture
Timeout deadline, pooled over per-capture margins across all ten runs.

| Condition | Lv0 | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 | Lv6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12MP normal | 37.7 | 19.3 | 4.3 | 4.0 | 5.0 | 3.4 | 5.3 |
| 24MP mem. pressure | 14.3 | 7.7 | 5.9 | 4.3 | 4.7 | 5.6 | 7.8 |

**Consequence to know about:** RQ4 (`tables/tab_rq4_pacing_summary.tex`) is now
the only place the paper reports deadline slack. Its column is still called
"Slack" and is still normalized the same way, precisely so this column can come
back without a rename. Per-run values are in the `slackP5Percent` field of the
`RQ1Runs` sheet of each Full workbook.

#### 2.3 Removed: the M+S pair (@5 / @30, %)

Per-run rate of captures where Bokeh **and** Filter both executed.

| Condition | | Lv0 | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 | Lv6 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 12MP normal | @5 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| | @30 | 100 | 96.0 | 89.3 | 44.3 | 34.3 | 27.3 | 27.7 |
| 24MP mem. pressure | @5 | 100 | 100 | 100 | 94.0 | 94.0 | 96.0 | 80.0 |
| | @30 | 99.3 | 97.0 | 71.0 | 46.7 | 41.7 | 38.0 | 17.7 |

M+S is not recoverable from the surviving M and S columns — it is a conjunction
per capture, not a product of two rates. To restore it, take
`multiAndSingleCompletedAt5Percent` / `multiAndSingleCompletedAt30Percent` from
the `RQ1Runs` sheet, or recompute `bokehExecuted && filterExecuted`.

Note the one row where the distinction bites: 24MP Lv6 @30 is 17.7 for M+S
against 23.7 for M alone.

#### 2.4 Removed: the cumulative-delay pair Σ*d* P50 (@5 / @30, s)

Median across runs of the transition delay already accumulated before shot 5 and
before shot 30.

| Condition | | Lv0 | Lv1 | Lv2 | Lv3 | Lv4 | Lv5 | Lv6 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 12MP normal | @5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | @30 | 0 | 0 | 1.1 | 3.1 | 3.5 | 3.9 | 4.3 |
| 24MP mem. pressure | @5 | 0 | 0 | 0 | 0 | 0 | 0.8 | 0.5 |
| | @30 | 0 | 0.2 | 1.1 | 4.2 | 1.4 | 5.2 | 5.1 |

Recompute from `cumulativeTransitionDelayMs` in the `RQ3Pacing` sheet, or sum
`transitionDelayMs` within a run over the prefix. The case-study table still
reports a cumulative applied delay for one run (5.21 s against a 3.52 s peer
median), so the quantity has not left the paper entirely.

#### 2.5 Changed unit: M, S and Activated now print counts

Percentages became per-run means of a count. **No underlying number moved** —
`scripts/rq1_summary_counts.py` prints both forms from one pass and reproduces
every cell of the pre-revision table. Run it to regenerate either form:

```bash
python scripts/rq1_summary_counts.py
```

* **M, S** — mean captures per run on which the node executed, out of 5 and 30.
  Multiply by 10 for the pooled total out of 50 and 300.
* **Activated** — mean paced transitions per run, out of **4 and 29**, not 5 and
  30: a *k*-capture prefix holds at most *k*−1 transitions. This is the one
  column where the count and the capture horizon have different denominators.
* ***d* P50** — unchanged, still milliseconds.

| Cond. | Lv | M@5 | M@30 | S@5 | S@30 | A@5 | A@30 |
|---|---|---|---|---|---|---|---|
| 12MP | 0 | 5.0 (100%) | 30.0 (100%) | 5.0 (100%) | 30.0 (100%) | 0.0 (0.0%) | 1.1 (3.8%) |
| 12MP | 1 | 5.0 (100%) | 28.8 (96.0%) | 5.0 (100%) | 30.0 (100%) | 0.0 (0.0%) | 0.1 (0.3%) |
| 12MP | 2 | 5.0 (100%) | 26.8 (89.3%) | 5.0 (100%) | 30.0 (100%) | 0.0 (0.0%) | 4.0 (13.8%) |
| 12MP | 3 | 5.0 (100%) | 13.4 (44.7%) | 5.0 (100%) | 26.3 (87.7%) | 0.0 (0.0%) | 8.1 (27.9%) |
| 12MP | 4 | 5.0 (100%) | 10.3 (34.3%) | 5.0 (100%) | 29.2 (97.3%) | 0.1 (2.5%) | 9.8 (33.8%) |
| 12MP | 5 | 5.0 (100%) | 8.2 (27.3%) | 5.0 (100%) | 21.8 (72.7%) | 0.0 (0.0%) | 8.5 (29.3%) |
| 12MP | 6 | 5.0 (100%) | 8.3 (27.7%) | 5.0 (100%) | 26.3 (87.7%) | 0.5 (12.5%) | 9.5 (32.8%) |
| 24MP | 0 | 5.0 (100%) | 29.8 (99.3%) | 5.0 (100%) | 30.0 (100%) | 0.0 (0.0%) | 2.6 (9.0%) |
| 24MP | 1 | 5.0 (100%) | 29.1 (97.0%) | 5.0 (100%) | 30.0 (100%) | 0.0 (0.0%) | 2.0 (6.9%) |
| 24MP | 2 | 5.0 (100%) | 21.3 (71.0%) | 5.0 (100%) | 23.7 (79.0%) | 0.1 (2.5%) | 3.7 (12.8%) |
| 24MP | 3 | 4.7 (94.0%) | 14.0 (46.7%) | 5.0 (100%) | 24.3 (81.0%) | 0.4 (10.0%) | 10.7 (36.9%) |
| 24MP | 4 | 4.7 (94.0%) | 12.5 (41.7%) | 5.0 (100%) | 24.1 (80.3%) | 0.4 (10.0%) | 3.9 (13.4%) |
| 24MP | 5 | 4.8 (96.0%) | 11.4 (38.0%) | 4.9 (98.0%) | 24.1 (80.3%) | 1.7 (42.5%) | 13.4 (46.2%) |
| 24MP | 6 | 4.0 (80.0%) | 7.1 (23.7%) | 4.7 (94.0%) | 20.6 (68.7%) | 1.2 (30.0%) | 12.6 (43.4%) |

**RQ2 was deliberately NOT converted.** Its rates are over the 300 captures each
cell *requested*, and most arms never reach them, so a count column would print
"8.7" beside Full's "30.0" and hide that both are shares of the same requested
burst. The two tables' cross-check is now "RQ2 rate × 30 = RQ1 count": 12MP Lv4
Full 34.3/97.3 against 10.3/29.2, and 24MP Lv4 Full 41.7/80.3 against 12.5/24.1.

#### 2.6 Two places outside RQ1 that depended on the removed columns

* `figures/fig_casestudy_12mp.tex` shades captures 8–12 as the baseline
  first-timeout window. The 8 is RQ1's printed onset; **the 12 was the removed
  KM median** and now has to come from §2.1 of this document.
* `tables/tab_casestudy_selection.tex` compares its peer medians against RQ1's
  12MP/Lv4 macro-averages. Those are now 9.8 transitions, 10.3 M captures and
  29.2 S captures, not 33.8% / 34.3% / 97.3%.

---

### 3. RQ3 — two columns removed and the two blocks merged

`tables/tab_rq3_admission_summary.tex`.

#### 3.1 Removed: Feasible-work **Margin** and Unsafe-work **Overrun**

P50 realized magnitudes over model skips of the relevant factual class,
normalized by the Capture Timeout deadline, in separate always-admit runs.

| | Margin | Overrun |
|---|---:|---:|
| 12MP normal, Multi-frame | +1.2% | −3.0% |
| 12MP normal, Single-frame | +0.7% | −3.5% |
| 24MP mem. pressure, Multi-frame | +2.6% | −3.2% |
| 24MP mem. pressure, Single-frame | +1.6% | −3.4% |

Both are regenerated by `scripts/rq2_audit_pool.py`, which still computes and
prints them; only the table stopped showing them.

**The sign convention went with them and must come back if they do.** Verbatim
from the deleted note:

> Margin and Overrun are P50 realized magnitudes normalized by the Capture
> Timeout deadline in separate always-admit runs. Both are signed onto one axis,
> budget minus realized cost: Margin is positive, the room a skipped feasible
> decision still had, and Overrun negative, the amount by which a skipped unsafe
> decision would have passed the deadline. The stored quantities are unsigned
> magnitudes; the sign is printed so the two columns are read on the same axis
> rather than as two unrelated positive numbers.

Column widths, if restored into the merged nine-column layout: Margin needs
24pt, not 23 — `$+1.2\%$` measures 23.06pt at `\scriptsize` and silently wrapped
at 23. Overrun needs 26pt.

#### 3.2 The two blocks became one table, still inside `\columnwidth`

Block (a) *Controller-enforced runs* and block (b) *Always-admit audit* are now
the left four and right four columns of one nine-column table. The pre-merge
two-block layout is in git history at the last revision of
`tables/tab_rq2_admission_summary.tex`.

Nine columns in 252pt only worked after two format changes; both are load-bearing
and undoing either forces `table*` again. Measured at `\scriptsize`:

| Cell format | Content width | Verdict |
|---|---:|---|
| `1,966 (93.6%)` on every row (first merged draft) | 312pt | 60pt over, at zero column spacing |
| counts on data rows, shares on **Overall**, no `[watchdog]` | 224pt | fits, `\tabcolsep` ≈ 1.5pt |
| shares on every row, counts nowhere | 231pt | fits, `\tabcolsep` ≈ 1.1pt |

#### 3.3 Removed: the per-row percentages

Data rows print counts; only **Overall** prints a share. The per-condition admit
rate is therefore no longer in the table:

| | Model admit | Model skip | Feas. adm. | Feas. skip | Uns. adm. | Uns. skip |
|---|---:|---:|---:|---:|---:|---:|
| 12MP Multi-frame | 93.6% | 6.4% | 98.1% | 1.9% | 5.7% | 94.3% |
| 12MP Single-frame | 99.6% | 0.4% | 99.4% | 0.6% | 0.0% | 100.0% |
| 24MP Multi-frame | 87.5% | 12.5% | 94.7% | 5.3% | 1.9% | 98.1% |
| 24MP Single-frame | 98.0% | 2.0% | 97.1% | 2.9% | 3.7% | 96.3% |

Each is the count over its own row denominator, so all of them are recoverable by
division; the denominators are in the table note (2,100 / 2,100 / 2,116 / 2,114
on the left, Admitted + Skipped per factual class on the right).

**The cost to weigh if this comes up again:** 93.6% against 87.5% — how much
harder admission works under memory pressure — is a comparison a reader now has
to compute. If the RQ3 prose leans on it, quote it from this table rather than
from the exhibit, or switch to the shares-everywhere variant above, which fits
`\columnwidth` too and costs the deployed volumes instead.

#### 3.4 Removed: the `[watchdog]` cause annotation and the population subtitles

The Unsafe cells read `1 [watchdog]` and `2 [watchdog]`; they now print the bare
count and the cause is in the note. That column held one digit inside 36.5pt —
the worst width-to-content ratio in the table — and dropping the annotation was
worth 16pt of the 60 that had to be found. Restoring it needs the `\rqtwoun`
spacer macro back as well, or the `]` of `1 [watchdog]` and a bare `0` land on
the same right edge with their digits 34pt apart.

The two top-level headers also carried a population subtitle, removed on advisor
instruction:

```
balanced full-controller arm, 8,430 decisions
disjoint pacing-only pool, 3,746 decisions
```

Both populations moved into the table note, which is why that note is not
optional — it is now the only thing in the exhibit preventing a left cell from
being read against a right cell.

**Why the split existed, since the merge removes that protection.** The two
halves are different, disjoint populations: 8,430 deployed decisions on the left,
3,746 audited decisions on the right, with their own denominators and their own
selection caveat. Stacked, no row could be read as one decision set measured two
ways. Merged, three things carry that burden instead — each top-level header
names its own population on a second line, the percentages close only within a
half, and the RQ3 prose must still state both denominators. If a reader ever
crosses the boundary, restore the two-block form rather than patching the note.

#### 3.5 One row is new

**Overall** previously existed only in block (a). Its audit-half cells —
3,470 (97.3%) / 98 (2.7%) feasible and 5 (2.8%) / 173 (97.2%) unsafe — are the
sum of the four printed audit rows (3,568 feasible and 178 unsafe decisions), not
a separate regeneration. Pooling within a half is what block (a)'s Overall row
already did.

---

### 4. Open item, inherited not introduced

`scripts/rq2_audit_pool.py` disagrees with the printed Unsafe-work columns on two
of four rows. Its regeneration *and* its own hardcoded `PUBLISHED` constants both
give 12MP Multi-frame **4 (11.4%) / 31 (88.6%)** and 24MP Single-frame
**3 (5.6%) / 51 (94.4%)**, where the table prints 2 (5.7%) / 33 (94.3%) and
2 (3.7%) / 52 (96.3%). Feasible-work agrees on all four rows.

The table's values were left untouched by the merge because
`figures/fig_rq3_unsafe_spike_anatomy.tex` follows the table — it takes apart five
unsafe admits, not the script's eight. Resolving this needs to know which
regeneration produced the published cells. Resolve before submission; if the
script wins, the figure moves with the table.

Separately, `figures/fig_casestudy_12mp.tex` claims Table I reads "10/17" for
normal capture / 12MP / M+S / Lv4. `tables/tab_timeout_index.tex` prints 8/12
there. Pre-existing and not touched by this revision.

---

### 5. What did NOT renumber, and why

`docs/`, `data/` and `scripts/` keep the old RQ numbering:

* Part 2 of this document still documents RQ1(a), RQ1(b), RQ2, RQ3 —
  read them as RQ1, RQ2, RQ3, RQ4.
* Part 1 of this document, Part 4 of this document, `data/rq3/**` and
  `scripts/rq3_*.py` describe what the manuscript now calls **RQ4**.
* `scripts/rq2_admission_metrics.py`, `scripts/rq2_audit_pool.py` and
  `scripts/rq2_unsafe_admit_safeguards.py` produce what the manuscript now calls
  **RQ3**.
* `scripts/rq1_ablation_metrics.py` produces what is now **RQ2**.

These are internal compatibility names, the same treatment `AGENTS.md` already
gives the CSV fields containing `required`. Renaming them would break the RQ3
evidence handoff that `AGENTS.md` declares authoritative, and would rename
generated-artifact directories that the scripts write by path. File paths *inside*
those documents were updated, so every reference still resolves.

## Part 4 — RQ3 File Manifest

This manifest lists the files required to carry the current RQ3 summary to
another session or paper branch. Paths are repository-relative.

### Copy these current source and context files

#### Shared context and interpretation

- `AGENTS.md`
- `docs/rq-evidence.md` (this file; the manifest originally listed the
  measurement guide, the pacing handoff and itself as three separate files)
- `data/rq3/coordination/README.md`
- `data/rq3/estimator/README.md`

#### Paper integration and current exhibits

- `2_4_static_safeguards.tex`
- `tables/tab_rq4_pacing_selectivity.tex`

RQ3 ships one single-column table and no figure. Its definitions, provenance,
and claim limits used to live in the table's own header comment and are now in
`docs/exhibits.md`, so copy that file too; copy the `.tex` whole rather than
extracting the environment, and review it from a `pdflatex` render.

#### Generators used by the summary analysis

- `scripts/rq3_pacing_summary_metrics.py`
- `scripts/rq3_calibration_metrics.py`
- `scripts/rq3_selectivity_metrics.py`
- `scripts/rq3_coordination_metrics.py`
- `scripts/rq3_coordination_audit.py`
- `scripts/rq3_estimator_metrics.py`

`rq3_pacing_summary_metrics.py` imports the calibration loader and selectivity
bootstrap/binning helpers, so copy all three even if only the policy generator
is being changed. That path requires `openpyxl`. `rq3_estimator_metrics.py`
imports the loader and eligibility rules of `rq3_coordination_metrics.py`, and
`rq3_coordination_audit.py` imports the same module; those three use only the
Python standard library.

### Copy or regenerate these generated inputs

#### Targeting and boundary-mechanism data

Directory: `data/rq3/policy/`

- `backlog_error_quantiles.csv`
- `band_activation_12mp_normal.csv`
- `band_activation_24mp_memory.csv`
- `boundary_case_details.csv`
- `boundary_mechanism.csv`
- `boundary_overrun_unpaced.csv`
- `boundary_safe_paced.csv`
- `burst_share_swarm_12mp_normal.csv`
- `burst_share_swarm_24mp_memory.csv`
- `delay_vs_backlog_12mp_normal.csv`
- `delay_vs_backlog_24mp_memory.csv`
- `pressure_cloud.csv`
- `summary.csv`

#### Admission--pacing coordination data

Directory: `data/rq3/coordination/`

- `summary.csv`
- `envelope_share.csv`
- `action_summary.csv`
- `flexible_cases.csv`
- `mandatory_floor_cases.csv`
- `floor_miss_encoding.csv`
- `floor_miss_filter.csv`
- `envelope_ladder_12mp_normal.csv`
- `envelope_ladder_24mp_memory.csv`
- `avoided_delay_12mp_normal.csv`
- `avoided_delay_24mp_memory.csv`

#### Outcome matrix and estimator data

Directory: `data/rq3/estimator/`

Everything the current table prints, apart from the cost figures in its note.

- `summary.csv`
- `outcome_matrix.csv`
- `sizing_summary.csv`
- `floor_zero_delay_account.csv`
- `queued_pricing_scatter.csv`
- `scatter_{12mp_normal,24mp_memory}_{no_delay_required,covered,flexible,below_floor}.csv`
- `draft_pricing_ecdf_{12mp_normal,24mp_memory}.csv`
- `reserve_error_ecdf_{12mp_normal,24mp_memory}.csv`

`floor_zero_delay_account.csv` is the row-by-row account of the 11 below-floor
decisions that received no delay; `data/rq3/estimator/README.md` defines every
column and records which of them is load-bearing.

The scatter and ECDF files backed the deleted figure. They are still generated
and are still the fastest way to check the population P05/P50/P95 line in the
table note, but nothing in the manuscript reads them.
`scatter_12mp_normal_below_floor.csv` is deliberately a header with no rows,
because no 12MP decision fell below the floor.

Generated CSV cells must not be edited manually. Regenerate them from the
scripts above when the source workbooks or eligibility rules change.

### Source workbooks required for regeneration

- `data/ablation_sampling/48U_metrics_12MP_normal_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_12MP_normal_0803_2.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_2.xlsx`

These are inputs, not files created by the RQ3 summary analysis.

The superseded policy, selectivity, and calibration TeX exhibits and their
obsolete preview script have been deleted. The calibration and selectivity
Python modules remain because `rq3_pacing_summary_metrics.py` imports their shared
loader, binning, bootstrap, and burst helpers.

### Regeneration order

```text
python3 scripts/rq3_pacing_summary_metrics.py sampling  # requires openpyxl
python3 scripts/rq3_coordination_metrics.py
python3 scripts/rq3_coordination_audit.py
python3 scripts/rq3_estimator_metrics.py
make                                            # requires pdflatex
```

### Current environment verification status

- Targeting and cost regeneration: reproduced (`openpyxl` 3.1.5 present).
- Coordination aggregation: reproduced, byte-identical to the committed CSVs.
- Admission-action and floor audit: reproduced; the margin identity closes to
  1.0 ms.
- Outcome matrix and estimator data: reproduced; the delay identity closes to
  0.50 ms at 12MP and 0.76 ms at 24MP.
- LaTeX build: reproduced with TeX Live 2026 `pdflatex`; references resolve and
  there are no content-box or package warnings. The current prose-light,
  float-heavy skeleton emits one 6.7 pt page-output `Overfull \\vbox`, which
  must be rechecked after the missing section prose is drafted.
