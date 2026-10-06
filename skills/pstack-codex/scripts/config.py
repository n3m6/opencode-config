#!/usr/bin/env python3
"""Read and validate pstack settings without changing native OpenCode configuration."""
import argparse
import json
from pathlib import Path
import sys

ROLES = frozenset("feature refactoring bug-fix perf-issue hillclimb judgment hardest how-explorer how-explainer why-investigator why-synthesizer reflect-tooling reflect-judgment arena-runner arena-judge swarm-worker architect-runner interrogate-reviewer".split())
PANELS = frozenset("arena-runner arena-judge architect-runner interrogate-reviewer".split())
EFFORTS = frozenset("inherit-parent none minimal low medium high xhigh max ultra".split())
DEFAULTS = {"version": 1, "max_workers": 3, "arena_candidates": 3, "reviewers": 3, "roles": {}}


def entries(name, value):
    if isinstance(value, list):
        if name not in PANELS or not 1 <= len(value) <= 128:
            raise ValueError(f"Invalid panel settings: {name}")
        return value
    return [value]


def validate(data, capabilities=None):
    if not isinstance(data, dict) or set(data) - set(DEFAULTS):
        raise ValueError("Expected a configuration object with supported keys")
    if type(data.get("version", 1)) is not int or data.get("version", 1) != 1:
        raise ValueError("Unsupported configuration version")
    for key in ("max_workers", "arena_candidates", "reviewers"):
        value = data.get(key, DEFAULTS[key])
        if type(value) is not int or not 1 <= value <= 128:
            raise ValueError(f"{key} must be an integer between 1 and 128")
    roles = data.get("roles", {})
    if not isinstance(roles, dict) or set(roles) - ROLES:
        raise ValueError("Unknown role in roles")
    role_entries = [(name, role) for name, value in roles.items() for role in entries(name, value)]
    for name, role in role_entries:
        if not isinstance(role, dict) or set(role) - {"model", "reasoning_effort"}:
            raise ValueError(f"Invalid role settings: {name}")
        model = role.get("model", "inherit-parent")
        effort = role.get("reasoning_effort", "inherit-parent")
        if not isinstance(model, str) or not model or not isinstance(effort, str) or effort not in EFFORTS:
            raise ValueError(f"Invalid model or reasoning effort: {name}")
        if capabilities is not None:
            if not isinstance(capabilities, dict) or not isinstance(capabilities.get("models"), dict):
                raise ValueError("Capabilities must contain a models object")
            if any(not isinstance(name, str) or not isinstance(efforts, list) or any(not isinstance(value, str) for value in efforts) for name, efforts in capabilities["models"].items()):
                raise ValueError("Capabilities must map model names to reasoning-effort lists")
            resolved_model = capabilities.get("parent_model") if model == "inherit-parent" else model
            models = capabilities.get("models", {})
            if model != "inherit-parent" and model not in models:
                raise ValueError(f"Model is not confirmed available: {model}")
            if effort != "inherit-parent" and effort not in models.get(resolved_model, []):
                raise ValueError(f"Reasoning effort is not confirmed for {resolved_model}: {effort}")
    return data


def load(project=None, user_config=None):
    result = dict(DEFAULTS, roles={})
    paths = [Path(user_config) if user_config else Path.home()/".config/opencode/pstack/config.json"]
    if project is not None:
        paths.append(Path(project)/".opencode/pstack.json")
    for path in paths:
        if path.exists():
            data = validate(json.loads(path.read_text()))
            result.update({k: v for k, v in data.items() if k != "roles"})
            for name, role in data.get("roles", {}).items():
                inherited = result["roles"].get(name, {})
                result["roles"][name] = dict(inherited, **role) if isinstance(inherited, dict) and isinstance(role, dict) else role
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    show = commands.add_parser("show")
    show.add_argument("--project", type=Path)
    show.add_argument("--user-config", type=Path)
    check = commands.add_parser("validate")
    check.add_argument("input", type=Path)
    check.add_argument("--capabilities", type=Path)
    write = commands.add_parser("write")
    write.add_argument("input", type=Path)
    write.add_argument("--destination", type=Path, required=True)
    write.add_argument("--capabilities", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "show":
            print(json.dumps(load(args.project, args.user_config), indent=2))
            return
        data = json.loads(args.input.read_text())
        capabilities = json.loads(args.capabilities.read_text()) if args.capabilities else None
        validate(data, capabilities)
        if args.command == "write":
            role_entries = [role for name, value in data.get("roles", {}).items() for role in entries(name, value)]
            overrides = any(r.get("model", "inherit-parent") != "inherit-parent" or r.get("reasoning_effort", "inherit-parent") != "inherit-parent" for r in role_entries)
            if overrides and capabilities is None:
                raise ValueError("Writing overrides requires --capabilities with confirmed models and efforts")
            args.destination.parent.mkdir(parents=True, exist_ok=True)
            args.destination.write_text(json.dumps(data, indent=2)+"\n")
            print(args.destination)
        else:
            print("Configuration is valid")
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
