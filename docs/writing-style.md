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
-> Capture Timeout and Draft workload
-> limitation of static thermal guards and admission-only control
-> coordinated remaining-sequence admission and capture pacing
-> deadline safety, Draft feature availability, and pacing cost
```

## Paragraph Construction

- Put the paragraph's main claim or function in the first sentence.
- Use the remaining sentences to define, instantiate, contrast, or quantify
  that first sentence.
- Keep one argumentative job per paragraph. Do not combine background,
  mechanism, and evaluation conclusions in the same paragraph unless it is a
  short overview.
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

## Feedback Checklist

When reviewing manuscript text, check the following in order:

1. Can an SEIP reviewer identify the paragraph's purpose from its first sentence?
2. Is the actor, action, object, and causal relation unambiguous?
3. Does the wording match the actual camera-framework behavior?
4. Is every benefit tied to a mechanism or evidence?
5. Does the paragraph connect to the paper's Capture Timeout framing?
6. Are success, failure, and trade-off paths stated symmetrically where useful?
7. Are terminology and capitalization consistent with nearby sections?
8. Can any modifier or repeated phrase be removed without losing meaning?
