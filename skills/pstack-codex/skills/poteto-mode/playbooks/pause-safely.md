### Pause safely

Stop on the user's explicit pause request and preserve a usable checkpoint.

1. Stop at the next safe boundary. Finish the current atomic operation or back it out; start no new work. Interrupt delegated work through available tools and check what changes or processes remain.
2. Preserve task-owned files and artifacts. Commit a scoped WIP only when the branch and task permit it. Do not stage unrelated user changes, push new work, or create a PR merely to pause.
3. Write a durable note in the task workspace with goal, authorization, current branch/worktree, completed proof, outstanding work, processes, artifact paths, and the first next action. Link a decision trail instead of duplicating it. Use a temporary path only when the checkpoint is explicitly disposable.
4. If an active goal or monitor exists, use its supported pause/update mechanism under the user's request. Do not assume stopping this turn stopped external execution.

**Reply:** confirmed pause state, preserved paths or commits, any still-running operation, and the first action on resume.
