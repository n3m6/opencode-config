---
name: arena
description: Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers
  into it. Use for @arena, 'arena this', 'throw it in the arena', or when one attempt at a non-trivial artifact
  would lock in the wrong shape.
metadata:
  opencode/autoinvoke: false
---

# Arena

Before using delegation, model settings, history, external actions, or persistent monitoring, read [OpenCode runtime](../../references/opencode-runtime.md).

Fan out N parallel attempts at the same task. Read every candidate end to end. Pick the strongest as the base. Graft the best ideas from the others into it. Verify the synthesized result.

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Cross-judge
4. Pick
5. Graft
6. Verify

## Phase A: Frame

The N candidates will receive the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric. State what success looks like for *this* task, then turn it into 3-6 concrete gradeable criteria. The rubric is the picker's tool in Phase D. Candidates only see the task.
3. Pick the candidate count from the user or `arena_candidates` in the pstack configuration, default three, or one candidate per configured panel entry when a list is supplied. Use the `arena-runner` role preferences, inherited by default. Confirm overrides against session capabilities. Multiple same-model runs provide independent attempts, not provider diversity. If parallel delegation is unavailable, build sequential candidate sketches and disclose the loss of independent attempts.
4. Assign output paths. Each candidate writes to its own location (a git worktree where possible, otherwise `/tmp/arena-<slug>/candidate-<n>/`), per the [separate-before-serializing-shared-state](../principle-separate-before-serializing-shared-state/SKILL.md) principle skill.

## Phase B: Fan out

Launch N candidates within the runtime concurrency, each with the same task, shared grounding path, its own output location, and instructions to produce the artifact and a short rationale. Queue excess candidates.

Each rationale names the alternatives the candidate considered and what it rejected.

If a candidate fails to produce output, proceed with N-1 and note the dropout in the synthesis record.

## Phase C: Cross-judge

After all candidates finish, use the `arena-judge` role preference to launch an independent read-only judge when permitted. Give it the rubric and anonymized candidate paths. Use a genuinely different available model when configured. The judge can run while the parent reads the completed candidates. If no independent judge can run, perform rubric scoring yourself and record that limitation.

## Phase D: Pick a base

Read every candidate end to end before picking.

Score each candidate against the rubric criterion by criterion, not on holistic feel. Compare against the cross-judge. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base on which candidate a future maintainer can extend most easily without breaking invariants. Prefer the cleaner boundary or smaller API when two feel tied, per the Laziness Protocol.

Record the pick and the reason in a short synthesis note alongside the base artifact, including the cross-judge's verdict.

## Phase E: Graft

Walk each losing candidate once more and identify what is worth porting into the base. The signal is usually one or two things per candidate, not most of it.

Fold each graft in by hand, per the [redesign-from-first-principles](../principle-redesign-from-first-principles/SKILL.md) principle skill. Don't paste mechanically. The result has to remain coherent under one mental model.

Record what was grafted, from which candidate, and what was rejected and why.

When N candidates converge on the same shape, that is a strong agreement signal. Note the convergence in the record and ship the consensus shape. No graft is needed. When N candidates wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

The synthesized artifact has to hold up under the same scrutiny as any other output, per the [prove-it-works](../principle-prove-it-works/SKILL.md) principle skill.

If verification surfaces a problem the arena did not catch, either Phase A was wrong (re-frame and re-run) or one candidate caught it and you missed the graft (go back to Phase E). Don't paper over.

## Outputs

One synthesized artifact. One short synthesis note alongside, naming the base, the grafts (with source candidate), the rejections, the dropouts if any, and the verification result.
