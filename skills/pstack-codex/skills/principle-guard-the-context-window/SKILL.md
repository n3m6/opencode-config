---
name: principle-guard-the-context-window
description: 'Apply when context is filling up: large outputs, long files, repeated reads, fan-out planning. Route
  bulk to subagents; keep summaries in the main thread, not raw payloads.'
metadata:
  opencode/autoinvoke: false
---

# Guard the Context Window

The working context is finite, even when the session can compact earlier turns. Every token should be worth its cost.

**Why:** Context overflow degrades reasoning quality, creates compression artifacts, and halts progress.

**Pattern:**
- **Isolate large payloads.** Route verbose outputs, screenshots, and large documents to subagents. The main context gets summaries, not raw data.
- **Keep frequently used content inline.** Templates and references used on every invocation belong in the skill file, not in separate files that cost a read each time.
- **Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs.

Apply this principle within the user's scope and current session permissions. Read [OpenCode runtime](../../references/opencode-runtime.md) for delegation and authorization boundaries. Missing permission or unavailable independent review is a gap to report, not permission to bypass a limit.
