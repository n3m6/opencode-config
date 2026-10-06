### Opening a PR

Use this delivery step only when the user requested a PR or established PR delivery for the task.

1. Inspect repository instructions, status, and the actual default/base branch. Prefer a suitable existing checkout or managed worktree. Isolate concurrent writers. Preserve unrelated edits and local commits; never reset a shared checkout to produce a tidy PR. Use the `opencode/` prefix for new branches unless the user or repository says otherwise.
2. Review the actual scoped diff. Apply the bundled code cleanup, relevant comment review, and technical-writing guidance. Run required checks and meaningful behavior proof. Record material gaps; an independent review is useful when warranted and permitted.
3. Prepare small ordered commits when appropriate to the change. Stage only intended files. Respect repository conventions for titles and commit structure. Do not rewrite shared history for formatting.
4. Write a reviewer-facing description around the final problem and resulting behavior, with relevant verification and real tradeoffs. Follow the repository template; a small PR can be two sentences and validation. Put bulk logs, measurement details, and review receipts in linked artifacts. Use structured tool arguments or `--body-file` for multiline text.
5. Create through the available supported PR tool or authenticated forge CLI. Respect draft or ready preferences and actual verification state. A stack's root targets trunk; each child targets its parent branch. Do not promise a PR when no authenticated creation path exists.
6. Read back the actual URL, title, body, base, head, and draft state. Include the URL of every created PR in the final reply. Opening a PR does not start a monitor or authorize merging.
7. Deliver the link and current validation. Babysit follows only when requested; Shipping requires actual merge authorization.

**Reply:** PR link, behavior change, validation, and material unresolved gaps.
