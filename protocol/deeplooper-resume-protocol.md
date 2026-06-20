# DEEPLOOPER Resume Protocol

Use this protocol when the user asks to resume a DEEPLOOPER run or provides a `.pipeline/deeplooper-<run-id>/` directory.

## Recovery Sources

1. Resolve the run directory.
2. Read `state.md` if present and coherent.
3. If `state.md` is missing or inconsistent, recover from artifacts.
4. Telemetry files are never recovery inputs.

## State-Based Recovery

If `state.md` is coherent, recover:

- `next_stage`
- `current_slice`
- `current_phase`
- `slices_done`
- `slices_blocked`
- `requeue_counts`
- `interaction_mode`
- `failure_policy`

Before dispatching the recovered stage, check whether that stage's summary artifact exists and begins with `### Status — FAIL`. If so, route through Error Handling instead of silently restarting.

## Artifact-Based Recovery

When reconstructing from disk:

1. Goals complete if `goals.md` exists.
2. Research complete if `research/summary.md` exists.
3. Design complete if `design.md` exists.
4. Skeleton complete if `skeleton-results.md` begins with `### Status — PASS`; Structure complete if `structure.md` exists.
5. Baseline complete if `baseline-results.md` exists.
6. Slice loop is recoverable when `slice-queue.md` exists.
7. For each active `phases/phase-NN/`, parse:
   - `stage7-summary.md`
   - `done-check-results.md`
   - `stage8-summary.md` when acceptance ran
8. `### Status — PASS` means complete. `### Status — FAIL`, missing status, or malformed status means the slice is incomplete and should restart at the owning stage or enter Error Handling.
9. `stage9-summary.md` with PASS means report is next. PARTIAL may report or requeue remediation based on the summary. FAIL routes through `dl-reflector` for remediation slice creation unless all failures are blocked/escalated.
10. `stage10-summary.md` means the run is complete.

## Cursor Selection

- If pre-loop artifacts are incomplete, resume at the first incomplete front-end stage.
- If `slice-queue.md` is missing after baseline, rebuild it from `design.md` and `skeleton-results.md`.
- If a slice is `building` and lacks a passing `stage7-summary.md`, reset it to `ready` and resume at `dl-slice-planner` unless its task spec is already current and feasibility passed.
- If implementation passed but `done-check-results.md` is missing or failing, resume at `dl-done-checker`.
- If a slice is done but reflection artifacts are stale, resume at `dl-reflector` for that slice.
- If all slices are done or blocked, resume at `dl-verify`.

After recovery, overwrite `state.md` with `resume_source: state` or `resume_source: artifacts`, rebuild the visible checklist from `slice-queue.md`, initialize telemetry sequence from `events.jsonl` line count if present, emit `run.resumed`, and continue.
