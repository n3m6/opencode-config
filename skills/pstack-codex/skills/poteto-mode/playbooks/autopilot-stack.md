### Autopilot-stack

Build and verify one linear PR stack for the user to review and land.

1. Establish the ordered units, current base branch, user review gates, and delivery scope. Do not merge under this playbook.
2. Use permitted owners in isolated worktrees for self-contained work. Dependent units branch from the parent's exact tip. Each PR targets its parent branch, with the root targeting trunk. Record branch, base, head, owner, checks, and proof in a durable task board.
3. Build in verifiable units and inspect the actual diffs. Use code cleanup, scoped comment review, and repository checks. Publish according to the requested PR state and attach created PRs when available.
4. Audit owners and branch state through available tools. Bound active workers by runtime limits. Use consolidated handoffs and preserve uncommitted work before replacing a stalled owner. Schedule later audits only when the user requested that ongoing behavior.
5. Run Babysit to merge-ready in stack order. The root owns restacking when needed. Re-run affected checks after a changed patch or base. Independent verification follows Shipping's evidence rules; missing lanes remain gaps.
6. Report STACK-READY only when every required unit has current proof and no unresolved blockers. Hand back the bottom-to-top list, review gates, and any gap. The user lands the stack or separately authorizes Shipping.

**Reply:** the ordered stack, current proof and CI, review gates, unresolved work, and the next action to land it.
