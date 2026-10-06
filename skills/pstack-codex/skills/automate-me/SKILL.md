---
name: automate-me
description: Use for "automate me", "create/update/refresh my -mode skill", "turn/capture my preferences or working
  style into a skill", or wanting agents to follow how the user works. Drafts or revises a personal -mode skill
  via skill-creator + unslop, optionally pulling fresh evidence from recent transcripts.
metadata:
  opencode/autoinvoke: false
---

# Automate me

Create or update a personal working-style skill from the user's explicit preferences and observed recurring behavior.

1. Identify the intended mode and scope. Search the current project's `.opencode/skills` and the user's available skill catalog for an existing matching mode. Preserve its destination. For a new skill, use the destination the user requested, otherwise the local skill-creator's current discoverable default. Do not assume nested category folders are discovered.
2. Use the current conversation and scoped OpenCode session history as evidence, following [OpenCode runtime](../../references/opencode-runtime.md). Read only the requested project and time range. If no history access exists, proceed from supplied preferences and state that limitation. Separate explicit preferences from repeated observations and uncertain inferences.
3. Ask only for material missing preferences. If the user already requested an update, do not ask again whether to update. Honor existing authorization and review checkpoints.
4. Use the available skill-creator to write a concise mode skill. Capture only guidance that changes decisions. Keep task-specific mechanics in relevant skills, link maintained resources, and preserve the user's chosen products and scope.
5. Preserve an existing invocation policy. A new personal mode should use normal automatic discovery unless the user explicitly requests explicit-only behavior. Use supported `agents/openai.yaml` settings rather than inventing a sticky-mode metadata field. Continuing behavior across the current chat is a conversational preference, not cross-chat persistence.
6. Apply [unslop](../unslop/SKILL.md), validate names, descriptions, references, and any scripts, and exercise a representative request. Report what was learned, what was changed, which observations remained tentative, and how to invoke the skill.

This skill authors reusable instructions. It does not create schedules, hooks, or external automations unless the user separately asks for them.
