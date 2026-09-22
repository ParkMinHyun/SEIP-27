# Naive recent-N baseline replay (2026-09-22)

Question (advisor): what goes wrong if the controller simply uses the mean of
the last N completed draft sequences instead of the current method?

Sources: the four full-controller workbooks that RQ4 uses
(`data/S26_Ultra/SM-S948U_metrics_12MP_normal_0906.xlsx`,
`data/S26_Ultra/SM-S948U_metrics_24MP_memory_0906.xlsx`,
`data/S26/SM-S942B_metrics_12MP_normal_0906.xlsx`,
`data/S26/SM-S942B_metrics_24MP_memory_0829.xlsx`).
The predictor port follows `ML@b6712a0` (working tree, with a local change to
`CaptureAvailablePacer.kt` only; the predictor files were clean).

## Run order

```
python load.py          # workbooks -> wb.pkl
python partA.py         # open-loop forecasts at every recorded decision -> adm.pkl, pac.pkl
python validate.py      # port reproduces recorded P-hat and U
python runsim.py late   # per-run capture timelines -> prep_late.pkl
python runsim.py early
python val2.py          # simulator + ported controller reproduce the recorded trace
python arms.py late     # closed-loop admission replay, all estimators
python arms.py early
python summarize.py late early
python sens.py          # imputation sensitivity (min / median of 5 nearest)
python tables.py        # CSVs under out/  (copies are in results/)
# follow-up: stage-wise naive (sum of each remaining stage's recent-N statistic)
python arms_stage.py late          # summary_stage_late.csv (kept as results/B_stage_naive_arms.csv)
python arms_stage_margin.py        # additive margin sweep (results/B_stage_naive_margin_sweep.csv)
python arms_stage_scale.py         # multiplicative factor sweep (results/B_stage_naive_scale_sweep.csv)
python partA_stage.py              # open-loop coverage, and U/P-hat by condition
python shadow.py                   # shadow U / P-hat at naive admissions that ended in a miss
```

## What each layer is and is not

- Part A (open loop): forecasts scored against realized time-to-draft-end
  (`draftEnd - nodeStart`) or realized backlog on the recorded trace. No
  counterfactual.
- Part B (closed-loop admission replay): capture requests, draft-ready times,
  pacing delays, session boundaries (`pacerSessionId`) and non-stage time are
  pinned to the trace; only the admission estimator changes. Stages the recorded
  controller skipped take the nearest executed duration of that stage in the same
  run. COMPLETE_30 runs only (226 runs, 6,780 captures). This is a
  TRACE_CONDITIONED_ESTIMATE in the workbook's own terminology, not a factual
  arm. Pacing is frozen at the recorded delays, which were sized for the recorded
  workload; thermal feedback and the watchdog are not modeled.
- Part C (pacing, one step): the manuscript's `eq:pacing` evaluated with swapped
  inputs at each recorded decision. A closed-loop pacing comparison is not
  identifiable from these exports (the app cadence and the gate cannot be
  separated), so no pacing counterfactual outcome is claimed.
