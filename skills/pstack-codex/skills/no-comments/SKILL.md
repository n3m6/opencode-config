---
name: no-comments
description: Review comments and workaround explanations in a scoped diff, preserve necessary contracts, and fix
  accepted findings. Use for no-comments or an explicit comment cleanup.
metadata:
  opencode/autoinvoke: false
---

# No comments

Review comments and workaround explanations in the caller's scope. Preserve useful contracts and fix accepted findings.

1. Establish the supplied files or diff. If no scope is given, use the current changes against the repository's actual base branch, including working-tree edits. Read [OpenCode runtime](../../references/opencode-runtime.md).
2. Give a permitted independent read-only reviewer the [comment-reviewer brief](../../references/comment-reviewer.md). This file is a role prompt, not a registered agent type. If independent review is unavailable, review directly and state that limitation.
3. Inspect proposed deletions against nearby code. Preserve license notices, public contracts, proven external constraints, useful source links, and necessary tool directives. An uncertain constraint remains unresolved until checked with [how](../how/SKILL.md) or [why](../why/SKILL.md). Do not delete a safety suppression without correcting the underlying problem.
4. Apply accepted scoped edits. When code can express the constraint, use the smallest useful type, name, API, test, or structural change. Use [architect](../architect/SKILL.md) if the requested fix needs a different shape. Do not widen the assignment just to eliminate every workaround.
5. Run the affected checks and inspect the final diff. Report deletion count, accepted structural fixes, preserved comments with reasons, and unresolved constraints. A report-only request returns findings without applying edits.
