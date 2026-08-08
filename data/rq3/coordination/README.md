# RQ3 Coordination Artifact

This directory contains generated evidence for the RQ3 summary table. Do not
edit generated CSV cells by hand.

## Generators

- `scripts/rq3_coordination_metrics.py` builds the retrospective realized-work
  and mandatory-work envelope partition.
- `scripts/rq3_coordination_audit.py` joins planned/executed admission classes,
  target/next margins, backlog-estimation error, queue residence, and thermal
  headroom change.

Run both from the repository root:

```text
python3 scripts/rq3_coordination_metrics.py
python3 scripts/rq3_coordination_audit.py
```

Both scripts use only the Python standard library and read the values-only XLSX
exports directly through ZIP/XML.

## Generated files

| File | Contents |
|---|---|
| `summary.csv` | Envelope totals, coverage, flexible share, floor misses, and flexible-band avoided-delay diagnostics |
| `envelope_share.csv` | Counts and percentages for the envelope partition |
| `action_summary.csv` | Flexible-band target/next demotion and mandatory-floor audit aggregates |
| `flexible_cases.csv` | One auditable row per admission-flexible transition |
| `mandatory_floor_cases.csv` | One auditable row per below-floor transition |
| `avoided_delay_12mp_normal.csv` | 12MP flexible-band diagnostic values |
| `avoided_delay_24mp_memory.csv` | 24MP flexible-band diagnostic values |

## Category definitions

```text
realized-work covered: d >= d_exec
admission-flexible:     d_mand <= d < d_exec
below mandatory floor: d < d_mand
```

Here `d_exec` uses the realized admitted Draft duration. `d_mand` replaces
admission-skippable work with DynamicFunction, Encoding, and measured Draft
overhead. The `2C` term spans the post-decision Draft and the next capture's
Draft released by the delay. Both values are retrospective matched-policy
targets, not physical minima: the deployed heuristic halves positive projected
pressure to limit user-visible delay and relies on admission to shed optional
work under residual pressure.

`targetOrNextDemoted` is an observed action anywhere in this two-Draft horizon.
It is not causal attribution of the next admission decision to the current
delay.

## Validity and interpretation

Timeout-measurement-error records are invalid observations rather than actual
Capture Timeout outcomes. No valid analyzed run timed out. Do not describe the
current population as survival-conditioned.

The existing trace cannot support a factual 0.5x or 0.75x delay trajectory.
Pacing changes later backlog, admission, thermal state, and realized work, so a
mechanically scaled delay column is not a closed-loop counterfactual. Similarly,
do not use unrelated-domain pacing policies as the default RQ3 baseline.

`potential_avoided_ms = d_exec - d` is local envelope arithmetic within the
admission-flexible band. It is not time that a burst would necessarily save
without pacing.

The mandatory floor is a sufficient retrospective reservation condition, not
the timeout boundary. Because it already excludes optional work, demotion in a
floor-miss case records admission action but does not mathematically remove the
remaining mandatory-floor deficit.

`deadlineRefMs`, `horizonReserveMs`, and `backlogResidualMs` decompose the
realized deadline margin:

```text
margin = deadlineRef + horizonReserve + backlogResidual - 2 * d_mand
```

`unmetFloorMs = 2 * (d_mand - d)` and `uncountedBudgetMs` are the same identity
split so that their difference is the margin; the figure uses them as axes, so
its diagonal is the deadline. `rq3_coordination_audit.py` aborts if the identity
does not close to 2 ms on every analyzed decision. This is exact arithmetic on
the realized trace and is not a counterfactual: it explains the margin that was
observed, not the margin a different delay would have produced.

See `docs/rq3-current.md` for the full paper-level interpretation and current
artifact inventory.
