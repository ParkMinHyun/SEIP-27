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

### Paper integration and current exhibits

- `2_4_static_safeguards.tex`
- `tables/tab_rq3_pacing_compact.tex`
- `figures/fig_rq3_pacing_compact.tex`
- `docs/tab_rq3_pacing_compact_preview.png`
- `docs/fig_rq3_pacing_compact_preview.png`

### Generators used by the compact pair

- `scripts/rq3_policy_metrics.py`
- `scripts/rq3_calibration_metrics.py`
- `scripts/rq3_selectivity_metrics.py`
- `scripts/rq3_coordination_metrics.py`
- `scripts/rq3_coordination_audit.py`
- `scripts/render_rq3_compact_preview.py`

`rq3_policy_metrics.py` imports the calibration loader and selectivity
bootstrap/binning helpers, so copy all three even if only the policy generator
is being changed. That path requires `openpyxl`. The coordination and preview
generators use only the Python standard library.

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
- `avoided_delay_12mp_normal.csv`
- `avoided_delay_24mp_memory.csv`

Generated CSV cells must not be edited manually. Regenerate them from the
scripts above when the source workbooks or eligibility rules change.

## Source workbooks required for regeneration

- `data/ablation_sampling/48U_metrics_12MP_normal_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_12MP_normal_0803_2.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_1.xlsx`
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_2.xlsx`

These are inputs, not files created by the compact RQ3 work.

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
python3 scripts/render_rq3_compact_preview.py
```

After the preview script writes its temporary HTML/SVG, render the two preview
PNGs with headless Chrome. The final paper should still be compiled with the
repository `Makefile` on a machine with `pdflatex` and all required packages.

## Current environment verification status

- Coordination aggregation: reproduced.
- Admission-action and floor audit: reproduced.
- Browser preview generation and OCR: verified.
- Targeting/boundary regeneration: source updated, but local execution is
  blocked by missing `openpyxl`; the committed policy CSVs remain available.
- LaTeX build: blocked locally because `pdflatex` is not installed.
