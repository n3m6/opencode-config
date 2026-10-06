### Eval

**You own the experiment design. Plan, blind, run, synthesize.**

**Non-negotiables for blinding:**

- No `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`, or `arena` in any directory, file, or prompt the candidate sees.
- The candidate prompt looks like an organic user request. State the goal, not the meta.
- No chain-eliciting cues. Don't ask the candidate to list which skills, principles, or files they applied. Ask for design notes generally and grade chain-following from code shape, not self-report.
- Sanitize directory and slug names. Use project-shaped names a user might pick.
- Don't tell the candidate other candidates exist.
- The judge can know it's judging but sees outputs by sanitized label only, never by model name.
- Comparing two variants: one judge scores both sets in a single pass on one scale, blind to which set each came from.

**Steps:**

1. **Frame.** State what variant is under test and what behavior counts as success. Write the rubric (3-6 concrete criteria) for the judge only. Hold it back from candidates.
2. **Set up sanitized environments.** Per-candidate working dir with the variant in place. Plant any context an organic task would have: a project skeleton, the skills the candidate would naturally read.
3. **Author one organic prompt.** What a user would type. No leakage of what's being measured.
4. **Run N permitted independent candidates** per the arena runtime rules, with confirmed different models when configured. Each works in its own sanitized directory. Use the same prompt for each and queue excess runs. If independent execution is unavailable, report that limitation; a direct fixture walkthrough does not establish activation or model differences.
5. **Use one permitted independent blinded judge** per arena Phase C. The judge sees outputs by sanitized label and the rubric, never a model name. State when independent judgment or model diversity was unavailable.
6. **Verify the chain from transcripts, not self-report.** Inspect each candidate's actual tool trace or scoped session record when available, plus its output artifacts. A summary or self-report cannot prove which files were read. Record trace coverage gaps instead of inventing transcript paths. Grade chain-following only where evidence establishes it.
7. **Read every candidate output yourself** end to end. Compare to the judge's verdict. Disagreement means a model is biased or the rubric is ambiguous. Synthesize.

**Reply:** variant under test, rubric, per-candidate notes, judge's verdict, your synthesis, and a recommendation for whether to promote the variant.
