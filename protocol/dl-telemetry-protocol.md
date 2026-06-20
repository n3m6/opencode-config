# DEEPLOOPER Telemetry Protocol

DEEPLOOPER uses the same JSONL envelope as `telemetry-protocol.md`, with a `deeplooper-<timestamp>` run id and `writer_agent` values from the `dl-*` namespace.

## Files

- `.pipeline/deeplooper-<run-id>/telemetry/events.jsonl` — append-only canonical event stream.
- `.pipeline/deeplooper-<run-id>/telemetry/run-log.md` — derived timeline regenerated at boundaries.
- `.pipeline/deeplooper-<run-id>/telemetry/metrics-summary.md` — final or abort rollup.

Telemetry is diagnostic only. Resume reads `state.md`, `slice-queue.md`, and stage artifacts, never telemetry.

## Additional Event Classes

| Class | Events | Writer |
| --- | --- | --- |
| `slice.*` | `slice.queued`, `slice.started`, `slice.completed`, `slice.blocked`, `slice.escalated` | `deeplooper`, `dl-reflector` |
| `requeue.*` | `requeue.requested`, `requeue.decided`, `requeue.exhausted` | `deeplooper` |
| `reflect.*` | `reflect.started`, `reflect.completed` | `dl-reflector` |
| `spec_amendment.*` | `spec_amendment.applied`, `spec_amendment.rejected` | `dl-reflector` |
| `global_gate.*` | `global_gate.started`, `global_gate.completed`, `global_gate.remediation_queued` | `deeplooper` |

## Slice Context Payload

Slice-scoped events should include:

```json
{
  "slice_id": "S-002",
  "phase_dir": "phases/phase-02",
  "requeue_count": 1,
  "acceptance_criteria": ["AC-002"],
  "deps": ["S-001"]
}
```

## Stage Telemetry Additions

- `dl-slice-planner`: `slice_id`, `phase_dir`, `task_count`, `requeue_count`, `used_lessons`, `feasibility_items`, `done_items`.
- `dl-done-checker`: `slice_id`, `checked`, `passed`, `failed`, `skipped`.
- `dl-reflector`: `slice_id`, `queue_updates`, `lessons_added`, `spec_amendments`, `remediation_slices_added`.
- `dl-implement`: retains implementation metrics but reports `mode: "slice" | "remediation"`.
- `dl-verify`: reports `verify_status`, `red_criteria`, and `remediation_required`.

## Derived Log Requirements

`run-log.md` should show current slice status instead of deepwork's phase snapshot:

- Current slice id and phase dir
- Requeue count and last reason
- Ready, pending, done, blocked, and escalated slice counts
- Latest spec amendment
- Global gate status
