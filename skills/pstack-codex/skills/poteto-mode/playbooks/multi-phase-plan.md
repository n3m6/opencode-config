### Multi-phase plan

Plan a large change as ordered units that each end in a verifiable state.

1. Establish the actual goal, affected subsystems, delivery scope, dependencies, and user review gates. Use how and why for relevant code behavior and decision history. A request for a plan produces a plan, not implementation or PRs.
2. Name the target domain shape and system ownership. Use architect for cross-boundary decisions and competing sketches when useful. Keep source-grounded file pointers and conventions rather than bulk dumps.
3. Order the units by dependency and proof. Each unit names its intended behavior, exact scope, prerequisite, implementation owner, verification commands or driver, expected observable result, and delivery form. A stack records the parent branch and PR base explicitly.
4. Scale verification to the change. Use behavioral tests and actual user paths where relevant. Performance work includes an interleaved base/head baseline, realistic end-to-end metric, and failure budget. A documentation-only unit does not need fictional live-app or performance lanes. Missing required drivers or independent reviewers remain gaps.
5. Separate interaction review gates from mechanical checks. Preserve human review when requested. Use independent reviewers within available concurrency and session authorization; queue excess lanes. Every required slice needs evidence.
6. Write the plan with technical-writing and unslop. Keep task steps in the main document and detailed measurement or reference material in linked appendices. Include the risk that could invalidate the proposed sequence, without speculative filler.
7. If execution is authorized, start the first unit and maintain show-me-your-work. Use Autonomous run or Orchestrate when the scope calls for them. Register future audit ticks only when requested and supported.

**Reply:** ordered phases or PRs, prerequisites, proof and review gates, key choices, and the next unit.
