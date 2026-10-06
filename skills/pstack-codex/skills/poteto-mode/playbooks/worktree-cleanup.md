### Worktree and simulator cleanup

Reclaim only the requested, verified-unused state and preserve recoverable work.

1. Record current disk usage. Run the bundled audit as `python3 <plugin-root>/skills/poteto-mode/scripts/worktree-audit.py <repo-path>`. It reads actual worktree paths and reports tracked, untracked, and ignored contents without deleting anything. Branch merge status is evidence, not permission to remove a checkout.
2. Inspect attached worktrees, pinned or active chats, running agents, and relevant processes through available tools. An unavailable usage check leaves a candidate unresolved. Do not infer abandonment from age or a missing name in the sidebar.
3. Check each candidate's branch/commit, local changes, unpushed commits, ignored assets, and relation to the task. Primary, pinned, shared, or active worktrees stay. Preserve needed ignored files separately; Git snapshots may omit them.
4. For an app-managed worktree, prefer its archive tool after verifying the returned identity. Its snapshot and constraints govern recovery. For an ordinary worktree within the authorized cleanup set, use normal `git worktree remove <exact-listed-path>` when clean. Do not force removal or recursively delete a directory merely because normal removal refused it.
5. If cleanup would lose uncommitted or untracked work, prepare the inventory and preservation options, then obtain the needed user decision. Existing explicit authorization for a specific discard remains valid. Never broaden a worktree request into removal of app data or caches.
6. Remove unavailable simulators or named caches only when that separate cleanup is requested and the platform tools are actually present. Protect active instances and user-owned files. Re-measure space and re-list worktrees.

**Reply:** before/after usage, archived or removed worktrees, preserved artifacts, and held candidates with concrete reasons.
