# DEEPLOOPER Backward Loop Protocol

This protocol is invoked when a DEEPLOOPER slice cannot be corrected by local requeue, or when a slice has been requeued more than two times.

## Inputs

- Run ID: `deeplooper-<timestamp>`
- Current slice id and phase dir
- Triggering stage: `skeleton`, `slice-planner`, `implement`, `done-checker`, `verify`, or `accept`
- Failure evidence from the triggering artifact
- Current `slice-queue.md`, `lessons.md`, `goals.md`, and `design.md`

## Classification

The controller or `dl-backward-loop-detector` classifies the issue as one of:

| Classification | Meaning | Action |
| --- | --- | --- |
| `LOCAL_SLICE` | The slice task spec or implementation details are wrong, but Goals and Design remain valid. | Requeue the same slice with the failure reason. |
| `LOOP_DESIGN` | The slice DAG, architecture, slice boundaries, dependencies, or technology choice must change. | Escalate to the Design gate. |
| `LOOP_GOALS` | Acceptance criteria, scope, constraints, or non-goals must change. | Escalate to the Goals gate. |

No Plan, Structure, Replan, Defer, Continue, or Full Reset options exist in DEEPLOOPER. Completed slice commits and completed phase directories are preserved.

## Local Requeue

1. Increment the slice's `requeue_count` in `slice-queue.md`.
2. Set `status: ready` unless dependencies are now blocked.
3. Set `last_reason` to the concise failure root cause.
4. Append the root cause and planning instruction to `lessons.md`.
5. Emit `requeue.requested` and `requeue.decided` telemetry.
6. Re-enter the loop at `dl-slice-planner` for the same slice.

If `requeue_count > 2`, stop local requeue and escalate.

## Design Escalation

Use when the issue requires changing the approach, slice DAG, slice boundaries, dependency ordering, file architecture, or skeleton/structure assumptions.

1. Write `feedback/design-escalation-<NN>.md` containing the request, current slice, phase artifacts, and relevant lessons.
2. Mark the current slice `escalated` in `slice-queue.md`.
3. Preserve all completed phase directories and commits.
4. Preserve the failed phase directory for audit; do not delete completed-slice evidence.
5. Overwrite `state.md` with `next_stage: design`, `current_slice` set to the escalated slice, and increment `backward_loops`.
6. Dispatch `dl-design` with `=== FAILURE CONTEXT ===` containing the feedback file, current `slice-queue.md`, `lessons.md`, and completed-slice summaries.
7. After Design approval, rebuild or patch the remaining queue from the new Slice DAG while keeping completed slices marked `done` unless the user explicitly invalidates them.

## Goals Escalation

Use when success criteria, scope, non-goals, or constraints must change.

1. Write `feedback/goals-escalation-<NN>.md` containing accumulated learnings and why Design cannot resolve the issue alone.
2. Mark the current slice `escalated`.
3. Preserve the whole run directory and all completed commits.
4. Overwrite `state.md` with `next_stage: goals`, `current_slice` set to the escalated slice, and increment `backward_loops`.
5. Dispatch `dl-goals` with `=== PRIOR RUN LEARNINGS ===` containing the escalation file, `lessons.md`, and the current living spec.
6. After Goals approval, proceed through Research and Design again only as needed by the controller; never delete completed slice evidence automatically.

## Telemetry

Emit:

- `backward_loop.requested` before classification is acted on.
- `requeue.*` for local requeues.
- `gate.presented` and `gate.approved` for Goals or Design escalation decisions.
- `backward_loop.decided` with `context.loop_target: "design" | "goals"` for escalation.

Telemetry is diagnostic only and must not affect resume recovery.
