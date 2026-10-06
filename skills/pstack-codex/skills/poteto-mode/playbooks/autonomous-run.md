### Autonomous run

Define done as an observable predicate, then drive authorized work to it.

1. State the goal, scope, completion predicate, and permitted external actions before the first iteration. Use actual tests, reproduction results, or delivery state as the predicate.
2. Pick an active-session checking mechanism from the available tools. Use bounded waits for events such as CI or worker completion. Use a background shell command for a long-running process that should notify on completion. A user-requested future monitor needs a persistent scheduling mechanism; when the session exposes none, checkpoint and report that unattended continuation is unavailable.
3. Make the smallest change supported by evidence, verify it, and keep only changes that advance the goal. Sequence verifiable units and record before/after results. Commit or publish according to the task's established delivery scope.
4. Resolve in-scope tooling failures and blockers. Record unrelated discoveries without silently opening new projects or PRs. Ask only for required missing information or authorization; an autonomy grant does not override tool restrictions or named human checkpoints.
5. Checkpoint decisions, branch/worktree state, artifacts, and the next action through show-me-your-work.
6. Stop when the predicate is met, the user stops the run, or the session's actual limits prevent progress. Report a concrete impasse rather than spinning or weakening the predicate.

**Reply:** the predicate, iterations, kept and discarded changes, current evidence, and any required continuation.
