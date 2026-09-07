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
| [`tab_rq1_cadence_diagnostic`](#tab_rq1_cadence_diagnostic) | `tables/` | Not input by any section |
| [`tab_rq1_end_to_end_summary`](#tab_rq1_end_to_end_summary) | `tables/` | Live -- `_4_experiments.tex`, RQ1 |
| [`tab_rq2_ablation`](#tab_rq2_ablation) | `tables/` | Live -- `_4_experiments.tex`, RQ2 |
| [`tab_rq3_admission_summary`](#tab_rq3_admission_summary) | `tables/` | Live -- `_4_experiments.tex`, RQ3 |
| [`tab_rq4_pacing_sizing`](#tab_rq4_pacing_sizing) | `tables/` | Live -- `_4_experiments.tex`, RQ4 |
| [`tab_rq4_pacing_selectivity`](#tab_rq4_pacing_selectivity) | `tables/` | Superseded 2026-08-21 by `tab_rq4_pacing_sizing`; kept on disk |
| [`tab_rq4_pacing_summary`](#tab_rq4_pacing_summary) | `tables/` | Superseded 2026-08-13 by `tab_rq4_pacing_selectivity`; kept on disk |
| [`tab_setup`](#tab_setup) | `tables/` | Live -- `4_1_setup.tex`, evaluation setup |
| [`tab_timeout_index`](#tab_timeout_index) | `tables/` | Live -- `2_4_static_safeguards.tex` |
| [`alg_admission`](#alg_admission) | `figures/` | Live -- `3_3_admission.tex` |
| [`fig_capture_pipeline`](#fig_capture_pipeline) | `figures/` | Live -- `2_3_draft_sequence.tex` |
| [`fig_casestudy_12mp`](#fig_casestudy_12mp) | `figures/` | Live -- `_4_experiments.tex`, case study |
| [`fig_casestudy_s26_12mp`](#fig_casestudy_s26_12mp) | `figures/` | Candidate -- not input by any section |
| [`fig_parallel_capture_overlap`](#fig_parallel_capture_overlap) | `figures/` | Live -- `2_2_parallel_capture.tex` |
| [`fig_rq3_unsafe_spike_anatomy`](#fig_rq3_unsafe_spike_anatomy) | `figures/` | Live -- `_4_experiments.tex`, RQ3 |

## tab_casestudy_selection

`tables/tab_casestudy_selection.tex` &middot; Live -- `_4_experiments.tex`, case study

Case study: deployment rationale and a compact peer audit for the 12MP trace
without external memory pressure.

Measurement source: SM-S948U_metrics_12MP_normal_0906.xlsx, supplied outside
the repository on 2026-09-06 (SHA-256
1a8d1da73367446272d51e87896ec588e9725e8b9296b71f5df6224fc4bce83e).
The figure traces come from CaseStudyTrace, and the peer audit comes from
RQ3Summary.  The table's current `This run` display values were supplied by the
author on 2026-09-07 and are recorded in
`data/case_study/12mp_normal_author_supplied_this_run.csv`.  The workbook records 56 sessions, of
which 55 are complete 30-capture runs.  No analyzed session records Capture
Timeout or a watchdog failure.
Deployment fact supplied by the author: 12MP is the default resolution.

The peer set holds the plotted condition fixed: MP12, no external memory
pressure, starting overheat level 4, complete 30-capture execution, and no
recorded timeout or watchdog failure.  It contains run IDs 4, 12, 17, 28, 33,
34, 42, 43, 49, and 52 (n = 10).

The author-supplied `This run` values are 26.7% M execution, 73.3% S execution,
55.2% pacing activation, 5.21 s cumulative delay, and 5.2% Slack P5.  These
values are held fixed while the peer columns are recomputed from the workbook;
no workbook run identifier is inferred from this display-only input.

The comparison header uses bottom-aligned cells so its one- and two-line labels
share a common baseline above the midrule.  Header alignment follows the body:
metric labels are left-aligned, scalar values are right-aligned, and the range
and comparison columns are centered.

The earlier mechanism-coverage filter does not apply to this workbook.  No
run has an M-stage skip followed later by an S-stage skip; at level 4, S is
executed on all 30 captures in every peer.

Peer figures: data/case_study/12mp_normal_peer_comparison.csv, exported from
the same workbook and peer population.  Peer median / [min, max], with the
preferred direction in brackets, in table row order:
  M executed               45.0 / [26.7, 100.0] %      [higher]
  S executed              100.0 / [100.0, 100.0] %     [higher]
  pacing activated         31.0 / [13.8, 69.0] %       [lower]
  cumulative delay       4173.0 / [3510, 11702] ms     [lower]
  deadline margin P5      659.0 / [324.7, 1102.4] ms   [higher]
The two cost rows read frequency then magnitude: how often pacing intervened,
then what those interventions summed to.
"Pacing activated" is the RQ1 name for this quantity and replaces the
earlier "paced transitions": both are RQ3Summary.pacedPercent, the share of a
run's 29 transitions carrying a positive applied delay.  The Slack row divides
the workbook's millisecond values by the timeout constant and prints only the
resulting percentages in the manuscript.

The exported field burstSpanMs remains a sixth peer metric in the CSV and is
not a table row.  Its selected / median / [min, max] values are 22367 /
22554.5 / [22173, 28837] ms.  It stays out because it overlaps cumulative
applied delay and therefore does not add an independent responsiveness cost.

The author-supplied run is below the peer median for both stage-execution
metrics and slack, and above it for both pacing costs.  All five verdicts
therefore read `worse` under the direction printed beside each metric.

The deadline margin row is reported only as a percentage of the timeout.  The
workbook converts the peer median and range to 9.4 / [4.6, 15.7]%; the 5.2%
`This run` value is author-supplied.  The timeout constant must not appear in
manuscript text.

Block (b) remains a table so the run's placement is directly checkable.  The
metric names carry the preferred direction and the last column states the
corresponding verdict.  All five rows currently read "worse."  The [min, max]
column shows the peer spread without assigning direction; direction belongs to
the metric.
Delay and activation read better lower, while margin and stage execution read
better higher.

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
Block (b) uses the author-supplied fixed widths: 0.376 for the metric, 0.150
for the peer range, and 0.075 for the verdict.  The cumulative-delay label stays
on one source line.  Preserve this format during data-only refreshes, even if a
standalone render chooses to wrap a long cell.

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

## tab_rq1_cadence_diagnostic

`tables/tab_rq1_cadence_diagnostic.tex` &middot; Not input by any section

Compact cross-device diagnostic for the 24MP-request memory-pressure
collection. The upper block contrasts the capture interval after subtracting
the recorded controller-added pacing delay with whole Draft Sequence duration
at low and high starting overheat levels, and reports the ratio between those
two base metrics. The lower block decomposes the deadline usage of S26
captures that timed out.

External working-collection sources:

- `SM-S942B_metrics_24MP_memory_0829_original.xlsx`
- `48U_metrics_24MP_memory_0803_1.xlsx`
- `48U_metrics_24MP_memory_0803_2.xlsx`

The source population is the three named original workbooks, not the balanced
RQ1 population currently printed in `tab_rq1_end_to_end_summary`. Runs are
selected by `RQ1Runs.includedForRq1`, namespaced by workbook and run ID, and
grouped by `startingOverheatLevel`: Lv1--2 contains 14 S26 and 21 S26 Ultra
runs; Lv5--6 contains 24 and 20, respectively. Timeout runs contribute their
factual observed prefix.

Each P50 pools event rows rather than averaging run-level medians. Capture
interval uses `shotToShotWithoutRecordedPacingMs`, exported as
`max(shotToShotTimeMs - transitionDelayMs, 0)`. This is an arithmetic
recorded-delay subtraction, not a counterfactual trace replayed with pacing
disabled; policy divergence, subsequent queue state, and thermal trajectory
are not replayed. The zero floor occurs more often for S26 and can bias its
capture interval downward.

Draft Sequence P50 uses `draftSequenceDurationMs` only for
captures on which both `bokehExecuted` and `filterExecuted` are true. The
field is the wall-clock interval from Draft start to completion: it includes
the executed \(M\) and \(S\) stages, mandatory encoding and saving, and
between-stage overhead. It is not the arithmetic sum of the two optional-stage
durations. Conditioning on both stages avoids making the high-level cells look
artificially short merely because admission skipped optional stages.

The upper block's `Sequence/interval ratio` divides the two unrounded pooled
P50s shown in the same row. It is a ratio of marginal medians, not the median
of per-capture ratios, a paired capture measure, or a worker-utilization
estimate.

The lower block is timeout-conditional. It selects the 11 `CaseStudyTrace`
rows from included S26 runs at `startingOverheatLevel` 1, 2, 5, or 6 for which
`captureTimedOut` is true; this population originates from
`SM-S942B_metrics_24MP_memory_0829_original.xlsx`. Pre-Draft elapsed time is
`draftStartUptimeMs - (timeoutDeadlineUptimeMs - captureTimeoutMs)`;
deadline consumption substitutes `draftEndUptimeMs` into the same expression,
and margin is `timeoutMarginMs`. Because these are marginal P50s, the median
Pre-Draft elapsed time and median Draft Sequence duration need not sum to the
median deadline consumption.

The source workbooks describe a 24MP-request condition, not an all-24MP
execution population: Lv5--6 rows are 4000x3000 on both devices, and most
Lv1--2 rows have also fallen back to that output size.

Unrounded pooled values, in printed row order, are:

```text
Lv1--2  S26 Ultra  capture interval 506.0  Draft Sequence 678.0   ratio 1.34
Lv1--2  S26        capture interval 288.5  Draft Sequence 662.0   ratio 2.29
Lv5--6  S26 Ultra  capture interval 695.0  Draft Sequence 1341.0  ratio 1.93
Lv5--6  S26        capture interval 432.0  Draft Sequence 1087.0  ratio 2.52
S26 timeout (n=11) pre-Draft elapsed 6534.0  Draft Sequence 659.0
S26 timeout (n=11) deadline consumption 7114.0  margin -114.0
```

The 2026-08-31 two-metric revision removed raw measured S2S and executed \(M\)
duration so the exhibit directly compares device cadence before added pacing
with whole-sequence worker occupancy. Their former values, in row order, were
`551/407/776/451` ms and `253.5/201.5/539/350` ms, respectively. Restore them
from `shotToShotTimeMs` and positive `bokehActualDurationMs` on captures where
`bokehExecuted` is true.

The table rounds timing values to the nearest millisecond and the derived
ratios to two decimal places; ratios are computed from the corresponding
unrounded P50s. The pacing exclusion is defined in this entry rather than the
caption so the caption stays on one line.
`Draft Sequence duration` is the whole wall-clock interval described above,
not the literal sum of \(M\) and \(S\).
The first stub is `Starting overheat level`, matching the RQ1 terminology.
The table has an outer border, a vertical rule between every column, and
single horizontal rules throughout so that the header and body form one
continuous grid. The timeout separator spans the same grid as the upper block.
The five-column tabular uses `\fittabcolsep` with divisor 10
to fit exactly to `\columnwidth`.

## tab_rq1_end_to_end_summary

`tables/tab_rq1_end_to_end_summary.tex` &middot; Live -- `_4_experiments.tex`, RQ1

RQ1: Baseline failure reference, full-controller Draft availability, and
pacing cost.
This is the RQ1 table; the per-loop ablation is now its own research
question, RQ2, in tables/tab_rq2_ablation.tex.

2026-09-07 MEASUREMENT-IMAGE UPDATE.  The eight columns under `Draft stages
executed` and `Pacing cost` were refreshed, in Lv0--Lv6 order, from these four
external measurement renders:
  - SM-S942B_metrics_12MP_normal_0906.png
  - SM-S942B_metrics_24MP_memory_0829.png
  - SM-S948U_metrics_12MP_normal_0906.png
  - SM-S948U_metrics_24MP_memory_0906.png

The refreshed M, S, and Activated cells are per-run counts, and delay P50
pools positive transition delays, matching the table's existing count and
delay conventions.  For these eight columns, this revision supersedes the
2026-08-31 working-collection provenance below.

2026-09-07 SURVIVAL-COLUMN FORMAT UPDATE.  The user-supplied table base
replaces the Baseline and Deadline safety data cells with the common
`Survived runs (timeout onset)` form.  A cell `x/10 (k)` reports the number of
runs that survived the 30-capture horizon and the earliest timeout onset in
parentheses; `10/10 (--)` means that all ten survived and no onset was
observed.  Fully survived cells are bold.  The fixed-width `\rqsurvived`
wrapper right-aligns these values while the two `c` columns keep both headers
centered.  Device, Condition, Starting overheat level, and N follow the
supplied base; the measurement-image update above remains authoritative for
M, S, Activated, and delay P50.

2026-08-31 S26 EXTENSION.  The S26 block is reconstructed from the external
working collection:
  - SM-S942B_metrics_12MP_normal_0829.xlsx
  - SM-S942B_metrics_12MP_normal_baseline_0829.xlsx
  - SM-S942B_metrics_24MP_memory_baseline_0829.md/.png

The 12MP baseline onsets come from the baseline workbook.  The original 24MP
baseline workbook was replaced, so its earliest observed timeout indices are
recovered from the preserved notes and rendering:
  - 12MP Lv0--Lv6: --, --, 22, 15, 9, 9, 9.
  - 24MP Lv0--Lv6: 23, 21, 19, 9, 6, 3, 6.

S26 full-controller values use every run marked `includedForRq1` and are
recomputed from `RQ1Runs` and `RQ3Pacing`.  M, S, and Activated remain per-run
counts; captures not reached after an observed timeout add no executed stage or
paced transition.  Delay P50 pools positive observed transition delays.

S26 run counts are therefore not balanced: 12MP has N=5/5/5/10/11/10/10,
and 24MP has N=5/7/7/10/10/11/10 for Lv0--Lv6.  The 24MP block retains nine
observed Capture Timeout runs (Lv1 two, Lv2 four, Lv5 one, Lv6 two) rather
than treating them as invalid measurements.

All pre-2026-08-31 source, balancing, and fixed-denominator notes below apply
to the S26 Ultra block unless they explicitly name S26.

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
  - Timeout onset no longer splits Earliest / KM-median.  The 2026-09-07
    row format pairs a survived-run count with the earliest first-timeout
    capture in parentheses for both Baseline and Deadline safety; it does not
    restore the Kaplan--Meier sub-column.  The parenthesized onset remains a
    minimum over ten trials rather than a typical value.  An arithmetic mean
    remains unavailable because the Section 2 motivation campaign's
    per-trial indices are not in this repository and no-timeout runs are
    right-censored.
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

The header remains four rows.  Baseline and Deadline safety use the same
two-line `Survived runs (timeout onset)` label and retain the -0.4ex multirow
adjustment.  Their data columns use `c` alignment for the headers and the
fixed-width, right-aligned `\rqsurvived` wrapper for values.  The width is
measured from the bold `10/10 (--)` form so the paired survival and onset
values align without widening one condition block independently.

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

RQ2 isolates the contribution of admission and pacing at starting overheat
level 4.  Each scenario is one full-width panel with a shared metric header;
the four configurations remain an unrolled admission-by-pacing design.

2026-09-07 PACING-ONLY/FULL REFRESH.  Only the `Pacing only` and `Full` rows
were refreshed.  `No control` and `Admission only` retain their previous
sources and values.  The refreshed sources, supplied outside this repository,
are:

  - S26 Ultra, 12MP normal:
    `SM-S948U_metrics_12MP_normal_pacing_only_0906.xlsx` for Pacing only and
    `SM-S948U_metrics_12MP_normal_0906.xlsx` for Full.
  - S26 Ultra, 24MP memory pressure:
    `SM-S948U_metrics_24MP_only_pacing_only_0906.xlsx` for Pacing only and
    `SM-S948U_metrics_24MP_memory_0906.xlsx` for Full.
  - S26, 12MP normal:
    `SM-S942B_metrics_12MP_normal_pacing_only_0906.xlsx` for Pacing only and
    `SM-S942B_metrics_12MP_normal_0906.xlsx` for Full.

Source SHA-256 values, in the same order within each device/condition pair,
are:

  - S26 Ultra 12MP: `6370682e810b2373571953e7683a96303c644641a88b8711f8e47ce8460dd78d`,
    `1a8d1da73367446272d51e87896ec588e9725e8b9296b71f5df6224fc4bce83e`.
  - S26 Ultra 24MP: `3022ac64e40c3954354b589c4a1a8e7599157846bad48e3a5c67e80adf34c27d`,
    `3b79b5fcd7484625233252b0cbc203244c0f8468828689bc7e1e2d03a250e3be`.
  - S26 12MP: `eeb5215aca0f46218f714a6c34d20d8769ee1f1da6248cd970e1028b4abe2228`,
    `72b4140894e433686f7b821cd8be4c3db019cff9b4c1ba784a0c1ed0371037e`.

Population and aggregation rules:

  - Select `RQ1Runs.includedForRq1 = true` at `startingOverheatLevel = 4`,
    and join `RQ3Pacing` by `runId`.
  - Cap every run at capture 30.  The earlier 29-capture carry-forward rule is
    not exercised by any selected Full run in this refresh.
  - Pacing-only Capture Timeout runs remain in the population because timeout
    is the measured outcome of that arm.  The timeout capture and all
    unreached requested captures contribute zero to Captures, M, and S.
  - Full runs labelled Capture Timeout are invalid measurements and are
    excluded.  The S26 Ultra 24MP Full population retains one 30-capture
    watchdog run; its missing stage observations are scored as skipped stages,
    not printed with a placeholder and not used to discard the run.
  - Captures, M, and S use `30 x N` requested captures as their denominator.
    M and S additionally require an on-time capture and literal
    `bokehExecuted` / `filterExecuted` execution, respectively.
  - Activated is positive `transitionDelayMs` divided by all nonblank observed
    transition delays.  The first capture has no incoming transition.  `d P50`
    is the inclusive median of the pooled positive transition delays.
  - All included Lv4 runs are used after the Full timeout exclusion; this
    refresh does not force each cell to N=10.  Consequently, denominators are
    300, 360, 330, or 420 as shown by the audit counts below.

Numerical audit behind the refreshed cells:

| Panel | Configuration | N | Survived | Reached / on time | M / S | Positive / eligible transitions | d P50 (ms) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S26 Ultra 12MP | Pacing only | 10 | 0/10 | 143 / 133 | 133 / 133 | 68 / 133 | 242.5 |
| S26 Ultra 12MP | Full | 10 | 10/10 | 300 / 300 | 174 / 300 | 110 / 290 | 437 |
| S26 Ultra 24MP | Pacing only | 12 | 0/12 | 113 / 101 | 101 / 101 | 59 / 101 | 483 |
| S26 Ultra 24MP | Full | 11 | 11/11 | 330 / 330 | 147 / 254 | 117 / 319 | 400 |
| S26 12MP | Pacing only | 14 | 1/14 | 271 / 258 | 258 / 258 | 115 / 257 | 387 |
| S26 12MP | Full | 10 | 10/10 | 300 / 300 | 168 / 224 | 154 / 290 | 297 |

The repeated Captures/M/S rates in Pacing only are intentional: with
admission disabled, every capture that completes before the deadline executes
both optional stages.  In the S26 12MP panel, Pacing only therefore executes M
on 61.4% of requested captures, slightly above Full's 56.0%, but completes
only 61.4% of requested captures versus Full's 100.0%.  Keep the adjacent
Captures column when discussing this inversion.

The panel headers combine device, capture condition, and level so the metric
header appears only once.  The 24MP condition remains a requested-mode label;
it is not regrouped by the per-capture size bucket recorded after fallback.

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

RQ3 reports only the always-admit admission-model audit on one device.
The former Controller-enforced block remains documented below as historical evidence.
Each capture contributes at most one selected decision per optional-work
group: Multi-frame = Bokeh; Single-frame = Filter.

---
2026-09-07 SCOPE NARROWED.  The live table now prints only the Always-admit
model audit.  The Controller-enforced block, including Model admit, Unsafe,
Model skip, and Shortfall, was removed from the exhibit at user direction; its
values and provenance remain below and in docs/rq-evidence.md as historical
evidence.  The current table has five columns: Group, Feasible work
Admitted/Skipped, and Unsafe work Admitted/Skipped.  Every data and Overall
cell prints its within-class percentage with the decision count in parentheses;
the Feasible pair and Unsafe pair each sum to 100%.  The Unsafe-work Admitted
values remain bold because Figure~\ref{fig:rq3_unsafe_spike_anatomy} analyzes them.
The four data columns use centered column placement, while every value is
right-aligned inside one shared-width `\makebox`, following the alignment pattern
used for RQ1's Survived-runs cells.
The final audit column retains one trailing `\tabcolsep`; do not replace it with
an empty trailing `@{}`, which makes its values appear flush against the rule end.
The RQ3 prose now states only the 3,746-decision audit population.
---
HISTORICAL MERGED-TABLE DESIGN, superseded by the scope reduction above.
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

RQ4: the delay engages selectively as reservation consumes more of the
decision-time TTL, and stays a small share of the backlog it drains.

Adopted as the RQ4 exhibit of record on 2026-08-21, succeeding
`tab_rq4_pacing_selectivity`, whose entry keeps the reasoning for the earlier
swap away from `tab_rq4_pacing_summary`.  That reasoning still applies: the
summary table measured d against d*, which is a decomposition of prediction
error at a fixed coefficient rather than a sizing report.

FORMAT REFRESHED 2026-09-07 from the user-supplied table form.  The caption is
"RQ4 Pacing-Delay Sizing under Backlog Pressure" and the label remains
tab:rq4_pacing_sizing.  The three-row header names the device, states that the
four activation columns are reservation-to-TTL bands, and keeps the two sizing
diagnostics ($d/B$ P50 and backlog overlap) separate.  The final band is printed
as reservation at least 100% of TTL; it does not identify an actual Capture
Timeout.  4_5_rq4_pacing.tex is the only \ref site.

The four bands partition transitions by

    rho_i = R_i / T_i, where R_i = B_i + G_i + 2C_i.

Here $B_i$ and $C_i$ are measured from the completed trace and $G_i$ is the
recorded online backlog-growth term.  The workbook exposes no realized
counterpart for $G_i$, so $R_i$ is deliberately called a trace-conditioned
reservation rather than actual consumed time.  $T_i$ is the TTL at the pacing
decision, and every analyzed transition has $T_i>0$.  The half-open bands are
$\rho_i<60\%$, $60\%\leq\rho_i<80\%$,
$80\%\leq\rho_i<100\%$, and $\rho_i\geq100\%$.

Current source workbooks (2026-09-07 refresh):

- `SM-S948U_metrics_12MP_normal_0906.xlsx` (SHA-256
  `1a8d1da73367446272d51e87896ec588e9725e8b9296b71f5df6224fc4bce83e`);
- `SM-S948U_metrics_24MP_memory_0906.xlsx` (SHA-256
  `3b79b5fcd7484625233252b0cbc203244c0f8468828689bc7e1e2d03a250e3be`).

The workbooks are external measurement sources and are not copied into this
repository.  The derived cells and their audit counts are recorded in
`data/rq3/policy/s26_ultra_0906_summary.csv`:

  activationPercent band reservation_under_60_ttl / reservation_60_80_ttl /
    reservation_80_100_ttl / reservation_at_least_100_ttl
                          the four reservation-to-TTL band cells; the CSV carries
                          the percentage in value and the band size in denominator,
                          while adjacent activationCount rows carry the numerators
  delayOverBacklogPercent P50   the d/B column; its denominator is
                          pacedTransitions, retained in the audit CSV
  backlogDrainingDelaySharePercent   the Overlap backlog column

The same CSV now also records the run-level delay-share percentiles,
never-paced-run counts, admission-aware envelope counts, and thin-margin
summary quoted in `4_5_rq4_pacing.tex`.  The two sub-1% observations are kept
row by row in `data/rq3/estimator/s26_ultra_0906_thin_margin_tail.csv`.

Population.  The S26 Ultra 12MP-normal Full workbook contains 56 run
summaries.  Run 11 is incomplete at 29 shots and is excluded, leaving 1,414
analyzed transitions over 55 complete runs, of which 463 were paced.  The
24MP-memory Full workbook contains 68 run summaries; nine incomplete runs are
excluded, leaving 1,553 analyzed transitions over 59 complete runs, of which
578 were paced.  For 12MP and 24MP respectively, the four band denominators
sum to 1,414 and 1,553, and their paced counts sum to 463 and 578.  The
recorded delay agrees between `RQ3Pacing.transitionDelayMs` and
`PacingReplay.beforeAppliedDelayMs` on every analyzed transition in both
conditions.

THE BANDS ARE TRACE-CONDITIONED, NOT TIMEOUT OUTCOMES.  They replace the
controller's backlog and Draft-duration estimates with measured $B_i$ and $C_i$
while retaining its recorded $G_i$, because the workbook exposes no realized
backlog-growth counterpart.  Their sum $R_i$ is a reservation, not actual
consumed time; $\rho_i=R_i/T_i$ normalizes it by the TTL available at that
decision.  Every band uses this same ratio, half-open [lo, hi), with the last
band open at its upper edge.
Activation against the controller's own online score is true by construction
and must not be reported as a result.  This distinction is encoded in
scripts/rq3_calibration_metrics.py and scripts/rq3_pacing_summary_metrics.py.

2026-09-07 REAGGREGATION.  Against the source hashes above, the 12MP row is
1.3% (7/551), 18.1% (62/343), 57.0% (151/265), 95.3% (243/255), 12.5% over
463 paced transitions, and 99.1% overlap.  The 24MP row is 9.6% (55/572),
32.8% (144/439), 62.2% (240/386), 89.1% (139/156), 13.2% over 578 paced
transitions, and 96.9% overlap.  Each displayed percentage is rounded to one
decimal after computing from the printed counts.
Every denominator is valid: decision-time TTL is positive on all analyzed
transitions, ranging from 3,792 to 7,000 ms at 12MP and from 2,426 to 7,000 ms
at 24MP.

2026-09-07 LAYOUT FOLLOW-UP.  A thin `\cmidrule(lr){1-7}` separates the two
condition rows.  The repeated `(N paced)` annotations were removed from the
$d/B$ and overlap cells; their 463 and 578 denominators remain in the audit CSV.
Vertical rules separate every data column.  The `\multicolumn` header formats
repeat the relevant right-hand rules so the separators continue through all
three header rows instead of disappearing inside the spanning cells.
The former `Overlap backlog` prose header is printed as its pooled definition,
$\sum_i\min(d_i,B_i)/\sum_i d_i$, to distinguish this ratio of sums from the
per-transition $d/B$ P50 beside it.

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

2026-08-31 S26 EXTENSION.  Device and SoC use one value column per device:
Galaxy S26 Ultra / Snapdragon 8 Elite Gen 5 for Galaxy and Galaxy S26 /
Exynos 2600.  RAM is the common 12 GB value, and it and all remaining common
configuration rows span both device columns.

The compact hardware block uses a 0.36/0.24 device-column split and bold device
names.  The longer S26 Ultra SoC wraps deliberately after `5`, rather than being
squeezed against the S26 value.  Use no vertical or per-row rules: one midrule
after SoC separates the device-specific hardware from RAM and the other common
platform and protocol settings.

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

Earliest Capture Timeout indices within a 30-capture horizon. The table lists
levels 0--6 directly and uses only a midrule at the production guard's level-4
cutoff. The former explanatory guard-decision rows were removed so that the
surrounding Section 2.4 prose, rather than the exhibit, owns their interpretation.

Protocol: ten 30-capture continuous-capture trials per combination of
starting level, resolution, memory condition, and M/M+S configuration;
M was enabled and the deployed guard was bypassed in a validation build.

Severity shading follows the earliest first-timeout index: white = no timeout;
the single-hue ramp darkens as the first failure moves earlier.

Set Starting overheat level on three lines and center it vertically across the
three header rows. Center every column header on both axes. Keep each fixed-width
data cell in the table grid but right-align its numeric or `--` entry.

Each colored cell reports the earliest index only; shading follows that index.
`--` means that no timeout occurred within the 30-capture horizon.

### Archived removed statistics

The 2026-09-02 simplification removed the median from each cell and the
first-timeout overheat-level range from the second column. The original values
are retained here as `earliest/median`; `--` means the statistic was not reached
within 30 captures.

| Starting level | First-timeout level | Normal 12MP M+S | Normal 12MP M | Normal 24MP M+S | Normal 24MP M | Memory 12MP M+S | Memory 12MP M | Memory 24MP M+S | Memory 24MP M |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lv0 | Lv1--3 | --/-- | --/-- | 29/-- | --/-- | --/-- | --/-- | 26/30 | --/-- |
| Lv1 | Lv2--3 | --/-- | --/-- | 29/-- | --/-- | 24/28 | --/-- | 19/22 | --/-- |
| Lv2 | Lv3 | 24/27 | --/-- | 18/23 | --/-- | 15/23 | 29/-- | 14/21 | 25/-- |
| Lv3 | Lv3--4 | 13/18 | 21/29 | 12/17 | 20/28 | 8/13 | 19/27 | 5/11 | 13/23 |
| Lv4 | Lv4--5 | 8/12 | 16/27 | 7/10 | 13/22 | 6/11 | 13/24 | 3/9 | 7/13 |
| Lv5 | Lv5--6 | 8/10 | 12/15 | 8/10 | 12/15 | 4/8 | 9/17 | 4/8 | 9/17 |
| Lv6 | Lv6 | 7/9 | 11/16 | 7/9 | 11/16 | 3/7 | 6/12 | 3/7 | 6/12 |

To restore the fuller diagnostic view, reintroduce the first-timeout level
column from the second field above and print the remaining cells as
`earliest/median`. Keep severity shading keyed to the earliest index.

### Column map

Recorded from the column-spec labels that used to sit in the tabular preamble.

| Column spec | Column |
| --- | --- |
| `\providecolor{tmoS1}{RGB}{252,227,220}` | first failure at capture >= 20 |
| `\providecolor{tmoS2}{RGB}{239,160,140}` | 10--19 |
| `\providecolor{tmoS3}{RGB}{201,80,63}` | 6--9 (white text) |
| `\providecolor{tmoS4}{RGB}{143,36,32}` | <= 5 (white text) |

## alg_admission

`figures/alg_admission.tex` &middot; Live -- `3_3_admission.tex`

Section 3.3 as pseudocode, added 2026-08-22 on the advisor's request. Input
from the top of `3_3_admission.tex`, which cites it as
`Algorithm~\ref{alg:admission}`; it floats to the top of the column where 3.3
starts. Requires `algorithm` and `algpseudocode`, added to `paper.tex` for
this exhibit and used by nothing else.

Three procedures, in the order 3.3 states the facts they carry: `Admit` is
the live-budget test and the sticky effect-group demotion, `SelectFactor`
is the Kish selector over the residual history, and `Calibrate` is the
capture-end residual update that fills the history `SelectFactor` reads.
The selector went through two other names on 2026-08-22, and both failures
are worth keeping. `Factor` collided with 3.2: \(\gamma\) is the `condition
factor` there and its weights decay by the same \(0.90\), so both the call
and `decay all factor weights` read as \(\gamma\)'s estimator. `Residual
Factor` fixed the collision and created a worse one, since the procedure
selects \(\phi_{\tau}\) from stored factors and does not compute the
\(\phi\) of Eq. 3 -- which `Calibrate` does, nine lines below. `Select`
names the operation, and the decay line stays qualified as
`residual-factor weights`. Every quantity is the
one 3.2 and 3.3 already define -- \(\hat P(\cdot)\) in particular stays the
function Eq. 2 defines and is never rebound to a scalar -- and the comments
point at the equations rather than restating them, so the float must be
re-read whenever an equation in 3.2 or 3.3 is renumbered or its content
changes.

The float's scope is the admission decision, and the watchdog appears only as
the window \(W_{i,j}\) that decision sizes. What happens when that window
expires -- the original-input save, which thread performs it, how long the
fallback persists -- is 3.3 prose and 3.5, not this float. Two `Watchdog
expiry` / `Queue drain` event lines carried it for part of 2026-08-22, as
full procedures first and then as unnumbered prose; both readings restated
implementation semantics the manuscript already gives, and both sat visibly
outside the decision flow. The one fact that had to survive their removal is
that \(G\) is queue-local, which is now the comment on the \(G\) update
itself. Do not reinstate the handlers; if a reviewer misses the fallback's
lifetime, extend 3.3's prose.

Two of its details answer a review of the first draft (2026-08-22) and must
not be undone as verbosity.

- `Admit` computes two upper estimates under two names, \(U\) for
  \(\mathcal{K}_{i,j}\) and \(U_{\mathcal{E}}\) for \(\mathcal{E}_i\). The
  draft assigned the scalar \(U\) and then wrote \(U(\mathcal{E}_i)\) three
  lines later, reusing a bound value as though it were the function Eq. 4
  defines. Do not fold the two back into one symbol.
- `Calibrate` binds \(\hat p^{d}\) and \(\hat P^{d}\) from the decision record
  before it forms \(\phi\), so the float cannot be read as recomputing
  \(\hat p(k)\) at completion. This is 3.3's `using stored decision-time
  predictions`, and it is what makes the residual reproducible; the
  superscript exists only in the float. `Admit` carries the matching `record`
  line, without which the float reads from a store nothing writes. It sits
  before the skip test on purpose: a skipped stage's prediction is still
  recorded, and its sequence is then excluded at completion by the
  fully-observed test rather than by never having been written.

Verified against the implementation at `ML@63f9bb7`
(`DraftSequenceExecutionPredictor.kt` for the estimate, the selector and the
watchdog window, `DraftSequenceAdmissionPolicy.kt` for the demotion set,
`DraftSequenceExecutionProfiler.kt` for where a decision is taken and when
calibration runs).

Four deliberate omissions, all implementation detail that 3.3 does not carry.
The workload-policy classification (the code's `OPTIONAL`, `REQUIRED`,
`RESERVED`) is out: the manuscript says `optional stage` and `mandatory
terminal key`, and the author asked on 2026-08-22 to keep the taxonomy out of
the float. The Frame Watermark exception -- a Frame Watermark and the
decoding it forces are never demoted -- is out for the same reason. `Admit`
tests `G` before it estimates, whereas the code estimates first and lets the
policy layer override, because the code's extra estimate feeds the metrics
store only; the decision is identical. And the code records the watchdog
reservation's own estimate as a decision too, so the terminal-only sequence
accumulates its own residual history; the float records only the admission
decision, because 3.3 describes the reservation as a window computation and
not as a second decision.

`\Require`/`\Ensure` lines were drafted and cut the same day: they restated
the procedure signature, which is the one place a reader already looks.

\(W_{i,j}\) is computed on its own line rather than inside the `return`, so
that every equation of 3.2 and 3.3 the float uses is anchored by a comment
(Eqs. 2 and 4 on \(U\), 5 on the test, 6 on \(W_{i,j}\), 3 in `Calibrate`).
Folded into the `return`, the line is too long for `\Comment` to fit beside
it: the marker stays and `Eq. 6` alone wraps to the next line, which is the
float's only wrapped line. The split costs one numbered line and buys a
reference the reader would otherwise have to find in the prose.

`SelectFactor` ends on two lines that spell out the weighted-quantile walk instead
of calling a `WeightedQuantile` helper, and its sums are indexed
\(l \in H\) so the selected history, not the pool, is visibly the population.
The float exists to show how \(U\) is built from online evidence and then
spent against the budget; a helper name would hide the one line where
\(\tau\) picks an actual observation. Length is not the thing to optimize
there. The ascending sort is its own line for the same reason: it was folded
into the return as `smallest factor whose cumulative weight reaches ...` for
part of 2026-08-22, which left the float with a cumulative weight and no
stated order to accumulate in. 3.3's own sentence sorts first too.

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

Coordinated admission and pacing in a representative 12MP 30-capture run
without external memory pressure.  The measurement source and peer population
are recorded under tab_casestudy_selection above.  Run 28 is the nearest
non-singleton alternative to the medoid under the documented five-metric
distance rule.

The shaded controller-off timeout window from the previous data collection is
removed.  The 2026-09-06 workbook contains controller-on sessions only and is
from a different device, so retaining the old 8--12 window would create an
invalid cross-device baseline.  Red is now reserved for the Capture Timeout
floor in the merged panel.

The four panels map workbook fields directly: bokehExecuted to M,
filterExecuted to S, appliedDelayMs to the pacing bars, realQueueDepth to
Draft Sequence queue depth, and realBacklogMs and timeoutMarginMs to the two
curves of the merged share-of-timeout panel.  The exported CSVs preserve
runShotIndex as the capture index.

Queue depth is an integer count, so it is drawn as a staircase rather
than as the interpolated series used for the two time-valued curves.

---- stage execution strip -------------------------------------

Run 28 executes M on captures 1--14 and skips it on captures 15--30.
S executes on all 30 captures.  Filled and hollow square marks preserve the
existing executed/skipped encoding.

---- queue depth -----------------------------------------------
Grouped with the execution strip above it because both are per-capture
discrete quantities.  The panel now uses realQueueDepth, the count of waiting
Draft Sequences, rather than the earlier in-service-inclusive reconstruction.
Both fields are observed on all 30 captures in run 28, so the plotted
trajectory needs no imputation or gap marker.

---- applied pacing delay --------------------------------------
The largest applied delay is 792 ms at capture 19.  The axis ceiling is
900 ms with labelled ticks at 0, 400, and 800 ms; the panel height is
0.27 column widths.  A 7pt separation between panels keeps adjacent top and
bottom tick labels distinct in the rendered column.  This case-study panel is
scaled to the selected run; the all-run RQ4 summary reports delay
distributions numerically instead.

---- Draft backlog and Slack (merged) ---------------------------

Draft backlog and Slack shared an axis on 2026-09-07; they were two stacked
panels before.  Both are durations divided by the same 7000 ms Capture
Timeout budget, so a shared ordinate is dimensionally legitimate, and it
shows what the split panels could not: backlog and realized Slack move
against each other across the whole run, which is the coupling the
controller exists to manage.  The two stacked panels also duplicated the
ordinate scale, the grid, and the 0--60% tick column for one shared unit.

What the shared axis must NOT be read as: the two curves do not partition
the budget and do not sum to 100%.
Verified against ML@bb27a0f, `CaptureMetricsExcelExporter.kt`:
`timeoutMarginMs` is `timeoutTimestampMs - draftEndUptimeMs` (L1594), read
from the capture's own deadline clock, while `realBacklogMs` is
`max(draftEndUptimeMs)` over unfinished earlier Drafts minus the pacing
decision snapshot (L352).  The origins differ, and neither term contains the
capture's own Draft duration, so the identity is
`Slack = T_i - backlog - (own Draft + release gap)`, where `T_i` is the
decision-time remaining window -- 3,792 to 7,000 ms at 12MP per the
tab_rq4_pacing_sizing entry above, and not a quantity this figure prints.
On the plotted run the pair sums to 45.5%--73.2%.  Capture 8 is the case
that prompted the check: 3,033 ms of backlog against 150 ms of Slack, with
3,817 ms of the capture's own work (including its 386 ms applied delay) in
between, totalling 6,850 ms of the 7,000 ms budget.

For the same reason the crossings carry no threshold meaning.  Two
differently anchored intervals becoming equal is not a safety event, and
`backlog > Slack` reduces to `2*backlog + own work > budget`, which is not a
criterion the controller uses or the paper claims.  Do not annotate the
crossings, and do not describe them in prose as the point where Draft
pressure overtakes the remaining window.  An additive panel would need `T_i`
stacked as backlog + own Draft + Slack; `T_i` is not in
`data/case_study/12mp_normal_*.csv`, so that variant requires a new export
rather than arithmetic on the current files.

The non-additivity belongs in the caption, not the ylabel, and the ylabel is
`\% of\\Capture Timeout` for that reason.  Two attempts to make the label
carry it were tried on 2026-09-07 and both stated something false about a
curve.  `Duration` reads as elapsed processing time, which Slack is not: it
is `deadline - draftEnd`, time deliberately left unspent, so the word
reclassifies the safety quantity as a cost.  `Interval` is correct for both
and is the word the implementation note uses for backlog, but on a
per-capture ordinate it collides with the completion-to-completion interval
$\pi_i$ of Section 3.1 and reads as the gap between shots.  The plain
normalization is true of both curves and asserts no genus; the caption is
where the reader is told the pair does not add up, and it is also where a
reviewer looks for that qualification.

Encoding: Draft backlog is a solid blue!55!black line, reusing the pacing
bars' color so the delay panel above reads as the response to the curve
below; Slack is a solid black!80 line.  Both carry the same round 0.9pt mark
the two panels used before the merge, and both are solid: color alone
separates them, and the identical line and mark keep the two series reading
as the same kind of measured per-capture quantity rather than as a series
and a reference.  Dashing is therefore free, and it is spent on the Capture
Timeout floor below, which is what a dash pattern conventionally marks.  The
legend entry is "Backlog", not "Draft backlog": the panel's other curve is
"Slack", the ylabel already scopes both to the Capture Timeout budget, and
the one-word pair keeps the two-column legend inside the corner it occupies.
That legend sits at the panel's north east, the one corner neither curve
enters.

Timeout floor: the 0% line is Slack's failure boundary and not Backlog's.
Backlog shares the ordinate because it is a duration against the same
denominator, but no horizontal line is a threshold for it, and it
legitimately sits at 0% on capture 1, where the queue is empty.  The
merge therefore made a full-width solid red rule read as a threshold for
both curves, with its label landing next to exactly the point that misreads
worst.  Two changes fix the ownership without weakening the deadline: the
label reads "Capture Timeout (Slack = 0)" and moves to the panel's south
east, the far side from the capture-1 backlog origin; and the rule is dashed
so it reads as a reference rather than a third series.  The floor stays the
only failure encoding; no below-zero tint or cross-device reference band is
drawn, and the minimum-approach annotations stay on the Slack curve.

Geometry: the merged panel is 0.40 column widths, against 0.30 + 0.30 plus a
separation for the pair, so the figure is about 0.20 column widths shorter.
ymax is 80 rather than the pair's 70 to clear the legend row above the
backlog peak; ymin remains -11 so the Capture Timeout label can hang below
the 0% floor without clipping.  Labelled ticks stay at 0/20/40/60%.  The
ylabel is the shared unit alone, since the legend names the quantities.

Values in this entry are not all reconcilable with the tree: the 68.2%
backlog peak at capture 15, the 3.10% Slack minimum, the 75% axis, the 900 ms
delay ceiling, and the removal of the shaded window describe the 2026-09-06
collection, which was documented here in d135b2e but whose figure and CSVs
never landed.  `data/case_study/12mp_normal_*.csv` is still the earlier
collection: backlog peaks at 4469 ms (63.8%) at capture 23, Slack bottoms at
150 ms (2.14%) at capture 8 with a second low of 354 ms (5.06%) at capture
24, and those are the two annotations the figure prints.  The geometry above
describes the file as it stands; resolve the numeric half when the 2026-09-06
data is transferred.

---- stage legend -----------------------------------------------
The two-row legend remains right-aligned above the execution strip.  Both
entries use "stage" so the execution and admission-skip states stay
grammatically parallel.  Although S has no skipped marks in this run, the
hollow entry is still needed to decode the M row.

## fig_casestudy_s26_12mp

`figures/fig_casestudy_s26_12mp.tex` &middot; Candidate -- not input by any section

Alternative S26 case study for 12MP capture without external memory pressure.
Measurement source: SM-S942B_metrics_12MP_normal_0906.xlsx, supplied outside
the repository on 2026-09-07 (SHA-256
72b4140894e433686f7b821cd8be4c3db019cff9b4c1ba784a0c1ed0371037e).
The plotted trace is `CaseStudyTrace` run 4 (workbook rows 92--121);
the peer audit comes from `RQ3Summary`.

The peer set fixes starting overheat level 4, complete 30-capture execution,
and no recorded Capture Timeout or watchdog failure. It contains runs 4, 5,
17, 18, 19, 30, 31, 32, 39, and 52 (n = 10). Selection uses the same
five-metric min--max-normalized distance documented for the live case study:
pacing activation, cumulative applied delay, M execution, S execution, and
Slack P5. Run 4 has the smallest distance (0.725); run 39 is next (0.769).
Run 4 also has no singleton pacing block and exposes both admission decisions.

The figure uses one derived trace file,
`data/case_study/s26_12mp_normal_trace.csv`. Its fields map
`bokehExecuted` to M, `filterExecuted` to S, `appliedDelayMs` to the
bars, `realBacklogMs` to Draft backlog, `realQueueDepth` to Draft Sequence
queue depth, and `timeoutMarginMs` to Slack. Capture 2 lacks backlog and queue
measurements, so the CSV records `nan` and the corresponding plots open a gap.

Run 4 executes M through capture 19 and S through capture 20, then skips the
respective stages. Pacing occurs on captures 9--13 and 15--26, with a maximum
of 736 ms at capture 20. Draft backlog peaks at 4,748 ms (67.8% of the timeout)
at capture 19. Slack reaches 37 ms (0.53%) at capture 20 and then recovers;
the annotation rounds this observation to 0.5%. No capture in the run records
Capture Timeout or a watchdog failure.

The four-panel layout retains the queue-depth strip required for a demotion
case but merges Draft backlog and Slack because both are expressed as a share
of the same timeout. Marker shape and color distinguish those two curves.
Horizontal grid lines only, a shared capture axis, and an in-panel two-column
legend reduce visual density relative to the five-panel alternative.

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
