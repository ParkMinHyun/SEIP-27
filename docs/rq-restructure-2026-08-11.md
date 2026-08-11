# RQ restructure of 2026-08-11 — what changed and how to put it back

Advisor meeting of 2026-08-11. Five columns left RQ1, two left the admission
table, the ablation became its own research question, and everything downstream
renumbered. **Nothing recorded here was deleted because it was wrong.** Every
removed value is printed below in the form it was published in, so any of it can
be restored without re-deriving it from the workbooks.

Read this before reinstating any column. Each section states the values, the
LaTeX that carried them, and what else has to move with them.

---

## 1. Numbering map

The manuscript now has four research questions. The evidence layer does not
follow the renumbering — see §5.

| New | Question | Was | Exhibit |
|---|---|---|---|
| RQ1 | End-to-end effectiveness | RQ1(a) | `tables/tab_rq1_end_to_end_summary.tex` |
| RQ2 | Control-loop contribution | RQ1(b) | `tables/tab_rq2_ablation.tex` |
| RQ3 | Admission decision quality | RQ2 | `tables/tab_rq3_admission_summary.tex` |
| RQ4 | Pacing-delay sizing | RQ3 | `tables/tab_rq4_pacing_summary.tex` |

### File renames (`git mv`, history preserved)

| Old | New |
|---|---|
| `tables/tab_rq1_ablation.tex` | `tables/tab_rq2_ablation.tex` |
| `tables/tab_rq2_admission_summary.tex` | `tables/tab_rq3_admission_summary.tex` |
| `tables/tab_rq3_pacing_summary.tex` | `tables/tab_rq4_pacing_summary.tex` |
| `figures/fig_rq2_unsafe_spike_anatomy.tex` | `figures/fig_rq3_unsafe_spike_anatomy.tex` |

### Label renames

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

## 2. RQ1 — five columns removed, three changed unit

`tables/tab_rq1_end_to_end_summary.tex`. The table went from 20 columns to 14.

### 2.1 Removed: Timeout onset **M** (Kaplan–Meier median first-timeout capture)

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

### 2.2 Removed: Slack P5 (%)

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

### 2.3 Removed: the M+S pair (@5 / @30, %)

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

### 2.4 Removed: the cumulative-delay pair Σ*d* P50 (@5 / @30, s)

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

### 2.5 Changed unit: M, S and Activated now print counts

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

### 2.6 Two places outside RQ1 that depended on the removed columns

* `figures/fig_casestudy_12mp.tex` shades captures 8–12 as the baseline
  first-timeout window. The 8 is RQ1's printed onset; **the 12 was the removed
  KM median** and now has to come from §2.1 of this document.
* `tables/tab_casestudy_selection.tex` compares its peer medians against RQ1's
  12MP/Lv4 macro-averages. Those are now 9.8 transitions, 10.3 M captures and
  29.2 S captures, not 33.8% / 34.3% / 97.3%.

---

## 3. RQ3 — two columns removed and the two blocks merged

`tables/tab_rq3_admission_summary.tex`.

### 3.1 Removed: Feasible-work **Margin** and Unsafe-work **Overrun**

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

### 3.2 The two blocks became one table, still inside `\columnwidth`

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

### 3.3 Removed: the per-row percentages

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

### 3.4 Removed: the `[watchdog]` cause annotation and the population subtitles

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

### 3.5 One row is new

**Overall** previously existed only in block (a). Its audit-half cells —
3,470 (97.3%) / 98 (2.7%) feasible and 5 (2.8%) / 173 (97.2%) unsafe — are the
sum of the four printed audit rows (3,568 feasible and 178 unsafe decisions), not
a separate regeneration. Pooling within a half is what block (a)'s Overall row
already did.

---

## 4. Open item, inherited not introduced

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

## 5. What did NOT renumber, and why

`docs/`, `data/` and `scripts/` keep the old RQ numbering:

* `docs/rq1-rq3-metrics-guide.md` still documents RQ1(a), RQ1(b), RQ2, RQ3 —
  read them as RQ1, RQ2, RQ3, RQ4.
* `docs/rq3-current.md`, `docs/rq3-file-manifest.md`, `data/rq3/**` and
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
