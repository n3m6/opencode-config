### Resume Mode Protocol

If the user provides a run ID, asks to resume, or points at an existing `.pipeline/qrspi-<run-id>/` directory, do not start a new run immediately.

1. Resolve the run directory: `.pipeline/qrspi-<run-id>/`
2. Read `.pipeline/qrspi-<run-id>/state.md`
3. If `state.md` exists and is coherent, use it as the authoritative recovery record:
   - recover `route`
   - recover `current_phase`
   - recover `total_phases`
   - recover `next_stage`
4. If `state.md` is missing or inconsistent, reconstruct progress from artifacts on disk using this phase-aware algorithm:
   - Read `config.md` to confirm the route.
   - Check pre-phase completion markers:
     - Goals complete if `goals.md` exists
     - Questions complete if `questions.md` exists
     - Research complete if `research/summary.md` exists
     - Design complete if `design.md` exists, or the route is quick-fix
     - Structure complete if `structure.md` exists, or the route is quick-fix
     - Plan complete if `baseline-results.md` exists
   - If any pre-phase stage is incomplete, resume at the first incomplete stage and force `current_phase: 1`.
   - Otherwise read `phase-manifest.md` to determine `total_phases`.
   - Scan only active phase directories with `ls .pipeline/qrspi-<run-id>/phases/phase-*/`. Ignore anything under `phases/archive/`.
   - For each active phase directory in numeric order:
     - `phases/phase-NN/stage7-summary.md` means Implement is complete for phase `NN`
     - `phases/phase-NN/stage8-summary.md` means Accept-Test is complete for phase `NN`
     - `phases/phase-NN/replan/phase-NN-replan.md` means Replan is complete for phase `NN`
   - Determine the recovery cursor as follows:
     - If no active phase directory has any stage artifact yet, set `current_phase: 1` and `next_stage: implement`
     - If the highest active phase with artifacts has no `stage7-summary.md`, restart `implement` for that phase
     - If it has `stage7-summary.md` but no `stage8-summary.md`, restart `accept` for that phase
     - If it has `stage8-summary.md` but no replan note:
       - if the route is quick-fix, or that phase equals `total_phases`, set `next_stage: verify`
       - otherwise set `next_stage: replan`
     - If it has a replan note:
       - if that completed phase now equals `total_phases`, set `next_stage: verify`
       - otherwise set `current_phase` to the next phase number and set `next_stage: implement`
   - Stage-level recovery only: if a phase directory contains partial in-stage artifacts without the stage summary file, restart that entire stage from its beginning.
   - Override phase recovery with post-phase markers when present:
     - `stage9-summary.md` means `next_stage: report`
     - `stage10-summary.md` means the run is complete
5. Immediately overwrite `state.md` from the recovered route, phase, and next-stage cursor with `resume_source: artifacts` when artifact recovery was used.
6. For quick-fix runs, always force `current_phase: 1` and `total_phases: 1` during recovery.
7. Reconstruct the visible todo checklist from the recovered route and the refreshed `phase-manifest.md`, ignoring archived future phases.

If both `state.md` and the artifact set imply the run is already complete, present the preserved report path and stop.

### Telemetry Non-Interference

The recovery algorithm above never reads any file under `telemetry/`. The existence or absence of `telemetry/events.jsonl`, `telemetry/run-log.md`, or `telemetry/metrics-summary.md` has no effect on which stage is recovered or which artifacts are considered authoritative. Telemetry files may be missing, partial, or stale without affecting resume correctness.

After recovery completes and `state.md` is refreshed, initialize the telemetry sequence counter from the existing `events.jsonl` line count (0 if missing) and emit a `run.resumed` event before re-dispatching the recovered next stage.
