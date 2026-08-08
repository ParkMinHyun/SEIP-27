# RQ3 File Manifest

This manifest lists the files required to carry the current RQ3 summary to
another session or paper branch. Paths are repository-relative.

## Copy these current source and context files

### Shared context and interpretation

- `AGENTS.md`
- `docs/rq1-rq3-metrics-guide.md`
- `docs/rq3-current.md`
- `docs/rq3-file-manifest.md`
- `data/rq3/coordination/README.md`
- `data/rq3/estimator/README.md`

### Paper integration and current exhibits

- `2_4_static_safeguards.tex`
- `tables/tab_rq3_pacing_summary.tex`

RQ3 ships one single-column table and no figure. The table carries its
definitions, provenance, and claim limits in its own header comment; copy the
file whole rather than extracting the environment and review it from a
`pdflatex` render.

### Generators used by the summary analysis

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

## Copy or regenerate these generated inputs

### Targeting and boundary-mechanism data

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

### Admission--pacing coordination data

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

### Outcome matrix and estimator data

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

## Source workbooks required for regeneration

- `data/ablation_sampling/48U_metrics_12MP_normal_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_12MP_normal_0803_2.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_2.xlsx`

These are inputs, not files created by the RQ3 summary analysis.

The superseded policy, selectivity, and calibration TeX exhibits and their
obsolete preview script have been deleted. The calibration and selectivity
Python modules remain because `rq3_pacing_summary_metrics.py` imports their shared
loader, binning, bootstrap, and burst helpers.

## Regeneration order

```text
python3 scripts/rq3_pacing_summary_metrics.py sampling  # requires openpyxl
python3 scripts/rq3_coordination_metrics.py
python3 scripts/rq3_coordination_audit.py
python3 scripts/rq3_estimator_metrics.py
make                                            # requires pdflatex
```

## Current environment verification status

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
