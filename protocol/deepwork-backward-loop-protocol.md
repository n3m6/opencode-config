### Backward Loop Protocol

This protocol is invoked from any of the following:

- A stage subagent (`qrspi-implement`, `qrspi-accept`, `qrspi-replan`) returns a `### Backward Loop Request`.
- `qrspi-verify` returns FAIL and the **auto Stage 7 fix-mode pass** (see precondition below) does not recover. In that case deepwork synthesizes a backward-loop request from the verifier's failing rows before invoking this protocol.
- The Plan/Replan **unclean-cap or stable-cap escalation gate** in deepwork yields a "loop back" answer; deepwork synthesizes a backward-loop request from the reviewer's final `### Fix Guidance` and invokes this protocol with the user-chosen target.

#### Precondition: Stage 9 → Stage 7 Auto-Fix Pass

When `qrspi-verify` returns FAIL, deepwork attempts **one** Stage 7 fix-mode pass before invoking this protocol:

1. The verifier's failing rows are formatted as regression evidence.
2. Deepwork dispatches `qrspi-implement` with `=== MODE === verify-fix` and `=== VERIFY FAILURES ===` containing those rows; `qrspi-implement` runs the existing regression-remediation path, capped at one round.
3. Deepwork re-dispatches `qrspi-verify`. PASS or PARTIAL → continue to Stage 10. FAIL again → invoke this protocol with the verify failure as the loop request body.

This pass is bypassed when the user has already triggered a backward loop in this stage instance, or when `qrspi-implement` itself returned a `### Backward Loop Request`.

When this protocol is invoked:

1. Read the backward loop request details.
2. If the caller already has a user-chosen option from the Plan/Replan unclean-cap escalation gate, skip the prompt in step 2 entirely. Treat that earlier answer as the protocol decision, continue directly with the matching option handler below, and do not emit a second `backward-loop-decision` gate pair; the original Plan/Replan gate already captured the wait time and choice.
3. Otherwise, present the issue to the user via `question`:

   ```
   ### Backward Loop Detected

   **Stage:** [which stage reported it]
   **Issue:** [description from the subagent]
   ```

[If the route is `quick-fix`, present only these options:
C) Loop back to **Plan** (revise task specifications)
E) Attempt a **local fix** within the current stage
F) **Continue as-is** (accept the limitation)
G) Full reset to **Goals** (restart the pipeline with accumulated learnings)]

Options:
A) Loop back to **Design** (re-architect the approach)
B) Loop back to **Structure** (re-map files and interfaces)
C) Loop back to **Plan** (revise task specifications)
D) Defer to the next **Replan** (record the issue for the next phase boundary)
E) Attempt a **local fix** within the current stage
F) **Continue as-is** (accept the limitation)
G) Full reset to **Goals** (restart the pipeline with accumulated learnings)

Which option?

```

Do not present Design or Structure as loop targets on the quick-fix route.

4. **If the user chooses A, B, or C** (loop-back):
a. Determine the loop target stage number (Design=4, Structure=5, Plan=6).
b. Create the feedback and archive directories if needed: `mkdir -p .pipeline/qrspi-<run-id>/feedback` and `mkdir -p .pipeline/qrspi-<run-id>/phases/archive`.
c. Write loop feedback to `.pipeline/qrspi-<run-id>/feedback/{stage}-loop-{NN}.md` with the backward loop request details using the edit tool.
d. Before deleting or moving any active artifact, write `.pipeline/qrspi-<run-id>/feedback/{stage}-loop-{NN}-evidence.md` containing:
   - the backward loop request details
   - the triggering stage and current phase
   - the current phase's `execution-manifest.md`, `integration-results.md`, `acceptance-results.md`, `stage7-summary.md`, `stage8-summary.md`, and `backward-loop-analysis.md` when present
   - the current `plan.md`, `phase-manifest.md`, and any current-phase task specs when present
   Use `N/A` for missing optional files. This evidence file is the preserved failure context for the rerun.
e. Preserve completed phase directories `phases/phase-01/` through `phases/phase-(N-1)/` unchanged.
f. Archive the current incomplete phase directory by moving it to `.pipeline/qrspi-<run-id>/phases/archive/failed-phase-NN-loop-{NN}/` when it exists. Do not delete the only copy of the failed phase evidence.
g. Archive any unstarted future phase directories by moving them under `.pipeline/qrspi-<run-id>/phases/archive/phase-NN/` before regenerating the remaining plan.
h. Delete regenerated top-level artifacts based on the loop target:
  - Plan: `plan.md`, `phase-manifest.md`, `baseline-results.md`, and `tasks/`
  - Structure: all Plan artifacts plus `structure.md`
  - Design: all Structure artifacts plus `design.md`
i. Reset the todo items for the target stage and all downstream stages to not-started, and remove stale unstarted phase entries that no longer match the active manifest.
j. Overwrite `state.md` with the loop target as `next_stage`, increment `backward_loops`, set `current_phase` to the earliest incomplete phase number when completed phases are preserved, reset it to `1` only when no completed phases remain or the target is before phased execution, and preserve `phase_history` for already-completed phases.
k. Re-enter the pipeline at the target stage. The re-run must receive the feedback file and evidence file as additional context.
l. When re-entering Design, Structure, or Plan from Phase 2 or later, also include:

```

=== NEXT REMAINING PHASE ===
Include the earliest incomplete phase number that must be replanned.

=== PRIOR PHASE MANIFEST ===
Include the last known phase-manifest.md so the rerun can preserve completed
phase numbering and only regenerate the remaining phases.

=== COMPLETED PHASES CONTEXT ===
For each completed prior phase, include the full execution-manifest.md,
integration-results.md, acceptance-results.md, stage7-summary.md, and
stage8-summary.md from that phase directory.

=== FAILURE CONTEXT ===
Include the loop feedback file, the loop evidence file, and any available
stage7/stage8 summaries or backward-loop analysis from the archived failed
phase directory.

```

Stage 6 will recreate active phase directories and task locations after the loop target completes.
5. **If the user chooses D** (defer to Replan):
a. Create the feedback directory if needed: `mkdir -p .pipeline/qrspi-<run-id>/feedback`
b. Write `.pipeline/qrspi-<run-id>/feedback/deferred-replan-{NN}.md` with the current stage, current phase, and backward-loop request details.
c. Overwrite `state.md` with the same current phase, increment `backward_loops`, and keep the normal next stage.
d. Continue the current stage as non-blocking. The next Replan stage must read all deferred replan feedback files.
6. **If the user chooses E** (local fix): Continue the current stage, treating the issue as a non-blocking problem.
7. **If the user chooses F** (continue): Proceed to the next stage without changes.
8. **If the user chooses G** (full reset to Goals):
a. Create the feedback directory if needed: `mkdir -p .pipeline/qrspi-<run-id>/feedback`
b. Write `.pipeline/qrspi-<run-id>/feedback/goals-reset-context.md` containing the backward-loop request, current phase, and a concise summary of what was learned before the reset.
c. Delete every pipeline artifact except `feedback/`, including all active and archived `phases/` directories. Do NOT delete the `telemetry/` directory — preserve it as a diagnostic record of the failed run state.
d. Recreate `state.md` with `route: unknown`, `current_phase: 1`, `total_phases: 0`, `last_completed_stage: none`, `next_stage: goals`, incremented `backward_loops`, and `resume_source: state`.
e. Reset the visible checklist to the initial pre-plan state.
f. Re-enter the pipeline at **Stage 1** and include the contents of `feedback/goals-reset-context.md` as `=== PRIOR RUN LEARNINGS ===` in the Goals dispatch.

### Telemetry Integration

Telemetry events are emitted by deepwork around the protocol steps above:

- **Before presenting the decision to the user:** Emit `backward_loop.requested` with `stage`, `phase`, and `context` containing the loop request details.
- **When invoked with a preselected Plan/Replan loop-back target:** Deepwork still emits `backward_loop.requested` before entering the protocol, but skips the extra backward-loop decision prompt and emits the corresponding `backward_loop.decided` event directly from the preselected choice after the loop-back artifacts are determined.
- **After the user decides:**
  - Options A, B, C (loop-back): Emit `backward_loop.decided` with `decision.choice` (A/B/C), `decision.reason` (user input or inferred), `context.loop_target` (design/structure/plan), `context.deleted_artifacts` (list of deleted top-level artifacts), and `context.archived_artifacts` (list of archived phase directories).
  - Option D (defer): Emit `backward_loop.deferred` with `decision.choice: "D"` and `decision.reason`.
  - Options E, F (local fix / continue): Emit `backward_loop.decided` with `decision.choice: "E"` or `"F"` and the reason.
  - Option G (full reset): Emit `backward_loop.reset` with `summary` (brief learnings summary) and `context.artifacts_deleted` (all deleted artifact paths). Note: telemetry files are NOT included in the deleted list.
- **After emitting the event:** Regenerate `telemetry/run-log.md`.
```
