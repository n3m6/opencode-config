---
name: principle-never-block-on-the-human
description: Apply when tempted to ask 'should I do X?' on reversible work. Proceed, present the result, let the
  human course-correct after the fact; reserve confirmation for irreversible actions.
metadata:
  opencode/autoinvoke: false
---

# Never Block on the Human

The human supervises asynchronously. Agents must stay unblocked. Make reasonable decisions, proceed, and let the human course-correct after the fact.

**Why:** Every permission pause stalls the pipeline and makes the human the bottleneck. Since code changes are reversible and reviewable, a wrong decision usually costs less than blocking.

**Pattern:**
- **Proceed, then present.** Do the work, show the result. Don't ask "should I do X?" Do X, explain why.
- **Make the system self-healing.** When you notice a problem, log it and fix it in the next round.

**Boundaries:**
- **Irreversible actions** (force-push, delete production data, send external messages) require applicable authorization. An existing explicit grant remains valid.
- **Reversible actions** (write code, edit notes, split tasks) should proceed without blocking.
- **Product direction** comes from the human. *Execution* should not block.

Apply this principle within the user's scope and current session permissions. Read [OpenCode runtime](../../references/opencode-runtime.md) for delegation and authorization boundaries. Missing permission or unavailable independent review is a gap to report, not permission to bypass a limit.
