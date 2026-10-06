### Autopilot-full

Coordinate independent PRs through build, verification, and explicitly authorized merge. One owner carries each PR; the parent owns the final verification judgment.

1. Freeze the queue, success criteria, user-owned items, forge, and merge authorization. A request to state a plan ends with that plan until the user authorizes execution. Respect review checkpoints already given.
2. Assign owners within current delegation limits. Each owner gets an isolated branch/worktree, scope, proof criteria, decision trail, and publishing permissions. If agents are unavailable, execute the queue sequentially and disclose the missing independent ownership.
3. Owners build in verifiable units, inspect the final diff, apply bundled code cleanup and scoped comment review, and open PRs as requested. Respect draft preferences and repository conventions. Attach every created PR when the app tool is available. Record the exact code-ready head and any later patch-changing push.
4. Independently verify each code-ready head. Use relevant live behavior, repository checks, regression comparison to trunk, and adversarial review. All required slices need evidence. A missing independent verifier or live driver is a gap, not a clean verdict. Combine proven findings into one scoped fix request; a new patch needs fresh affected verification.
5. Bring each owner to merge-ready through Babysit. Re-check head, base, patch identity, CI, review requirements, and mergeability immediately before merging. Shipping owns that final gate. No owner treats another agent's recommendation as user authorization or bypasses a forge requirement.
6. Maintain a durable queue and decision trail in the task workspace. Read actual worker state, branches, PRs, and check deltas at drain points. Replace a stalled worker with a consolidated brief only after checking what work or processes still exist. Use available future scheduling only when the user requested ongoing monitoring.
7. Merge authorized independent PRs one at a time after the matching verified verdict. Confirm the result on the forge and fetched trunk. Stop at an unverified or user-owned item. End by draining remaining delegated work and reporting any post-merge findings.

**Reply:** each PR's current head, proof, disposition, merge result, and remaining user-owned or blocked items.
