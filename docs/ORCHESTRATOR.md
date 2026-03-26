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
                                │  Validate plan,  │
                                │  generate run ID,│
                                │  create state dir│
                                └────────┬─────────┘
                                         │
                          ═══════════════════════════════
                          ║  .pipeline/<run-id>/plan.md ║
                          ═══════════════════════════════
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
                                   stage1-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 2 — executor         │
                          │                              │
                          │  Reads: plan.md,             │
                          │         analysis-manifest.md │
                          │                              │
                          │  Delegates to: @build        │
                          │  (wave-based parallel exec)  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: plan-summary.md
                                   file-list.md
                                   stage2-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 3 — code-review-loop │
                          │  (max 3 iterations)          │
                          │                              │
                          │  ┌────────────────────────┐  │
                          │  │    code-review         │──┼──▶ 5 lens subagents:
                          │  │   (orchestrator)       │  │    • newcomer
                          │  └────────────────────────┘  │    • adversary
                          │  ┌────────────────────────┐  │    • operator
                          │  │    @build (fixes)      │  │    • future-maintainer
                          │  └────────────────────────┘  │    • scaler
                          │                              │
                          │  Loop: review → fix →      │
                          │        build/test → repeat  │
                          └─────────────┬────────────────┘
                                        │
                          Outputs: review-critical.md
                                   file-list.md (overwrite)
                                   stage3-summary.md
                                        │
                                        ▼
                          ┌──────────────────────────────┐
                          │  STAGE 4 — test-coverage-   │
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
                          └─────────────┬────────────────┘
                                        │
                          Outputs: stage4-summary.md
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
                               ┌───────────────────┐
                               │  POST-PIPELINE    │
                               │  PASS → cleanup  │
                               │  FAIL → preserve │
                               └───────────────────┘
```

## Pipeline State Files

All inter-stage data flows through files in `.pipeline/<run-id>/`:

| File                   | Written By    | Purpose                                      |
| ---------------------- | ------------- | -------------------------------------------- |
| `plan.md`              | Pre-Flight    | Full user plan (verbatim)                    |
| `analysis-manifest.md` | Stage 1       | Analysis Manifest table                      |
| `stage1-summary.md`    | Stage 1       | Analyzer stage summary                       |
| `plan-summary.md`      | Stage 2       | Condensed plan summary for downstream stages |
| `file-list.md`         | Stage 2, 3, 5 | Updated file list (overwritten each time)    |
| `stage2-summary.md`    | Stage 2       | Executor stage summary                       |
| `review-critical.md`   | Stage 3       | CRITICAL findings from code review           |
| `stage3-summary.md`    | Stage 3       | Code review stage summary                    |
| `stage4-summary.md`    | Stage 4       | Test coverage stage summary                  |
| `refactor-critical.md` | Stage 5       | CRITICAL findings from refactoring           |
| `stage5-summary.md`    | Stage 5       | Refactoring stage summary                    |
| `stage6-summary.md`    | Stage 6       | Verification stage summary                   |

---

## Agent Summaries

### Primary Agent

#### orchestrator

The top-level pipeline controller. Accepts a user-provided markdown plan and drives it through a fixed six-stage pipeline. It **never writes code** — all work is delegated to subagents via the `task` tool. It manages inter-stage data by reading/writing pipeline state files in `.pipeline/<run-id>/` and tracks progress via a 7-item todo checklist. After the pipeline completes, it auto-cleans on PASS or preserves the audit trail on FAIL/PARTIAL.

---

### Stage 1 — Analysis

#### analyzer

Coordinator agent that dispatches plan analysis to two specialized subagents in parallel, then collates their results into a unified **Analysis Manifest** (a table with columns: `#, Plan Task, Status, Finding, Recommendation, Scope`). Read-only — never modifies files.

#### analyzer-task-checker

Analyzes each plan task **individually** against the current codebase — checking entity existence, convention compliance, and scope. Returns a per-task findings table. Read-only.

#### analyzer-plan-checker

Analyzes **cross-task interactions** in the plan — dependency ordering, conflicts, and plan-level gaps. Returns a cross-task findings table and optional holistic findings. Read-only.

---

### Stage 2 — Execution

#### executor

Executes the plan by delegating all implementation work to `@build`. Analyzes task dependencies, groups them into parallelizable **waves**, and executes wave-by-wave. Incorporates the analyzer's GAP/RISK/AMBIGUOUS recommendations into delegation prompts. Returns an **Execution Manifest** with per-task status, files modified/created, and a plan summary.

---

### Stage 3 — Code Review

#### code-review-loop

Manages an iterative **review → fix → build/test → re-review** cycle (max 3 iterations). Delegates reviews to `code-review` and fixes to `@build`. Tracks findings across iterations and exits when no CRITICAL issues remain or the iteration limit is reached. Returns a **Code Review Manifest** with per-finding severity and status.

#### code-review

Review orchestrator that dispatches to five specialized **lens-based** subagents in parallel, then collates, deduplicates, and calibrates their findings into a single unified table.

#### code-review-newcomer

Reviews code through a **newcomer's lens** — readability, clarity, naming, and approachability. Read-only.

#### code-review-adversary

Reviews code through an **adversary's lens** — security vulnerabilities, robustness, and abuse resistance. Read-only.

#### code-review-operator

Reviews code through an **operator's lens** — diagnosability, observability, logging, and failure recovery. Read-only.

#### code-review-future-maintainer

Reviews code through a **future maintainer's lens** — changeability, extensibility, and technical debt. Read-only.

#### code-review-scaler

Reviews code through a **scaler's lens** — performance at load, resource efficiency, and concurrency safety. Read-only.

---

### Stage 4 — Test Coverage

#### test-coverage-filler

Analyzes testable behaviors in all modified files and fills gaps by delegating behavior-driven test creation to `@build`. Runs a **design → quality-review** loop (max 3 iterations) to ensure created tests verify specific behaviors. Returns a **Test Behavior Report** with per-behavior verification status.

#### test-coverage-gate

Extracts testable behaviors from modified/created files — input contracts, decision paths, error handling, boundary conditions, state transitions — and evaluates which behaviors have verified tests. Attempts to run the project's coverage tool or falls back to heuristic behavior analysis. Read-only.

#### test-quality-reviewer

Evaluates test files for **assertion quality and behavior accuracy** — detects trivial assertions, tautological mocking, missing behavioral checks, happy-path-only coverage, and behavior mismatches against specifications. Ensures tests verify the specific behaviors they claim to test. Read-only.

---

### Stage 5 — Code Refactoring

#### code-refactor-loop

Manages an iterative **refactor-review → fix → build/test → re-review** cycle (max 3 iterations). All refactorings must be **behavior-preserving** — no functional changes allowed. Delegates reviews to `code-refactor-review` and fixes to `@build`. Returns a **Code Refactor Manifest** with per-finding severity and status.

#### code-refactor-review

Reviews code for **refactoring opportunities** — duplication, complexity, naming, structure, and design smells. Returns structured findings with severity levels. Read-only.

---

### Stage 6 — Verification

#### verifier

Verifies that the implementation **complies with the plan** and that **build, lint, and tests all pass**. Also verifies CRITICAL findings from Stages 3 and 5 are actually resolved. Runs up to 3 verify→fix iterations by delegating fixes to `@build`. Returns a **Verification Report** with overall PASS / PARTIAL / FAIL status.

#### plan-compliance-checker

Cross-references the Plan Summary and Execution Manifest against the current codebase to verify every plan requirement was implemented. Returns a structured **Plan Compliance table**. Read-only.

---

### Stage 7 — Reporting

#### pipeline-reporter

Formats the **Final Report** from all six stage summaries and CRITICAL findings. Produces a structured markdown report with per-stage summaries, a build/lint/test status table, aggregated CRITICAL findings, and any unresolved items. Never writes code or modifies files.
