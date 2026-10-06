#!/usr/bin/env python3
"""Inventory Git worktrees and local state. This command never deletes anything."""
import argparse
import json
from pathlib import Path
import subprocess


def git(path, *args, required=True):
    result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
    if required and result.returncode:
        raise ValueError(result.stderr.strip())
    return result.stdout if result.returncode == 0 else None


def status_counts(raw):
    entries = iter(raw.split("\0"))
    tracked, untracked = [], []
    for entry in entries:
        if not entry:
            continue
        kind, path = entry[:2], entry[3:]
        if kind == "??":
            untracked.append(path)
        else:
            tracked.append(path)
            if "R" in kind or "C" in kind:
                next(entries, None)
    return tracked, untracked


def audit(repo, base=None):
    repo = Path(repo).resolve()
    if base is None:
        base = git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", required=False)
        base = base.strip() if base else None
    records = []
    for record in git(repo, "worktree", "list", "--porcelain", "-z").split("\0\0"):
        if not record.strip("\0"):
            continue
        fields = {}
        for item in record.split("\0"):
            if item:
                key, _, value = item.partition(" ")
                fields[key] = value
        path = Path(fields["worktree"])
        entry = {"path": str(path), "head": fields.get("HEAD"), "branch": fields.get("branch"), "locked": "locked" in fields, "prunable": "prunable" in fields, "usage": "unknown; verify active chats, agents, and processes", "removal_authorized": False}
        if not path.exists():
            entry["error"] = "Worktree path is missing"
            records.append(entry)
            continue
        try:
            tracked, untracked = status_counts(git(path, "status", "--porcelain=v1", "-z", "--untracked-files=all"))
            ignored = [p for p in git(path, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").split("\0") if p]
            upstream = git(path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}", required=False)
            unpushed = git(path, "rev-list", "--count", "@{upstream}..HEAD", required=False) if upstream else None
            merged = None
            if base:
                valid = git(path, "rev-parse", "--verify", base, required=False)
                if valid:
                    result = subprocess.run(["git", "-C", str(path), "merge-base", "--is-ancestor", "HEAD", base], capture_output=True)
                    if result.returncode in (0, 1):
                        merged = result.returncode == 0
            entry.update({"tracked_changes": len(tracked), "untracked_files": len(untracked), "ignored_files": len(ignored), "tracked_examples": tracked[:20], "untracked_examples": untracked[:20], "ignored_examples": ignored[:20], "upstream": upstream.strip() if upstream else None, "unpushed_commits": int(unpushed) if unpushed else None, "merged_into_base": merged, "base": base})
        except ValueError as error:
            entry["error"] = str(error)
        records.append(entry)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--base", help="Existing local ref to compare with; does not fetch")
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.repo, args.base), indent=2))
    except ValueError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
