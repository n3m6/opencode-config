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
                          │  🔒 Human/Auto Gate          │
                          │                              │
                          │  Interactive dialogue via    │
                          │  question tool               │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-goals-synthesizer│  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │  qrspi-goals-reviewer  │  │  (max 5 rounds)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: requirements.md,
                                   goals.md, config.md,
                                   reviews/goals-review-round-NN.md
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │  STAGE 2 — Research         │
                         │  (merged Questions + Research)
                         │                              │
                         │  ┌────────────────────────┐  │
                         │  │   qrspi-questions      │  │  (initial or follow-up batch)
                         │  └────────────────────────┘  │
                         │    ├─ qrspi-question-     │  │
                         │    │  generator           │  │
                         │    ├─ qrspi-question-     │  │
                         │    │  leakage-reviewer    │  │
                         │    └─ qrspi-question-     │  │
                         │       quality-reviewer    │  │
                         │                              │
                         │  ┌────────────────────────┐  │
                         │  │  qrspi-research-pass   │  │  (one batch at a time)
                         │  └────────────────────────┘  │
                         │    ├─ qrspi-codebase-     │  │
                         │    │  researcher          │  │
                         │    ├─ qrspi-web-          │  │
                         │    │  researcher          │  │
                         │    ├─ qrspi-research-     │  │
                         │    │  synthesizer         │  │
                         │    └─ qrspi-research-     │  │
                         │       reviewer            │  │
                         │                              │
                         │  Outer loop rebuilds the    │
                         │  cumulative summary and     │
                         │  follow-up question set     │
                         └─────────────┬────────────────┘
                                 │
                         Outputs: goal-inventory.md,
                              questions.md,
                              question-*-review.md,
                              research/iterations/round-*/...,
                              research/question-ledger.md,
                              research/open-questions.md,
                              research/summary.md,
                              reviews/research/round-*/...,
                              reviews/research-review-round-NN.md
                                 │
                             ┌──────────┴──────────┐
                             │                     │
                         Full route            Quick-fix
                             │                     │          (Stages 4 & 4.5 self-skip)
                             ▼                    ▼
                          ┌──────────────────────────────┐
                          │  STAGE 4 — Design           │
                          │  🔒 Human/Auto Gate          │
                          │  (SKIP on quick-fix)         │
                          │                              │
                          │  Interactive design          │
                          │  discussion via question     │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-design-synthesizer│  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-design-reviewer  │  │  (max 5 rounds)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: design.md,
                                   reviews/design-review-round-NN.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 4.5 — Skeleton +     │
                          │  Structure                   │
                          │  (SKIP on quick-fix)         │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │  qrspi-skeleton        │  │
                          │  └────────────────────────┘  │
                          │       (dispatches             │
                          │   qrspi-fast-impl-loop once  │
                          │   in a git worktree, then    │
                          │   runs structure mapping     │
                          │   and review loop)           │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-structure-mapper │  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-structure-reviewer│  │  (max 5 rounds)
                          │  └────────────────────────┘  │
                          │  ↺ backward loop → Design    │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: skeleton-results.md
                                   (PASS → code squash-merged),
                                   structure.md,
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
                          │  │qrspi-task-spec-writer  │  │
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-task-spec-reviewer│  │  (max 3 rounds per task)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │  qrspi-plan-reviewer   │  │  (max 6 rounds, stable-cap)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-feasibility-chkr  │  │  (pre-impl, max 2 patch rounds)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-plan-patcher     │  │  (on feasibility fail)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-baseline-checker │  │
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: plan.md, phase-manifest.md,
                                   tasks/outlines/task-NN.outline,
                                   tasks/task-NN.md,
                                   reviews/plan-review-round-NN.md,
                                   reviews/task-spec/task-NN-review-round-MM.md,
                                   feasibility-results.md,
                                   feedback/feasibility-patch-round-NN.md,
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
  │  │  │qrspi-fast-impl-loop   │  │  (per-task loop)          │
  │  │  └────────────────────────┘  │                           │
  │  │       │ code → test → verify │                           │
  │  │       ▼                      │                           │
  │  │  ┌────────────────────────┐  │                           │
  │  │  │ qrspi-fast-impl-code   │  │  (production code)        │
  │  │  │ qrspi-fast-impl-test   │  │  (behavior tests)         │
  │  │  │ qrspi-fast-impl-verify │  │  (review + commit)        │
  │  │  └────────────────────────┘  │                           │
  │  │  ┌────────────────────────┐  │                           │
   │  │  │qrspi-e2e-regression-  │  │                           │
   │  │  │checker                │  │  (wave-level E2E gate)    │
   │  │  └────────────────────────┘  │                           │
   │  │  ┌────────────────────────┐  │                           │
  │  │  │qrspi-integration-      │  │                           │
  │  │  │checker                 │  │                           │
  │  │  └────────────────────────┘  │                           │
   │  │  ┌────────────────────────┐  │                           │
   │  │  │qrspi-baseline-        │  │                           │
   │  │  │regression-checker     │  │  (post-waves baseline)    │
   │  │  └────────────────────────┘  │                           │
  │  │                              │                           │
  │  │  ↺ backward loop possible   │                           │
  │  └─────────────┬────────────────┘                           │
  │                │                                            │
     │  Outputs: phases/phase-NN/execution-manifest.md,            │
   │           phases/phase-NN/e2e-regression-results.md,        │
     │           phases/phase-NN/stage7-summary.md,                │
     │           phases/phase-NN/integration-results.md,           │
     │           phases/phase-NN/regression-results.md,            │
     │           phases/phase-NN/stage7-integration-summary.md     │
  │                │                                            │
  │                ▼                                           │
  │  ┌──────────────────────────────┐                           │
  │  │  STAGE 8 — Acceptance Test  │                           │
  │  │                              │                           │
   │  │  ┌────────────────────────┐  │                           │
   │  │  │ qrspi-coverage-planner │  │  (coverage draft/revise)  │
   │  │  └────────────────────────┘  │                           │
   │  │  ┌────────────────────────┐  │                           │
   │  │  │qrspi-acceptance-tester │  │  (review/write/run loop)  │
   │  │  └────────────────────────┘  │                           │
   │  │    ├─ qrspi-review-accept-│  │                           │
   │  │    │  goal-traceability   │  │  (full mode only)         │
   │  │    ├─ qrspi-review-accept-│  │                           │
   │  │    │  spec                │  │  (full mode only)         │
   │  │    └─ qrspi-review-accept-│  │                           │
   │  │       code-quality        │  │  (full mode, new/revise)  │
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
     │           phases/phase-NN/boundary-violations.md,          │
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
  │  │  │ qrspi-replan-reviewer │  │  (max 5 rounds, stable-cap)│
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
                          │  (single pass + auto-fix     │
                          │   re-verify on FAIL)         │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │   qrspi-verifier       │  │
                          │  └────────────────────────┘  │
                          │                              │
                          │  FAIL → Stage 7 verify-fix  │
                          │  pass, then re-verify once   │
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

**Full pipeline** — for features, new products, and anything requiring architectural design. May be single-phase or multi-phase. Question generation is owned internally by the merged Stage 2 (Research):

```
Goals → Research → Design → Skeleton+Structure → Plan → [Implement → Accept-Test → Replan]* → Verify → Report
```

**Quick-fix** — for targeted bug fixes, small changes, and 1–3 file modifications. Always single-phase. It still reaches Stages 4 and 4.5, but those stages self-skip and mark themselves skipped before continuing to Stage 6:

```
Goals → Research → Plan → Implement → Accept-Test → Verify → Report
```

Route is determined during Stage 1 (Goals) and written to `config.md`. Route changes are allowed before Stage 6 (Plan). After Plan is written, the route is locked.

### Execution Modes

Deepwork supports two run-level interaction modes:

- `interactive` — the default. Goals, Design, controller escalation gates, backward-loop choices, and retry/abort handling use the `question` tool.
- `automated` — opt-in. The pipeline suppresses question-based prompts, resolves stage-local approval gates automatically, and uses deterministic controller defaults. `failure_policy` then controls whether controller-level unresolved states continue best-effort or abort conservatively.

`interaction_mode` and `failure_policy` are persisted in both `state.md` and `config.md` so resume recovery and downstream stages can preserve the same behavior.

Phase handling rules:

- Full route reads its phase count from `phase-manifest.md` after Stage 6.
- If `phase-manifest.md` declares one phase, the full route behaves like a single-pass run: no Replan loop fires.
- If `phase-manifest.md` declares multiple phases, deepwork runs Stage 7 and Stage 8 for one phase at a time, invokes Stage 8.5 between phases, and only enters Verify after the final phase completes.
- Quick-fix is always single-phase (`total_phases: 1`).

---

## Pipeline State Files

All inter-stage data flows through files in `.pipeline/qrspi-<run-id>/`:

### Top-Level Artifacts

| File                                                    | Written By                   | Purpose                                                                              |
| ------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------ |
| `state.md`                                              | Deepwork                     | Recovery state, automation policy, and next-stage cursor (YAML frontmatter)          |
| `config.md`                                             | Stage 1                      | Route, run_id, automation policy, and metadata                                       |
| `requirements.md`                                       | Stage 1                      | Verbatim user task or PRD preserved for downstream reference                         |
| `goals.md`                                              | Stage 1                      | Distilled intent, requirements, constraints, non-goals, acceptance criteria          |
| `goal-inventory.md`                                     | Stage 2                      | Normalized goal inventory (FR/NFR/C/AC IDs) seeded once and reused across rounds     |
| `questions.md`                                          | Stage 2                      | Latest active question-batch snapshot for compatibility consumers                    |
| `question-leakage-review.md`                            | Stage 2                      | Latest question-batch leakage-review snapshot for compatibility consumers            |
| `question-quality-review.md`                            | Stage 2                      | Latest question-batch quality-review snapshot for compatibility consumers            |
| `research/iterations/round-NN/questions.md`             | Stage 2                      | Round-local active question-batch snapshot for merged research                       |
| `research/iterations/round-NN/q-NN.md`                  | Stage 2                      | Round-local per-question research findings                                           |
| `research/iterations/round-NN/summary.md`               | Stage 2                      | Round-local research summary                                                         |
| `research/question-ledger.md`                           | Stage 2                      | Cumulative audit trail of every asked research question                              |
| `research/open-questions.md`                            | Stage 2                      | Latest unresolved-question snapshot for follow-up or stalled exit                    |
| `research/summary.md`                                   | Stage 2                      | Unified cumulative research summary                                                  |
| `reviews/research/round-NN/research-pass-review-round-MM.md` | Stage 2                 | Round-local batch-pass review history for `qrspi-research-pass`                       |
| `design.md`                                             | Stage 4                      | Approach, slice inventory + dependency DAG, phases, replan gates, test strategy      |
| `structure.md`                                              | Stage 4.5                    | File mapping, interfaces, system architecture diagram, file/module Mermaid diagram   |
| `skeleton-results.md`                                       | Stage 4.5                    | Skeleton PASS/FAIL, squash-merged files, plan handoff section (Completed Files)      |
| `skeleton-task.md`                                          | Stage 4.5                    | Ephemeral task spec used by the skeleton implementation loop                         |
| `skeleton/stage7-summary.md`                                | Stage 4.5                    | Skeleton execution summary kept outside `phases/phase-*` so resume does not treat it as a normal phase |
| `plan.md`                                                   | Stage 6, 8.5                 | Current remaining-work implementation plan                                           |
| `phase-manifest.md`                                         | Stage 6, 8.5                 | Current phase ordering, task-to-phase mapping, and replan gates                      |
| `feasibility-results.md`                                    | Stage 6                      | Per-task PASS/FAIL from the Feasibility Checklist check; overwritten after each patch round |
| `baseline-results.md`                                       | Stage 6                      | Pre-implementation build/lint/typecheck/E2E/test baseline                            |
| `tasks/outlines/task-NN.outline`                            | Stage 6                      | Per-task planning outlines produced by plan-writer; input to task-spec-writer        |
| `tasks/task-NN.md`                                          | Stage 6                      | Canonical initial task specs with source traceability and appended review status     |
| `reviews/task-spec/task-NN-review-round-MM.md`              | Stage 6                      | Per-task spec review history from task-spec-reviewer                                 |
| `tasks/outlines/inactive/task-NN.outline`                   | Stage 6                      | Superseded task outlines archived when plan-writer rewrites the outline set          |
| `tasks/inactive/task-NN.md`                                 | Stage 6                      | Superseded task specs archived when the active task set is rewritten                 |
| `reviews/task-spec/inactive/task-NN-review-round-MM.md`     | Stage 6                      | Superseded task-spec reviews archived alongside their associated inactive task specs |
| `reviews/*.md`                                              | Stages 1, 2, 4, 4.5, 6, 8, 8.5 | Automated review history                                                          |
| `feedback/{step}-round-NN.md`                               | Any gate                     | Rejection feedback + rejected artifact                                               |
| `feedback/feasibility-patch-round-NN.md`                    | Stage 6 / Deepwork           | Plan-patch audit note after a feasibility failure patch round                        |
| `feedback/feasibility-patch-round-NN-escalation.md`         | Stage 6 / Deepwork           | Patcher escalation record when local patch is impossible                             |
| `feedback/plan-patch-phase-NN-round-RR.md`                  | Deepwork (option P)          | Runtime Option-P patch audit trail written during the backward loop protocol         |
| `feedback/plan-patch-phase-NN-round-RR-failed.md`           | Deepwork (option P)          | Runtime Option-P feasibility failure after a patch attempt                           |
| `feedback/plan-patch-phase-NN-round-RR-escalation.md`       | Deepwork (option P)          | Runtime Option-P patcher escalation record when local patching is impossible         |
| `feedback/deferred-replan-NN.md`                            | Deepwork                     | Deferred phase-boundary issues from backward loops                                   |
| `feedback/goals-reset-context.md`                           | Deepwork                     | Accumulated learnings before a full reset to Goals                                   |
| `stage9-summary.md`                                     | Stage 9                      | Verification summary (PASS/PARTIAL/FAIL)                                             |
| `stage10-summary.md`                                    | Stage 10                     | Final report                                                                         |

### Phase-Scoped Artifacts

| File Pattern                                    | Written By | Purpose                                                                       |
| ----------------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `phases/archive/phase-NN/`                      | Deepwork   | Archived unstarted future phase directories removed by Replan or loopback     |
| `phases/phase-01/tasks/ -> ../../tasks/`        | Deepwork   | Symlink from Phase 1 to the canonical Stage 6 task set                        |
| `phases/phase-NN/tasks/task-NN.md`              | Stage 8.5  | Complete task set for that phase, with stable task IDs and review status      |
| `phases/phase-NN/execution-manifest.md`         | Stage 7    | Per-phase execution and review results                                        |
| `phases/phase-NN/e2e-regression-results.md`     | Stage 7    | Per-wave E2E regression results for the phase                                 |
| `phases/phase-NN/regression-results.md`         | Stage 7    | Post-all-waves baseline regression comparison with suspected task attribution |
| `phases/phase-NN/stage7-summary.md`             | Stage 7    | Per-phase implementation summary                                              |
| `phases/phase-NN/integration-results.md`        | Stage 7    | Per-phase integration results                                                 |
| `phases/phase-NN/stage7-integration-summary.md` | Stage 7    | Per-phase integration summary                                                 |
| `phases/phase-NN/coverage-plan.md`              | Stage 8    | Per-phase acceptance coverage plan                                            |
| `phases/phase-NN/acceptance-results.md`         | Stage 8    | Per-phase acceptance results                                                  |
| `phases/phase-NN/backward-loop-analysis.md`     | Stage 8    | Per-phase backward-loop classification output when needed                     |
| `phases/phase-NN/boundary-violations.md`        | Stage 8    | Per-phase record of non-test files written during acceptance authoring/repair |
| `phases/phase-NN/stage8-summary.md`             | Stage 8    | Per-phase acceptance summary                                                  |
| `phases/phase-NN/replan/phase-NN-replan.md`     | Stage 8.5  | Replan note describing the delta after that completed phase                   |
| `telemetry/events.jsonl`                        | Deepwork   | Canonical append-only event stream (JSONL); never read by resume or recovery  |
| `telemetry/run-log.md`                          | Deepwork   | Derived chronological human timeline; regenerated at each stage boundary      |
| `telemetry/metrics-summary.md`                  | Deepwork   | Derived end-of-run aggregate metrics; generated at Stage 10 and on abort      |

Rules:

- Phase-local execution artifacts are the authoritative audit trail for multi-phase runs.
- Active execution ignores anything under `phases/archive/`; archived phase directories are kept only for audit.
- Phase 2 and later receive real task copies in their phase directory. Replan does not rely on shared top-level cumulative execution or acceptance files.
- `telemetry/` files are diagnostic only. The resume recovery algorithm and backward-loop artifact deletion rules never read or delete them.

---

## Telemetry

The pipeline emits structured telemetry to three files under `telemetry/` on every run. This layer answers operational questions (how long did each stage take? how many review rounds fired? which phase triggered a backward loop?) without replacing the stage-artifact audit trail.

### Artifacts

| File                           | Format              | Produced by                     | Notes                                                                 |
| ------------------------------ | ------------------- | ------------------------------- | --------------------------------------------------------------------- |
| `telemetry/events.jsonl`       | JSONL (append-only) | Deepwork + nested orchestrators | Source of truth; one JSON object per line                             |
| `telemetry/run-log.md`         | Markdown            | Deepwork                        | Derived; regenerated at every stage boundary and on abort/resume/loop |
| `telemetry/metrics-summary.md` | Markdown            | Deepwork                        | Derived; generated at Stage 10 completion and on run abort            |

### Write Ownership

Only the currently active orchestrator appends to `events.jsonl`. Parallel-dispatch stages (Research, Plan, Implement, Accept-Test, Replan) write their own `child.*` and `phase.*` events; they never race on the shared stream because only one stage runs at a time at the deepwork level.

Leaf agents (every agent not listed as an orchestrator) never write `events.jsonl`. They return a `### Telemetry` JSON section upward; their parent serializes the data into events.

### Event Classes

| Class             | Written by           | Representative events                                                                               |
| ----------------- | -------------------- | --------------------------------------------------------------------------------------------------- |
| `run.*`           | deepwork             | `run.started`, `run.resumed`, `run.completed`, `run.aborted`                                        |
| `stage.*`         | deepwork             | `stage.started`, `stage.completed`, `stage.failed`, `stage.skipped`, `stage.retried`                |
| `phase.*`         | qrspi-implement      | `phase.started`, `phase.completed`                                                                  |
| `gate.*`          | deepwork             | `gate.presented`, `gate.approved`, `gate.rejected` for both human and automated gate decisions      |
| `child.*`         | nested orchestrators | `child.dispatched`, `child.returned`                                                                |
| `review.*`        | nested orchestrators | `review.round_started`, `review.round_completed`                                                    |
| `backward_loop.*` | deepwork             | `backward_loop.requested`, `backward_loop.decided` (includes `decision.choice: "P"` for option P), `backward_loop.deferred`, `backward_loop.reset` |
| `checkpoint.*`    | deepwork             | `checkpoint.created`                                                                                |
| `metrics.*`       | deepwork             | `metrics.generated`                                                                                 |

### Non-Interference Guarantee

The resume recovery algorithm (see **State Management and Resume** below) never reads any file under `telemetry/`. The backward-loop artifact deletion rules never delete telemetry files. Telemetry can be safely deleted or ignored without affecting pipeline correctness.

Full schema, event taxonomy, and per-event minimum contracts are documented in `protocol/telemetry-protocol.md`. Derived artifact formats (`run-log.md`, `metrics-summary.md`) are specified in `agents/deepwork.md`.

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
next_stage: research
stages_completed:
  - goals
phase_history:
  - phase: 1
    completed_stages:
      - goals
backward_loops: 0
interaction_mode: interactive
failure_policy: fail-closed
resume_source: state
---
```

Rules:

- `current_phase` is `1` until `phase-manifest.md` exists.
- `total_phases` is `1` for quick-fix, and `0` until Plan produces `phase-manifest.md` for full route.
- Phase directory names are always zero-padded two-digit identifiers: `phases/phase-01`, `phases/phase-02`, ..., `phases/phase-NN`.
- `resume_source` is `state` when recovered from `state.md`, `artifacts` when reconstructed from files on disk, and `fresh` on a brand-new run.
- Valid `next_stage` / `last_completed_stage` values: `goals`, `research`, `design`, `design-skipped`, `skeleton`, `skeleton-skipped`, `plan`, `implement`, `accept`, `replan`, `verify`, `report`, `done`. For quick-fix, `design-skipped` and `skeleton-skipped` are written instead of their full-route completion values.
- `interaction_mode` persists whether the run is interactive or fully automated.
- `failure_policy` persists whether automated controller gates continue best-effort or fail closed.
- `stages_completed` may include `replan` once any phase transition completes.
- `phase_history` records per-phase stage-boundary completion. For single-phase runs, keep one entry.
- Recovery is stage-level only. If the run is interrupted mid-stage, restart that stage from the beginning instead of resuming a substep.

### Resume Mode

If the user provides a run ID, asks to resume, or points at an existing `.pipeline/qrspi-<run-id>/` directory:

1. Resolve the run directory: `.pipeline/qrspi-<run-id>/`
2. Read `.pipeline/qrspi-<run-id>/state.md`
3. If `state.md` exists and is coherent, use it as the authoritative recovery record: recover `route`, `current_phase`, `total_phases`, `interaction_mode`, `failure_policy`, and `next_stage`. Before re-dispatching the recovered `next_stage`, check whether the corresponding summary artifact for that stage/phase already exists on disk and parses as `### Status — FAIL`; if so, surface it via the existing Error Handling path instead of silently restarting.
4. If `state.md` is missing or inconsistent, reconstruct progress from disk:
   - read `config.md` to confirm the route and recover `interaction_mode` / `failure_policy` when present
   - use top-level markers for Goals, Research, Design, Skeleton+Structure, and Plan; treat `goal-inventory.md`, `questions.md`, the `question-*-review.md` snapshots, `research/open-questions.md`, `research/question-ledger.md`, and `research/iterations/` as in-progress markers that force a Research restart when `research/summary.md` is missing; treat Stage 4.5 as complete when `structure.md` exists; if `skeleton-results.md` is PASS but `structure.md` is absent, resume at the structure mapping sub-step (the skeleton orchestrator's Step 0 handles this automatically); a present-but-FAIL `skeleton-results.md` routes through Error Handling
   - if pre-phase work is complete, read `phase-manifest.md` for `total_phases`
   - scan active phase directories under `phases/phase-*/` and ignore `phases/archive/`
   - treat `stage7-summary.md`, `stage8-summary.md`, and `replan/phase-NN-replan.md` inside each phase directory as the authoritative stage markers
   - for each summary artifact, parse its first `### Status` heading: `PASS` (and `PARTIAL` for `stage9-summary.md`) means the stage is complete; `FAIL`, missing, or malformed Status means the stage is incomplete and Error Handling owns the retry/abort decision
   - if no active phase directory has any stage artifact yet, resume at Implement for Phase 1
   - if the highest active phase with artifacts has no complete `stage7-summary.md`, restart Implement for that phase
   - if it has a complete `stage7-summary.md` but no complete `stage8-summary.md`, restart Accept-Test for that phase
   - if it has a complete `stage8-summary.md` but no complete replan note, resume at Replan unless the route is quick-fix or that phase is now final, in which case resume at Verify
   - if it has a complete replan note and more phases remain, resume Implement for the next phase
   - if a phase directory has partial artifacts but lacks its stage summary, restart that stage from the beginning
   - let `stage9-summary.md` (PASS or PARTIAL) and `stage10-summary.md` override phase recovery when verification or reporting already completed; a `stage9-summary.md` parsed as FAIL or with a missing Status heading routes through Error Handling rather than advancing to Report
5. Reconstruct `state.md` from recovered artifacts with `resume_source: artifacts` when disk recovery was needed.
6. For quick-fix runs, force `current_phase: 1` and `total_phases: 1` during recovery.
7. Rebuild the visible todo checklist from the refreshed `phase-manifest.md`, ignoring archived future phases.

If both `state.md` and the artifact set imply the run is already complete, present the preserved report path and stop.

---

## Automated Review Loops

Every alignment and planning stage runs an internal automated review loop before human review or downstream consumption. Each loop caps at a maximum to prevent infinite loops; the minimum is 1 round (PASS at any round terminates).

| Stage                         | Reviewer Agent                               | Max Rounds | Failure Action                                                                           |
| ----------------------------- | -------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------- |
| 1 — Goals                     | `qrspi-goals-reviewer`                       | 5          | Re-dispatch synthesizer with review feedback                                             |
| 2 — Research                  | `qrspi-research-reviewer`                    | unbounded  | Generate incremental follow-up batches until clean or stalled                            |
| 4 — Design                    | `qrspi-design-reviewer`                      | 5          | Re-dispatch design synthesizer with feedback; checks slice DAG coherence and Architectural Patterns scope instead of Mermaid diagram |
| 4.5 — Skeleton (smoke check)  | `qrspi-fast-impl-loop` (smoke check)         | 1          | FAIL → backward loop to Design or Error Handling                                         |
| 4.5 — Structure (mapping)     | `qrspi-structure-reviewer`                   | 5          | Re-dispatch structure mapper with feedback; `unclean-cap` at round 5 proceeds without a gate (no human review — Plan reviewer + feasibility checker are the downstream safety net) |
| 6 — Plan (plan review)        | `qrspi-plan-reviewer`                        | 6          | Re-dispatch plan writer with feedback; stable-cap if same `Fix Guidance` repeats         |
| 6 — Plan (task-spec review)   | `qrspi-task-spec-reviewer`                   | 3 per task | Repair in place; unresolved cross-task conflicts → Stage 6 FAIL                          |
| 6 — Plan (feasibility + patch)| `qrspi-feasibility-checker` + `qrspi-plan-patcher` | 2   | Patch failing subgraph in place; after 2 rounds → `feasibility-unclean` escalation gate |
| 8.5 — Replan                  | `qrspi-replan-reviewer`                      | 5          | Re-dispatch replan writer with feedback; stable-cap if same `Fix Guidance` repeats       |

Review loop logic:

- If the reviewer returns `PASS` at any round, the loop terminates immediately with `clean`. The previous "min 2" confirmation re-review has been removed (it cost a full reviewer round per clean stage without ever changing the outcome).
- If the reviewer returns `FAIL` and the maximum has not been reached, re-dispatch the synthesizer/writer with review feedback, then re-review.
- For Stage 2 (Research), the outer loop keeps running until the cumulative reviewer returns `clean` or the unresolved-question snapshot stalls. A research `stable-cap` now means the loop stopped making a meaningful delta, not that it hit a fixed round cap.
- For Stage 6 (Plan) and Stage 8.5 (Replan): if two consecutive FAIL rounds emit identical `### Fix Guidance` (whitespace-normalized), terminate with `stable-cap`; the rerun loop is not converging and additional rounds will not help.
- If the reviewer returns `FAIL` at the maximum round cap, terminate with `unclean-cap`.

Terminal review states:

- `clean` — the final review round passed.
- `stable-cap` — Research/Plan/Replan only. For merged Research, the unresolved-question snapshot stalled without a meaningful delta, so the stage continues automatically to Design with the remaining concerns captured in `research/open-questions.md` and `reviews/research-review-round-NN.md`. For Plan/Replan, downstream still runs only after deepwork raises a question gate before continuing.
- `unclean-cap` — reached the maximum with outstanding concerns. For Goals/Design/Structure, this surfaces in the human gate. For Plan/Replan (no human gate), deepwork raises a question gate before continuing to the next stage.

Stage 2 (Research) now owns both question generation and research. It alternates between incremental question-batch generation and research passes until the cumulative research state is clean or the unresolved-question snapshot stalls. A stalled loop returns `PASS` with `terminal_review_state = stable-cap`, preserving the latest unresolved items for downstream design and planning.

Stage 4.5 (Skeleton+Structure) runs between Design and Plan on the full route. It selects the thinnest end-to-end slice from `design.md` (preferring the Foundation Slice, otherwise the slice most depended on per the `## Slice Dependency DAG`), creates a single task spec via codebase recon (no structure.md dependency), dispatches `qrspi-fast-impl-loop` in a fresh git worktree, and smoke-checks the result. A PASS squash-merges the skeleton code onto the pipeline branch, writes `skeleton-results.md` with a `## Plan Handoff` section, then immediately dispatches `qrspi-structure-mapper` and runs an automated structure review loop (up to 5 rounds) to produce `structure.md`. Stage 6 (Plan) reads both `skeleton-results.md` (to avoid re-assigning skeleton files as fresh CREATE tasks) and `structure.md` (for the file map, interfaces, and system architecture diagram). A FAIL with a backward loop request from the skeleton build or structure mapper routes immediately back to Design — no plan, phases, or tasks exist yet, making this the cheapest possible validation point. Resume after a partial run uses `skeleton-results.md` as an internal checkpoint: if the build passed but `structure.md` is absent, the stage re-enters only at the structure mapping sub-step (no rebuild). Stage 4.5 is skipped on the quick-fix route.

Stage 6 (Plan) now runs three review layers and a pre-implementation check: (1) a plan-level review loop (max 6 rounds, stable-cap detection) by `qrspi-plan-reviewer`; (2) a per-task spec review loop (max 3 rounds) by `qrspi-task-spec-reviewer` repairing each spec in place, gated on plan review being `clean`; (3) a feasibility check and bounded patch loop (max 2 rounds) by `qrspi-feasibility-checker` and `qrspi-plan-patcher`, gated on both reviews being clean. The feasibility check runs each task spec's `## Feasibility Checklist` items against the real codebase before any build. Failures trigger `qrspi-plan-patcher` which regenerates only the failing task subgraph in place (no deletions, stable IDs). After 2 rounds, unresolved feasibility failures are recorded as `feasibility-unclean` and surfaced to the user via deepwork's Stage 6 escalation gate — the same path as `unclean-cap`. After all three layers complete, `qrspi-baseline-checker` runs and the final review status block is appended to every `tasks/task-NN.md`.

---

## Operational Rules

- The deepwork agent never writes project code or runs project commands itself. It delegates all implementation work through direct subagent invocation.
- Its edit permission is limited to pipeline state files inside `.pipeline/qrspi-<run-id>/`. The only repository commands deepwork may run itself are narrowly scoped git checkpoint commands (at stage boundaries) and pipeline-directory management commands required to manage stage boundaries.
- After each subagent dispatch, the deepwork agent stops and waits for the subagent response before continuing.
- Inter-stage state lives in pipeline files, not in todo metadata. The `todowrite` tool is only for the user-visible progress checklist.
- Research isolation is structurally enforced: `goals.md` is never passed to any researcher, reviewer, or synthesizer in Stage 2. Researchers receive only the question text from the active round-local question-batch snapshot under `research/iterations/round-NN/questions.md`; the top-level `questions.md` file remains a compatibility snapshot.
- Stage 2 includes independent question leakage and question quality reviews before any research begins.
- Stage 6 records a pre-implementation baseline so later verification can distinguish known failures from new regressions.
- Stage 6 writes the canonical initial `tasks/` directory, maintains `tasks/inactive/`, `tasks/outlines/inactive/`, and `reviews/task-spec/inactive/` as archives for superseded artifacts, and deepwork creates `phases/phase-01/tasks/` as a symlink to that canonical task set after Plan completes.
- Stage 7 includes a per-task code review gate (6 specialized reviewers), validates that every task listed for the current phase exists before implementation begins, writes phase-local execution artifacts including `regression-results.md` (post-all-waves baseline regression comparison), and remediates new regressions in up to 3 bounded rounds. Stage 7 also creates per-wave git checkpoints (`qrspi: phase [N] wave [N] complete`), per-task squash-merge commits (`qrspi: phase [N] task [T]`), per-remediation-round git checkpoints (`qrspi: phase [N] remediation round [N]`), and a post-remediation integration checkpoint when remediation succeeds (`qrspi: phase [N] post-remediation integration`).
- Stage 7 runs each task dispatch in its own ephemeral git worktree under `<repo-parent>/.qrspi-worktrees/<run-id>/phase-NN/task-T` on a per-task branch (`qrspi-task/<run-id>/phase-NN/task-T`). Successful tasks are squash-merged back onto the pipeline branch in stable task order; failed tasks leave their worktree and branch in place for inspection. A squash conflict triggers a one-shot rebase-and-retry inside the worktree (driven by a fix-mode dispatch with `MODE: rebase-conflict` in the regression evidence) before the task is abandoned.
- Stage 8 and Stage 8.5 write only to the active phase directory plus shared review history.
- Stable task IDs are preserved across replans. Replan uses the current remaining task specs as the authoritative carry-forward source, writes the complete next-phase task set into `phases/phase-NN/tasks/`, and appends a review-status block before Stage 7 consumes it.
- Verify and Report aggregate by enumerating `phases/phase-*/` rather than relying on top-level cumulative execution or acceptance files.

---

## Human Gates

Two stages require human approval before proceeding:

| Stage      | Artifact    | What the User Reviews                                                   |
| ---------- | ----------- | ----------------------------------------------------------------------- |
| 1 — Goals  | `goals.md`  | Intent, constraints, non-goals, acceptance criteria                     |
| 4 — Design | `design.md` | Approach, vertical slices + dependency DAG, phases, replan gates, tests |

All human gates present the automated review status to the user ("passed clean in round N" or "reached the N-round cap with remaining concerns documented in ...").

Human gate prompts should stay concise. They should direct the user to the generated artifact path under `.pipeline/qrspi-<run-id>/...` for the full document instead of pasting the entire artifact body into the question prompt.

Rejection captures feedback in `feedback/{step}-round-NN.md`. The re-generation subagent receives all prior feedback files to avoid repeating rejected approaches. After human feedback is incorporated, the automated review loop restarts from round 1 before the next human review.

---

## Backward Loops

Stages 4.5 (Skeleton), 7 (Implement), 8 (Accept-Test), 8.5 (Replan), and 9 (Verify) can trigger backward loops when a fundamental issue is discovered. Stage 8 uses a dedicated `qrspi-backward-loop-detector` subagent to classify persistent failures and recommend whether a backward loop is needed. Stage 8.5 triggers a formal backward loop when the remaining work can no longer stay within the existing goals or design.

### Option P — Incremental Plan Patch (LOOP_PLAN default)

When a backward loop request has `Affected Artifact: plan`, the recommended default action is **Option P — Incremental Plan Patch**. Unlike options A/B/C, option P does not delete artifacts or archive the current phase. Instead:

1. `qrspi-plan-patcher` regenerates only the failing task specs and their transitive dependents in the active `<phase-dir>/tasks/` set, preserving stable task IDs. Phase 1 resolves through the canonical `tasks/` symlink; later phases use their phase-local task copies.
2. `qrspi-feasibility-checker` re-checks the patched active-phase tasks against the real codebase.
3. `qrspi-implement` is re-entered in `patch` mode with only the patched task IDs, reusing existing wave/worktree/squash-merge machinery.

Option P is bounded to **2 runtime rounds per phase**, counted by unique attempted round numbers represented by `feedback/plan-patch-phase-NN-round-RR.md` or `feedback/plan-patch-phase-NN-round-RR-failed.md`. Patcher escalation files and Stage 6's earlier `feedback/feasibility-patch-round-NN.md` files do not consume this runtime budget. On exhaustion, or when the patcher escalates with a backward loop request of its own, the heavy options (A, B, C) become the fallback. Option P is unavailable on the quick-fix route.

### Stage 9 → Stage 7 Auto-Fix Route

When Stage 9 (Verify) returns FAIL, deepwork first attempts a single auto Stage 7 fix-mode pass before presenting backward-loop options:

1. The verifier's failing rows are formatted as regression evidence and passed to `qrspi-implement` with `=== MODE === verify-fix` and the previous phase as the active phase.
2. `qrspi-implement` runs **only** the regression remediation path (no waves, no integration), capped at one round, then returns.
3. Deepwork re-dispatches `qrspi-verify`. If the new result is PASS or PARTIAL, deepwork proceeds to Stage 10. If the second Stage 9 attempt also returns FAIL, deepwork falls into the standard Backward Loop Protocol with the verify failure as the loop request body.

This converts a common failure mode (small last-mile regression visible only at full-suite verify) from "abort/retry" into "automated single-shot remediation with operator escalation only on persistence."

The deepwork agent presents the issue to the user with these options:

**Full route options (LOOP_PLAN with patch budget remaining):**

| Option | Action                                                                                                            |
| ------ | ----------------------------------------------------------------------------------------------------------------- |
| P      | **Incremental Plan Patch** ← Recommended (no deletion, bounded to 2 rounds)                                       |
| A      | Loop back to **Design** (re-architect the approach; deletes design.md + skeleton-results.md + structure.md + plan artifacts) |
| B      | Loop back to **Structure mapping** (re-run only the structure mapping sub-step; preserves skeleton-results.md and the skeleton commit — cheap re-entry) |
| C      | Loop back to **Plan** (revise task specifications — heavy, archives phase)                                        |
| D      | Defer to next **Replan** (record issue for phase boundary)                                                        |
| E      | Attempt a **local fix** within the current stage                                                                  |
| F      | **Continue as-is** (accept the limitation)                                                                        |
| G      | Full reset to **Goals** (restart with accumulated learnings)                                                      |

**Full route options (non-LOOP_PLAN, or LOOP_PLAN with patch budget exhausted):**

| Option | Action                                                                                                            |
| ------ | ----------------------------------------------------------------------------------------------------------------- |
| A      | Loop back to **Design** (re-architect the approach; deletes design.md + skeleton-results.md + structure.md + plan artifacts) |
| B      | Loop back to **Structure mapping** (re-run only the structure mapping sub-step; preserves skeleton-results.md and the skeleton commit — cheap re-entry) |
| C      | Loop back to **Plan** (revise task specifications)                                                                |
| D      | Defer to next **Replan** (record issue for phase boundary)                                                        |
| E      | Attempt a **local fix** within the current stage                                                                  |
| F      | **Continue as-is** (accept the limitation)                                                                        |
| G      | Full reset to **Goals** (restart with accumulated learnings)                                                      |

**Quick-fix route options** (Design and Structure mapping are skipped, so A and B are unavailable; Replan is skipped, so D is unavailable; P is unavailable):

| Option | Action                                                       |
| ------ | ------------------------------------------------------------ |
| C      | Loop back to **Plan** (revise task specifications)           |
| E      | Attempt a **local fix** within the current stage             |
| F      | **Continue as-is** (accept the limitation)                   |
| G      | Full reset to **Goals** (restart with accumulated learnings) |

Loop-back mechanics (options A, B, C):

1. Write loop feedback to `feedback/{stage}-loop-{NN}.md`.
2. Write `feedback/{stage}-loop-{NN}-evidence.md` with the triggering request, current phase artifacts, current plan/manifest, and task specs before moving or deleting anything.
3. Preserve completed phase directories `phases/phase-01/` through `phases/phase-(N-1)/` unchanged.
4. Archive the current incomplete phase directory under `phases/archive/failed-phase-NN-loop-{NN}/` and archive any unstarted future phase directories under `phases/archive/`.
5. Delete the regenerated top-level artifacts owned by the loop target or later stages:
   - Option B (Structure mapping): `structure.md` plus all Plan artifacts. Preserve `skeleton-results.md` and the skeleton commit — only the mapping step re-runs.
   - Option A (Design): `design.md`, `skeleton-results.md`, `structure.md`, plus all Plan artifacts. The skeleton commit stays on the branch; the feedback file notes that the branch contains skeleton code from the prior design iteration.
6. Reset todo items for the target stage and all downstream stages, removing stale future-phase checklist entries.
7. Overwrite `state.md` with the loop target as `next_stage` (Design → `design`, Structure mapping → `skeleton`, Plan → `plan`), increment `backward_loops`, set `current_phase` to the earliest incomplete phase when completed phases are being preserved, and reset `current_phase` to `1` only when no completed phases remain or the loop target is before phased execution.
8. Re-enter the pipeline at the target stage. For Phase 2 and later loopbacks to Design, Structure mapping, or Plan, deepwork passes `NEXT REMAINING PHASE`, the prior `phase-manifest.md`, preserved completed-phase artifacts, the loop feedback file, and the loop evidence file as context.

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
2. Determines the run-level automation policy: `interaction_mode` defaults to `interactive` and is set to `automated` only when the user explicitly asks for noninteractive execution; `failure_policy` defaults to `fail-closed` and is set to `best-effort` only when the user explicitly asks for best-effort automation.
3. Generates a run ID with `date +%Y%m%d-%H%M%S`, prefixed with `qrspi-`.
4. Creates `.pipeline/qrspi-<run-id>/phases/` and `.pipeline/qrspi-<run-id>/telemetry/`, initializes an empty `telemetry/events.jsonl`, and checks out branch `qrspi/<run-id>` from `main`.
5. Writes initial `state.md` with `route: unknown`, `next_stage: goals`, `interaction_mode`, `failure_policy`, and `resume_source: fresh`. Emits the `run.started` telemetry event with `route: "unknown"`.
6. Creates the visible progress checklist using `todowrite` (nine items: Stage 1 Goals, Stage 2 Research, Stage 4 Design, Stage 4.5 Skeleton+Structure, Stage 6 Plan, Phase 1 Implement, Phase 1 Acceptance test, Stage 9 Verify, Stage 10 Report).
7. After Plan completes, creates `phases/phase-01/tasks/` as a symlink to `../../tasks/` and creates any additional empty planned phase directories.
8. Immediately enters Stage 1.

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

### Stage 2 — Research

#### qrspi-research

Merged stage orchestrator. Dispatches `qrspi-questions` to generate the initial batch, then alternates between batch-local research passes and cumulative review. It preserves strict goal isolation for all researcher-facing work, keeps the compatibility snapshots (`questions.md`, `question-*-review.md`) plus the cumulative research summary (`research/summary.md`), and continues generating incremental follow-up batches until the cumulative findings are clean or the unresolved-question snapshot stalls. A stalled loop returns PASS with `stable-cap` and preserves the latest unresolved items in `research/open-questions.md` and `reviews/research-review-round-NN.md`.

#### qrspi-questions

Internal question-batch orchestrator. Supports `initial` and `follow-up` modes, dispatches the question generator, runs dual independent reviews (leakage and quality), and writes both the latest compatibility snapshots and a round-local question batch file. No human gate runs in this stage.

#### qrspi-question-generator

Performs a shallow repo orientation to ground the batch in the actual codebase. In `initial` mode it uses the normalized goal inventory as the completeness contract. In `follow-up` mode it uses unresolved open questions plus the question ledger as the batch contract and emits only new incremental questions. Every question carries four fields: `Tag`, `Covers`, `Answer shape`, and `Decision unblocked`. Read-only.

#### qrspi-question-leakage-reviewer

Independently reviews initial and follow-up question batches against `goals.md` and flags any question text that leaks the requested change to a goal-blind researcher. Judgment is scoped to question text only — `Covers`, `Answer shape`, and `Decision unblocked` remain out of scope. Read-only.

#### qrspi-question-quality-reviewer

Independently reviews question batches for per-question completeness, boundedness, objectivity, tag accuracy, and decision relevance. In `initial` mode it checks full normalized-goal coverage. In `follow-up` mode it checks open-question coverage, non-duplication against the ledger, and incremental-scope discipline. Emits a `### Traceability Matrix` in every review output. Read-only.

#### qrspi-research-pass

Internal batch-local research runner. Takes one active question batch, dispatches codebase and web researchers per tag, applies the greenfield fallback when codebase findings are empty or low-signal, writes round-local `q-NN.md` artifacts and a round-local summary, and runs a bounded batch review loop before returning control to the outer research stage.

#### qrspi-codebase-researcher

Researches a single question against the current codebase using grep, find, cat, and ls. Returns factual findings with file:line references. Never sees `goals.md`. Pure documentarian — describes what exists, never suggests changes. Read-only.

#### qrspi-web-researcher

Researches a single question using web search (webfetch). Returns factual findings with source URLs. Never sees `goals.md`. Pure documentarian. The only agent in the pipeline with `webfetch: allow`. Read-only.

#### qrspi-research-synthesizer

Combines supplied per-question research findings into a batch or cumulative summary organized by topic. Deduplicates overlapping findings, cross-references supported discoveries, and emits an explicit `## Open Questions` section that lists only material unresolved areas or `None.`. Read-only.

#### qrspi-research-reviewer

Reviews research artifacts in two modes. `batch-pass` validates one researched batch and decides whether that batch must be rerun or is ready for the outer loop. `cumulative-loop` validates cumulative findings, identifies unresolved material questions, and recommends `clean`, `generate-follow-up-questions`, or `stalled`. Read-only.

---

### Stage 4 — Design

#### qrspi-design

Stage orchestrator. Conducts interactive design discussion with the user (2–3 approaches, trade-offs, vertical slice decomposition, phase grouping, replan gates, test strategy). Enforces guardrails against horizontal layer planning, vague test strategy, missing phase gates, missing slice dependency DAG, and speculative future-proofing. Dispatches the design synthesizer, runs the automated design review loop, and holds a human gate.

#### qrspi-design-synthesizer

Synthesizes a design document from goals, research summary, and the interactive design discussion. Structures the chosen approach, conceptual architectural patterns (no component/file detail), vertical slice decomposition with a slice dependency DAG, phases with replan gates, test strategy, and key decisions with trade-offs. Does not produce a Mermaid system diagram — that is produced by the structure mapper in Stage 4.5 where it can reflect the merged skeleton code and approved file map. Handles feedback-driven re-generation. Read-only.

#### qrspi-design-reviewer

Reviews `design.md` independently for goals alignment, vertical slice quality, test strategy completeness, internal consistency, research congruence, YAGNI compliance, phase coherence, slice DAG coherence, and that Architectural Patterns stays at the conceptual level. Does not check for a Mermaid system diagram. Flags horizontal decomposition, speculative architecture, weak replan gates, or vague testing. Read-only.

---

### Stage 4.5 — Skeleton + Structure

#### qrspi-skeleton

Stage 4.5 orchestrator for the full route (skipped on quick-fix). Selects the thinnest end-to-end slice from `design.md` (`## Vertical Slices`, preferring the Foundation Slice), derives file paths via codebase recon (grep/find/ls/cat), writes a minimal ephemeral `skeleton-task.md`, creates a fresh git worktree, and dispatches `qrspi-fast-impl-loop` once using the non-phase `skeleton/` execution directory. On PASS with `Review Status: CLEAN`, squash-merges the skeleton code onto the pipeline branch, writes `skeleton-results.md`, then immediately dispatches `qrspi-structure-mapper` and runs the automated structure review loop (up to 5 rounds), producing `structure.md`. Stage 6 (Plan) reads both `skeleton-results.md` (to avoid re-assigning skeleton files as fresh tasks) and `structure.md` (for the file map, interfaces, and system architecture). On FAIL with a `### Backward Loop Request` from the skeleton build or structure mapper, the request routes back to Design only — the cheapest possible validation point since no plan, phases, or tasks exist yet. Resume uses `skeleton-results.md` as an internal checkpoint: PASS + missing `structure.md` re-enters only the mapping sub-step.

#### qrspi-structure-mapper

Maps each vertical slice from the design to specific files and components. Defines interfaces between components (function signatures, class signatures, type definitions). Tracks CREATE vs. MODIFY per file and verifies paths against the actual codebase. Documents skeleton-created files as `EXISTS (skeleton)` using their real on-disk interfaces as ground truth. Produces a Mermaid file/module architectural diagram plus an authoritative `## System Architecture` diagram grounded in verified existing/skeleton modules and planned `CREATE` entries from the file map — this is the system diagram that Design no longer carries. Handles feedback-driven re-generation. Read-only.

#### qrspi-structure-reviewer

Reviews `structure.md` independently for design alignment, file action correctness, skeleton fidelity, interface completeness, interface compatibility, convention adherence, cross-slice dependency clarity, file/module diagram quality, architecture fidelity, and granularity. Verifies MODIFY, CREATE, and EXISTS paths against the codebase; checks that the system architecture diagram uses verified real modules for existing/skeleton/MODIFY components and labels planned components only when they appear as `CREATE` entries in the file map. Read-only.

---

### Stage 6 — Plan

#### qrspi-plan

Stage orchestrator. Reads route-appropriate inputs plus optional repository guidance from `AGENTS.md`, dispatches the plan writer to produce a draft plan and task outlines, runs the automated plan-level review loop (max 6 rounds, with stable-cap detection on repeated reviewer guidance), generates individual task specs from those outlines, runs a per-task review loop (max 3 rounds) when the plan-level loop terminated `clean`, blocks on unresolved task-spec failures or cross-task conflicts, appends final review status (plan: `clean`/`stable-cap`/`unclean-cap`; task-spec: `task_spec_clean` or `skipped`) to each task spec, and dispatches the baseline checker. When the plan-level loop terminates in `stable-cap` or `unclean-cap`, the per-task review loop is skipped entirely; the baseline checker still runs and deepwork's Stage 6 escalation gate surfaces the upstream concern before Stage 7 begins. No human gate.

#### qrspi-plan-writer

Writes ordered task outlines with task metadata, dependencies, phase assignments, scope, acceptance-criteria coverage, and stable task IDs while honoring repository instructions from `AGENTS.md` when present. Produces `plan.md`, `phase-manifest.md`, and individual `task-NN.outline` files. Supports full route (uses all prior artifacts) and quick-fix route (single outline from goals + research). Read-only.

#### qrspi-task-spec-writer

Loads the persisted `task-NN.outline` plus upstream artifacts from the pipeline run directory, expands that outline into a self-contained `task-NN.md` spec, and writes the task file directly into the current run's `tasks/` directory. Uses the canonical outline path under `tasks/outlines/` plus `goals.md`, `requirements.md`, `research/summary.md`, `plan.md`, and `phase-manifest.md` for all routes, and also reads `design.md` and `structure.md` for full-route tasks. Produces concrete file paths, descriptions, test expectations, dependency explanations, traceability metadata, and a `## Source Traceability` section citing upstream artifact sections.

#### qrspi-task-spec-reviewer

Per-task mutating reviewer. Reads the current task outline, current task spec, full plan, design, and structure, then loads active sibling task specs from the canonical top-level `tasks/` directory to check outline-to-spec fidelity, structure-slice fidelity, source-traceability completeness, dependency correctness, self-containment, and cross-task consistency. Repairs only the current `task-NN.md` file in place. Records unresolved cross-task conflicts it could not fix locally.

#### qrspi-plan-reviewer

Reads the current `plan.md`, `phase-manifest.md`, and active `tasks/task-NN.md` files from the pipeline run directory, then reviews the plan for AGENTS guidance compliance, goals coverage, dependency correctness, phase and wave coherence, task self-containment, source traceability, file specificity, test expectation specificity, and placeholder-free quality. Flags forward dependencies, vague files, vague tests, missing coverage, invalid source traceability citations, conflicts with `AGENTS.md`, or overview/task mismatches. Read-only.

#### qrspi-feasibility-checker

Read-only pre-implementation gate dispatched by `qrspi-plan` after task-spec review passes. Runs each task's `## Feasibility Checklist` items — `path-exists:`, `symbol-exists:`, `import-resolves:`, and `command-exits-0:` — against the real codebase using bash and minimal build probes. Writes `feasibility-results.md` with per-task PASS/FAIL and the first failing check per task. A PASS confirms all plan preconditions are satisfiable before any build begins. Never modifies files.

#### qrspi-plan-patcher

Incremental plan-patch agent invoked when `qrspi-feasibility-checker` finds unsatisfied preconditions (Stage 6 D.5 loop) or when the backward-loop protocol chooses Option P. Classifies the failure as local (plan defect) or upstream (structure/design/goals). For local defects, regenerates only the failing tasks and their transitive dependents in place, preserving stable task IDs, `plan.md`, `phase-manifest.md`, and all other task specs. Returns a `### Backward Loop Request` immediately when a local fix is impossible. Never deletes plan-wide artifacts.

#### qrspi-baseline-checker

Records the pre-implementation build, lint, typecheck, E2E, and test baseline before Stage 7 begins. Produces `baseline-results.md`, capturing known pre-existing failures without attempting fixes and marking missing checks as `SKIPPED` or `NOT CONFIGURED`.

---

### Stage 7 — Implement

#### qrspi-implement

Stage orchestrator. Analyzes current-phase task dependencies into waves, then dispatches `qrspi-fast-impl-loop` once per task in each wave. Each task dispatch executes in its own ephemeral git worktree (`<repo-parent>/.qrspi-worktrees/<run-id>/phase-NN/task-T`) on a per-task branch (`qrspi-task/<run-id>/phase-NN/task-T`); successful tasks are squash-merged back onto the pipeline branch in stable task order with `qrspi: phase [N] task [T]` commits. When a squash conflict occurs, Stage 7 attempts one rebase-and-retry inside the worktree via a fix-mode dispatch before abandoning the task. After each completed wave it runs a wave-level E2E regression gate and creates a git checkpoint (`qrspi: phase [N] wave [N] complete`); failed E2E rounds enter a bounded E2E remediation loop (up to 3 rounds). After all waves it runs integration and baseline regression checks in parallel and writes `regression-results.md`. If the baseline regression check returns new failures it enters a bounded remediation loop (up to 3 rounds), re-dispatching affected tasks in `fix` mode and re-running the regression checker per round, then re-running integration once remediation passes, with a git checkpoint after each round (`qrspi: phase [N] remediation round [N]` plus `qrspi: phase [N] post-remediation integration`). It validates that every task listed for the phase exists in `phases/phase-NN/tasks/`, records per-task review outcomes, and writes phase-local execution artifacts. In `verify-fix` mode it skips waves and the standard integration step, runs a single regression-remediation pass seeded with the Stage 9 verifier's failing rows (re-dispatching affected tasks in `fix` mode against fresh worktrees, then re-running the baseline regression and integration checkers), and appends a `## Verify-Fix Pass` section to `stage7-summary.md`. Verify-fix is single-shot — no multiple rounds and no further escalation inside Stage 7 itself. In `patch` mode it runs only the tasks named in `=== PATCH TASKS ===`, creates fresh worktrees for them, computes waves scoped to the patch subset, squash-merges and gates with the same E2E/integration/regression machinery as phase mode, and appends a `## Patch Pass` section to `stage7-summary.md`.

#### qrspi-e2e-regression-checker

Wave-level E2E regression gate. Re-runs the configured E2E command when the baseline says E2E is configured, compares current failures against the baseline E2E inventory, attributes new failures to suspected task IDs using the cumulative execution manifest, and returns PASS or FAIL without fixing anything.

#### qrspi-fast-impl-loop

Owns one task invocation. Sequences `qrspi-fast-impl-code`, `qrspi-fast-impl-test`, and `qrspi-fast-impl-verify` in fresh mode, or code/test repair paths in fix mode. It routes post-verify failures by explicit route hint, detects stalls, enforces an 8-cycle budget, and returns the Stage 7 task result contract.

#### qrspi-fast-impl-code

Delegates production-code implementation or repair to `build`. It never authors tests, stops as soon as the targeted slice builds, and requests a backward loop when the task requires upstream plan, structure, or design changes.

#### qrspi-fast-impl-test

Discovers, classifies, adopts, repairs, and writes deterministic behavior tests after production code exists. It rejects flaky, harness-noisy, ambiguous, type-only, or implementation-detail tests as unsafe evidence.

#### qrspi-fast-impl-verify

Runs targeted verification, dispatches the specialized code-review gate, applies bounded local fixes through `build`, and commits only when verification passes and review status is `CLEAN`. Returns an explicit route hint for any remaining failure.

#### qrspi-code-review

Per-task review orchestrator. Reads changed files, selects applicable specialist reviewers using deterministic grep and wc signals, dispatches them in parallel, and collates findings. Blocks only on CRITICAL/HIGH severity. Always dispatches code-quality and test-coverage reviewers. Conditionally dispatches others based on code content:

| Reviewer                         | Focus                                      | Trigger                                                             |
| -------------------------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| `qrspi-review-code-quality`      | Clean code, maintainability                | Always                                                              |
| `qrspi-review-test-coverage`     | Missing test cases                         | Always                                                              |
| `qrspi-review-security`          | Vulnerabilities, secrets, injection        | Auth/crypto/HTTP/FS signals in code                                 |
| `qrspi-review-silent-failure`    | Swallowed errors, missing logging          | try/catch/error/async signals                                       |
| `qrspi-review-goal-traceability` | Goal-to-code alignment                     | Full route only                                                     |
| `qrspi-review-code-simplifier`   | Over-engineering, unnecessary abstractions | > 3 files, > 200 changed-file lines, or wrappers/factories detected |

The code simplifier is always non-blocking (advisory only).

#### qrspi-integration-checker

Runs a lightweight integration gate after all implementation waves complete. Checks changed-file build sanity, shared interface compatibility, generated-artifact parity for derived artifacts (schemas, docs, declarations, generated clients, manifests), and targeted smoke checks. Uses the review status summary as a risk signal when interpreting failures. Produces `integration-results.md` and `stage7-integration-summary.md`. Can trigger backward loops for structural mismatches.

#### qrspi-baseline-regression-checker

Post-all-waves baseline regression gate. Diffs the current build, lint, typecheck, E2E, and test state against `baseline-results.md`, attributes new failures to suspected task IDs using the cumulative execution manifest, and returns PASS or FAIL without fixing anything. Produces `phases/phase-NN/regression-results.md`. Invoked by Stage 7 after all implementation waves and integration checks, and re-invoked after each remediation round.

---

### Stage 8 — Acceptance Test

#### qrspi-accept

Stage orchestrator. Dispatches the acceptance tester to run a phase-scoped acceptance loop against the acceptance criteria assigned to the current phase. The tester records each round as either `lite` (reuse-only execution path, no planner-review fan-out and no test authoring) or `full` (planner review + writer + run + repair loop, max 3 plan-review cycles per round with stable-cap detection). Acceptance mode is reported as `none`, `lite`, `full`, or `mixed` across the phase. The orchestrator forbids production/source fixes; writes outside the configured `TEST FILE BOUNDARY` immediately fail Stage 8 and write a `boundary-violations.md` audit file. If persistent failures remain, it dispatches the backward-loop detector to classify them and recommend next steps. Writes phase-local coverage, acceptance, summary, backward-loop analysis, and (on boundary violation) boundary-violations artifacts plus phase-scoped review history. Each criterion in `acceptance-results.md` carries a `Status` (`PASS`/`FAIL`) and a `Failure Reason` from a fixed enum: `none` (PASS), `blocking_review`, `reconciliation`, `blocked_action`, `boundary_violation`, or `executed_failed`.

#### qrspi-coverage-planner

Drafts or revises the current phase's acceptance coverage plan for a single round. Maps each phase-scoped criterion to a lifecycle action (`reuse`, `revise`, `new`, or `blocked`), a concrete test type, trigger, expected outcome, relevant files or components, and a planned test file before any acceptance reviewers or test-writing work runs.

#### qrspi-acceptance-tester

Runs the acceptance test inner loop. It always starts with the coverage planner, then chooses between two paths:

- `lite` reuse-only path: when every current-phase criterion maps to an existing acceptance suite with `Action: reuse`, it skips planner review and test authoring, executes the mapped suites directly, and still reports per-criterion PASS or FAIL.
- `full` path: dispatches the acceptance-plan reviewers (`qrspi-review-accept-goal-traceability`, `qrspi-review-accept-spec`, and conditionally `qrspi-review-accept-code-quality`), blocks test generation until blocking review findings clear, writes or reconciles the active acceptance tests, validates that stale coverage was deleted before execution, and allows up to 2 acceptance-test-only repair attempts per round for harness, import, command, flake, or assertion defects.

Once a phase leaves `lite` mode the remaining rounds stay `full`. Each round is capped at 3 plan-review cycles; two consecutive cycles with the same blocking findings trigger a `stable-cap` early exit. Production/source defects are recorded as persistent failures for Stage 7 fix/review routing or backward-loop classification. Tests only the acceptance criteria assigned to the current phase in `phase-manifest.md`. Every criterion ends with a `Status` (`PASS`/`FAIL`) and a `Failure Reason` from a fixed enum: `none`, `blocking_review`, `reconciliation`, `blocked_action`, `boundary_violation`, or `executed_failed`.

#### qrspi-review-accept-goal-traceability

Read-only acceptance-plan reviewer dispatched by `qrspi-acceptance-tester` in `full` mode. Checks that each phase-scoped criterion maps to exactly one coverage-plan row with a valid action (`reuse`/`revise`/`new`/`blocked`), trace fields, and no duplicate or extraneous rows. Returns FAIL for any `CRITICAL` or `HIGH` finding.

#### qrspi-review-accept-spec

Read-only acceptance-plan reviewer dispatched by `qrspi-acceptance-tester` in `full` mode. Checks each coverage-plan row for trigger fidelity, outcome fidelity, assertion specificity, boundary inclusion, and action consistency against the criterion. Returns FAIL for any `CRITICAL` or `HIGH` finding.

#### qrspi-review-accept-code-quality

Read-only acceptance-plan reviewer dispatched by `qrspi-acceptance-tester` in `full` mode, only when the coverage plan contains at least one `Action: new` or `Action: revise` row. Checks the planned coverage for determinism, behavior focus, isolation, data realism, anti-patterns, and unnecessary suite sprawl. Returns FAIL for any `CRITICAL` or `HIGH` finding.

#### qrspi-backward-loop-detector

Analyzes the full completed phase context (goals, execution manifest, integration results, acceptance results, persistent failures) with a binary checklist per failure group and derives one of: `NO_LOOP`, `DEFER_REPLAN`, `LOOP_PLAN`, `LOOP_STRUCTURE`, `LOOP_DESIGN`, or `LOOP_GOALS`. The classification is then routed through deepwork's backward loop protocol for user decision.

---

### Stage 8.5 — Replan

#### qrspi-replan

Stage orchestrator. Reads the completed phase directory, prior completed phase summaries, deferred replan feedback, and the authoritative current remaining task specs for the next implementation phase. It dispatches the replan writer to revise remaining work, runs the automated replan review loop (max 5 rounds, with stable-cap detection), writes the complete next-phase task set into `phases/phase-NN/tasks/`, and writes a phase-local replan note. If the writer determines that Goals or Design must change, the stage returns a formal backward-loop request instead of forcing a replan. It only fires on multi-phase full-route runs between phases.

#### qrspi-replan-writer

Revises the remaining plan (tasks, phases, phase-manifest) after a completed phase. It uses the current remaining task specs as the authoritative source for carrying forward unfinished work, may modify, reorder, split, add, remove, or supersede remaining tasks, and emits the complete task set for the next implementation phase only. It must not change goals, the chosen design approach, or completed phases. When Goals or Design must change, it returns a `### Backward Loop Request` instead of replanned artifacts. It also processes any deferred replan feedback from backward loops. Read-only.

#### qrspi-replan-reviewer

Reviews the replanned remaining work for continued alignment to existing goals, no silent design drift, phase coherence, dependency correctness, task self-containment, file specificity, and justified modifications. Read-only.

---

### Stage 9 — Verify

#### qrspi-verify

Stage orchestrator. Enumerates `phases/phase-*/` and dispatches the verifier with per-phase execution manifests, `stage7-summary.md` files (including Phase Evidence Quality), `regression-results.md` per phase, and acceptance results.

#### qrspi-verifier

Runs one full configured build/lint/typecheck/E2E/test pass, checks aggregated per-phase acceptance results, and compares current failures against `baseline-results.md`. May reuse the latest phase's `regression-results.md` when **all** of the following hold: that file reports `### Status — PASS` with `### Skipped Checks` of `None.`; `git log` (filtered to non-test paths) confirms no production-source changes since the last `qrspi: phase [N] *` checkpoint; and the baseline `Coverage` row, if present, also passed in the cached regression results. When reuse is allowed, the verifier carries the cached Build/Lint/Typecheck/Test rows forward and runs only the acceptance test full re-run plus a smoke sub-suite of the configured E2E command. It never fixes issues; failures are reported with evidence for Stage 7 fix/review routing or backward-loop decisions. Reports PASS / PARTIAL / FAIL while distinguishing unchanged baseline failures from new regressions, and emits a `### Code Health Summary` per-phase table covering deterministic/flaky/harness-noisy/ambiguous/redundant test counts, NO_TASK_AUTHORED_TESTS audit overrides, outstanding concerns, coverage status, and Plan/Replan terminal review states.

---

### Stage 10 — Report

#### qrspi-report

Stage orchestrator. Enumerates `phases/phase-*/`, reads per-phase stage summaries and replan notes, and then dispatches the reporter.

#### qrspi-reporter

Formats the Final Report from pipeline config, goals summary, phase manifest, `baseline-results.md`, per-phase acceptance results, per-phase replan notes, and the per-phase stage summaries. Produces a structured markdown report with pipeline route, phase structure, baseline status, per-phase implementation and acceptance status, build/lint/typecheck/E2E/test status, acceptance criteria results, overall status, unresolved items, and the preserved audit trail path. Never writes code or modifies files.
