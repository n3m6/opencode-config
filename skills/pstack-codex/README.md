# Pstack (OpenCode)

Rigorous engineering workflows adapted from Lauren Tan's pstack, converted from the Codex plugin for OpenCode. This package includes 49 skills and 23 playbooks. The original MIT license is in `LICENSE`.

Invoke `@poteto-mode` with a concrete task. Use `@how`, `@why`, `@architect`, `@interrogate`, or another bundled skill directly when its workflow is the desired result.

Original invocation policies are preserved. `setup-pstack` permits automatic selection; the other 48 skills are explicit-only and load when you mention them as `@skill-id`.

Personal preferences live at `~/.config/opencode/pstack/config.json`; project preferences at `.opencode/pstack.json` override them. Run `python3 <package-root>/scripts/config.py show --project <project-root>` to inspect effective settings, where `<package-root>` is this directory. `@setup-pstack` guides scoped updates and confirmed overrides.

Read [OpenCode runtime](references/opencode-runtime.md) for tool availability, delegation, configuration, history, authorization, and verification. The package does not supply an MCP server, native UI driver, or persistent scheduler.
