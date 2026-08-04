# Case-study figures

## Evidence and selection

The figures use `CaseStudyTrace` and `RQ3Summary` from the following exporter outputs:

- `SM-S948U_metrics_12MP_normal_0803.xlsx`
- `SM-S948U_metrics_24MP_memory_0803.xlsx`

The workbooks were exported from implementation commit
`99aae0af8c3fa1ceb784083446e83c40d0fb917f`. Captures with a recorded Capture
Timeout or watchdog failure are excluded from case-study eligibility and from
the same-condition medians.

The selection protocol requires one complete 30-capture run to show the full
coordination sequence: pacing activates before Bokeh demotion; pacing later
reaches zero; backlog then increases and pacing reactivates; Filter demotes at a
later capture; and all 30 captures complete without a timeout.

- **12MP normal-memory run 30** is the only failure-free run that satisfies the
  sequence. It starts at overheat level 4, reaches level 5 at capture 20, and
  remains MP12 throughout.
- **24MP-mode memory-pressure run 34** is one of two mechanism-complete runs.
  The other, run 27, starts at level 5 and is therefore the production MP12
  fallback. Run 34 starts at level 3, reaches only level 4, processes captures
  1--2 at MP24 and captures 3--30 at MP12, and never enters the level-5
  fallback.

The selected runs are deliberately not best-performing traces. The precise
selected-versus-peer-median values are recorded in
`data/case_study/0803/selection_audit.csv` and printed beneath each figure.

## Caption drafts

**12MP normal-memory case.** Coordinated control during a failure-free 30-capture
run. Pacing activates at capture 5 before Bokeh demotes at capture 9. Because
previously admitted Drafts remain queued, the pacing delay persists through
capture 12; it then reaches zero while the lighter Filter-only sequence runs.
Unpaced arrivals rebuild the backlog and reactivate pacing at capture 21, after
which Filter demotes at capture 23. The deadline margin remains positive for all
captures. The run is selected for complete mechanism coverage, not favorable
performance; its pacing cost and burst span exceed the same-condition medians,
whereas its lower-tail margin and optional-stage completion are lower.

**24MP-mode memory-pressure case.** Coordinated control during a failure-free
30-capture run without level-5 resolution fallback. Pacing activates at capture
4; Bokeh demotes and the delay reaches zero at capture 6. As arrivals rebuild
the queue, pacing reactivates at capture 9, and Filter later demotes at capture
17. The deadline margin remains positive for all captures. Captures 1--2 are
processed at MP24 and captures 3--30 at MP12, matching the production 24MP-mode
protocol. The run is selected for complete non-fallback mechanism coverage, not
favorable performance; its pacing cost and burst span exceed the same-condition
medians, whereas its lower-tail margin and optional-stage completion are lower.

## Files

- `fig_case_study_12mp.tex` and `fig_case_study_24mp.tex`: standalone PGFPlots sources
- `case_study_trace_body.tex`: shared layout
- `fig_case_study_12mp.pdf` and `fig_case_study_24mp.pdf`: publication-ready vector output
- `fig_case_study_12mp.png` and `fig_case_study_24mp.png`: review previews
