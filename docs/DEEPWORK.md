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
                                │ create run state │
                                │ and branch       │
                                └────────┬─────────┘
                                         │
                          ═══════════════════════════════════════════
                          ║   .pipeline/qrspi-<run-id>/config.md    ║
                          ═══════════════════════════════════════════
                                         │
                                         ▼
                          ┌──────────────────────────────┐
                          │  STAGE 1 — Goals             │
                          │  🔒 Human Gate               │
                          │                              │
                          │  Interactive dialogue via    │
                          │  question tool               │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-goals-synthesizer│  │
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: goals.md, config.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 2 — Questions         │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-question-generator│  │
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: questions.md
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
                          └─────────────┬────────────────┘
                                        │
                          Outputs: research/q-*.md
                                   research/summary.md
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
                          └─────────────┬────────────────┘
                                        │
                          Outputs: design.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 5 — Structure         │
                          │  🔒 Human Gate               │
                          │  (SKIP on quick-fix)         │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │ qrspi-structure-mapper │  │
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: structure.md
                                        │
                                        │
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 6 — Plan             │
                          │  (route locked after this)   │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │   qrspi-plan-writer    │  │
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: plan.md, tasks/task-NN.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 7 — Implement        │
                          │  (wave-based parallel)       │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │  qrspi-implementer     │  │  (per-task TDD)
                          │  │  (× N tasks per wave)  │  │
                          │  └────────────────────────┘  │
                          │                              │
                          │  ↺ backward loop possible   │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: execution-manifest.md
                                   stage7-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 8 — Acceptance Test   │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │qrspi-acceptance-tester │  │
                          │  └────────────────────────┘  │
                          │                              │
                          │  ↺ backward loop possible   │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: acceptance-results.md
                                   stage8-summary.md
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
                               │  PASS → cleanup      │
                               │  PARTIAL/FAIL →      │
                               │  preserve audit trail│
                               └──────────────────────┘
```

## Pipeline Routes

**Full pipeline** — for features, new products, and anything requiring architectural design:

```
Goals → Questions → Research → Design → Structure → Plan → Implement → Accept-Test → Verify → Report
```

**Quick-fix** — for targeted bug fixes, small changes, and 1–3 file modifications. It still reaches Stages 4 and 5, but those stages self-skip and mark themselves skipped before continuing to Stage 6:

```
Goals → Questions → Research → Plan → Implement → Accept-Test → Verify → Report
```

Route is determined during Stage 1 (Goals) and written to `config.md`. Route changes are allowed before Stage 6 (Plan). After Plan is written, the route is locked.

---

## Pipeline State Files

All inter-stage data flows through files in `.pipeline/qrspi-<run-id>/`:

| File                          | Written By | Purpose                                      |
| ----------------------------- | ---------- | -------------------------------------------- |
| `config.md`                   | Stage 1    | Route (full/quick-fix), run_id, and metadata |
| `goals.md`                    | Stage 1    | Intent, constraints, acceptance criteria     |
| `questions.md`                | Stage 2    | Tagged research questions                    |
| `research/q-NN.md`            | Stage 3    | Per-question research findings               |
| `research/summary.md`         | Stage 3    | Unified research summary                     |
| `design.md`                   | Stage 4    | Architecture, vertical slices, test strategy |
| `structure.md`                | Stage 5    | File mapping, interfaces, create/modify      |
| `plan.md`                     | Stage 6    | Overall implementation plan                  |
| `tasks/task-NN.md`            | Stage 6    | Per-task specifications                      |
| `feedback/{step}-round-NN.md` | Any gate   | Rejection feedback + rejected artifact       |
| `execution-manifest.md`       | Stage 7    | Per-task execution results                   |
| `stage7-summary.md`           | Stage 7    | Implementation summary                       |
| `acceptance-results.md`       | Stage 8    | Per-criterion acceptance test results        |
| `stage8-summary.md`           | Stage 8    | Acceptance testing summary                   |
| `stage9-summary.md`           | Stage 9    | Verification summary (PASS/PARTIAL/FAIL)     |
| `stage10-summary.md`          | Stage 10   | Final report                                 |

---

## Operational Rules

- The deepwork agent never writes project code or runs project commands itself. It delegates all implementation work through subagents via the `task` tool.
- Its edit permission is limited to pipeline state files inside `.pipeline/qrspi-<run-id>/`.
- After each `task` dispatch, the deepwork agent stops and waits for the subagent response before continuing.
- Inter-stage state lives in pipeline files, not in todo metadata. The `todowrite` tool is only for the 10-stage progress checklist.
- In mechanical stages, the deepwork agent copies subagent outputs verbatim into pipeline state files.
- In interactive stages (1 and 4), the deepwork agent conducts dialogue via the `question` tool before dispatching synthesizer subagents.
- Research isolation is structurally enforced: `goals.md` is never passed to any researcher. Researchers receive only the question text from `questions.md`.

---

## Human Gates

Three stages require human approval before proceeding:

| Stage         | Artifact       | What the User Reviews                    |
| ------------- | -------------- | ---------------------------------------- |
| 1 — Goals     | `goals.md`     | Intent, constraints, acceptance criteria |
| 4 — Design    | `design.md`    | Approach, vertical slices, test strategy |
| 5 — Structure | `structure.md` | File mapping, interfaces                 |

Rejection captures feedback in `feedback/{step}-round-NN.md`. The re-generation subagent receives all prior feedback files to avoid repeating rejected approaches.

---

## Backward Loops

Stages 7 (Implement) and 8 (Accept-Test) can trigger backward loops when a fundamental issue is discovered. The deepwork agent presents the issue to the user with options:

- **Loop to Design**: Re-architect the approach (cascades through Structure → Plan)
- **Loop to Structure**: Re-map files and interfaces (cascades through Plan)
- **Loop to Plan**: Revise task specifications only
- **Local fix**: Attempt to fix within the current stage
- **Continue as-is**: Accept the limitation

Loop-backs delete downstream artifacts and re-run from the target stage, with feedback captured for the re-run.

---

## Pre-Flight

Before Stage 1 starts, the deepwork agent:

1. Requires an actionable task description from the user.
2. Generates a run ID with `date +%Y%m%d-%H%M%S`, prefixed with `qrspi-`.
3. Creates `.pipeline/qrspi-<run-id>/` and checks out `qrspi/<run-id>` from `main`.
4. Passes that run ID into Stage 1 so `config.md` records it as pipeline metadata.
5. Creates ten todo items for stage progress.
6. Immediately enters Stage 1.

---

## Validation and Error Handling

- If a subagent returns an error or malformed output, the deepwork agent asks the user whether to retry the stage or abort.
- On abort, the run directory is preserved as a partial audit trail.
- After Stage 10, PASS deletes `.pipeline/qrspi-<run-id>/`; PARTIAL and FAIL preserve it for debugging.

---

## Agent Summaries

### Primary Agent

#### deepwork

The top-level deepwork pipeline controller. Accepts a user's task and drives it through a 10-stage pipeline with two route variants (full and quick-fix). Conducts interactive dialogue for alignment stages (Goals, Design) and delegates all implementation to subagents. Manages inter-stage data through pipeline state files and tracks progress via a 10-item todo checklist. Supports backward loops from execution stages back to alignment stages with user approval.

---

### Stage 1 — Goals

#### qrspi-goals-synthesizer

Synthesizes `goals.md` (intent, constraints, non-goals, acceptance criteria) and `config.md` (route, created date, run_id, metadata) from the interactive dialogue context. Ensures all acceptance criteria are specific and testable. Handles feedback-driven re-generation. Read-only.

---

### Stage 2 — Questions

#### qrspi-question-generator

Generates 5–15 neutral, tagged research questions from `goals.md`. Tags each question as `codebase`, `web`, or `hybrid`. Self-reviews every question for goal leakage — ensuring a researcher who reads only the question cannot infer the planned changes. Read-only.

---

### Stage 3 — Research

#### qrspi-codebase-researcher

Researches a single question against the current codebase using grep, find, cat, and ls. Returns factual findings with file:line references. Never sees `goals.md`. Pure documentarian — describes what exists, never suggests changes. Read-only.

#### qrspi-web-researcher

Researches a single question using web search (webfetch). Returns factual findings with source URLs. Never sees `goals.md`. Pure documentarian. The only agent in the pipeline with `webfetch: allow`. Read-only.

#### qrspi-research-synthesizer

Combines per-question research findings into a unified summary organized by topic. Deduplicates overlapping findings and cross-references related discoveries. Read-only.

---

### Stage 4 — Design

#### qrspi-design-synthesizer

Synthesizes a design document from goals, research summary, and the interactive design discussion. Structures the chosen approach, architectural patterns, vertical slice decomposition, test strategy, and key decisions with trade-offs. Handles feedback-driven re-generation. Read-only.

---

### Stage 5 — Structure

#### qrspi-structure-mapper

Maps each vertical slice from the design to specific files and components. Defines interfaces (function/class signatures), tracks create vs. modify per file, and verifies paths against the actual codebase. Handles feedback-driven re-generation. Read-only.

---

### Stage 6 — Plan

#### qrspi-plan-writer

Writes ordered task specifications with file paths, descriptions, test expectations, dependencies, and LOC estimates. Supports full route (uses all prior artifacts) and quick-fix route (single task from goals + research). Read-only.

---

### Stage 7 — Implement

#### qrspi-implementer

Implements a single task using TDD: write failing tests → implement to pass → self-review → commit. Delegates all coding to `@build`. Reports backward loop requests if the task spec is fundamentally unworkable. Max 3 red-green-verify iterations.

---

### Stage 8 — Acceptance Test

#### qrspi-acceptance-tester

Maps every acceptance criterion from `goals.md` to tests, writes and runs them via `@build`. Reports per-criterion PASS or FAIL only. If a criterion is not objectively testable, that is treated as a Stage 1 quality failure rather than a third runtime status. Flags design-level failures for backward loops.

---

### Stage 9 — Verify

#### qrspi-verifier

Runs the full build/lint/test suite and checks acceptance results. Fixes issues via a verify→fix loop (max 3 iterations) by delegating to `@build`. Reports PASS / PARTIAL / FAIL.

---

### Stage 10 — Report

#### qrspi-reporter

Formats the Final Report from pipeline config, goals summary, `acceptance-results.md`, and the stage summaries. Produces a structured markdown report with per-stage results, build/test status, acceptance criteria results, overall status, and unresolved items. Never writes code or modifies files.
