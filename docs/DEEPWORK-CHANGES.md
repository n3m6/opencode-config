# Deepwork Pipeline Changes — 2026-06-20

A summary of the changes made to the QRSPI pipeline today.

## Why

Implementation kept discovering plan, structure, and design flaws late, forcing
expensive global backward loops that destroyed completed work. The day's work
overhauled the pipeline to validate the design empirically *before* planning
locks, and to make recovery from late-discovered flaws incremental instead of
destructive. The work landed in three conceptual packages plus a documentation
pass and two rounds of dry-run fixes.

## Changes

### Documentation refresh (commit `2b11267`, 12:35)

- Updated `docs/DEEPWORK.md` to reflect current output files, new review paths,
  and clarified pipeline stages for the goal-inventory and verification flows.

### Package 1 — Walking skeleton + incremental re-queue (commit `a878117`, 14:55)

- **New Stage 4.5 — Skeleton.** Added `qrspi-skeleton`, which builds the thinnest
  end-to-end slice of the design in an isolated git worktree to prove the design
  is implementable before Plan locks. A passing skeleton is squash-merged onto
  the pipeline branch; a failing one is cheap to discard (no plan or phases exist
  yet) and routes straight back to Design.
- **Checklist-first task specs + feasibility gate.** Added `qrspi-feasibility-checker`,
  a pre-implementation gate that runs each task spec's machine-checkable
  `## Feasibility Checklist` (`path-exists:`, `symbol-exists:`, `import-resolves:`,
  `command-exits-0:`) against the real codebase before any build begins.
- **Incremental plan patching (Option P).** Added `qrspi-plan-patcher`, which
  regenerates only the failing task subgraph in place (stable IDs, no deletions)
  instead of looping the whole pipeline back. Wired into both Stage 6 (on
  feasibility failure, max 2 rounds) and the runtime backward-loop protocol as
  the recommended default for `LOOP_PLAN`.
- Updated `qrspi-plan`, `qrspi-plan-writer`, `qrspi-implement`,
  `qrspi-task-spec-writer`, `qrspi-task-spec-reviewer`, the backward-loop and
  resume protocols, and the controller to integrate the new stage and agents.

### Package 1 dry-run fixes (commit `5ff1b1f`, 15:39)

- Stage 4.5 backward loop now pre-selects Option A (Design) regardless of
  interaction mode, since Structure/Plan/phases don't exist yet — avoids
  presenting invalid B/C/D/P options.
- Fixed `state.md` transitions: `next_stage` is always `design` after Research
  (the Stage 4 handler owns the quick-fix skip chain); added `skeleton` to the
  valid `next_stage`/`last_completed_stage` ordering and the examples; removed the
  legacy `questions` stage left over from the Stage 2 merge.
- Registered `qrspi-skeleton` as a valid backward-loop invoker across the
  controller and protocol files; fixed the metrics-summary and run-log examples.

### Package 2 — Reorder Skeleton before Structure + lighter Design (commit `7b83144`, 18:10)

- **Skeleton now runs before Structure**, so the structure map and the plan are
  grounded in real, merged skeleton code rather than a purely theoretical design.
- **Lighter Design.** `qrspi-design-synthesizer` and `qrspi-design-reviewer` were
  trimmed to approaches, conceptual architectural patterns, vertical slices, and
  the slice dependency DAG. Design no longer produces a Mermaid system diagram.
- **Structure owns the system diagram.** `qrspi-structure-mapper` now produces the
  authoritative `## System Architecture` diagram, grounded in verified
  existing/skeleton modules and planned `CREATE` entries.

### Package 3 — Fold Structure into the Skeleton stage (commit `2d40dd7`, 18:58)

- **Merged stages.** `qrspi-skeleton` now orchestrates both the skeleton build and
  the structure mapping + review loop in one Stage 4.5 (Skeleton+Structure). The
  standalone `agents/qrspi-structure.md` orchestrator was deleted.
- **No Structure human gate.** Goals and Design remain the only two human gates.
  The structure review loop caps at 5 automated rounds; `unclean-cap` proceeds
  without a gate, relying on the Plan reviewer and feasibility checker downstream.
- **Internal resume checkpoint.** `skeleton-results.md` (PASS) acts as an internal
  sub-stage checkpoint: if a run is interrupted after the skeleton build but
  before structure mapping, resume re-enters only the mapping sub-step (Step G) —
  the build and squash-merge do not re-run.
- **Backward loops re-wired.** Option B (loop to Structure) now re-enters only the
  mapping sub-step (deletes `structure.md` + Plan artifacts, preserves
  `skeleton-results.md` and the skeleton commit, sets `next_stage: skeleton`).
  Option A (loop to Design) now also deletes `skeleton-results.md`.
- **Quick-fix simplified.** The quick-fix route now skips Stages 4 and 4.5 (no more
  `structure-skipped` state value).
- Updated `agents/deepwork.md`, `protocol/deepwork-resume-protocol.md`,
  `protocol/deepwork-backward-loop-protocol.md`, and `docs/DEEPWORK.md`.

### Package 3 dry-run verification fixes (in commit `2d40dd7`)

- `protocol/telemetry-protocol.md`: replaced the stale `Structure (5)` standard-
  context row with a `Skeleton+Structure (4.5)` row matching the fields
  `qrspi-skeleton` actually returns, and corrected the `terminal_review_state`
  note so Structure no longer claims a human gate.
- `agents/qrspi-skeleton.md`: added `skeleton-task.md` to both FAIL return
  templates (it is always written before any failure) and specified an explicit
  return format for the Step 0 early-PASS resume case.

## Net pipeline shape

```
Goals → Research → Design → Skeleton+Structure (4.5) → Plan → [Implement → Accept-Test → Replan]* → Verify → Report
```

Quick-fix still skips Stages 4 and 4.5:

```
Goals → Research → Plan → Implement → Accept-Test → Verify → Report
```
