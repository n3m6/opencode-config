## 1. Executive Summary
- **Risk:** The `qrspi-implement` prompt suffers from mode collapse, mixing analytical TDD, code generation, and critical self-review in a single prompt instruction block.
- **Risk:** The `qrspi-accept` orchestrator delegates a complex 6-step nested loop to a single `qrspi-acceptance-tester` subagent, far exceeding a legacy MoE's capacity for stable orchestration.
- **Risk:** Massive concatenations of verbatim upstream texts (e.g., pasting all of `plan.md`, `design.md`, and `goals.md`) cause severe context overload and "lost-in-the-middle" issues for instruction following.
- **Risk:** Retry loops inside `qrspi-plan` merely append feedback context without mutating the primary directive, causing models to endlessly loop and repeat identical failures.
- **Strength:** Generating deterministic, disk-backed phase histories and explicitly boundary-gated pipeline state files successfully avoids open-ended memory bloat.
- **Strength:** Specialized subagents isolated by domain (code quality, security, goal traceability) safely constrain the required expertise window for individual review passes.

## 2. Findings Table

| # | Severity | File | Stage | Legacy-MoE Failure Mode | Trigger In Current Prompt | Why It Fails On Legacy MoE | Likely Symptom | Recommended Fix | Fix Type |
| - | -------- | ---- | ----- | ----------------------- | ------------------------- | -------------------------- | -------------- | --------------- | -------- |
| 1 | Critical | `agents/qrspi-implement.md` | Implement | Planning/coding/testing mode collapse | "Use TDD: 1. Write failing tests... 2. Implement minimal code... 3. Self-review" | Legacy MoE struggles to shift from analytical test planning to creative generation to self-critique in a single run. | The model writes tests but no code, or sycophantically claims its broken code passes review. | Extract the test-writing phase from the implementation/coding phase. | Stage Split |
| 2 | High | `agents/qrspi-accept.md` | Accept | Controller overreach vs thin dispatch | "Each round must: 1. Draft... 2. Dispatch... 3. Revise... 4. Dispatch... 5. Dispatch..." | The loop involves deeply nested sequences of dispatching other agents, requiring stable structured loops that legacy models lose track of. | The model hallucinates the results of the sub-dispatch or skips steps entirely. | Move the 6-step inner loop logic into the `qrspi-accept` controller natively. | Stage Split |
| 3 | High | `agents/qrspi-plan.md` | Plan | Context overload and lost-in-the-middle risk | "[paste contents of goals.md verbatim]... [paste contents of design.md verbatim]" | Appending immense upstream blocks verbatim pushes the model's constrained context boundaries, causing it to drop system instructions. | The model ignores format requests or writes vague test expectations in tasks. | Extract specific targets from these artifacts instead of raw verbatim concatenation. | Context Reduction |
| 4 | High | `agents/qrspi-code-review.md` | Review | Context overload and lost-in-the-middle risk | "[paste the line-numbered contents of each changed file verbatim]" | Dumping complete source files introduces massive irrelevant context bloat that dilutes the focus required to spot isolated bugs. | Hallucinated line numbers, reviewing the wrong lines, or missing critical security flaws entirely. | Provide unified diffs instead of unmodified full-file contents. | Context Reduction |
| 5 | Medium | `agents/qrspi-plan.md` | Plan | Loop instability / verbose drift | "re-dispatch qrspi-plan-writer with the original inputs plus: === REVIEW FEEDBACK ===" | Re-feeding identical core inputs while merely appending feedback encourages the model to lock into the exact same generative trajectory. | The 10-round review loop caps out continually with identical plan formats. | Place negative constraints based on the failure at the very top of the system prompt. | Retry Mutation |
| 6 | Medium | `agents/deepwork.md` | Deepwork | Weak structured-output contracts | "### Status — PASS \| FAIL\n### Files Written — list of files" | Free-form markdown headers are frequently polluted with conversational conversational filler, prepended paragraphs, or variant spacing. | Orchestrator controller fails to traverse the pipeline because regex fails to parse statuses. | Replace markdown headers with strict XML block schemas. | Schema Hardening |

## 3. Stage-by-Stage Risk Review

**agents/deepwork.md**
- **Already helps:** The explicit management of the backward-loop protocol prevents unconstrained fallback behavior, and phase-manifested disk saves ensure stability.
- **Creates risk:** Parsing outputs exclusively through markdown headers (`### Status - PASS`) is highly brittle for legacy models that trend conversational.
- **Verdict:** Should be hardened. Enforce strict XML tags for status outputs without fully redesigning the router structure.

**agents/qrspi-plan.md**
- **Already helps:** The rigid task table format and absence of human blocking here force a deterministic, predictable review structure.
- **Creates risk:** Reading upstream states entirely verbatim without summary filters ensures context blackouts; appending feedback sequentially creates loop paralysis.
- **Verdict:** Should be hardened. Context volume must be dramatically reduced, and loop prompts must mutate rather than just loop-and-append. 

**agents/qrspi-implement.md**
- **Already helps:** Using execution manifests and wave-grouping cleanly isolates task dependencies limit logic.
- **Creates risk:** Delegating TDD synthesis, actual coding, and self-review down to a single `qrspi-implementer` call invites severe mode collapse.
- **Verdict:** Should be split. Sub-tasks like test writing, implementing, and post-review should be separate explicit calls.

**agents/qrspi-accept.md**
- **Already helps:** Externalizing fallback definitions via `qrspi-backward-loop-detector` keeps root-cause tracing out of the test loop itself.
- **Creates risk:** Forcing `qrspi-acceptance-tester` to execute a robust 6-part nested plan orchestration loop assumes a level of autonomous fidelity Legacy MoE simply lacks.
- **Verdict:** Needs structural splitting. The loop execution must be handled at the deterministic controller script layer, not delegated to a text-inference prompt.

**agents/qrspi-code-review.md**
- **Already helps:** Specialized reviewers effectively divide tasks into non-overlapping analytical functions avoiding domain cross-wiring.
- **Creates risk:** Parsing entirely intact line-numbered files instead of patch/diff variants expands the model working window arbitrarily out of scale to the code modifications.
- **Verdict:** Should be hardened by strictly piping in differential outputs rather than full file state.

## 4. Highest-Leverage Changes

**1. Convert Output Headers to Strict XML Tag Schemas**
- **Why it matters:** Legacy MoEs possess drastically lower format adherence and higher conversational bias. Markdown headers break quickly; explicit XML tagging forces structural alignment.
- **Smallest viable change:** Replace `### Status` and `### Files Written` requests globally with `<status>` and `<files_written>` definitions.
- **Expected downside:** Marginal token overhead increases; deepwork parser scripts have to be refactored specifically to parse blocks.

**2. Pass Diffs Instead of Full Line-Numbered Files in Code Review**
- **Why it matters:** Legacy MoE working context windows are strict. Sifting for bugs across irrelevant lines triggers hallucinations and dilutes explicit system instructions.
- **Smallest viable change:** Refactor `qrspi-code-review.md` Step A to collect `git diff -U3` snippets instead of full `cat -n` outputs.
- **Expected downside:** Reviewers lose awareness of unmodified surrounding architectures that might give context to changing types or functions.

**3. Isolate TDD Generation from Functional Implementation**
- **Why it matters:** Mode collapse triggers reliably when analytical reasoning (deducing a test shape) flows directly into task execution (satisfying the test constraints) in the same inference window.
- **Smallest viable change:** Stop asking `qrspi-implementer` to write test code and implement feature code at the same time. Introduce a `qrspi-test-writer` beforehand.
- **Expected downside:** Noticeable slow down in stage turnaround time as wait-steps effectively double for Phase 7 implementation.

**4. Mutate Retry Iterations with Prepend Constraints**
- **Why it matters:** In static failure loops, the original task prompt dominates the appended feedback text, causing looping models to generate the identical failed answer repeatedly.
- **Smallest viable change:** Update the review logic in `qrspi-plan.md` to shift "REVIEW FEEDBACK" to the absolute top of the system prompt marked as `=== CRITICAL RETRY DIVERGENCE ===`.
- **Expected downside:** Can artificially restrict and break correctly passing details in the plan when the model swings wildly away from its previous generation.

**5. Flatten the Acceptance Tester Subagent Loop**
- **Why it matters:** Legacy MoEs are incapable of adhering closely to deep 6-stage nested reasoning tracks autonomously over repetitive loops.
- **Smallest viable change:** Move the exact 6 step directions (Draft, Dispatch Reviewer, Revise, Write Tests) from the `qrspi-acceptance-tester` sub-agent prompt into the `qrspi-accept.md` task dispatching controller itself.
- **Expected downside:** Requires creating more pipeline state artifacts to persist the between-actions data across the flattened steps.

## 5. Suggested Prompt Rewrites

### Rewrite 1
File: `agents/deepwork.md`
Problematic pattern: "Every stage subagent returns: \n### Status — PASS | FAIL\n### Files Written..."
Safer replacement:
```text
Every stage subagent MUST return its output strictly within these XML tags. Do not write text outside the tags:
<response>
  <status>PASS or FAIL</status>
  <files_written>list of pipeline files created</files_written>
  <summary>one-line description</summary>
</response>
```
Why this is safer for legacy MoE: Replacing markdown headers with XML constraints grounds the output token sequence deterministically. Models are heavily trained to obey tag boundaries strictly, neutralizing preamble conversational filler that breaks legacy parsing capabilities.

### Rewrite 2
File: `agents/qrspi-implement.md`
Problematic pattern: "Implement this task using TDD: 1. Write failing tests... 2. Implement minimal code... 3. Self-review"
Safer replacement:
```text
=== INSTRUCTIONS ===
Implement the requested functional code to fulfill the task specifications precisely.
Focus ONLY on writing the source code implementation. Do NOT write tests or perform a self-review in this run; those are handled externally.
Halt immediately after writing the code, commit the changes, and return your status.
```
Why this is safer for legacy MoE: Removing TDD reasoning and critically sycophantic self-review from the immediate generative task eliminates mode collapse overlap. A legacy MoE is highly capable when confined simply to writing code to fulfill a spec independently.

### Rewrite 3
File: `agents/qrspi-plan.md`
Problematic pattern: "re-dispatch qrspi-plan-writer with the original inputs plus: === REVIEW FEEDBACK ==="
Safer replacement:
```text
=== CRITICAL RETRY NOTICE ===
Your previous plan was rejected. You MUST pivot your approach. Focus unconditionally on rectifying these exact issues:
[paste the reviewer output verbatim]

Do NOT generate the same plan format. Address the feedback above, then process:
=== GOALS ===...
```
Why this is safer for legacy MoE: Appending feedback to the bottom of large prompts succumbs to instruction dilution. Front-loading the negative constraint forcibly pivots the model behavior away from its historical generative repetition baseline.

### Rewrite 4
File: `agents/qrspi-code-review.md`
Problematic pattern: "=== FILE CONTENTS ===\n[paste the line-numbered contents of each changed file verbatim]"
Safer replacement:
```text
=== FILE DIFFS ===
[paste ONLY the unified diffs context of code specifically altered or introduced by the implementer]
```
Why this is safer for legacy MoE: Full file ingestion inherently pushes large systems out of narrow context bandwidth. Supplying exact unified diffs ensures tokens are efficiently spent focusing the model on evaluating execution vulnerabilities directly. 

## 6. Validation And Experiments

**4 Metrics To Track:**
- **Regex Parse Failure Rate:** Tracking how often deepwork scripts violently crash when parsing stage state returns.
- **Retry Loop Peak Rate:** Percentage of review rounds in `qrspi-plan` hitting the maximum failure cap of 10 loops.
- **Mean Active Tokens per Prompt:** Measuring context density during `qrspi-plan` and `qrspi-code-review` steps specifically.
- **Backward Loop Invocation Rate:** To identify if tasks are effectively succeeding or randomly trapping models into early loop resets.

**3 A/B Tests To Run:**
- A/B test unified git diffs vs full line-numbered files in the code review module to check for hallucinatory variance rates.
- A/B test verbatim context concatenation vs extractive summaries during `qrspi-plan` baseline context generation.
- A/B test extracting test code synthesis vs implementation tasking in `qrspi-implementer` to measure execution stability against execution speed overhead.

**3 Failure Signatures To Handle with Fallbacks:**
- **Repetitive Formatting Traps:** When an MoE returns identically formed schemas ignoring appended review feedback, the fallback must radically alter the temperature and inject divergence constraints.
- **Sycophantic Test Validation:** The model writes failing logic but "Self Reviews" bypassing the failure. Trigger immediate reliance on grounded deterministic execution tools parsing.
- **Bleeding Tags/Unclosed XML Structure:** Encountering truncated completions. The fallback must re-prompt without tasking requirements, strictly telling the MoE to complete closing tags.

## 7. Final Verdict

This pipeline cannot be made entirely legacy-MoE friendly with standard prompt hardening alone. While schemas bounds, rewriting retry loops with front-loaded urgency, and restricting context volume will patch over superficial errors (like regex parsing breaks), the cognitive structure of the actual implementation steps exceeds the single-inference abilities of legacy models. 

The core implementation (`qrspi-implement.md`) and acceptance boundaries (`qrspi-accept.md`) most decisively mandate structural splitting. Mode collapse triggered by mixing testing, generation, and critique inside one instruction stream will consistently unravel legacy generations regardless of how concise or robustly the constraints are framed.

Before embarking on any broader codebase adjustments, the immediate changes must be migrating away from verbatim document dumping for stages relying on `plan` / `review`, and converting all agent-to-deepworker exchanges to strict, explicit XML schemas. Hardening context weight and validation formatting acts as the safety net required prior to restructuring the wider loop iterations.
