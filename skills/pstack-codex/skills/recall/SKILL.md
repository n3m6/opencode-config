---
name: recall
description: Reconstruct your recent working context from your own chat history, live state, and the shared record
  (user reports, prior fixes, incidents), then hand back a tight current-state brief. Use for 'recall my work on
  X', 'catch me up', 'what have I been working on', 'where did I leave off', before starting or resuming work.
metadata:
  opencode/autoinvoke: false
---

# Recall

Reconstruct current working context from scoped chat history, live repository state, and the shared record. Return a brief the user can act on.

1. Pin the requested project, topic, and time range. Default to the active project and the last seven days only when the user says recent without a range. A specific prior chat to continue uses the Session pickup playbook. Use a complete supplied state capsule instead of mining it again.
2. Read [OpenCode runtime](../../references/opencode-runtime.md). Use available OpenCode session listing and reading tools, paging as needed. Read only matching chats and skip test or evaluation noise. Use an explicitly provided local transcript when needed; do not guess filesystem history paths. If history access is unavailable, work from the current conversation and repository and say what context is missing.
3. Extract each thread's goal, decisions, open work, corrections, and artifacts, with real chat IDs or source links. Delegate large scoped searches only when permitted. Keep raw records out of the main context.
4. For a named subsystem, feature, or bug, use [why](../why/SKILL.md) to reconstruct the shared record: current symptoms, prior fixes, reverts, incidents, and decisions. Keep it scoped and mark unavailable sources. Pure activity recall can skip this sweep.
5. Check inherited branches, PRs, and tickets against live state. A summary of a command is not its output; inspect the artifact or actual record when the answer depends on what ran.
6. Write the capsule, one status line per thread, recurring problems, and the single next useful action. Keep all in-scope threads while cutting redundant detail. Use accurate status labels such as merged, open PR, in flight, verified uncommitted, reverted, or planned. Cite the real record and sanitize private context before public output.
