### Shipping

Verify the exact changes that will land and merge only the authorized contiguous run from the bottom of a stack.

1. Freeze the bottom-to-top PR list and resolve the actual forge tools. Confirm the user's merge authorization and any retained review gates. For each PR, obtain independent proof from a reviewer that did not write the change. Exercise relevant real behavior against base and head, run required repository checks, and record PASS, PASS+NOTES, FAIL, or a verification gap. Missing independent proof is not a pass. External verdict comments require authorization.
2. Stop the landable run at the first PR without passing proof. A passing descendant above that ceiling cannot land through this chain.
3. Record verdict head, base, and `git patch-id --stable` for the reviewed base-to-head diff. Compare to the current patch before merging. A changed patch invalidates affected proof. An unchanged patch after rebase retains only applicable code proof; refresh CI and mergeability at the current head. For changes confined to tests or documentation, justify which behavior proof remains applicable and check the changed material afresh. Never substitute matching messages or old green checks.
4. Fetch current trunk and prepare only the lowest verified PR. Rebase or retarget only when needed and authorized for that owned branch. Preserve other work. After publishing, repeat the patch/proof checks. Do not pre-arm descendants.
5. Re-check the current head, base, required checks, review state, mergeability, and user gates. Merge through the supported forge tool with the requested strategy. On GitHub, an authorized example is `gh pr merge <pr> --squash --match-head-commit <verified-head>`. Use auto-merge only when the user requested merge when ready. Never bypass enforced requirements.
6. Confirm the actual merged state through the forge; requesting auto-merge is not a merge result. With GitHub, inspect `gh pr view <pr> --json state,mergedAt,mergeCommit,headRefOid,mergeStateStatus,autoMergeRequest,statusCheckRollup`. Pending checks or an armed auto-merge can be a wait rather than failure. Use bounded event waits and checkpoints; future monitoring follows the runtime rules.
7. After each merge, fetch trunk, confirm the resulting commit, remove the merged item, and recompute the next bottom's base, head, proof, and checks. Do not assume automatic child retargeting happened. Prepare the next PR only after the prior one actually merged.
8. Stop at the verified ceiling. Extending the chain requires proof for the next item. Cancel or finish remaining monitors as authorized.

**Reply:** the verified run and ceiling, reviewer and proof per PR, what was requested versus actually merged, and the next gap.
