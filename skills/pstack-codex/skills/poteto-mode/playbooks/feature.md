### Feature

**You own the design. Plan, review, verify.** Use permitted implementation helpers when useful. Verify the adopted work.

1. `how` over the affected subsystem.
2. `architect` for parallel design exploration.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target (the [separate-before-serializing-shared-state](../../principle-separate-before-serializing-shared-state/SKILL.md) principle skill). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. Implement against the named shape. Use a permitted scoped implementation helper or arena when competing shapes warrant comparison. Give writers isolated worktrees or disjoint file ownership and require behavioral proof. If delegation is unavailable, implement directly and state the missing independent perspective rather than stalling. Review all adopted diffs yourself.
5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass. Flag it.
6. Rebase into small, ordered commits. Stack follow-ups.
   Use the [sequence-verifiable-units](../../principle-sequence-verifiable-units/SKILL.md) principle skill, building, verifying, and committing each small unit before the next.
7. If the design is contested, `interrogate` before shipping.
8. If PR delivery is requested or established for this task, run **Opening a PR**.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries. Spawn a fresh owner rather than chaining interrupts.

**Reply:** what you built, what you chose and why, the throughput checkpoint, open decisions. Tables for design alternatives.
