# Fix Multi-Phase Controller for Long-Running Sessions

All 7 issues from [LONG_RUNNING.md](../issues/LONG_RUNNING.md) stem from the same root cause: the pipeline was designed around single-phase execution and later extended to multi-phase without fully adapting the state model, artifact layout, and cleanup rules. This plan restructures the pipeline around **phase-scoped directories** and fixes each issue systematically.

## Design Decisions (Agreed)

| Decision | Choice | Rationale |
|---|---|---|
| Artifact layout | **Phase-scoped directories** under `phases/phase-NN/` | Clean separation; resume becomes trivial; backward loops can't destroy completed phases |
| Task resolution | **Full copy, uniform structure** — every phase reads from `phases/phase-NN/tasks/` | Implementer has one consistent location per phase |
| Phase 1 tasks | **Symlink** `phases/phase-01/tasks/ → ../../tasks/` created during Stage 6 | Avoids duplication while maintaining uniform structure |
| Phase 2+ tasks | Replan writes **complete task set** into `phases/phase-NN/tasks/` | Each phase is self-contained |
| Recovery granularity | **Stage-level** — if interrupted mid-stage, restart the entire stage | Pragmatic for prompt-driven agents; avoids sub-step checkpointing complexity |
| Backward loop context | Pass **full completed phase artifacts + failure context** when re-entering Plan from Phase 2+ | Prevents duplicate/conflicting work with already-implemented code |
| Replan task review status | Replan appends **same review status format** as Stage 6 | Simple and uniform |
| Pre-implement validation | `qrspi-implement` validates tasks against manifest | Catches missing tasks before execution |
| Cross-phase reporting | Reporter agent reads across `phases/phase-*/` itself | No pre-merge step needed from deepwork |

---

## Proposed Changes

### Component 1 — Directory Layout & Pipeline Files Convention

The new directory structure replaces the flat cumulative artifact layout with phase-scoped isolation:

```
.pipeline/qrspi-<run-id>/
├── state.md                          # Deepwork recovery state
├── config.md                         # Route, metadata (Stage 1)
├── goals.md                          # Stage 1
├── questions.md                      # Stage 2
├── question-leakage-review.md        # Stage 2
├── question-quality-review.md        # Stage 2
├── research/                         # Stage 3
│   ├── q-01.md ... q-NN.md
│   └── summary.md
├── design.md                         # Stage 4 (full route only)
├── structure.md                      # Stage 5 (full route only)
├── plan.md                           # Stage 6 (initial; updated by Replan)
├── phase-manifest.md                 # Stage 6 (initial; updated by Replan)
├── baseline-results.md               # Stage 6
├── tasks/                            # Stage 6 (original task specs)
│   └── task-NN.md
├── reviews/                          # All automated review history
│   ├── goals-review-round-NN.md
│   ├── research-review-round-NN.md
│   ├── design-review-round-NN.md
│   ├── structure-review-round-NN.md
│   ├── plan-review-round-NN.md
│   ├── acceptance-phase-NN-review-round-MM.md
│   └── replan-review-round-NN.md
├── feedback/                         # Backward loops, rejections
│   ├── {step}-round-NN.md
│   ├── {stage}-loop-{NN}.md
│   ├── deferred-replan-NN.md
│   └── goals-reset-context.md
│
├── phases/                           # Phase-scoped execution artifacts
│   ├── phase-01/
│   │   ├── tasks/                    # → ../../tasks/ (symlink for Phase 1)
│   │   ├── execution-manifest.md     # Stage 7
│   │   ├── stage7-summary.md         # Stage 7
│   │   ├── integration-results.md    # Stage 7
│   │   ├── stage7-integration-summary.md  # Stage 7
│   │   ├── coverage-plan.md          # Stage 8
│   │   ├── acceptance-results.md     # Stage 8
│   │   ├── backward-loop-analysis.md # Stage 8 (if applicable)
│   │   ├── stage8-summary.md         # Stage 8
│   │   └── replan/                   # Stage 8.5
│   │       └── phase-01-replan.md
│   ├── phase-02/
│   │   ├── tasks/                    # Real copies from Replan
│   │   │   └── task-NN.md
│   │   ├── execution-manifest.md
│   │   ├── stage7-summary.md
│   │   ├── ... (same structure)
│   │   └── stage8-summary.md
│   └── ...
│
├── stage9-summary.md                 # Verify (post all phases)
└── stage10-summary.md                # Report (post all phases)
```

> [!IMPORTANT]
> The top-level `tasks/` directory remains as the canonical Stage 6 output. `phases/phase-01/tasks/` is a symlink to it. Phase 2+ directories contain real copies written by Replan. The implementer always reads from `phases/phase-NN/tasks/` regardless of phase number.

---

### Component 2 — deepwork.md (Primary Agent)

#### [MODIFY] `agents/deepwork.md`

**Change 1 — Pipeline Files Convention section (lines 180–224)**

Replace the current flat file layout documentation with the new phase-scoped directory layout shown in Component 1 above. Update all file path references to reflect the new structure.

**Change 2 — Pre-Flight section (lines 241–277)**

After creating the pipeline directory, also create the `phases/` parent directory:

```
mkdir -p .pipeline/qrspi-<run-id>/phases
```

**Change 3 — Stage 6 post-processing (lines 367–388)**

After `qrspi-plan` returns successfully, add new steps:

1. Read `phase-manifest.md` to determine `total_phases`
2. Create `phases/phase-01/` directory: `mkdir -p .pipeline/qrspi-<run-id>/phases/phase-01/tasks`
3. Create symlink: create a symlink from `phases/phase-01/tasks/` pointing to `../../tasks/`
4. If multi-phase, create empty phase dirs for planned phases: `mkdir -p .pipeline/qrspi-<run-id>/phases/phase-NN` for each phase in the manifest

> [!IMPORTANT]
> The symlink command needs to be added to deepwork's bash permission allowlist: `"ln -s *": allow`

**Change 4 — Stage 7 dispatch (lines 390–418)**

Update the dispatch prompt to include the phase directory path:

```
=== PHASE DIR ===
phases/phase-[NN]
```

So `qrspi-implement` knows where to read tasks and write outputs.

**Change 5 — Stage 8 dispatch (lines 420–446)**

Update the dispatch prompt to include:

```
=== PHASE DIR ===
phases/phase-[NN]
```

So `qrspi-accept` knows where to read phase results and write outputs.

**Change 6 — Stage 8.5 Replan post-processing (lines 448–476)**

After `qrspi-replan` returns, add a **manifest refresh protocol**:

1. Re-read the updated `phase-manifest.md` using `cat`
2. Recompute `total_phases` from the updated manifest
3. Create the next phase directory: `mkdir -p .pipeline/qrspi-<run-id>/phases/phase-[N+1]/tasks`
4. Rebuild the visible `todowrite` checklist from the updated manifest — remove stale phase entries and add new ones if phases were added/removed by Replan
5. Overwrite `state.md` with the refreshed `total_phases`, incremented `current_phase`, and `next_stage: implement`

**Change 7 — Resume Mode fallback algorithm (lines 120–146)**

Replace the current coarse recovery map with a phase-aware algorithm:

```
RECOVERY ALGORITHM (without state.md):

1. Read config.md → get route
2. Check pre-phase completion markers:
   - goals.md exists            → Goals complete
   - questions.md exists        → Questions complete
   - research/summary.md exists → Research complete
   - design.md exists (or quick-fix) → Design complete
   - structure.md exists (or quick-fix) → Structure complete
   - baseline-results.md exists → Plan complete

3. Scan phase directories: ls phases/phase-*/
   For each phase dir (phase-01, phase-02, ...) in numeric order:
   a. phases/phase-NN/stage7-summary.md exists → Implement complete for phase NN
   b. phases/phase-NN/stage8-summary.md exists → Accept-Test complete for phase NN
   c. phases/phase-NN/replan/ contains phase-NN-replan.md → Replan complete for phase NN

4. Determine current_phase:
   - highest phase number with ANY artifact present inside phases/phase-NN/
   - if no phase dirs exist, current_phase = 1

5. Determine next_stage:
   - if current phase has no stage7-summary.md → next_stage = implement
   - if current phase has stage7-summary.md but no stage8-summary.md → next_stage = accept
   - if current phase has stage8-summary.md but no replan output:
     - read phase-manifest.md for total_phases
     - if current_phase < total_phases → next_stage = replan
     - if current_phase = total_phases or route = quick-fix → next_stage = verify

6. Post-phase checks:
   - stage9-summary.md exists → next_stage = report
   - stage10-summary.md exists → run complete

7. Reconstruct state.md from inferred values with resume_source: artifacts
```

**Change 8 — `state.md` contract (lines 148–178)**

Add `replan` to the `stages_completed` vocabulary and to `phase_history.completed_stages`. Example after Phase 1 Replan completes:

```yaml
---
run_id: qrspi-20260414-181500
route: full
current_phase: 2
total_phases: 3
last_completed_stage: replan
next_stage: implement
stages_completed:
  - goals
  - questions
  - research
  - design
  - structure
  - plan
  - implement
  - accept
  - replan
phase_history:
  - phase: 1
    completed_stages:
      - implement
      - accept
      - replan
backward_loops: 0
resume_source: state
---
```

**Change 9 — Backward Loop Protocol (lines 510–567)**

Replace the current "delete artifacts from the target stage onward" cleanup language with **phase-aware cleanup rules**:

```
BACKWARD LOOP CLEANUP RULES:

For any phase N backward loop (options A, B, C):

1. PRESERVE completed phase directories:
   - All phases/phase-01/ through phases/phase-(N-1)/ remain untouched

2. DELETE current incomplete phase artifacts:
   - rm -rf .pipeline/qrspi-<run-id>/phases/phase-NN/

3. DELETE regenerated top-level artifacts based on target:
   - If target = Plan (C):  delete plan.md, phase-manifest.md, baseline-results.md, tasks/
   - If target = Structure (B): also delete structure.md
   - If target = Design (A): also delete design.md and structure.md

4. PASS completed phase context AND failure context to the re-entered stage:
   - When re-entering Plan (or Design/Structure) from Phase 2+, deepwork
     includes two context blocks in the dispatch prompt:

     === COMPLETED PHASES CONTEXT ===
     For each completed phase (phase-01 through phase-(N-1)):
       - Full execution-manifest.md
       - Full integration-results.md
       - Full acceptance-results.md
       - stage7-summary.md
       - stage8-summary.md

     === FAILURE CONTEXT ===
       - The backward-loop analysis from the current phase
         (phases/phase-NN/backward-loop-analysis.md)
       - The loop feedback file from feedback/{stage}-loop-{NN}.md
       - Any relevant stage7/stage8 summaries from the failed phase

5. After the target stage re-runs:
   - Recreate phase directories for the new plan
   - Create symlink/copies for tasks as in the original flow

For full reset to Goals (option G):
- Delete every pipeline artifact EXCEPT feedback/
- Delete all phases/ directories
- Recreate state.md with route: unknown, next_stage: goals
```

**Change 10 — Permission update**

Add to the bash permission allowlist:

```yaml
"ln -s *": allow
```

---

### Component 3 — qrspi-plan.md (Stage 6 Orchestrator)

#### [MODIFY] `agents/qrspi-plan.md`

**Change 1 — Step B directory creation (line 61)**

Add phase-01 directory and tasks symlink creation:

```
mkdir -p .pipeline/<run-id>/phases/phase-01
```

The symlink creation will be handled by deepwork after the Plan stage returns (deepwork has `ln -s` permission; qrspi-plan does not).

**Change 2 — Bash permissions**

No change needed — qrspi-plan already has `mkdir` permission. The symlink is created by deepwork.

---

### Component 4 — qrspi-implement.md (Stage 7 Orchestrator)

#### [MODIFY] `agents/qrspi-implement.md`

**Change 1 — Input section (lines 33–39)**

Add `PHASE DIR` as a new input from deepwork:

```
4. **Phase Dir** — the relative path to the current phase directory (e.g., `phases/phase-01`)
```

**Change 2 — Step A — Read Inputs (lines 41–62)**

Replace task and output file reads to use phase-scoped paths:

```
- cat .pipeline/<run-id>/<phase-dir>/tasks/task-*.md (read from phase directory)
```

Remove the "detect prior phase outputs" logic (lines 57–62). Each phase directory is self-contained — no need to "preserve prior phase history" because prior phases live in separate directories.

**Change 3 — New Step A.5 — Pre-Implement Validation Gate**

Insert a new validation step after reading inputs:

```
### Step A.5 — Validate Task Files Against Manifest

Read phase-manifest.md and extract the list of task numbers assigned to the current phase.
For each task number in the manifest:
  - Verify that <phase-dir>/tasks/task-NN.md exists
  - If any task file is missing, return FAIL immediately:

### Status — FAIL
### Phase — [current phase number]
### Files Written — []
### Summary — Phase [N]: task-NN.md is listed in phase-manifest.md
  but not found in <phase-dir>/tasks/. Cannot proceed with implementation.
```

**Change 4 — Step D — Write Execution Manifest (lines 136–145)**

Change all output paths from top-level to phase-scoped:

```
- Write execution manifest to .pipeline/<run-id>/<phase-dir>/execution-manifest.md
- Write stage summary to .pipeline/<run-id>/<phase-dir>/stage7-summary.md
```

Remove all "preserving prior phase rows" / "preserving prior phase sections" language — each phase writes its own fresh files.

**Change 5 — Step E — Integration Check (lines 149–198)**

Update integration output paths:

```
- Write to .pipeline/<run-id>/<phase-dir>/integration-results.md
- Write to .pipeline/<run-id>/<phase-dir>/stage7-integration-summary.md
```

For multi-phase runs, pass completed phase context to the integration checker so it can check cross-phase compatibility:

```
=== COMPLETED PHASE SUMMARIES ===
[for each completed prior phase: paste execution-manifest.md and integration-results.md]
```

Remove "preserving prior phase sections" language.

**Change 6 — Return contract (lines 200–228)**

Update `### Files Written` to reference phase-scoped paths.

---

### Component 5 — qrspi-accept.md (Stage 8 Orchestrator)

#### [MODIFY] `agents/qrspi-accept.md`

**Change 1 — Input section (lines 34–39)**

Add `PHASE DIR` as a new input from deepwork.

**Change 2 — Step A — Read Inputs (lines 41–74)**

Change reads to use phase-scoped paths for phase artifacts:

```
- cat .pipeline/<run-id>/<phase-dir>/execution-manifest.md
- cat .pipeline/<run-id>/<phase-dir>/integration-results.md
```

Remove the "detect prior acceptance outputs" logic (lines 70–74) — each phase writes its own files.

**Change 3 — Step C — Write Tester Artifacts (lines 124–128)**

Change all output paths to phase-scoped:

```
- Write coverage-plan.md to .pipeline/<run-id>/<phase-dir>/coverage-plan.md
- Write acceptance-results.md to .pipeline/<run-id>/<phase-dir>/acceptance-results.md
```

Remove "preserving prior phase sections" / "preserving prior phase rows" language.

**Change 4 — Step D — Backward-Loop Detector dispatch (lines 130–183)**

Update to pass phase-scoped paths for execution and acceptance artifacts.

**Change 5 — Step E — Write Stage Summary (lines 188–200)**

Write to phase-scoped path:

```
- Write to .pipeline/<run-id>/<phase-dir>/stage8-summary.md
```

Remove "preserving prior phase sections" language.

**Change 6 — Backward-loop analysis output (line 186)**

Write to phase-scoped path:

```
- Write to .pipeline/<run-id>/<phase-dir>/backward-loop-analysis.md
```

**Change 7 — Return contract**

Update `### Files Written` to reference phase-scoped paths.

---

### Component 6 — qrspi-replan.md (Stage 8.5 Orchestrator)

#### [MODIFY] `agents/qrspi-replan.md`

**Change 1 — Input section (lines 33–41)**

Add two new inputs from deepwork:

```
4. **Completed Phase Dir** — path to the completed phase directory (e.g., `phases/phase-01`)
5. **Next Phase Dir** — path to the next phase directory (e.g., `phases/phase-02`)
```

**Change 2 — Step A — Read Inputs (lines 43–63)**

Replace reads of cumulative top-level artifacts with phase-scoped reads:

```
- cat .pipeline/<run-id>/<completed-phase-dir>/execution-manifest.md
- cat .pipeline/<run-id>/<completed-phase-dir>/integration-results.md
- cat .pipeline/<run-id>/<completed-phase-dir>/acceptance-results.md
- cat .pipeline/<run-id>/<completed-phase-dir>/stage7-summary.md
- cat .pipeline/<run-id>/<completed-phase-dir>/stage8-summary.md
```

For multi-phase context (Phase 3+ replan), also read summaries from all prior completed phase dirs.

**Change 3 — Step B — Create Working Directories (lines 65–68)**

Add next phase directory creation:

```
mkdir -p .pipeline/<run-id>/<next-phase-dir>/tasks
mkdir -p .pipeline/<run-id>/<completed-phase-dir>/replan
```

**Change 4 — Step C — Task output destination (line 156)**

Change task file writes from top-level `tasks/` to next-phase-scoped directory:

```
- Write each task-NN.md to .pipeline/<run-id>/<next-phase-dir>/tasks/task-NN.md
```

**Change 5 — Replan note output (line 157)**

Write to the completed phase's replan directory:

```
- Write to .pipeline/<run-id>/<completed-phase-dir>/replan/phase-[PP]-replan.md
```

**Change 6 — New Step E — Append Review Status to Task Specs**

Add a new step after the review loop completes (mirroring Stage 6's Step E):

```
### Step E — Append Review Status to Task Specs

After the review loop ends, append a review status block to every task file
in <next-phase-dir>/tasks/:

## Review Status
- **State:** [clean (round NN) or unclean-cap (round 5)]
- **Outstanding Concerns:** ["None." if clean, otherwise paste final review summary]
```

This directly fixes **Issue 6** — replanned tasks now carry the same review status contract as Stage 6 tasks.

---

### Component 7 — qrspi-replan-writer.md (Replan Writer Leaf)

#### [MODIFY] `agents/qrspi-replan-writer.md`

**Change 1 — Input documentation**

Update to clarify that execution/integration/acceptance inputs come from the completed phase directory (not cumulative top-level files).

**Change 2 — Output format (lines 58–90)**

Update task output instructions to clarify that task files represent the **complete set for the next phase**, not incremental updates to a shared task directory:

```
### task-NN.md
[one section for EVERY task assigned to the next phase — both carried-forward
unchanged tasks and new/modified tasks. This must be a complete set.]
```

---

### Component 8 — qrspi-backward-loop-detector.md

#### [MODIFY] `agents/qrspi-backward-loop-detector.md`

**Change 1 — Input documentation (lines 28–40)**

Update to note that execution/integration/acceptance inputs come from the current phase directory. Add **Completed Phase Summaries** as an optional input for multi-phase context:

```
11. **Completed Phase Summaries** — optional summary of prior completed phases
    (execution manifests and acceptance results from phases/phase-01/ through
    phases/phase-(N-1)/)
```

---

### Component 9 — qrspi-verify.md & qrspi-verifier.md (Stage 9)

#### [MODIFY] `agents/qrspi-verify.md`

**Change 1 — Step A — Read Inputs (lines 39–44)**

Replace reads of top-level cumulative artifacts with reads across all phase directories:

```
- ls .pipeline/<run-id>/phases/phase-*/
- For each phase dir: cat phases/phase-NN/execution-manifest.md
- For each phase dir: cat phases/phase-NN/acceptance-results.md
- cat .pipeline/<run-id>/baseline-results.md
```

**Change 2 — Step B — Verifier dispatch**

Update the dispatch prompt to include phase-scoped execution and acceptance data:

```
=== EXECUTION MANIFEST (ALL PHASES) ===
[for each phase dir: headed with "## Phase N", paste that phase's execution-manifest.md]

=== ACCEPTANCE RESULTS (ALL PHASES) ===
[for each phase dir: headed with "## Phase N", paste that phase's acceptance-results.md]
```

---

### Component 10 — qrspi-report.md & qrspi-reporter.md (Stage 10)

#### [MODIFY] `agents/qrspi-report.md`

**Change 1 — Step A — Read Inputs (lines 37–57)**

Replace reads of top-level cumulative artifacts with reads across all phase directories:

```
- ls .pipeline/<run-id>/phases/phase-*/
- For each phase dir:
  - cat phases/phase-NN/stage7-summary.md
  - cat phases/phase-NN/stage7-integration-summary.md
  - cat phases/phase-NN/stage8-summary.md
  - cat phases/phase-NN/acceptance-results.md
- ls .pipeline/<run-id>/phases/phase-*/replan/
- For each replan dir: cat the replan notes
```

**Change 2 — Step B — Reporter dispatch (lines 59–101)**

Restructure the dispatch prompt to organize inputs by phase:

```
=== STAGE SUMMARIES ===

## Phase 1
Stage 7 — Implementation: [paste phases/phase-01/stage7-summary.md]
Stage 7 — Integration: [paste phases/phase-01/stage7-integration-summary.md]
Stage 8 — Acceptance: [paste phases/phase-01/stage8-summary.md]
Replan Note: [paste phases/phase-01/replan/phase-01-replan.md or "N/A"]

## Phase 2
Stage 7 — Implementation: [paste phases/phase-02/stage7-summary.md]
...

=== ACCEPTANCE RESULTS (ALL PHASES) ===
## Phase 1
[paste phases/phase-01/acceptance-results.md]
## Phase 2
[paste phases/phase-02/acceptance-results.md]

Stage 9 — Verification: [paste stage9-summary.md]
```

#### [MODIFY] `agents/qrspi-reporter.md`

**Change 1 — Input documentation**

Add note that stage summaries and acceptance results are now organized by phase.

**Change 2 — Output format (lines 29–79)**

Add per-phase sections to the report structure:

```
### Per-Phase Results

#### Phase 1
- **Implementation**: [Stage 7 summary for phase 1]
- **Integration**: [Stage 7 integration summary for phase 1]
- **Acceptance**: [Stage 8 summary for phase 1]
- **Replan**: [replan note or "N/A"]

#### Phase 2
...

### Acceptance Criteria (All Phases)

| Phase | # | Criterion | Status |
|-------|---|-----------|--------|
[derived from all phases' acceptance-results.md]
```

---

### Component 11 — docs/DEEPWORK.md

#### [MODIFY] `docs/DEEPWORK.md`

Update all sections to reflect the new phase-scoped directory structure:

1. **Flowchart** — update output annotations to show phase-scoped paths
2. **Pipeline State Files table** — restructure to show phase-scoped vs top-level files
3. **State Management and Resume** — document the new fallback recovery algorithm
4. **Backward Loops** — document phase-aware cleanup rules
5. **Operational Rules** — add notes about phase directory creation, symlinks, and task validation

---

## Issue-to-Change Traceability

| Issue | Fix Location | Component |
|---|---|---|
| 1. Resume fallback not phase-aware | deepwork.md Change 7 (recovery algorithm) | 2 |
| 2. `state.md` underspecified | deepwork.md Change 8 (state contract) | 2 |
| 3. Replan doesn't refresh control state | deepwork.md Change 6 (manifest refresh) | 2 |
| 4. Cumulative artifacts lack phase schema | All phase-scoped dir changes | 1, 4, 5, 6, 9, 10 |
| 5. Backward-loop cleanup phase-destructive | deepwork.md Change 9 (phase-aware cleanup) | 2 |
| 6. Replan tasks lack review status | qrspi-replan.md Change 6 (append review status) | 6 |
| 7. Superseded tasks not separated | Phase-scoped task dirs + replan full-copy | 1, 6, 7 |

---

## Resolved Questions

- **Symlink permission**: Approved. Add `"ln -s *": allow` to deepwork's bash permissions. `qrspi-plan` does not need it.
- **Backward loop context from Phase 2+**: Send **full phase artifacts** (execution-manifest, integration-results, acceptance-results, stage summaries) **plus** the backward-loop analysis and feedback files that describe what went wrong. This gives the re-entered stage full context on both what succeeded and why the loop was triggered.

---

## Verification Plan

### Automated Checks

1. **Editor validation** — Run `get_errors` on all modified agent files to verify no syntax/frontmatter issues
2. **Permission audit** — Verify every agent's `permission:` block still matches its actual file access patterns
3. **Contract audit** — Dry-run trace through these scenarios:
   - Quick-fix route (should be unchanged except for phase-01 dir creation)
   - Two-phase full route, no interruptions
   - Two-phase full route, resume with `state.md` present (mid Phase 2 Implement)
   - Two-phase full route, resume without `state.md` (after Phase 1 Accept, before Replan)
   - Two-phase full route, Phase 2 backward loop to Plan
   - Three-phase full route with Replan adding a new phase

### Manual Verification

4. **Cross-reference check** — Verify every `cat` / `ls` / write path in every modified agent matches the new directory layout
5. **Dispatch prompt check** — Verify every `task` dispatch prompt in every modified stage agent includes the `PHASE DIR` input where needed
6. **Recovery completeness check** — Verify the fallback recovery algorithm can correctly identify next_stage for every possible interruption point in a 3-phase run

### Documentation

7. **Update LONG_RUNNING.md** — Mark all 7 issues as resolved and reference this plan
8. **Update DEEPWORK.md** — Full documentation refresh for the new structure
