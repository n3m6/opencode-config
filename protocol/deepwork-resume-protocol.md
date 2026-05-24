### Resume Mode Protocol

If the user provides a run ID, asks to resume, or points at an existing `.pipeline/qrspi-<run-id>/` directory, do not start a new run immediately.

1. Resolve the run directory: `.pipeline/qrspi-<run-id>/`
2. Read `.pipeline/qrspi-<run-id>/state.md`
3. If `state.md` exists and is coherent, use it as the authoritative recovery record:
   - recover `route`
   - recover `current_phase`
   - recover `total_phases`

- recover `interaction_mode`
- recover `failure_policy`
- recover `next_stage`
- before re-dispatching that recovered `next_stage`, check whether the corresponding summary artifact for the same stage/phase already exists on disk and parses as `### Status — FAIL`
- if such a failed summary exists, do not silently restart; surface it through the existing Error Handling path for that recovered stage instead

4. If `state.md` is missing or inconsistent, reconstruct progress from artifacts on disk using this phase-aware algorithm:

- Read `config.md` to confirm the route and recover `interaction_mode` / `failure_policy` when present.
- Check pre-phase completion markers:
  - Goals complete if `goals.md` exists
  - Research complete if `research/summary.md` exists
  - Design complete if `design.md` exists, or the route is quick-fix
  - Structure complete if `structure.md` exists, or the route is quick-fix
  - Plan complete if `baseline-results.md` exists
- The merged Research stage owns all intermediate question-generation artifacts. If any of `goal-inventory.md`, `questions.md`, `question-leakage-review.md`, `question-quality-review.md`, `research/open-questions.md`, `research/question-ledger.md`, or `research/iterations/` exist without `research/summary.md`, treat Research as in-progress and restart `next_stage: research` from the beginning of the merged stage.
- If any pre-phase stage is incomplete, resume at the first incomplete stage and force `current_phase: 1`.
- Otherwise read `phase-manifest.md` to determine `total_phases`.
- Scan only active phase directories with `ls .pipeline/qrspi-<run-id>/phases/phase-*/`. Ignore anything under `phases/archive/`.
- For each Stage 7 / 8 / 8.5 / 9 summary artifact found, parse the first `### Status` heading of the file to classify the artifact:
  - `### Status — PASS` (also `### Status — PARTIAL` for `stage9-summary.md`) → stage **complete**; treat the artifact as authoritative.
  - `### Status — FAIL` → stage **incomplete with explicit failure on disk**; do not advance past it. Surface to the user via the existing Error Handling path with retry stage or abort run options before continuing recovery.
  - Missing `### Status` first heading, malformed Status, or unrecognized value → treat the same as FAIL (stage incomplete; surface via Error Handling). This includes summary files written by older pipeline versions that predate this contract.
- Throughout the rules below, "X is complete" means the corresponding summary file exists **and** parses as PASS (or PARTIAL for Stage 9) per the Status rule above. Files that parse as FAIL or missing-Status do not satisfy completion and trigger Error Handling instead.
- For each active phase directory in numeric order:
  - `phases/phase-NN/stage7-summary.md` (complete) means Implement is complete for phase `NN`
  - `phases/phase-NN/stage8-summary.md` (complete) means Accept-Test is complete for phase `NN`
  - `phases/phase-NN/replan/phase-NN-replan.md` (complete) means Replan is complete for phase `NN`
- Determine the recovery cursor as follows:
  - If no active phase directory has any stage artifact yet, set `current_phase: 1` and `next_stage: implement`
  - If the highest active phase with artifacts has no complete `stage7-summary.md`, restart `implement` for that phase
  - If `stage7-summary.md` is complete but `stage8-summary.md` is not, restart `accept` for that phase
  - If `stage8-summary.md` is complete but no complete replan note exists:
    - if the route is quick-fix, or that phase equals `total_phases`, set `next_stage: verify`
    - otherwise set `next_stage: replan`
  - If the replan note is complete:
    - if that completed phase now equals `total_phases`, set `next_stage: verify`
    - otherwise set `current_phase` to the next phase number and set `next_stage: implement`
- Stage-level recovery only: if a phase directory contains partial in-stage artifacts without the stage summary file, restart that entire stage from its beginning.
- Override phase recovery with post-phase markers when present:
  - `stage9-summary.md` parsed as PASS or PARTIAL → `next_stage: report`
  - `stage9-summary.md` parsed as FAIL or with a missing `### Status` heading → surface via Error Handling for Stage 9 recovery (do not advance to `report`)
  - `stage10-summary.md` means the run is complete (presence check; Stage 10 is not bound by the Status-line contract)

5. Immediately overwrite `state.md` from the recovered route, phase, and next-stage cursor with `resume_source: artifacts` when artifact recovery was used.

- Preserve recovered `interaction_mode` / `failure_policy`; if neither `state.md` nor `config.md` yields them, default to `interaction_mode: interactive` and `failure_policy: fail-closed`.

6. For quick-fix runs, always force `current_phase: 1` and `total_phases: 1` during recovery.
7. Reconstruct the visible todo checklist from the recovered route and the refreshed `phase-manifest.md`, ignoring archived future phases.

If both `state.md` and the artifact set imply the run is already complete, present the preserved report path and stop.

### Telemetry Non-Interference

The recovery algorithm above never reads any file under `telemetry/`. The existence or absence of `telemetry/events.jsonl`, `telemetry/run-log.md`, or `telemetry/metrics-summary.md` has no effect on which stage is recovered or which artifacts are considered authoritative. Telemetry files may be missing, partial, or stale without affecting resume correctness.

After recovery completes and `state.md` is refreshed, initialize the telemetry sequence counter from the existing `events.jsonl` line count (0 if missing) and emit a `run.resumed` event before re-dispatching the recovered next stage.
