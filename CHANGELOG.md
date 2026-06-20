# Changelog

This file records notable changes merged to `main` by date.

## 2026-06-20

Two changes landed today. The first folded the standalone Structure stage (Stage 5) into the Skeleton stage (Stage 4.5) so the combined stage builds the skeleton slice, then immediately maps files and interfaces and runs the automated structure review loop, all in one agent dispatch. The second was an end-to-end dry-run verification of the updated pipeline that found and fixed three residual inconsistencies.

| Time (+0530) | Commit | Summary |
| ------------ | ------ | ------- |
| 18:30        | —      | Package 3: fold Stage 5 Structure into Stage 4.5 Skeleton, drop the Structure human gate, add internal resume checkpoint via skeleton-results.md. |
| 23:15        | —      | Dry-run verification: fix telemetry protocol (Stage 5 row → 4.5 row, terminal_review_state note), fix qrspi-skeleton.md return templates (add skeleton-task.md, specify Step 0 resume return format). |

### Package 3 — Fold Structure into the Skeleton Stage

- **Merged stages.** `qrspi-skeleton` now orchestrates both the skeleton build and the structure mapping + review loop in a single stage (Stage 4.5 — Skeleton+Structure). The standalone `agents/qrspi-structure.md` orchestrator has been deleted.
- **No Structure human gate.** Goals and Design remain the only two human gates. The structure review loop caps at 5 automated rounds; `unclean-cap` proceeds without a gate, with the Plan reviewer and feasibility checker as the downstream safety net.
- **Internal resume checkpoint.** `skeleton-results.md` (PASS) is used as an internal sub-stage checkpoint. If the pipeline is interrupted after the skeleton build but before structure mapping completes, resume re-enters only the mapping sub-step (Step G) — the skeleton build and squash-merge do not re-run.
- **Backward loop B re-wired.** Option B (loop back to Structure) now re-enters only the structure mapping sub-step: `structure.md` and Plan artifacts are deleted, `skeleton-results.md` and the skeleton commit are preserved, and `next_stage: skeleton` lets Step 0 route directly to Step G.
- **Backward loop A updated.** Option A (loop back to Design) now also deletes `skeleton-results.md`. The squash-merged skeleton commit stays on the branch; the feedback file notes this for the Design re-run.
- **quick-fix skip simplified.** The quick-fix route now skips Stages 4 and 4.5 (no more `structure-skipped` state value).
- **Key files:** `agents/qrspi-skeleton.md` (expanded), `agents/qrspi-structure.md` (deleted), `agents/deepwork.md`, `protocol/deepwork-resume-protocol.md`, `protocol/deepwork-backward-loop-protocol.md`, `docs/DEEPWORK.md`.

## 2026-05-24

Five commits landed on `main` today. The work focused on simplifying Stage 7, tightening Stage 8 acceptance rules, merging question generation into the research stage, adding automated pipeline policy, and then hardening the new automated flow.

| Time (+0530) | Commit    | Summary                                                                             |
| ------------ | --------- | ----------------------------------------------------------------------------------- |
| 13:44        | `56cc471` | Removed the Stage 7 simplify pass and its related contracts.                        |
| 14:21        | `72f8eb9` | Tightened Stage 8 acceptance with a lighter reuse-only path and stricter telemetry. |
| 15:20        | `fceff77` | Merged Questions and Research into a single iterative Stage 2 research loop.        |
| 16:13        | `de87387` | Added automated pipeline mode with persistent run-level automation policy.          |
| 16:35        | `b12c570` | Fixed automated-mode edge cases, prompt guards, and recovery details.               |

### 56cc471 - removing simplify pass

- Removed the post-wave `qrspi-simplify-pass` step from Stage 7 and deleted `agents/qrspi-simplify-pass.md`.
- Simplified the fast implementation contract so `qrspi-fast-impl-code`, `qrspi-fast-impl-test`, and `qrspi-fast-impl-verify` now operate only in `fresh` and `code-repair` flows; the old `simplify`, `simplify-sync`, and `### Simplifier Findings` paths were removed.
- Shortened Stage 7 orchestration so implementation now ends after wave execution plus integration and baseline regression checks, without a follow-up simplification round-trip.
- Removed simplifier-related reporting from deepwork metrics and updated verifier, loop, and documentation contracts to match the slimmer implementation pipeline.
- Key files: `agents/deepwork.md`, `agents/qrspi-fast-impl-code.md`, `agents/qrspi-fast-impl-loop.md`, `agents/qrspi-fast-impl-test.md`, `agents/qrspi-fast-impl-verify.md`, `agents/qrspi-implement.md`, `agents/qrspi-verifier.md`, `docs/DEEPWORK.md`.

### 72f8eb9 - tightening acceptance stage

- Added a `lite` acceptance mode for reuse-only coverage. When every current-phase criterion maps cleanly to an existing acceptance suite with `Action: reuse`, Stage 8 can skip reviewer fan-out and test authoring and execute the mapped suites directly.
- Preserved a `full` acceptance path for any round that introduces `new`, `revise`, or `blocked` coverage, lacks a concrete mapped test file, or follows a failed `lite` round.
- Added explicit `boundary_violation` handling so off-boundary file creation or edits are recorded as acceptance failures instead of being mixed into generic execution failures.
- Expanded Stage 8 telemetry and summaries with acceptance mode, planner-review cycle counts, per-round cycle details, and richer failure-reason reporting.
- Key files: `agents/qrspi-accept.md`, `agents/qrspi-acceptance-tester.md`, `docs/DEEPWORK.md`.

### fceff77 - fixed questions

- Merged the old Questions and Research stages into one Stage 2 research loop. Deepwork now dispatches `qrspi-research`, which owns question generation, batch research, synthesis, review, and follow-up question generation.
- Added `agents/qrspi-research-pass.md` to run a single research batch, including batch-local review rounds, cumulative synthesis inputs, and a web fallback when codebase research is empty or too low-signal.
- Reworked question generation and review for `initial` and `follow-up` modes so later rounds ask only incremental questions, maintain a question ledger, preserve compatibility snapshots such as `questions.md`, and track unresolved open questions explicitly.
- Updated stage numbering, state transitions, compatibility artifacts, docs, and telemetry references to reflect the merged Stage 2 research model.
- Key files: `agents/deepwork.md`, `agents/qrspi-question-generator.md`, `agents/qrspi-question-leakage-reviewer.md`, `agents/qrspi-question-quality-reviewer.md`, `agents/qrspi-questions.md`, `agents/qrspi-research-pass.md`, `agents/qrspi-research-reviewer.md`, `agents/qrspi-research-synthesizer.md`, `agents/qrspi-research.md`, `docs/DEEPWORK.md`, `protocol/deepwork-resume-protocol.md`, `protocol/telemetry-protocol.md`.

### de87387 - automated mode

- Added a persistent run-level automation policy to deepwork with `interaction_mode` (`interactive` or `automated`) and `failure_policy` (`fail-closed` or `best-effort`), stored in `state.md`, mirrored into run artifacts, and recovered on resume.
- Passed automation context into Goals and taught deepwork to auto-handle plan and replan unclean-cap gates, backward-loop choices, and stage error handling according to the selected automation policy.
- Distinguished stage-local gates from human-only gates in deepwork telemetry so automated approvals and retries are recorded explicitly rather than treated like manual prompts.
- Updated related stage prompts and protocols so Goals, Design, and Structure can participate in automated runs without losing recovery context.
- Key files: `agents/deepwork.md`, `agents/qrspi-design.md`, `agents/qrspi-fast-impl-code.md`, `agents/qrspi-fast-impl-loop.md`, `agents/qrspi-goals-reviewer.md`, `agents/qrspi-goals-synthesizer.md`, `agents/qrspi-goals.md`, `agents/qrspi-structure.md`, `docs/DEEPWORK.md`, `protocol/deepwork-backward-loop-protocol.md`, `protocol/deepwork-resume-protocol.md`, `protocol/telemetry-protocol.md`.

### b12c570 - automated pipeline fixes

- Added `git diff` and `git log` permissions to deepwork so stage allowlist checks and stage-boundary checkpoint lookups can run in the automated pipeline.
- Fixed prompt guards in Goals, Design, and Structure so `question` is only used during interactive runs.
- Strengthened plan and replan mutation reruns by replaying fuller upstream context, including route-appropriate artifacts, completed-phase evidence, and remaining task specs, into rewrite prompts.
- Corrected several recovery and control-flow edge cases: the replan review prompt now points at the right review artifact path, backward-loop reset preserves automation policy, resume handling surfaces on-disk failed summaries instead of silently restarting, and Stage 9 verify-fix now terminates the original verify-failure branch cleanly once the fix path takes over.
- Normalized repo keyword discovery commands in Goals and Question Generator to use repeated `grep --include` flags instead of brace-glob syntax.
- Key files: `agents/deepwork.md`, `agents/qrspi-design.md`, `agents/qrspi-goals.md`, `agents/qrspi-plan.md`, `agents/qrspi-question-generator.md`, `agents/qrspi-replan.md`, `agents/qrspi-structure.md`, `protocol/deepwork-backward-loop-protocol.md`, `protocol/deepwork-resume-protocol.md`.
