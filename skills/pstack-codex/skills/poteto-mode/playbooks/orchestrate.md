### Orchestrate

Run a standing program with multiple tracks from one coordinating chat. A single task driven to a predicate uses Autonomous run; one bespoke run uses figure-it-out.

1. Write durable standing orders: goal, success evidence, scope, user review gates, publishing and merge authorization, budgets, repository/base, and the queue. Keep user-owned decisions visible. Plan-only requests finish at the plan.
2. Choose the smallest useful coordination structure. The parent assigns work, drains evidence, reviews outcomes, and reports progress. Add sub-coordinators only when actual workload and supported nesting justify them. Available capacity bounds simultaneous work, not queue size.
3. Keep a task board in the program workspace, such as `.pstack/<program>/units.json`, with unit ID, dependencies, owner, branch/worktree, head/base, state, artifacts, proof, and next action. The parent is its writer. Workers return artifacts and compact reports rather than mutating shared coordination state. No unbundled orchestration daemon is required.
4. Dispatch complete briefs to permitted workers in isolated checkouts or disjoint scopes. Reviewers inspect exact artifacts and commits independently. A read-only brief prevents assigned writes but is not tool-enforced isolation. Record unavailable independence or runtime drivers as gaps.
5. Drain completions promptly and compare reports to real diffs, checks, and artifact state. Count verified units, not messages. Return proven defects in one scoped fix brief. Preserve the original user goal and later corrections in each replacement brief.
6. Refresh branch and dependency state before integrating. Keep stacks explicit. Use Babysit and Shipping for CI, review, and authorized merge. A worker never inherits merge authority from a vague coordinator recommendation.
7. Check liveness with available agent tools and observed work, not guessed runtime or transcript mtime. Before replacing a stalled worker, identify existing changes, running processes, and active locks; interrupt supported work safely and transfer the usable state. A stuck or missing lane remains outstanding.
8. Checkpoint standing orders, queue, decisions, proof, and next drain. If the user requests multi-day ongoing execution, use available automation and resumption tools with clear completion and notification rules. Without them, state the continuation limit. After restart, reconstruct from the saved board and live forge/branch state rather than assuming old agent IDs survived.
9. End when the program's observable goal is met and all delegated work is drained, or report the precise unfulfilled predicate and required next action. Do not redefine success around a budget or platform limit.

**Reply:** verified progress, current frontier, decisions, live blockers, remaining work, and the durable checkpoint.
