# RQ3 File Manifest

This manifest lists the files required to carry the current compact RQ3 work to
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
- `tables/tab_rq3_pacing_compact.tex`
- `figures/fig_rq3_pacing_compact.tex`

Both exhibits carry their definitions, provenance, and claim limits in their own
header comments; copy the files whole rather than extracting the environments.
The browser-preview PNGs earlier revisions listed here are no longer produced —
review from a `pdflatex` render instead.

### Generators used by the compact pair

- `scripts/rq3_policy_metrics.py`
- `scripts/rq3_calibration_metrics.py`
- `scripts/rq3_selectivity_metrics.py`
- `scripts/rq3_coordination_metrics.py`
- `scripts/rq3_coordination_audit.py`
- `scripts/rq3_estimator_metrics.py`

`rq3_policy_metrics.py` imports the calibration loader and selectivity
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

Everything the current table and figure print, apart from the cost block.

- `summary.csv`
- `outcome_matrix.csv`
- `queued_pricing_scatter.csv`
- `scatter_{12mp_normal,24mp_memory}_{no_delay_required,covered,flexible,below_floor}.csv`
- `draft_pricing_ecdf_{12mp_normal,24mp_memory}.csv`
- `reserve_error_ecdf_{12mp_normal,24mp_memory}.csv`

The eight `scatter_*` files are the rows of `queued_pricing_scatter.csv` split
per mark style, which is what pgfplots consumes;
`scatter_12mp_normal_below_floor.csv` is deliberately a header with no rows,
because no 12MP decision fell below the floor.

Generated CSV cells must not be edited manually. Regenerate them from the
scripts above when the source workbooks or eligibility rules change.

## Source workbooks required for regeneration

- `data/ablation_sampling/48U_metrics_12MP_normal_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_12MP_normal_0803_2.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_2.xlsx`

These are inputs, not files created by the compact RQ3 work.

## Generators the current pair no longer calls

`scripts/render_rq3_compact_preview.py` produced the browser-review PNGs that
earlier revisions shipped. It is preserved, not deleted, but it renders the
previous exhibit layout and is not part of the reproduction sequence above.
`docs/rq1-rq3-metrics-guide.md` still lists it; that document is historical
material.

## Historical RQ3 alternatives to preserve

The compact pair replaces these as the current include, but they remain useful
provenance and must not be deleted:

- `tables/tab_rq3_pacing_policy.tex`
- `figures/fig_rq3_pacing_policy.tex`
- `tables/tab_rq3_pacing_selectivity.tex`
- `figures/fig_rq3_pacing_selectivity.tex`
- `tables/tab_rq3_pacing_calibration.tex`
- `figures/fig_rq3_pacing_calibration.tex`

Do not include all historical pairs beside the compact pair in the main paper.

## Regeneration order

```text
python3 scripts/rq3_policy_metrics.py sampling  # requires openpyxl
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
- LaTeX build: reproduced with TeX Live 2026 `pdflatex`, no overfull or
  underfull boxes.
