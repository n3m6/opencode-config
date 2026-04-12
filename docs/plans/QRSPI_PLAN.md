# Plan: qrspi-agent Primary Agent Pipeline

Build a new `qrspi-agent` primary agent implementing the QRSPI methodology adapted for opencode. It takes a user task from intent capture through research, design, planning, TDD implementation, acceptance testing, and verification — using **13 new agents** and a **10-stage pipeline** with two route variants. Clean-slate design, no modifications to existing orchestrator agents.

## Pipeline Routes

```
Full:       Goals → Questions → Research → Design → Structure → Plan → Implement → Accept-Test → Verify → Report
Quick-Fix:  Goals → Questions → Research ──────────────────────→ Plan → Implement → Accept-Test → Verify → Report
```

Human gates on: **Goals**, **Design**, **Structure**. All other stages auto-proceed.

---

## Phase A — Alignment (Stages 1–6)

### Stage 1 — Goals (Human-Gated)

qrspi-agent converses interactively via `question` to capture intent, constraints, and testable acceptance criteria. Also determines route (full vs quick-fix). Dispatches `qrspi-goals-synthesizer` to produce `goals.md` + `config.md`. User approves or rejects with feedback.

Interactive dialogue covers:

- What are you building? Why?
- Constraints and non-goals?
- Testable acceptance criteria (specific + measurable, never subjective)
- Task size → route determination (full vs quick-fix)

Rejection captures feedback in `feedback/goals-round-NN.md` (rejected artifact + user feedback verbatim). Re-generation subagent receives all prior feedback files.

### Stage 2 — Questions (Auto-Proceed)

- Input: `goals.md`
- Dispatches `qrspi-question-generator`
- Tags each question: `codebase` | `web` | `hybrid`
- Self-reviews for goal leakage — questions must be neutral enough that a researcher cannot infer the planned changes
- Produces: `questions.md`

### Stage 3 — Research (Auto-Proceed, Strict Isolation)

- Input: **`questions.md` ONLY** — `goals.md` is never passed to any researcher
- Per-question parallel dispatch:
  - `qrspi-codebase-researcher` for `codebase`-tagged questions (grep, find, cat, read)
  - `qrspi-web-researcher` for `web`-tagged questions (webfetch enabled)
  - `hybrid` questions get both researchers
- Dispatches `qrspi-research-synthesizer` with all per-question findings
- Produces: `research/q-*.md` (per-question) + `research/summary.md` (unified)

### Stage 4 — Design (Human-Gated, SKIP on Quick-Fix)

- Input: `goals.md` + `research/summary.md`
- qrspi-agent presents 2–3 approaches with trade-offs and a recommendation via `question`
- Converges with user on approach and vertical slice decomposition (end-to-end slices, not horizontal layers)
- Dispatches `qrspi-design-synthesizer` with goals + research + conversation summary
- Produces: `design.md` (approach, patterns, vertical slices, test strategy)
- User approves or rejects with feedback

### Stage 5 — Structure (Human-Gated, SKIP on Quick-Fix)

- Input: `goals.md` + `research/summary.md` + `design.md`
- Dispatches `qrspi-structure-mapper`
  - Maps each vertical slice to specific files/components
  - Defines interfaces (function/class signatures)
  - Tracks create vs. modify per file
- Produces: `structure.md`
- User approves or rejects with feedback

### Stage 6 — Plan (Auto-Proceed)

- Full route: all prior artifacts as input
- Quick-fix route: `goals.md` + `research/summary.md` only
- Dispatches `qrspi-plan-writer`
  - Full: ordered task specs with file paths, descriptions, test expectations, dependencies, LOC estimates
  - Quick-fix: single task file from research
- Produces: `plan.md` + `tasks/task-NN.md`

---

## Phase B — Execution (Stages 7–10)

### Stage 7 — Implement (Auto, Wave-Based)

- Input: `plan.md`, `tasks/*.md`, `design.md`, `structure.md`
- qrspi-agent analyzes task dependencies → wave grouping
- Per wave: dispatch `qrspi-implementer` for each task in parallel
  - TDD per task: write failing tests → implement to pass → inline self-review → commit
- **Backward loop trigger**: if implementation reveals a fundamental design/plan flaw → ask user via `question` → optionally loop back to Design/Structure/Plan
- Produces: `execution-manifest.md` + `stage7-summary.md`

### Stage 8 — Acceptance Test (Auto)

- Input: `goals.md` + implemented code
- Dispatches `qrspi-acceptance-tester`
  - Maps each acceptance criterion from `goals.md` to tests
  - Writes + runs tests, reports per-criterion pass/fail
- **Backward loop trigger**: if failures indicate a design-level issue → ask user
- Produces: `acceptance-results.md` + `stage8-summary.md`

### Stage 9 — Verify (Auto, Max 3 Iterations)

- Input: all execution artifacts
- Dispatches `qrspi-verifier`
  - Runs full build/lint/test suite
  - Fix loop: verify → fix → re-verify (max 3)
  - Reports: PASS / PARTIAL / FAIL
- Produces: `stage9-summary.md`

### Stage 10 — Report

- Dispatches `qrspi-reporter` with all stage summaries
- Presents final report to user
- PASS → cleanup `.pipeline/qrspi-<run-id>/`. PARTIAL/FAIL → preserve audit trail.

---

## Agents to Create (13 Files)

| #   | File                            | Mode     | Purpose                                                           | Key Permissions                                             |
| --- | ------------------------------- | -------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| 1   | `qrspi-agent.md`                | primary  | Pipeline controller + interactive dialogue                        | edit (state files), question, task, todowrite, limited bash |
| 2   | `qrspi-goals-synthesizer.md`    | subagent | Synthesize `goals.md` + `config.md` from conversation             | read-only bash                                              |
| 3   | `qrspi-question-generator.md`   | subagent | Generate neutral research questions, self-review for goal leakage | read-only bash                                              |
| 4   | `qrspi-codebase-researcher.md`  | subagent | Per-question codebase research (trace logic, find patterns)       | read-only bash (grep, find, cat, ls)                        |
| 5   | `qrspi-web-researcher.md`       | subagent | Per-question external research                                    | read-only bash + webfetch                                   |
| 6   | `qrspi-research-synthesizer.md` | subagent | Combine per-question findings into unified summary                | read-only                                                   |
| 7   | `qrspi-design-synthesizer.md`   | subagent | Synthesize design document from conversation context              | read-only bash                                              |
| 8   | `qrspi-structure-mapper.md`     | subagent | Map vertical slices to files, define interfaces                   | read-only bash                                              |
| 9   | `qrspi-plan-writer.md`          | subagent | Write ordered task specs with full detail                         | read-only bash                                              |
| 10  | `qrspi-implementer.md`          | subagent | Per-task TDD + inline review (delegates to `@build`)              | full code access (bash, edit, task to @build)               |
| 11  | `qrspi-acceptance-tester.md`    | subagent | Acceptance testing against goals criteria                         | code write for tests (bash, edit, task to @build)           |
| 12  | `qrspi-verifier.md`             | subagent | Build/lint/test verification + fix loop                           | full access (bash, edit, task to @build)                    |
| 13  | `qrspi-reporter.md`             | subagent | Final report formatting                                           | none (read-only data assembly)                              |

---

## Pipeline State Files

```
.pipeline/qrspi-<run-id>/
├── config.md                     Stage 1  — Route (full/quick-fix), metadata
├── goals.md                      Stage 1  — Intent, constraints, acceptance criteria
├── questions.md                  Stage 2  — Tagged research questions
├── research/
│   ├── q-01.md ... q-NN.md      Stage 3  — Per-question findings
│   └── summary.md               Stage 3  — Unified research summary
├── design.md                     Stage 4  — Architecture, vertical slices, test strategy
├── structure.md                  Stage 5  — File mapping, interfaces, create/modify
├── plan.md                       Stage 6  — Overall plan
├── tasks/
│   └── task-NN.md               Stage 6  — Per-task specs
├── feedback/
│   └── {step}-round-NN.md       Any gate — Rejection feedback + rejected artifact
├── execution-manifest.md         Stage 7  — Per-task execution results
├── stage7-summary.md            Stage 7  — Implement summary
├── acceptance-results.md         Stage 8  — Per-criterion test results
├── stage8-summary.md            Stage 8  — Acceptance test summary
├── stage9-summary.md            Stage 9  — Verification summary (includes PASS/PARTIAL/FAIL)
└── stage10-summary.md           Stage 10 — Final report
```

---

## Backward Loops

When a later stage discovers a fundamental issue:

1. The subagent (implementer/tester) reports the issue in its output
2. qrspi-agent asks the user via `question`: "Stage N revealed [issue]. Options: (A) Loop back to [Design/Structure/Plan], (B) Attempt a local fix, (C) Continue as-is"
3. If loop-back approved:
   - Capture current context as feedback in `feedback/{step}-loop-NN.md`
   - Delete artifacts from loop target stage onward
   - Re-run from target stage forward, including feedback as additional input
4. If declined: continue with best-effort local fix or accept as-is

Loop targets:

- Architecture/approach mismatch → loop to **Design**
- File/interface mismatch → loop to **Structure**
- Task specification issue → loop to **Plan**

---

## Route Determination

During Goals (Stage 1), the goals-synthesizer classifies the task:

- **Full**: Features, new products, architectural changes, multi-file changes requiring design alignment
- **Quick-fix**: Bug fixes, small changes, estimated 1–3 file modifications

Route is written to `config.md` and controls which stages execute.
Route change is allowed before Plan executes (Stage 6). After Plan approval, the route is locked.

---

## Implementation Order

| Wave | Steps                                                                                                                                    | Depends On |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| 1    | `qrspi-agent.md` + `docs/QRSPI.md`                                                                                                       | —          |
| 2    | `qrspi-goals-synthesizer`, `qrspi-question-generator`, `qrspi-codebase-researcher`, `qrspi-web-researcher`, `qrspi-research-synthesizer` | Wave 1     |
| 3    | `qrspi-design-synthesizer`, `qrspi-structure-mapper`, `qrspi-plan-writer`                                                                | Wave 2     |
| 4    | `qrspi-implementer`, `qrspi-acceptance-tester`, `qrspi-verifier`, `qrspi-reporter`                                                       | Wave 3     |

---

## Verification

1. Validate YAML frontmatter syntax for all 13 agents
2. Verify research isolation: researchers have NO access to `goals.md` (task permissions + prompt inputs)
3. Verify `qrspi-web-researcher` is the only agent with `webfetch: allow`
4. Verify quick-fix route correctly skips Design + Structure
5. Manual test: full pipeline with a small feature task
6. Manual test: quick-fix route with a bug fix
7. Manual test: trigger backward loop

---

## Decisions

- **Clean slate**: 13 new agents, `qrspi-` prefix, no modifications to existing orchestrator agents
- **Research isolation**: Architecturally enforced — researchers never receive `goals.md`
- **Selective gates**: Goals, Design, Structure only
- **Lean execution**: Reviews inline with implementation, not separate stages
- **Wave-based parallelism** (not worktrees)
- **Artifacts**: `.pipeline/qrspi-<run-id>/`

---

## Further Considerations

1. **Question goal-leakage reviewer**: Currently self-reviewed by the question-generator. A separate reviewer that only sees questions (not goals) would be structurally stronger. Recommend deferring to v2.
2. **Step count tuning**: qrspi-agent handles interactive dialogue + 10 stages. May need ~65 steps. If interactive stages consume too many, consider splitting into separate primary modes.
3. **Multi-phase execution**: QRSPI-plus supports multi-phase (Phase 1 = PoC, Phase 2 = full feature) with Replan between phases. Current design is single-phase. Could add in v2.
