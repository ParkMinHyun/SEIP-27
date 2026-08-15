# Project Rules

This repository is a LaTeX paper project for SEIP 2027.

## Shared Context

- Treat `AGENTS.md` as the single source of truth for shared working context, used by both Codex and Claude. `CLAUDE.md` imports it via `@AGENTS.md`, so edit `AGENTS.md` only.
- Keep instructions in repository-relative paths only. Do not add local absolute paths or machine-specific settings.
- When a durable project rule changes, update this file and commit it so other machines inherit the same context after `git pull`.
- User-facing discussion can be in Korean, but manuscript text should be written in polished academic English unless explicitly requested otherwise.

## Session Startup Sync

- At the start of a work session, ask whether the user wants to sync the shared context and implementation reference.
- Use `./sync-context.ps1` from the repository root to update this paper repository and any accessible `ML` implementation clone.
- The sync script uses safe fast-forward pulls and reports the commit hashes that should be treated as the current context.
- If syncing fails because of credentials, network access, or local uncommitted changes, report the issue and continue only with the accessible context.

## Paper Goal

- Current manuscript topic: preventing Capture Timeout in the Android Camera Framework.
- The Draft Sequence was introduced together with the post-processing pipeline; it publishes an early image and provides recovery while post-processing continues.
- The work targets enabling lightweight multi-frame composition in the Draft Sequence for Portrait mode, whose heavy post-processing can then be deferred until the camera app enters the background.
- The proposed system is the Budget-Aware Draft Controller, comprising remaining-sequence admission and capture-availability pacing. Use the descriptive name without a forced acronym and refer to it as ``the controller'' after first use.
- The paper studies coordinated workload and arrival control for tail-latency-based Capture Timeout, not average-latency optimization for a single image-processing stage.
- Frame the work as feature enablement under a safety constraint, not as timeout mitigation. The hierarchy is: enable the Draft Sequence's lightweight multi-frame composition under parallel capture whenever safely possible → Capture Timeout is the deployment blocker → static thermal gating cannot tell safe captures from unsafe ones → coordinated runtime control of workload and capture arrival. Sections 2.4, 3.1 and 3.2 already open on this hierarchy; align the abstract, introduction, and conclusion with it when they are drafted.
- Preserve the core research framing unless the user explicitly asks to change the problem statement, contribution, or terminology.

## RQ Numbering (changed 2026-08-11)

The manuscript has **four** research questions. The evidence layer under `docs/`, `data/` and `scripts/` still uses the old three-RQ numbering as internal compatibility names — the same treatment the CSV fields containing `required` already get. Translate, do not rename.

| Manuscript | Question | Was | Exhibit | Evidence layer still calls it |
|---|---|---|---|---|
| RQ1 | End-to-end effectiveness | RQ1(a) | `tables/tab_rq1_end_to_end_summary.tex` | RQ1(a) |
| RQ2 | Control-loop contribution | RQ1(b) | `tables/tab_rq2_ablation.tex` | RQ1(b), `scripts/rq1_ablation_metrics.py` |
| RQ3 | Admission decision quality | RQ2 | `tables/tab_rq3_admission_summary.tex` | RQ2, `scripts/rq2_*.py` |
| RQ4 | Pacing-delay sizing | RQ3 | `tables/tab_rq4_pacing_selectivity.tex` | RQ3, `docs/rq-evidence.md`, `data/rq3/`, `scripts/rq3_*.py` |

- **The section below titled "Current RQ3 Evidence Rules" governs what the manuscript now calls RQ4.** Every "RQ3" in it means pacing-delay sizing.
- `docs/rq-evidence.md` (Part 3) records every column removed in that revision, with its published values and a restore procedure. Consult it before reinstating a column or before quoting a statistic that RQ1 no longer prints.
- RQ4 evaluates whether the proposed controller computes an appropriately sized pacing delay for the Draft backlog and Capture Timeout budget. Do not frame it as a comparison against pacing methods transplanted from other domains unless the user explicitly requests that comparison.
- RQ1 prints $M$, $S$ and Activated as per-run counts, not percentages; RQ2 keeps percentages because its denominator is captures *requested*, not captures present. Do not "unify" the two without reading §2.5 of the restructure document.

## Current RQ3 Evidence Rules

- Treat `docs/rq-evidence.md` (Part 1) as the authoritative RQ3 handoff, `docs/rq-evidence.md` (Part 4) as the transfer checklist, and `data/rq3/coordination/README.md` as the generated-artifact dictionary.
- The current main-paper exhibit is `tables/tab_rq4_pacing_selectivity.tex` alone, and RQ3 ships no figure. It replaced `tables/tab_rq4_pacing_summary.tex` on 2026-08-13: the summary table measured $d$ against the retrospective target $d^{*}$, which is algebraically an estimator report at a fixed coefficient, whereas the selectivity table asks whether the delay is selective, proportionate, and bounded. The superseded summary file stays on disk unreferenced; restore it by swapping the `\input` in `_4_experiments.tex`. Separately, an earlier generation of RQ3 policy, selectivity, and calibration TeX pairs — not the current selectivity table — was deleted; do not restore or reference those.
- RQ3 evaluates trace-derived targeting, admission-aware envelope coverage, work conservation, and responsiveness cost. It does not establish global optimality or a universally minimum counterfactual delay.
- Do not mechanically scale recorded delay by 0.5 or 0.75 on the factual trace. Pacing is closed-loop and changes subsequent backlog, admission, thermal state, throttling, and realized Draft duration; a scaling study requires new matched runs or a validated closed-loop replay/simulator.
- The deployed $2C$ horizon covers the Draft that begins after the pacing decision and the next capture's Draft released by that delay. Pacing deliberately applies half of the positive projected deficit so it does not convert all residual pressure into user-visible delay, relying on node-time admission to skip optional work when its suffix bound exceeds the live budget. This is an intuitive coordination heuristic, not an exact fixed-point derivation or a literal half-deficit transfer to admission. `target-or-next` is an observed admission-action audit over this horizon, not causal attribution of the next decision to the current delay.
- In manuscript prose, call $d^{*}$ the retrospective matched-policy target, not the physically required, minimum, or optimal delay. Existing CSV fields and class keys containing `required` are internal compatibility names for that target and need not be renamed.
- Timeout-labelled records removed from the current collection are known invalid measurements, not actual Capture Timeout outcomes. No valid analyzed run timed out; do not describe this population as survival-conditioned. Document the measurement fault and exclusion manifest when that evidence is accessible rather than inventing details.
- The mandatory floor is a sufficient retrospective reservation condition, not the actual timeout boundary. Because it already excludes optional work, admission demotion documents coordination but does not itself erase a mandatory-floor deficit.
- Every statistic printed beside a population must be computed on that population. In particular, do not explain a `Paced` count with an estimator error measured over the whole class: the class that required no delay is 81% and 78% unpaced, and restricting to the paced decisions changes the backlog error's sign. See the two-block split in `docs/rq-evidence.md` (Part 1).
- Keep the minimum realized deadline margin reported somewhere, and characterize its tail instead of trimming it. The worst observation in the collection is 0.11% of the budget — 8 ms — and "how close did it ever come" is the first thing an industrial reviewer asks of a timeout-prevention claim. Supporting facts, one row per decision, are in `data/rq3/estimator/thin_margin_tail.csv`. Never upgrade them into a bounded-margin or guaranteed-deadline claim, and leave the baseline counterfactual to RQ1.
- **The RQ3 prose owns that minimum, not the table.** The table prints `Slack P5` per class and nothing else: no min column, and no tail sentence in the note. Two reasons. Per class the minimum is not always the informative statistic — on the 14-decision floor block min and P5 are 4.39% and 4.53% — and a bare min column reads as "no timeout was luck". More decisively, the 0.11% is the minimum of the *no-delay-required* class, which block (a) excludes and block (b) prints no Slack column for; it is therefore the minimum of no column the table prints, and 6 of the 11 sub-1% decisions sit in that same unprinted class. On the rows (a) does print, P5 understates the class minimum by only 1.03x–4.1x, so the printed column is not misread without it.
- When the prose states the 0.11%, it must carry the saturation that explains it (backlog already 42–79% of the budget, queue wait 31–75%, overheat 5–6 or late in a burst), that pacing or an optional-work skip was engaged on all eleven, and the claim limit. Do not let it stand as a bare number — that is what makes it read as a lucky escape.


## Implementation Reference

The actual implementation for this research is maintained in a private GitHub repository:

- `https://github.com/ParkMinhyun/ML`

Use this implementation as the primary source of truth when writing or revising methodology, architecture, algorithms, implementation details, and evaluation setup. Because the repository is private, access may depend on each machine's GitHub credentials.

Preferred lookup order:

1. If `external/ML/` exists in this repository, inspect it first.
2. If `../ML/` exists as a sibling clone, inspect it next.
3. If `LOCAL_CONTEXT.md` exists, read it for a machine-specific path to the private implementation.
4. If the implementation cannot be accessed, state that limitation and ask the user before writing implementation-specific claims.

Implementation-reference rules:

- Before writing methodology or direction from the implementation, check the latest accessible `ML` working tree.
- Record the implementation commit hash when using code as evidence for manuscript text.
- Distinguish implementation facts from paper-level interpretation.
- Do not invent class names, file names, algorithms, parameters, evaluation scripts, or results.
- Do not commit private credentials, tokens, machine-specific absolute paths, or private implementation source snapshots into this paper repository unless the user explicitly requests it.

## Reference Papers

Use the two PDFs in `references/` as style and organization references:

- `references/ICSE25_TOPSEED Learning Seed Selection Strategies for.pdf`
- `references/ICSE26_Enhancing Symbolic Execution with Self-Configuring Parameters.pdf`

Apply them as guidance for:

- overall paper structure and section flow;
- academic tone, argument rhythm, and transition style;
- how motivation, examples, experiments, threats, and related work are framed;
- table/figure caption style and result discussion style.

Read `docs/writing-style.md` when drafting manuscript text or giving writing
feedback. It records the recurring style patterns found across the two papers
and explains how to adapt them to an SEIP industrial paper.

Do not copy text, claims, or citations from the reference papers unless the user explicitly asks and the source is properly cited. The research topic of this manuscript is different, so use the references for writing form rather than technical substance.

## Writing Rules

- Prefer concise, direct academic prose.
- Keep terminology consistent across files. If introducing or renaming a term, check nearby section files and `macros.tex`.
- Avoid unsupported claims. If a claim needs evidence, add a citation placeholder or ask for the intended source.
- Preserve LaTeX commands, labels, citations, and macros unless the requested edit requires changing them.
- Do not invent experimental numbers, benchmark names, tool names, or citation keys.
- When editing a section, maintain consistency with the included section files in `paper.tex`.
- Keep rationale out of the `.tex` sources. Files under `tables/` and `figures/` carry one `% Notes: docs/exhibits.md#<file stem>` line and no other commentary; section files carry a pointer only where a durable constraint applies. Provenance, layout constraints, removed columns, and revision history belong in `docs/exhibits.md`; section-level writing constraints belong in `docs/writing-style.md`. When an exhibit changes, update its entry there in the same commit.

## Banned and Fixed Terminology

- **The feature being enabled is `lightweight multi-frame composition`, a stage of the `Draft Sequence`.** `2_3_draft_sequence.tex` defines it in those words and `2_4_static_safeguards.tex` denotes it \(M\), naming it the `lightweight multi-frame Draft stage`. Do not weld the two into `lightweight multi-frame Draft composition`: that compound names nothing in the implementation and reads as though `Draft` modified `composition` rather than the pipeline, which also collides with the composition that post-processing itself performs. Write `the Draft Sequence's lightweight multi-frame composition`, or `the lightweight multi-frame Draft stage` when the stage is meant as a unit.
- **The two per-capture processing pipelines are `the Draft pipeline` and `the post-processing pipeline`.** Do not write `Draft path`, `Draft-path`, or `draft path` for either; `Draft` stays capitalized because it names the pipeline, not a generic draft. `Draft Sequence` remains the defined name for the configured chain of stages, so use it where the stage composition is the point and `Draft pipeline` where the execution path as a whole is. The word `path` is still correct for control-flow branches inside the implementation — `normal path`, `drain path`, `fail-open path`, `immediate path` — and those must not be swept into this rule.
- **The heavy pipeline is always `post-processing`, never `final processing` or `final composition`.** Those two were the post-processing-side counterpart of `Draft path`: three names for one referent, all in `3_6_implementation.tex`, which is currently commented out of `_3_approach.tex`. `final` survives only as an adjective on the *output* — `final image`, `draft--final visual gap`, `Draft/final publication arbitration` — because there the contrast with the Draft image is the point. Also never leave a bare `the pipeline` in a passage where both pipelines are in scope; name which one, since Sections 2.3 and 2.4 alternate between them within a few lines.
- **`Draft Sequence`, `Draft work`, and `Draft stage` are three nested levels and must not be collapsed into one another.**
  - `Draft Sequence` — the per-capture unit that occupies the single worker. It is what the queue holds, so anything counting queued or pending items is Draft Sequences: `12 Draft Sequences pending` in `2_4_static_safeguards.tex`, and the `Draft Sequence queue depth` panel of `figures/fig_casestudy_12mp.tex`.
  - `Draft work` — the processing carried out *inside* one Draft Sequence: its service demand, how much is left, how much was retained (`how much Draft work remains`, `scales each capture's Draft work to its remaining budget`, the `Draft work retained`/`Draft work executed` table headers). Uncountable — never `Draft-works`, and never a queue unit, which is the error the case-study y-label used to make.
  - `Draft stage` — the individual step admission decides on, and how \(M\) is defined in `2_4_static_safeguards.tex`.
  Swapping any two breaks something: a quantity cannot `remain` as a stage, \(M\) defined as `work` loses the fact that admission decides per stage, and a queue of `work` loses the per-capture unit the single-worker model is built on.
- For the thing that gets skipped, use exactly two names: `optional stage` when the decision unit is meant (the same word the `node` rule mandates), and `optional Draft work` when the aggregate is meant, shortened to `optional work` on re-mention in the same passage. `optional Draft image processing`, `optional image processing`, `optional Draft processing`, and `Draft workload` were the drifted variants and are all resolved into those two.
- **Do not describe a skipped optional stage as masked, hidden, or free.** Sections 2.3 and 2.4 motivate the feature as closing the draft--final visual gap, and post-processing for the target mode is deferred until the application backgrounds, so the Draft image is what the user sees for the whole foreground session; calling the skip invisible concedes that the static level-4 guard was sufficient and dissolves the paper's premise. The two costs are ranked by recoverability, not visibility: the delay lengthens shot-to-shot latency and is never recovered, whereas the skipped stage's fidelity cost ends when the final image replaces the Draft image. For the responsiveness cost use the manuscript's established `user-perceived` wording, not `visible`.
- **Do not use the word "burst" in printed manuscript text**, including section prose, table cells, figure labels, and captions. Replace it with what is actually meant:
  - a temporal grouping of shots — `consecutive captures`;
  - state whose lifetime ends when the Draft task queue drains — `queue-local`, and `persistent across queue drains` for state that survives;
  - a scope bounded by the last drain — `since the queue last drained`;
  - an experimental trial in the evaluation exhibits — `run`, which is what the exhibits already say.
- Exported field names containing `burst` (`burstSpanMs`, `burstDelaySharePercent`, `burstsNeverPaced`) are internal compatibility names, the same treatment the fields containing `required` get. Do not rename them; translate them in prose.
- **Do not use the word "node" in printed manuscript text**, including section prose, table cells, figure labels, and captions. It is an implementation term for an element of the Draft node chain, and the manuscript already calls the same thing a stage. Replace it with what is actually meant:
  - an optional processing step of the Draft Sequence — `optional stage`;
  - the configured ordering of those steps — `stage sequence`, or `Draft Sequence` where the whole path is meant;
  - admission running when execution reaches such a step — `admission at each optional stage`, never `node-time admission`;
  - the admission decision point itself — `admission point`, which Section 3.3 already defines.
- Class names, identifiers, and exported fields containing `node` are internal compatibility names, the same treatment `burst` and `required` get. Do not rename them; translate them in prose. `3_4_admission.tex` and `3_6_implementation.tex` were drafted before this rule and still carry the term; neither is currently included from `_3_approach.tex`, so translate them when they are brought back in.
- Call the controller's policy a **safety-constrained, responsiveness-dominant trade-off**. `timeout > delay > admit` is acceptable when describing the product priority informally, but never translate it into a strict lexicographic optimum: that optimum is the corner solution "delay only as a last resort", which the deployed policy does not implement. Section~4 states the trade-off by name so the four RQs read as its verification.
- Section 3.2 states ordered control priorities and margin dynamics only, and carries no scalar cost objective. A `min Σκ(d_i) + Σ(1-a_{i,j})v_{i,j}` formulation was drafted and rejected for three reasons, all of which still apply: convexity of the delay cost does not imply the split the deployed policy performs, because admission is discrete and its quality cost is a step function; `κ` and `v` appear in neither the implementation nor the evaluation, so the `argmin` reads as ornamental; and `π_i` is a completion-to-completion interval that equals a capture's service demand only while the worker stays busy, which is exactly the condition pacing exists to break. Do not reintroduce anything of that shape.
- Three further claims Section 3.2 must not make, each of which contradicts the implementation or a later subsection: that margin "does not reset" (every capture starts a fresh clock, and the coupling comes from serialized Draft execution); that pacing leaves a remainder to admission (no numeric state passes between the two modules); and that either runtime test is an online form of `μ_i > 0` (`μ_i` is realized only at completion, so the tests are decision-time forecasts against the deadline window each module can still read).
- Overlap between 3.1 and 3.2 is split by rule: 3.1 owns module roles, inputs, integration boundaries, and the asymmetric interaction; 3.2 owns margin dynamics, the two costs, and their ranking. State each fact in exactly one of the two.

## Repository Layout

- Main entry point: `paper.tex`
- Macros and reusable commands: `macros.tex`
- Bibliography: `refs.bib`
- Section files: `_*.tex`, `2_*.tex`, `3_*.tex`, `4_*.tex`, `discussion.tex`, and appendix files.
- Figures: `figures/`
- Reference papers: `references/`

## Build and Verification

- Use the existing `Makefile` first when checking the paper build.
- If the build fails because of local LaTeX tooling, report the exact missing tool or package instead of rewriting unrelated files.
- Do not commit or intentionally edit generated LaTeX artifacts such as `.aux`, `.log`, `.fls`, `.fdb_latexmk`, `.synctex.gz`, or rebuilt PDFs unless the user explicitly requests it.

## Collaboration Rules

- Before broad rewrites, inspect the relevant section files and preserve the author's intended argument.
- Prefer small, reviewable edits over sweeping rewrites.
- For writing tasks, summarize what changed and name the edited files.
- For research-content tasks, distinguish clearly between facts found in the manuscript, in references, and in inference.
