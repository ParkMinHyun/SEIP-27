# Writing Style: Professor's Section 2.1 Revision

## Authority and scope

This guide is based on the professor's revision of
`2_1_release_process.tex` in commit
`c5c4532000a18ddfd8fe7131a14f9b70d4fb187a`, compared with its parent,
`ad1b6c8f66cced0c459786a090df7193f450f062`.
The user designated this revision as the model for rewriting Chapter 2 on
2026-09-05.

This file replaces the previous writing-style guide in full. The previous
reference-paper synthesis, section-specific prescriptions, and revision
history are no longer writing instructions. Do not recover them from Git
history or use the PDFs in `references/` as a competing style authority unless
the user explicitly requests that. `AGENTS.md` remains authoritative for the
research framing, technical facts, evidence limits, and established terminology.

The sample establishes an explanatory style for industrial background and
motivation. It does not establish a template for the abstract, evaluation,
related work, captions, or the entire paper. Apply the observed principles
where they help readers understand the argument; do not invent rules for
parts of the paper the professor has not revised.

## What the professor changed

The revision retains the two-block structure but expands the body from seven
sentences to ten: the opening paragraph grows from four to five sentences,
and the Capture Timeout block from three to five. Its main effect is to make
the explanation easier to follow, not to minimize its length.

| Aspect | Before the revision | In the professor's revision | Lesson supported by the change |
| --- | --- | --- | --- |
| Subsection title | `Production Release Process and Capture Reliability` lists two topics. | `Image Capture Reliability` names the central subject. | Name the subject the reader needs to understand rather than enumerate the subsection's contents. |
| System context | Enumerates Samsung-specific extensions, services, vendor components, and companion applications. | Explains that image capture spans system-level components across the Android stack. | Preserve the relationship that motivates the argument; omit a component inventory when its individual entries do no explanatory work. |
| Consequence of failure | Contrasts a firmware update with an application-only fix and explains revalidation in the next sentence. | Connects a late failure directly to firmware-level changes, coordination, and revalidation. | Keep the practical consequence close to the fact that causes it. |
| Daily validation | Introduces testing through the cost of firmware updates and calls it black-box testing. | States its purpose directly: detecting capture failures early. | Explain why an activity is performed before adding details about how it is classified. |
| Additional validation | Starts with `Periodically`. | Starts with `In addition to this daily testing` and explicitly includes root-cause diagnosis. | Explain how the next activity complements the one already introduced. |
| Paragraph ending | Ends with the list of stress-testing activities. | Adds `Together, these activities` and identifies their common role in capture reliability. | State what the preceding details amount to when that prepares the next concept. |
| Timeout introduction | Leads with `high-priority ... KPI` and `hard release gate`. | Connects to `this validation process`, describes a fixed internal deadline, and names Capture Timeout. | Introduce a concept through its meaning before explaining its organizational importance. |
| Timeout completion | Includes frame and metadata collection as well as Draft image production. | Describes completion through production of the initial user-visible draft image. | Use the detail needed at this point in the explanation; this edit is not evidence that the implementation's completion conditions changed. |
| Consequences of a violation | Packs a fail-fast crash, observability, release blocking, and corrective action into one sentence. | Explains the intentional crash and its testing purpose, then release blocking and corrective action in a separate sentence. | Separate consequences that answer different reader questions. |
| Closing significance | Ends with correcting the cause or restricting the feature. | Adds why resolving violations matters in camera development. | Make the importance of the background explicit after explaining the mechanism and its consequences. |

The first paragraph follows this progression:

> Image capture spans components -> late failures require coordinated changes
> -> daily testing detects failures early -> stress testing complements it
> -> together these activities validate capture reliability.

The second block starts from that established context:

> This validation process -> a named deadline -> its clock behavior
> -> how a violation becomes observable -> how it affects release
> -> why resolving violations is an important development task.

## Principles for subsequent writing

### Explain relationships in the order the reader needs them

Start from a concrete setting or an already established concept. Define the
new concept, explain its operation, and then state its consequences and
significance. A reader should not have to infer a mechanism from an early
label such as `hard release gate`. Give enough context to follow the local
argument; defer a concept's internal details once its role is clear.

Connect paragraphs through a specific idea already introduced. The
professor's `in this validation process` is effective because it names the
relationship to the preceding paragraph, not merely because it is a
transition phrase.

### Make causes, purposes, and consequences explicit

The revision uses `Consequently`, `To detect`, `In addition`, `Together`, and
`Therefore` to distinguish consequence, purpose, addition, synthesis, and
implication. Use a connective when that relationship is present. These words
are examples, not a mandatory list or a required sequence.

When introducing an engineering action, explain what it accomplishes in the
local argument. When introducing a constraint, explain what happens because
of it. Prefer that explanation to a compressed management or implementation
label that assumes the reader already knows its significance.

### Reduce information density without deleting the argument

Keep a sentence focused enough that its role is apparent. Separate a runtime
effect from an organizational consequence when combining them obscures either
one. A longer sentence is still appropriate when its clauses explain one
causal chain, as in the professor's description of firmware-level changes.

Do not remove essential setup, evidence, or an engineering reason merely to
shorten the text. The removed component list and the added explanatory
sentences serve the same objective: readers receive the information needed
to understand the next step, at the point where they need it.

### Use repetition when it makes the explanation traceable

The professor repeats `capture failures`, `validation process`, `reliability`,
and `violation`. Reusing an established term can make the subject clearer
than replacing it with a synonym or an ambiguous pronoun.

A paragraph may close by stating the common role or practical significance of
its details. Such a sentence earns its place when it synthesizes them or
prepares the next paragraph. Do not add a generic importance claim to every
paragraph or remove a useful synthesis merely because it revisits a concept.

### Choose headings for their actual content

The shortened subsection title identifies one central subject. The retained
`Capture Timeout.` heading introduces a defined concept. Use headings to help
readers identify what the following text explains. Let the amount and function
of the material determine the number of headings and paragraphs.

The sample supplies no rule requiring a one-sentence overview, a fixed number
of run-in headings, or a particular heading arrangement in other subsections.

### Preserve technical meaning while changing presentation

Retain the manuscript's established research goal, terminology, symbols,
labels, experimental settings, and supported findings. Distinguish background
reported by the authors, behavior verified in the implementation, observations
in an exhibit, and the interpretation drawn from those observations.

Do not generalize incidental typography in this one revision. The lowercase,
quoted `draft sequence` and uncapitalized `draft image` in the professor's 2.1
are not an instruction to rename `Draft Sequence` or `Draft image` elsewhere.
Keep the professor's supplied text intact unless the user requests an edit to
it; use the established terminology in newly written sections.

The revision uses passive voice as well as active voice. It does not support
an active-voice-only rule, a prohibition on repetition, or a requirement that
every sentence be short.

## Applying the new model to Sections 2.2-2.4

These are applications of the observed principles to the current manuscript,
not additional instructions attributed to the professor.

| Section | Reader's question | Explanatory progression |
| --- | --- | --- |
| 2.2, Parallel Capture | How does accepting the next request earlier affect capture reliability? | Define the capability and explain the callback's role -> state the responsiveness benefit -> explain independent timeout clocks and the shared worker -> show how waiting consumes a later capture's time. |
| 2.3, Draft Sequence | Why does the camera need this sequence, and why is extending it difficult? | Define the Draft result and its relationship to the final image -> explain replacement -> explain the single worker and the costs of concurrent execution -> describe the sequence's evolution and deferred post-processing -> motivate lightweight multi-frame composition and its deadline constraint. |
| 2.4, Limitations of the Thermal Guard | Why is the existing guard insufficient for deciding when the feature can run? | Define the thermal indicator and explain the failure that led to the guard -> explain its impact on ordinary use and what the cutoff does not observe -> introduce the experiment and its conditions -> compare Draft configurations under matched starting conditions -> motivate coordinated control of optional-stage execution and future capture arrivals. |

For 2.4, explain what the table actually measures before drawing a conclusion.
`tables/tab_timeout_index.tex` reports the earliest timeout index across ten
trials per condition, grouped by starting overheat level. It does not report
the thermal level at the moment of failure or the average failure point. A
missing timeout means none was observed within 30 captures. These are limits
of the evidence, not stylistic preferences. Implementation verification and
source distinctions for this rewrite are recorded in `docs/implementation-map.md`.

## Review questions

- Is the subject understandable before its importance or limitation is asserted?
- Does each step explain how it follows from the previous one?
- Are an action's purpose and a mechanism's consequence clear?
- Does each retained detail help explain the argument or support its evidence?
- Does a closing sentence synthesize the explanation rather than add praise?
- Are the claims faithful to their sources and the manuscript's terminology?
- Is a proposed rule actually supported by the professor's revision, rather
  than inherited from the deleted guide or inferred from a single formatting choice?
