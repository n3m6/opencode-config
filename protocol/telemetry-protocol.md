### Telemetry Protocol

Shared event contract for the QRSPI pipeline telemetry system. Covers write ownership, event schema, taxonomy, emission procedure, and the stage return contract. Derived artifact formats (`run-log.md`, `metrics-summary.md`) are specified in `agents/deepwork.md`.

---

## 1. Purpose and Scope

Telemetry provides three complementary artifacts under `.pipeline/qrspi-<run-id>/telemetry/`:

| File                 | Kind                      | Purpose                                                                |
| -------------------- | ------------------------- | ---------------------------------------------------------------------- |
| `events.jsonl`       | Canonical runtime stream  | One JSON object per line, append-only, never edited after the fact     |
| `run-log.md`         | Derived human timeline    | Chronological incident-review view, regenerated at each stage boundary |
| `metrics-summary.md` | Derived end-of-run rollup | Aggregate counts and durations, generated at Stage 10 and on abort     |

**Out of scope for v1:** per-tool command tracing inside `@build`, external telemetry backends, cross-run dashboards.

**Non-interference guarantee:** Telemetry files are diagnostic-only. The resume recovery algorithm (`deepwork-resume-protocol.md`) never reads any file under `telemetry/`. Backward loop artifact deletion rules never delete telemetry files.

---

## 2. Write Ownership

Only the currently active orchestrator may append to `events.jsonl`. This prevents write races in parallel-dispatch stages.

| Orchestrator      | Events it writes directly                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `deepwork`        | `run.*`, `stage.*`, `gate.*` (when gate is in deepwork context), `backward_loop.*`, `checkpoint.*`, `metrics.*`            |
| `qrspi-research`  | `child.*` for researcher dispatches inside Stage 3                                                                         |
| `qrspi-plan`      | `child.*` for plan-writer, task-spec-writer, task-spec-reviewer, plan-reviewer, baseline-checker dispatches inside Stage 6 |
| `qrspi-implement` | `phase.*`, `child.*` for wave task-loop dispatches and post-wave checker dispatches inside Stage 7                         |
| `qrspi-accept`    | `child.*` for acceptance-tester and backward-loop-detector dispatches inside Stage 8                                       |
| `qrspi-replan`    | `child.*` for replan-writer and replan-reviewer dispatches inside Stage 8.5                                                |

**Leaf agents** (every agent not listed above) never write `events.jsonl` directly. They return a `### Telemetry` section in their structured output; their parent orchestrator serializes the data into the shared stream.

---

## 3. Event Schema

Every event is one JSON object on one line (no trailing comma, no blank lines). Required fields always present; optional fields omitted when not applicable.

**Required envelope fields (all events):** `schema_version:"1"` · `event_id:"<run-id>-<seq>"` · `sequence:<int ≥ 1>` · `ts:<YYYY-MM-DDTHH:MM:SSZ UTC>` · `run_id:"qrspi-YYYYMMDD-HHMMSS"` · `writer_agent:<name>` · `writer_scope:"controller"|"stage-orchestrator"|"nested-orchestrator"` · `event_type:<see §4>` · `status:"info"|"pass"|"fail"|"skip"|"warn"` · `route:"full"|"quick-fix"|"unknown"` · `summary:<one sentence>`

**Conditional scope fields (include only when applicable):** `stage` (all non-`run.*` events) · `stage_instance:<int>` (on re-entry) · `phase:<int>` (stage 7/8/8.5) · `wave:<int>` (stage 7 waves) · `task_id` (task-scoped) · `review_round:<int>` (review-loop events) · `attempt:<int>` (retry events) · `child_agent` + `correlation_id` (all `child.*`) · `parent_event_id` (`child.returned` only)

**Payload objects (omit entirely when empty):** `context:{...}` (stage metrics from `### Telemetry` return) · `artifacts:[...]` (relative file paths) · `timing:{started_at, ended_at, duration_s}` · `decision:{choice, reason}` (gate and loop events) · `error:{message, artifact}` (fail events) · `git:{commit, message}` (checkpoint events)

---

## 4. Event Taxonomy

### 4.1 Taxonomy

| Class             | Events (status)                                                                                                                    | Writer             |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| `run.*`           | `run.started` (info) · `run.resumed` (info) · `run.completed` (pass\|fail) · `run.aborted` (fail)                                  | deepwork           |
| `stage.*`         | `stage.started` (info) · `stage.completed` (pass) · `stage.failed` (fail) · `stage.skipped` (skip) · `stage.retried` (info)        | deepwork           |
| `phase.*`         | `phase.started` (info) · `phase.completed` (pass)                                                                                  | qrspi-implement    |
| `gate.*`          | `gate.presented` (info) · `gate.approved` (pass) · `gate.rejected` (warn)                                                          | deepwork           |
| `child.*`         | `child.dispatched` (info) · `child.returned` (pass\|fail)                                                                          | stage orchestrator |
| `review.*`        | `review.round_started` (info) · `review.round_completed` (pass\|fail)                                                              | stage orchestrator |
| `backward_loop.*` | `backward_loop.requested` (warn) · `backward_loop.decided` (info) · `backward_loop.deferred` (info) · `backward_loop.reset` (warn) | deepwork           |
| other             | `checkpoint.created` (info) · `artifact.generated` (info) · `metrics.generated` (info)                                             | deepwork / any     |

### 4.2 Per-Class Minimum Contracts

**`stage.*`** must include: `stage`, `status`, `summary`, `artifacts` (for completed), `timing`.

**`child.*`** must include: `child_agent`, `correlation_id`, `stage`. `child.returned` must also include `parent_event_id`, `artifacts`, and `context` with at least `{"status": "PASS"|"FAIL"}`.

**`gate.*`** must include: `stage`, `artifacts` (gate artifact path or human-gate artifact). `gate.approved` and `gate.rejected` must include `decision`.

**`backward_loop.*`** must include: `stage`, `phase`, `decision` (for `decided` and `deferred`). `backward_loop.decided` must include `context.loop_target`, `context.deleted_artifacts`, `context.archived_artifacts`.

**`checkpoint.created`** must include: `stage`, `git.message`, `git.commit` (the short SHA if available, otherwise "clean-worktree").

---

## 5. Writing Events (Deepwork Pattern)

Deepwork maintains a `telemetry_seq` integer counter throughout its execution.

**Initialization:**

- Fresh run: set `telemetry_seq = 1`.
- Resumed run: run `cat .pipeline/<run-id>/telemetry/events.jsonl` to read the existing stream. Count the number of lines to determine the current event count. Set `telemetry_seq = count + 1`.

**Emitting an event:**

1. Run `date -u +%Y-%m-%dT%H:%M:%SZ` to capture the current UTC timestamp.
2. Compose the event as a single-line JSON object. Use `telemetry_seq` as `sequence` and `"<run-id>-<telemetry_seq>"` as `event_id`.
3. Run `cat .pipeline/<run-id>/telemetry/events.jsonl` to read the current file content (empty string if the file was just created).
4. Overwrite `.pipeline/<run-id>/telemetry/events.jsonl` with the current content plus the new JSON line appended (one line per event, no blank lines).
5. Increment `telemetry_seq`.

**For `stage.started` / `stage.completed` pairs:** capture the started-at timestamp before dispatch. Capture the ended-at timestamp after receiving the stage return. Compute `duration_s` as the difference in seconds if possible, otherwise omit it.

---

## 6. Stage Agent Telemetry Return Section

Every stage orchestrator appends a `### Telemetry` section to its structured return. This section is a single-line JSON object containing stage-specific metrics. It appears **after `### Summary`** and does not affect existing section parsing.

```
### Telemetry — {"review_rounds": <N>, "gate_status": "approved|rejected|none", "child_calls": <N>, ...}
```

The parent orchestrator (deepwork or a nested orchestrator) reads this line, parses the JSON, and stores it as the `context` payload of the corresponding `stage.completed` or `child.returned` event.

**Standard context fields by stage:**

| Stage           | Telemetry context fields                                                                 |
| --------------- | ---------------------------------------------------------------------------------------- |
| Goals (1)       | `review_rounds`, `gate_status`, `gate_rounds` (rejections before approval)               |
| Questions (2)   | `review_rounds`, `gate_status`, `gate_rounds`                                            |
| Research (3)    | `question_count`, `codebase_count`, `web_count`, `hybrid_count`, `review_rounds`         |
| Design (4)      | `review_rounds`, `gate_status`, `gate_rounds`                                            |
| Structure (5)   | `review_rounds`, `gate_status`, `gate_rounds`                                            |
| Plan (6)        | `task_count`, `review_rounds`, `task_spec_review_rounds` (total across tasks)            |
| Implement (7)   | `wave_count`, `task_count`, `e2e_remediation_rounds`, `regression_remediation_rounds`    |
| Accept-Test (8) | `acceptance_loop_rounds`, `criteria_count`, `criteria_passed`, `backward_loop_requested` |
| Replan (8.5)    | `review_rounds`, `backward_loop_requested`                                               |
| Verify (9)      | `verify_rounds`                                                                          |
| Report (10)     | — (no internal loops)                                                                    |
