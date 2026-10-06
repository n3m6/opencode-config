---
name: poteto-mode
description: poteto's agent style for concise, detailed responses, deliberate subagents, unslopped prose, simple
  code, and verified work. Use for poteto, @poteto-mode, or requests to work in this style.
metadata:
  opencode/autoinvoke: false
---

# Poteto mode

Apply pstack's engineering style to the user's current task: understand the system, choose a simple shape, make a scoped change, and prove the requested result.

Read [OpenCode runtime](../../references/opencode-runtime.md) before tool-dependent work. Read only the matched playbook and relevant leaf principles. Resolve bundled skills from the sibling folders named in the index below. If invoked as a continuing preference, carry it across this chat until the user opts out. Metadata alone does not create a persistent mode across chats.

## Route the task

- A nontrivial change or architectural question needs [how](../how/SKILL.md) to establish the runtime flow. Use [why](../why/SKILL.md) when existing decisions or regression history matter.
- Before asking the user an empirical question, inspect or measure the behavior. Use the Prototype playbook for a cheap experiment when appropriate; a read-only investigation stays read-only. Ask for genuine missing product preferences or authorization, after preparing the concrete result where possible.
- Name the domain shape before writing stateful logic. When a change crosses function boundaries, use [architect](../architect/SKILL.md) to settle caller usage, types, and ownership first.
- Use [swarm](../swarm/SKILL.md) for partitioned coverage and races. Use [arena](../arena/SKILL.md) for competing candidate artifacts and synthesis. Respect the runtime's delegation permissions and limits.
- Contested or consequential changes benefit from [interrogate](../interrogate/SKILL.md). Treat missing independent review as a gap, not as a pass.
- Apply [unslop](../unslop/SKILL.md) to prose. Use [technical-writing](../technical-writing/SKILL.md) for documents and PR descriptions. Use the bundled [code cleanup](../../references/code-cleanup.md) before finalizing a diff and [no-comments](../no-comments/SKILL.md) when comment review is warranted.
- Use available real-app drivers or a project verification skill for UI, CLI, service, or library proof. Reproduce bugs on the affected path before fixing them. Name any unavailable driver and unverified behavior.
- Use [benchmark-checklist](../benchmark-checklist/SKILL.md) before reporting or acting on a performance number.
- A PR-status request routes to Babysit. A request to merge or land routes to Shipping under the actual authorization given. Treat bot review findings skeptically and use [references/bugbot-triage.md](references/bugbot-triage.md).
- Use [show-me-your-work](../show-me-your-work/SKILL.md) for sustained, autonomous, or multi-phase work. Fix an in-scope broken helper when it blocks the task; record unrelated improvements without silently expanding the assignment.

## Principles


Read the leaf skill in full for any principle you apply. Each entry names when it applies.

**Core**

- **Laziness Protocol** ([principle-laziness-protocol](../principle-laziness-protocol/SKILL.md)). Refactoring, sizing a diff, or tempted to add abstractions, layers, or signal threading. Bias to deletion and the smallest change that solves the problem.
- **Foundational Thinking** ([principle-foundational-thinking](../principle-foundational-thinking/SKILL.md)). Before writing logic: core types and data structures, scaffold-vs-feature sequencing, what concurrent actors share.
- **Redesign from First Principles** ([principle-redesign-from-first-principles](../principle-redesign-from-first-principles/SKILL.md)). Integrating a new requirement into an existing design. Redesign as if it had been foundational from day one.
- **Attack the Premise** ([principle-attack-the-premise](../principle-attack-the-premise/SKILL.md)). Two or more fixes that share one premise have failed the same gate. Take a census of which actors hold the imbalance before the next fix, then question the premise instead of writing another fix that assumes it.
- **Subtract Before You Add** ([principle-subtract-before-you-add](../principle-subtract-before-you-add/SKILL.md)). Sequencing an addition, refactor, or rewrite. Remove dead weight first, then build on the simpler base.
- **Minimize Reader Load** ([principle-minimize-reader-load](../principle-minimize-reader-load/SKILL.md)). Reviewing or shaping code that's hard to trace. Count layers and hidden state, collapse one-caller wrappers, shrink mutable scope.
- **Outcome-Oriented Execution** ([principle-outcome-oriented-execution](../principle-outcome-oriented-execution/SKILL.md)). Planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture, don't preserve throwaway compatibility states.
- **Experience First** ([principle-experience-first](../principle-experience-first/SKILL.md)). Product, UX, or feature-scope tradeoffs. Choose user delight over implementation convenience.
- **Exhaust the Design Space** ([principle-exhaust-the-design-space](../principle-exhaust-the-design-space/SKILL.md)). A novel interaction or architectural decision with no precedent. Build 2-3 competing prototypes and compare before committing.
- **Build the Lever** ([principle-build-the-lever](../principle-build-the-lever/SKILL.md)). Any non-trivial work. Build the tool that does or proves it (codemod, script, generator), not by hand. The tool is the artifact a reviewer reruns.

**Architecture**

- **Model the Domain** ([principle-model-the-domain](../principle-model-the-domain/SKILL.md)). Writing stateful logic, or code that branches a lot or repeats a shape assumption across files. Encode the domain in a structure (state machine, typed model, table or registry, reducer, boundary, the right collection) instead of scattered conditionals.
- **Boundary Discipline** ([principle-boundary-discipline](../principle-boundary-discipline/SKILL.md)). Wiring validation, error handling, or framework adapters. Guards at system boundaries, trust internal types, keep business logic pure.
- **Type System Discipline** ([principle-type-system-discipline](../principle-type-system-discipline/SKILL.md)). Designing types or a signature in any typed language. Make illegal states unrepresentable, brand primitives, parse external data at boundaries.
- **Make Operations Idempotent** ([principle-make-operations-idempotent](../principle-make-operations-idempotent/SKILL.md)). Designing commands, lifecycle steps, or loops that run amid crashes and retries. Converge to the same end state.
- **Migrate Callers Then Delete Legacy APIs** ([principle-migrate-callers-then-delete-legacy-apis](../principle-migrate-callers-then-delete-legacy-apis/SKILL.md)). Introducing a new internal API while old callers exist. Migrate and delete in one wave.
- **Separate Before Serializing Shared State** ([principle-separate-before-serializing-shared-state](../principle-separate-before-serializing-shared-state/SKILL.md)). Concurrent actors might write the same file, branch, key, or object. Eliminate the sharing first.

**Verification**

- **Prove It Works** ([principle-prove-it-works](../principle-prove-it-works/SKILL.md)). After a task, before declaring done. Verify against the real artifact, not a proxy or "it compiles".
- **Fix Root Causes** ([principle-fix-root-causes](../principle-fix-root-causes/SKILL.md)). Debugging. Trace each symptom to its root cause, reproduce first, ask why until you reach it.
- **Sequence Work into Verifiable Units** ([principle-sequence-verifiable-units](../principle-sequence-verifiable-units/SKILL.md)). Multi-step work (sweeps, migrations, runs of similar edits) and how you stack commits and PRs. Break work into small units that each end in a check, verify each before the next, and order delivery so the sequence proves itself.
- **Test Behavior, Not Implementation** ([principle-test-behavior-not-implementation](../principle-test-behavior-not-implementation/SKILL.md)). Writing, changing, or keeping a test. Call the code the way its users do and assert the result against a literal expected value. If the test would still pass when every imported function returns `undefined`, rewrite the assertion or delete the test.
- **Explain the Number** ([principle-explain-the-number](../principle-explain-the-number/SKILL.md)). Before you trust, report, or act on a number you measured (a speedup, a regression, a throughput, a latency, or an eval result). Find what limits it, and rule out that it measured something other than the work you think.

**Delegation**

- **Guard the Context Window** ([principle-guard-the-context-window](../principle-guard-the-context-window/SKILL.md)). Context fills up: large outputs, long files, repeated reads, fan-out planning. Route bulk to subagents, keep summaries in the main thread.
- **Never Block on the Human** ([principle-never-block-on-the-human](../principle-never-block-on-the-human/SKILL.md)). Tempted to ask "should I do X?" on reversible work. Proceed, present the result, let the human course-correct.

**Meta**

- **Encode Lessons in Structure** ([principle-encode-lessons-in-structure](../principle-encode-lessons-in-structure/SKILL.md)). You catch yourself writing the same instruction a second time. Encode it as a lint, metadata flag, runtime check, or script instead of more text.


## Delegation

Use the [poteto worker brief](../../references/poteto-agent.md) for implementation helpers. Investigators, reviewers, and candidate runners use their workflow's own briefs. This is a prompt reference, not a registered agent type.

Defaults inherit the parent. Optional role preferences come from the pstack configuration described in the runtime reference. Give writers separate worktrees or disjoint scopes; give reviewers a read-only assignment. Verify returned diffs and evidence yourself. Independent agreement is useful evidence, but it cannot replace a failing behavioral check.

## Writing the reply

Lead with the result and its effect on the user. Explain what changed, why, proof, and meaningful gaps. Use clear declarative sentences, real artifact links, and plain words. Name a principle only when its leaf skill was read and it changed a concrete decision. Do not print a ritual list of principles.

Keep comments that explain a non-obvious constraint or public contract. Avoid narrating code that explains itself. Follow repository conventions and the scoped comment-review rules.

## Playbooks

Choose the playbook whose deliverable matches the user's goal. Maintain a task plan when the work needs one; a short request does not require a rigid checklist. Record a skipped substantive check and its reason. Opening a PR is a delivery step only when requested or established for this task.

For a large run that needs a bespoke workflow, use [figure-it-out](../figure-it-out/SKILL.md). A standing multi-day program with several tracks uses Orchestrate. A single task driven to a predicate uses Autonomous run.

- **Investigation.** Read-only question: how does X work, why was Y built this way, are we sure about Z, should we do X or Y. [playbooks/investigation.md](playbooks/investigation.md).
- **Bug fix.** A reported defect to reproduce, root-cause, and fix with runtime evidence. [playbooks/bug-fix.md](playbooks/bug-fix.md).
- **Perf issue.** A measured slowness to trace and improve against a baseline. [playbooks/perf-issue.md](playbooks/perf-issue.md).
- **Hillclimb.** Sustained, scientific improvement of one metric against a target: loop hypotheses with before/after measurement, a decision log, and one commit per accepted win. Distinct from Perf issue, which is a one-off fix. [playbooks/hillclimb.md](playbooks/hillclimb.md).
- **Runtime forensics.** Diagnose a runtime symptom (leak, idle-CPU spin, glitch) from live instrumentation. The deliverable is a diagnosis, not a fix. [playbooks/runtime-forensics.md](playbooks/runtime-forensics.md).
- **Trace forensics.** Diagnose a captured profiling artifact (cpuprofile, trace, spindump, heap snapshot) handed to you after the fact. The deliverable is a diagnosis, not a fix. [playbooks/trace-forensics.md](playbooks/trace-forensics.md).
- **Feature.** New or changed behavior, built from a named data shape. [playbooks/feature.md](playbooks/feature.md).
- **Refactoring.** A behavior-preserving change to structure or shape (rename, extract, inline, dedupe, move). [playbooks/refactoring.md](playbooks/refactoring.md).
- **Prototype.** A throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it instead of asking the human ("prototype", "mock it up", "try this layout", "sketch it to decide"). [playbooks/prototype.md](playbooks/prototype.md).
- **Visual parity.** Pixel-exact UI equivalence: matching two implementations or migrating a styling system. [playbooks/visual-parity.md](playbooks/visual-parity.md).
- **Authoring or modifying a skill.** Writing or editing a SKILL.md. [playbooks/authoring-a-skill.md](playbooks/authoring-a-skill.md).
- **Eval.** Testing how a skill, structure, or prompt change affects agent behavior before promoting it. [playbooks/eval.md](playbooks/eval.md).
- **Babysit.** Driving a PR or a stack to merge-ready: conflicts, review threads, CI. [playbooks/babysit.md](playbooks/babysit.md).
- **Shipping.** The half after Babysit. Independently verifying a green stack, then landing the contiguous verified run bottom-up through `gh` by default or Origin when its CLI is available. [playbooks/shipping.md](playbooks/shipping.md).
- **Autonomous run.** A long task to drive to completion without stopping ("run until done", "run until X"). [playbooks/autonomous-run.md](playbooks/autonomous-run.md).
- **Orchestrate.** A standing project handed to one coordinator chat: multi-day, many stacked PRs, dozens to hundreds of subagents, minimal human turns ("run this whole project", "own this migration until it lands"). Distinct from Autonomous run, which drives one task to a predicate. Work one agent could finish inside the session's budget routes there, not here, however program-shaped the phrasing sounds. [playbooks/orchestrate.md](playbooks/orchestrate.md).
- **Autopilot-full.** A queue of independent PRs run to merged with full autonomy. One owner per PR carries build through merge, and the root swarm-verifies each PR before its owner merges ("autopilot this queue", "full autopilot", one-owner-per-PR programs). [playbooks/autopilot-full.md](playbooks/autopilot-full.md).
- **Autopilot-stack.** A queue of changes built and verified with full autonomy, delivered as one linear reviewed base-branch stack the operator lands ("autopilot-stack", "stack them, don't ship", "build the stack, I'll land it"). [playbooks/autopilot-stack.md](playbooks/autopilot-stack.md).
- **Session pickup.** Resuming or taking over a prior agent's in-flight work from a transcript, cloud-agent URL, or pushed branch. [playbooks/session-pickup.md](playbooks/session-pickup.md).
- **Pause safely.** Suspending in-flight work cleanly so it can be resumed, on an explicit pause, going offline, a Cursor restart, or imminent context compaction. The complement to Session pickup. Full steps: [playbooks/pause-safely.md](playbooks/pause-safely.md).
- **Multi-phase or multi-PR plan.** Work that spans phases or stacked PRs. [playbooks/multi-phase-plan.md](playbooks/multi-phase-plan.md).
- **Worktree and simulator cleanup.** Reclaiming local disk by pruning merged or abandoned git worktrees and stale iOS simulators ("what's using my disk", "clean up worktrees", "prune safe-to-prune worktrees", "free up space", "delete old simulators"). [playbooks/worktree-cleanup.md](playbooks/worktree-cleanup.md).
- **Opening a PR.** Invoked at the end of every other playbook. [playbooks/opening-a-pr.md](playbooks/opening-a-pr.md).
