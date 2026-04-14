# QRSPI Pipeline

## Flowchart

```
                                ┌───────────────────┐
                                │    User Task      │
                                │  (natural lang)   │
                                └────────┬──────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │   PRE-FLIGHT     │
                                │ validate task,   │
                                │ create run state,│
                                │ branch, checklist│
                                └────────┬─────────┘
                                         │
                          ═══════════════════════════════════════════
                          ║   .pipeline/qrspi-<run-id>/state.md     ║
                          ═══════════════════════════════════════════
                                         │
                                         ▼
                          ┌──────────────────────────────┐
                          │  STAGE 1 — Goals            │
                          │  🔒 Human Gate               │
                          │                              │
                          │  Interactive dialogue via    │
                          │  question tool               │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-goals-synthesizer│  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │  qrspi-goals-reviewer  │  │  (min 3 / max 5 rounds)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: goals.md, config.md,
                                   reviews/goals-review-round-NN.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 2 — Questions        │
                          │  🔒 Human Gate               │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-question-generator│  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-question-leakage- │  │
                          │  │reviewer                │  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-question-quality- │  │
                          │  │reviewer                │  │  (dual review, up to 5 rounds)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: questions.md,
                                   question-leakage-review.md,
                                   question-quality-review.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 3 — Research         │
                          │  ⚠️ Strict Isolation         │
                          │  (goals.md NEVER passed)     │
                          │                              │
                          │  Per-question parallel:      │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-codebase-researcher│ │  (codebase-tagged)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-web-researcher   │  │  (web-tagged)
                          │  └────────────────────────┘  │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-research-synthesizer││  (combine findings)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-research-reviewer│  │  (up to 5 rounds)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: research/q-*.md,
                                   research/summary.md,
                                   reviews/research-review-round-NN.md
                                        │
                             ┌──────────┴──────────┐
                             │                     │
                         Full route            Quick-fix
                             │                     │          (Stages 4 & 5 self-skip)
                             ▼                    ▼
                          ┌──────────────────────────────┐
                          │  STAGE 4 — Design           │
                          │  🔒 Human Gate               │
                          │  (SKIP on quick-fix)         │
                          │                              │
                          │  Interactive design          │
                          │  discussion via question     │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-design-synthesizer│  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-design-reviewer  │  │  (min 3 / max 5 rounds)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: design.md,
                                   reviews/design-review-round-NN.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 5 — Structure        │
                          │  🔒 Human Gate               │
                          │  (SKIP on quick-fix)         │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-structure-mapper │  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-structure-reviewer│  │  (min 3 / max 5 rounds)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: structure.md,
                                   reviews/structure-review-round-NN.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 6 — Plan             │
                          │  (route locked after this)   │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │   qrspi-plan-writer    │  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │  qrspi-plan-reviewer   │  │  (min 5 / max 10 rounds)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-baseline-checker │  │
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: plan.md, phase-manifest.md,
                                   tasks/task-NN.md,
                                   reviews/plan-review-round-NN.md,
                                   baseline-results.md
                                        │
                                        ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Per-Phase Loop                                              │
  │                                                             │
  │  ┌──────────────────────────────┐                           │
  │  │  STAGE 7 — Implement        │                           │
  │  │  (wave-based parallel)       │                           │
  │  │                              │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │  qrspi-implementer     │  │  (per-task TDD)           │
  │  │  │  (× N tasks per wave)  │  │                           │
  │  │  └────────────────────────┘  │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │   qrspi-code-review    │  │  (6 specialist reviewers) │
  │  │  └────────────────────────┘  │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │qrspi-integration-      │  │                           │
  │  │  │checker                 │  │                           │
  │  │  └────────────────────────┘  │                           │
  │  │                              │                           │
  │  │  ↺ backward loop possible   │                           │
  │  └─────────────┬────────────────┘                           │
  │                │                                            │
     │  Outputs: phases/phase-NN/execution-manifest.md,            │
     │           phases/phase-NN/stage7-summary.md,                │
     │           phases/phase-NN/integration-results.md,           │
     │           phases/phase-NN/stage7-integration-summary.md     │
  │                │                                            │
  │                ▼                                           │
  │  ┌──────────────────────────────┐                           │
  │  │  STAGE 8 — Acceptance Test  │                           │
  │  │                              │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │qrspi-acceptance-tester │  │  (inner loop, max 3 rds)  │
  │  │  └────────────────────────┘  │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │qrspi-backward-loop-    │  │  (on persistent failures) │
  │  │  │detector                │  │                           │
  │  │  └────────────────────────┘  │                           │
  │  │                              │                           │
  │  │  ↺ backward loop possible   │                           │
  │  └─────────────┬────────────────┘                           │
  │                │                                            │
     │  Outputs: phases/phase-NN/coverage-plan.md,                │
     │           phases/phase-NN/acceptance-results.md,           │
     │           reviews/acceptance-phase-PP-review-round-NN.md,  │
     │           phases/phase-NN/backward-loop-analysis.md,       │
     │           phases/phase-NN/stage8-summary.md                │
  │                │                                            │
  │                ▼                                            │
  │  ┌──────────────────────────────┐                           │
  │  │  STAGE 8.5 — Replan         │                           │
  │  │  (multi-phase only)          │                           │
  │  │                              │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │  qrspi-replan-writer  │  │                           │
  │  │  └────────────────────────┘  │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │ qrspi-replan-reviewer │  │  (min 3 / max 5 rounds)  │
  │  │  └────────────────────────┘  │                           │
  │  │                              │                           │
  │  │  Skipped for quick-fix,      │                           │
  │  │  single-phase, or final phase│                           │
  │  └─────────────┬────────────────┘                           │
  │                │                                            │
     │  Outputs: plan.md (updated), phase-manifest.md (updated),  │
     │           phases/phase-(NN+1)/tasks/task-NN.md,            │
     │           reviews/replan-review-round-NN.md,               │
     │           phases/phase-NN/replan/phase-NN-replan.md        │
  │                │                                            │
  │                └───────▶ loop back to Stage 7 ──────────┐  │
  │                                                          │  │
  │  Repeat until the final phase is complete ◀──────────────┘  │
  └─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 9 — Verify            │
                          │  (max 3 iterations)          │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │   qrspi-verifier       │  │
                          │  └────────────────────────┘  │
                          │                              │
                          │  Result: PASS / PARTIAL /    │
                          │          FAIL                │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: stage9-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 10 — Report           │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │   qrspi-reporter       │  │
                          │  └────────────────────────┘  │
                          │                              │
                          │  Produces: Final Report      │
                          └─────────────┬────────────────┘
                                        │
                                        ▼
                               ┌──────────────────────┐
                               │   POST-PIPELINE      │
                               │  PASS/PARTIAL/FAIL → │
                               │  preserve audit trail│
                               └──────────────────────┘
```

## Pipeline Routes

**Full pipeline** — for features, new products, and anything requiring architectural design. May be single-phase or multi-phase:

```
Goals → Questions → Research → Design → Structure → Plan → [Implement → Accept-Test → Replan]* → Verify → Report
```

**Quick-fix** — for targeted bug fixes, small changes, and 1–3 file modifications. Always single-phase. It still reaches Stages 4 and 5, but those stages self-skip and mark themselves skipped before continuing to Stage 6:

```
Goals → Questions → Research → Plan → Implement → Accept-Test → Verify → Report
```

Route is determined during Stage 1 (Goals) and written to `config.md`. Route changes are allowed before Stage 6 (Plan). After Plan is written, the route is locked.

Phase handling rules:

- Full route reads its phase count from `phase-manifest.md` after Stage 6.
- If `phase-manifest.md` declares one phase, the full route behaves like a single-pass run: no Replan loop fires.
- If `phase-manifest.md` declares multiple phases, deepwork runs Stage 7 and Stage 8 for one phase at a time, invokes Stage 8.5 between phases, and only enters Verify after the final phase completes.
- Quick-fix is always single-phase (`total_phases: 1`).

---

## Pipeline State Files

All inter-stage data flows through files in `.pipeline/qrspi-<run-id>/`:

### Top-Level Artifacts

| File                              | Written By                   | Purpose                                                            |
| --------------------------------- | ---------------------------- | ------------------------------------------------------------------ |
| `state.md`                        | Deepwork                     | Recovery state and next-stage cursor (YAML frontmatter)            |
| `config.md`                       | Stage 1                      | Route, run_id, and metadata                                        |
| `goals.md`                        | Stage 1                      | Intent, constraints, non-goals, acceptance criteria                |
| `questions.md`                    | Stage 2                      | Tagged research questions                                          |
| `question-leakage-review.md`      | Stage 2                      | Independent review of question neutrality                          |
| `question-quality-review.md`      | Stage 2                      | Independent review of question coverage and tagging quality        |
| `research/q-NN.md`                | Stage 3                      | Per-question research findings                                     |
| `research/summary.md`             | Stage 3                      | Unified research summary                                           |
| `design.md`                       | Stage 4                      | Architecture, vertical slices, phases, replan gates, test strategy |
| `structure.md`                    | Stage 5                      | File mapping, interfaces, create/modify, Mermaid diagram           |
| `plan.md`                         | Stage 6, 8.5                 | Current remaining-work implementation plan                         |
| `phase-manifest.md`               | Stage 6, 8.5                 | Current phase ordering, task-to-phase mapping, and replan gates    |
| `baseline-results.md`             | Stage 6                      | Pre-implementation build/test baseline                             |
| `tasks/task-NN.md`                | Stage 6                      | Canonical initial task specs with appended review status           |
| `reviews/*.md`                    | Stages 1, 3, 4, 5, 6, 8, 8.5 | Automated review history                                           |
| `feedback/{step}-round-NN.md`     | Any gate                     | Rejection feedback + rejected artifact                             |
| `feedback/deferred-replan-NN.md`  | Deepwork                     | Deferred phase-boundary issues from backward loops                 |
| `feedback/goals-reset-context.md` | Deepwork                     | Accumulated learnings before a full reset to Goals                 |
| `stage9-summary.md`               | Stage 9                      | Verification summary (PASS/PARTIAL/FAIL)                           |
| `stage10-summary.md`              | Stage 10                     | Final report                                                       |

### Phase-Scoped Artifacts

| File Pattern                                    | Written By | Purpose                                                                   |
| ----------------------------------------------- | ---------- | ------------------------------------------------------------------------- |
| `phases/archive/phase-NN/`                      | Deepwork   | Archived unstarted future phase directories removed by Replan or loopback |
| `phases/phase-01/tasks/ -> ../../tasks/`        | Deepwork   | Symlink from Phase 1 to the canonical Stage 6 task set                    |
| `phases/phase-NN/tasks/task-NN.md`              | Stage 8.5  | Complete task set for that phase, with stable task IDs and review status  |
| `phases/phase-NN/execution-manifest.md`         | Stage 7    | Per-phase execution and review results                                    |
| `phases/phase-NN/stage7-summary.md`             | Stage 7    | Per-phase implementation summary                                          |
| `phases/phase-NN/integration-results.md`        | Stage 7    | Per-phase integration results                                             |
| `phases/phase-NN/stage7-integration-summary.md` | Stage 7    | Per-phase integration summary                                             |
| `phases/phase-NN/coverage-plan.md`              | Stage 8    | Per-phase acceptance coverage plan                                        |
| `phases/phase-NN/acceptance-results.md`         | Stage 8    | Per-phase acceptance results                                              |
| `phases/phase-NN/backward-loop-analysis.md`     | Stage 8    | Per-phase backward-loop classification output when needed                 |
| `phases/phase-NN/stage8-summary.md`             | Stage 8    | Per-phase acceptance summary                                              |
| `phases/phase-NN/replan/phase-NN-replan.md`     | Stage 8.5  | Replan note describing the delta after that completed phase               |

Rules:

- Phase-local execution artifacts are the authoritative audit trail for multi-phase runs.
- Active execution ignores anything under `phases/archive/`; archived phase directories are kept only for audit.
- Phase 2 and later receive real task copies in their phase directory. Replan does not rely on shared top-level cumulative execution or acceptance files.

---

## State Management and Resume

### `state.md` Contract

Deepwork owns `.pipeline/qrspi-<run-id>/state.md`. It is overwritten after Pre-Flight, after every successful stage transition, after every backward-loop routing decision, and after every resume recovery decision. Written as YAML frontmatter:

```yaml
---
run_id: qrspi-YYYYMMDD-HHMMSS
route: full
current_phase: 1
total_phases: 1
last_completed_stage: goals
next_stage: questions
stages_completed:
  - goals
phase_history:
  - phase: 1
    completed_stages:
      - goals
backward_loops: 0
resume_source: state
---
```

Rules:

- `current_phase` is `1` until `phase-manifest.md` exists.
- `total_phases` is `1` for quick-fix, and `0` until Plan produces `phase-manifest.md` for full route.
- Phase directory names are always zero-padded two-digit identifiers: `phases/phase-01`, `phases/phase-02`, ..., `phases/phase-NN`.
- `resume_source` is `state` when recovered from `state.md`, `artifacts` when reconstructed from files on disk, and `fresh` on a brand-new run.
- `stages_completed` may include `replan` once any phase transition completes.
- `phase_history` records per-phase stage-boundary completion. For single-phase runs, keep one entry.
- Recovery is stage-level only. If the run is interrupted mid-stage, restart that stage from the beginning instead of resuming a substep.

### Resume Mode

If the user provides a run ID, asks to resume, or points at an existing `.pipeline/qrspi-<run-id>/` directory:

1. Resolve the run directory: `.pipeline/qrspi-<run-id>/`
2. Read `.pipeline/qrspi-<run-id>/state.md`
3. If `state.md` exists and is coherent, use it as the authoritative recovery record: recover `route`, `current_phase`, `total_phases`, and `next_stage`.
4. If `state.md` is missing or inconsistent, reconstruct progress from disk:
   - read `config.md` to confirm the route
   - use top-level markers for Goals, Questions, Research, Design, Structure, and Plan
   - if pre-phase work is complete, read `phase-manifest.md` for `total_phases`
   - scan active phase directories under `phases/phase-*/` and ignore `phases/archive/`
   - treat `stage7-summary.md`, `stage8-summary.md`, and `replan/phase-NN-replan.md` inside each phase directory as the authoritative stage markers
   - if no active phase directory has any stage artifact yet, resume at Implement for Phase 1
   - if the highest active phase with artifacts has no `stage7-summary.md`, restart Implement for that phase
   - if it has `stage7-summary.md` but no `stage8-summary.md`, restart Accept-Test for that phase
   - if it has `stage8-summary.md` but no replan note, resume at Replan unless the route is quick-fix or that phase is now final, in which case resume at Verify
   - if it has a replan note and more phases remain, resume Implement for the next phase
   - if a phase directory has partial artifacts but lacks its stage summary, restart that stage from the beginning
   - let `stage9-summary.md` and `stage10-summary.md` override phase recovery when verification or reporting already completed
5. Reconstruct `state.md` from recovered artifacts with `resume_source: artifacts` when disk recovery was needed.
6. For quick-fix runs, force `current_phase: 1` and `total_phases: 1` during recovery.
7. Rebuild the visible todo checklist from the refreshed `phase-manifest.md`, ignoring archived future phases.

If both `state.md` and the artifact set imply the run is already complete, present the preserved report path and stop.

---

## Automated Review Loops

Every alignment and planning stage runs an internal automated review loop before human review or downstream consumption. Each loop guarantees a minimum number of review rounds and caps at a maximum to prevent infinite loops.

| Stage         | Reviewer Agent                                                              | Min Rounds | Max Rounds | Failure Action                                              |
| ------------- | --------------------------------------------------------------------------- | ---------- | ---------- | ----------------------------------------------------------- |
| 1 — Goals     | `qrspi-goals-reviewer`                                                      | 3          | 5          | Re-dispatch synthesizer with review feedback                |
| 2 — Questions | Dual: `qrspi-question-leakage-reviewer` + `qrspi-question-quality-reviewer` | 1          | 5          | Re-dispatch generator; user choice after round 1            |
| 3 — Research  | `qrspi-research-reviewer`                                                   | 1          | 5          | Re-dispatch affected researchers + synthesizer; FAIL on cap |
| 4 — Design    | `qrspi-design-reviewer`                                                     | 3          | 5          | Re-dispatch design synthesizer with feedback                |
| 5 — Structure | `qrspi-structure-reviewer`                                                  | 3          | 5          | Re-dispatch structure mapper with feedback                  |
| 6 — Plan      | `qrspi-plan-reviewer`                                                       | 5          | 10         | Re-dispatch plan writer with feedback                       |
| 8.5 — Replan  | `qrspi-replan-reviewer`                                                     | 3          | 5          | Re-dispatch replan writer with feedback                     |

Review loop logic:

- If the reviewer returns `PASS` but the minimum has not been reached, re-run the reviewer on the unchanged artifact.
- If the reviewer returns `FAIL` and the maximum has not been reached, re-dispatch the synthesizer/writer with review feedback, then re-review.
- If the reviewer returns `FAIL` at the maximum round cap, terminate with `unclean-cap` status.

Terminal review states:

- `clean` — the final review round passed.
- `fixed-unverified` — (Stage 2 only) round 1 failed, fixes applied, user chose immediate presentation.
- `unclean-cap` — reached the maximum with outstanding concerns.

Stage 3 (Research) differs: if the review loop reaches the 5-round cap with unresolved material issues, the stage returns `FAIL` rather than proceeding with weak research.

Stage 6 (Plan) additionally appends a final review status block to every `tasks/task-NN.md` after the loop ends, so Stage 7 implementers can treat outstanding review concerns as an execution risk signal.

---

## Operational Rules

- The deepwork agent never writes project code or runs project commands itself. It delegates all implementation work through subagents via the `task` tool.
- Its edit permission is limited to pipeline state files inside `.pipeline/qrspi-<run-id>/`.
- After each `task` dispatch, the deepwork agent stops and waits for the subagent response before continuing.
- Inter-stage state lives in pipeline files, not in todo metadata. The `todowrite` tool is only for the user-visible progress checklist.
- Research isolation is structurally enforced: `goals.md` is never passed to any researcher, reviewer, or synthesizer in Stage 3. Researchers receive only the question text from `questions.md`.
- Stage 2 includes independent question leakage and question quality reviews before any research begins.
- Stage 6 records a pre-implementation baseline so later verification can distinguish known failures from new regressions.
- Stage 6 writes the canonical initial `tasks/` directory, and deepwork creates `phases/phase-01/tasks/` as a symlink to that canonical task set after Plan completes.
- Stage 7 includes a per-task code review gate (6 specialized reviewers), validates that every task listed for the current phase exists before implementation begins, and writes phase-local execution artifacts.
- Stage 8 and Stage 8.5 write only to the active phase directory plus shared review history.
- Stable task IDs are preserved across replans. Replan uses the current remaining task specs as the authoritative carry-forward source, writes the complete next-phase task set into `phases/phase-NN/tasks/`, and appends a review-status block before Stage 7 consumes it.
- Verify and Report aggregate by enumerating `phases/phase-*/` rather than relying on top-level cumulative execution or acceptance files.

---

## Human Gates

Four stages require human approval before proceeding:

| Stage         | Artifact       | What the User Reviews                                  |
| ------------- | -------------- | ------------------------------------------------------ |
| 1 — Goals     | `goals.md`     | Intent, constraints, non-goals, acceptance criteria    |
| 2 — Questions | `questions.md` | Research question neutrality, coverage, and tagging    |
| 4 — Design    | `design.md`    | Approach, vertical slices, phases, replan gates, tests |
| 5 — Structure | `structure.md` | File mapping, interfaces, Mermaid diagram              |

All human gates present the automated review status to the user ("passed clean in round N" or "reached the N-round cap with remaining concerns documented in ...").

Rejection captures feedback in `feedback/{step}-round-NN.md`. The re-generation subagent receives all prior feedback files to avoid repeating rejected approaches. After human feedback is incorporated, the automated review loop restarts from round 1 before the next human review.

---

## Backward Loops

Stages 7 (Implement), 8 (Accept-Test), and 8.5 (Replan) can trigger backward loops when a fundamental issue is discovered. Stage 8 uses a dedicated `qrspi-backward-loop-detector` subagent to classify persistent failures and recommend whether a backward loop is needed. Stage 8.5 triggers a formal backward loop when the remaining work can no longer stay within the existing goals or design.

The deepwork agent presents the issue to the user with these options:

**Full route options:**

| Option | Action                                                       |
| ------ | ------------------------------------------------------------ |
| A      | Loop back to **Design** (re-architect the approach)          |
| B      | Loop back to **Structure** (re-map files and interfaces)     |
| C      | Loop back to **Plan** (revise task specifications)           |
| D      | Defer to next **Replan** (record issue for phase boundary)   |
| E      | Attempt a **local fix** within the current stage             |
| F      | **Continue as-is** (accept the limitation)                   |
| G      | Full reset to **Goals** (restart with accumulated learnings) |

**Quick-fix route options** (Design and Structure are skipped, so A and B are unavailable; Replan is skipped, so D is unavailable):

| Option | Action                                                       |
| ------ | ------------------------------------------------------------ |
| C      | Loop back to **Plan** (revise task specifications)           |
| E      | Attempt a **local fix** within the current stage             |
| F      | **Continue as-is** (accept the limitation)                   |
| G      | Full reset to **Goals** (restart with accumulated learnings) |

Loop-back mechanics (options A, B, C):

1. Write loop feedback to `feedback/{stage}-loop-{NN}.md`.
2. Preserve completed phase directories `phases/phase-01/` through `phases/phase-(N-1)/` unchanged.
3. Delete the current incomplete phase directory and archive any unstarted future phase directories under `phases/archive/`.
4. Delete the regenerated top-level artifacts owned by the loop target or later stages.
5. Reset todo items for the target stage and all downstream stages, removing stale future-phase checklist entries.
6. Overwrite `state.md` with the loop target, increment `backward_loops`, set `current_phase` to the earliest incomplete phase when completed phases are being preserved, and reset `current_phase` to `1` only when no completed phases remain or the loop target is before phased execution.
7. Re-enter the pipeline at the target stage. For Phase 2 and later loopbacks to Design, Structure, or Plan, deepwork passes `NEXT REMAINING PHASE`, the prior `phase-manifest.md`, preserved completed-phase artifacts, and the failed phase's backward-loop analysis and summaries as context.

Defer to Replan (option D):

1. Write deferred feedback to `feedback/deferred-replan-{NN}.md`.
2. Continue the current stage as non-blocking. The next Replan stage reads all deferred replan feedback files.

Full reset to Goals (option G):

1. Write accumulated learnings to `feedback/goals-reset-context.md`.
2. Delete every pipeline artifact except `feedback/`, including all active and archived phase directories.
3. Recreate `state.md` with `route: unknown`, `next_stage: goals`, incremented `backward_loops`.
4. Reset the visible checklist to the initial pre-plan state.
5. Re-enter Stage 1 with `=== PRIOR RUN LEARNINGS ===` included in the Goals dispatch.

---

## Pre-Flight

Before Stage 1 starts, the deepwork agent:

1. Requires an actionable task description from the user. If no task is provided, asks for one. If too vague, asks clarifying questions.
2. Generates a run ID with `date +%Y%m%d-%H%M%S`, prefixed with `qrspi-`.
3. Creates `.pipeline/qrspi-<run-id>/phases/` and checks out branch `qrspi/<run-id>` from `main`.
4. Writes initial `state.md` with `route: unknown`, `next_stage: goals`, `resume_source: fresh`.
5. Creates the visible progress checklist using `todowrite` (ten items: Stage 1–6, Phase 1 Implement, Phase 1 Acceptance test, Stage 9, Stage 10).
6. After Plan completes, creates `phases/phase-01/tasks/` as a symlink to `../../tasks/` and creates any additional empty planned phase directories.
7. Immediately enters Stage 1.

---

## Validation and Error Handling

- If a subagent returns `### Status — FAIL` (without a backward loop), the deepwork agent does NOT proceed to the next stage.
- It surfaces the error to the user via `question`, including which stage failed and the `### Summary` from the subagent's return.
- The user can choose to retry the stage or abort the pipeline.
- On abort, the run directory is preserved as a partial audit trail.
- When retrying, prior artifacts are not overwritten unless the retry path explicitly requires it.
- After Stage 10, the full `.pipeline/qrspi-<run-id>/` directory is preserved for PASS, PARTIAL, and FAIL runs as the audit trail.

---

## Agent Summaries

### Primary Agent

#### deepwork

The top-level QRSPI pipeline controller. Accepts a user's task and drives it through a 10-stage pipeline with two route variants (full and quick-fix) and optional multi-phase execution. Conducts no interactive dialogue itself — delegates alignment stages and all implementation to subagents. Manages inter-stage data through pipeline state files, creates phase directories and archives obsolete unstarted future phases, tracks progress via a visible todo checklist, persists recovery state in `state.md`, and handles backward loops, resume flow, and cross-stage error routing.

---

### Stage 1 — Goals

#### qrspi-goals

Stage orchestrator. Captures the user's intent through sequential interactive dialogue (core change, constraints, non-goals, acceptance criteria, size estimate). Performs a scope decomposition check — if the request bundles multiple independent subsystems, asks the user to narrow before proceeding. Dispatches the goals synthesizer, runs the automated goals review loop, and holds a human gate for approval.

#### qrspi-goals-synthesizer

Synthesizes `goals.md` (intent, constraints, non-goals, acceptance criteria) and `config.md` (route, created date, run_id, metadata) from the interactive dialogue context. Ensures all acceptance criteria are specific and testable. Handles feedback-driven re-generation. Read-only.

#### qrspi-goals-reviewer

Reviews `goals.md` independently for intent clarity, constraint specificity, scope boundaries, acceptance testability, single-run scope, and implicit assumptions. Returns PASS or FAIL with fix guidance. Read-only.

---

### Stage 2 — Questions

#### qrspi-questions

Stage orchestrator. Dispatches the question generator, runs dual independent reviews (leakage and quality), and manages a user choice after round 1 issues (present now or loop until clean). Holds a mandatory human gate before research begins.

#### qrspi-question-generator

Generates 5–15 neutral, tagged research questions from `goals.md`. Tags each question as `codebase`, `web`, or `hybrid`. Prefers splitting `hybrid` questions into separate `codebase` and `web` questions unless the question truly requires both. Performs a first-pass self-review for goal leakage and can rewrite questions using reviewer feedback. Read-only.

#### qrspi-question-leakage-reviewer

Independently reviews `questions.md` against `goals.md` and flags any question that leaks the requested change to a goal-blind researcher. Produces per-question SAFE or LEAKS status with rewrite guidance. Read-only.

#### qrspi-question-quality-reviewer

Independently reviews `questions.md` against `goals.md` for comprehensiveness, objectivity, specificity, tag accuracy, hybrid splitting, redundancy, and missing investigation areas. Returns per-question and set-level findings with improvement guidance. Read-only.

---

### Stage 3 — Research

#### qrspi-research

Stage orchestrator. Dispatches codebase and web researchers per question tag in parallel, collects findings into per-question artifacts, dispatches the research synthesizer, and runs up to 5 automated review rounds. Enforces strict goal isolation. Returns FAIL (not PASS with weak results) if the review loop reaches the 5-round cap with unresolved material issues.

#### qrspi-codebase-researcher

Researches a single question against the current codebase using grep, find, cat, and ls. Returns factual findings with file:line references. Never sees `goals.md`. Pure documentarian — describes what exists, never suggests changes. Read-only.

#### qrspi-web-researcher

Researches a single question using web search (webfetch). Returns factual findings with source URLs. Never sees `goals.md`. Pure documentarian. The only agent in the pipeline with `webfetch: allow`. Read-only.

#### qrspi-research-synthesizer

Combines per-question research findings into a unified summary organized by topic. Deduplicates overlapping findings and cross-references related discoveries. Does not add opinions or recommendations. Read-only.

#### qrspi-research-reviewer

Reviews the complete research set (per-question artifacts and synthesis) for objectivity, citation quality, factual coverage, synthesis fidelity, and cross-reference validity. Identifies which specific artifacts need re-research and provides targeted fix guidance. Read-only.

---

### Stage 4 — Design

#### qrspi-design

Stage orchestrator. Conducts interactive design discussion with the user (2–3 approaches, trade-offs, vertical slice decomposition, phase grouping, replan gates, test strategy). Enforces guardrails against horizontal layer planning, vague test strategy, missing phase gates, and speculative future-proofing. Dispatches the design synthesizer, runs the automated design review loop, and holds a human gate.

#### qrspi-design-synthesizer

Synthesizes a design document from goals, research summary, and the interactive design discussion. Structures the chosen approach, architectural patterns, Mermaid system diagram, vertical slice decomposition, phases with replan gates, test strategy, and key decisions with trade-offs. Handles feedback-driven re-generation. Read-only.

#### qrspi-design-reviewer

Reviews `design.md` independently for goals alignment, vertical slice quality, test strategy completeness, internal consistency, research congruence, YAGNI compliance, phase coherence, and diagram quality. Flags horizontal decomposition, speculative architecture, weak replan gates, or vague testing. Read-only.

---

### Stage 5 — Structure

#### qrspi-structure

Stage orchestrator. Dispatches the structure mapper, runs the automated structure review loop, and holds a human gate. Enforces guardrails against missing slice coverage, vague file maps, missing interfaces, and missing diagrams.

#### qrspi-structure-mapper

Maps each vertical slice from the design to specific files and components. Defines interfaces between components (function signatures, class signatures, type definitions). Tracks CREATE vs. MODIFY per file and verifies paths against the actual codebase. Includes a Mermaid architectural diagram showing file/module layout, interface boundaries, and data flow. Handles feedback-driven re-generation. Read-only.

#### qrspi-structure-reviewer

Reviews `structure.md` independently for design alignment, file action correctness, interface completeness, interface compatibility, convention adherence, cross-slice dependency clarity, diagram quality, and granularity. Verifies MODIFY and CREATE paths against the codebase using bash. Read-only.

---

### Stage 6 — Plan

#### qrspi-plan

Stage orchestrator. Reads route-appropriate inputs, dispatches the plan writer, runs the automated plan review loop (min 5 / max 10 rounds), appends final review status to each task spec, and dispatches the baseline checker. No human gate.

#### qrspi-plan-writer

Writes ordered task specifications with file paths, descriptions, test expectations, dependencies, phase assignments, LOC estimates, and stable task IDs. Produces `plan.md`, `phase-manifest.md`, and individual `task-NN.md` files. Supports full route (uses all prior artifacts) and quick-fix route (single task from goals + research). Read-only.

#### qrspi-plan-reviewer

Reviews the plan for goals coverage, dependency correctness, phase and wave coherence, task self-containment, file specificity, test expectation specificity, LOC realism, and placeholder-free quality. Flags forward dependencies, vague files, vague tests, missing coverage, or overview/task mismatches. Read-only.

#### qrspi-baseline-checker

Records the pre-implementation build and test baseline before Stage 7 begins. Produces `baseline-results.md`, capturing known pre-existing failures without attempting fixes.

---

### Stage 7 — Implement

#### qrspi-implement

Stage orchestrator. Analyzes current-phase task dependencies into waves, dispatches implementers in parallel per wave (forwarding goals, review context, and design context), validates that every task listed for the phase exists in `phases/phase-NN/tasks/`, records per-task review outcomes, runs integration checks, and writes phase-local execution artifacts.

#### qrspi-implementer

Implements a single task using TDD: write failing tests → implement to pass → self-review → specialized code review → commit. Uses the plan review status as an execution risk signal — if `unclean-cap`, treats outstanding concerns as unresolved planning risk and may request a backward loop instead of guessing. Reports backward loop requests if the task spec is fundamentally unworkable.

#### qrspi-code-review

Per-task review orchestrator. Reads changed files, selects applicable specialist reviewers based on code signals, dispatches them in parallel, and collates findings. Blocks only on CRITICAL/HIGH severity. Always dispatches code-quality and test-coverage reviewers. Conditionally dispatches others based on code content:

| Reviewer                         | Focus                                      | Trigger                                              |
| -------------------------------- | ------------------------------------------ | ---------------------------------------------------- |
| `qrspi-review-code-quality`      | Clean code, maintainability                | Always                                               |
| `qrspi-review-test-coverage`     | Missing test cases                         | Always                                               |
| `qrspi-review-security`          | Vulnerabilities, secrets, injection        | Auth/crypto/HTTP/FS signals in code                  |
| `qrspi-review-silent-failure`    | Swallowed errors, missing logging          | try/catch/error/async signals                        |
| `qrspi-review-goal-traceability` | Goal-to-code alignment                     | Full route only                                      |
| `qrspi-review-code-simplifier`   | Over-engineering, unnecessary abstractions | LOC > 200, > 3 files, or wrappers/factories detected |

The code simplifier is always non-blocking (advisory only).

#### qrspi-integration-checker

Runs a lightweight integration gate after all implementation waves complete. Checks changed-file build sanity, shared interface compatibility, and targeted smoke checks. Uses the review status summary as a risk signal when interpreting failures. Produces `integration-results.md` and `stage7-integration-summary.md`. Can trigger backward loops for structural mismatches.

---

### Stage 8 — Acceptance Test

#### qrspi-accept

Stage orchestrator. Dispatches the acceptance tester to run an inner review/write/run loop (max 3 rounds) against the current phase's acceptance criteria. If persistent failures remain, dispatches the backward-loop detector to classify them and recommend next steps. Writes phase-local coverage, acceptance, summary, and backward-loop analysis artifacts plus phase-scoped review history.

#### qrspi-acceptance-tester

Runs the acceptance test inner loop: drafts a coverage plan, dispatches 3 acceptance reviewers in parallel to detect plan issues, revises the plan, writes and runs the acceptance tests, and allows up to 2 fix attempts per round for simple local bugs. Tests only the acceptance criteria assigned to the current phase in `phase-manifest.md`. Reports per-criterion PASS or FAIL.

#### qrspi-backward-loop-detector

Analyzes the full completed phase context (goals, execution manifest, integration results, acceptance results, persistent failures) and classifies failures using a severity table. Returns one of: `NO_LOOP`, `DEFER_REPLAN`, `LOOP_PLAN`, `LOOP_STRUCTURE`, `LOOP_DESIGN`, or `LOOP_GOALS`. The classification is then routed through deepwork's backward loop protocol for user decision.

---

### Stage 8.5 — Replan

#### qrspi-replan

Stage orchestrator. Reads the completed phase directory, prior completed phase summaries, deferred replan feedback, and the authoritative current remaining task specs for the next implementation phase. It dispatches the replan writer to revise remaining work, runs the automated replan review loop (min 3 / max 5 rounds), writes the complete next-phase task set into `phases/phase-NN/tasks/`, and writes a phase-local replan note. If the writer determines that Goals or Design must change, the stage returns a formal backward-loop request instead of forcing a replan. It only fires on multi-phase full-route runs between phases.

#### qrspi-replan-writer

Revises the remaining plan (tasks, phases, phase-manifest) after a completed phase. It uses the current remaining task specs as the authoritative source for carrying forward unfinished work, may modify, reorder, split, add, remove, or supersede remaining tasks, and emits the complete task set for the next implementation phase only. It must not change goals, the chosen design approach, or completed phases. When Goals or Design must change, it returns a `### Backward Loop Request` instead of replanned artifacts. It also processes any deferred replan feedback from backward loops. Read-only.

#### qrspi-replan-reviewer

Reviews the replanned remaining work for continued alignment to existing goals, no silent design drift, phase coherence, dependency correctness, task self-containment, file specificity, and justified modifications. Read-only.

---

### Stage 9 — Verify

#### qrspi-verify

Stage orchestrator. Enumerates `phases/phase-*/` and dispatches the verifier with per-phase execution manifests and acceptance results.

#### qrspi-verifier

Runs the full build/lint/test suite, checks aggregated per-phase acceptance results, and compares current failures against `baseline-results.md`. Fixes issues via a verify→fix loop (max 3 iterations). Reports PASS / PARTIAL / FAIL while distinguishing unchanged baseline failures from new regressions.

---

### Stage 10 — Report

#### qrspi-report

Stage orchestrator. Enumerates `phases/phase-*/`, reads per-phase stage summaries and replan notes, and then dispatches the reporter.

#### qrspi-reporter

Formats the Final Report from pipeline config, goals summary, phase manifest, `baseline-results.md`, per-phase acceptance results, per-phase replan notes, and the per-phase stage summaries. Produces a structured markdown report with pipeline route, phase structure, baseline status, per-phase implementation and acceptance status, build/test status, acceptance criteria results, overall status, unresolved items, and the preserved audit trail path. Never writes code or modifies files.
