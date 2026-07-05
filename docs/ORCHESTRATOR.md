# Orchestrator Pipeline

## Flowchart

```
                                ┌───────────────────┐
                                │    User Plan      │
                                │   (markdown)      │
                                └────────┬──────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │   PRE-FLIGHT     │
                                │ validate plan,   │
                                │ create run state │
                                │ and branch       │
                                └────────┬─────────┘
                                         │
                          ═══════════════════════════════════════
                          ║ .pipeline/<run-id>/plan.md          ║
                          ║ .pipeline/<run-id>/base-branch.md   ║
                          ═══════════════════════════════════════
                                         │
                                         ▼
                          ┌──────────────────────────────┐
                          │  STAGE 1 — analyzer         │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │ analyzer-task-checker  │  │  (per-task analysis)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │ analyzer-plan-checker  │  │  (cross-task analysis)
                          │  └────────────────────────┘  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: analysis-manifest.md
                                   holistic-findings.md (optional)
                                   stage1-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 2 — executor         │
                          │                              │
                          │  Reads: plan.md,             │
                          │         base-branch.md,      │
                          │         analysis-manifest.md │
                          │         holistic-findings.md │
                          │         (optional)           │
                          │                              │
                          │  Delegates to: @impl-loop    │
                          │  per-task worktrees          │
                          │  (wave-based parallel exec)  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: plan-summary.md
                                   execution-manifest.md
                                   file-list.md
                                   stage2-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 3 — test-coverage-   │
                          │           filler             │
                          │  (max 3 iterations)          │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │  test-coverage-gate    │  │  (behavior analysis)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │  @build (create tests) │  │  (design tests)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │  test-quality-reviewer │  │  (behavior + assertion quality)
                          │  └────────────────────────┘  │
                          │                              │
                          │  Loop: design → quality-   │
                          │        review → repeat      │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: file-list.md (overwrite)
                                   stage3-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 4 — code-review-loop │
                          │  (max 3 iterations)          │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │    code-review         │──┼──▶ specialized reviewers:
                          │  │   (orchestrator)       │  │    • code quality
                          │  └────────────────────────┘  │    • plan traceability
                          │  ┌────────────────────────┐  │    • test coverage
                          │  │    @build (fixes)      │  │    • security
                          │  └────────────────────────┘  │    • silent failure
                          │                              │    • simplifier
                          │                              │
                          │  Loop: review → fix →      │
                          │        build/test → repeat  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: review-critical.md
                                   file-list.md (overwrite)
                                   stage4-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 5 — code-refactor-   │
                          │           loop               │
                          │  (max 3 iterations)          │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │ code-refactor-review   │  │  (find refactor opps)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │    @build (fixes)      │  │  (apply refactors)
                          │  └────────────────────────┘  │
                          │                              │
                          │  Loop: review → fix →      │
                          │        build/test → repeat  │
                          │  (behavior-preserving only)  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: refactor-critical.md
                                   file-list.md (overwrite)
                                   stage5-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 6 — verifier         │
                          │  (max 3 iterations)          │
                          │                              │
                          │  Reads: plan-summary.md,     │
                          │         execution-manifest.md│
                          │         file-list.md,        │
                          │         review-critical.md,  │
                          │         refactor-critical.md │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │ plan-compliance-checker│  │  (plan vs code)
                          │  └────────────────────────┘  │
                          │  ┌────────────────────────┐  │
                          │  │  @build (fixes/tests)  │  │  (build + lint + test)
                          │  └────────────────────────┘  │
                          │                              │
                          │  Result: PASS / PARTIAL /    │
                          │          FAIL                │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: stage6-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 7 — pipeline-reporter│
                          │                              │
                          │  Reads: all stage summaries, │
                          │         review-critical.md,  │
                          │         refactor-critical.md │
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

## Pipeline State Files

All inter-stage data flows through files in `.pipeline/<run-id>/`:

| File                    | Written By    | Purpose                                      |
| ----------------------- | ------------- | -------------------------------------------- |
| `plan.md`               | Pre-Flight    | Full user plan (verbatim)                    |
| `base-branch.md`        | Pre-Flight    | Branch/ref used as the diff baseline         |
| `analysis-manifest.md`  | Stage 1       | Analysis Manifest table                      |
| `holistic-findings.md`  | Stage 1       | Holistic Findings section from analyzer      |
| `stage1-summary.md`     | Stage 1       | Analyzer stage summary                       |
| `plan-summary.md`       | Stage 2       | Condensed plan summary for downstream stages |
| `execution-manifest.md` | Stage 2       | Execution Manifest table                     |
| `file-list.md`          | Stage 2, 3, 4, 5 | Updated file list (overwritten each time) |
| `stage2-summary.md`     | Stage 2       | Executor stage summary                       |
| `stage3-summary.md`     | Stage 3       | Test coverage stage summary                  |
| `review-critical.md`    | Stage 4       | CRITICAL/HIGH findings from code review      |
| `stage4-summary.md`     | Stage 4       | Code review stage summary                    |
| `refactor-critical.md`  | Stage 5       | CRITICAL findings from refactoring           |
| `stage5-summary.md`     | Stage 5       | Refactoring stage summary                    |
| `stage6-summary.md`     | Stage 6       | Verification stage summary                   |

---

## Operational Rules

- The orchestrator never writes project code or runs project commands itself. It delegates all implementation work through subagents via the `task` tool.
- Its edit permission is limited to pipeline state files inside `.pipeline/<run-id>/`.
- After each `task` dispatch, the orchestrator stops and waits for the subagent response before continuing.
- Inter-stage state lives in pipeline files, not in todo metadata. The `todowrite` tool is only for the 7-stage progress checklist.
- The orchestrator is intentionally mechanical: it copies the user plan and named subagent output sections verbatim into pipeline state files rather than summarizing, deduplicating, or reinterpreting them.
- When Stage 1 emits `holistic-findings.md`, the orchestrator passes it through verbatim to Stage 2. The orchestrator does not interpret those findings itself.
- Executor treats holistic findings as routing signals: `Schedule` adjusts wave planning, `Gap` creates synthetic `[Holistic Gap]` tasks, `Guidance` shapes delegations, and `Escalate` pauses for user confirmation.

## Pre-Flight

Before Stage 1 starts, the orchestrator:

1. Requires a markdown plan with actionable tasks.
2. Warns if the plan is large: over 15 tasks triggers a caution, and over 25 tasks requires explicit confirmation.
3. Generates a run ID with `date +%Y%m%d-%H%M%S`.
4. Creates `.pipeline/<run-id>/`.
5. Records the current branch in `.pipeline/<run-id>/base-branch.md`.
6. Checks out `pipeline/<run-id>` from that base branch to isolate the run.
7. Writes the raw plan into `.pipeline/<run-id>/plan.md`.
8. Creates seven todo items for stage progress only, then immediately enters Stage 1.

## Validation And Error Handling

- Each stage validates the structure of the returned manifest or report before moving forward.
- If a stage returns malformed output, the orchestrator retries that stage once with an explicit malformed-output instruction.
- If the retry still fails, the orchestrator asks the user whether to retry the same stage or abort the pipeline.
- On abort, the run directory is preserved as a partial audit trail.
- After Stage 7, PASS deletes `.pipeline/<run-id>/`; PARTIAL and FAIL preserve it for debugging.

---

## Agent Summaries

### Primary Agent

#### orchestrator

The top-level pipeline controller. Accepts a user-provided markdown plan and drives it through a fixed seven-step pipeline. It **never writes code** — all work is delegated to subagents via the `task` tool. It manages inter-stage data by reading/writing pipeline state files in `.pipeline/<run-id>/` and tracks progress via a 7-item todo checklist. After the pipeline completes, it auto-cleans on PASS or preserves the audit trail on FAIL/PARTIAL.

---

### Stage 1 — Analysis

#### analyzer

Coordinator agent that dispatches plan analysis to two specialized subagents in parallel, then collates their results into a unified **Analysis Manifest** (a table with columns: `#, Plan Task, Status, Finding, Recommendation, Scope`). It can also append optional **Holistic Findings** tagged as `Schedule`, `Gap`, `Guidance`, or `Escalate` for plan-wide execution signals. Read-only — never modifies files.

#### analyzer-task-checker

Analyzes each plan task **individually** against the current codebase — checking entity existence, convention compliance, and scope. Returns a per-task findings table. Read-only.

#### analyzer-plan-checker

Analyzes **cross-task interactions** in the plan — dependency ordering, conflicts, and plan-level gaps. Returns a cross-task findings table and optional holistic findings tagged for executor routing. Read-only.

---

### Stage 2 — Execution

#### executor

Executes the plan by creating one git worktree per task, delegating implementation to `@impl-loop`, and reconciling each dependency wave back onto the pipeline branch via squash merge. Incorporates the analyzer's GAP/RISK/AMBIGUOUS recommendations into delegation prompts and triages optional holistic findings: `Schedule` changes wave planning, `Gap` creates synthetic `[Holistic Gap]` tasks, `Guidance` adds shared delegation context, and `Escalate` pauses for user confirmation. Returns an **Execution Manifest** with per-task status, any synthetic gap rows, files modified/created, plus a plan summary, updated file list, and stage summary.

---

### Stage 3 — Test Coverage

#### test-coverage-filler

Analyzes testable behaviors in all modified files and fills gaps by delegating behavior-driven test creation to `@build`. Runs a **design → quality-review** loop (max 3 iterations) to ensure created tests verify specific behaviors. Returns a **Test Behavior Report** with per-behavior verification status.

#### test-coverage-gate

Extracts testable behaviors from modified/created files — input contracts, decision paths, error handling, boundary conditions, state transitions — and evaluates which behaviors have verified tests. Attempts to run the project's coverage tool or falls back to heuristic behavior analysis. Read-only.

#### test-quality-reviewer

Evaluates test files for **assertion quality and behavior accuracy** — detects trivial assertions, tautological mocking, missing behavioral checks, happy-path-only coverage, and behavior mismatches against specifications. Ensures tests verify the specific behaviors they claim to test. Read-only.

---

### Stage 4 — Code Review

#### code-review-loop

Manages an iterative **review → fix → build/test → re-review** cycle (max 3 iterations). Delegates reviews to `code-review` and fixes to `@build`. Fixes CRITICAL/HIGH/MEDIUM findings, leaves LOW/advisory findings reported, and returns a **Code Review Manifest** with per-finding severity and status.

#### code-review

Review orchestrator that dispatches to specialized reviewers, then collates and deduplicates their findings into New vs Pre-existing tables.

#### review-code-quality

Reviews changed files for structure, maintainability, naming, and scope discipline. Read-only.

#### review-plan-traceability

Checks that changed behavior traces back to the plan and that planned behavior is represented in the changes. Read-only.

#### review-test-coverage

Checks behavior coverage, test quality, and missing or non-meaningful tests. Read-only.

#### review-security

Checks security-sensitive changes for exploitable control failures, injection, secret handling, and related risks. Read-only.

#### review-silent-failure

Checks error handling, fallbacks, retries, and async paths for silent failures or misleading success states. Read-only.

#### review-code-simplifier

Checks changed files for dead code, unnecessary wrappers, and safe simplifications. Read-only.

---

### Stage 5 — Code Refactoring

#### code-refactor-loop

Manages an iterative **refactor-review → fix → build/test → re-review** cycle (max 3 iterations). All refactorings must be **behavior-preserving** — no functional changes allowed. Delegates reviews to `code-refactor-review` and fixes to `@build`. Returns a **Code Refactor Manifest** with per-finding severity and status.

#### code-refactor-review

Reviews code for **refactoring opportunities** — duplication, complexity, naming, structure, and design smells. Returns structured findings with severity levels. Read-only.

---

### Stage 6 — Verification

#### verifier

Verifies that the implementation **complies with the plan** and that **build, lint, and tests all pass**. It consumes the Plan Summary, the persisted **Execution Manifest**, the final file list, CRITICAL/HIGH review findings from Stage 4, and CRITICAL refactor findings from Stage 5. Runs up to 3 verify→fix iterations by delegating fixes to `@build`. Returns a **Verification Report** with overall PASS / PARTIAL / FAIL status.

#### plan-compliance-checker

Cross-references the Plan Summary, Execution Manifest, and final file list against the current codebase to verify every plan requirement was implemented. Returns a structured **Plan Compliance table**. Read-only.

---

### Stage 7 — Reporting

#### pipeline-reporter

Formats the **Final Report** from all six stage summaries and CRITICAL/HIGH findings using the current stage order: Stage 3 is Test Coverage and Stage 4 is Code Review. Produces a structured markdown report with per-stage summaries, a build/lint/test status table, aggregated blocking findings, and any unresolved items. Never writes code or modifies files.
