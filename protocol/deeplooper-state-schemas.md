# DEEPLOOPER State Schemas

These schemas are the recovery contract for `.pipeline/deeplooper-<run-id>/`. They are intentionally Markdown/YAML so agents can read and rewrite them without a parser dependency.

## `state.md`

`deeplooper` owns this file. It is stage-boundary and slice-boundary state, not sub-step state.

```yaml
---
run_id: deeplooper-YYYYMMDD-HHMMSS
route: full
last_completed_stage: goals
next_stage: research
current_slice: null
current_phase: 0
slices_done: []
slices_blocked: []
requeue_counts: {}
backward_loops: 0
interaction_mode: interactive
failure_policy: fail-closed
resume_source: fresh
---
```

### Field Rules

- `route` is always `full`.
- `current_slice` is `null` outside the slice loop and the slice id while a slice is selected, building, requeued, or escalated.
- `current_phase` is `0` before normal slice phases exist; otherwise it is the numeric part of the selected slice's `phase_dir`.
- `slices_done` lists slice ids with `status: done` in `slice-queue.md`.
- `slices_blocked` lists slice ids with `status: blocked` or `status: escalated`.
- `requeue_counts` mirrors every slice with a nonzero `requeue_count`.
- `next_stage` values: `goals`, `research`, `design`, `skeleton`, `baseline`, `slice-loop`, `verify`, `accept`, `report`, `done`.
- `resume_source`: `fresh`, `state`, or `artifacts`.

## `slice-queue.md`

`slice-queue.md` is the living implementation plan. It is updated by `deeplooper` and `dl-reflector`.

```markdown
# Slice Queue

## Queue Invariants
- One active slice at a time.
- `phase_dir` values use `phases/phase-NN` for normal slices.
- A slice is ready only when all `deps` have status `done`.
- `requeue_count > 2` escalates to Design or Goals.

## Slices

### S-001 — Human-readable title
- id: S-001
- title: Human-readable title
- deps: []
- status: ready
- requeue_count: 0
- last_reason: None.
- acceptance_criteria: [AC-001]
- phase_dir: phases/phase-01
- source: design.md#vertical-slices
```

### Status Values

- `pending`: dependencies are not done.
- `ready`: eligible for the next slice loop pass.
- `building`: selected by the controller.
- `done`: implemented, done-checked, and reflected.
- `blocked`: cannot proceed without external input, but not necessarily a Goals/Design defect.
- `escalated`: routed to Design or Goals after cap/external classification.

### Update Rules

- Completed slices remain `done` across requeues and escalations unless the user explicitly invalidates them at a Goals/Design gate.
- Requeues update only the active slice's `requeue_count`, `last_reason`, and status.
- Remediation slices use ids `R-001`, `R-002`, ... and must cite `stage9-summary.md` or `global-acceptance-results.md` as `source`.

## `lessons.md`

Per-run lessons. Not shared across runs.

```markdown
# Lessons

## Active Constraints
- [timestamp] [slice-id] [source] Constraint. Planning instruction: ...

## Requeue Root Causes
- [timestamp] [slice-id] [source] Root cause. Planning instruction: ...

## Useful Patterns
- [timestamp] [slice-id] [source] Pattern. Planning instruction: ...

## Remediation Notes
- [timestamp] [criterion-id] [source] Red criterion. Planning instruction: ...
```

`dl-slice-planner` must read this file before writing any task spec.

## `spec-history.md`

Append-only audit log for living-spec changes.

```markdown
# Spec History

## 2026-06-20T00:00:00Z — S-002
- Amendment type: clarify acceptance criterion | add constraint | narrow non-goal | link criterion to slice
- Source evidence: `phases/phase-02/done-check-results.md`
- Applied change: [exact text changed in goals.md]
- Rationale: [why this is a clarification, not scope expansion]
```

`dl-reflector` may update `goals.md` only when it can write a corresponding `spec-history.md` entry.

## Phase Directory Contract

Every normal slice phase may contain:

```text
phases/phase-NN/
├── tasks/task-*.md
├── slice-plan-summary.md
├── feasibility-results.md
├── execution-manifest.md
├── e2e-regression-results.md
├── integration-results.md
├── regression-results.md
├── stage7-summary.md
├── stage7-integration-summary.md
├── done-check-results.md
├── coverage-plan.md
├── acceptance-results.md
├── backward-loop-analysis.md
└── stage8-summary.md
```

Required for a `done` slice: task specs, `stage7-summary.md` with PASS, `done-check-results.md` with PASS, and reflected queue state.
