# Current RQ3 Design and Interpretation

This document is the authoritative handoff for the current RQ3 candidate. It
supersedes the earlier four-policy RQ3 design still retained as historical
material in `docs/rq1-rq3-metrics-guide.md`.

## Research question

RQ3 asks whether the Context-Aware Draft Sequence Controller computes an
appropriately sized capture-availability delay for the Draft backlog and the
remaining Capture Timeout budget.

The current evaluation does not compare the controller against pacing methods
transplanted from unrelated domains. Such methods optimize different signals
and would not isolate whether this controller sizes its own intervention
appropriately. RQ3 instead evaluates five properties of the deployed control
structure:

1. whether pacing activates where retrospectively measured pressure is high;
2. why online actions can disagree with pressure reconstructed later;
3. how much of the realized-work envelope pacing covers by itself;
4. when admission handles optional work within the same two-Draft horizon; and
5. whether the resulting wait drains measured backlog at bounded user-visible
   cost.

## Current artifacts

The current main-paper candidates are:

- `tables/tab_rq3_pacing_compact.tex`;
- `figures/fig_rq3_pacing_compact.tex`.

The earlier policy, selectivity, and calibration TeX pairs are retained and
must not be deleted or silently overwritten. They are historical alternatives,
not additional exhibits to ship beside the compact pair.

Browser-rendered review previews are:

- `docs/tab_rq3_pacing_compact_preview.png`;
- `docs/fig_rq3_pacing_compact_preview.png`.

These PNGs preserve the content hierarchy for review but are not substitutes
for the final LaTeX render.

## Population and data-quality rule

The compact analysis uses the Full controller workbooks:

- `data/ablation_sampling/48U_metrics_12MP_normal_0803_{1,2}.xlsx`;
- `data/ablation_sampling/48U_metrics_24MP_memory_0803_{1,2}.xlsx`.

The timeout labels removed from this collection are known invalid measurements,
not actual Capture Timeout outcomes. Their removal is data-quality filtering,
not outcome-based survival conditioning. No valid analyzed run experienced an
actual Capture Timeout. Future manuscript revisions must not call this
population survival-conditioned. The final paper should identify the timeout
measurement fault and exclusion manifest wherever the experiment-validity
protocol is described; do not invent those details if the implementation or
manifest is unavailable.

Complete 30-shot runs are required. The current compact population contains 70
12MP-normal bursts and 69 24MP-memory-pressure bursts, producing 1,920 and
1,861 analyzed transitions. A transition additionally requires a recorded
pacing decision and a complete prior-Draft timeline. Watchdog-truncated
transitions lack a complete realized Draft duration and are excluded from the
envelope reconstruction for that reason.

## Envelope definitions

For one transition, let:

- \(d\) be the applied pacing delay;
- \(B\) be measured Draft backlog at the decision;
- \(T\) be the remaining deadline window;
- \(C_{exec}\) be the realized duration of the admitted Draft sequence; and
- \(C_{mand}\) contain DynamicFunction, Encoding, and measured Draft overhead,
  excluding admission-skippable optional work.

The retrospective pacing-only envelopes are:

\[
d^*_{exec}=\left\lceil\frac{[B+2C_{exec}-\max(0,T)]^+}{2}\right\rceil
\]

and

\[
d^*_{mand}=\left\lceil\frac{[B+2C_{mand}-\max(0,T)]^+}{2}\right\rceil.
\]

The factor \(2C\) is the deployed prospective horizon: (i) the Draft that
begins after the pacing decision and (ii) the Draft of the next capture released
by that delay. Waiting one millisecond both drains one millisecond of backlog
and shifts the next deadline by one millisecond, hence division by two.

Transitions with \(d^*_{exec}>0\) are partitioned into:

- **Pacing covers realized work:** \(d\ge d^*_{exec}\);
- **Admission-flexible:** \(d^*_{mand}\le d<d^*_{exec}\); and
- **Below mandatory floor:** \(d<d^*_{mand}\).

The admission-flexible category is a joint-control interpretation, not a claim
that pacing alone covers the work that eventually ran.

## Actual admission-action audit

Demotion ranks optional-work classes as:

```text
Bokeh+Filter > Filter only > Encoding only
```

The compact table reports two observed actions for admission-flexible
transitions:

- **target:** admission demoted the Draft directly associated with the pacing
  transition;
- **target-or-next:** admission demoted either that target or the next capture's
  Draft, matching the two-Draft prospective horizon.

Target-or-next is a horizon audit. It must not be phrased as causal attribution
of the next admission decision to the current delay.

Observed flexible-band demotion is:

| Condition | Target | Target or next |
|---|---:|---:|
| 12MP normal | 7/26 (26.9%) | 21/26 (80.8%) |
| 24MP memory pressure | 17/43 (39.5%) | 31/43 (72.1%) |

The flexible-band realized target-margin minimum/P5 is 134/183 ms in 12MP and
36/84 ms in 24MP.

## Mandatory-floor audit

No 12MP transition fell below \(d^*_{mand}\). Fourteen of 140 positive-envelope
24MP transitions did, clustered in four bursts:

- 11/14 received zero delay;
- admission demoted 14/14 target Drafts;
- online backlog was below subsequently realized backlog in 14/14;
- thermal headroom rose during queue residence in 12/14;
- median decision-to-Draft-start queue residence was 4.78 s;
- retained target and next captures had minimum realized margins of 307 and
  276 ms; and
- 0/14 produced an actual Capture Timeout.

The floor is a retrospective sufficient reservation condition, not the actual
timeout boundary. Because \(d^*_{mand}\) already excludes optional work, target
demotion documents coordination but does not itself erase the mandatory-floor
deficit. Backlog under-estimation and rising headroom are observationally
consistent with queue/thermal drift after the online decision; do not claim
causality from this trace split.

## Why no alternative-policy or scaled-delay baseline is required

RQ3 must not be reframed around Thermal LUT, CoDel-inspired, or other
domain-mismatched pacing methods unless the user explicitly changes the
research question. Those comparisons ask which foreign controller performs
better, not whether the proposed controller sizes delay appropriately for its
Draft backlog and deadline model.

Likewise, multiplying each recorded delay by 0.5 or 0.75 on the same trace is
not a valid counterfactual. Pacing is closed-loop: changing one delay changes
later arrival times, backlog, admission decisions, thermal state, throttling,
and realized Draft durations. The existing factual dataset therefore cannot
answer what the 0.5x or 0.75x trajectory would have been. A defensible scaling
study would require new matched factual runs or a validated closed-loop replay
or simulator; mechanically rescaling the recorded column is prohibited.

This limitation does not invalidate the current RQ3. It limits the supported
claim to trace-derived targeting, envelope coverage, coordination, work
conservation, and observed cost. Do not claim global optimality, a universally
minimal delay, or a counterfactual end-to-end speedup.

## Reproduction

Run from the repository root:

```text
python3 scripts/rq3_policy_metrics.py sampling  # requires openpyxl
python3 scripts/rq3_coordination_metrics.py
python3 scripts/rq3_coordination_audit.py
python3 scripts/render_rq3_compact_preview.py
```

The first command regenerates targeting and boundary-mechanism inputs. The
second produces the envelope partition. The third joins actual admission
actions and audits mandatory-floor misses. The fourth produces temporary
HTML/SVG preview sources; headless Chrome is then used to write the committed
PNG previews.

Detailed generated-file definitions are in
`data/rq3/coordination/README.md`.
The complete transfer checklist is `docs/rq3-file-manifest.md`.

## Supported manuscript conclusion

The current evidence supports the following bounded conclusion:

> The controller applies pacing selectively, sizes it against the admitted
> workload and measured backlog, and deliberately relies on admission for
> optional-work protection instead of forcing pacing alone to cover all
> realized Draft work.

It does not support `globally optimal`, `minimum necessary under every
counterfactual`, or a causal thermal claim.
