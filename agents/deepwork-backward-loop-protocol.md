### Backward Loop Protocol

When a stage subagent (`qrspi-implement`, `qrspi-accept`, or `qrspi-replan`) includes a `### Backward Loop Request` section in its return:

1. Read the backward loop request details.
2. Present the issue to the user via `question`:

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

3. **If the user chooses A, B, or C** (loop-back):
a. Determine the loop target stage number (Design=4, Structure=5, Plan=6).
b. Write loop feedback to `.pipeline/qrspi-<run-id>/feedback/{stage}-loop-{NN}.md` with the backward loop request details using the edit tool.
c. Create the feedback directory if needed: `mkdir -p .pipeline/qrspi-<run-id>/feedback`
d. Preserve completed phase directories `phases/phase-01/` through `phases/phase-(N-1)/` unchanged.
e. Delete the current incomplete phase directory with `rm -rf .pipeline/qrspi-<run-id>/phases/phase-NN/`.
f. Archive any unstarted future phase directories by moving them under `.pipeline/qrspi-<run-id>/phases/archive/phase-NN/` before regenerating the remaining plan.
g. Delete regenerated top-level artifacts based on the loop target:
  - Plan: `plan.md`, `phase-manifest.md`, `baseline-results.md`, and `tasks/`
  - Structure: all Plan artifacts plus `structure.md`
  - Design: all Structure artifacts plus `design.md`
h. Reset the todo items for the target stage and all downstream stages to not-started, and remove stale unstarted phase entries that no longer match the active manifest.
i. Overwrite `state.md` with the loop target as `next_stage`, increment `backward_loops`, set `current_phase` to the earliest incomplete phase number when completed phases are preserved, reset it to `1` only when no completed phases remain or the target is before phased execution, and preserve `phase_history` for already-completed phases.
j. Re-enter the pipeline at the target stage. The re-run must receive the feedback file as additional context.
k. When re-entering Design, Structure, or Plan from Phase 2 or later, also include:

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
Include the failed phase's backward-loop-analysis.md, the loop feedback file,
and any relevant stage7/stage8 summaries from the failed phase.

```

Stage 6 will recreate active phase directories and task locations after the loop target completes.
4. **If the user chooses D** (defer to Replan):
a. Create the feedback directory if needed: `mkdir -p .pipeline/qrspi-<run-id>/feedback`
b. Write `.pipeline/qrspi-<run-id>/feedback/deferred-replan-{NN}.md` with the current stage, current phase, and backward-loop request details.
c. Overwrite `state.md` with the same current phase, increment `backward_loops`, and keep the normal next stage.
d. Continue the current stage as non-blocking. The next Replan stage must read all deferred replan feedback files.
5. **If the user chooses E** (local fix): Continue the current stage, treating the issue as a non-blocking problem.
6. **If the user chooses F** (continue): Proceed to the next stage without changes.
7. **If the user chooses G** (full reset to Goals):
a. Create the feedback directory if needed: `mkdir -p .pipeline/qrspi-<run-id>/feedback`
b. Write `.pipeline/qrspi-<run-id>/feedback/goals-reset-context.md` containing the backward-loop request, current phase, and a concise summary of what was learned before the reset.
c. Delete every pipeline artifact except `feedback/`, including all active and archived `phases/` directories.
d. Recreate `state.md` with `route: unknown`, `current_phase: 1`, `total_phases: 0`, `last_completed_stage: none`, `next_stage: goals`, incremented `backward_loops`, and `resume_source: state`.
e. Reset the visible checklist to the initial pre-plan state.
f. Re-enter the pipeline at **Stage 1** and include the contents of `feedback/goals-reset-context.md` as `=== PRIOR RUN LEARNINGS ===` in the Goals dispatch.
```
