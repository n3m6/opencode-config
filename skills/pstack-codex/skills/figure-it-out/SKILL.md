---
name: figure-it-out
description: 'Design an auditable playbook when no narrower one fits: a large migration, an ambitious multi-part
  change, or work a human reviews after stepping away. Scales rigor to the task, runs a hypothesis loop, and logs
  decisions via show-me-your-work. Use for @figure-it-out, ''figure it out'', a large migration, or when no narrower
  playbook applies.'
metadata:
  opencode/autoinvoke: false
---

# Figure it out

Before using delegation, model settings, history, external actions, or persistent monitoring, read [OpenCode runtime](../../references/opencode-runtime.md).

When the task matches no playbook, design one. The deliverable before any code is the workflow itself: a sequence of phases that scales rigor to the task, runs the scientific method, and leaves a decision trail a human can audit after stepping away.

## Start

Open a todolist whose first item is to read the Principles section of the [poteto-mode](../poteto-mode/SKILL.md) skill. Then add the phases below as todos.

## Phase A: Frame

Ground first, then commit. Don't start the run until you can state:

- The definition of done as a falsifiable predicate (the [prove-it-works](../principle-prove-it-works/SKILL.md) principle skill).
- Scope, quantified: rough units and effort, plus the blockers grounding surfaced.
- The rigor level, biased high. One-way doors and high blast radius get more. Reversible low-stakes steps get less. Rigor is gates and artifacts, not "try harder".

Present the framing and tradeoffs before committing to a long run. Reversible work proceeds (the [never-block-on-the-human](../principle-never-block-on-the-human/SKILL.md) principle skill), but a multi-hour run earns one checkpoint.

## Phase B: Design the workflow

Decompose into atomic, independently-landable units. Sequence riskiest-unknown-first. Scaffold and verification come before features (the [foundational-thinking](../principle-foundational-thinking/SKILL.md) principle skill).

- Build the verification harness before the work, with the baseline captured from the pre-change state, so the check reads as "old value vs new value".
- For one-way-door design decisions, run the [architect](../architect/SKILL.md) skill (it runs [arena](../arena/SKILL.md)). Skip it for mechanical work whose shape is already concrete. A second arena over a settled design is over-engineering (the [laziness-protocol](../principle-laziness-protocol/SKILL.md) principle skill).
- Decide what fans out. Parallelize only across seams, and give each worker its own worktree or branch (the [separate-before-serializing-shared-state](../principle-separate-before-serializing-shared-state/SKILL.md) principle skill). Don't over-fan.
- Write the designed phase list down. That list is what the human reviews.

Then execute the design. Add its steps to the todolist as concrete items, after the Phase C entry and before Phase D. Run each under the Phase C loop discipline, and weave the Phase D log through them, a row as each step lands, rather than saving the whole trail for the end.

## Phase C: Run the loop

Each unit is an experiment. State the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced, revert it if it didn't.
Apply the [sequence-verifiable-units](../principle-sequence-verifiable-units/SKILL.md) principle skill, verifying each unit before starting the next instead of batching checks at the end.

- Verify by inspecting the artifact, never a self-report. When something passes too easily, suspect the observation method before the system.
- Pair delegated work with a judge. If a worker games the gate, reset and harden the contract. If the gate itself is wrong, fix the gate in its own change rather than routing around it.
- A verdict is VERIFIED, NOT VERIFIED, or INCONCLUSIVE. Inconclusive is not a pass. Don't hide a negative.

## Phase D: Keep the audit trail

Log the run via the [show-me-your-work](../show-me-your-work/SKILL.md) skill. figure-it-out's work is usually ambitious enough to commit the trail so the reviewer can read it in the PR. The trail plus the diff is what lets the human come back and trust the work.

## Phase E: Verify and hand back

Check the whole against the Phase A predicate on the real product, not just the harness. Encode any recurring correction as a gate, a lint rule, a check, or a script (the [encode-lessons-in-structure](../principle-encode-lessons-in-structure/SKILL.md) principle skill).

**Reply:** the playbook you designed, the rigor level and why, the decision-trail path, what's verified against the predicate, and what's still open.
