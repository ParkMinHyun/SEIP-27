# Writing Style Guide for the SEIP 2027 Manuscript

This guide records recurring writing patterns observed across the following
accepted ICSE papers:

- `references/ICSE25_TOPSEED Learning Seed Selection Strategies for.pdf`
- `references/ICSE26_Enhancing Symbolic Execution with Self-Configuring Parameters.pdf`

Because both papers are coauthored, the patterns below should be treated as a
shared paper-writing style rather than attributed to any one author. Apply the
patterns to form and argumentation, not to technical content.

## Core Argument Rhythm

The papers repeatedly use the following reviewer-oriented progression:

1. Establish the technical setting and its practical objective.
2. Identify a concrete limitation in current practice.
3. Explain why the apparently simple solution is difficult.
4. State the paper's goal in operational terms.
5. Introduce the approach through a small number of named stages.
6. Explain each stage in execution order.
7. Evaluate the main effect, component efficacy, generality, and sensitivity.
8. Close by restating the mechanism and evidence rather than introducing a new claim.

For this manuscript, preserve the corresponding chain:

```text
commercial capture workflow
-> lightweight multi-frame composition in the Draft Sequence as the feature to enable
-> Capture Timeout under parallel capture as the deployment blocker
-> limitation of static thermal guards and admission-only control
-> coordinated remaining-sequence admission and capture pacing
-> deadline safety, Draft feature availability, and pacing cost
```

The chain starts at the feature, not at the failure. `AGENTS.md` states the
same hierarchy as a project rule: the paper enables a feature under a safety
constraint, and is not a timeout-mitigation paper. Text that opens from
"Capture Timeout is the problem" reduces the contribution to mitigation and
should be rewritten.

## Paragraph Construction

- Put the paragraph's main claim or function in the first sentence.
- Use the remaining sentences to define, instantiate, contrast, or quantify
  that first sentence.
- Keep one argumentative job per paragraph. Do not combine background,
  mechanism, and evaluation conclusions in the same paragraph unless it is a
  short overview.
- Open a subsection with a short overview before the first run-in heading,
  stating the premise or the module's role. Sections 3.3 and 3.4 set the
  pattern with two sentences each; 2.4, 3.1, and 3.2 were brought into it on
  2026-08-20 at the same total page count, and 2.4 and 3.1 settled at one
  sentence. One sentence that carries a proposition beats two where the second
  only announces what follows.
- The overview compresses; it does not relocate. Where this guide assigns a
  fact to a named heading block, that block keeps the full statement and the
  overview refers to it at a higher altitude.
- Do not pay for an overview by cutting a conclusion that has to follow its
  evidence. 2.4 briefly lost `a fixed thermal threshold cannot reliably
  identify which captures have sufficient budget`; previewed before the trials
  and absent after them, it left the reader to infer the subsection's own claim
  at the point where the paper should state it.
- Do not preview the run-in headings, as a list or as a plan. Where a
  subsection is short enough to show all of its headings at once, neither
  `we first ... then ... finally` nor `we describe X and measure Y` adds
  anything over the headings themselves: the first announces an order, the
  second announces work, and neither states a fact. Both were drafted here on
  2026-08-20, in 3.1 and 2.4, and both were cut within the day. What the
  overview owes the reader is the subject, not the table of contents.
- An overview sentence must not restate setup that a later paragraph gives
  precisely. 2.4's cut sentence named the measurement axes four lines before
  `Target workload and configuration.` gave the trial count, levels,
  resolutions, and memory conditions in full.
- Prefer explicit transitions that expose the logical relation, including
  `However`, `Specifically`, `For example`, `In contrast`, `As a result`, and
  `To address this`.
- Use transitions only when they encode a real relation; do not add them as
  decoration.
- End motivation paragraphs with the unresolved limitation or design need so
  that the next paragraph has a clear entry point.

## Sentence Style

- Prefer a concrete subject and an active technical verb: `the framework
  executes`, `the controller estimates`, `admission removes`, or `pacing
  delays`.
- State the action before its benefit. Explain the benefit in a following
  clause or sentence when necessary.
- Use short parallel lists for staged algorithms and paired comparisons.
- Define important terms explicitly before using them in reasoning.
- When explaining an algorithm, follow execution order and connect prose to
  figures, equations, or algorithm lines.
- Use present tense for system behavior and paper content; use past tense for
  completed experiments and observations.
- The reference papers commonly use first-person plural for research actions
  (`we present`, `we evaluate`, `we compare`) and system names for mechanism
  descriptions. Follow that division when it improves clarity.
- Avoid ambiguous references such as `this`, `it`, or `the system` when two
  possible antecedents or actors are present.

## Vocabulary and Claim Strength

The papers favor operational vocabulary: `select`, `identify`, `construct`,
`update`, `compare`, `measure`, `cover`, `detect`, and `retain`. Prefer such
verbs over vague claims such as `handle`, `support`, or `improve` without an
object or mechanism.

The reference papers sometimes use strong modifiers such as `novel`,
`significantly`, `substantially`, `remarkably`, and `optimal`. Do not imitate
these automatically. In this manuscript:

- use `significantly` only for a supported statistical result;
- use `optimal` only when optimality is formally established;
- replace promotional modifiers with a concrete mechanism or measured value;
- avoid claiming that a component `improves reliability` when the available
  evidence only shows that it provides a recovery path;
- avoid `immediate` or `real-time` unless the corresponding latency is defined
  or measured;
- distinguish a user-visible early capture result from a mere preview.

## Approach Description

- Begin an approach section with the goal and a compact overview of the named
  control stages.
- Explain what each stage consumes, decides, and produces.
- Follow the same stage order in the overview, detailed algorithm, figure, and
  evaluation.
- Provide intuition after the operational definition, not in place of it.
- Make the interaction between stages explicit. For this paper, admission
  controls current service demand, whereas pacing controls future arrivals.
- State costs alongside benefits. In particular, any pacing benefit must be
  paired with its shot-to-shot latency cost.

## Evaluation Writing

- Start each evaluation subsection by stating what question or property is
  being evaluated.
- Name the compared configurations before discussing results.
- Lead result discussion with the principal aggregate result, then use one or
  two representative cases to explain why it occurred.
- Separate observation from interpretation: first report what the table or
  figure shows, then explain the mechanism that likely produced it.
- Report negative cases, exceptions, variability, and trade-offs rather than
  presenting only favorable outcomes.
- Use ablations to connect each controller component to its intended role.
- Treat generality and sensitivity as separate questions from main
  effectiveness.
- Refer to tables and figures for specific evidence; do not merely repeat all
  cells in prose.

## Adaptation to SEIP

The current paper is an industrial software-engineering paper, not an
algorithm-only research paper. In addition to the patterns above, feedback and
revisions should emphasize:

- the production context and why Capture Timeout is a release-blocking problem;
- the concrete failure mechanism across requests, not only per-stage latency;
- the engineering constraints that rule out superficially simple alternatives;
- the distinction between deployed implementation facts, experimental
  evidence, and paper-level interpretation;
- operational trade-offs, especially Draft feature availability versus
  shot-to-shot latency;
- actionable lessons that can transfer beyond this one camera framework
  without overstating generality.

## Section-Level Constraints

Some sections carry constraints that are not style preferences but records of
decisions already taken and mistakes already made. They used to live as comment
headers inside the section files. `AGENTS.md` is the authority for all of them;
this section records where each one applies so a reviewer can check a section
without rereading every rule.

### Section 2.4, internal ordering

2.4 carries two run-in headings. `Production static thermal guard.` covers the
level-4 safeguard, why it applies uniformly, and the two things the level cannot
reveal. `Required runtime control.` covers everything after it: the \(M\)/\(S\)
notation, the trial configuration, `tab_timeout_index`, the evidence on both
sides of the threshold, why neither naive alternative suffices, and the closing
requirement.

It carried three until 2026-08-21, when `Target workload and configuration.`
was merged into what followed it. The old boundary fell between an experiment
and its own findings: the first three sentences under `Required runtime
control.` report what the trials showed, not what is required, so neither
heading covered them. Merged, the block runs setup, table, evidence, goal, and
2.4 lands Section 2 on the requirement Section 3 answers.

The two headings are meant to be read as an opposition, which is why the first
one carries `static` even though the subsection title already says it. They line
up on three axes -- what ships against what is needed, static against runtime,
a guard that blocks against control that modulates -- and static-against-runtime
is the axis the framing hierarchy in `AGENTS.md` itself turns on. A reader who
skims only the run-in headings gets 2.4's argument in two lines. That is worth
more than avoiding the two-word echo of the title, and the echo also fixes the
gating of the title to the guard of the block as the same thing.

Shortening the first heading cost one underfull hbox, and `paper.tex` now
carries `\hyphenation{light-weight}` because of it. The merged block's first
line reads `Required runtime control. We denote the candidate` at 218.9pt
against a 252.0pt column, and the next word, `lightweight`, has no hyphenation
point in TeX's English patterns, so adding it overshoots to 268.0pt. The line
was all-or-nothing on an eleven-character block and TeX stretched it, badness
2875. The longer heading had hidden this by pushing `candidate` off the first
line entirely. Neither `\hyphenpenalty` nor `\emergencystretch` was involved --
both were checked -- and the exception is the fix rather than a reworded
sentence or a heading chosen for its length. It applies to all four places the
manuscript writes `lightweight`.

Do not unify `static`, `fixed`, and `uniform` in this subsection: they name
three different properties. `uniform` is applied identically across device
models, `fixed` is the threshold value not moving off level 4, and `static` is
not adapting to runtime state. Only the third is what the controller replaces.

Three things not to do to the merged block.

- Do not rename it `Target workload and control objective.`. Section 3.1's own
  run-in heading is `Control objective.`, and duplicating the phrase makes 2.4
  look like it states the objective 3.1 owns.
- Do not soften the closing sentence. `coordinated runtime control that scales
  each capture's Draft work to its remaining budget and derives
  capture-availability pacing from the admitted backlog and the live deadline
  window` is the last step of the framing hierarchy `AGENTS.md` pins; it reads
  as specific because the handover to Section 3 is what it is for.
- Do not trim the setup sentences as redundant with the evaluation.
  `_4_experiments.tex` carries no setup description at all -- it goes from the
  RQ list straight to RQ1 -- so this block is the manuscript's only account of
  the device, the trial protocol, and the \(M\) versus \(M+S\) comparison.

### Section 3.1, internal ordering

3.1 and 3.2 were merged into `3_1_overview.tex` on 2026-08-15 and the workload
model became 3.2. The two used to be split, with a rule policing which
subsection owned which fact, and both opened on the same premise. The merged
subsection is ordered by run-in headings:

- the opening paragraph for what the controller is;
- `Controller architecture.` for the two modules and the integration
  boundaries;
- `Control objective.` for the hard constraint, the recursion, the two levers it
  exposes, the asymmetric interaction between them, and which of the two costs
  the policy prefers.

The two headings map onto the two halves of the subsection title. There were
three until 2026-08-21, when `Safety and responsiveness.` and `Cross-shot margin
dynamics.` were merged. The pair delay/skip crossed that heading boundary twice
-- once named as the two product costs, once as the two levers on the terms of
the recursion -- so the second block re-introduced what the first had just
introduced.

Inside the merged block the order is load-bearing: the constraint, then the
recursion, then the levers with the asymmetry, then the identity-not-a-control-law
caveat, and the cost ranking last. The caveat has to separate the equation from
the ranking. The responsiveness-dominant preference is a product priority, and
placed directly after the equation it reads as a consequence of it -- which is
the misreading the old heading boundary used to prevent, and is the same
lexicographic-optimum reading `AGENTS.md` bans elsewhere. Ending on the ranking
also leaves the block on the named trade-off, which is the sentence
`_4_experiments.tex` cites.

Keep the headings short enough to match the ones in 2.3 and 2.4, and do not name
this subsection for the two modules -- `Remaining-Sequence Admission` and
`Admission-Aware Capture-Availability Pacing` are the titles of 3.3 and 3.4, and
a title like `Coordinated Admission and Pacing` here promises their detail two
subsections early. `Cross-shot` is the manuscript's fixed term; do not write
`cross-capture`.

The adjective `cross-shot` attaches to the contention, not to the constraint.
Section 2.2 is titled for cross-shot deadline *contention*, and 3.1 does not use
the adjective at all: its recap sentence reads `This constraint spans captures:`.
That subject is consistent because the sentence before it states the constraint
at stream level -- `avoiding Capture Timeout`, not a per-capture deadline -- so
the clause after the colon, `each capture has its own Capture Timeout window`,
enumerates the constraint's instances rather than contradicting its scope. The
coupling itself comes from the clause after that, the single worker.

Two forms were tried on 2026-08-21 and rejected. `The constraint is cross-shot:`
puts the adjective on the wrong noun. `Enforcing this constraint is cross-shot:`
puts it on the right one but reads awkwardly, since `cross-shot` modifies nouns
like contention or window comfortably and a gerund badly. The cost of the
surviving form is that `cross-shot` now appears only in Section 2.2, which is
acceptable: 2.2 introduces and explains the concept, and 3.1 only recaps it
before the recursion formalizes it. `cross-capture` remains banned outright.

State each fact exactly once, and keep the asymmetry beside the levers rather
than in the opening, so that stretch reads as identity, then levers, then what
the levers cannot do.

Each lever gets exactly one limit there, and it is that lever's own past:
admission cannot restore consumed budget, pacing cannot alter work already in
progress. Those two are what justify `act prospectively`, and keeping them
parallel is the point. Until 2026-08-21 admission also carried `or revise a
scheduled delay`, which reads as a limit on the wrong module -- revising a
delay is pacing's business, and `3_4_pacing.tex` owns that fact, where a
committed delay going unrevised is the reason pacing needs the high-side
reserve. It also arrived before its motivation: the irreversibility of delay is
what ranks the two costs, and the cost sentence two lines later already carries
it with `irreversibly`. Do not restore it, and do not add its mirror image to
pacing either; a lever's inability to undo the *other* lever's committed
decision is not a fact 3.1 needs.

The opening must anchor to keeping the Draft Sequence's lightweight multi-frame
composition available, which is where Section 2.4 hands over; Capture Timeout is
the safety constraint on that goal, not the goal itself.

`Controller architecture.` must say that the shared estimates are *learned* from
observed durations, and that the update lands at Draft Sequence completion. The
block said only `share runtime state and online estimates` until 2026-08-21, and
`online` alone reads as "computed at runtime", which a per-model timing table
would also satisfy -- so the sentence asserted the sharing while leaving out the
mechanism that produces it. In the implementation each stage's duration is
buffered as it finishes and the models are updated in one place,
`completeDraftSequenceExecution`, which feeds the admission-side predictor and
the pacing-side context from the same measurements; that single hook is why the
two modules can be said to share estimates at all. Name both granularities,
per-stage and whole-sequence: 3.2's per-key point estimate and 3.4's reserve
draw on the two separately, so the overview is where the distinction is planted.
Do not trim the clause as redundant with 3.2's opening -- 3.2 says where the
estimates come from, 3.1 says that the two modules share one source.

The opening and the `Control objective.` block name different scopes, and the
difference is load-bearing. The opening names the feature being enabled, the
lightweight multi-frame composition -- \(M\) alone. The constraint sentence
names what the controller executes at runtime, which is all **optional
stages**, \(M\) and \(S\) together: admission replaces the level-4 thermal
guard, and that guard suppressed both (Section 2.4), so both are what admission
now decides per capture -- `3_3_admission.tex` rejects "an \(M\) or \(S\)
stage", and `3_5_implementation.tex` states the replacement in those terms.
Narrowing the constraint sentence to the multi-frame stage was tried on
2026-08-21 and is wrong twice over: it understates admission's scope, and
`lightweight` does not even single \(M\) out, since the single-frame stages of
\(S\) are lightweight too. Write it as Section 2.4's handover sentence does --
`optional stages ... whenever safely possible` -- which is also the bare form
`AGENTS.md` mandates for every verb that acts on the decision unit, and the
phrase the rest of Section 3 already uses throughout.

`\label{sec:objective}` belongs on the `\subsection` line. `_4_experiments.tex`
references it, and a `\label` placed after a run-in heading is not attached to a
numbered unit -- it silently anchors to the preceding float.

The controller overview `figure*` is declared immediately after that `\label`,
before the opening paragraph, and should stay there. A double-column float
cannot be placed on the page LaTeX is already building, so its declaration point
is a floor on where it can land. Declared after the opening paragraph instead,
it dropped to page 4 while the sentence citing it stayed on page 3; moved to the
top of the subsection it lands on page 3 with that sentence, at the same total
page count.

The `Control objective.` block must not describe a skipped optional
stage as masked, hidden, or otherwise free. Sections 2.3 and 2.4 motivate the feature as closing the draft--final
visual gap, and for the target mode post-processing is deferred until the
application backgrounds, so the Draft image is what the user sees for the whole
foreground session. The asymmetry that ranks the two costs is recoverability,
not visibility: the delay is never recovered, whereas the skipped stage's
fidelity cost ends when the final image replaces the Draft image.

### Section 3.1, claims that must not be made

Each of the following contradicts the implementation or a later subsection.

- That margin "does not reset". Every capture starts a fresh Capture Timeout
  clock; the cross-shot coupling comes from serialized Draft execution, where a
  predecessor can hold the worker past the next capture request.
- That pacing leaves a remainder for admission to consume. No numeric state
  passes between the two modules: admission runs its own live-budget test for
  each optional stage, and pacing converts a fixed fraction of its own
  projected deficit into delay.
- That either runtime test is an online form of the margin condition. The
  realized margin exists only at completion, so both tests are decision-time
  forecasts against the deadline window each module can still read.

A scalar cost objective of the shape `min` over a delay cost plus a skipped-work
penalty was drafted for this subsection and rejected; `AGENTS.md` records the
three reasons, all of which still apply. Do not reintroduce anything of that
shape.

### Section 3.1, load-bearing phrasing

- Keep `deadline-constrained, responsiveness-dominant trade-off` verbatim.
  Section 4 opens by citing it by name, so rewording it breaks the reference.
  This line read `safety-constrained` until 2026-08-21, disagreeing with
  `AGENTS.md` and with both places the manuscript prints the term; the
  qualifier is `deadline-constrained` because the compressed label is reused
  pages later in Section 4 with no context, and the paper has a second safety
  notion in scope -- the static thermal guard of Section 2.4 -- that
  `safety-constrained` would not distinguish it from. Changing it is a
  three-file edit: `3_1_overview.tex`, `_4_experiments.tex`, and `AGENTS.md`.
- Do not restate the priority ranking as a strict lexicographic optimum
  ("timeout first, delay second, optional work third"). That corner solution is
  "delay only as a last resort", which the deployed policy does not implement:
  pacing converts only part of the projected deficit into delay.

### Section 3.4, backlog-tracking order

Section 3 uses \(T\) for the live remaining Capture Timeout window in both
control modules. Admission reads \(T_{i,j}\) for capture \(i\) at admission
point \(j\). After capture \(i\), pacing makes its decision at \(t_i\), reads
the newest committed capture's remaining window as \(T_i\), and applies the
resulting \(d_i\) to the next capture opportunity. The shared letter identifies
the common deadline-window concept; the decision point identifies the reading.
Do not restore admission's former \(R_{i,j}\) notation.

`Backlog tracking.` is ordered representation, clock and Equation 7, the
per-capture extension and Equation 8, the gloss on \(\hat P^{\mathrm{last}}\)
and on the maximum, repeated extension, rebase.
Restructured 2026-08-23 over two passes. Before that, Equation 8 came
immediately after Equation 7, so the provisional estimate was the first thing
said about how \(t^{\mathrm{end}}\) advances and the general construction was
never stated.

Three facts about \(t^{\mathrm{end}}\) are easy to state wrongly, and each was
stated wrongly in some draft of this block:

- \(t^{\mathrm{end}}\) is a timestamp, not \(\sum\hat P\). It is an
  execution-time anchor plus accumulated predicted work, so write that the clock
  *carries* one predicted Draft processing time per unfinished capture,
  *accumulated along the Draft-worker timeline* -- never that it is the sum of
  the point predictions. Each rebase resets the anchor and thereby drops timing
  error from completed sequences; prediction error in the provisional point
  estimates still stored for later captures can accumulate with queue depth.
- The representation sentence names an amount, not a position. `predicted Draft
  processing time` is what the backlog is; `predicted time on the Draft-worker
  timeline` was tried on 2026-08-23 and reverted, because a time *on* a timeline
  reads as a point, which describes \(t^{\mathrm{end}}\) rather than
  \(\hat B_i\), and the duration/timestamp split is the one distinction the rest
  of the block depends on. The timeline belongs in the next sentence, where the
  clock's contents are given. Contrast with `Draft Sequence queue depth`, not
  bare `queue depth`: that is the y-label of `figures/fig_casestudy_12mp.tex`.
- Not every capture on the clock is priced by its own estimate, and there is no
  operation that prices one that way on its own. Between rebases every queued
  capture carries \(\hat P^{\mathrm{last}}\); a resolved estimate enters only
  when a Draft Sequence starts and the rebase runs. So the two-tier fact belongs
  in the rebase sentence, as `resolved point estimate` against `provisional
  estimates already stored`, and not as a standing rule before Equation 8. A
  draft sentence reading `A Draft Sequence that has started contributes its own
  point estimate` was cut on 2026-08-23 for asserting an operation the
  implementation does not have. Verified against `ML@898ae37`:
  `queuePacingDecision` advances the clock by the snapshot current at the
  decision, which is the last started sequence's, and `rebaseBacklogClock`
  prices the starting sequence from its own resolved key while summing each
  queued decision's stored snapshot.

Two sentences carry facts a reviewer would otherwise have to reconstruct, and
neither is filler:

- `since the capture cannot be requested before its callback is released` is the
  reason for the maximum. A version that read `the maximum anchors the extension
  at the later of the current drain time and the callback release` was reverted
  the same day: it verbalizes \(\max(a,b)\) and drops the justification, leaving
  a sentence that could be deleted without loss.
- `Several decisions may extend the timeline before the next Draft Sequence
  starts` is why more than one provisional estimate can be stored at once, and
  it carries the parallel-capture premise that the block's opening sentence used
  to state directly. It replaced `Under parallel capture a callback can be
  released before the preceding capture's Draft Sequence starts, so pacing
  predicts the backlog`, which said the same thing before the reader had the
  clock to attach it to.

`At each Draft Sequence start` is deliberately unqualified. It read `At each
Draft Sequence start whose workload sequence the controller can price` until
2026-08-23, which understates when the rebase happens: a start with no
predictable workloads still rebases, contributing zero point work, so the
qualifier scoped the whole sentence to protect one clause. That case is a JPEG
passthrough the manuscript's workload model does not admit, and it is not worth
a sentence.

The subsection overview says `using predicted time` and stops there. It carried
`rather than queue depth` until 2026-08-23, which placed the block's own
contrast five lines above the sentence that defines it; the overview refers, the
block states.

Known gap between Equation 8 and the implementation, as of `ML@898ae37`:
`queuePacingDecision` advances the clock by the point work *plus* a learned
between-stage overhead (`draftSequenceOverheadDurationMs`) that 3.2's
\(\hat P\) does not model, so Equation 8 understates the real advance by that
term. Adding it needs a new symbol in 3.2, which is a modeling decision rather
than a wording one. An uncommitted working-tree edit removing that term from
`rebaseBacklogClock` was present on 2026-08-23; if the term is dropped from both
clock operations, delete this paragraph rather than editing Equation 8.

### Section 3.5, scope of the integration report

3.5 exists to answer four reviewer questions and nothing else: where the
controller attaches, what deploying it costs, how it relates to the static
safeguard the evaluated build replaces, and what a recorded decision means. On
2026-08-20 the subsection was trimmed to those four, after review feedback that
its edge-case detail diluted the facts a reviewer has to carry into Section 4.

The overview is two sentences, matching 3.3 and 3.4.

The first states three things and each one is load-bearing. `the framework's
existing decision points` asserts that the framework already decided at both
sites, which is what makes 2.4 hand over to 3.5: the static level-4 guard was a
decision at the same place admission now decides, and the APM policy hook was
already the mechanism for deciding when to release the callback. Both sites are
pre-existing framework code (`ApmPolicy`, `ApmPolicyManager`, and the untouched
Draft node-chain accessor in `ML@cdd524f`). `preserving its ownership and
execution structure` is the claim that survived deleting the old topic sentence
`Two existing ownership points host the controller` -- keep the claim, not the
announcement. `without introducing new cross-layer interfaces` is sharper than the
earlier `not new interfaces` because 2.1 established the cross-layer workflow as
the expensive surface, and it confirms at implementation level what 3.1 promised
about HAL and application interfaces. If the implicit claim in `decision points`
ever has to go, `extension points` is the neutral fallback.

The second gives the engineering reason the change is scoped narrowly: the
revalidation cost 2.1 establishes. Do not restore the form `Because it must be
deployable in a commercial product` -- restructuring the framework would also be
deployable, so deployability does not entail a minimally scoped change and the
sentence read as a non sequitur. Revalidation cost does entail it.

Neither sentence was lifted from the block below, so nothing there became
redundant -- `one scheduler thread, no additional Draft worker, no persistent
controller state` and the per-device-constant sentence remain the precise
statements the overview refers to. If the overview ever has to carry a body fact,
the one candidate is the `has not yet shipped in a commercial release` clause,
which currently rides on the thermal-guard sentence and is not part of that
sentence's claim; moving it up would also foreground the paper's weakest fact,
which is a rhetorical choice rather than a fix.

Removed then, and not to be restored:

- The destination of a rejected Draft Sequence submission (a shared executor, still
  profiled and admitted). Rejection happens only at pipeline close, so the
  detail describes teardown, and naming a second executor invites the reader to
  doubt the single-worker model that 3.2 and 3.4 are built on. The load-bearing
  clause is `cannot be rejected under queue pressure`; keep that.
- That pacing commits its clock update at decision time, so an unhonored delay
  can leave the backlog clock late. 3.4 already states that each Draft Sequence
  start the controller can price rebases the clock from the actual start and
  discards the accumulated error, which is the same fact at the altitude 3.4
  owns.
- A standalone sentence separating an offered capture opportunity from a taken
  one. It was the third statement of that limit, after 3.1's definition of
  pacing and the instrumentation sentence; it now rides along in the
  instrumentation sentence as the second reason \(d_i\) is not realized waiting.
- The per-sequence hook that bound the configured workload sequence to
  admission, watchdog handling, and model updates. Removed on 2026-08-21: it
  was not one of the two attachments the cost sentence counts but a wiring
  detail inside the first, and it stood between them. Each of the three things
  it named is owned elsewhere -- admission at each optional stage by 3.3's
  opening sentence, the watchdog by 3.3's `Watchdog fallback.` block, model
  updates by 3.2 -- so the only new fact was that one site binds all three,
  which carries no cost, safety, or evaluation consequence and is referenced
  nowhere else. With the class name barred, `a hook binds` also left the reader
  nothing checkable.

The block reads as attach, then cost, then replace, and the connectives that
carry that order are load-bearing. `Together, the two attachments` ties the cost
sentence to the two host sentences before it; `one scheduling thread for that
deferred release` names what the thread is for, which is the first thing a reader
asks and answers it by pointing back at the pacing sentence; `also removes` marks
the guard replacement as a further property of the evaluated build. Do not strip
them as filler. The shipping status is its own sentence: spliced onto the
thermal-guard sentence with a semicolon, it read as part of that sentence's claim
when it is an unrelated status statement.

Two wordings the trim broke and a follow-up pass repaired, both worth keeping as
they now stand:

- Name the two submissions. Once the Draft Sequence fallback sentence went, `both
  of its submissions` had no antecedent within the block: only the delay was named
  afterwards. The block now says `neither its Draft Sequence submission nor its
  delay request`, so it is self-contained; do not collapse it back to `both`
  or to a bare `controller submissions`, which drops the fail-open claim's scope.
- The immediate paths `commit no pacing decision`, not `no decision`. Those
  captures still produce admission decisions in the trace; only the pacing
  record is absent, which is what a reviewer checking a paced-fraction
  denominator needs to know. Verified against `ML@cdd524f`:
  `sendCaptureAvailableImmediately` and `sendCaptureAvailable(CaptureMetadata)`
  never reach the policy, while the two policy call sites run the callback
  inline when `policy.execute` returns false, so `releases the callback
  immediately` is literal.
- `runs at that level` rather than `runs there`. The nearest antecedent for
  `there` was the guard, not level 4.

Kept deliberately, against the same feedback:

- ~~`which serializes concurrent callbacks`~~. Argued for and then removed the
  same day: callback arrival is sequential even under parallel capture, so the
  two-callbacks-under-price story was wrong. The pacer's lock is real and every
  entry point carries it, but what it serializes is the callback decision against
  the Draft-start rebase, the completion update, and the deadline update, which
  arrive on other threads. That is implementation hygiene, not a fact a reviewer
  needs. Do not restore either version.
- `no additional Draft worker`. The Draft executor already exists; the claim is
  that integration adds none. `no Draft worker` would deny the single-thread
  executor that 3.2's workload model assumes.
- ~~The enumeration `overheat level, memory, and CPU are recorded for analysis
  only`~~. Also removed the same day. The load-bearing half is that no
  device-state signal reaches control, and the sentence about removing the static
  level-4 thermal guard two lines below already supplies the contrast with 2.4;
  the list of logged signals belongs to the evaluation, which can license its own
  analysis variables. `neither module consumes a device-state signal for control`
  is the surviving claim.
- The full instrumentation enumeration, including `watchdog state`. The next
  sentence claims the evaluation can separate model decision quality from sticky
  demotion and watchdog enforcement, which only the enumeration supports.
- That next sentence's purpose clause, though its cross-reference to the
  evaluation section was dropped on 2026-08-20. Without the clause, `recorded
  separately from the enforced action` is inert bookkeeping inside 3.5; cutting
  the whole sentence instead would strand RQ3's always-admit audit sentence,
  which presupposes that the trace distinguishes recommendation from enforced
  outcome and is licensed nowhere else.

Both of 3.5's remaining section cross-references were removed on 2026-08-20: the
opening sentence no longer points at 2.1 for the framework, and the
instrumentation sentence no longer points at the evaluation section. The last
one, to 2.4's static guard, went on 2026-08-21: the sentence now calls it `the
existing static level-4 thermal guard`, which carries the same claim --
that the evaluated build replaced a safeguard already in production -- without
sending the reader back a section for it. 3.5 now makes no section reference at
all.

Both `2_1_release_process.tex` and `2_4_static_safeguards.tex` keep their
labels (`\label{sec:release-process}`, `\label{sec:guard-limit}`); an
unreferenced label is silent, and a later section may need it.

### Section 3.5, naming the integration points

3.5 must not name the implementation's components. A first draft described the
integration as `the Draft-saving manager owns the predictor, the admission
policy, and the pacer, and still executes Draft Sequences on its single-thread
executor`, with `a per-Draft-task profiler`, `the application-facing
capture-availability policy`, `the pacing decider`, and `a delayed scheduler`
after it. Every one of those is a class or field name in `ML@cdd524f`
(`SavingDraftImageTaskManager`, `draftSequenceExecutionPredictor`,
`admissionPolicy`, `captureAvailablePacer`, `savingDraftImageThreadPool`,
`DraftSequenceExecutionProfiler`, `CaptureAvailableApmPolicy`,
`CaptureAvailablePacingDecider`, `SingleThreadDelayedScheduler`), and the
sentence reproduced the manager's field-declaration order. They were removed on
2026-08-20.

The problem is not only disclosure. Those nouns appeared in no other manuscript
file: 3.1 names the two modules *Remaining-Sequence Admission* and
*Capture-Availability Pacing*, 3.2 says `the controller` and `the estimator`,
and 2.2--3.4 say `single worker`, never `executor`. A reader met `manager`,
`predictor`, `pacer`, `decider`, and `profiler` for the first and only time in
the last subsection of Section 3, where they read as a fourth vocabulary for
things already named twice.

Name integration points by the role Section 3 already gave them:

- the host component by what it owns -- `the framework component that already
  owns the single Draft worker` -- not by a component name;
- the two modules as `both modules`, or as `admission` and `pacing`, the words
  3.3 and 3.4 use as agents;
- the estimator as `the estimator they share`, which is 3.1's `share runtime
  state and online estimates` at noun altitude;
- the callback site as `the application-facing capture-availability path`;
- the deferral as `defers callback release by the computed \(d_i\)`, stating the
  effect rather than the mechanism that produces it.

Two terminology consequences of the same pass. The queue unit is `Draft
Sequence`, so `Draft-task submission` became `Draft Sequence submission`; `Draft
task` was a fourth name for the unit the three-level rule already fixes.
`the two-Draft horizon` became `the two-sequence reserve horizon`, matching
3.4's `per-Draft-Sequence reserve` and `two future Draft Sequences` -- `Draft`
is not a count noun anywhere else in the manuscript.

Generic engineering vocabulary is still fine, and the overview figure uses it:
`one scheduling thread` states a deployment cost and names nothing. What is
banned is a noun a reader could only have gotten from the source tree.
`Whether a requested delay was honored is not persisted` replaced `Scheduler
acceptance is not persisted` for that reason and because, once the scheduler
went, `Scheduler` had no antecedent.

The integration cost claim is `no persistent controller state`, not `no
persistent storage`. The evaluated build does persist: the metrics store is a
Room database with an export worker, added to extract the study's traces and to
be removed before deployment. Read against the instrumentation paragraph three
lines below, the unscoped `storage` wording reads as a contradiction; the scoping
word is what closes it.

Do not close it a second time by stating in 3.5 that the recording path is
study-only. A sentence to that effect was added on 2026-08-20 and cut the same
day: once the cost claim names controller state, the sentence buys only the
deployment-cost point, and that belongs with the other measurement caveats in
Section 4's threats to validity, which is also where the no-formal-guarantee
paragraph moved. The supporting implementation fact, if that paragraph ever needs
it: `DraftSequenceExecutionProfiler` groups its state by destination, where
`modelUpdate` holds what the predictor learns from and `metricsRecorder` is the
sole writer of the metrics store, and the two are written at disjoint call sites
(`ML@cdd524f`). The per-Draft device-state read belongs to the recording path for
the same reason, so the enumerated signals cost nothing in a deployed build.

The `Instrumentation.` block itself stays. Section 4 already depends on it: RQ2
reads the recommendation-versus-enforced split, RQ3 labels each decision
retrospectively from the realized trace, and RQ4's delay numbers rest on the
requested-versus-realized semantics sentence. Deleting the block would leave
Section 4 asserting a data source the paper never defines.

## Feedback Checklist

When reviewing manuscript text, check the following in order:

1. Can an SEIP reviewer identify the paragraph's purpose from its first sentence?
2. Is the actor, action, object, and causal relation unambiguous?
3. Does the wording match the actual camera-framework behavior?
4. Is every benefit tied to a mechanism or evidence?
5. Does the paragraph connect to the paper's framing, in which multi-frame
   Draft composition is the feature and Capture Timeout is the constraint?
6. Are success, failure, and trade-off paths stated symmetrically where useful?
7. Are terminology and capitalization consistent with nearby sections?
8. Can any modifier or repeated phrase be removed without losing meaning?
