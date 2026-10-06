# Review the final code

Inspect the actual task diff before committing or handing it back. Follow the repository's conventions and keep the smallest change that achieves the requested behavior.

Remove dead code, unused imports, duplicate logic, speculative fallback paths, and wrappers that add no useful boundary. Trace callers before deleting an API. Preserve the domain shape and public contracts the task requires. Do not add compatibility machinery or blanket guards without a concrete need.

Check newly added comments, type escapes, suppressions, and exception handling against the surrounding code. Keep explanations of real external constraints and API contracts. A formatting cleanup does not justify unrelated architecture changes.

Run the affected checks after accepted changes. Review the final diff against the user's goal, and name any remaining unverified behavior. For adversarial review or comment-specific work, use the bundled interrogate or no-comments skill within its scope.
