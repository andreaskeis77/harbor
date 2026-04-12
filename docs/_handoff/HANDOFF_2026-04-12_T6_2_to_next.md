# Handoff: T6.2 to next phase

**Date**: 2026-04-12 (same calendar day as the prior session; second sitting)
**From session**: T6.1 through T6.2 (4 bolts this sitting)
**Branch**: `main` (all merged)
**Last PR**: #47 (T6.2)

---

## Session delivery summary

| Bolt  | PR  | Title                                                                |
|-------|-----|----------------------------------------------------------------------|
| T6.1  | #44 | Instrument `propose-source` through automation task observer         |
| C.3   | #45 | Unified toast/status primitive replaces scattered inline mounts      |
| C.4   | #46 | Cross-project pending-actions queue (API + operator page)            |
| T6.2  | #47 | Workflow-summary snapshot as first non-mutating automation driver    |

All four bolts followed the Validation Protocol: branch → implement → targeted tests → quality gates → docs → commit → push → PR → merge.

---

## Confirmed current state

- **186 tests, 96% coverage** (70% gate enforced; +14 tests across the four bolts)
- **12 Alembic migrations** (unchanged — no new tables this sitting)
- **53 API endpoints** (+2: `/api/v1/pending-actions`, `/api/v1/projects/{project_id}/snapshot-summary`)
- **12 ORM models** (unchanged)
- **3 static asset files**; toast container rendered globally from `_render_document`
- **Observer pattern now validated on three call-sites**: `draft-handbook`, `propose-source`, `snapshot_workflow_summary`
- **Quality gates**: compileall + ruff (9 rule sets) + pytest with coverage — all green

---

## Architecture developments this sitting

### Observer at N=3 — the abstraction still does not pay for itself
Every one of the three instrumented call-sites uses the same four-step shape:

1. validate project → 404 before observer start, no orphan rows
2. `start_automation_task_observer` → side-channel, returns `task_id`
3. `try: <work on request session>` → on success: `mark_automation_task_succeeded` on the same request session
4. `except: session.rollback(); fail_automation_task_observer(task_id, ...); raise`

Three near-identical try/except blocks. The honest call is: the pattern is recognizable enough that a future dispatcher-shaped helper will probably make sense — but not yet. The decision threshold is:

- **Don't refactor at N=3** — three call-sites can share a pattern without sharing code. Manifest rule: "three similar lines is better than a premature abstraction."
- **Refactor at N=4 or when a caller *cannot* follow the shape** — e.g., when a scheduled handler runs outside a request session, the existing `session.rollback()` step becomes meaningless and the shape will need to split anyway.

### Toast primitive replaces the inline-mount pattern, not just "adds to it"
The important design decision in C.3 was to **remove** the five inline `<p class="status info">` mounts rather than keep them around for progress messages. Keeping two mechanisms side-by-side would have been a "unified" feature in name only. The compatibility shim lives entirely inside `setStatus` — it reroutes its arguments to `showToast` and ignores the mount id. All ~20 existing call-sites migrated without touching them.

### Cross-project aggregation surface is a general shape
`/api/v1/pending-actions` is the first endpoint that cuts across projects. The shape (`list_<entity>_across_projects` + joined `ProjectRecord` + enriched read model with `project_title`) is a good template for future cross-project views (stale sources, dormant campaigns, handbook-drift summary).

### First non-mutating automation driver
T6.2's `snapshot_workflow_summary` is deliberately observational: it reads existing state, serializes it, and records the serialization as the task's `result_summary`. No domain mutation. This is the shape a periodic scheduler will target — so when T6.3+ introduces scheduling, the handlers will already exist in the right shape.

### Key files touched this session

| File                                             | Role                                                                    |
|--------------------------------------------------|-------------------------------------------------------------------------|
| `src/harbor/api/routes/openai_adapter.py`        | `propose-source` instrumented through observer (T6.1)                   |
| `src/harbor/static/operator.js`                  | `showToast` primitive; `setStatus` rewired; pending-actions renderer    |
| `src/harbor/static/operator.css`                 | Toast stack styles + animations                                         |
| `src/harbor/api/routes/operator_web.py`          | Toast container in `_render_document`; pending-actions page; mounts gone |
| `src/harbor/review_queue_registry.py`            | `list_pending_actions` + `PendingActionRead` + `PENDING_REVIEW_QUEUE_STATUSES` |
| `src/harbor/api/routes/review_queue.py`          | `GET /pending-actions` endpoint                                         |
| `src/harbor/api/routes/workflow_summary.py`      | `POST /snapshot-summary` endpoint; counts JSON serializer               |
| `tests/test_automation_task_registry_api.py`     | +3 tests for propose-source observer                                    |
| `tests/test_operator_web_shell.py`               | Toast container, retired-mount absence, pending-actions page, JS markers |
| `tests/test_pending_actions_api.py`              | New file, 3 aggregation tests                                            |
| `tests/test_snapshot_summary_api.py`             | New file, 3 observer-driver tests                                       |

---

## Candidate next steps

### Option A: T6.3 — second non-mutating driver
Introduce one more observational task kind so the dispatcher abstraction is justified by two real needs, not speculation. Good candidate: `handbook_freshness_check` (computes days-since-last-handbook-version + unreviewed-source count + writes result_summary). Same observer shape. Prepares the ground for T6.4.

### Option B: T6.4 — minimal scheduler primitive
Only sensible once at least two non-mutating handlers exist (see Option A). Smallest honest scheduler: a cron-like config table + a startup-triggered in-process scheduler that invokes the existing endpoints. Requires migration + background task discipline.

### Option C: C.5 — automation task filter/search controls
C.2 surfaces the task log; with three task kinds now, filtering by `task_kind` and `status` becomes ergonomic. Pure UI bolt, no backend churn.

### Recommended path
**C.5 first**, then **T6.3**, then **T6.4**.

Rationale:
- C.5 is cheap and removes operator friction *now* that there are three kinds.
- T6.3 should come before T6.4 — scheduling infrastructure built on one handler is speculation; built on two is engineering.
- Resisting the urge to jump to T6.4 keeps the observer/driver abstraction honest.

---

## Validation commands

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_pending_actions_api.py tests/test_snapshot_summary_api.py tests/test_automation_task_registry_api.py tests/test_operator_web_shell.py -q
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py smoke-operator-web-shell-slice
python .\tools\task_runner.py smoke-openai-chat-session-slice
```

---

## Lessons reinforced this sitting

1. **At N=3 call-sites, don't refactor to a dispatcher.** Three try/except observers are fine. Wait until N=4 or until a caller genuinely cannot fit the shape (e.g., runs outside a request session).
2. **"Unified" means remove the old mechanism, not coexist with it.** C.3 deleted five inline mounts; the compatibility shim is one wrapper function, not a dual-system migration.
3. **Non-mutating tasks are legitimate automation targets.** T6.2 proves the observer works without any domain write — exactly the shape a scheduler will trigger.
4. **Cross-project surfaces follow a template.** Joined query + enriched read model + filter constant. The shape will repeat for stale-sources, dormant-campaigns, etc.
5. **`session.rollback()` before the side-channel fail-observer is load-bearing on SQLite.** Without it the observer deadlocks on the writer lock. Preserved verbatim across all three call-sites.

---

## Prompt for the new chat

Paste this into the new chat to prime context:

> Ich arbeite am Harbor-Projekt (projekt-partitioniertes Research-System, FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + pytest). Das lokale Repo liegt unter `C:\projekte\Harbor`; `main` ist canonical baseline. Wir folgen dem Harbor Engineering Manifest und dem Validation Protocol.
>
> Letzte Session (2026-04-12, zweites Sitting) hat 4 Bolts gemerged: T6.1, C.3, C.4, T6.2 (PRs #44–#47). Stand jetzt: 186 tests, 96% coverage, 12 migrations, 53 endpoints, Observer-Pattern auf 3 Call-Sites validiert, unified toast primitive live, cross-project pending-actions queue live, erster non-mutating automation driver (`snapshot_workflow_summary`) live.
>
> Start-Lesereihenfolge:
> 1. `docs/_handoff/HANDOFF_2026-04-12_T6_2_to_next.md`
> 2. `docs/_handoff/HANDOFF_2026-04-12_T6_0B_to_next.md` (prior handoff)
> 3. `docs/PROJECT_STATE.md`
> 4. `docs/STRATEGY_ROADMAP_v0_1.md`
> 5. `docs/MASTERPLAN.md`, `docs/WORKING_AGREEMENT.md`, `docs/VALIDATION_PROTOCOL.md`
>
> Offene Optionen für den nächsten Bolt (Empfehlung: C.5 → T6.3 → T6.4):
> - **C.5** — automation task filter/search controls in der C.2 Task-Log-Panel
> - **T6.3** — zweiter non-mutating automation handler (z. B. handbook-freshness check)
> - **T6.4** — minimal scheduler primitive (nur sinnvoll nach T6.3)
>
> Bitte lies zuerst den Handoff und bestätige dann, welchen Bolt wir als nächstes anpacken. Keine Implementierung ohne Discussed → Prepared → Applied → Validated → Accepted.

---

## Key metrics

| Metric                       | Before sitting | After sitting |
|------------------------------|----------------|---------------|
| Tests                        | 172            | 186 (+14)     |
| Coverage                     | 96%            | 96%           |
| Migrations                   | 12             | 12            |
| Endpoints                    | 51             | 53 (+2)       |
| ORM models                   | 12             | 12            |
| Observer call-sites          | 1              | 3             |
| Bolts merged this sitting    | —              | 4 (#44–#47)   |
