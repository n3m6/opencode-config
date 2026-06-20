# DEEPLOOPER Dry-Run Contract Trace

This is a static dry-run of the DEEPLOOPER C3 pipeline contracts. It verifies the new controller can pass artifacts between copied/adapted agents without relying on the old Plan/Replan middle.

## 1. Happy Path Slice Loop

1. `deeplooper` creates `.pipeline/deeplooper-20260620-000000/`, initializes `state.md`, `lessons.md`, `spec-history.md`, telemetry, and branch `deeplooper/deeplooper-20260620-000000`.
2. `dl-goals` writes `requirements.md`, `goals.md`, `config.md`; controller forces `route: full`.
3. `dl-research` writes `research/summary.md`.
4. `dl-design` writes `design.md` with `## Vertical Slices` and `## Slice Dependency DAG`.
5. `dl-skeleton` writes `skeleton-task.md`, `skeleton-results.md`, `structure.md`; skeleton output seeds slice 0 / structure context.
6. `dl-baseline-checker` writes `baseline-results.md`.
7. Controller writes `slice-queue.md` with `S-001` ready and `phase_dir: phases/phase-01`.
8. Controller dispatches `dl-slice-planner` for `S-001`; it writes `phases/phase-01/tasks/task-01.md` and `slice-plan-summary.md`.
9. `dl-feasibility-checker` receives `RUN ID`, `CURRENT SLICE`, `PHASE DIR`, mode `slice`, and the task specs; PASS means all preconditions are valid. The controller writes the returned `### Feasibility Results` to `<phase-dir>/feasibility-results.md`.
10. `dl-implement` receives `CURRENT SLICE`, `CURRENT PHASE`, `PHASE DIR`, and mode `slice`; it reads tasks from the phase dir and writes `execution-manifest.md`, `stage7-summary.md`, integration/regression artifacts.
11. `dl-done-checker` reads `## Done Checklist` from phase-dir tasks and writes `done-check-results.md` PASS.
12. `dl-reflector` in `slice-success` marks `S-001` done, appends lessons/spec history as needed, unblocks next slices.
13. Controller checkpoints `deeplooper: slice S-001 complete` and repeats.

Contract check: no step reads `plan.md`, `phase-manifest.md`, `qrspi-*`, or replan artifacts.

## 2. Local Requeue

1. `dl-feasibility-checker` returns FAIL for `S-002`: `path-exists: src/current.ts` missing.
2. Controller treats this as `LOCAL_SLICE` and dispatches `dl-reflector` with `MODE: slice-requeue`.
3. `dl-reflector` increments `S-002` from `requeue_count: 0` to `1`, sets `last_reason`, appends a lesson, and leaves completed slices done.
4. Controller checkpoints `deeplooper: slice S-002 requeued`.
5. Next loop selects `S-002` again. `dl-slice-planner` receives the requeue reason and rewrites `phases/phase-02/tasks/task-01.md` with corrected feasibility assumptions.

Contract check: only the active slice task spec changes; no completed phase is deleted or archived.

## 3. Requeue Cap Escalation

1. `S-003` returns local failures across three attempts.
2. After `dl-reflector` increments to `requeue_count: 3`, controller sees `requeue_count > 2`.
3. Controller emits `requeue.exhausted`, reads `protocol/deeplooper-backward-loop-protocol.md`, and classifies the issue.
4. If the issue is slice DAG or file-boundary related, controller marks `S-003` escalated and re-enters `dl-design` with failure context.
5. If the issue changes acceptance criteria or scope, controller escalates to `dl-goals`.

Contract check: completed slices and commits are preserved; only remaining queue entries are rebuilt or patched after the human gate.

## 4. Global-Gate Remediation

1. All ready/pending slices are done; controller dispatches `dl-verify`.
2. `dl-verify` writes `stage9-summary.md` with `### Status — FAIL` and `### Red Criteria — AC-007`.
3. Controller dispatches `dl-reflector` with `MODE: global-remediation`, passing the `### Red Criteria` verbatim as `TRIGGER EVIDENCE`. The reflector also reads `stage9-summary.md` / `global-acceptance-results.md` as a fallback so the red criteria are always available.
4. `dl-reflector` adds `R-001 — Remediate AC-007` with `source: stage9-summary.md`, a new `phase_dir`, and deps based on attribution.
5. Controller returns to slice selection; `R-001` goes through planner, feasibility, implementation, done checker, and reflection.
6. Global verify repeats until PASS, PARTIAL with only blocked/escalated criteria, or escalation.

Contract check: red criteria become ordinary slices and reuse the same local loop instead of invoking a global rollback.

## 5. Resume Checkpoints

- Before slice loop: recover from front-end artifacts and rebuild `slice-queue.md` if missing.
- During a selected slice: `state.md.current_slice` plus `slice-queue.md` decide whether to restart planner, feasibility, implementation, done checker, or reflection.
- After global verify FAIL: `stage9-summary.md` plus `slice-queue.md` decide whether to enqueue remediation or report PARTIAL.
- Telemetry is not consulted for recovery.

## Contract Mismatches Found and Resolved

- Old `phase-manifest.md` dependency replaced with `slice-queue.md`.
- Old `Plan Review Status` label replaced with `Slice Review Status` in implementation flow.
- Old `Affected Artifact: plan|structure` routing replaced with `slice|design|goals`.
- Old Replan/Option-P model replaced with `dl-reflector` local requeue and remediation slices.
- Acceptance and report stages now consume slice queue and phase artifacts, not replan notes.
- Controller `dl-feasibility-checker` and `dl-done-checker` dispatches now pass `RUN ID` + `PHASE DIR` explicitly so the checkers can resolve `.pipeline/<run-id>/<phase-dir>/` artifacts.
- `dl-feasibility-checker` now declares `CURRENT SLICE` and `PHASE DIR` in its own input/return contract, matching the controller dispatch and phase-local `feasibility-results.md` write.
- Controller persists the feasibility checker's `### Feasibility Results` to `<phase-dir>/feasibility-results.md` (the checker is read-only and delegates the write to its caller).
- Global-gate `global-remediation` now passes `dl-verify`'s `### Red Criteria` to `dl-reflector` as `TRIGGER EVIDENCE`; previously the reflector had no source for the red criteria to enqueue.
