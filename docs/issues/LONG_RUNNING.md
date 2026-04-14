# Long-Running Session Issues

## Status

As of 2026-04-14, the single-phase quick-fix route is in good shape, but the multi-phase full route is still not safe enough for proper long-running sessions.

The current problem is not syntax or frontmatter integrity. The agent files parse clean in the editor. The remaining risk is behavioral and contract-level:

- resume without `state.md` is not reliable enough for multi-phase runs
- phase boundaries are not encoded consistently enough across cumulative artifacts
- Replan can change the remaining plan, but deepwork does not fully refresh its control state from those changes
- backward loops in later phases can destroy earlier completed-phase history

In short: the multi-phase controller shape exists, but the recovery model is still incomplete.

## Validations Run

The following validations were run against the current agent files before writing this document.

### 1. Current-file inspection after post-edit changes

The latest versions of these files were re-read directly because they had changed since the previous implementation pass:

- `agents/deepwork.md`
- `agents/qrspi-plan-writer.md`

Additional targeted reads were used to verify the specific parts of the flow that matter for long-running sessions:

- `agents/qrspi-implement.md`
- `agents/qrspi-accept.md`
- `agents/qrspi-replan.md`
- `agents/qrspi-replan-writer.md`
- `agents/qrspi-replan-reviewer.md`
- `agents/qrspi-backward-loop-detector.md`

### 2. Editor validation on the current agent files

`get_errors` was run on the long-running-session surface:

- `agents/deepwork.md`
- `agents/qrspi-plan.md`
- `agents/qrspi-plan-writer.md`
- `agents/qrspi-implement.md`
- `agents/qrspi-accept.md`
- `agents/qrspi-backward-loop-detector.md`
- `agents/qrspi-replan.md`
- `agents/qrspi-replan-writer.md`
- `agents/qrspi-replan-reviewer.md`
- `agents/qrspi-verify.md`
- `agents/qrspi-report.md`

Result:

- no editor-reported errors were found in any of those files

### 3. Dry-run contract audit for the quick-fix route

A dry-run audit of the quick-fix route was run after the recent fixes.

Scope:

- Goals → Questions → Research → Plan → Implement → Accept → Verify → Report

Result:

- quick-fix is internally consistent
- phase naming, quick-fix current phase dispatch, and invalid loopback options were fixed
- quick-fix is not the source of the remaining long-running-session problems

### 4. Dry-run contract audit for a two-phase full route with resume and replan

A dry-run audit was run for the long-running scenario that matters here:

1. Stage 6 produces a two-phase plan
2. Phase 1 runs Implement and Accept
3. Replan runs
4. Phase 2 runs Implement and Accept
5. Resume is simulated once with `state.md` present
6. Resume is simulated once with `state.md` missing so disk artifacts must drive recovery

This was the main validation used to identify the issues below.

### 5. Manual verification of audit claims

The dry-run audit output was checked manually against the current files before being written into this document.

Two example claims from an earlier audit were not carried forward because they were no longer current:

- deepwork **does** now contain a Stage 8.5 Replan section
- deepwork **does** now document a `state.md` write after Replan returns

Only the issues that still hold against the current files are listed below.

## Validation Constraints

These constraints are important for interpreting the findings.

### No executable pipeline harness in this repo

This repository contains agent definitions and prompt contracts, not a runnable end-to-end pipeline harness. That means the validations performed here are:

- contract audits
- file and prompt-flow inspection
- editor validation

They are **not** true runtime executions of an Opencode session.

### Recovery behavior is prompt-driven, not code-enforced

The recovery model depends on what deepwork and the stage agents are instructed to do with:

- `state.md`
- `phase-manifest.md`
- cumulative Stage 7 / Stage 8 artifacts
- feedback files

Because these are prompt contracts rather than code-enforced hooks, underspecified behavior is a real bug. If the contract does not clearly say how to recover, different runs can behave differently.

### Shared top-level artifacts make phase recovery harder

The multi-phase design currently keeps several outputs in shared top-level files instead of phase-scoped files. That increases ambiguity during:

- resume without `state.md`
- phase-local backward loops
- Replan updates to the remaining work

## Outstanding Issues

### 1. Resume fallback is not phase-aware when `state.md` is missing

The fallback recovery logic in `agents/deepwork.md` is still too coarse for multi-phase runs.

Current behavior:

- it checks whether `stage7-summary.md` exists
- it checks whether `stage8-summary.md` exists
- it does **not** include a Replan completion marker in the recovery map
- it does not define how to infer the current phase from cumulative artifacts

Why this matters:

- after Phase 1 Accept, the run may need to enter Replan
- after Replan, the run may need to enter Phase 2 Implement
- without `state.md`, the current completion map cannot reliably distinguish those states

Practical effect:

- resume can re-enter the wrong stage
- resume can re-enter the wrong phase
- deepwork can mistake a phase boundary for a mid-phase interruption

Smallest fix:

- add Replan completion to the artifact recovery map
- define an explicit fallback recovery algorithm for multi-phase runs, not just a list of marker files

### 2. `state.md` is not rich enough for interrupted long-running work

`state.md` exists, but the contract is still underspecified for the kinds of interruptions that matter in long-running sessions.

What is missing:

- no explicit in-progress marker for Replan
- no explicit distinction between "replan writer ran" and "replan review loop completed"
- no transaction marker for partially-written Replan outputs
- no clear update rules for `phase_history` across all stage transitions
- no explicit rule for how `stages_completed` is maintained beyond a few stage examples

Why this matters:

- if interruption happens mid-Replan, deepwork cannot safely tell whether the plan on disk is authoritative or partial
- if interruption happens during a review loop, there is no contract for whether to resume the loop or restart it

Practical effect:

- resume is only reliable while `state.md` remains intact and semantically correct
- once `state.md` is stale, incomplete, or missing, recovery becomes guesswork

Smallest fix:

- extend the `state.md` contract with fields such as `in_progress_stage`, `in_progress_substep`, `replan_status`, and explicit `phase_history` update rules
- optionally add an on-disk in-progress marker for Replan

### 3. Replan can change the remaining phase structure, but deepwork does not fully refresh control state from the new manifest

The Replan stage is allowed to update `phase-manifest.md` and the remaining plan. Deepwork currently increments `current_phase` after Replan, but it does not clearly re-read the updated manifest and refresh its control model from it.

Why this matters:

- Replan may add remaining tasks
- Replan may split remaining tasks
- Replan may change how much work remains in future phases
- Replan may change the number or shape of remaining phases

Current gap:

- deepwork increments the phase number
- but it does not clearly say it recomputes `total_phases` from the updated `phase-manifest.md`
- it also does not clearly rebuild the visible checklist from the updated manifest

Practical effect:

- `total_phases` in `state.md` can become stale
- todowrite can drift from the actual remaining plan
- deepwork can believe the run is on Phase N+1 while the new manifest describes a different remaining structure

Smallest fix:

- after Replan returns, deepwork should re-read `phase-manifest.md`, recompute `total_phases`, and rebuild phase-scoped checklist entries from the new manifest before dispatching the next Implement stage

### 4. Multi-phase cumulative artifacts do not have a complete, canonical phase schema

The design moved several files to cumulative, cross-phase artifacts. That is reasonable, but the schema is not yet defined consistently enough.

What is currently better:

- `execution-manifest.md` now has a `Phase` column in `agents/qrspi-implement.md`

What is still incomplete:

- `acceptance-results.md` is described as cumulative, but Stage 8 does not define a canonical per-phase section layout in the artifact itself
- `coverage-plan.md` is cumulative, but no canonical per-phase layout is specified
- `integration-results.md` is cumulative, but no explicit phase encoding is defined in the artifact format
- `stage7-summary.md`, `stage7-integration-summary.md`, and `stage8-summary.md` all say "preserve prior phase sections" without defining an exact section format

Why this matters:

- these files are part of resume and audit behavior
- if phase boundaries are not encoded consistently, deepwork and later stages cannot reliably separate Phase 1 from Phase 2

Practical effect:

- recovery without `state.md` becomes much harder
- report generation and backward-loop reasoning must infer phase boundaries from prose instead of a schema

Smallest fix:

- require an explicit `## Phase N` section format or an explicit `Phase` column in every cumulative artifact that can span multiple phases

### 5. Backward-loop cleanup is phase-destructive

The backward-loop protocol in `agents/deepwork.md` still says to delete artifacts from the loop target stage onward.

That is acceptable in a single-pass pipeline, but it is unsafe in a multi-phase pipeline because several files are now cumulative across phases:

- `execution-manifest.md`
- `stage7-summary.md`
- `integration-results.md`
- `stage7-integration-summary.md`
- `acceptance-results.md`
- `stage8-summary.md`

Why this matters:

- a Phase 2 backward loop to Plan or Design should not erase valid Phase 1 history
- current cleanup language is stage-scoped, not phase-scoped

Practical effect:

- a later-phase loopback can destroy previously-completed phase history
- this breaks the audit trail and weakens resume safety

Smallest fix:

- either move to phase-scoped result files, or define phase-aware cleanup rules that preserve completed-phase history while resetting only the affected current and downstream phase state

### 6. Replan-updated tasks do not carry a defined review-status handoff into Implement

Stage 7 expects to pass a task's plan review status into implementation. That assumption holds for tasks produced by Stage 6 Plan, but it is not clearly maintained for tasks that are changed by Replan.

Current behavior:

- Stage 6 appends a `Review Status` block to task files
- Replan can overwrite or replace remaining task files
- Replan's documented task output does not define a `Review Status` handoff contract for those updated tasks

Why this matters:

- `qrspi-implement` wants to pass `PLAN REVIEW STATUS` to the implementer
- a replanned task may now be current, but not clearly annotated as reviewed, unreviewed, or newly-replanned

Practical effect:

- Stage 7 has an ambiguous input contract for tasks changed after Plan
- implementation risk signaling becomes inconsistent exactly where long-running runs need it most

Smallest fix:

- define a standard status for Replan-updated tasks, such as `NOT_YET` or `REPLANNED`, and require Stage 7 to handle it explicitly
- or have Replan append its own review-status block to each changed task after the Replan review loop finishes

### 7. Superseded task files are preserved for audit, but not separated from the current remaining task set

`agents/qrspi-replan.md` explicitly keeps superseded task files as audit artifacts unless they are overwritten. That preserves history, but the downstream contract does not yet distinguish active tasks from historical ones strongly enough.

Why this matters:

- `qrspi-implement` reads all `tasks/task-*.md` files before phase filtering
- there is no documented validation that every task listed in the active `phase-manifest.md` exists as a current file
- there is no separate archive location for superseded tasks

Practical effect:

- stale task files remain in the same namespace as active task files
- resume and manual inspection can become confusing after multiple Replan cycles
- a missing active task file is not proactively validated before execution begins

Smallest fix:

- validate that every task referenced by the current `phase-manifest.md` exists before Stage 7 begins
- move superseded tasks to an explicit archive area, or define a current-task marker convention

## Issues Surfaced But Not Carried Forward

During auditing, a few findings were surfaced and then rejected after manual verification against the current files.

These are **not** current outstanding issues:

- "deepwork has no Replan section" — no longer true
- "deepwork does not write `state.md` after Replan" — no longer true
- "quick-fix route is still internally inconsistent" — no longer true

They are listed here only to make it clear that this document was filtered against the current repository state.

## Recommended Priority Order

If this area is addressed in follow-up work, the order should be:

1. Make resume safe without `state.md`
2. Make Replan refresh deepwork's control state from the updated manifest
3. Make cumulative artifacts phase-structured and machine-readable
4. Make backward-loop cleanup phase-aware
5. Make Replan-to-Implement task review handoff explicit
6. Separate active tasks from superseded historical tasks

Until those are addressed, the multi-phase route should be treated as experimental for long-running sessions.
