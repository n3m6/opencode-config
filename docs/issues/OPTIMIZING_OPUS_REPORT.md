# Legacy MoE Pipeline Compatibility Audit

> **Target model:** Legacy Mixture-of-Experts, roughly early Mixtral-class behavior  
> **Pipeline:** QRSPI (Goals → Questions → Research → Design → Structure → Plan → Implement → Accept → Replan → Verify → Report)  
> **Primary files audited:** `deepwork.md`, `qrspi-plan.md`, `qrspi-implement.md`, `qrspi-accept.md`, `qrspi-code-review.md`  
> **Child agents inspected:** `qrspi-implementer.md`, `qrspi-acceptance-tester.md`, `qrspi-plan-writer.md`, `qrspi-plan-reviewer.md`, `qrspi-backward-loop-detector.md`, `qrspi-integration-checker.md`, `qrspi-review-code-quality.md`

---

## 1. Executive Summary

**Highest-risk compatibility issues:**

1. **qrspi-plan.md pastes every upstream artifact verbatim into both the writer and reviewer dispatches** — goals, research, design, structure, plan, phase-manifest, all task specs, plus loopback context — creating payloads that routinely exceed a legacy MoE's effective working window and trigger lost-in-the-middle degradation.
2. **qrspi-implementer.md collapses five cognitive modes into one agent** — TDD test writing, implementation coding, self-review, specialized review dispatch, review-fix application, and git commit — forcing the legacy MoE to route across planning/coding/testing/reviewing/version-control domains in a single inference chain.
3. **qrspi-plan.md runs a 5–10 round review loop** that re-passes the full artifact set each round, accumulating context monotonically without resetting; a legacy MoE will degrade to verbose repetition or hallucinated fixes by round 4–5.
4. **No prompt-level routing tags** (`[MODE: ...]`, `[DOMAIN: ...]`, `[LANG: ...]`) appear in any stage or leaf-agent prompt, removing the routing cues a legacy MoE depends on to select the right expert mixture.
5. **Retry prompts do not mutate strategy.** When `qrspi-plan.md` re-dispatches the plan writer after a review FAIL, it appends the review feedback but leaves the instructions identical, making a legacy MoE likely to repeat the same plan defect.

**Current pipeline strengths to preserve:**

1. **Disk-backed state and explicit stage boundaries.** Every stage reads from and writes to `.pipeline/`, keeping context grounded in files rather than accumulated conversation history. This is already the single most MoE-friendly design choice.
2. **Deterministic external validation.** Build/test outcomes come from tool execution (`@build`), not model inference. The pipeline does not ask the model to decide whether tests passed.
3. **Backward-loop handling is controller-level.** Loop classification is isolated in `qrspi-backward-loop-detector`, and loop routing decisions are made by deepwork via user confirmation — never autonomously by the coding agent.
4. **Specialized leaf reviewers.** Code review is split into 6 narrow single-checklist agents dispatched in parallel, which is ideal for MoE because each prompt is short and single-domain.

---

## 2. Findings Table

| # | Severity | File | Stage | Legacy-MoE Failure Mode | Trigger In Current Prompt | Why It Fails On Legacy MoE | Likely Symptom | Recommended Fix | Fix Type |
|---|----------|------|-------|------------------------|--------------------------|---------------------------|----------------|----------------|----------|
| 1 | Critical | `qrspi-plan.md` | Plan | Context overload / lost-in-the-middle | Step C pastes `goals.md`, `research/summary.md`, `design.md`, `structure.md` verbatim; Step D re-pastes all of those plus `plan.md`, `phase-manifest.md`, and every `task-NN.md` — every round | Total payload exceeds the effective working window; middle artifacts (design, structure) are ignored or garbled | Plan writer produces tasks that contradict design.md; reviewer misses dependency errors it was just told about | Replace verbatim paste with targeted excerpts: acceptance-criteria list, relevant design-slice summary, affected file-map rows, and task-order table only | Context Reduction |
| 2 | Critical | `qrspi-plan.md` | Plan | Loop instability / verbose drift | Review loop runs 5–10 rounds, re-dispatching plan writer and reviewer with full context each time; no context reset between rounds | Context grows monotonically; by round 5 the model has seen 5 copies of goals.md; expert routing degrades into repetition | Plan writer reproduces the same defect; reviewer flip-flops between PASS and FAIL; output becomes repetitive boilerplate | Cap effective loop at 3 rounds max; reset context each round to only current artifacts + latest review delta; require the plan writer's retry prompt to include a `=== ROOT CAUSE ===` section that names the specific defect before regenerating | Loop Control |
| 3 | Critical | `qrspi-implementer.md` | Child Agent | Mode collapse: plan + code + test + review + commit | Prompt says "Implement this task using TDD: 1. Write failing tests 2. Implement 3. Self-review 4. Run specialized code review 5. Commit" — five cognitive modes in one inference chain | Legacy MoE expert routing destabilizes when switching between test-writing, implementation, self-review, review dispatch, and git commit within one chain | Tests are copy-pasted from the task spec instead of written; implementation drifts from tests; self-review is sycophantic; commit step is forgotten or hallucinated | Split implementer into 3 separate leaf agents: `qrspi-impl-red` (write failing tests), `qrspi-impl-green` (implement to pass), `qrspi-impl-verify` (verify + dispatch review + commit). Each is single-mode | Stage Split |
| 4 | High | All agents | All | Missing routing tags | No prompt begins with `[MODE: ...]`, `[DOMAIN: ...]`, `[LANG: ...]`, or version tags | Legacy MoE relies on early-prompt routing cues to select expert groups; without them, the base mixture is used, degrading specialized performance | Coding agents produce planning prose; planning agents produce code snippets; review agents offer implementation suggestions instead of judgments | Add `[MODE: PLANNING]`, `[MODE: CODING]`, `[MODE: REVIEW]`, `[MODE: DISPATCH]` and `[DOMAIN: ...]` tags to the first line of every agent prompt | Routing Tag |
| 5 | High | `qrspi-implementer.md` | Child Agent | Self-review sycophancy | Phase 3 asks @build to "Self-review and verify" its own output: "Quick review: obvious bugs, missing error handling, inconsistencies" | A legacy MoE grading its own output produces uniformly positive self-review; no negative-bias pressure or checklist | Self-review always returns PASS; real issues surface only at the later review stage, wasting review rounds | Remove the self-review from Phase 3 entirely; the external code-review (Phase 4) already covers this. Phase 3 should only run tests and report coverage | Prompt Rewrite |
| 6 | High | `qrspi-plan.md` | Plan | Retry without strategy mutation | Step D re-dispatches `qrspi-plan-writer` with identical instructions plus `=== REVIEW FEEDBACK ===` appended | The legacy MoE treats the appended feedback as additional context but re-executes the same generation strategy; the feedback may be in the lost-in-the-middle zone | Same plan defect reproduced; reviewer flip-flops or degrades to approval | Require the retry prompt to include `=== ROOT CAUSE OF FAILURE ===` (extracted from review feedback) and `=== MUTATION INSTRUCTION ===` (what to change differently), placed at the start of the instructions block | Retry Mutation |
| 7 | High | `qrspi-accept.md` | Accept | Context overload in acceptance tester dispatch | Step B pastes goals, execution manifest, phase manifest, integration results, design context, and structure context verbatim | The acceptance tester receives the full design.md and structure.md even though its job is to test against acceptance criteria, not architectural artifacts | Acceptance tests target implementation internals instead of user-facing criteria; coverage plan drifts toward testing architecture | Pass only acceptance-criteria excerpt from goals.md and the execution-manifest summary (task status rows + file lists). Design/structure should not be in the acceptance tester prompt | Context Reduction |
| 8 | High | `qrspi-acceptance-tester.md` | Child Agent | Mode collapse: review + write + execute + fix | Inner loop does: (1) draft coverage plan, (2) dispatch reviewers, (3) revise plan, (4) dispatch writer, (5) dispatch executor, (6) dispatch fix attempts — all in one inference chain for up to 3 rounds | The model must orchestrate 4 different subagent dispatches plus plan revision within one inference session; expert routing across these modes is fragile | Coverage plan diverges from reviewer feedback; fix attempts ignore test output; round 3 repeats round 2 verbatim | Move coverage-plan drafting/revision into a separate `qrspi-coverage-planner` agent; keep the acceptance tester as a thin dispatcher of plan → write → run → fix steps | Stage Split |
| 9 | High | `qrspi-implement.md` | Implement | Verbatim artifact paste to implementer | Step C pastes task spec, goals section, route, phase, plan review status, design context, completed dependencies — all verbatim | Single task dispatch can exceed 4K tokens of context preamble before the instructions; design context for full-route tasks is especially large | Implementer ignores the design context or contradicts it; instructions at the end of the prompt are diluted | Replace design context with a focused excerpt: only the relevant vertical-slice description and the interfaces for files in this task's file list | Context Reduction |
| 10 | Medium | `qrspi-plan.md` | Plan | Minimum 5 review rounds is excessive | "If the reviewer returns PASS and review_round is less than 5, increment review_round and run the reviewer again on the unchanged current artifacts" | After a clean PASS on round 1, running 4 more rounds with unchanged input on a legacy MoE risks the later rounds hallucinating issues to justify their existence | Reviewer finds phantom problems on round 4; plan writer degrades the plan to address phantom findings | Reduce minimum to 2 rounds (one write, one confirm). A clean PASS on round 2 should terminate | Loop Control |
| 11 | Medium | `qrspi-implementer.md` | Child Agent | Blank-page generation for tests | Phase 1 instructions say "Write tests for this task based on the Test Expectations section" — the model generates test code from scratch | Legacy MoE hallucinating test imports, assertion APIs, and framework conventions when generating from a blank file | Tests use nonexistent test helpers, wrong assertion syntax, or incorrect import paths | Have the plan stage produce a test skeleton scaffold (file path, imports, test-function signatures, assertion stubs) that the implementer fills in rather than generating from scratch | Prompt Rewrite |
| 12 | Medium | `qrspi-code-review.md` | Review | Mixed prose and machine-parsed structure | Output mixes markdown prose (`### Summary`), structured tables (`### Findings`), and severity labels without strict delimiters | Legacy MoE may emit findings in prose instead of the required table format, or mix severity labels with descriptions | Parser fails to extract findings; review gate defaults to PASS when it should FAIL | Add explicit delimiters: `---BEGIN FINDINGS TABLE---` / `---END FINDINGS TABLE---`; require severity to be the exact enum value in column 2 with no surrounding text | Schema Hardening |
| 13 | Medium | `qrspi-backward-loop-detector.md` | Child Agent | Qualitative review without forcing binary decisions early | Process says "Group persistent failures by likely root cause" then "classify each root cause" — two qualitative steps before any binary output | Legacy MoE produces meandering root-cause analysis that never reaches a clear classification; loop target becomes ambiguous | Backward loop request contains contradictory recommendations; deepwork cannot parse the target | Restructure as checklist-first: for each failure, answer YES/NO to "requires new file boundaries?", "requires interface change?", "requires architecture change?", "requires scope change?" — then derive the classification mechanically from the answers | Prompt Rewrite |
| 14 | Medium | `qrspi-plan-reviewer.md` | Child Agent | Review without negative-bias checklist | The reviewer uses a qualitative standard ("Every acceptance criterion…is materially addressed") without forced-negative prompting | Legacy MoE defaults to agreement; without explicit "find at least one concern" or "list 3 weaknesses" pressure, review is sycophantic | Reviewer returns PASS with boilerplate "looks good" notes on round 1, masking real issues | Add a forced-negative section: "Before returning PASS, identify the 3 weakest areas. If none are material, explain why each is acceptable." | Prompt Rewrite |
| 15 | Medium | `qrspi-implement.md` | Implement | Integration checker receives full plan.md verbatim | Step E pastes `plan.md`, `phase-manifest.md`, `baseline-results.md`, execution manifest, all completed phase summaries, review status summary, and design context | Integration checker only needs cross-task interface data; full plan context dilutes focus | Integration checker runs irrelevant smoke tests or misses interface conflicts buried in the middle of the payload | Pass only the current-phase task summaries (from execution manifest), the interface/contract excerpts from design.md, and the delta from baseline-results.md | Context Reduction |
| 16 | Medium | `deepwork.md` | Deepwork | Controller prompt is 739 lines | The full deepwork prompt is ~39KB including resume algorithm, backward-loop protocol, state.md contract, file conventions | While deepwork is a dispatcher, the prompt itself exceeds the effective window; the Resume Mode algorithm (lines 124–166) and Backward Loop Protocol (lines 629–714) are especially dense | Deepwork misroutes a backward loop, skips a phase directory step, or produces malformed state.md | Keep the controller prompt but move the Resume Mode algorithm and Backward Loop Protocol into separate reference files that deepwork reads with `cat` only when it needs them | Context Reduction |
| 17 | Low | `qrspi-plan.md` | Plan | Plan writer and task-spec-writer both receive goals verbatim | Plan writer passes goals verbatim to each `qrspi-task-spec-writer` dispatch, which also receives the plan overview containing goals coverage notes | Double-pass of goals in the same chain wastes context tokens and risks conflicting interpretations | Task spec writer uses a paraphrase from the plan overview that diverges from the original goals text | Pass only the specific acceptance criteria relevant to this task, not the full goals.md | Context Reduction |
| 18 | Low | `qrspi-accept.md` | Accept | Route consistency check is model-side | Lines 60–67: "If config.md says the route is quick-fix and either design.md or structure.md exists, return FAIL immediately" | Asking the model to detect file-existence inconsistencies is unreliable on legacy MoE | Inconsistency is not detected; acceptance tester receives design context for a quick-fix run | Move this check to deepwork (controller level) as a pre-dispatch validation using `ls` | Tool Gate |
| 19 | Low | `qrspi-implementer.md` | Child Agent | No error-output filtering | Phase 2 retry includes "the failing test output" without specifying truncation or filtering | Full test output may include noisy stack traces, framework boilerplate, or unrelated stderr | Retry prompt is polluted with irrelevant output; model fixates on an unrelated warning | Specify: "include only the first failing test name, assertion line, expected vs actual values, and the first 10 lines of the stack trace" | Context Reduction |
| 20 | Low | `qrspi-code-review.md` | Review | Reviewer selection is model-side heuristic | Step B: "Dispatch qrspi-review-security when the task spec, design context, file paths, or file contents include signals such as: auth, permission, secret…" | Legacy MoE may miss or over-match keyword heuristics, dispatching the wrong reviewer set | Security reviewer is skipped for a file handling auth tokens; or dispatched for a file that merely mentions "user" in a comment | Move reviewer selection to a deterministic keyword scan in the orchestrator (deepwork or implement stage) using `grep` on the changed file list | Tool Gate |
| 21 | Low | `qrspi-acceptance-tester.md` | Child Agent | Fix attempts lack root-cause requirement | Step 5: "If the failures can be fixed with a small local code change, make the smallest safe fix" — no requirement to explain root cause before fixing | Legacy MoE applies a syntactic patch that silences the test without addressing the underlying defect | Fix attempt passes the test by weakening the assertion or adding a special case that breaks later | Add: "Before applying any fix, first write one sentence identifying the root cause. If the root cause is not a local implementation bug, report UNCHANGED." | Retry Mutation |
| 22 | Low | All agents | All | No observability instrumentation | No agent prompt includes instructions to emit structured timing, token-usage, or outcome metadata | Cannot measure per-stage degradation, context-size correlation with failure rate, or retry effectiveness | No data to drive iterative pipeline improvement for legacy MoE | Add a required `### Telemetry` section to every stage return: `round_count`, `context_tokens_approx`, `outcome`, `duration_seconds` | Metrics |

---

## 3. Stage-by-Stage Risk Review

### 3.1 agents/deepwork.md

**What already helps legacy MoE:**
- Thin dispatcher design: deepwork never writes code or makes implementation decisions.
- Disk-backed state with `state.md` YAML checkpoint after every transition.
- Structured return contract (`### Status`, `### Files Written`, `### Summary`) is simple and parseable.
- Backward-loop decisions go through user confirmation, preventing autonomous looping.
- Permission model is tightly scoped: only `cat`, `ls`, `mkdir`, `ln`, `mv`, `rm` on pipeline files.

**What still creates risk:**
- The prompt is 739 lines / ~39KB. The Resume Mode algorithm (lines 124–166) and Backward Loop Protocol (lines 629–714) are dense procedural instructions that will be in the lost-in-the-middle zone for a legacy MoE.
- No `[MODE: DISPATCH]` routing tag.
- The backward-loop option menu (7 options A–G) is complex enough for the model to misparse user choices.

**Verdict:** Harden with routing tags and context reduction (externalize Resume and Backward Loop Protocol into `cat`-able reference files). No stage split needed.

---

### 3.2 agents/qrspi-plan.md

**What already helps legacy MoE:**
- Clear step labeling (A → B → C → D → E → F).
- Separate plan writer and plan reviewer agents rather than self-review.
- Red Flags and Common Rationalizations tables provide checklist-style grounding.
- Baseline checker is a separate deterministic step.

**What still creates risk:**
- **Critical context overload**: Steps C and D paste every upstream artifact verbatim — goals, research, design, structure, plan, phase-manifest, all task specs, plus loopback context. This is the single largest context payload in the pipeline.
- **Loop instability**: 5–10 round review loop with monotonically growing context. The minimum of 5 rounds is already beyond what a legacy MoE can sustain without degradation.
- **Retry without mutation**: Re-dispatch to plan writer appends review feedback but doesn't require root-cause identification or strategy change.

**Verdict:** Needs both **context reduction** and **loop control** hardening. The review loop ceiling should drop to 3 rounds max. Context passed to writer and reviewer should be reduced to targeted excerpts. These are prompt-level changes, not stage splits.

---

### 3.3 agents/qrspi-implement.md

**What already helps legacy MoE:**
- Wave-based parallelism: tasks are grouped by dependency and dispatched per-wave.
- Integration checker is a separate agent call after all waves complete.
- Phase-scoped execution manifest provides grounded per-task status tracking.
- Validation against phase-manifest before execution catches missing task files.

**What still creates risk:**
- **Delegated implementer is mode-collapsed**: `qrspi-implementer.md` (dispatched from here) runs TDD phases, self-review, specialized code review, review-fix, and commit in one inference chain.
- **Full artifact verbatim paste**: each implementer dispatch pastes the task spec, goals excerpt, plan review status, design context, and completed dependencies. For full-route tasks with large design.md, this creates substantial context overhead.
- **Integration checker receives full plan.md** verbatim (Step E) — unnecessary context for a cross-task compatibility check.

**Verdict:** The implement orchestrator itself is acceptably structured. The **child agent `qrspi-implementer.md` needs a stage split** into red/green/verify phases. Context passed to both implementer and integration checker needs **reduction**.

---

### 3.4 agents/qrspi-accept.md

**What already helps legacy MoE:**
- Clean two-step structure: dispatch acceptance tester, then conditionally dispatch backward-loop detector.
- Backward-loop classification is isolated in a separate agent — the acceptance tester only reports persistent failures.
- Route consistency check catches quick-fix/design artifact mismatches early.
- Phase-scoped file writing prevents cross-phase contamination.

**What still creates risk:**
- Full design/structure context is passed to the acceptance tester, which only needs acceptance criteria and implementation status.
- The acceptance tester (`qrspi-acceptance-tester.md`) itself is mode-collapsed: it drafts coverage plans, dispatches reviewers, revises plans, dispatches writers, dispatches executors, and dispatches fix attempts — all within one inference chain.
- Prior-phase summaries are read but may be very large for multi-phase runs.

**Verdict:** The accept orchestrator is reasonably thin. Harden with **context reduction** (remove design/structure from acceptance tester dispatch). The child agent `qrspi-acceptance-tester.md` should have its coverage-plan drafting/revision split out if the mode-collapse proves problematic empirically. **Start with context reduction before splitting.**

---

### 3.5 agents/qrspi-code-review.md

**What already helps legacy MoE:**
- 6 narrow specialized reviewers dispatched in parallel — each has a short single-checklist prompt.
- Reviewer selection is signal-based (keyword matching on file paths/contents).
- Clear severity hierarchy with binary blocking rule (only CRITICAL/HIGH block).
- Read-only permissions — cannot accidentally modify code.
- Code simplifier is explicitly marked non-blocking.

**What still creates risk:**
- Reviewer selection is a model-side heuristic. The keyword matching ("auth, permission, secret, token…") is error-prone on a legacy MoE.
- Output schema mixes prose sections (`### Summary`) with a structured table (`### Findings`). A legacy MoE may emit findings in prose or corrupt the table format.
- Line-numbered file contents are passed verbatim. For tasks touching many files, this can be substantial context.

**Verdict:** Mostly sound. Harden with **schema hardening** (add explicit delimiters around the findings table) and **tool gate** (move reviewer selection to deterministic keyword `grep`). No split needed.

---

## 4. Highest-Leverage Changes

### Change 1: Add Routing Tags to Every Agent Prompt

**Why it matters for legacy MoE:** Expert routing in a MoE model is influenced by early-prompt tokens. Without explicit mode/domain tags, the model uses its base mixture, which may route a planning prompt through coding experts or vice versa. This is the lowest-cost, broadest-impact change.

**Smallest viable change:** Add a `[MODE: ...]` and `[DOMAIN: ...]` tag as the first line of every agent prompt, before any other content. Examples:
- deepwork.md: `[MODE: DISPATCH] [DOMAIN: PIPELINE-ORCHESTRATION]`
- qrspi-plan.md: `[MODE: PLANNING] [DOMAIN: TASK-DECOMPOSITION]`
- qrspi-implementer.md: `[MODE: CODING] [DOMAIN: TDD-IMPLEMENTATION]`
- qrspi-code-review.md: `[MODE: REVIEW] [DOMAIN: CODE-QUALITY]`
- qrspi-accept.md: `[MODE: TESTING] [DOMAIN: ACCEPTANCE-VERIFICATION]`

**Expected downside:** Minimal. These tags are ignored by frontier models and helpful for legacy MoE. The only cost is one line per prompt file.

---

### Change 2: Reduce Plan Stage Context by 60–70%

**Why it matters for legacy MoE:** The plan stage (Steps C and D) is the single largest context payload. On a legacy MoE, the middle of the payload—typically design.md and structure.md—falls into the lost-in-the-middle zone, causing the plan to contradict the design or miss file mappings.

**Smallest viable change:** Replace verbatim pastes with targeted excerpts:
- **Goals**: paste only the Acceptance Criteria section, not the full goals.md.
- **Research**: paste only the Summary section and relevant findings, not the full Q&A.
- **Design**: paste only the vertical-slice descriptions and phase boundaries relevant to the current task set.
- **Structure**: paste only the file-map rows (path, CREATE/MODIFY, interface) relevant to the tasks being planned.
- **Review rounds**: pass only the current plan.md and task-specs, plus the delta from the latest review. Do not re-paste goals/research/design/structure each round.

**Expected downside:** If the excerpting is too aggressive, the plan writer may miss cross-slice dependencies. Mitigation: keep the full file-map table but omit the detailed interface descriptions unless a task references that interface.

---

### Change 3: Cap Plan Review Loop at 3 Rounds; Require Root-Cause on Retry

**Why it matters for legacy MoE:** The current 5–10 round loop creates monotonically growing context and increases the probability of verbose drift. By round 5, a legacy MoE has seen 5 copies of goals.md and is likely to reproduce the same defect or hallucinate new ones.

**Smallest viable change:**
- Set max rounds to 3 (was 10), min rounds to 1 (was 5).
- On review FAIL, require the retry prompt to include:
  ```
  === ROOT CAUSE OF FAILURE ===
  [one sentence: what specific defect caused the FAIL]

  === MUTATION INSTRUCTION ===
  [one sentence: what to change differently this time]
  ```
  These fields must be placed **before** the main instructions block to ensure they are in the model's active window.

**Expected downside:** Fewer review rounds may let marginal defects through. Mitigation: the acceptance stage and backward-loop detector catch plan defects downstream. The current pipeline already has `unclean-cap` tracking for exactly this scenario.

---

### Change 4: Split `qrspi-implementer.md` Into Three Single-Mode Agents

**Why it matters for legacy MoE:** The implementer currently runs test writing, implementation, self-review, code review dispatch, review-fix, and commit in one inference chain. This is the highest mode-collapse risk in the pipeline. A legacy MoE's expert routing cannot reliably switch between these cognitive modes.

**Smallest viable change:** Split into:
1. `qrspi-impl-red` — Receives task spec + test expectations. Dispatches `@build` to write failing tests. Returns test files and failing output. Single mode: [MODE: TESTING].
2. `qrspi-impl-green` — Receives task spec + failing tests. Dispatches `@build` to implement. Handles red-green retry loop (max 3). Returns implementation files + passing output. Single mode: [MODE: CODING].
3. `qrspi-impl-verify` — Receives implementation files list. Runs tests, dispatches `qrspi-code-review`, handles review-fix loop (max 2), commits. Single mode: [MODE: VERIFICATION].

The existing `qrspi-implement.md` orchestrator dispatches these three in sequence per task.

**Expected downside:** More subagent calls per task increases latency and cost. Each split agent still needs enough context to understand the task, but each prompt can be shorter and single-domain. The orchestrator (`qrspi-implement.md`) takes on slightly more sequencing work.

---

### Change 5: Add Structured Telemetry to Every Stage Return

**Why it matters for legacy MoE:** Without per-stage metrics, there is no way to correlate context size, round count, or retry depth with failure rate. This data is essential for iterating on prompt-level changes.

**Smallest viable change:** Add a required `### Telemetry` section to every stage return contract:
```
### Telemetry
- rounds: [N]
- context_tokens_approx: [N]
- outcome: [PASS|FAIL|LOOP]
- child_agents_dispatched: [N]
```

Deepwork logs these to `.pipeline/<run-id>/telemetry.jsonl` after each stage transition.

**Expected downside:** Slight increase in return payload size. The model may hallucinate the `context_tokens_approx` value — this should be treated as an estimate, not a measurement. For precise measurement, instrument the orchestration framework itself.

---

## 5. Suggested Prompt Rewrites

### Rewrite 1
**File:** `agents/qrspi-plan.md`  
**Problematic pattern:** Step C pastes `[paste contents of goals.md verbatim]`, `[paste contents of research/summary.md verbatim]`, `[paste contents of design.md verbatim]`, `[paste contents of structure.md verbatim]` — four full artifacts.

**Safer replacement:**
```text
=== ACCEPTANCE CRITERIA ===
[paste ONLY the Acceptance Criteria section from goals.md — not the full document]

=== RESEARCH KEY FINDINGS ===
[paste ONLY the Key Findings subsection from research/summary.md — typically 10-20 lines]

=== DESIGN SLICES ===
[paste ONLY the Vertical Slices and Phase Boundaries subsections from design.md]

=== FILE MAP ===
[paste ONLY the file-map table from structure.md — path, action, and interface-summary columns]

=== NEXT REMAINING PHASE ===
[paste the provided next remaining phase number, or `1`]

=== INSTRUCTIONS ===
[MODE: PLANNING] [DOMAIN: TASK-DECOMPOSITION]
Write an ordered implementation plan overview and delegate every task spec.
...
```

**Why this is safer for legacy MoE:** Reduces the total input from ~4 full documents (often 8K+ tokens combined) to ~2K tokens of targeted excerpts. The acceptance criteria, key findings, slice descriptions, and file-map table contain the information the plan writer actually needs. The routing tag `[MODE: PLANNING]` activates planning-specialized experts. The removed bulk (research Q&A details, design rationale prose, structure interface details) was in the lost-in-the-middle zone anyway.

---

### Rewrite 2
**File:** `agents/qrspi-plan.md`  
**Problematic pattern:** Step D retry re-dispatches plan writer with identical instructions plus `=== REVIEW FEEDBACK === [paste reviewer output verbatim]` appended at the end.

**Safer replacement:**
```text
=== ROOT CAUSE OF FAILURE ===
[Extract from review feedback: the single most critical defect identified by the reviewer.
Write one sentence. Example: "Task 03 has a forward dependency on Task 04."]

=== MUTATION INSTRUCTION ===
[Write one sentence describing what the plan writer must do differently.
Example: "Reorder Task 03 and Task 04 so 03 depends on 02 only."]

=== REVIEW FEEDBACK ===
[paste the reviewer's Fix Guidance section ONLY — not the full review output]

=== ACCEPTANCE CRITERIA ===
[paste acceptance criteria excerpt — same as initial dispatch]

=== FILE MAP ===
[paste file-map table — same as initial dispatch]

=== INSTRUCTIONS ===
[MODE: PLANNING] [DOMAIN: TASK-DECOMPOSITION]
Revise the plan to address the ROOT CAUSE OF FAILURE above.
Apply the MUTATION INSTRUCTION.
Do not regenerate unchanged tasks — only modify the affected tasks and plan sections.
...
```

**Why this is safer for legacy MoE:** The root cause and mutation instruction are placed at the top of the prompt, inside the model's active window. The review feedback is reduced to only the Fix Guidance section (typically 3–5 lines) instead of the full reviewer output (which includes the findings table, all area statuses, and the summary). The explicit mutation instruction prevents the model from re-executing the same generation strategy.

---

### Rewrite 3
**File:** `agents/qrspi-implementer.md`  
**Problematic pattern:** Phase 3 says "Self-review and verify the implementation: 1. Run all tests 2. Check that all Test Expectations are covered 3. Quick review: obvious bugs, missing error handling, inconsistencies"

**Safer replacement:**
```text
=== TASK ===
[paste task spec verbatim]

=== INSTRUCTIONS ===
[MODE: VERIFICATION] [DOMAIN: TEST-EXECUTION]
Verify the implementation by running tests only. Do NOT review code quality.
1. Run all tests for this task's files (not the full suite)
2. Report pass/fail counts and any failing test names with assertion details
3. For each Test Expectation from the task spec, confirm whether a passing test covers it

Return:
### Test Results — pass/fail output (first 20 lines of each failure only)
### Expectation Coverage — table: | # | Expectation | Covered By Test | Status |
### Overall — PASS or FAIL
```

**Why this is safer for legacy MoE:** Removes the self-review step entirely. Self-review on a legacy MoE produces uniformly positive results because the model is grading its own work without negative-bias pressure. The specialized code review (Phase 4, dispatched to 6 independent reviewers) already provides rigorous quality checking. Keeping Phase 3 focused on test execution only means the model stays in `[MODE: VERIFICATION]` without switching to review mode.

---

### Rewrite 4
**File:** `agents/qrspi-backward-loop-detector.md`  
**Problematic pattern:** Process says "1. Group persistent failures by likely root cause. 2. Use the severity table below to classify each root cause. 3. Choose the earliest affected artifact" — three qualitative reasoning steps.

**Safer replacement:**
```text
[MODE: REVIEW] [DOMAIN: FAILURE-CLASSIFICATION]

### Process

For EACH persistent failure, answer these binary questions in order:

1. Can this failure be fixed by changing only implementation code within the current task scope? → YES = NO_LOOP candidate. → NO = continue.
2. Does fixing this failure require adding, removing, or renaming files? → YES = LOOP_STRUCTURE candidate. → NO = continue.
3. Does fixing this failure require changing a component interface, API contract, or data schema? → YES = LOOP_STRUCTURE candidate. → NO = continue.
4. Does fixing this failure require a different technology choice, architecture pattern, or slice boundary? → YES = LOOP_DESIGN candidate. → NO = continue.
5. Does fixing this failure require changing what "success" means (acceptance criteria or scope)? → YES = LOOP_GOALS candidate. → NO = continue.
6. Does the current phase still satisfy its contract without this fix, AND is the fix already assigned to a future phase? → YES = DEFER_REPLAN. → NO = use the earliest loop target from questions 2-5.

Fill in this table:

| # | Criterion | Failure | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Classification |

THEN choose the overall recommendation as the earliest loop target across all failures.
```

**Why this is safer for legacy MoE:** Replaces open-ended root-cause analysis with a forced binary decision tree. The model answers YES/NO for each question, which is a much more reliable output mode for a legacy MoE than free-form reasoning. The table format ensures every failure is classified before the overall recommendation is derived, preventing the model from skipping failures or producing contradictory classifications.

---

### Rewrite 5
**File:** `agents/qrspi-code-review.md`  
**Problematic pattern:** Output format mixes `### Status`, `### Reviewers Run`, `### Findings` (table), `### Critical/High Count`, and `### Summary` without strict delimiters.

**Safer replacement:**
```text
[MODE: REVIEW] [DOMAIN: CODE-QUALITY-GATE]

### Output Format

Return EXACTLY this structure. Use the delimiters shown. Do not add prose between sections.

### Status — PASS or FAIL

### Reviewers Run
[one line per reviewer: reviewer-name — PASS or FAIL]

---BEGIN FINDINGS TABLE---
| # | Reviewer | Severity | File | Lines | Category | Issue | Recommendation |
|---|----------|----------|------|-------|----------|-------|----------------|
[rows here, or NONE if no findings]
---END FINDINGS TABLE---

### Critical/High Count — [integer]

### Summary — [one sentence only]
```

**Why this is safer for legacy MoE:** The `---BEGIN FINDINGS TABLE---` / `---END FINDINGS TABLE---` delimiters provide unambiguous parsing anchors. The `NONE` sentinel value (instead of "None." or free-form prose) is a single token that cannot be confused with a partial finding. The explicit instruction "Do not add prose between sections" prevents the model from injecting explanatory text that breaks the schema.

---

## 6. Validation And Experiments

### Metrics to Track

1. **Per-stage context token count** — Measure the total tokens in each subagent dispatch prompt. Correlate with stage failure rate. Target: no dispatch exceeds 6K tokens for a legacy MoE.
2. **Review-loop round count distribution** — Track how many rounds each plan review and acceptance review loop actually runs. If the modal value is the cap (currently 10), the loop is not converging.
3. **Same-defect retry rate** — When a plan review FAIL triggers a plan-writer re-dispatch, diff the new plan against the previous. If the defective section is unchanged, the retry failed to mutate.
4. **Structured-output parse success rate** — For every stage return and every reviewer return, attempt to parse the expected sections (`### Status`, `### Findings`, tables). Track the fraction that parse correctly vs those requiring fallback heuristics.

### A/B Tests to Run

1. **Routing tags vs no routing tags** — Run 20 identical pipeline tasks with and without `[MODE: ...]` / `[DOMAIN: ...]` tags on all agent prompts. Measure per-stage failure rate, review loop round count, and structured-output parse success rate. This is the lowest-cost experiment with the broadest expected signal.
2. **Verbatim artifact paste vs targeted excerpts in qrspi-plan.md** — For the plan stage only, compare full-artifact dispatch (current) against acceptance-criteria + file-map-only dispatch (proposed). Measure plan-review PASS rate on round 1 and the number of task specs that contradict design.md.
3. **3-round plan review cap vs 5-round minimum** — Compare plan quality (measured by downstream acceptance-test pass rate) between a 3-round cap with root-cause mutation and the current 5-round minimum. If 3 rounds + mutation instruction matches or exceeds 5 rounds' downstream quality, the shorter loop is strictly better for legacy MoE.

### Failure Signatures That Should Trigger Fallback

1. **Plan-writer regenerates identical output after review FAIL.** If a diff between the previous and current plan.md shows <5% character change after a FAIL-triggered retry, the pipeline should halt and surface the unchanged defect to the user rather than continuing the loop.
2. **Structured-output parse failure on 2+ consecutive stage returns.** If deepwork cannot parse `### Status` from two consecutive stage returns, the legacy MoE's structured-output reliability has degraded below usable levels. Fallback: simplify the return contract to a single line `STATUS: PASS` or `STATUS: FAIL` followed by free-form content.
3. **Acceptance tester reports the same persistent failure across 2 consecutive rounds with identical evidence.** This indicates the fix-attempt loop is not mutating. Fallback: skip remaining fix attempts, write the persistent failure, and immediately dispatch the backward-loop detector.

---

## 7. Final Verdict

**Can this pipeline be made legacy-MoE friendly with prompt hardening alone?**

Mostly yes. The pipeline's core architecture — disk-backed state, explicit stage boundaries, deterministic external validation, controller-level loop handling — is already well-suited for a legacy MoE. The majority of the 22 findings (16 of 22) can be addressed with prompt-level changes: routing tags, context reduction, schema hardening, retry mutation, and loop control. These changes do not require structural redesign. The pipeline's separation between orchestrator agents and leaf agents provides natural prompt boundaries that are easier to harden individually than a monolithic system.

**Which stages most likely need structural splitting?**

Two child agents are mode-collapsed beyond what prompt hardening can fix: (1) `qrspi-implementer.md`, which runs TDD test writing, implementation, self-review, specialized review dispatch, review-fix application, and git commit in one inference chain — this should be split into 3 single-mode agents (red, green, verify+commit). (2) `qrspi-acceptance-tester.md`, which drafts coverage plans, dispatches reviewers, revises plans, dispatches writers, dispatches executors, and dispatches fix attempts — this should have its coverage-plan drafting/revision extracted into a separate agent. These two splits are the only structural changes recommended; the rest of the pipeline can be hardened in place.

**What should be changed first before any broader redesign?**

Start with three changes in this priority order: (1) Add `[MODE: ...]` and `[DOMAIN: ...]` routing tags to every agent prompt — this is a one-line change per file with zero downside and the broadest expected impact on legacy MoE routing. (2) Reduce the plan stage context by replacing verbatim artifact pastes with targeted excerpts and cap the review loop at 3 rounds with root-cause mutation — this addresses the two highest-severity findings (context overload and loop instability) in the single most critical pipeline stage. (3) Add `---BEGIN/END---` delimiters to all structured-output sections — this reduces parse failures without changing any agent's responsibilities. Only after measuring the impact of these three changes should the implementer and acceptance-tester stage splits be attempted.
