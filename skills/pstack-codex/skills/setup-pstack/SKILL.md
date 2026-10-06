---
name: setup-pstack
description: Configure which models pstack uses per role and at what reasoning budget. Detects your available
  models and writes a pstack preferences file that overrides the skill defaults. Use for @setup-pstack,
  "configure pstack models", "pstack budget", or changing pstack's model choices.
---

# Setup pstack

Configure pstack's worker count and role preferences. Defaults inherit the parent model; no setup is required to start.

1. Read [OpenCode runtime](../../references/opencode-runtime.md), especially model overrides and configuration precedence. Inspect the session's available subagents, models, and variants, and which overrides an agent definition supports. Do not derive model IDs or variants by guessing suffixes.
2. Read existing settings with `python3 <pstack-root>/scripts/config.py show --project <project-root>`, where `<pstack-root>` is the package root (two levels above this skill's directory). Confirm which scope the user requested: personal settings at `~/.config/opencode/pstack/config.json` or project settings at `.opencode/pstack.json`. Preserve unrelated existing settings.
3. Show the current roles and worker counts. If the user already supplied choices, apply them. Otherwise ask only for preferences needed to configure them. Leaving every role inherited is a valid choice. A worker count is a total to queue; concurrency is bounded by `max_workers` and actual runtime limits.
4. Draft JSON with `version: 1`, optional `max_workers`, `arena_candidates`, `reviewers`, and `roles`. Each ordinary role is an object with separate `model` and `reasoning_effort` values. Candidate/reviewer roles can be lists of those objects, one seat per entry; an arena-judge list supplies a pool for one judge. Use `inherit-parent` for either setting to inherit it. Supported role names are defined in [config.py](../../scripts/config.py).
5. For overrides, write a temporary capability record from actual session metadata: `{"parent_model":"<confirmed-model>","models":{"<confirmed-model>":["<supported-effort>"]}}`. These are placeholders describing the schema, not real choices. Validate with `python3 <pstack-root>/scripts/config.py validate <draft.json> --capabilities <capabilities.json>`. Do not claim an override can run when no matching subagent or model supports it.
6. Write the selected file with `config.py write <draft.json> --destination <chosen-path>` and `--capabilities` when overriding a model or effort. Re-read effective settings. Explain that pstack reads this file itself; it is not a native OpenCode setting, and a role override only takes effect through a matching subagent.
7. If the task includes creating a verification skill, route to [create-verification-skill](../create-verification-skill/SKILL.md). Otherwise report any missing verification harness as an optional follow-up.

Reply with the saved scope, effective preferences, and unsupported choices or remaining gaps.
