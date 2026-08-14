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
- The Draft Sequence was introduced together with the post-processing pipeline; it publishes an early image and provides recovery while final processing continues.
- The work targets enabling a lightweight multi-frame Draft workload in Portrait mode, whose heavy final composition can then be deferred until the camera app enters the background.
- The proposed system is the Budget-Aware Draft Controller, comprising remaining-sequence admission and capture-availability pacing. Use the descriptive name without a forced acronym and refer to it as ``the controller'' after first use.
- The paper studies coordinated workload and arrival control for tail-latency-based Capture Timeout, not average-latency optimization for a single image-processing stage.
- Preserve the core research framing unless the user explicitly asks to change the problem statement, contribution, or terminology.

## RQ Numbering (changed 2026-08-11)

The manuscript has **four** research questions. The evidence layer under `docs/`, `data/` and `scripts/` still uses the old three-RQ numbering as internal compatibility names — the same treatment the CSV fields containing `required` already get. Translate, do not rename.

| Manuscript | Question | Was | Exhibit | Evidence layer still calls it |
|---|---|---|---|---|
| RQ1 | End-to-end effectiveness | RQ1(a) | `tables/tab_rq1_end_to_end_summary.tex` | RQ1(a) |
| RQ2 | Control-loop contribution | RQ1(b) | `tables/tab_rq2_ablation.tex` | RQ1(b), `scripts/rq1_ablation_metrics.py` |
| RQ3 | Admission decision quality | RQ2 | `tables/tab_rq3_admission_summary.tex` | RQ2, `scripts/rq2_*.py` |
| RQ4 | Pacing-delay sizing | RQ3 | `tables/tab_rq4_pacing_summary.tex` | RQ3, `docs/rq3-*.md`, `data/rq3/`, `scripts/rq3_*.py` |

- **The section below titled "Current RQ3 Evidence Rules" governs what the manuscript now calls RQ4.** Every "RQ3" in it means pacing-delay sizing.
- `docs/rq-restructure-2026-08-11.md` records every column removed in that revision, with its published values and a restore procedure. Consult it before reinstating a column or before quoting a statistic that RQ1 no longer prints.
- RQ4 evaluates whether the proposed controller computes an appropriately sized pacing delay for the Draft backlog and Capture Timeout budget. Do not frame it as a comparison against pacing methods transplanted from other domains unless the user explicitly requests that comparison.
- RQ1 prints $M$, $S$ and Activated as per-run counts, not percentages; RQ2 keeps percentages because its denominator is captures *requested*, not captures present. Do not "unify" the two without reading §2.5 of the restructure document.

## Current RQ3 Evidence Rules

- Treat `docs/rq3-current.md` as the authoritative RQ3 handoff, `docs/rq3-file-manifest.md` as the transfer checklist, and `data/rq3/coordination/README.md` as the generated-artifact dictionary.
- The current main-paper exhibit is `tables/tab_rq4_pacing_summary.tex` alone, and RQ3 ships no figure. The older RQ3 policy, selectivity, and calibration TeX pairs have been deleted; do not restore or reference them.
- RQ3 evaluates trace-derived targeting, admission-aware envelope coverage, work conservation, and responsiveness cost. It does not establish global optimality or a universally minimum counterfactual delay.
- Do not mechanically scale recorded delay by 0.5 or 0.75 on the factual trace. Pacing is closed-loop and changes subsequent backlog, admission, thermal state, throttling, and realized Draft duration; a scaling study requires new matched runs or a validated closed-loop replay/simulator.
- The deployed $2C$ horizon covers the Draft that begins after the pacing decision and the next capture's Draft released by that delay. Pacing deliberately applies half of the positive projected deficit so it does not convert all residual pressure into user-visible delay, relying on node-time admission to skip optional work when its suffix bound exceeds the live budget. This is an intuitive coordination heuristic, not an exact fixed-point derivation or a literal half-deficit transfer to admission. `target-or-next` is an observed admission-action audit over this horizon, not causal attribution of the next decision to the current delay.
- In manuscript prose, call $d^{*}$ the retrospective matched-policy target, not the physically required, minimum, or optimal delay. Existing CSV fields and class keys containing `required` are internal compatibility names for that target and need not be renamed.
- Timeout-labelled records removed from the current collection are known invalid measurements, not actual Capture Timeout outcomes. No valid analyzed run timed out; do not describe this population as survival-conditioned. Document the measurement fault and exclusion manifest when that evidence is accessible rather than inventing details.
- The mandatory floor is a sufficient retrospective reservation condition, not the actual timeout boundary. Because it already excludes optional work, admission demotion documents coordination but does not itself erase a mandatory-floor deficit.
- Every statistic printed beside a population must be computed on that population. In particular, do not explain a `Paced` count with an estimator error measured over the whole class: the class that required no delay is 81% and 78% unpaced, and restricting to the paced decisions changes the backlog error's sign. See the two-block split in `docs/rq3-current.md`.
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

## Banned and Fixed Terminology

- **Do not use the word "burst" in printed manuscript text**, including section prose, table cells, figure labels, and captions. Replace it with what is actually meant:
  - a temporal grouping of shots — `consecutive captures`;
  - state whose lifetime ends when the Draft task queue drains — `queue-local`, and `persistent across queue drains` for state that survives;
  - a scope bounded by the last drain — `since the queue last drained`;
  - an experimental trial in the evaluation exhibits — `run`, which is what the exhibits already say.
- Exported field names containing `burst` (`burstSpanMs`, `burstDelaySharePercent`, `burstsNeverPaced`) are internal compatibility names, the same treatment the fields containing `required` get. Do not rename them; translate them in prose.
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
