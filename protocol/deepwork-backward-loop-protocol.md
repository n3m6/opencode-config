### Backward Loop Protocol

This protocol is invoked from any of the following:

- A stage subagent (`qrspi-skeleton`, `qrspi-implement`, `qrspi-accept`, `qrspi-replan`) returns a `### Backward Loop Request`. When invoked from `qrspi-skeleton` (Stage 4.5), option A (Design) is always pre-selected by the caller — the multi-option prompt is skipped (see caller note in deepwork.md Stage 4.5 handler).
- `qrspi-verify` returns FAIL and the **auto Stage 7 fix-mode pass** (see precondition below) does not recover. In that case deepwork synthesizes a backward-loop request from the verifier's failing rows before invoking this protocol.
- The Plan/Replan **unclean-cap or stable-cap escalation gate** in deepwork yields a "loop back" answer; deepwork synthesizes a backward-loop request from the reviewer's final `### Fix Guidance` and invokes this protocol with the user-chosen target.

#### Precondition: Stage 9 → Stage 7 Auto-Fix Pass

When `qrspi-verify` returns FAIL, deepwork attempts **one** Stage 7 fix-mode pass before invoking this protocol:

1. The verifier's failing rows are formatted as regression evidence.
2. Deepwork dispatches `qrspi-implement` with `=== MODE === verify-fix` and `=== VERIFY FAILURES ===` containing those rows; `qrspi-implement` runs the existing regression-remediation path, capped at one round.
3. Deepwork re-dispatches `qrspi-verify`. PASS or PARTIAL → continue to Stage 10. FAIL again → invoke this protocol with the verify failure as the loop request body.

This pass is bypassed when the user has already triggered a backward loop in this stage instance, or when `qrspi-implement` itself returned a `### Backward Loop Request`.

When this protocol is invoked from the second Stage 9 FAIL after that single fix-mode pass has already completed, do not run the precondition again. Treat the verify-fix pass as already consumed and continue directly with the backward-loop decision flow.

#### Incremental Patch Precondition (LOOP_PLAN)

When the backward loop request's `Affected Artifact` is `plan` (i.e. the backward-loop detector classified the failure as `LOOP_PLAN`), check the phase patch budget before presenting any option to the user:

1. Count unique attempted runtime Option-P patch round numbers for the current phase in `.pipeline/<run-id>/feedback/`: a round counts when either `feedback/plan-patch-phase-[NN]-round-[RR].md` or `feedback/plan-patch-phase-[NN]-round-[RR]-failed.md` exists. Count a given `RR` only once even if both files exist. `feedback/plan-patch-phase-[NN]-round-[RR]-escalation.md` does not count because the patcher returned before attempting a local patch. Do not count Stage 6 `feedback/feasibility-patch-round-*.md` files; those belong to the pre-implementation feasibility loop.
2. If the count is **less than 2** (`patch_budget_remaining = 2 - count > 0`), the default option is **P — Incremental Plan Patch** (described below). This is recommended before any destructive option.
3. If the count is **2 or more** (patch budget exhausted), option P is unavailable. Present the full option set without P as the default.

When this protocol is invoked:

1. Read the backward loop request details.
2. If the caller already has a user-chosen option from the Plan/Replan unclean-cap escalation gate, or an automated preselected option from a noninteractive run, skip the prompt in step 2 entirely. Treat that earlier choice as the protocol decision, continue directly with the matching option handler below, and do not emit a second `backward-loop-decision` gate pair; the original gate already captured the wait time and choice.
3. Otherwise, present the issue to the user via `question`:

   ```
   ### Backward Loop Detected

   **Stage:** [which stage reported it]
   **Issue:** [description from the subagent]
   **Affected Artifact:** [from the backward loop request]
   **Patch Budget:** [if LOOP_PLAN: "N of 2 patch rounds used — P is available / budget exhausted"]
   ```

[If the route is `quick-fix`, present only these options:
C) Loop back to **Plan** (revise task specifications)
E) Attempt a **local fix** within the current stage
F) **Continue as-is** (accept the limitation)
G) Full reset to **Goals** (restart the pipeline with accumulated learnings)]

Options (for LOOP_PLAN with patch budget remaining — P appears first and is recommended):
P) **Incremental Plan Patch** ⟵ Recommended for LOOP_PLAN (no deletion, no phase archive, patch budget: N remaining)
A) Loop back to **Design** (re-architect the approach; deletes design.md + skeleton-results.md + structure.md + plan artifacts)
B) Loop back to **Structure mapping** (re-run only the structure mapping sub-step; preserves skeleton-results.md and the skeleton commit — cheap re-entry)
C) Loop back to **Plan** (revise task specifications — deletes plan artifacts and phase, heavy)
D) Defer to the next **Replan** (record the issue for the next phase boundary)
E) Attempt a **local fix** within the current stage
F) **Continue as-is** (accept the limitation)
G) Full reset to **Goals** (restart the pipeline with accumulated learnings)

Options (for any other Affected Artifact, or LOOP_PLAN with patch budget exhausted):
A) Loop back to **Design** (re-architect the approach; deletes design.md + skeleton-results.md + structure.md + plan artifacts)
B) Loop back to **Structure mapping** (re-run only the structure mapping sub-step; preserves skeleton-results.md and the skeleton commit — cheap re-entry)
C) Loop back to **Plan** (revise task specifications)
D) Defer to the next **Replan** (record the issue for the next phase boundary)
E) Attempt a **local fix** within the current stage
F) **Continue as-is** (accept the limitation)
G) Full reset to **Goals** (restart the pipeline with accumulated learnings)

Which option?

```

Do not present Design or Structure mapping as loop targets on the quick-fix route.
Do not present option P on the quick-fix route.

4. **If the user (or automated policy) chooses P** (Incremental Plan Patch):

   a. Determine the failing task IDs from the backward loop request's `Affected Task IDs` field. If absent, read them from the triggering stage subagent's return.
   b. Create the feedback directory if needed: `mkdir -p .pipeline/<run-id>/feedback`
   c. Read the current `plan.md`, `phase-manifest.md`, and affected task specs from `.pipeline/<run-id>/<phase-dir>/tasks/`. For Phase 1 this resolves through the canonical tasks symlink; for later phases it preserves the phase-local task set.
   d. Dispatch `qrspi-plan-patcher` as a subagent. Include the backward loop request, failing task IDs, plan, phase manifest, affected task specs, goals, design, structure, and current feasibility results (if `feasibility-results.md` exists). Pass the current patch round number (count of existing attempted Option-P patch rounds for the current phase + 1).
   e. **If patcher returns `### Backward Loop Request`:** the local patch is impossible. Write the escalation to `feedback/plan-patch-phase-[NN]-round-[RR]-escalation.md`. Emit `backward_loop.decided` with `decision.choice: "P"`, `decision.reason: "patcher escalated to upstream"`, and `context.escalated: true`. Present the user with the remaining options (A, B, C, D, E, F, G) so they can choose the appropriate heavy fallback. The patch round does NOT count toward the budget (patcher returned immediately rather than attempting).
   f. **Otherwise:** Write the updated task specs from the patcher's returned `### task-NN.md` blocks into `.pipeline/<run-id>/<phase-dir>/tasks/`. Apply any `### plan.md (delta only)` changes to `plan.md`. Write the patch note to `feedback/plan-patch-phase-[NN]-round-[RR].md`.
   g. Run `qrspi-feasibility-checker` on the patched task specs from `.pipeline/<run-id>/<phase-dir>/tasks/` (mode: `patch`). Write the result to `feasibility-results.md`.
   h. **If feasibility PASS:** Re-enter Stage 7 in `patch` mode:
      - Dispatch `qrspi-implement` with `=== MODE === patch`, `=== PATCH TASKS === <comma-separated patched task IDs>`, and `=== PATCH ROUND === [RR]`.
      - If `qrspi-implement` returns `### Status — FAIL`, follow **Error Handling** for Stage 7 instead of advancing to Accept-Test.
      - If `qrspi-implement` returns `### Backward Loop Request`, emit the Stage 7 failure/backward-loop telemetry and re-enter this protocol using that new request. Do not mark Option P successful.
      - Create the stage-boundary checkpoint: `"qrspi: phase [N] option-P patch round [NN]"`.
      - Update `state.md`: preserve `current_phase`, increment `backward_loops`, set `next_stage: accept`.
      - Emit `backward_loop.decided` with `decision.choice: "P"`, `decision.reason`, `context.patch_tasks` (list), `context.patch_round` (N), `context.feasibility_status: "pass"`.
      - Continue to Stage 8 (Accept-Test).
   i. **If feasibility FAIL:** Write the failure summary to `feedback/plan-patch-phase-[NN]-round-[RR]-failed.md`. Decrement effective patch budget. If budget is still > 0, re-enter step 4 (dispatch patcher again with the updated round count). If budget is exhausted (2 rounds consumed), emit `backward_loop.decided` with `decision.choice: "P"`, `context.exhausted: true`, and present the user with the remaining options (A, B, C, D, E, F, G).

5. **If the user (or automated policy) chooses A, B, or C** (loop-back):
a. Determine the loop target stage (Design=4, Structure mapping=4.5, Plan=6). For option B (Structure mapping), `next_stage` is set to `skeleton`; the skeleton orchestrator's Step 0 self-routes to the mapping sub-step without re-running the skeleton build.
b. Create the feedback and archive directories if needed: `mkdir -p .pipeline/<run-id>/feedback` and `mkdir -p .pipeline/<run-id>/phases/archive`.
c. Write loop feedback to `.pipeline/<run-id>/feedback/{stage}-loop-{NN}.md` with the backward loop request details using the edit tool.
d. Before deleting or moving any active artifact, write `.pipeline/<run-id>/feedback/{stage}-loop-{NN}-evidence.md` containing:
   - the backward loop request details
   - the triggering stage and current phase
   - the current phase's `execution-manifest.md`, `integration-results.md`, `acceptance-results.md`, `stage7-summary.md`, `stage8-summary.md`, and `backward-loop-analysis.md` when present
   - the current `plan.md`, `phase-manifest.md`, and any current-phase task specs when present
   Use `N/A` for missing optional files. This evidence file is the preserved failure context for the rerun.
e. Preserve completed phase directories `phases/phase-01/` through `phases/phase-(N-1)/` unchanged.
f. Archive the current incomplete phase directory by moving it to `.pipeline/<run-id>/phases/archive/failed-phase-NN-loop-{NN}/` when it exists. Do not delete the only copy of the failed phase evidence.
g. Archive any unstarted future phase directories by moving them under `.pipeline/<run-id>/phases/archive/phase-NN/` before regenerating the remaining plan.
h. Delete regenerated top-level artifacts based on the loop target:
  - Plan: `plan.md`, `phase-manifest.md`, `baseline-results.md`, `feasibility-results.md`, and `tasks/`
  - Structure mapping (option B): `structure.md` plus all Plan artifacts. Preserve `skeleton-results.md` and the squash-merged skeleton commit — the skeleton build does not re-run, only the structure mapping step does. Set `next_stage: skeleton` so the orchestrator's Step 0 self-routes to the mapping sub-step (Step G).
  - Design (option A): all Structure mapping artifacts plus `design.md` and `skeleton-results.md`. The squash-merged skeleton commit stays on the branch (a new skeleton build will run after Design re-runs); note this in the feedback file so the Design stage is aware the skeleton code on the branch is from a prior, now-replaced, design iteration.
i. Reset the todo items for the target stage and all downstream stages to not-started, and remove stale unstarted phase entries that no longer match the active manifest.
j. Overwrite `state.md` with the loop target as `next_stage` (Design → `design`, Structure mapping → `skeleton`, Plan → `plan`), increment `backward_loops`, set `current_phase` to the earliest incomplete phase number when completed phases are preserved, reset it to `1` only when no completed phases remain or the target is before phased execution, and preserve `phase_history` for already-completed phases.
k. Re-enter the pipeline at the target stage. The re-run must receive the feedback file and evidence file as additional context.
l. When re-entering Design, Structure mapping, or Plan from Phase 2 or later, also include:

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

6. **If the user chooses D** (defer to Replan):
a. Create the feedback directory if needed: `mkdir -p .pipeline/<run-id>/feedback`
b. Write `.pipeline/<run-id>/feedback/deferred-replan-{NN}.md` with the current stage, current phase, and backward-loop request details.
c. Overwrite `state.md` with the same current phase, increment `backward_loops`, and keep the normal next stage.
d. Continue the current stage as non-blocking. The next Replan stage must read all deferred replan feedback files.
7. **If the user chooses E** (local fix): Continue the current stage, treating the issue as a non-blocking problem.
8. **If the user chooses F** (continue): Proceed to the next stage without changes.
9. **If the user chooses G** (full reset to Goals):
a. Create the feedback directory if needed: `mkdir -p .pipeline/<run-id>/feedback`
b. Write `.pipeline/<run-id>/feedback/goals-reset-context.md` containing the backward-loop request, current phase, and a concise summary of what was learned before the reset.
c. Delete every pipeline artifact except `feedback/`, including all active and archived `phases/` directories. Do NOT delete the `telemetry/` directory — preserve it as a diagnostic record of the failed run state.
d. Recreate `state.md` with `route: unknown`, `current_phase: 1`, `total_phases: 0`, `last_completed_stage: none`, `next_stage: goals`, incremented `backward_loops`, the preserved `interaction_mode` / `failure_policy` from the current run, and `resume_source: state`.
e. Reset the visible checklist to the initial pre-plan state.
f. Re-enter the pipeline at **Stage 1** and include the contents of `feedback/goals-reset-context.md` as `=== PRIOR RUN LEARNINGS ===` in the Goals dispatch.

### Automated Policy for LOOP_PLAN

When `interaction_mode = automated`:
- `failure_policy = best-effort` and patch budget remaining → automatically choose **P**. Emit `gate.presented` and `gate.approved` with `decision.choice: "P"` and reason `Automated best-effort policy: incremental patch before destructive loop-back.`
- `failure_policy = best-effort` and patch budget exhausted → automatically choose **C** (loop back to Plan). Emit `gate.approved` with `decision.choice: "C"` and reason `Automated best-effort policy: patch budget exhausted, falling back to plan loop-back.`
- `failure_policy = fail-closed` → automatically choose **C** after any patcher escalation, or follow **Error Handling** for unrecoverable states.

### Telemetry Integration

Telemetry events are emitted by deepwork around the protocol steps above:

- **Before presenting the decision to the user:** Emit `backward_loop.requested` with `stage`, `phase`, and `context` containing the loop request details.
- **When invoked with a preselected Plan/Replan loop-back target or an automated noninteractive loop target:** Deepwork still emits `backward_loop.requested` before entering the protocol, but skips the extra backward-loop decision prompt and emits the corresponding `backward_loop.decided` event directly from the preselected choice after the loop-back artifacts are determined.
- **After the user decides:**
  - Option P (incremental patch): Emit `backward_loop.decided` with `decision.choice: "P"`, `decision.reason`, `context.patch_tasks` (list of patched task IDs), `context.patch_round` (round number), `context.feasibility_status` (`pass`/`fail`/`exhausted`/`escalated`), `context.loop_target: "plan"`.
  - Options A, B, C (loop-back): Emit `backward_loop.decided` with `decision.choice` (A/B/C), `decision.reason` (user input or inferred), `context.loop_target` (design/structure-mapping/plan), `context.deleted_artifacts` (list of deleted top-level artifacts), and `context.archived_artifacts` (list of archived phase directories).
  - Option D (defer): Emit `backward_loop.deferred` with `decision.choice: "D"` and `decision.reason`.
  - Options E, F (local fix / continue): Emit `backward_loop.decided` with `decision.choice: "E"` or `"F"` and the reason.
  - Option G (full reset): Emit `backward_loop.reset` with `summary` (brief learnings summary) and `context.artifacts_deleted` (all deleted artifact paths). Note: telemetry files are NOT included in the deleted list.
- **After emitting the event:** Regenerate `telemetry/run-log.md`.
```
