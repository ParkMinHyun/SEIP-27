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
- The proposed system is currently framed as the Context-Aware Draft Sequence Controller, comprising remaining-sequence admission and capture-availability pacing.
- The paper studies coordinated workload and arrival control for tail-latency-based Capture Timeout, not average-latency optimization for a single image-processing stage.
- RQ3 evaluates whether the proposed controller computes an appropriately sized pacing delay for the Draft backlog and Capture Timeout budget. Do not frame RQ3 as a comparison against pacing methods transplanted from other domains unless the user explicitly requests that comparison.
- Preserve the core research framing unless the user explicitly asks to change the problem statement, contribution, or terminology.

## Current RQ3 Evidence Rules

- Treat `docs/rq3-current.md` as the authoritative RQ3 handoff, `docs/rq3-file-manifest.md` as the transfer checklist, and `data/rq3/coordination/README.md` as the generated-artifact dictionary.
- The current main-paper candidates are `tables/tab_rq3_pacing_compact.tex` and `figures/fig_rq3_pacing_compact.tex`; preserve the older RQ3 policy, selectivity, and calibration pairs as untouched historical alternatives.
- RQ3 evaluates trace-derived targeting, admission-aware envelope coverage, work conservation, and responsiveness cost. It does not establish global optimality or a universally minimum counterfactual delay.
- Do not mechanically scale recorded delay by 0.5 or 0.75 on the factual trace. Pacing is closed-loop and changes subsequent backlog, admission, thermal state, throttling, and realized Draft duration; a scaling study requires new matched runs or a validated closed-loop replay/simulator.
- The deployed $2C$ horizon covers the Draft that begins after the pacing decision and the next capture's Draft released by that delay. `target-or-next` is an observed admission-action audit over this horizon, not causal attribution of the next decision to the current delay.
- Timeout-labelled records removed from the current collection are known invalid measurements, not actual Capture Timeout outcomes. No valid analyzed run timed out; do not describe this population as survival-conditioned. Document the measurement fault and exclusion manifest when that evidence is accessible rather than inventing details.
- The mandatory floor is a sufficient retrospective reservation condition, not the actual timeout boundary. Because it already excludes optional work, admission demotion documents coordination but does not itself erase a mandatory-floor deficit.


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
