# Legacy MoE Optimization Audit Prompt

Use the prompt below to audit the current deepwork pipeline for issues that are likely to appear when the pipeline runs against a legacy Mixture-of-Experts coding model.

````text
[MODE: PIPELINE AUDIT]
[DOMAIN: PROMPT ENGINEERING / AGENTIC CODING / LEGACY MOE]
[TARGET MODEL: Legacy Mixture-of-Experts model, roughly early Mixtral-class behavior]

You are auditing an existing agentic coding pipeline for compatibility with a legacy Mixture-of-Experts model.

Assume the target model has these weaknesses:
- fragile expert routing
- effective context degradation beyond a modest working window
- instruction dilution in long prompts
- verbose drift and repetition in multi-step loops
- weaker structured-output reliability
- hallucinated APIs, test outcomes, and imports
- poor self-critique compared with tool-grounded validation
- a tendency to repeat the same failed fix unless retry state is mutated externally
- weaker performance when planning, coding, testing, and reviewing are mixed in one inference

Your goal is to identify issues in the current pipeline that would be acceptable for a modern frontier model but risky for a legacy MoE model, then recommend concrete prompt-contract and orchestration fixes.

Audit these files in this order:
1. agents/deepwork.md
2. agents/qrspi-plan.md
3. agents/qrspi-implement.md
4. agents/qrspi-accept.md
5. agents/qrspi-code-review.md
6. Only inspect directly related child-agent prompts if you need them to confirm a specific finding.

What to preserve unless there is a strong reason to change it:
- disk-backed state between stages
- explicit stage boundaries
- deterministic external validation
- backward-loop handling as a controller-level concept

Be skeptical and specific. Do not give generic advice like "make prompts clearer" or "use better models." Tie every finding to the current pipeline as written.

Look for the following failure modes:

1. Routing drift and task impurity
- Does a single stage prompt ask the model to switch between different cognitive modes, such as planning, coding, testing, reviewing, and committing, inside one inference?
- Does a prompt mix multiple technical domains or languages without explicit routing cues?
- Are domain tags, mode tags, language tags, or version tags missing where they would help a legacy MoE route correctly?

2. Context overload and lost-in-the-middle risk
- Does a stage paste large upstream artifacts verbatim when a compact state object or targeted excerpt would be safer?
- Does a stage depend on the model carrying too much earlier context instead of re-stating the minimum needed state?
- Are full files, full plans, or long summaries being passed where only a focused slice is needed?

3. Planning/coding/testing mode collapse
- Does a prompt ask the same model call to plan and implement?
- Does it ask the same call to write tests, write code, review code, and decide readiness?
- Does it ask the model to do self-review that should be split into a separate pass or separate agent?

4. Blank-page generation vs scaffolded editing
- Does the pipeline ask the model to synthesize too much from scratch instead of filling a scaffold, replacing a bounded block, or working from signatures/tests?
- Are there places where fill-in-the-middle or skeleton-first prompting would reduce risk?

5. Weak structured-output contracts
- Are outputs too free-form for reliable parsing?
- Are schemas underspecified?
- Does a prompt mix prose, markdown, and machine-parsed structure without clear delimiters?

6. Weak review design
- Are review prompts qualitative when they should be checklist-based, binary, or rubric-driven?
- Is the reviewer likely to be sycophantic because it is effectively grading its own work or operating without a negative-bias checklist?
- Should one review pass be split into critic and optimizer passes, or otherwise made more specialized?

7. Loop instability
- When a test or review fails, is there a hard retry limit?
- Does the retry prompt mutate strategy, or is the model likely to repeat the same fix?
- Is the model forced to explain root cause before retrying?
- Does the loop reset context cleanly, or does it keep appending more history until the model degrades?

8. Validation realism
- Does any prompt rely on the model to infer that tests passed instead of using deterministic tool output?
- Are errors and tracebacks filtered to the smallest useful failure signature, or is noisy output likely to pollute context?
- Are lint/type/test gates early enough and concrete enough for a legacy model to use them effectively?

9. Controller overreach vs thin dispatch
- Even if deepwork is described as a thin dispatcher, do any downstream prompts still hide oversized responsibilities inside a single stage?
- Are there stages that should be split further for a legacy MoE model, even if they are acceptable on stronger models?

10. Observability and experimentation gaps
- What should be measured to know whether the pipeline is actually improving for a legacy MoE?
- Which prompt-level A/B tests or routing experiments are most likely to pay off?

Use this evaluation standard:
- Treat legacy-MoE compatibility as the primary constraint.
- Prefer small prompt-contract changes over full redesign when possible.
- Escalate to stage splitting only when prompt hardening is unlikely to be enough.
- Distinguish between issues already mitigated by the current design and issues that remain exposed.

Output format:

## 1. Executive Summary
- Maximum 6 bullets.
- State the 3 to 5 highest-risk compatibility issues.
- State the 2 to 4 current pipeline strengths that should be preserved.

## 2. Findings Table
Use this exact table format:

| # | Severity | File | Stage | Legacy-MoE Failure Mode | Trigger In Current Prompt | Why It Fails On Legacy MoE | Likely Symptom | Recommended Fix | Fix Type |

Rules:
- Severity must be one of: Critical, High, Medium, Low.
- File must be a real repository path.
- Stage must be one of: Deepwork, Plan, Implement, Accept, Review, or Child Agent.
- Trigger In Current Prompt must quote or paraphrase the exact instruction that creates the risk.
- Fix Type must be one of: Prompt Rewrite, Context Reduction, Stage Split, Schema Hardening, Loop Control, Routing Tag, Tool Gate, Retry Mutation, or Metrics.

## 3. Stage-by-Stage Risk Review
For each of these files, give a short section:
- agents/deepwork.md
- agents/qrspi-plan.md
- agents/qrspi-implement.md
- agents/qrspi-accept.md
- agents/qrspi-code-review.md

For each section:
- note what already helps legacy MoE performance
- note what still creates risk
- say whether the stage should be hardened, split, or left mostly unchanged

## 4. Highest-Leverage Changes
Provide exactly 5 changes.

For each change include:
- Title
- Why it matters for legacy MoE specifically
- Smallest viable change
- Expected downside or tradeoff

At least 3 of the 5 changes must be prompt-level changes that do not require a full pipeline redesign.

## 5. Suggested Prompt Rewrites
Provide 3 to 5 concrete rewrite examples for the most important risky instructions.

For each rewrite use this format:

### Rewrite N
File: <path>
Problematic pattern: <short quote or paraphrase>
Safer replacement:
```text
<replacement prompt text>
````

Why this is safer for legacy MoE: <1 short paragraph>

## 6. Validation And Experiments

Provide:

- 4 metrics to track
- 3 A/B tests to run
- 3 failure signatures that should trigger fallback behavior or task simplification

## 7. Final Verdict

Answer in 3 short paragraphs:

- Can this pipeline be made legacy-MoE friendly with prompt hardening alone?
- Which stages most likely need structural splitting?
- What should be changed first before any broader redesign?

Additional constraints:

- Do not assume frontier-model strengths.
- Do not recommend open-ended autonomous planning.
- Do not recommend passing full repository context by default.
- Do not recommend letting the model decide whether tests passed.
- Prefer dense technical language over conversational filler.
- If a finding is speculative, label it clearly as speculative.

```

```
