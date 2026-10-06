---
name: swarm
description: Fan out N parallel workers, drain them, and return one report. Use for @swarm, 'swarm this', or parallel
  coverage, races, gauntlets, and exploration.
metadata:
  opencode/autoinvoke: false
---

# Swarm

Run coverage slices or independent attempts and return one consolidated report.

1. Frame the goal, scope, done predicate, and required artifact. Choose partitioned coverage, a race, or a mix. For a race, declare `first pass`, `rank all`, or `best-of` before launch. N is the total work count, not the concurrency limit.
2. Read [OpenCode runtime](../../references/opencode-runtime.md). Use the configured `swarm-worker` role, inherited by default. Match concurrency to the actual session and `max_workers`. Give each writer a separate checkout or disjoint writable scope. A verifier's brief names exact commits and measurement methods when applicable.
3. Launch permitted workers with complete briefs: goal, slice or arm, artifact path, verification commands, and reporting contract. Queue excess work. If delegation is prohibited or unavailable, cover the slices directly and record that independence or parallelism was unavailable.
4. Each worker returns `PASS`, `ISSUES`, or `BLOCKED` with evidence. A proof of a defect is `ISSUES`; list all proven issues in that slice. A missing required slice is a gap. For malformed reports, request the missing evidence once, then record the gap if it remains.
5. Verify the returned artifacts and apply the declared coverage or race rule. Same-model runs are independent attempts; model or provider diversity must be evidenced by what actually ran.
6. Return a compact results table, deduplicated issues, gaps or dropouts, and the selection rule. Preserve artifact paths without pasting raw worker dumps.
