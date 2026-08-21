# Exhibit notes

Provenance, layout constraints, and revision history for the manuscript's
tables and figures.

Every file under `tables/` and `figures/` used to carry this material as a
comment header, which grew to roughly two thirds of some of those files. The
`.tex` files now carry a single pointer line back to this document and no other
commentary. Read the relevant section here before editing an exhibit: several
entries record numbers that were published, columns that were deliberately
removed, and geometry that must be re-derived if a header changes.

A section is named after its file stem, so `tables/tab_rq2_ablation.tex` is
documented under [`tab_rq2_ablation`](#tab_rq2_ablation).

The numbers, data paths, script names, and implementation commit hashes below
are reproduced from those comment headers unchanged. Where an entry conflicts
with `AGENTS.md`, `AGENTS.md` wins and this file should be corrected.

## Index

| Exhibit | Directory | Status |
| --- | --- | --- |
| [`tab_casestudy_selection`](#tab_casestudy_selection) | `tables/` | Live -- `_4_experiments.tex`, case study |
| [`tab_controller_state`](#tab_controller_state) | `tables/` | Not input by any section |
| [`tab_rq1_end_to_end_summary`](#tab_rq1_end_to_end_summary) | `tables/` | Live -- `_4_experiments.tex`, RQ1 |
| [`tab_rq2_ablation`](#tab_rq2_ablation) | `tables/` | Live -- `_4_experiments.tex`, RQ2 |
| [`tab_rq3_admission_summary`](#tab_rq3_admission_summary) | `tables/` | Live -- `_4_experiments.tex`, RQ3 |
| [`tab_rq4_pacing_sizing`](#tab_rq4_pacing_sizing) | `tables/` | Live -- `_4_experiments.tex`, RQ4 |
| [`tab_rq4_pacing_selectivity`](#tab_rq4_pacing_selectivity) | `tables/` | Superseded 2026-08-21 by `tab_rq4_pacing_sizing`; kept on disk |
| [`tab_rq4_pacing_summary`](#tab_rq4_pacing_summary) | `tables/` | Superseded 2026-08-13 by `tab_rq4_pacing_selectivity`; kept on disk |
| [`tab_setup`](#tab_setup) | `tables/` | Live -- `4_1_setup.tex`, evaluation setup |
| [`tab_timeout_index`](#tab_timeout_index) | `tables/` | Live -- `2_4_static_safeguards.tex` |
| [`fig_capture_pipeline`](#fig_capture_pipeline) | `figures/` | Live -- `2_3_draft_sequence.tex` |
| [`fig_casestudy_12mp`](#fig_casestudy_12mp) | `figures/` | Live -- `_4_experiments.tex`, case study |
| [`fig_parallel_capture_overlap`](#fig_parallel_capture_overlap) | `figures/` | Live -- `2_2_parallel_capture.tex` |
| [`fig_rq3_unsafe_spike_anatomy`](#fig_rq3_unsafe_spike_anatomy) | `figures/` | Live -- `_4_experiments.tex`, RQ3 |

## tab_casestudy_selection

`tables/tab_casestudy_selection.tex` &middot; Live -- `_4_experiments.tex`, case study

Case study: deployment rationale and a compact peer audit for the 12MP trace
without external memory pressure.

Implementation source: private ML repository commit
99aae0af8c3fa1ceb784083446e83c40d0fb917f (2026-08-04).
Workbooks, now held in this repository:
  data/ablation_sampling/48U_metrics_12MP_normal_0803_1.xlsx
  data/ablation_sampling/48U_metrics_12MP_normal_0803_2.xlsx
Deployment fact supplied by the author: 12MP is the default resolution.

Peer source, and why this folder.  Block (b) was previously computed from the
single 0803_FULL workbook in the ML clone.  It now comes from the balanced
copy in data/ablation_sampling/, which is what the RQ1 tables report from, and
the two-part split means runs are keyed <part>:<runId>.  The peer set that
falls out -- Lv4, MP12, complete and timeout-free -- is exactly the ten runs
of the RQ1 12MP/Lv4 cell: their macro-averages are 33.8% activated, 34.3%
M and 97.3% S.  Those were that row's printed values until 2026-08-11; RQ1
now prints the same three quantities as per-run counts -- 9.8 paced
transitions of 29, 10.3 M captures and 29.2 S captures of 30 -- so compare
against those and not against the percentages.  Quoting a peer median
here against a macro-average there is therefore a difference of statistic, not
of data, and the S row is the one where the two look furthest apart: nine of
the ten peers execute S on every capture, so the median is 100.0 while the
mean is 97.3.

Carried over from the trim, and to be stated if block (b) is challenged: the
balancing dropped the four 12MP/Lv4 runs that retained all optional Draft work
(see the folder README).  Against the untrimmed data/ablation_original/, where
the same filter admits 14 peers, the medians read M 38.3, S 100.0, activated
32.8, delay 4,460.5 ms and margin P5 451.7 ms.  The trim therefore moves the
M peer median from 38.3 to 28.3 and leaves this run only 1.6 points below it,
so the anti-selection claim now rests on a thin margin in that row while the
other four keep a wide one.

Scope note.  This table justifies the case-study *setting*, not the pick of
one run out of the 44 recorded.  An earlier revision carried the generator's
mechanism-coverage funnel (44 -> 43 -> 28 -> 4 -> 1) instead.  That was
removed deliberately and should not be reinstated: the funnel's own numbers
say the full coordination sequence appears in one of 43 valid sessions, which
reads as atypicality and costs more than the transparency it buys.  The
representativeness argument below is the one this paper needs -- 12MP without
memory pressure is the ordinary configuration, and Lv4 is where the product
actually failed.  The peer note keeps the anti-selection evidence that does
not carry the atypicality problem.

Peer figures: data/case_study/12mp_normal_peer_comparison.csv, produced by
scripts/export_casestudy.py.  Peers hold the condition, the starting overheat
level, and the size bucket of the selected session fixed and keep only
complete timeout-free sessions (n = 10).  Selected / peer median / peer
[min, max], with the preferred direction in brackets, in table row order --
work delivered first, then what it cost, then the margin that survived:
  M executed              26.7 / 28.3   / [23.3, 66.7] %       [higher]
  S executed              73.3 / 100.0  / [73.3, 100.0] %      [higher]
  pacing activated        55.2 / 29.3   / [20.7, 62.1] %       [lower]
  cumulative delay        5212 / 3519.0 / [2930, 6587] ms      [lower]
  deadline margin P5     366.1 / 411.2  / [209.2, 738.1] ms    [higher]
The two cost rows read frequency then magnitude: how often pacing intervened,
then what those interventions summed to.
"Pacing activated" is the RQ1 name for this quantity and replaces the
earlier "paced transitions": both are RQ3Summary.pacedPercent, the share of a
run's 29 transitions carrying a positive applied delay.  RQ1 prints 9.8
transitions for 12MP Lv4 -- the same macro-average as the 33.8% it printed
before 2026-08-11, over the same ten runs whose median is the 29.3 peer
figure here.

Burst span (burstSpanMs, the 30-shot span: sum(shotToShotTimeMs) over shots
2..30) is a sixth peer metric in the CSV and is deliberately NOT a row here.
It is 21717 / 20336 / [16585, 21717] ms: unfavourable, and on this peer set
the run is the slowest of the ten, so as a row its verdict would read worst
rather than worse.  It stays out for the same reason as before -- it is not
independent of cumulative delay -- and the arithmetic now makes that point
more sharply than it did on the untrimmed peer set.  The run exceeds the peer
median by 1,381 ms of burst span while carrying 1,693 ms more applied delay,
so the pacing more than accounts for the slowdown and the run was in fact
slightly quicker than the median peer outside its paced transitions.  Listing
both would pad "unfavourable on every metric" with two near-duplicate rows.
Do not reinstate it as a row; if the end-to-end responsiveness cost is wanted
in prose, the pair is also the metrics-guide (section 6.2) check that pacing
is the only material source of the slowdown.

All five rows are on the unfavourable side of the peer median.  S executed
equals
the peer minimum exactly, so no peer with this setting completes less
optional single-frame work; M executed is above its peer minimum of 23.3% and
is therefore not claimed as a minimum.  The deadline margin is reported as a
percentage of the timeout (366.1 -> 5.2, 411.2 -> 5.9) because the deadline
constant must not appear in the manuscript, and pairing an absolute margin
with a normalized one anywhere in the paper would make it recoverable.

Block (b) was prose in an earlier revision, naming three of the metrics.
It is a table now for one reason: "unfavourable on every metric" is a claim
the reader has to take on trust in a sentence and can check at a glance in a
grid, and naming a subset invites the question of what the unnamed ones say.

The metric names carry the preferred direction and the last column carries the
verdict.  An intermediate revision dropped the arrows on the grounds that they
duplicate the verdict column and make the reader combine an arrow with two
numbers to recover the one word "worse".  They are restored because that
argument had the dependency backwards: without a direction marker the verdict
column can only be trusted, not checked, and a reader who wants to confirm
that 55.2 against a peer median of 29.3 is in fact worse has to find the
answer in the note.  With both present the row is self-verifying, which is
what a reviewer needs from an anti-selection table.
The verdict column stays: a column of five identical entries is the evidence
for the claim in the note, and a future run that beats its peers on some
metric would break it visibly.  The [min, max] column needs no direction,
since its job is to show that the S value coincides with the peer minimum.
Direction is a property of the metric, not of this run, so the arrow sits on
the metric name.  Delay and activation are costs and read better lower;
margin and the two completion rates read better higher.

Layout: booktabs, which the preamble already loads and whose rule spacing it
already tunes.  The previous grid ruled every row and every column, so the
six data rows of block (b) carried more rule than data.  Horizontal rules now
mark structure only -- head, body, foot -- and the multi-line rows of block
(a) are separated by \addlinespace instead.  No vertical rules; tabcolsep is
raised to 5pt so the columns stay apart without them.

Both tabulars are the same total width.  Without vertical rules the total is
just sum(widths) + 2*n*tabcolsep, so with tabcolsep at 5pt block (a) is
(0.42+0.45)cw + 20pt and block (b) is sum(B) + 50pt; sum(B) = 0.751cw makes
them equal.  Changing a width in either block means recomputing the other,
and changing tabcolsep means recomputing both.

0.40 / 0.47 rather than 0.42 / 0.45: the choice column has slack its
longest entry does not use, the rationale column had a one-word overhang.
The sum is unchanged, so block (b) still matches without recomputation.

## tab_controller_state

`tables/tab_controller_state.tex` &middot; Not input by any section

Online duration quantities consumed by admission and pacing: one row per
quantity, with how it is constructed and updated and where its lifetime ends.

**Abstraction revised 2026-08-19.** Section 3.4 replaced the explicitly named
learned Draft overhead with \(\hat Q(\mathcal K)\), a whole-Draft occupancy
estimate. This keeps the pacing equations faithful to whole-Draft timing without
exposing the estimator's implementation-specific decomposition. The earlier row
was:

```
    \(\hat H\) &
    Recency-weighted mean of whole-Draft time outside modeled workload intervals; updated at Draft completion &
    Pacing; persistent across queue drains \\
```

Do not append this term to the current equations: \(\hat Q\) already includes
the same timing component abstractly, so doing so would double count it. If the
implementation-specific decomposition is ever restored, replace the \(\hat Q\)
definition and both uses consistently rather than adding \(\hat H\) to \(\hat Q\).

## tab_rq1_end_to_end_summary

`tables/tab_rq1_end_to_end_summary.tex` &middot; Live -- `_4_experiments.tex`, RQ1

RQ1: Baseline failure reference, full-controller Draft availability, and
pacing cost.
This is the RQ1 table; the per-loop ablation is now its own research
question, RQ2, in tables/tab_rq2_ablation.tex.

Controller-off Timeout onset retains the previously reported baseline
reference.  Full-controller values are reconstructed from the balanced copy in
data/ablation_sampling/:
  - 48U_metrics_12MP_normal_0803_1.xlsx
  - 48U_metrics_12MP_normal_0803_2.xlsx
  - 48U_metrics_24MP_memory_0803_1.xlsx
  - 48U_metrics_24MP_memory_0803_2.xlsx
The workbooks were exported by CaptureMetricsExcelExporter.  The
implementation reference was inspected at commit:
99aae0af8c3fa1ceb784083446e83c40d0fb917f

Per the collection correction, sessions containing Capture Timeout are
excluded and incomplete non-timeout sessions remain outside the exporter's
RQ1 inclusion set.  On the unbalanced source in data/ablation_original/, the four
workbooks contribute 84 and 72 complete, timeout-free runs to the 12MP and
24MP conditions.

---
2026-08-11 REVISION.  Five columns were removed and three changed unit on
advisor feedback.  docs/rq-evidence.md (Part 3) holds every removed value
and the exact restore procedure; read it before reinstating anything.  In
summary:
  - Timeout onset no longer splits Earliest / KM-median.  The single printed
    value is the EARLIEST first-timeout capture; the Kaplan-Meier median
    sub-column is gone.  Neither number was recomputed -- both are the
    previously published pair, and the revision only chose which one stays.
    An arithmetic mean was requested first and is NOT computable here: the
    per-trial first-timeout indices belong to the Section 2 motivation
    campaign (Table~\ref{tab:timeout_index}), whose raw export is in neither
    this repository nor the ML clone, and cells that never time out within 30
    captures are right-censored, which leaves a mean undefined.  The earliest
    index is exact under censoring, which the mean is not, so it needs no
    estimator caveat -- but it is a MINIMUM over ten trials and must never be
    described as typical.  The caption says "earliest" and must keep saying it.
  - Slack P5, the M+S pair and the Sigma-d pair are removed.
  - M, S and Activated print COUNTS instead of percentages.
---

COUNT CONVENTION.  M and S are the mean number of captures per run on which
the node executed, over the first 5 and the first 30 captures, so the printed
value is read directly against the @5 / @30 header: "13.4 of 30".  Activated
is the mean number of PACED TRANSITIONS per run, and its denominator is not
the capture count -- a k-capture prefix holds at most k-1 transitions, so the
eligible base is 4 at @5 and 29 at @30.  That is why its header names its own
unit; do not read it against 5 / 30.
  Every count is exact, not a rescaling of the previously printed percentage.
Recomputed from RQ3Pacing (bokehExecuted, filterExecuted, transitionDelayMs)
over the runs RQ1Runs marks includedForRq1, which is exactly ten per cell in
the balanced copy.  The recomputation reproduces all 14 rows of the previous
percentage-form table on every M, S, Activated and d cell, so the unit change
moved no underlying number.  Totals behind the per-run means, and the
percentages they replace, are tabulated in the revision document.

Cells that did not change, because they already held ten runs: 12MP Lv0, Lv1
and 24MP Lv0, Lv2, Lv4, Lv5, Lv6.

Aggregation conventions:
  - EVERY column, retention included, uses all ten retained runs.  The
    denominator of an @H cell is therefore H x 10 captures, which is the same
    rule Table~\ref{tab:rq2_ablation} states as "over the 300 captures each
    cell requested".  The two tables now agree by construction rather than by
    coincidence.
  - The denominators coincide because of what this arm contains, and that is
    worth checking again if the run set is ever re-exported: across all 140
    runs here, NO run ends before 30 captures, NO capture is flagged
    isTimeout, and NO capture has a negative timeoutMarginMs.  "Captures
    present in the run", "captures that met the deadline" and "captures
    requested" are all 30 per run.  The distinction that forced the
    300-capture denominator in Table~\ref{tab:rq2_ablation} -- truncated runs
    and deadline-missing captures -- simply does not arise in this table.
  - RETIRED: the rule that dropped a watchdog-bearing run from the retention
    average for the horizon the watchdog falls inside.  It was redundant and
    disproportionate.  Redundant because the watchdog capture already scores
    zero on its own: in both affected runs (24MP Lv2 run 37 and Lv4 run 24,
    watchdog at shot 13 with only 9 ms and 53 ms of margin left) neither Bokeh
    nor Filter executed, so excluding the capture and keeping it give
    identical cell values.  Disproportionate because it discarded 30 captures
    on account of one, and it also hid real behaviour -- optional work stays
    suppressed on shots 14 and 15 immediately after the watchdog.
    The change moves the affected numbers in both directions, because the
    affected run is above the cell mean in one case and below it in the other
    (M of 63.3% at Lv4 against the cell's 39.3%, and 60.2% at Lv2 against
    72.2%).  Recorded in the percentage form the table used before
    2026-08-11, which is the form the surrounding argument was written in:
      24MP Lv2 @30  M+S/M/S  72.2/72.2/81.1 -> 71.0/71.0/79.0
      24MP Lv4 @30  M+S/M/S  39.3/39.3/82.2 -> 41.7/41.7/80.3
    The post-change M and S values are what the printed counts 21.3/23.7 and
    12.5/24.1 now carry.
    No @5 cell moves: both watchdogs fall at shot 13, outside that horizon,
    and the retired rule already left @5 eligible.  No pacing column and no N
    moves either; those already used all ten runs, so retiring the rule is
    what makes the table internally uniform instead of splitting the retention
    block off from every other column.
  - retention is measured by EXECUTION (the node has a positive observed
    duration).  In this arm that agrees with the exporter's Completed flag;
    the two diverge only in the forced-execution arms of
    Table~\ref{tab:rq2_ablation}.

The 24MP/memory-pressure workbook is treated as one requested-mode scenario
rather than regrouped by exported Draft sizeBucket.  This preserves its mixed
MP24-to-MP12 execution and the MP12 fallback traces at Lv5--6.

Retention and activation counts are computed within each run and macro-averaged
across all ten runs; because every run here is a complete 30-capture session,
that macro-average equals the pooled H x 10 count divided by ten exactly.
Delay P50 pools positive transition-delay events.

\fittabcolsep (macros.tex) solves for the \tabcolsep that makes the outer
rules land exactly on \textwidth.  Fourth argument is 2 x the column count,
now 14 columns and so 28; it was 40 when the table held 20.

Column alignment, per the advisor's standing rule: every header cell is
centred both horizontally (\multicolumn{1}{c} plus \makecell[c]) and
vertically (\multirow with the offsets below), and every DATA cell is
right-aligned.  The three leading columns stay centred because they are row
labels, not measurements.

Header geometry is unchanged from the 20-column form -- still four rows,
still the same line counts per row -- so the -1.8ex and -0.4ex \multirow
nudges carry over.  Re-derive them if a header gains or loses a line.
  "Timeout onset" is broken across two lines on purpose.  Set on one line it
measures wider than any other header here, and with a two-character datum
under it the right-aligned value would sit an implausible distance from its
own label.  Two lines put the column near the width of its neighbours.

$d$, not "Applied Delay".  RQ4 prints the applied pacing delay as $d$
throughout Table~\ref{tab:rq4_pacing_summary}, and one quantity carries one
printed name in this paper.  The symbol also matches the two columns to its
left, which are already set as bold math ($M$, $S$), and it is introduced
in the prose of Section~\ref{sec:guard-limit} beside $M$ and $S$.

"Draft stages retained", not "Draft work retained" (2026-08-15).  The four
columns under this group header are the per-run capture counts on which the
stages $M$ and $S$ executed, so it names stages under the sharpened AGENTS.md
rule that reserves "Draft work" for amounts.  Width is not a concern here as
it is in Table~\ref{tab:rq2_ablation}: this is a \textwidth table* with no
explicit p-widths, the header spans four columns, and it grows only 61.8pt to
64.2pt at \scriptsize.  Table~\ref{tab:rq2_ablation}'s counterpart header
moved in the same commit; keep the two phrased alike, since they are the same
quantity under two denominators.

Emphasize the scenario boundary only after the final 12MP row.

## tab_rq2_ablation

`tables/tab_rq2_ablation.tex` &middot; Live -- `_4_experiments.tex`, RQ2

RQ2: Two-factor controller ablation across two stress conditions.
Split out of RQ1 and promoted to its own research question on 2026-08-11:
RQ1 characterizes the full controller across starting levels, and RQ2 isolates
what each control loop contributes.  The file was tables/tab_rq1_ablation.tex
and the label was tab:rq1_ablation before that split.

This table still reports M and S as PERCENTAGES, whereas RQ1 now prints
per-run capture counts.  That is deliberate, not an oversight: RQ1's
denominator is a fixed 30-capture session, so a count reads directly, while
every rate here is over the 300 captures the cell REQUESTED and most arms
never reach them -- 12MP No control reaches a mean of 9.7 captures of 30, so a
count column would print "8.7" beside Full's "30.0" and hide that the two are
shares of the same requested burst.  See THE DENOMINATOR note below.

Reviewer-facing structure:
  - Admission and Pacing remain the two axes of a factorial design; the 2x2 is
    unrolled into four rows per condition so that two conditions fit one
    table.
  - S(30) alone is not reported.  An arm can trivially reach zero timeouts by
    discarding optional Draft work or by pacing arbitrarily slowly, so each
    row also reports how many of the requested captures actually completed,
    how much M and S work those captures delivered, and how often and how
    hard the pacer intervened.  RQ4 separately evaluates whether that delay is
    appropriately sized for the observed backlog.

Condition definition:
  Each condition is one (capture condition, starting overheat level) pair.
  12MP normal and 24MP memory pressure are each reported at starting level 4,
  the regime where the deployed static guard is closest to its decision
  boundary and where the baseline already fails.
  The 24MP workbooks are a requested-mode label: only the first one or two
  captures are 24MP and the remainder are 12MP.

THE DENOMINATOR, and why it changed.  Every rate in this table is taken over
the 30 x 10 = 300 captures the cell requested, NOT over the captures a run
happened to reach.  Two earlier forms were wrong in opposite directions and
both are worth remembering, because each looks reasonable in isolation:
  - Rate over captures present in the run.  This printed M = S = 100.0 for
    both admission-off arms, because with admission off every node runs on
    every capture.  But 12MP No control reaches a mean of 9.7 captures of 30,
    so "100%" was 100% of a third of a session, printed alongside Full's 100%
    of a whole one.  It also counted the capture that timed out as delivered
    work, which is exactly backwards: on that capture Bokeh and Filter did run
    (380-588 ms and 208-319 ms at 12MP/Lv4) but the Draft overran the deadline
    by 153-773 ms, and the exporter's own bokehCompleted/filterCompleted are
    False there.  That capture is the failure, not a delivered result.
  - Rate over the run, multiplied by a survival indicator.  This printed 0 for
    No control, which contradicts Section~\ref{sec:guard-limit}: the
    uncontrolled arm does not fail by doing no optional work, it fails by
    doing all of it.  It also charged the same failure twice, once in Survived
    runs and again inside M and S, so the printed gap mixed a retention
    difference with a survival penalty.
  The 300-capture denominator fixes both: a capture that was never reached
  because the session ended contributes zero, a capture whose Draft missed the
  deadline contributes zero, and every cell is divided by the same number.

ONE INVERSION TO STATE IN THE PROSE, NOT TO HIDE.  At 12MP, Pacing only
delivers more multi-frame Drafts per attempted burst than Full (40.7% against
34.3%), and the same holds for M+S.  This is real and follows from the
mechanism: Full deliberately skips M on about two thirds of its captures,
while Pacing only skips nothing and simply takes fewer captures -- 131 of 300
against Full's 300 of 300.  The Captures column immediately next to it
is what settles the comparison (40.7 against 100.0), so the honest move is to
print the inversion and say what it costs:
  "Pacing only delivers more multi-frame Drafts per attempted burst (40.7%
   against 34.3%), but only 40.7% of requested captures complete at all."
Do not switch denominators to make this row disappear; every total-work
measure produces it, because doing less work per capture IS the mechanism.

Reading the two blocks:
  12MP shows the trade.  Admission converts a 29.0% capture completion rate
  into 100% by giving up optional work, and pacing then buys S back from
  33.7% to 97.3% without giving up the completion rate.
  24MP shows dominance.  Full leads on all three of Captures, M and S
  (100.0/41.7/80.3 against Admission only's 87.3/24.3/51.0).
  The two conditions therefore do different work and both are worth keeping.

Degenerate corners are visible by construction: for the two admission-off
arms, Captures, M and S are the SAME number (29.0/29.0/29.0 and
40.7/40.7/40.7 at 12MP).  Those arms never skip, so every capture that
completes carries both stages, and the only thing that varies is how many
complete.  The repetition is the finding, not a redundancy to remove.

Column definitions (docs/rq-evidence.md (Part 2), sections 3.2--3.5, 4.3):
  Survived   runs reaching 30 captures with no Capture Timeout, over the
  runs      number of included runs after run reconstruction and dedup
  Captures   100 * (captures whose Draft completed within the deadline) / 300.
             The capture that timed out is excluded from the numerator; the
             captures never reached because the session ended contribute zero.
             The printed header is just "Captures (%)": the group header
             "Deadline safety" and the caption's "over the 300 captures each
             cell requested" supply the rest.  NOTE that the on-time
             qualifier now survives ONLY here and in the caption, so do not
             paraphrase this column as "captures taken" -- 12MP No control
             reached 97 captures but only 87 of them met the deadline, and it
             is 87/300 = 29.0 that is printed.
  M / S      100 * (captures that completed within the deadline AND executed
             Bokeh / Filter) / 300.  Execution means the node has a positive
             observed duration; see the "Recommendation vs execution" note
             below for why the Completed flag is not used.
  Activated  100 * count(RQ3Pacing.transitionDelayMs > 0) / count(nonblank
             transitionDelayMs) over observed eligible outgoing-shot
             intervals; structurally 0 when the pacer is off
  d P50      inclusive P50 of positive RQ3Pacing.transitionDelayMs values over
             observed eligible outgoing-shot intervals; -- when pacing is off.
             d is the applied pacing delay, the same symbol
             Table~\ref{tab:rq4_pacing_summary} uses throughout and the same
             column Table~\ref{tab:rq1_controller_behavior} prints beside its
             Sigma-d; it is introduced in the prose of
             Section~\ref{sec:pacing} and defined by
             Equation~\ref{eq:pacing}.

Sources per cell -- all four arms now live in this repository, so the table no
longer depends on a path in the private implementation clone.  Values are read
from data/ablation_sampling/ (the N=10-balanced copy; the No-control,
Pacing-only and Admission-only workbooks there are byte-for-byte copies of
data/ablation_original/, which stays the untouched source of record):
  No control:      48U_metrics_12MP_normal_baseline_0803.xlsx
                   48U_metrics_24MP_memory_baseline_0803.xlsx
  Pacing only:     48U_metrics_12MP_normal_pacing_only_0803.xlsx
                   48U_metrics_24MP_memory_pacing_only_0803.xlsx
  Admission only:  48U_metrics_12MP_normal_admit_only_0803.xlsx
                   48U_metrics_24MP_memory_admit_only_0803.xlsx
  Full:            48U_metrics_12MP_normal_0803_{1,2}.xlsx
                   48U_metrics_24MP_memory_0803_{1,2}.xlsx

Captures actually reached, per cell, behind the Captures column
(reached / on time, out of 300 -- the second number is what is printed):
  12MP  No control 97/87   Admission only 300/300
        Pacing only 131/122  Full 300/300
  24MP  No control 83/73   Admission only 264/262
        Pacing only 96/87    Full 300/300

Recomputation notes:
  - Values are recomputed directly from the workbooks with the guide's run
    reconstruction rule.
  - The Full arm pools BOTH parts of each condition's collection, which is the
    run set Table~\ref{tab:rq1_controller_behavior} has always used, and reads
    the balanced copy in data/ablation_sampling/.  See
    data/ablation_sampling/README.md for the selection rule and its known
    outcome-dependent bias.
  - The 24MP/Lv4 Pacing-only workbook contains 13 eligible runs.  This table
    takes the first ten in workbook collection order after includedForRq1
    filtering: run ids 5, 6, 7, 8, 14, 15, 16, 17, 18 and 19.
    NOTE THE PROTOCOL ASYMMETRY, and state it if this table is published: the
    Full arm is levelled by the deviation-score rule while this cell is
    levelled by collection order.  The asymmetry is conservative against the
    paper, not for it -- applying collection order to the Full arm would raise
    its 12MP/Lv4 retention rather than lower it (README: 55.0 against 34.3 on
    the old M+S denominator) -- but a reviewer will ask why one table uses two
    rules, so answer it in one sentence rather than leaving it to be found.
  - The predeclared per-cell exclusion is retired.  It removed one 24MP/Lv3
    Full session containing a Capture Timeout, and the guide flagged that it
    could not be applied symmetrically.  The data/ablation_original Full exports contain
    no Capture-Timeout session at all, so nothing is excluded here.  BUT SEE
    THE COLLECTION GAP BELOW -- that is not the same as none having occurred.
  - Execution, not the Completed flag.  ReplayNotes "Recommendation vs
    execution" states that Completed additionally requires
    recommendedAdmit = true, so in the two forced-execution arms it reports
    work that demonstrably ran as not completed.  Execution is the right input
    here; the deadline test is then applied on top of it by the denominator
    rule above, which is what keeps the timed-out capture out of the numerator.
  - Every arm, not only Pacing-only, is filtered through the workbooks'
    includedForRq1 manifest, which drops incomplete non-timeout sessions and
    retains Capture-Timeout and watchdog ones.  The displayed cells are
    affected by 12MP/Lv4/Pacing-only Run 21 (5 shots), which is removed before
    selecting the ten eligible runs.  The 24MP baseline workbook carries no
    RQ1Runs sheet; there every reconstructed Lv4 run is already a timeout or
    30-capture session.
  - In the Admission-only collection, pacing decisions were left enabled for
    observation but not applied to shutter cadence.  Median shot-to-shot on the
    transitions carrying a positive recorded delay (449 ms in 12MP, 886 ms in
    24MP) matches the unpaced median (434 and 839 ms) and is far below the
    recorded delay itself (median 1,709 and 1,080 ms), so those fields are
    shadow outputs rather than applied pacing.  Activated is therefore 0 and
    Delay P50 is undefined (--) for this arm.  The baseline workbooks behave
    the same way; the 24MP baseline records no pacing decision at all.
  - Cross-table consistency: the Full rows here still match
    Table~\ref{tab:rq1_controller_behavior}'s Lv4 rows EXACTLY, on all four
    values -- 12MP 34.3/97.3 and 24MP 41.7/80.3.  SINCE 2026-08-11 THAT TABLE
    PRINTS COUNTS, so the check is now against 30 x the rate: 12MP 10.3/29.2
    and 24MP 12.5/24.1.  Every run in that table is a
    complete, timeout-free 30-capture session, so its H x 10 denominator and
    this table's 300-capture denominator are the same number.  The earlier
    24MP/Lv4 mismatch (41.7 here against 39.3 there) is gone: that table has
    retired the rule that dropped a watchdog-bearing run from the completion
    average, which was the sole cause.  See its own aggregation note for why.
    The two definitions would still diverge for any arm that FAILS, which is
    why the group header here must NOT say "completion" -- but that arm does
    not appear in Table~\ref{tab:rq1_controller_behavior}, so on
    the overlap the two tables now agree by construction.  If a future edit
    makes a Full cell here disagree with that table's Lv4 row, something has
    changed in the run set, not in the metric.

DATA BALANCE NOTE:
  All eight displayed cells hold N=10, so every cell's denominator is exactly
  300 captures.  The Full cells use the balancing protocol in
  data/ablation_sampling/README.md; 24MP/Lv4 Pacing-only uses the
  first-ten-by-collection-order rule recorded above.
  All workbooks carry the 0803 campaign label and the same policy label
  (ReplayScope: RECORDED_RUNTIME / FACTUAL_RECORDED_TARGET / M+S).

Implementation reference inspected at commit:
99aae0af8c3fa1ceb784083446e83c40d0fb917f

"two-factor" was design vocabulary and could be misread as the table's two
CONDITIONS.  Naming the two factors settles it and matches the subsection
title, RQ2: Control-Loop Contribution.

Explicit column widths rather than one uniform \tabcolsep.  Measured at
\scriptsize with \settowidth, the binding content per column is: Condition
30.0pt (its own header), Configuration 45.2pt ("Admission only", which must
not wrap), Survived 26.6pt, Captures 27.5pt (both their own headers), M and
S 15.8pt of data each ("100.0") but 36.8pt jointly for the "Draft stages"
group header, Activated 28.6pt (its own header), $d$ 18.7pt ("$d$ P50").
The eight widths below sum to 229pt.

THE READING RULE FOR THIS WHOLE BLOCK.  Every collision in this table is
between two NEIGHBOURING HEADERS that each fill their own column.  When that
happens the only thing separating them is 2 x \tabcolsep, and at the
\tabcolsep this table can afford -- about 1.2pt -- two bold words 2.5pt apart
read as one phrase.  The fix is never to add \tabcolsep, which is global and
costs 14 gaps to buy one; it is to leave slack INSIDE the narrower of the two
columns, because a \multicolumn{1}{c} header is centred and half of that
slack lands in the gap.  Three pairs are managed this way, and the numbers
below are the gaps they currently get.

WHERE THE WIDTH CAME FROM.  Two header simplifications freed this column set
in sequence, and both were spent rather than returned to \tabcolsep:
  - Dropping "on time" from the Captures header took that column's floor from
    37.5pt to 27.5pt.  8pt of the 10 went to M and S (17pt each to 21pt
    each), which were the table's original tight spot: at 17pt their
    raggedleft data sat about 2.5pt apart and "100.0 100.0" read as one
    number, where at 21pt the gap is 5.3pt of column slack plus \tabcolsep,
    about 7.7pt.  The other 2pt went to Survived and Captures, whose headers
    nearly fill their boxes; they now clear each other by about 3.9pt.
  - Naming the delay $d$ took the last column's floor from 31.8pt
    ("delay (ms)") to 18.7pt.  That is 10.3pt of dead width in a 29pt column,
    and it is the largest single piece of slack this table has ever had.  It
    is spent three ways: 5pt returned to \tabcolsep, which lifts it from
    0.91pt back to 1.24pt and so widens all fourteen gaps at once; 2pt to
    Condition, whose centred header sat 3.0pt from "Configuration" and now
    clears it by 4.0pt; and 1pt to Activated, which was the one column in the
    table whose header was WIDER than its p{} value (28.6 against 28) and was
    therefore silently widening itself through its \multicolumn{1}{c}.
  The delay column keeps 3.3pt of the slack it gave up, as centring room:
"Activated" and "$d$ P50" are the closest pair in the table, and half of that
3.3pt is what puts 4.3pt between them.  Do not shrink it to its 18.7pt floor.
  The last header is the symbol $d$, not a word.  RQ4 prints the applied
pacing delay as $d$ throughout Table~\ref{tab:rq4_pacing_summary}, and one
quantity carries one printed name in this paper -- the same rule that kept
"Slack P5" identical across RQ1 and RQ4 while RQ1 still printed that column,
instead of renaming it "Deadline
margin".  $d$ is introduced in the prose of Section~\ref{sec:guard-limit}
beside $M$ and $S$, which is where this table's other math headers are
defined too.
  It also settles a collision that cost this column two earlier revisions.
The header used to be a word, and the break point was load-bearing: split as
"Delay P50" / "(ms)" its first line sat 1pt from "Activated" and the two
headers read as the single phrase "Activated Delay P50" -- worse than merely
tight, because "Applied Delay P50" was then a real column name in
Table~\ref{tab:rq1_controller_behavior}.  The break is now "$d$ P50" /
"(ms)", which puts the same qualifier back on the first line at 18.7pt where
"Delay P50" needed 27.1 and "delay (ms)" 31.8, and the leading italic letter
is what stops the two headers reading as one phrase even at 4.3pt apart.
Keep the qualifier ON the first line: moving "P50" down to join "(ms)" would
leave a bare 4.9pt "$d$" up against "Activated" and put the widest header
line back on row two.
  "Draft stages executed", not "delivered" and not "completion".  The column is
defined on EXECUTION -- the node has a positive observed duration, see the
"Recommendation vs execution" note above -- so the header now names what is
actually counted, and it matches "M executed (\%)" in
Table~\ref{tab:casestudy_selection}, which is the same quantity on one run.
"Completion" remains forbidden here: it is RQ1's word for a different
denominator.  The group header must still break across two lines; on one line
it measures about 63pt against the 42pt its two columns provide, and the
-8.4pt \multirow nudge below assumes a two-line row one.
  2026-08-15: "work" -> "stages" in this header, under the sharpened
AGENTS.md rule that a Draft stage is what admission admits or skips and
"Draft work" names an amount only.  The two columns under it are the
per-capture execution rates of the stages $M$ and $S$, so the group header
had to name stages.  It costs 2.4pt on row one (34.4 -> 36.8pt), which comes
out of the group's centring slack, not out of \tabcolsep: no p-width moves,
so the \fittabcolsep solution and the 14 gap widths below are unchanged, and
the header still clears its 42pt span by 5.2pt.
  \fittabcolsep (macros.tex) spreads what the p-widths and the three ruled
gaps leave -- 252 - 229 - 5.7 = 17.3pt -- over the 14
inter-column gaps (14 = 2 x 8 columns, less the two suppressed by the @{}
ends), giving about 1.24pt of \tabcolsep, so the outer rules land exactly on
\columnwidth and the fill survives a change of \columnwidth without
re-tuning every p-width.  It iterates because a \multicolumn span makes the
width only piecewise linear in \tabcolsep.  A ninth column does not fit;
use \begin{table*} instead.
  Condition and Configuration carry no group header, so they span both
header rows and centre across the whole header depth, as Device and Starting
overheat level do in Table~\ref{tab:rq1_controller_behavior} and
Table~\ref{tab:timeout_index}.  Leaving them in the second row alone would
sit them below the header's optical centre with an empty cell above.
  The -8.4pt nudge assumes both header rows hold at most two lines, which is
still true: row one's tallest cell is "Draft stages / executed" and row two's
are the two-line \makecells.  Re-derive it if \arraystretch, the font size,
or either row's line count changes.
  Other header cells are wrapped in \multicolumn{1}{c} so that a group
header centers over its column instead of inheriting the data column's
alignment, and in \makecell so one-line and two-line headers share a vertical
centre.  Note that \multicolumn{1}{c} also releases the p-width, so a header
wider than its p{} value silently widens the column; that is why the widths
above are measured against the headers and not only against the data.
  Vertical rules mark the three GROUP boundaries and nothing else: after
Configuration, so the two label columns are cut off from the measurements,
and after Captures and after S, where one \cmidrule group ends and the next
begins.  This matches Table~\ref{tab:rq4_pacing_summary} and
Table~\ref{tab:rq3_admission_audit}, which is the point -- the three tables
now rule at the same places.  Do NOT rule between Condition and
Configuration: both are row labels, and a rule there would separate a label
from its own sub-label.  Do not rule inside a group either; every data cell
holds one number, so a rule between M and S would separate nothing.
  A plain `|' does not work at this \tabcolsep.  Every column that a rule
follows is right-aligned and full: "Admission only" fills 45.2pt of its 46pt
box, and Captures and S hold raggedleft numbers flush to their right edge, so
the only thing between the digit and the rule is one \tabcolsep -- about
1.3pt, which reads as the number touching the line.  The `V' column type
below adds 1.5pt in front of the rule, roughly doubling that gap.  The pad
must be identical in the column spec AND in every \multicolumn that ends on a
rule; a `c|' left behind in a header row would draw its rule 1.5pt to the
left of the body's and show as a jog down the table.
  The three rules and their pads cost 5.7pt, which \fittabcolsep absorbs by
moving \tabcolsep from about 1.4pt to about 0.9pt.  This table has the least
\tabcolsep in the paper, so that is the whole margin -- a fourth rule would
have to be paid for out of a p-width, and the first place to look would be
the 8.7pt of deliberate slack in each of M and S.

---------------------------------------------------------------- 12MP Lv4

---------------------------------------------------------------- 24MP Lv4

### Column map

Recorded from the column-spec labels that used to sit in the tabular preamble.

| Column spec | Column |
| --- | --- |
| `>{\centering\arraybackslash}p{33pt}` | Condition |
| `>{\raggedright\arraybackslash}p{46pt}V` | Configuration |
| `>{\raggedleft\arraybackslash}p{28pt}` | Survived runs |
| `>{\raggedleft\arraybackslash}p{29pt}V` | Captures |
| `>{\raggedleft\arraybackslash}p{21pt}` | M executed |
| `>{\raggedleft\arraybackslash}p{21pt}V` | S executed |
| `>{\raggedleft\arraybackslash}p{29pt}` | Pacing activation |
| `>{\raggedleft\arraybackslash}p{22pt}` | d P50 |

## tab_rq3_admission_summary

`tables/tab_rq3_admission_summary.tex` &middot; Live -- `_4_experiments.tex`, RQ3

RQ3 results from the balanced Full-controller arm of this repository and the
always-admit audit on one device.
Each capture contributes at most one selected decision per optional-work
group: Multi-frame = Bokeh; Single-frame = Filter.

---
2026-08-11 REVISION.  Advisor feedback: merge the two stacked blocks into one
table and drop the Feasible-work Margin and Unsafe-work Overrun columns.
docs/rq-evidence.md (Part 3) holds both removed columns, the deleted note
text that defined their shared sign convention, and the restore procedure.
The file was tables/tab_rq2_admission_summary.tex and the label was
tab:rq2_admission_audit before the RQ renumbering of the same date.

THE MERGED TABLE STAYS INSIDE \columnwidth, AND THAT IS WHAT SETS THE CELL
FORMAT.  Nine columns carrying "1{,}966 (93.6\%)" measure 312pt against the
252pt available -- 60pt over with the column spacing already at zero, so no
width tuning reaches it.  Two things bought it back, and both are load-bearing:
  - Data rows print the COUNT alone and the Overall row prints the SHARE alone.
    The widest cell in a share column falls from 40.9pt to 18.1pt, and the
    percent sign is what tells a reader the last row changed unit.
  - The "[watchdog]" annotation left the Unsafe cells for the note.  That
    column held one digit inside 36.5pt, the worst ratio in the table, and
    dropping the annotation alone is worth 16pt.
The result sums to 224.5pt and solves to about 1.5pt of \tabcolsep, which is
more room than Table~\ref{tab:rq2_ablation} runs on.  Restoring either
convention puts the table back over \columnwidth and forces table* again.

WHAT THE COUNT/SHARE SPLIT COSTS, so nobody re-derives it as a discovery.  The
per-condition admit RATE is no longer printed -- 93.6% at 12MP Multi-frame
against 87.5% at 24MP is a comparison the reader must now do by division, and
the row denominators are not in the table body, which is why the note lists
them.  The alternative that keeps every rate is printing shares on every row
and counts nowhere; it also fits (231.5pt), but it would delete the deployed
volumes and the "3 adverse events in 8,430 decisions" reading with them.

THE ONE THING THE MERGE PUT AT RISK, and what now guards it.  The two halves
are DIFFERENT POPULATIONS: the left four columns are the balanced Full arm
(8,430 deployed decisions), the right four a DISJOINT Pacing-only pool (3,746
audited decisions).  The earlier two-block layout existed precisely so that
one row could not be read as one decision set measured two ways, and merging
removes that structural guard.  Three things replace it and none of them is
optional:
  1. The NOTE names both populations and prints the four deployed row
     denominators.  This used to be a subtitle line under each top-level
     header, which put it inside the exhibit; the subtitles were removed on
     advisor instruction and the note inherited the whole job, which is why it
     is not optional.
  2. The row totals do not close ACROSS the boundary and are not meant to.
     Model admit + Model skip = the left population; Admitted + Skipped closes
     within each factual class of the right one.  On the Overall row the
     percentages therefore sum to 100 within a half, never across.
  3. The prose must still state both denominators.  See WHAT THE RQ3 PROSE
     MUST CARRY below.
If a reviewer ever reads a left cell against a right cell as the same
decisions, restore the two-block layout from the revision document.
---

The Controller-enforced cells come from the balanced Full arm,
data/ablation_sampling/48U_metrics_<condition>_0803_{1,2}.xlsx, with both parts
pooled, runs delimited by a ppSequenceId reset, identical run signatures
counted once and shots after 30 excluded: 70 runs / 2,100 captures at 12MP
normal and 73 runs / 2,116 captures at 24MP memory pressure.  Two 24MP captures
carry no Filter decision, which is why the Single-frame denominator is 2,114.
Regenerate with scripts/rq2_admission_metrics.py.

This arm replaces the earlier unbalanced 0727 pool, and the two are not
directly comparable: the Full arm holds ten runs at each starting overheat
level Lv0--Lv6, whereas the 0727 pool was weighted towards the hot levels.
Standardizing on an equal weight per level, the Multi-frame admit rate moves
72.1% -> 59.9% at 12MP and 56.0% -> 60.5% at 24MP, so the change is a change in
measured behaviour and not only in the level mix.

The Full export contains no Capture-Timeout session -- the collection gap
recorded in docs/rq-evidence.md (Part 2) section 4.3.1 -- so the observed
safety cells characterize only the sessions present in that export.  The 0727
cells were filtered the same way, by dropping timeout-bearing runs.

These cells inherit the balancing protocol of data/ablation_sampling/README.md,
whose deviation score reads reported outcomes and is therefore not
outcome-neutral.  Against the untrimmed data/ablation_original the trim moves
the Multi-frame admit rate 63.1% -> 59.9% at 12MP and 60.2% -> 60.3% at 24MP,
and the Single-frame rate 92.2% -> 92.2% and 85.1% -> 84.7%; only the 12MP
Multi-frame cell moves by more than half a point.

The all-decision audit reports factual feasible/unsafe outcomes crossed with
the shadow-model admit/skip decision before session-sticky demotion.
The Always-admit cells pool two Pacing-only sources.  Runs are reconstructed
identically in both: split on a ppSequenceId reset, identical run signatures
counted once, shots after 30 excluded.  No run signature is shared across the
two campaigns, so the pools are disjoint.

(a) 0729: 659 captures from 34 unique runs in
48U_metrics_12MP_normal_0729_PacingOnly_{1,2}.xlsx -- updated workbook 1
contains all 22 runs in workbook 2 plus 12 additional runs -- and 827 captures
from 53 included runs in 48U_metrics_24MP_memory_0729_PacingOnly_{1,2}.xlsx,
where source run 16 of workbook 1 was invalid/incomplete and excluded.

(b) 0803: a starting-overheat-level subset of
data/ablation_sampling/48U_metrics_<condition>_pacing_only_0803.xlsx.  At 12MP
normal this adds every Lv1 and Lv2 run (2 and 1) plus the Lv4 runs carrying no
unsafe-admitted decision, which is all 11 Lv4 runs, for 14 runs / 223
captures; Lv3 was not drawn.  At 24MP memory pressure it adds every Lv0, Lv1
and Lv2 run (3, 1 and 3), for 7 runs / 169 captures; Lv3 and Lv4 were not
drawn.  Pooled totals are 882 decisions per group at 12MP and 996 Multi-frame
/ 986 Single-frame at 24MP, the Single-frame shortfall being captures that
carry no Filter decision.

Regenerate the Always-admit columns with scripts/rq2_audit_pool.py, which owns
the level-selection rule; `python scripts/rq2_audit_pool.py runs` prints the
per-run census it draws from, including the runs it holds back.
Shadow model decision = afterModelAdmit; factual cost
C = draftEndUptimeMs - nodeStartUptimeMs, the suffix as executed.

!! OPEN DISCREPANCY, PRE-DATING THE 2026-08-11 REVISION AND NOT RESOLVED BY IT.
scripts/rq2_audit_pool.py disagrees with the printed Unsafe-work columns on two
of the four rows.  Its regeneration AND its own hardcoded PUBLISHED constants
both give 12MP Multi-frame 4 (11.4%) / 31 (88.6%) and 24MP Single-frame
3 (5.6%) / 51 (94.4%), where this table prints 2 (5.7%) / 33 (94.3%) and
2 (3.7%) / 52 (96.3%).  The Feasible-work columns agree on all four rows, and
Figure~\ref{fig:rq3_unsafe_spike_anatomy} follows the TABLE, taking apart five
unsafe admits, not the script's eight.  The values printed here were left
untouched by the merge so that the figure and the table continue to agree; the
discrepancy is recorded rather than silently resolved, because deciding it
requires knowing which regeneration the published cells came from.  Resolve it
before submission, and update the figure with the table if the script wins.

The label is deliberately a measurement.  RQ3 scores the model's judgement on
the decision it made, so the audit build forcing every optional node is part
of the condition being measured, not an error to net out.  Netting it out
would answer a different question -- was the whole decision set safe end to
end -- and would read as moving the metric in the model's favour.  That
question is answered per decision in
Figure~\ref{fig:rq3_unsafe_spike_anatomy}, which marks, for each unsafe-admitted
decision, which shipped safeguard would have prevented the overrun.

For reference, on the earlier 0729-only pool, honouring the model's own skips
on both the cost and the budget moved the audit half to:
  12MP Multi   623 (96.4%) / 23 (3.6%)  +3.0%   3 (23.1%) / 10 (76.9%)  -1.4%
  12MP Single  630 (99.4%) / 23 (3.6%)  +4.0%   0 (0.0%)  /  6 (100.0%) -4.5%
  24MP Multi   729 (91.0%) / 72 (9.0%)  +3.7%   0 (0.0%)  / 26 (100.0%) -2.9%
  24MP Single  752 (92.4%) / 62 (7.6%)  +5.4%   0 (0.0%)  / 13 (100.0%) -1.5%
It lowers the unsafe-admit counts and raises the unnecessary-skip counts by
the same act, so it is recorded here rather than reported as the headline.
Those four lines have not been recomputed on the pooled set.  The third and
sixth numbers on each line are the retired Margin and Overrun columns.

Regenerate with data/rq2_spike_anatomy.mjs in the ML implementation
repository.

Every audit count is a count of its own factual class, so Admitted + Skipped
is that class's size.  Where the shares are printed -- the Overall row, since
the count/share split -- the two Feasible-work cells sum to 100% and the two
Unsafe-work cells sum to 100%.

---
WHAT THE RQ3 PROSE MUST CARRY
---
  the two populations   The left half is the balanced Full arm, 70 runs /
                        2,100 captures at 12MP and 73 / 2,116 at 24MP.  The
                        right half is a DISJOINT Pacing-only pool, 882
                        decisions per group at 12MP and 996 Multi-frame / 986
                        Single-frame at 24MP.  Since the merge this is the
                        single most important sentence in the RQ3 prose.
  the audit's design    The right half scores the shadow-model admit/skip
                        decision, taken before session-sticky demotion,
                        against the factual outcome; its counts are shares of
                        their own factual class and sum to 100% within each.
  the selection caveat  The audit's 0803 part is a starting-overheat-level
                        subset and is NOT outcome-neutral; at 24MP the level
                        rule alone removes that source's entire
                        unsafe-admitted population.  The block comment above
                        owns the detail.
  severity              Shortfall is the median predicted deficit normalized
                        by the Capture Timeout deadline over model skips in
                        the deployed half.  The audit half no longer prints a
                        severity column; if the prose needs the realized
                        magnitudes, take them from the revision document and
                        say they are not in the table.
  the group definition  Each capture contributes at most one decision per
                        optional-work group: Multi-frame = Bokeh, Single-frame
                        = Filter.

---
Layout mechanics
---
Nine columns inside \columnwidth, on the count/share split described in the
revision block above.  \fittabcolsep (macros.tex) solves for the \tabcolsep
that lands the outer rules on \columnwidth; its fourth argument is 2 x the
number of columns: 18.

Measured at \scriptsize, binding content per column -- the largest of its data,
its Overall cell and its own header:

  column          binding content              measured   p{}
  Group           "Single-frame"                 36.5      37
  Model admit     "94.7\%" (Overall)             18.1      19
  Unsafe          header (data is one digit)     20.6      21
  Model skip      "5.3\%"  (Overall)             14.6      15
  Shortfall       header                         26.4      27
  Feas. Admitted  header                         28.4      29
  Feas. Skipped   header                         24.5      25
  Uns. Admitted   header                         28.4      29
  Uns. Skipped    header                         24.5      25

Sum 227pt plus 2.4pt of rules, so \tabcolsep solves near 1.26pt.  Five of the
nine columns are header-bound and therefore carry their own internal slack,
which is what keeps neighbouring right-aligned numbers apart at that spacing.
The one pair with no slack to spare is Model admit against Unsafe; their group
header "Model admit" needs 39.2pt against the 40pt the two columns provide, so
do not shave either.

A header line wider than its p{} value inside a \makecell OVERFLOWS, and a
plain cell wider than it silently WRAPS with no warning.  Re-measure with
\settowidth before changing any label.

THE POPULATION SUBTITLES ARE GONE FROM THE HEADER, ON ADVISOR INSTRUCTION.
They read "balanced full-controller arm, 8,430 decisions" and "disjoint
pacing-only pool, 3,746 decisions" and were the merge's in-exhibit guard
against reading a left cell against a right cell.  Both populations, and the
per-row denominators the count format no longer shows, now live in the note
below, which is therefore NOT optional -- it is the only thing standing
between this table and the misreading the two-block layout used to prevent.

Column alignment follows the advisor's standing rule: every header cell is
centred horizontally and vertically, and every DATA cell is right-aligned.
Group stays left-aligned because it is a row label, not a measurement, which
is also what Table~\ref{tab:rq2_ablation} does with Configuration.

One line, as in Table~\ref{tab:rq4_pacing_summary}.  "TABLE N: " plus the
caption text must clear \columnwidth = 252pt at \footnotesize.

The Unsafe cells no longer carry a bracketed cause, so the \rqtwoun spacer
that used to equalise their widths is gone with it; the column is plain
right-aligned digits.  If "[watchdog]" ever comes back, bring the spacer back
with it -- without it the "]" of "1 [watchdog]" and a bare "0" land on the
same right edge and leave the two DIGITS 34pt apart.

Model admit + Model skip is a complete partition of the deployed population.
On the data rows the two counts therefore add to the row's denominator, and on
the Overall row the two shares sum to 100.0.  That is the only check a reader
has on the left half, so keep it -- and keep the note's denominators, because
without them the addition has nothing to land on.

THE POLICY-SKIP COLUMN WAS REMOVED, AND THE ADMIT COLUMN CHANGED MEANING
WITH IT.  An earlier revision printed a three-way partition -- Run, Policy
skip, Model skip -- where Run was the subset of model admits the controller
actually executed and Policy skip the subset a sticky session demotion
suppressed.  Policy skip is not part of the admission JUDGEMENT this half
scores: it is deployed-policy state inherited from an earlier rejection, and
it answers a different question.
  Dropping it forced the admit column to change.  Run alone would have left
59.9 + 6.4 = 66.3 per cent on the 12MP Multi-frame row, with a third of the
population vanished and no trace of where.  The column therefore now prints
the model's own decision, Run + Policy skip, which closes against Model skip.
The headline moves with it: the 12MP Multi-frame figure is 93.6% of decisions
admitted BY THE MODEL, where the previous 59.9% was the share the controller
went on to execute.  Both are true and they are not interchangeable -- do not
quote this cell as an execution rate, and check any other section that cites
59.9% before reusing the number.
  THE "Safe" COLUMN WENT WITH IT, AND HAD TO.  A revision in between printed
Model admit 1,966 beside Safe 1,257 and watchdog 1.  Those do not close --
Safe and watchdog split the EXECUTED decisions, not the model admits -- so
every reader subtracted, found 708 missing, and had to be told where it went.
An exhibit that provokes a subtraction it cannot answer is worse than one
that omits the term.  Nothing of substance is lost: Safe was
1,257 / 1,936 / 1,274 / 1,791 -- "all of them except the watchdog" -- and the
watchdog count alone carries the safety result, 3 adverse events across 8,430
deployed decisions.  A bare count of a rare adverse event needs no
denominator to be read, and printing none asserts none.  Realized C > B is
zero on every non-watchdog execution.

Shortfall is median 100(U-B)/D over model upper-bound skips only, where U is
the predicted suffix upper estimate, B the live remaining budget, and D the
configured Capture Timeout deadline.  The only nonzero watchdog count is at
24MP Multi-frame; those two watchdog timeouts occurred with 9 ms and 53 ms of
deadline margin.

The Unsafe-work Admitted cells are bold: they are the audit's failure mode --
work the model would have let through although it overran -- and they are the
four cells Figure~\ref{fig:rq3_unsafe_spike_anatomy} then takes apart one
decision at a time.  Nothing else in the table is bold, which is what makes
it read as emphasis rather than as another header level.

Two one-line header rows above the column names, so \multirow[c]{3} centres
with only the small nudge below.  The population subtitles that used to sit
under each top-level header were removed on advisor instruction and moved to
the note; see the layout comment above for why the note is now mandatory.

------------------------------------------------------------- 12MP normal
Model admit + Model skip = N on every row of the LEFT half: 1,966 + 134 =
2,100, 2,091 + 9 = 2,100, 1,852 + 264 = 2,116, 2,071 + 43 = 2,114, and
7,980 + 450 = 8,430 overall.  On the RIGHT half the pair that closes is
Admitted + Skipped WITHIN a factual class: 831 + 16 = 847 feasible and
2 + 33 = 35 unsafe on the first row, 847 + 35 = 882 decisions.  Every pair
of printed percentages sums to 100.0 with no rounding residue.
  SINCE THE COUNT/SHARE SPLIT, the data rows close by ADDITION and only the
Overall row closes to 100.0.  That is the check to keep stating: a reader
who wants a row's denominator adds its two counts, and the note prints the
four deployed totals so the addition can be verified without doing it.

SOURCE of the left half.  These cells are the A3 regeneration
(data/ablation_sampling Full, the documented source), not an earlier
revision's numbers, because the demoted and upper-bound counts exist only
in that regeneration and the row has to sum.  Two cells moved as a result,
and both were already recorded as failing to reproduce: 12MP Single-frame
$n$ was printed as 2,099 where the regeneration gives 2,100 (and
1,936 + 155 + 9 = 2,100, so the old value cannot close), and 12MP
Multi-frame's watchdog was printed as 1 where both A3 and A2 give 0.  The
consequence for the prose: no arm has an unsafe admit at 12MP in the
deployed half, and the only two watchdogs are at 24MP.

---------------------------------------------------- 24MP memory pressure

Overall pools WITHIN each half, never across it.  Left: the four deployed
rows, 7,980 + 450 = 8,430.  Right: the four audited rows, 3,470 + 98 =
3,568 feasible and 5 + 173 = 178 unsafe decisions, which is the sum of the
printed counts and not a separate regeneration.
  THIS ROW CHANGES UNIT, and the percent sign is what says so.  Every share
is of its own half: the two deployed shares close to 100.0 against 8,430,
and each audit pair closes to 100.0 within its own factual class.  Shortfall
is already a percentage on every row -- it is a median severity, not a
share -- and Unsafe stays a count here because it has no denominator to
take a share of.

### Column map

Recorded from the column-spec labels that used to sit in the tabular preamble.

| Column spec | Column |
| --- | --- |
| `>{\raggedright\arraybackslash}p{37pt}\|` | optional-work group |
| `>{\raggedleft\arraybackslash}p{19pt}` | model admit, n / Overall share |
| `>{\raggedleft\arraybackslash}p{21pt}\|` | unsafe admits, count only |
| `>{\raggedleft\arraybackslash}p{15pt}` | model skip, n / Overall share |
| `>{\raggedleft\arraybackslash}p{27pt}\|\|` | model-skip shortfall P50, % of D |
| `>{\raggedleft\arraybackslash}p{29pt}` | feasible work, model admits |
| `>{\raggedleft\arraybackslash}p{25pt}\|` | feasible work, model skips |
| `>{\raggedleft\arraybackslash}p{29pt}` | unsafe work, model admits |
| `>{\raggedleft\arraybackslash}p{25pt}` | unsafe work, model skips |

## tab_rq4_pacing_sizing

`tables/tab_rq4_pacing_sizing.tex` &middot; Live -- `_4_experiments.tex`, RQ4

RQ4: the delay engages selectively as retrospective pressure tightens, and
stays a small share of the backlog it drains.

Adopted as the RQ4 exhibit of record on 2026-08-21, succeeding
`tab_rq4_pacing_selectivity`, whose entry keeps the reasoning for the earlier
swap away from `tab_rq4_pacing_summary`.  That reasoning still applies: the
summary table measured d against d*, which is a decomposition of prediction
error at a fixed coefficient rather than a sizing report.

CAPTION AND LABEL ARE STILL THE PREDECESSOR'S.  The caption title reads "RQ4
pacing selectivity" and the label is tab:rq4_pacing_selectivity_half.  Nothing
references that label yet, so both can be renamed when the RQ4 prose is
written; until then do not assume the printed title matches the
research-question name.

Sources, all committed, one CSV row per printed cell.  From
data/rq3/policy/summary.csv:
  activationPercent band spare_over_40 / spare_20_40 / spare_0_20 /
    projected_overrun     the four Paced-by-pressure-band cells; the CSV
                          carries the percentage in value and the band size in
                          denominator, and the table prints both
  delayOverBacklogPercent P50   the d/B column; its denominator is
                          pacedTransitions, which the cell prints as "N paced"
  backlogDrainingDelaySharePercent   the Overlap backlog column
Regenerate with scripts/rq3_pacing_summary_metrics.py sampling.

Population.  The balanced Full arm: 1,920 analyzed transitions over 70 runs at
12MP normal and 1,861 over 69 runs at 24MP memory pressure, of which 411 and
471 were paced.  Two sums must hold after any regeneration and are the fastest
check on a mis-transcribed cell: the four band denominators partition the
analyzed transitions, and the four paced counts sum to pacedTransitions.

THE BANDS ARE MEASURED, NOT MODELLED.  They bin retrospective pressure in
budget points, half-open [lo, hi), with the last band open at its lower edge
and equal to the set carrying a positive retrospective matched-policy target.
Activation against the controller's OWN online score is true by construction --
it holds on 100% of analyzed transitions in both conditions -- so it is not
evidence of anything and must never be reported as a result.  This is stated at
the head of scripts/rq3_selectivity_metrics.py; read it before adding a column.

2026-08-21 CORRECTION.  The 24MP deficit cell printed 69.3% (97/140).  Its CSV
row is 68.79 over 141, and 141 is what makes the band denominators sum to the
1,861 analyzed transitions, so the printed denominator was one short and the
percentage followed it.  The cell now prints 68.8% (97/141).  No other cell
moved; every one of the remaining eleven was checked against its CSV row in
the same pass.

## tab_rq4_pacing_selectivity

`tables/tab_rq4_pacing_selectivity.tex` &middot; Superseded 2026-08-21 by `tab_rq4_pacing_sizing`; kept on disk

RQ4: delay sizing is conservative yet work-conserving.

Replaces tables/tab_rq4_pacing_summary.tex as the RQ4 exhibit (2026-08-13).
Why the swap, carried here from the \input site in _4_experiments.tex: the
summary table measured d against the retrospective target d*, which is
algebraically an estimator report at a fixed coefficient; the selectivity table
asks instead whether the delay is selective, proportionate and bounded.
The superseded file is left on disk unreferenced; swap the \input in
_4_experiments.tex to restore it.  This table is the main RQ4 exhibit of
record as of 2026-08-14, in `AGENTS.md` and in docs/rq-evidence.md (Part 1)
alike; the analysis blocks in Part 1 were written against the summary table and
read as the reasoning behind the RQ4 claim, not as a description of what is
printed.

Sources, all committed:
  data/rq3/estimator/summary.csv        requiredDelayDecisions, requiredAndPaced
  data/rq3/coordination/summary.csv     realizedWorkEnvelopeCovered, belowMandatoryFloor
  data/rq3/policy/summary.csv           backlogDrainingDelaySharePercent, delayOverBacklogPercent,
                                        activationPercent and its bands, burstDelaySharePercent,
                                        bursts, burstsNeverPaced
  data/rq3/estimator/outcome_matrix.csv the below-floor class's skip rate and margin
  data/rq3/coordination/action_summary.csv  the flexible class's target-or-next audit
Regenerate with: rq3_pacing_summary_metrics.py sampling; rq3_coordination_metrics.py;
rq3_coordination_audit.py; rq3_estimator_metrics.py.
Every printed cell has a CSV row.  Keep it that way.

---
THE HEADLINE, AND WHY IT IS THIS ONE
---
Delay sizing is conservative yet work-conserving.  The row reads left to right
as one argument: the need is sparse; where it exists pacing engages; the
mandatory reservation is covered almost always; the optional-inclusive target is
only partly covered, by design, because admission owns optional work; and
almost every applied millisecond drains real backlog rather than idling.

The superseded exhibit measured d against d* directly and made the over-shoot
its headline.  That comparison is algebraically an estimator report, not a
sizing report: d* is the SAME delay rule with realized inputs, so

    d - d* = (Chat - C) + (Bhat - B)/2                (closes to 0.50/0.76 ms)

and every cell of that table was a decomposition of prediction error at a fixed
coefficient.  It could not answer the question RQ4 asks in _4_experiments.tex,
and its consequence -- d lands at 5.4x and 3.6x d* where it covers -- was a
self-criticism with no engineering consequence attached.

MANDATORY-TARGET COVERAGE IS THE CELL TO PROTECT.  100.0 and 90.0 per cent.  It
is the metric that makes the coverage taxonomy readable as a result instead of
a shortfall: full coverage is 67.1 and 59.3, which looks weak until the reader
sees that the gap is optional work and that admission is the loop that owns it.
Printing mandatory beside full, under one group label, is what carries that.

---
WHAT EVERY CELL MUST NOT BE CALLED
---
d*      the retrospective matched-policy target.  NOT the physically required,
        minimum, or optimal delay.  CSV fields and class keys containing
        `required` are internal compatibility names for it (AGENTS.md).
d*_man  a retrospective SUFFICIENT reservation condition evaluated on mandatory
        work only.  NOT the timeout boundary, NOT a safety guarantee.  The
        caption and note must never imply that covering it prevents a timeout;
        RQ1 owns the outcome and Table~\ref{tab:rq2_ablation} owns the
        controller-off comparison.
90.0%   14 decisions fall below the floor at 24MP.  Their disposition is
        printed in the note and is strong: all 14 ran a demoted sequence
        (outcome_matrix.csv, below_floor, skipped_this_pct 100.0), their worst
        realized margin was 4.39 per cent of the budget
        (coordination/summary.csv, belowMandatoryMarginMsMin 307 ms), and none
        timed out.  AGENTS.md is explicit that admission demotion documents
        coordination but does NOT itself erase a mandatory-floor deficit, so do
        not write the 14 away as "handled by admission".

---
THE ONE EXPOSURE THIS TABLE CREATES, AND HOW THE NOTE ANSWERS IT
---
Column two says a delay was retrospectively required on 4.1 and 7.5 per cent of
decisions.  Pacing actually engaged on 21.4 and 25.3 per cent
(policy/summary.csv, activationPercent).  A reader who holds both numbers asks
why the controller paced five times more often than hindsight required, and the
answer is the conservatism of Chat -- the same fact as the 5.4x/3.6x over-shoot.

Do not leave that unanswered, and do not answer it by hiding the activation
rate.  The note answers it with selectivity, which is measured and strong:
engagement is 1.4 and 1.0 per cent on decisions carrying more than 40 per cent
of the budget in surplus, against 77.2 and 69.3 per cent on the required tail --
ratios of 55.9x and 71.9x.  Pacing is concentrated, not blanket.  The band
figures are activationPercent band spare_over_40 in policy/summary.csv and the
required-tail figures are activationPercent overrunStrict.

THE RATIO IS PRINTED, AND BOTH OF ITS SIDES MUST USE THE STRICT CUT.  It is
printed because it is the answer to the exposure above and a reader should not
have to divide two numbers to reach it.  This comment carried 71.4x through one
revision, which is 68.79/0.96 -- the BAND form of the required tail, denominator
141.  The note prints the strict form, 69.3 per cent over 140, so the two must
not be mixed; the [`tab_rq4_pacing_summary`](#tab_rq4_pacing_summary) entry
records the same 141-against-140 defect in an earlier table.  On the counts the ratios are
(61/79)/(9/652) = 55.9 and (97/140)/(6/623) = 71.9.  Recompute from counts if
either side moves -- the rounded percentages lose a tenth on the 24MP ratio.

---
THE RUNS THAT NEVER PACED, AND WHY THEY SIT IN THE COST SENTENCE
---
19 of 70 and 13 of 69 runs applied no delay at all (burstsNeverPaced).  It is
the run-level form of the selectivity claim and the strongest single statement
of delay minimality this collection supports, so it has to be printed
somewhere.  It goes in Cost rather than Selectivity for two reasons.  Its
population is RUNS -- 70 and 69 -- which is Cost's population and nobody else's
in this note; Selectivity is entirely per-decision, and a run-level rate dropped
into it would put a fourth denominator in one sentence.  And it is the qualifier
the cost figures need: a P50 of 18.1 per cent reads as what a typical run pays,
and it is not, because 27 and 19 per cent of runs pay zero.

Printing it also supplies the run denominator, which this note owed under its
own every-denominator rule (see VERIFIABILITY below) and did not carry.

The sentence says RUN, not "burst", which is what it said through one revision.
docs/rq-evidence.md (Part 1) maps burst -> run for printed text, RQ1 counts runs, and
this file's own comments already called it the per-run cost.  As of 2026-08-14
"burst" is banned from printed manuscript text everywhere, Section 3 included:
the approach text now says "consecutive captures" or "queue-local", and the
evaluation exhibits keep saying "run".  Exported field names such as
burstDelaySharePercent and burstsNeverPaced are internal compatibility names
and are not renamed.

A selectivity LADDER over four pressure bands was drafted as a second block and
cut: it needs a second partition of the same decisions (rho bands rather than
d* > 0), and two partitions in one exhibit cost more in reader effort than the
extra rows return.  One sentence in the note carries the same claim.

---
DO NOT ADD AN "EITHER LOOP" COLUMN.  ONE WAS BUILT AND REMOVED 2026-08-13.
---
It counted a decision when pacing engaged OR optional work was skipped on that
capture or the next, per pressure band, and read 21.9 / 51.8 / 74.5 / 92.4 at
12MP and 31.6 / 54.1 / 68.3 / 92.2 at 24MP -- monotone in both conditions,
agreeing to 0.2 points on the row that mattered.  It is indefensible, for three
reasons that were measured, not argued:

1. STICKY DEMOTION MAKES THE SKIP TERM A STEP FUNCTION OF BURST POSITION.
   DraftSequenceAdmissionPolicy holds a demotion until the Draft queue drains,
   so once a burst demotes, every later capture in it is demoted: of the
   decisions at or after their run's first demotion, 100.0 per cent are demoted
   (809 of 809 at 12MP, 784 of 784 at 24MP).  The skip indicator is therefore
   close to "has this burst demoted yet", which is monotone in shot index --
   and so is retrospective pressure, because backlog accumulates.  The
   association is mechanical.
2. A RULE THAT READS ONLY THE SHOT COUNTER BEATS IT.  Substituting
   "skip := shot >= 13" gives 45.7 / 83.3 / 92.0 / 98.7 and 42.2 / 76.2 / 91.0 /
   97.9: the same monotone rise, higher everywhere.  A permutation null that
   shuffles the skip label within (run x burst phase) reproduces the headline --
   null mean 92.09 and 92.14 against observed 92.4 and 92.2, P(null >= observed)
   = 0.62 and 0.59, 100 per cent of draws monotone.
3. IT DESTROYS THE SELECTIVITY CLAIM.  The rho >= 0 over rho < -40 ratio is
   55.9x and 71.4x for pacing activation and 4.2x and 2.9x for Either loop,
   barely above the shot-counter rule's 2.2x and 2.3x.  And its low-pressure
   cells are not coordination: all 143 and 197 decisions they counted had
   optional work skipped on the target's own Draft at median pressure -62.3 and
   -51.5 per cent of budget -- half the budget spare -- with 134 of 143 and 191
   of 197 receiving no delay.  Those cells report user-visible quality loss with
   the budget unused, printed as a virtue.

The legitimate use of "either control engaged" is per DECISION, not per band:
data/rq3/estimator/thin_margin_tail.csv carries an either_control_engaged
column, yes on all eleven sub-1-per-cent decisions, which is the fact AGENTS.md
requires the prose to carry beside the margin minimum.

---
POPULATIONS.  AGENTS.md: every statistic printed beside a population must be
computed on that population.  This table mixes three, so every count-based cell
prints count/denominator with its percentage beneath, and the note names each.
---
  Delay required        all analyzed decisions      1,920 and 1,861
  Activated, Mandatory, Full   the required tail    79 and 140
  Backlog overlap, d/B  the paced decisions         411 and 471
The required tail uses the STRICT cut d* > 0, which is what every
required-delay population in the pipeline uses; see the OVERRUN_PCT comment of
scripts/rq3_pacing_summary_metrics.py for why pressure == 0 needs no delay.
At 24MP that is 140, not the 141 of the rho >= 0 pressure band.

The counts were added 2026-08-14 on author instruction, in the form
n/denominator over (pct), so the denominator of every printed percentage is
visible in the exhibit itself and not only in the note.  Every numerator has a
CSV row; none is back-computed from a rounded percentage:
  Delay required     projectedOverrunStrict            79/1,920, 140/1,861
  Activated          79 - overrunButUnpaced 18 = 61,   140 - 43 = 97
                     (policy/summary.csv; the same 61/79 the ratio uses)
  Mandatory covered  79 - belowMandatoryFloor 0 = 79,  140 - 14 = 126
  Full covered       realizedWorkEnvelopeCovered       53/79, 83/140
The first four reproduce the printed percentages to the digit shown (77.215,
69.286, 90.0, 67.089, 59.286, 4.115, 7.523).

NEITHER CELL OF THE Applied delay BLOCK CARRIES COUNTS, AND NEITHER MAY BE
GIVEN ANY.  Backlog overlap is backlogDrainingDelaySharePercent, a share of
applied delay TIME, not of decisions -- its CSV row has an empty denominator
field, and the count-shaped fact nearby (waitsOutlastingBacklog, 0 and 8) is a
different statistic.  d/B P50 is a median.  That block therefore prints no
population marker at all: an n column holding 411 and 471 was built and removed
on author instruction the same day, because a bare count column beside two
statistics that are not counts of it reads as their denominator and is not one.
The note carries the population instead -- "over the 411 and 471 paced
decisions" -- and it is the only place that population appears, so do not trim
it out of the note.

Layout.  Column labels are centred, horizontally and vertically
(\makecell[cc] inside the \multicolumn wrapper, which is what puts the one-line
Activated on the midline between Mandatory and covered).  Data cells are flush
right.  The Condition column went from 55pt centred to 38pt ragged-left with an
explicit break in each label (12MP / normal, 24MP / mem. press.); left alignment
is what keeps the two labels readable once they wrap.  The tabular stays at 7
columns and \fittabcolsep 14.

THREE MECHANICAL TRAPS, ALL THREE HIT WHILE BUILDING THIS TABLE.
  1. \newline inside a \raggedleft p-column CENTRES the line it ends, because
     the \hfil it appends balances the column's \leftskip fil.  Measured: 61/79
     sat 5.95pt from the left edge and 5.85pt from the right while (77.2) below
     it was flush.  Use \linebreak, which appends nothing and lets the fil
     absorb the slack.  \raggedright columns are unaffected -- both fils are on
     the same side there -- but the Condition column uses \linebreak too, so the
     file has one break command and not two.
  2. Right-aligning a count over a parenthesised percentage aligns the ")"
     with the last DIGIT above it, which is the misalignment a reader sees.
     \cpct/\cpctb hang the count over that parenthesis with \phantom{)}; the
     two lines then share a right edge on their digits (verified with
     pdftotext -bbox: 385.92 for both lines of the 12MP cell).  The bold form
     puts the phantom inside \textbf, since a bold ")" is wider.
  3. A bare \makecell in one of these p-columns loses the row baseline and drops
     the taller headers by a line; keep the \multicolumn wrapper, and remember
     the V rules live in that wrapper's column spec once it is present.
The Delay required header is \multirow[c], not the \multirow[2] it carried
before 2026-08-14; "2" is not a valid vertical position for that argument.
Correcting it does NOT silence the 6.08pt overfull \vbox the build reports
against this table -- that box is the three-line header content against the two
rows multirow sizes for it, it is the identical 6.08011pt the committed original
produced, and it has no visible effect.  Removing it means dropping the multirow
and setting Delay in the group row with required / (%) beneath, which loosens
the three lines; that was judged not worth the change.  It is the table's only
box warning: there is no overfull \hbox, so a NEW warning means something in
these widths stopped fitting.

Two roundings to leave alone:
  d/B P50 at 12MP is 10.4474, so it prints 10.4.  policy/summary.csv stores the
  intermediate 10.45 and rounding that a second time gives 10.5, which is what
  an earlier revision printed.  24MP is 8.5732, so 8.6 is correct directly.
  Backlog overlap at 24MP is 98.72, so 98.7.

---
WHAT THE PROSE MUST STILL CARRY -- THIS TABLE DOES NOT PRINT IT
---
1. The minimum realized deadline margin: 0.11 per cent of the budget (8 ms) at
   12MP and 0.20 per cent (14 ms) at 24MP, with the saturation context
   AGENTS.md requires -- backlog already 42-79 per cent of the budget, queue
   wait 31-75 per cent, overheat 5-6 or late in a burst, and pacing or an
   optional-work skip engaged on all eleven sub-1-per-cent decisions.  Stated
   bare it reads as a lucky escape; with the saturation it reads as the
   mechanism working at its limit.  Never upgrade it to a bounded-margin or
   guaranteed-deadline claim.
   Source: data/rq3/estimator/thin_margin_tail.csv, one row per sub-1-per-cent
   decision, 6 at 12MP and 5 at 24MP; summary.csv's marginUnder1PctDecisions
   confirms the population is complete.  The 24MP minimum there is 14 ms (run
   1#6 shot 24), NOT 9 ms: a 9 ms observation exists in the raw 30-shot margin
   series but on a capture that is not an analyzed pacing decision, so it is a
   different population and must not be quoted beside these counts.
2. That the delay lands at 5.4x and 3.6x d* where it covers the target
   (sizing_summary.csv, `covered`: 432/80 and 685/188), and that the cause is
   the reserve construction -- Chat is a burst MAXIMUM while Bhat is a CENTRAL
   estimate of a whole queue.  Concede it in one sentence and name Chat as the
   parameter a team porting the controller should tune.  A reviewer who divides
   the printed backlog-relative delay by a d* recovered from the prose will find
   it either way; better it is the paper's sentence than the reviewer's.
   QUOTE THE RESERVE ERROR OF THE POPULATION THE SENTENCE IS ABOUT: beside the
   5.4x/3.6x the correct figures are the `covered` rows' own
   reserve_error_p50_pct, +41.4 and +44.4 per cent.  The larger +87.0 and +90.8
   belong to `paced_none_required` (n = 350 and 374) and may only be quoted
   beside that population.  Both are conservative, so the argument does not need
   the larger pair; it needs the honest one.
3. The 18 of 79 and 43 of 140 required-tail decisions that received no delay,
   with the mechanism, which is single and specific.  On those the reserve was
   right -- Chat - C median +74 ms and -9 ms -- and only the backlog clock was
   short: Bhat - B median -844 ms (12.1 per cent of budget) and -1,362 ms
   (19.5 per cent), worst -1,586 and -2,319 ms.
   data/rq3/policy/boundary_mechanism.csv scores backlog_under_estimated on 60
   of the 61.  The cause is the one Section~\ref{sec:pacing} states: E advances
   by the POINT sum per queued Draft, so the shortfall compounds with queue
   depth, and these decisions sat behind 8 and 6 queued Drafts at the median.
   Bounds on the reading: the deficit was small (median 2.2 and 3.8 per cent of
   budget, minimum 0.19 and 0.11), 24 of the 43 at 24MP were already running a
   demoted sequence, and none of the 61 timed out.
   This pairs with item 2 QUALITATIVELY and must be written that way: one
   asymmetry -- a maximum statistic for one Draft against a central statistic
   for a whole queue -- produces over-reservation where the reserve dominates
   and under-pricing where the queue does.  Do NOT put item 2's reserve
   percentages and this item's backlog percentages into one arithmetic
   comparison; they are measured on different populations.
   DO NOT write that pacing "trusted admission to skip" or "deferred to
   admission".  No such path exists: CaptureAvailablePacer passes no numeric
   deficit share to admission (its class comment at CaptureAvailablePacer.kt
   lines 39-46, and Section~\ref{sec:pacing}), and the measured cause is that
   Bhat was short, so the controller never saw a positive deficit.  It did not
   choose to abstain.  The note's admission figures are a CO-OCCURRENCE audit
   over the 2C horizon, which AGENTS.md fixes as an observed admission-action
   audit, not causal attribution.

---
VERIFIABILITY
---
Every count behind the table can be recomputed from two CSV rows:
  79 = 53 covered + 26 flexible + 0 below floor   (coordination/summary.csv)
  140 = 83 + 43 + 14
so Mandatory covered is 79 - 0 and 140 - 14, and Full covered is 53 and 83.

THE TABLE PRINTS ONLY PERCENTAGES, so the note carries every denominator: 79 of
1,920 and 140 of 1,861 for the required tail, and 411 and 471 for the paced
decisions.  That is the only path from a printed percentage back to a count, so
do not trim those numbers out of the note to save a line.  The counts were moved
out of the body deliberately: "140 / 1{,}861 (7.5\%)" needs 56pt, which forced
the condition stub to wrap to two lines and broke its alignment against the
single-line numeric cells.

Scoped to this group, as in tab_rq2_ablation.tex: a thin vertical rule with
1.5pt of lead-in, used to bound the header groups.

LAYOUT.  Two data rows, so every stub is ONE line: a two-line \makecell stub
beside single-line numeric cells left the numbers hanging at the wrong
baseline, which is why the condition column is 53pt and the labels are not
stacked.  Every count moved to the note for the same reason -- printing
"140 / 1{,}861 (7.5\%)" cost 56pt, which is what forced the stub to wrap.

Widths are \settowidth measurements at \scriptsize against
\columnwidth = 252pt, each column set 1-2pt above its widest cell:
  55  "24MP mem.\ press." 53.90     25  "req.\ (\%)" 23.63
  28  "Activated" 26.87             32  "Mandatory" 30.72
  23  "covered" 21.94               25  "Backlog" 23.33
  19  "$d/B$" 14.64
Sum 207pt plus three rules (0.4pt for | and 1.9pt for each V) = 211.2pt, so
\fittabcolsep lands tabcolsep near 3.4pt and the tabular keeps a few points of
slack.  Keep that slack: \makecell builds an inner tabular, so the header cells
do not measure exactly as bare text, and a budget fitted to the last point
overflows by a point or two for reasons no cell explains.

A GROUP LABEL CAN BE THE BINDING CONSTRAINT, NOT A DATA CELL.  A \multicolumn
with c alignment is NOT clipped to the p{} widths it spans: if its natural
width exceeds the span, TeX widens the spanned columns and the tabular grows
past \columnwidth, which \fittabcolsep cannot recover because widening
tabcolsep widens the span and the table together.  The two labels and the
spans they need, at the fitted tabcolsep of 3.137pt:
  "Where required (\%)"  62.80  vs  28+32+23 + 4 tabcolsep = 95.5   OK
  "Applied delay"        42.13  vs  25+19    + 2 tabcolsep = 50.3   OK
"Where a delay was required (\%)" needed ~100pt and was shortened; the per-cent
sign was dropped from "Applied delay (\%)" (53.11pt) for the same reason, and
the note states that both of its columns are shares.  Recheck both
inequalities before relabelling either group or narrowing columns 6-7.
Measure with \sbox{\bx}{\scriptsize\makecell[c]{...}} -- \makecell pads, so a
bare \settowidth of the text understates these by several points.

One rule per group boundary, three in total: the stub, the all-decisions
share, the required-tail block, the applied-delay block.  "Full covered" is
spelled out rather than abbreviated to "Full cov." so that it reads as the
pair of "Mandatory covered"; the contrast between the two is the point.

The two stub columns are CENTRED, horizontally by \centering here and
vertically by the [c] of their \multirow below.  Centring the condition
column also matches tab_rq1_end_to_end_summary.tex and tab_rq2_ablation.tex,
which both set Condition with \centering.  \arraybackslash is required
after \centering or \\ stops ending rows.

\multirow{2}{*}, NOT {=}.  The two stub labels are centred across both header
rows, which is what {*} buys.  The WIDTH ARGUMENT MATTERS: {=} sets the box
to the column width and produced a permanent "Overfull \hbox 1.01884pt ...
[] []" -- two boxes, no text -- reported at the line where the tabular is
invoked, from inside \fittabcolsep's \sbox as well as from the real
typesetting, and invariant to every p-width and to the fit target.  An
explicit width 2pt under the column made it worse by exactly 2pt, i.e.
\multirow does not compensate the difference.  {*} takes the natural width
of the content and does not overflow.  Do not "tidy" these back to {=}.

TWO lines in the stub, not three.  The header block is three lines tall (one
group row plus a two-line sub-label), but \multirow{2} budgets its box at
twice the NORMAL row height rather than the actual heights, so a three-line
stub overflows it -- "Overfull \vbox 6.08011pt too high" at the tabular's
line, constant against every other change.  "Delay required (\%)" is
therefore set over two lines and its column widened to 40pt to hold
"required (\%)"; it is spelled out, not abbreviated to "req.".

Mandatory covered, Backlog overlap and d/B carry the headline and are bold.
Full covered is deliberately NOT bold: its gap to Mandatory is the
coordination reading, and bolding both would flatten that contrast.

14 = twice the seven columns, which is \fittabcolsep's contract (macros.tex).
It fits this tabular to 251.99992pt against \columnwidth = 252pt, at
tabcolsep 3.137pt.  For reference if the fit ever needs re-tuning, the width
is PIECEWISE in \tabcolsep, measured over the real preamble --
    tabcolsep  0       1       2       3       4    pt
    width      213.72  225.72  237.72  250.22  263.22 pt
slope 12.0 up to 2pt, then 12.5, then 13.0, as the two \multicolumn group
labels stop and start binding their spans.  \fittabcolsep solves a linear
model, so on a piecewise curve the remedy for a residual is the target, never
the p-widths -- the solver just re-absorbs those into tabcolsep.

The minipage is load-bearing.  The table environment sets \centering, which
leaks into the last line of any paragraph typeset directly inside it.
\parindent is zeroed so the sentences run on as one block.

### Column map

Recorded from the column-spec labels that used to sit in the tabular preamble.

| Column spec | Column |
| --- | --- |
| `>{\centering\arraybackslash}p{55pt}\|` | condition |
| `>{\centering\arraybackslash}p{30pt}V` | delay required (%) |
| `>{\raggedleft\arraybackslash}p{28pt}` | activated on the tail |
| `>{\raggedleft\arraybackslash}p{32pt}` | mandatory covered |
| `>{\raggedleft\arraybackslash}p{23pt}V` | full covered |
| `>{\raggedleft\arraybackslash}p{25pt}` | backlog overlap |
| `>{\raggedleft\arraybackslash}p{19pt}` | d/B P50 |

## tab_rq4_pacing_summary

`tables/tab_rq4_pacing_summary.tex` &middot; Superseded 2026-08-13 by `tab_rq4_pacing_selectivity`; kept on disk

Coordination-aware RQ4 main-paper summary table, single column, two blocks.
docs/rq-evidence.md (Part 1) is the authoritative handoff for this exhibit and the
source of every claim limit recorded below.

Sources:
  data/rq3/estimator/outcome_matrix.csv     block (a)
  data/rq3/estimator/sizing_summary.csv     block (b)
  data/rq3/estimator/thin_margin_tail.csv   the note's slack-tail sentence
  data/rq3/estimator/summary.csv            the identity check and the repricing
  data/rq3/policy/summary.csv               the per-run pacing cost

---
The reading path, and why each block has its own population
---
Two questions, in this order, and a reviewer must be able to answer each one
without leaving its block:

  (a) When a reservation was actually required, how much of it did pacing
      cover?   Population: the decisions with d* > 0 -- 79 and 140 -- and
      every column is a count or a median over ALL decisions in the class,
      paced or not.  "Did pacing fire" is therefore a column, because a
      decision that received nothing still belongs to the class whose
      coverage the row reports.

  (b) When pacing fired, was the delay conservative but still work-
      conserving?   Population: the paced decisions -- d > 0 -- and every
      column is a median over exactly those.

The two populations are different sets, so no single row can serve both, and
the previous revision's defect was exactly that: it printed one four-class
partition of every analyzed decision with the estimator errors as columns, so
on the top row "Applied delay P50 = 377 ms" was a median over the 350 PACED
decisions while "Draft reserve error P50 = +230 ms" was a median over all
1,841 in the class -- and the caption then offered the second number as the
explanation of the first.  Recomputing the errors on the population the
sentence is about does not merely sharpen them:

                           class-wide (printed before)   paced only (correct)
  Draft reserve error       +230 / +250 ms                +555 / +653 ms
  Backlog error             -19  /  -43 ms                +445 / +231 ms

The backlog error changes SIGN.  The old numbers said the reserve over-covered
against a roughly correct backlog clock; the correct ones say that on the
decisions pacing actually acted on, BOTH estimates were conservative at once.

---
Why (a) prints no "none was required" row, and how the totals stay checkable
---
An earlier revision made (a) a partition of every analyzed decision, so its
first row was the complement of the required set.  That kept a visible sum but
cost the thing (a) exists to measure: with 1,920 as the denominator the
under-sized tail reads as 0.8% of decisions, which buries it.  Against the
population where a reservation was required it is 10.0%, and that is the
number a reviewer needs.

Verifiability is preserved without the row.  (a)'s block labels print
79/1,920 and 140/1,861, (b) prints 350/1,841 and 374/1,721, and
1,841 + 79 = 1,920 and 1,721 + 140 = 1,861.  Do not remove the denominators
from either place; they are the only remaining path to the analyzed totals.

---
Printed labels, and what each of them replaced
---
Column one of both blocks prints the CONDITION that defines the row, not a
name for it.  Successive revisions named these classes "Covered by pacing" /
"Left to admission" / "Below the mandatory floor", then "Covered in full" /
"Mandatory work" / "Less than mandatory"; each round argued about what the
name asserted -- "Left to admission" claimed a hand-off the table prints no
evidence for -- while the inequality asserts exactly the cut and nothing more.
Printing it removes the naming problem instead of relitigating it, and it
removes three glosses from the note.

  d >= d*                 was "Full requirement" / "Covered in full".
  d*_man <= d < d*        was "Mandatory work" / "Left to admission": the
                          delay reached the mandatory work but not the
                          optional work that also ran.
  d < d*_man              was "Less than mandatory" / "Below the floor".
  d > 0, d* = 0    (b)    paced although the realized work required nothing.
  d >= d* > 0      (b)    the covered class, restricted to the paced; it is
                          100% paced, so this is the whole of (a)'s top row.

Use \mathrm for the subscript.  "d^{*}_{man}" sets m, a and n as three math
variables, which both reads wrong and measures 7pt wider than
"d^{*}_{\mathrm{man}}" -- enough to have cost (a) a full point of \tabcolsep.

d* itself is NOT defined in this table any more.  The RQ4 PROSE carries the
definition, d* = ceil([B + 2C - max(0,T)]+ / 2), and must introduce it before
this table is read; the note glosses only d*_man, the two hatted errors, d/B
and inside B.  If the prose ever drops the formula, put it back in the note
beside d*_man -- not in the caption, which is deliberately one line.

  Unapplied, d* - d      was "Missing delay".  The formula sits under the word
                         so the column defines itself.
  Slack                  RQ1 printed this quantity as "Slack P5 (%)" until
                         2026-08-11, when that column was dropped on advisor
                         feedback; the archived values are in
                         docs/rq-evidence.md (Part 3).  THIS TABLE IS NOW
                         THE ONLY PLACE THE PAPER REPORTS DEADLINE SLACK, so
                         the naming rule that produced "Slack" no longer has a
                         second site to agree with -- but keep the name and
                         keep it normalized, both so the archived RQ1 column
                         can be restored without a rename and because an
                         earlier revision of this table called it "Deadline
                         margin", which gave one quantity two printed names.
  Decision-time error    was "Estimator error".  Both columns are what the
                         controller held AT THE DECISION minus what the
                         pipeline went on to do, so the label names the instant
                         the estimate was made rather than the machinery.
  inside B               was "absorbed", which never said what was absorbed
                         into what, and briefly rho_B, which put a Greek symbol
                         used nowhere else in the manuscript on a quantity the
                         words already name.  With B defined in the note, the
                         share of d that lies inside the outstanding backlog
                         needs no symbol.

(b) reuses (a)'s row labels verbatim where the classes coincide, so "Full
requirement" names the same set in both blocks.  It is 100% paced, which is
why its two error cells are identical in (a) and (b); that identity is the
control that makes the "none required" row's difference legible.

---
Definitions (short form printed in the note)
---
  B          measured Draft backlog at the pacing decision
  T          budget left in the deadline window at the decision
  C          realized duration of the admitted Draft sequence
  C_mand     the mandatory part of C: DynamicFunction, Encoding and measured
             Draft overhead, i.e. C with the optional work admission can skip
             removed
  d          the applied pacing delay
  d*         ceil( [B + 2C - max(0,T)]^+ / 2 ), the retrospective
             matched-policy target
  d*_mand    the same expression on C_mand: the mandatory floor
  Bhat       PacingReplay.beforeBacklogMs, the controller's backlog clock
  Chat       beforeDraftSequenceReservedDurationMs, the Draft reserve

The 2C horizon is the deployed prospective model: (i) the Draft that begins
after the pacing decision and (ii) the Draft of the next capture released by
that delay.  Pacing deliberately applies half of the positive projected
deficit so it does not turn all residual pressure into user-visible delay,
relying on node-time admission to skip optional work when its suffix bound
exceeds the live budget.  This is an intuitive coordination heuristic, not an exact
fixed-point derivation or a literal transfer of a half-deficit to admission.
A positive UNAPPLIED delay is therefore an unmet prospective reservation and
NOT an observed overrun, which is why the Slack column is printed beside it:
it says what the capture actually kept.  The caption must keep that clause --
without it, "Unapplied max 920 ms" reads as a 920 ms deadline overrun.

---
The two error columns
---
Away from the max(0,.) clip -- on the 61 and 97 decisions carrying both a
positive applied delay and a positive required delay --

    d - d*  =  (Chat - C)  +  (Bhat - B) / 2

holds identically.  scripts/rq3_estimator_metrics.py asserts it and it closes
to 0.50 and 0.76 ms, which is the two ceilings in the formulas.  That identity
is what makes these two columns a decomposition rather than two loose
diagnostics, so the caption states it.  It does NOT close on (b)'s "none
required" row, where d* is clipped at zero: there the two errors are what the
controller held, not a decomposition of a positive d*.

UNITS.  The identity is in milliseconds; the COLUMNS print each error as a
share of the realized quantity it estimates -- (Chat-C)/C and (Bhat-B)/B --
because +308 ms does not tell a reader whether the reserve was slightly or
grossly conservative, and +41% does.  Two consequences the caption and the
note both carry.  First, the printed cells no longer add: the ratios have
DIFFERENT denominators, so the decomposition has no percentage form, and the
caption states it in ms for that reason.  Second, each ratio is formed per
decision and only then taken at P50, so the percentage is not the millisecond
median divided by anything a reader can see; both forms are emitted in the
CSVs.  Nothing here leaks the Capture Timeout budget, which is what the units
rule below actually protects: C and B are not the budget.

  Draft reserve Chat.  CaptureAvailablePacingSession.getMaxDraftSequence-
  DurationMs prices it at the session's observed MAXIMUM Draft duration for
  the capture's size bucket, re-projected onto the admitted sequence.  A
  maximum against a typical realized duration over-covers, and it enters the
  formula twice.  It is positive on every row of (b) -- +87.0, +41.4 and
  +90.8, +44.4 per cent -- and largest exactly where the delay was least
  needed.  Normalised, the size of it is legible: on the decisions that
  required nothing the reserve is close to DOUBLE the Draft that actually ran.

  Backlog clock Bhat.  queuePacingDecision advances it by each queued Draft's
  POINT prediction plus one learned between-node overhead.  Per Draft that is
  nearly right (P50 +16 and +19 ms) but widely dispersed (P05 -135 and
  -293 ms), and unlike the reserve it is SUMMED over the queue, so the
  dispersion accumulates in both directions.  It is the term whose SIGN
  separates over-shooting pacing from under-shooting pacing: +11.9 and +6.7 on
  (b)'s over-shoot rows, -12.8, -29.6 and -19.8 on (a)'s short-fall rows.  The
  reserve only sets the magnitude of the over-shoot.  The gradient down (a)'s
  column survives normalisation -- -0.1, -12.8 at 12MP and -1.6, -19.8, -29.6
  at 24MP -- which is the mechanism the block exists to show.

The asymmetry is the finding an SEIP reader can act on: the controller already
knows to price a single Draft by a conservative statistic, and prices a whole
queue by a central one.

POPULATION RULE.  (a)'s error columns are class-wide and (b)'s are paced-only,
and the note says so.  Never quote (a)'s error cells as the explanation of a
Paced count, and never copy a value between the blocks except on the row where
the class is fully paced.

---
LIMITS -- all of these must survive any future edit
---
LIMIT -- closed loop.  Every quantity is arithmetic on the realized trace.
The repricing in docs/rq-evidence.md (Part 1), the unapplied delay, and the queued
pricing error are NOT recoverable time: a different delay changes later
arrivals, backlog, admission, thermal state and realized Draft duration.  The
same rule forbids rescaling the recorded delay by 0.5 or 0.75.

LIMIT -- the mandatory floor.  d*_mand is a sufficient reservation condition
reconstructed after the run, not the timeout boundary.  The 14 misses cluster
in four 24MP runs, none produced an actual Capture Timeout, and their Slack P5
-- 4.53% of the budget -- is the LARGEST of the three classes, which is the
direct evidence that the floor is conservative.  On the 11 that received no
delay at all the controller's own online pressure Bhat + 2*Chat - T was
non-positive (-46 to -1,729 ms), so zero was the correct output of the deployed
formula given its inputs; correcting the backlog clock alone flips that sign on
11/11 and reaches the floor on 9/11
(data/rq3/estimator/floor_zero_delay_account.csv).

LIMIT -- coverage is not severity.  The classes of (a) say how much of a
reconstructed reservation was satisfied.  They do NOT rank realized timeout
risk, and the table itself shows why: the d < d*_man row has the LARGEST Slack
P5 of the three, 4.53 against 1.03 and 2.61.  The caption used to say so in
words; now that the rows are inequalities and the caption is one line, the
burden moves to the RQ4 prose.  Never write that a worse coverage class was
closer to timing out, and do not let the ordering of the rows imply it.

---
The realized slack tail, and why this table reports none of it
---
This table prints Slack P5 per class and nothing else about the tail: no min
column, and no sentence in the note.  The RQ4 PROSE owns the minimum.  Both
halves of that were argued over more than once, so both are recorded.

No min COLUMN.  An earlier revision printed min and P5 side by side.  Per
class the minimum is not always the statistic that carries the tail -- on the
14-decision floor block min and P5 are 4.39 and 4.53, where it adds nothing --
and which of the two is informative depends on the class n.  A sentence can
say that; a column cannot.  A bare min column also reads as "no Capture
Timeout was luck", with nothing beside it to answer that.

No sentence in the NOTE either, which is the later and less obvious call.  It
looks like a gloss on Slack P5 and is not one: the 0.11% is the minimum of the
no-delay-required class, which (a) excludes and (b) prints no Slack column
for, so it is the minimum of NO column this table prints.  6 of the 11 sub-1%
decisions sit in that same unprinted class.  On the rows (a) does print, P5
understates the class minimum by only 1.03x to 4.1x -- 1.03 against 0.31, 2.61
against 1.91, 2.48 against 0.61, 1.20 against 0.51, 4.53 against 4.39 -- so
the printed column is not being misread without it.  The 65x figure that once
justified keeping it, 0.11 against 7.20, is min against P5 WITHIN that
unprinted class and is invisible to the reader either way.

None of that makes the tail unimportant; it makes it a finding rather than a
reading aid, and AGENTS.md now requires the prose to carry it with the
saturation context and the claim limit attached.  The facts are below.

Eleven of the 3,781 analyzed decisions finished under 1% of the budget, 6 at
12MP and 5 at 24MP (deadline_margin_under_1pct per class in
outcome_matrix.csv, and one row each in thin_margin_tail.csv).  On all eleven:

  the backlog B at the decision was 42-79% of the budget and the queue wait
  alone consumed 31-75% of it, so the slack is thin because the pipeline was
  already nearly full of budget-consuming work;
  ten of eleven were paced, at 288 to 921 ms; and
  eleven of eleven had pacing or an optional-work skip engaged.  There is no
  case in this tail where neither control acted.

The tightest, 8 ms at 12MP (run 2#21 shot 10, overheat level 5), had 785 ms of
pacing applied AND optional work skipped, and its required delay was zero: the
reservation was satisfied, and the rest of the budget went to a 2,614 ms wait
against a 3,369 ms backlog.  The eleven are the saturated states, either late
in a burst (24MP run 1#2 shots 29 and 30, backlog at 79% and 76% of budget) or
at overheat 5-6, and they coincide with the captures at which the guard-
bypassed baseline of Table~\ref{tab:timeout_index} first times out at the same
level.  That last correspondence is across ARMS -- an association between shot
index and overheat level, not paired executions -- so it may be written as a
coincidence and never as "these would have timed out".

Do not claim from any of this that the realized slack was bounded or that the
controller guaranteed the deadline.  The counterfactual belongs to the
controller-off and pacing-only arms of Table~\ref{tab:rq2_ablation}.

---
WHY THERE IS NO "OPTIONAL WORK SKIPPED" COLUMN
---
It was printed in an earlier revision and removed, because it could not do the
job it looked like it was doing.  The question it appeared to answer is why 11
of the 14 floor misses went unpaced, and the d < d*_man row already answers
that without it: Paced 3 of 14 beside a backlog error of -29.6% says the
backlog clock was badly low, and the column reads -1.6, -19.8, -29.6 down the
rows, so the mechanism is visible as a gradient rather than asserted.
The skip rate cannot answer it at all -- d*_mand is defined on the mandatory
work, so skipping optional work cannot close a mandatory-floor deficit -- yet
printed beside "Paced 3" it invites exactly that reading.

Two further reasons it was the weakest column.  Demotion is session-sticky, so
the 100% on the floor row is largely "these four runs had already entered the
demoted regime" rather than a response to these decisions.  And at 12MP the
flexible band's rate, 26.9%, is BELOW the 42.4% population rate: admission did
not step in more often there, so the column argued against the coordination
claim it appeared to support.

The rates are still generated.  outcome_matrix.csv carries skipped_this_pct
and skipped_either_pct for every class; the two-Draft rate is an observed
action audit over the 2C horizon and must never be phrased as causal
attribution of the next admission decision to this delay.  If a reviewer asks
whether admission was engaged on the floor misses, the answer is 14/14 target
Drafts demoted, and it belongs in prose with the "does not close the deficit"
clause attached.

---
Layout mechanics
---
\fittabcolsep, not a hardcoded \tabcolsep.  A fixed value leaves the two
blocks at different natural widths -- 237pt and 229pt for the values a previous
draft used -- so they sit unaligned inside a 252pt column.  \fittabcolsep
iterates \tabcolsep until the outer rules land on the target width, which is
what makes the two blocks agree with each other and with \columnwidth.  Its
fourth argument is 2 x the number of columns: 16 for (a), 14 for (b).

Every paired quantity is SPLIT into its own sub-columns under a \cmidrule
group -- "P50 | max" rather than "P50 / max" -- because a cell holding one
number needs only that number's width while "72 / 582" needs both plus a
separator, and because a reader could not tell at a glance which side of a
slash was which statistic.  The one exception is (b)'s Delay column, where
"0 -> 377" is kept as a single cell: the arrow is directional, so it carries
its own reading order, and required-against-applied is the comparison the
block exists to make.  Do not convert it back to a slash pair.

Vertical rules mark the group boundaries only.  Every data cell holds one
number or one arrow pair, so ruling each column would add lines that separate
nothing.

Widths are measured against the HEADERS as well as the data: a \makecell
header line wider than its p{} value overflows rather than widening the
column, and a \multicolumn group label wider than its span widens the columns
under it.  "Decision-time error P50 (\%)" is the binding label in both blocks
and is stacked as "Decision-time" / "error P50 (\%)" for that reason; set on
one line it measures 62pt against a 54pt span.

The block labels carry only the condition and its population.  A label is a
single unwrappable line in an `l' multicolumn spanning every column, so its
natural width is a floor on sum(p-widths) + 2*(n-1)*tabcolsep: a label
approaching \columnwidth drives \fittabcolsep to a tabcolsep near zero and
every data cell then touches its group rule.  Keep them short, and put
per-run quantities in the note rather than on them.

The 12MP d < d*_man row prints its two counts, 0 and 0, and spans
the remaining five columns with a phrase.  The zero is structural -- no 12MP
decision fell below the floor -- so the counts are real measurements and are
printed; the five quantities behind them are undefined on an empty set, and a
row of "--" there would read as measurements that went missing, which is the
opposite of what it means.

---
Units, and the rule that decides them
---
The Capture Timeout budget is an internal constant and must not be recoverable
from the manuscript.  It becomes recoverable the moment one quantity is
printed BOTH as an absolute duration and as a share of the budget, so the rule
is per quantity, not per table: delays in milliseconds (as in the RQ1 tables),
slack as a share of the budget (as in RQ1's "Slack P5"), the two estimator
errors as shares of C and B, d/B and inside-B as shares of the backlog, pacing
cost as a share of the run's elapsed time.  Before adding a row, check which
unit the quantity already uses elsewhere.

Note what the rule does and does not forbid.  A share of the BUDGET beside the
same quantity in milliseconds is the leak; a share of C or of B is not, since
neither is the budget and neither is printed absolutely anywhere in the paper.
That is why the estimator errors could move to per cent while Unapplied stays
in milliseconds, and why Slack must stay a share and never gain a ms column.

---
Population
---
Complete 30-capture runs from
data/ablation_sampling/48U_metrics_{12MP_normal,24MP_memory}_0803_{1,2}.xlsx:
70 and 69 runs, 1,920 and 1,861 analyzed pacing decisions.  Records affected
by the known timeout-measurement error were removed as invalid observations,
which is data-quality filtering and NOT outcome-based survival conditioning;
no valid analyzed run experienced an actual Capture Timeout, and the
manuscript must not describe this population as survival-conditioned.
Watchdog-truncated decisions lack a complete realized Draft duration and are
excluded from the required-delay reconstruction only.

The device is a Device column in Table~\ref{tab:rq1_end_to_end_summary} and is
named in the population paragraph, so the caption does not repeat it.

Regenerate with scripts/rq3_estimator_metrics.py (both blocks, the errors, the
slack tail and the repricing) and scripts/rq3_pacing_summary_metrics.py (the per-run
cost); see docs/rq-evidence.md (Part 1) for the order.  The two scripts build their
populations independently and agree on every shared quantity: 411 and 471
paced decisions, 100.0% and 98.7% of delay inside the backlog, and 19 of 70
and 13 of 69 runs never paced.  Treat a disagreement as a defect, not as a
rounding difference.

One line.  The rows are now the conditions themselves, so the prose that used
to name and rank the coverage classes has no work left to do, and $d^{*}$ is
defined in the RQ4 prose rather than here.  The table no longer carries the
formula anywhere, so that prose has to introduce it before this table is
read; see the d* note at the top of this file.

---
(a)  Coverage, over every decision that required a delay
---

Every width is the measured maximum of its own data and its own header,
taken with \settowidth at \scriptsize against \columnwidth = 252pt:
  50  "$d^*_{man}\le d<d^*$" 46.0  (header "Coverage" is only 28.2)
  16  "83" 7.0, as in (b)          33  "11 (25.6\%)" 32.2
$n$ cannot go below 16 even though its data needs 7: the "Pacing Decisions"
group label spans it together with paced, and that span is 16+33+2 tabcolsep.
(b) proves the label fits 55.9pt; at 10pt for $n$ the span falls to 51.5pt
and the label would widen both columns from above.
  12  "P50" 11.3                    14  "max" 12.8
  23  "P5 (\%)" 22.1                21  "$\hat C-C$" 19.6 / "$-29.6$" 20.6
  21  "$\hat B-B$" 19.9
Sum 203pt plus four rules, so \fittabcolsep lands tabcolsep near 3.0pt.
Column one is ruled off from Decisions: every other group in the header is
bounded by a rule, and without one the conditions ran into the counts.
A header line wider
than its p{} value inside a \makecell OVERFLOWS rather than wrapping, and a
plain-text cell wider than it silently wraps to two lines; both happened in
an earlier draft at 54pt.  Re-measure before changing any label.

The count columns went from 24pt to 33pt when the stacked "53" over
"(67.1\%)" became one line, and the errors paid for it: as percentages they
need 21pt where "$-1{,}392$" needed 26.  Percent signs are NOT repeated in
these cells -- "53 (67.1\%)" carries one already, and the error columns
declare theirs in the group header, which is what keeps them at 21pt.

Header row one carries the group labels at two lines, row two the
sub-labels at one, so the header is three lines tall.  A label spanning
both rows is therefore centred with \multirow[c]{2} plus an offset: the
box \multirow computes from 2 x the standard row height is shorter than
the header, and the residue is half of row two.  Re-derive the offset if
either row changes its line count.  \centering inside the \multirow
centres the \makecell box in the 60pt parbox; the DATA in this column
stays flush left, because the row labels are read as a list.

Plain $n$, matching (b) column for column, and the same 16pt.  Two
rejected alternatives, in order:

  $n$ with a share beside it -- "53 (67.1\%)" -- needs 33pt and puts a
  second percentage next to the paced share, which is a share of a
  different denominator.  Two percentages per row, two denominators.

  $n/N$ -- "53 / 79" -- reads well and is narrower still at 24.3pt, but
  it repeats a constant three times per condition and states in six
  cells what one block label states once.  If it is ever reinstated, N
  must be this block's own population and NOT the analyzed total:
  14/1{,}861 prints the under-sized tail as 0.8\% where 14/140 is
  10.0\%, a 13x dilution of the one finding this block exists to show.

The population moved to the block label instead, which is where a
reader starts and where it costs one line rather than six cells.

Stacked fractions, not "$\hat C-C$".  The cells hold percentages, so a
header written as a difference of two durations names a quantity in
milliseconds and not the one printed underneath it.  The fraction costs
nothing: 18.46pt against 19.61pt for the difference, so it is NARROWER
than the notation it replaces, and 1.2pt taller, which the sub-header row
absorbs without gaining a line.  Do not "simplify" it back.

------------------------------------------------------------- 12MP normal
The label carries this block's population and its share of the analyzed
total, and it is the only place either appears.  A revision that stripped
it to the condition alone argued that 79 is the row sum (53+26+0) and the
4.1% share is a sentence the prose owns.  Both are true and neither
survives contact with a reader: 79 and 140 then appear NOWHERE in the
table, so the reader sums a column to learn what the percentages in the
paced column are shares of, and 1,920 needs that sum plus (b)'s 1,841.
The share is also the first thing the RQ4 narrative says -- pacing
addresses a tail, it is not a fixed per-capture delay -- and a reader who
meets the table before that sentence has no way to see it.

A block label is a single unwrappable line spanning every column, so it is
a floor on the table's width.  These two measure 149pt and 175pt against a
244pt span, so there is room; re-measure with \settowidth before extending
either, and do not add the paced sum back (61 and 97 are the Paced
column's own total).

Both counts are printed rather than dashed: the zero is structural, and a
dash reads as a measurement that is missing.

---------------------------------------------------- 24MP memory pressure

---
(b)  Sizing, over the paced decisions only
---
(a) says whether the delay was ENOUGH.  It cannot say whether it was MORE
than enough, because it prints no applied delay, and "appropriately sized" is
a two-sided claim.  These are the only two populations on which the
comparison is defined: decisions that required nothing and were paced anyway,
and decisions whose requirement the delay covered.  On (a)'s short-fall rows
the applied delay is below the requirement by construction, and (a)'s
Unapplied column already reports that side.

The first half of the answer is unflattering and is meant to be: where the
delay covers the requirement it lands at 5.4x and 3.6x it at the median.

The second half is why that is not the same as arbitrary.  d* is a RESIDUAL
-- (B + 2C - T)/2 -- so it goes to zero whenever the deadline window is wide,
however much Draft work is queued.  Being a multiple of that residual
therefore says nothing about whether the wait was large in absolute terms.
Priced against the Draft work actually outstanding when it was applied, the
same delay is 10.8, 9.5, 7.3 and 20.3 per cent of the backlog, and 98.3 to
100 per cent of every millisecond of it ran while at least that much work was
still in the pipeline: only 0 of 403 waits at 12MP and 8 of 457 at 24MP
outlast the backlog they drain (sizing_summary.csv,
waits_outlasting_backlog; the denominators are this block's two populations,
350+53 and 374+83, not the 411 and 471 paced decisions, because the
short-fall rows are not in it).  The wait is not created by pacing; it is
moved from after the shutter to before it.

Do NOT upgrade that into a claim that the queue would have been unstable
without pacing.  This block is arithmetic on the realized trace.  The
controller-off and pacing-only arms of Table~\ref{tab:rq2_ablation} are where
that comparison lives, and the RQ4 prose should cross-refer to them rather
than re-derive the claim here.

An earlier revision printed Over-applied d - d* P50/P95 in two more columns.
It was replaced: required-against-applied already shows the over-shoot, and
the difference of the two printed medians is not the median difference
(432 - 80 = 352, while the median of d - d* is 320), which cost a caveat for
a column that carried nothing new.  Both are still emitted.

Measured the same way:
  47  "$d>0$, $d^{*}=0$" 46.2       (header "Population" is only 32.5)
  16  "1{,}841" 15.8            36  "350 (19.0\%)" 35.7
  34  "$188\to685$" 33.7            (header "Delay P50" is only 31.0)
  21  "$\hat C-C$" 19.6 / "$+90.8$" 20.5     21  "$\hat B-B$" 19.9
  19  "20.3\%" 18.1             27  "inside $B$" 26.3
Sum 221pt, tabcolsep near 1.9pt -- this block runs tighter than (a)'s 3.1pt
and is the one to watch when a label grows.

The unit moved from the sub-label to the group label, "Delay P50" over
"(ms)", because "$d^{*}\to d$ (ms)" measures 38.0pt where the arrow cell
alone needs 34: at 32pt the 24MP cell silently wrapped "$188\to685$" onto a
second line, which no overfull warning reports.  Check this column by eye
after any change to it.

Same three-line header and the same centred \multirow as (a).  An earlier
revision could not use \multirow here and left both labels top-aligned in
row one; it fails only when row two's first cell is left empty, which
makes \multirow's box shorter than its own content.  Giving the spanning
cells their offset, as in (a), places them on the header's optical centre.

Decisions is split into n and paced, exactly as in (a), instead of the one
"350/1{,}841 (19.0\%)" cell an earlier revision stacked over two lines.
That cell was the widest thing in the block at 53.4pt on one line, and it
also hid the source-class size inside a ratio; as two columns the same
information costs 52pt, prints on one line, and matches (a) column for
column.  Keep n: with (a) restricted to the required set, 1,841 and 1,721
here are half of the only remaining path to the analyzed totals.

The label is the condition $n$ COUNTS, exactly as in (a), and $d>0$ is not
part of it: 1,841 is the whole $d^{*}=0$ class and the paced column is what
restricts it to 350.  An earlier revision labelled this row
"$d>0$, $d^{*}=0$" and so asserted a conjunction its own $n$ does not
satisfy -- read literally it claims 1,841 paced decisions at 12MP, where
the analyzed total is 1,920 and only 411 were paced at all.

\raggedright cancels the \centering the float sets, which would otherwise
centre every line of the note; \par inside the group makes it take effect.

MOVED TO THE RQ4 PROSE, NOT DROPPED.  These results have no other home in
the manuscript and Section RQ4 must carry them:
  population estimator errors  reserve  +24/+232/+808 and -129/+253/+1,025;
                               per-Draft price -135/+16/+450 and
                               -293/+19/+503, all P05/P50/P95 in ms.  Do not
                               write that the reserve error is "almost
                               entirely above zero": its 24MP P05 is -129 ms.
  the queue relation           r = 0.95 and 0.88 between the summed per-Draft
                               pricing error and the backlog clock error
  the floor repricing          at or above the floor on 11 of 14 misses
  how often a delay was needed 79 of 1,920 (4.1%) and 140 of 1,861 (7.5%).
                               Was on (a)'s block labels.  It is the first
                               thing the narrative says -- pacing addresses a
                               tail, it is not a fixed per-capture delay.
  the responsiveness cost      18.1/24.5% and 9.8/29.7% of a run's elapsed
                               time at P50/P95.  Was in the note.  Say
                               "visible but bounded", never "negligible".
  the thin realized-slack tail 11 of 3,781 decisions under 1% of the budget;
                               the tightest kept 0.11%, which is 8 ms, on
                               12MP run 2#21 shot 10 at overheat 5.  Was in
                               the note until it was found to describe a
                               population the table prints no Slack for --
                               see below.  The prose OWNS this number now
                               and must carry three things with it: the
                               saturation that explains it (backlog already
                               42-79% of the budget, queue wait 31-75%,
                               overheat 5-6 or late in a burst), that pacing
                               or an optional-work skip was engaged on all
                               eleven, and the claim limit -- realized slack
                               is an outcome and not a bound, and what a
                               baseline would have done is RQ1's question.
                               Row-by-row facts: thin_margin_tail.csv.

Why the tail is prose and not a note.  It reads like a gloss on Slack P5 but
it is not one.  The 0.11% is the minimum of the no-delay-required class,
which (a) does not contain and (b) prints no Slack column for, so it is the
minimum of NO column this table prints; 6 of the 11 thin decisions sit in
that same invisible class.  On the rows (a) does print, P5 understates the
class minimum by only 1.03x to 4.1x -- 1.03 against 0.31, 2.61 against 1.91,
2.48 against 0.61, 1.20 against 0.51, 4.53 against 4.39 -- so the printed
column is not being misread without the sentence.  The 65x figure that once
justified keeping it (0.11 against 7.20) is min against P5 WITHIN the
invisible class.  It is a real and important finding; it is just not a
reading aid, which is the only thing this note is for.

THE NOTE'S RULE.  It carries only what a printed cell cannot be read without:
the gloss on a symbol that appears in a row or a header, what the (%) columns
are a share of, and which population each error is a median over.  A finding
is not a reading aid -- if a cell is still legible without the sentence, the
sentence is prose.  All three entries above failed that test and left.
\par\vspace{3pt}
{\tiny\raggedright
$d^{*}_{\mathrm{man}}$ uses $C$'s mandatory part alone.  $\hat{C}-C$ and
$\hat{B}-B$ are estimate minus realized at the decision, each as a share of
what it estimates and taken per decision before the median: class-wide in~(a),
paced only in~(b).  $d/B$ is the delay over the Draft work still outstanding
while it ran, and \emph{inside} $B$ the share of the delay that elapsed
against that work.\par}

### Column map

Recorded from the column-spec labels that used to sit in the tabular preamble.

| Column spec | Column |
| --- | --- |
| `>{\raggedright\arraybackslash}p{50pt}\|` | coverage condition |
| `>{\raggedleft\arraybackslash}p{16pt}` | decisions n |
| `>{\raggedleft\arraybackslash}p{33pt}\|` | paced n (%) |
| `>{\raggedleft\arraybackslash}p{12pt}` | unapplied P50 |
| `>{\raggedleft\arraybackslash}p{14pt}\|` | unapplied max |
| `>{\raggedleft\arraybackslash}p{23pt}\|` | slack P5 |
| `>{\raggedleft\arraybackslash}p{21pt}` | Chat - C, per cent of C |
| `>{\raggedleft\arraybackslash}p{21pt}` | Bhat - B, per cent of B |
| `>{\raggedright\arraybackslash}p{47pt}\|` | population condition |
| `>{\raggedleft\arraybackslash}p{16pt}` | source-class n |
| `>{\raggedleft\arraybackslash}p{36pt}\|` | paced n (%) |
| `>{\raggedleft\arraybackslash}p{34pt}\|` | delay dstar -> d |
| `>{\raggedleft\arraybackslash}p{21pt}` | Chat - C, per cent of C |
| `>{\raggedleft\arraybackslash}p{21pt}\|` | Bhat - B, per cent of B |
| `>{\raggedleft\arraybackslash}p{19pt}` | d / B |
| `>{\raggedleft\arraybackslash}p{27pt}` | inside B |

## tab_setup

`tables/tab_setup.tex` &middot; Live -- `4_1_setup.tex`, evaluation setup

The platform, capture conditions and run protocol of the evaluation, in one
half-column table.

Added 2026-08-21 when Section 4.1 was compressed.  Before it, the same material
ran as two bold run-in blocks of prose, `Experimental platform.` and `Capture
environment and workloads.`, and 4.1 carried five consecutive run-in headings.
Recent SEIP practice does not split setup that finely -- Hawkeye (ICSE-SEIP'24)
gives its platform two sentences under one `Experiment Platform.` heading, and
XTrace (ICSE-SEIP'26) has no setup subsection at all -- so the table absorbs the
enumerable settings and 4.1 keeps two headings, `Controller configurations.` and
`Protocol and measurement.`

WHAT BELONGS HERE AND WHAT DOES NOT.  A row is a setting with a value.  Anything
that is a procedure stays in the `Protocol and measurement.` prose: how the
device reaches a starting overheat level, how memory pressure is induced, what
resets between runs, and what the recording path exports.  Do not migrate those
into cells; they do not fit, and the prose is where a reviewer looks for them.

NO OPEN PLACEHOLDERS REMAIN.  The OS and camera-software rows were filled on
2026-08-21 as Android 17 (API level 37) and camera software 17.0.00.55 of July
2026.  The overheat-level preparation, the last outstanding
authored fact, was answered on 2026-08-21 and is 4.1 prose rather than a row: a
run starts when the platform reports a transition to the target level, which is
the same ordinal signal the deployed guard reads.  An ambient temperature was
never recorded and the author confirmed on 2026-08-21 that the environment was
an ordinary office, so the row stays qualitative; do not invent a figure for it
and do not re-raise it.
  Also settled that day: runs reach their target level while the device is
heating in most cases, and while it is cooling in the rest, when a run at a
higher level was followed by one taken as the level came down.  No manuscript
text is needed for this.  It would matter only if the heating/cooling mix
differed systematically between arms, and every arm comes from the same 0803
campaign collected the same way; the table also claims only a STARTING level,
which is what was observed.

THE ROW LABEL IS `Camera software`, NOT `Camera application`.  The version is
the camera application's, but the controller integrates in the framework
component that owns the Draft worker, so a row labelled by the application would
imply the version pins the framework and vendor layers too.  If a separate
platform or framework build identifier can be printed, it earns its own row
rather than being folded into this one.

WHAT THE AUTHOR TRIMMED ON 2026-08-21, AND WHY IT STAYS TRIMMED.  Three
conditions were shortened out of the table: that no device cooling was applied,
that the phone stayed tethered to a host machine over USB for the whole run, and
that the ADB loop requests captures faster than a person can press the shutter.
Each was raised the same day and settled by the author.  The USB tether does not
warrant a row or a threats line.  The capture-cadence comparison is redundant
beside `with no inserted delay`, which already says the loop adds no pacing of
its own; the comparison was rhetoric, not a second fact.  Do not re-propose
either.  If a reviewer ever asks for the arrival cadence as a number, the
measured shot-to-shot interval is recoverable from the exported traces and needs
no new setting row.

THE 24MP REQUESTED-MODE CAVEAT MOVED TO THE 4.1 PROSE.  It was a caption
sentence until the caption was trimmed to `Experimental setup.` on 2026-08-21,
which left the fact stated nowhere; it is now the third sentence of 4.1.  It has
to survive somewhere, because a reader who takes the 24MP label at face value
misreads the condition: only the first one or two captures of a run are produced
at that resolution.

Why only two of the four resolution-by-memory combinations are reported is also
4.1 prose, not a table row, because it is an argument rather than a setting.
The reported pair is the least and the most demanding of the four; the other two
were collected and lie between them.

## tab_timeout_index

`tables/tab_timeout_index.tex` &middot; Live -- `2_4_static_safeguards.tex`

Earliest and median Capture Timeout indices within a 30-capture horizon.
The timeout-level column reports the range of overheat levels observed when
the first timeout occurred across the trials in each starting-level row.

Protocol: ten 30-capture continuous-capture trials per combination of
starting level, resolution, memory condition, and M/M+S configuration;
M was enabled and the deployed guard was bypassed in a validation build.

Severity shading follows the earliest first-timeout index: white = no timeout;
the single-hue ramp darkens as the first failure moves earlier.

Give the two Overheat headers enough width while preserving the table width.

Each colored cell reports earliest/median; shading follows the earliest index.

### Column map

Recorded from the column-spec labels that used to sit in the tabular preamble.

| Column spec | Column |
| --- | --- |
| `\providecolor{tmoS1}{RGB}{252,227,220}` | first failure at capture >= 20 |
| `\providecolor{tmoS2}{RGB}{239,160,140}` | 10--19 |
| `\providecolor{tmoS3}{RGB}{201,80,63}` | 6--9 (white text) |
| `\providecolor{tmoS4}{RGB}{143,36,32}` | <= 5 (white text) |

## fig_capture_pipeline

`figures/fig_capture_pipeline.tex` &middot; Live -- `2_3_draft_sequence.tex`

Logical Draft and deferred post-processing paths.
Included from 2_3_draft_sequence.tex; contains the full figure environment
(Figure~\ref{fig:draft-pipeline}).

This is a logical dataflow view, not an execution-timing diagram. The
Draft Sequence publishes an early capture result, while post-processing
is deferred until the camera application switches to the background.
If post-processing fails or is interrupted, the published Draft image is
retained as the recovery result instead of being replaced.

---- shutter event (camera glyph) ----

---- shared collection stage ----

---- fork into the two processing paths ----

---- Draft path (capture-critical) ----

Schematic Draft image.

---- user-visible result ----

---- final path ----

Schematic final image.

replacement happens when final post-processing completes

---- recovery fallback (post-processing fails or is interrupted) ----
On this outcome no final image is produced, so the already-published
Draft image is retained as the recovery result.

## fig_casestudy_12mp

`figures/fig_casestudy_12mp.tex` &middot; Live -- `_4_experiments.tex`, case study

Coordinated admission and pacing in a 12MP 30-capture run without external
memory pressure.
Table VI records the deployment rationale for the setting and a compact peer
audit showing that the mechanism-revealing trace is not the best-performing
run in its matched condition.

Reference band.  The shaded capture window is where an uncontrolled run of
this setting first times out: captures 8--12, the controller-off Timeout onset
of the 12MP normal Lv4 row of RQ1
(tables/tab_rq1_end_to_end_summary.tex, \ref{tab:rq1_controller_behavior}).
ONLY THE LOWER EDGE IS STILL PRINTED THERE.  Since 2026-08-11 that column
reports the earliest first-timeout capture alone, which is the 8; the
Kaplan-Meier median 12 that closes the band was dropped with its sub-column
and is archived in docs/rq-evidence.md (Part 3).  If the band is ever
redrawn, take 12 from that record, not from the table.
Two other tables report a related quantity for this setting and do not agree
with it, so cite RQ1 and not them when the prose names the window: Table I
(\ref{tab:timeout_index}, normal capture, 12MP, M+S, starting level 4) reads
10/17 from the Section 2 motivation campaign, and the RQ2 No-control row
reads 8/8.5 from the 0803 baseline workbook.
It replaces the four dashed event markers an earlier revision drew at
captures 5, 9, 21 and 23.  Those markers annotated transitions the panels
already show -- pacing activation is visible in the applied-delay bars and
both demotions in the execution strip -- while the band adds what no panel
carried: where an uncontrolled run of the same setting would already have
timed out.  Do not reinstate the event lines alongside it; the figure does
not have room for two sets of capture-axis annotation.

Rejected alternative: lifting the window out of the axes as a red |-|
bracket above the strip, which would have let red keep one meaning across
the figure.  It was drawn and dropped.  With no fill through the panels the
window stops relating to the curves -- the reader has to carry two capture
indices down four panels by eye -- and the bracket sits far from the only
tick labels, so the range is not even readable where it is drawn.  The band
is worth the colour split it forces below.
If the source cell is ever recomputed, update the two arguments of
\csTimeoutRange below to match it.

Uncontrolled first-timeout window, spanning the full height of every panel
so that a single glance carries it down the stack.

Red carries failure throughout the figure: this window and the deadline in
the bottom panel.  What keeps the two from reading as one mark is form, not
hue -- the window is a capture interval and fills, the deadline is a
threshold and is a line -- and the fact that only one red area is left, the
danger tint under the floor having been dropped (see the bottom panel).  Do
not restore that tint while this band is red; two red areas crossing at the
bottom left is exactly the collision that was removed.

Queue depth is an integer count, so it is drawn as a staircase rather
than as the interpolated series used for the two time-valued panels.

---- stage execution strip -------------------------------------

The band is named once, on the annotation line above the strip, in the
space the removed event labels used to occupy.  It is centred on the
band rather than set flush left, so it points at what it names, and it
is broken over two lines and lifted by the same 1pt as the legend on
the right so the two blocks sit on one line.  "window" is load-bearing:
the band is a range over captures, not a single failure.

---- queue depth -----------------------------------------------
Grouped with the execution strip above it: both are per-capture
discrete quantities, which leaves the three time-valued panels
together below.

---- applied pacing delay --------------------------------------
The labelled ceiling is 1000 ms, not the 1500 an earlier revision used.
The largest delay this run applies is 696 ms at capture 12, so the top
third of the taller panel was empty and nothing is clipped here.  The
height is cut in the same proportion as the range, which keeps the
ms-per-length scale of the bars at exactly what it was -- 5000 ms per
\columnwidth -- and takes 0.08\columnwidth off the figure.  Do not lower
the ceiling without restoring the height, or the bars will read as
taller delays than the panels around them imply.
ymax is 1100 rather than a flush 1000: at 1000 the top tick label sits
on the axis frame, and with the 3.5pt group separation it ran into the
0 of the queue-depth panel above.  The 100 ms of headroom drops it about
5pt and the two labels clear each other.
This case-study panel is intentionally scaled to its selected run; the
all-run RQ4 summary reports delay distributions numerically instead.

---- real Draft backlog ----------------------------------------

---- deadline margin -------------------------------------------

ymin is -11, not the -6 that fitted when the deadline label sat at the
right end of the floor line inside the plot.  The label now hangs
under the 0% tick and needs about 9pt of clearance there; at -6 the
axis frame cut through it.  Nothing is plotted below zero in this run,
so the added strip costs only a 7% vertical compression of the curve.

The tinted band below zero is gone.  The margin never enters it in this
run -- its minimum is 2.1% -- so it shaded an empty strip, and it was
the red area that the reference window ran through.  The floor line and
its label carry the deadline on their own.

Under the 0% tick rather than at the right end of the floor line.  The
strip below zero is empty in this run, so the label reads as a caption
of the tick it hangs from, and it no longer sits where the margin curve
climbs back out at capture 30.

---- stage legend beside the timeout label -----------------------
Share the annotation line above the execution strip: the timeout label
identifies the reference window on the left, while this two-row legend is
right-aligned to the strip frame.  Both legend entries use "stage" so the
execution and admission-skip states remain grammatically parallel.

inner ysep is cut from the \tiny default (about 1.7pt a side) so the two
rows close up to the line spacing of the two-line band label opposite;
with the default the legend stood a third taller than that label and the
two blocks no longer read as one annotation line.

south east, not east: an east anchor sits at the middle of a two-row
matrix, which dropped the second row through the strip frame and on to
the markers.  Anchoring on the bottom edge keeps both rows above it and
puts the block on the same baseline as the band label opposite, which
is why the yshift here has to track the label's.
The yshift is 2pt under the label's because the two blocks measure their
bottoms differently: the label's south anchor lands on a line with no
descenders, the matrix's on a row that has them, so equal yshifts left
the legend sitting visibly higher.

## fig_parallel_capture_overlap

`figures/fig_parallel_capture_overlap.tex` &middot; Live -- `2_2_parallel_capture.tex`

Draft Sequences piling up under parallel capture (three shots).
Included from 2_2_parallel_capture.tex (Figure~\ref{fig:overlap}).
Requires TikZ with the `patterns', `decorations.pathreplacing', and
`positioning' libraries, plus pifont for the check mark.

The figure intentionally abstracts away internal Draft workloads. Each
capture first collects frames and metadata. These collection periods can
overlap, whereas Draft Sequences run one at a time in capture order. The
resulting worker wait grows across consecutive captures until capture i+2 misses
its deadline despite having the same Draft Sequence duration.

---------- legend ----------

---------- capture i ----------

HAL releases the next request before capture i's collection and Draft
work have completed.

---------- capture i+1 ----------

---------- capture i+2 ----------

The same Draft duration now extends beyond capture i+2's deadline.

---------- ordered Draft handoffs ----------

---------- budget braces for the failing capture ----------

---------- time axis ----------

## fig_rq3_unsafe_spike_anatomy

`figures/fig_rq3_unsafe_spike_anatomy.tex` &middot; Live -- `_4_experiments.tex`, RQ3

RQ3: what changed at each of the five unsafe model admits, as ratios to
the capture immediately before it, and which shipped safeguard would have
prevented each overrun.

The decisions are the unsafe-admit cell of the audit block in
Table~\ref{tab:rq3_admission_audit}; the measured values behind these ratios
are recorded in this header rather than in a companion table.

Bars are anchored at 1.0, so a bar to the right is an increase over the
preceding capture and a bar to the left a decrease.  The x coordinates below
are therefore ratio - 1, and the tick labels restate them as ratios.

  id  latency  CPU time  busy cores   prevented by
  M1     2.32      1.41        0.60   watchdog
  M2     1.95      1.15        0.59   watchdog
  M3     1.14      1.23        1.08   later single-frame skip
  S1     1.60      1.24        0.76   earlier multi-frame skip (+ watchdog)
  S2     1.42      1.37        0.96   earlier multi-frame skip

The right-hand column is the interpretation layer, kept outside the plot box
so the measured ratios stay the measured ratios:

  watchdog   the per-node watchdog, suppressed by the audit build so that admitted
     work could be measured to completion, would have cut the decision node at
     its own budget:
       M1 1460/1202 (+258)   M2 1648/889 (+759)
       S1  389/ 371 ( +18)
  model skips  the model's remaining skips in the same capture leave the
     decision inside its budget.  Work rejected AFTER the decision leaves the
     cost; a node rejected BEFORE it frees budget by shortening the path to
     it.  Both directions occur, so neither "prior" nor "later" alone would
     label these rows correctly -- and a Multi-frame decision is nodeOrder 1,
     so nothing can precede it at all:
       id  before(budget+)  after(cost-)   C_model/B_model
       M3        0               22          833 /  844
       S1      460               18          961 / 1435
       S2      330                0          713 /  983

Every row carries at least one, so none of the five would have reached a
shipped build as a Capture Timeout.  M1-M2 are covered only by the watchdog:
they are over budget even on their own decision set, which is why they are the
two genuine model errors.

The row pitch is set by the value labels, not the bars: three labels per row
need about 6.5pt of vertical separation at \tiny, so the bar shift, the bar
width that makes the group's bars touch, and the y unit all follow from that.
A transposed, vertical-bar version was tried and dropped: three labels per
group then sit side by side and need a full-width float to clear each other,
which costs more page area than this layout.

The relation is multiplicative, latency = CPU time / busy cores, so the bars
must not be read as adding up on this linear scale.  Regenerate the values
with data/rq2_spike_anatomy.mjs in the ML repository.

Safeguard verdict, drawn outside the plot box so it never competes with a
value label for x range. The tick reads as "this did not ship as a timeout"
on its own; the letter says which safeguard prevented it.

Value labels: one macro per side so the anchor and its matching nudge stay
literal. A conditional inside a TikZ key value is not worth the fragility.
#1 vertical offset matching the bar shift, #2 bar end in plot
coordinates, #3 row, #4 printed ratio.

Bar width equals the bar shift spacing below, so the three bars of a
group touch. Both are 6.5pt because that is the least vertical room the
three value labels need at \tiny; anything narrower would either
reintroduce a gap or collide the labels.

Fixing the y unit sets the row pitch directly. A group is 19.5pt tall,
so 25pt leaves 5.5pt between groups - enough that touching bars read as
one group rather than the rows running together.

scale only axis makes width the plot box rather than the box plus its
labels, so the bars get the column's full width instead of sharing it
with the row names.

Plotted values are ratio - 1 so that the bars grow out of 1.0; the tick
labels put them back into ratio units.  The limits leave room for a
value label past either end of the longest bar and for the key.

The key sits inside the plot: the single-frame band is empty right of
about 0.8, which is where its three rows fit without covering a bar or
a value label.

A bar plot's default legend image stacks two swatches; one is enough.

1.0: no change from the preceding capture.  Bars leave this line, so it is
drawn over the grid rather than as one more gridline.

Multi-frame / single-frame boundary.

Explicit shifts: pgfplots would otherwise put the first plot at the bottom
of each group, reversing the legend's reading order.

Value labels sit past the end of their bar, so they fall right of an
increase and left of a decrease and never cover the bar.

Safeguard column, outside the plot box. The header sits on the box edge so
it reads as this column's heading rather than as a floating note, and it
states the outcome so the panel carries the conclusion without the caption.

## Deleted exhibits

Removed from the repository, with the reason. Do not recreate them; if the need
returns, recover the file from git history rather than redrawing it.

### fig_controller_overview, fig_controller_timeline (deleted 2026-08-20)

`figures/fig_controller_overview.tex` (67 lines) and
`figures/fig_controller_timeline.tex` (121 lines) were two TikZ attempts at the
Section 3.1 controller figure. Both were superseded by the PowerPoint-built
`figures/fig_controller_interaction.pdf`, which 3.1 has shipped since; neither
was `\input` by any section, and neither defined a `\label`, so removing them
changed no cross-reference. A third copy, `fig_controller_timeline.tex` at the
repository root, was an earlier revision of the same drawing that still carried
its rationale as an inline comment block and still said `optional nodes`; the
`node` ban and the notes-live-in-`docs/` rule both post-date it.

They also would not have been safe to reuse as drawn. The timeline figure
labelled the queue `Draft tasks`, which is the unit `Draft Sequence` names, and
the root copy's comment repeated it three more times.

The live Figure 2 pipeline is untouched and is not related to these files:
`scripts/build_controller_figure_pptx.js` draws
`figures/fig_controller_interaction.pptx`, `scripts/build_controller_figure.ps1`
exports the PDF from it, and both consume `figures/controller_icons/`, trimmed
by `scripts/trim_icons.ps1`.
