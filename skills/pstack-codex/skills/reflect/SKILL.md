---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface learnings, and route each
  to a concrete edit on an existing skill. Use when the user says reflect.
metadata:
  opencode/autoinvoke: false
---

# Reflect

Turn evidence from the active task into focused improvements to existing skills.

1. Scope the evidence to this task. Read [OpenCode runtime](../../references/opencode-runtime.md) and obtain the active session record through available tools or a supplied transcript. If only summaries are available, mark that limitation and use observable artifacts; do not invent tool traces.
2. Read the existing skills the task actually used. Identify repeated friction, missed judgment, or reliable shortcuts. Prefer an existing skill as the home for a lesson.
3. When permitted, use three independent read-only reviewers with [tooling](references/tooling-reviewer.md), [judgment](references/judgment-reviewer.md), and [divergent](references/divergent-reviewer.md) briefs. Use `reflect-tooling` and `reflect-judgment` preferences, inherited by default. Queue within runtime limits. Otherwise apply the three lenses directly and disclose the lack of independent review.
4. Synthesize with [the synthesis contract](references/synthesizer.md). Separate accepted lessons, rejected suggestions, and backlog. Ground each accepted lesson in an observed failure or useful behavior rather than personal preference inferred from one example.
5. Make the requested skill edits. Preserve scope, invocation policy, and unrelated guidance. Use the available skill-creator for substantial authoring and validate the resulting frontmatter, links, helpers, and relevant behavior. A new skill is warranted only when no existing skill fits and the capability deserves its own entry point.
6. Return the lesson, its evidence, the file changed, validation, and any unresolved gap. Do not turn reflection into unrelated repository cleanup.
