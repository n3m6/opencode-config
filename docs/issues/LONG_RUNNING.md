# Long-Running Session Status

## Status

As of 2026-04-14, the prompt contracts for the multi-phase full route have been refactored around phase-scoped execution directories. The contract-level blockers called out in the earlier long-running-session review are now addressed in the agent prompts and in [docs/DEEPWORK.md](../DEEPWORK.md).

The repository still does not contain an executable end-to-end pipeline harness, so this status reflects prompt-contract and documentation correctness, not a true runtime session replay. The remaining risk is live-session shakeout, not an unresolved controller design gap.

## Landed Changes

- Deepwork now treats `phases/phase-NN/` as the authoritative execution surface for Stage 7, Stage 8, and Stage 8.5 artifacts.
- Resume without `state.md` now uses a phase-aware recovery algorithm that scans active phase directories, replan notes, and verification/report markers.
- `state.md` now documents `replan` as a tracked stage, updates `phase_history` at phase boundaries, and explicitly limits recovery granularity to the stage level.
- Stage 6 still writes the canonical initial `tasks/` directory, and deepwork now creates `phases/phase-01/tasks/` as a symlink to that task set.
- Replan now writes the complete next-phase task set into `phases/phase-NN/tasks/`, keeps stable task IDs across the run, and appends the same review-status block that Stage 6 uses.
- Stage 7 now validates that every task listed for the active phase exists before implementation begins.
- Backward-loop cleanup is now phase-aware: completed phases are preserved, the failed current phase is deleted, and obsolete unstarted future phases are archived under `phases/archive/`.
- Verify and Report now aggregate across `phases/phase-*/` instead of relying on top-level cumulative execution or acceptance artifacts.

## Validation Run

The following validations were run after the refactor:

### 1. Editor validation

`get_errors` was run with no reported errors on:

- `agents/deepwork.md`
- `agents/qrspi-plan.md`
- `agents/qrspi-plan-writer.md`
- `agents/qrspi-implement.md`
- `agents/qrspi-accept.md`
- `agents/qrspi-replan.md`
- `agents/qrspi-replan-writer.md`
- `agents/qrspi-backward-loop-detector.md`
- `agents/qrspi-verify.md`
- `agents/qrspi-verifier.md`
- `agents/qrspi-report.md`
- `agents/qrspi-reporter.md`
- `docs/DEEPWORK.md`

### 2. Stale-path audit

A targeted search for old top-level Stage 7 / Stage 8 artifact paths across the `agents/` tree found no remaining stale references in the updated QRSPI surface. The only remaining matches were in `agents/orchestrator.md`, which is outside the phase-aware deepwork pipeline documented here.

### 3. Cross-file contract audit

A post-edit read-only contract audit was run across the updated controller, stage agents, downstream verifier/reporter agents, and `docs/DEEPWORK.md`. The audit initially called out a few deepwork steps that were phrased too implicitly; those were tightened so the controller now explicitly requires:

- writing recovered `state.md` immediately after artifact-based recovery
- creating the Phase 1 task symlink with `ln -s`
- re-reading `phase-manifest.md` after Replan
- archiving obsolete future phases with `mv`

## Resolution Map

### 1. Resume fallback was not phase-aware when `state.md` was missing

Resolved. Deepwork now scans active `phases/phase-*/` directories, uses phase-local `stage7-summary.md`, `stage8-summary.md`, and `replan/phase-NN-replan.md` markers, and reconstructs `state.md` from disk when needed.

### 2. `state.md` was too underspecified for interrupted long-running work

Resolved at the chosen recovery granularity. The new contract makes `state.md` a stage-boundary checkpoint, tracks `replan` in `stages_completed`, and updates `phase_history` at each phase boundary. It does not attempt sub-step recovery; interrupted stages restart from the beginning by design.

### 3. Replan could change the remaining phase structure without refreshing deepwork state

Resolved. After Replan, deepwork now re-reads `phase-manifest.md`, recomputes `total_phases`, rebuilds the visible checklist, archives obsolete unstarted future phases, and overwrites `state.md` from the refreshed manifest.

### 4. Multi-phase cumulative artifacts lacked a canonical phase schema

Resolved by removing the shared cumulative execution model. Stage 7, Stage 8, and Stage 8.5 now write phase-local artifacts under `phases/phase-NN/`, and downstream aggregation happens by enumerating those directories.

### 5. Backward-loop cleanup was phase-destructive

Resolved. Loopback now preserves completed phase directories, deletes only the failed current phase directory, archives obsolete unstarted future phases, and keeps the completed-phase audit trail intact.

### 6. Replan-updated tasks lacked a review-status handoff into Implement

Resolved. Replan now appends the same `## Review Status` block that Stage 6 uses to every next-phase task file it writes.

### 7. Superseded or stale task files were not separated clearly enough from the active remaining task set

Resolved for the active execution path. Phase-local task directories isolate the currently executable task set, and Stage 7 now validates the manifest-to-task-file mapping before it starts implementation.

## Remaining Constraints

- This repository still has no executable pipeline harness. The contracts are materially stronger, but real-session runtime behavior still needs live-session validation.
- Recovery remains stage-level, not sub-step. If interruption happens mid-stage or mid-review-loop, the whole stage restarts.
- Phase 1 intentionally uses a symlink to the top-level Stage 6 task directory. The authoritative audit trail for completed work is the phase-local stage outputs, not the mutable top-level `tasks/` directory.

## Conclusion

The long-running-session blockers documented in the earlier audit are now addressed at the prompt-contract level. The multi-phase full route should no longer be treated as structurally incomplete; the remaining work is operational shakeout in real sessions rather than another controller redesign.
