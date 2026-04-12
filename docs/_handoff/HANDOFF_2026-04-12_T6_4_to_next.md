# Handoff: T6.4 to next phase

**Date**: 2026-04-12 (third sitting of the day)
**From session**: C.5 → T6.3 → T6.4 (3 bolts this sitting)
**Branch**: `main` (all merged)
**Last PR**: #50 (T6.4)

---

## Session delivery summary

| Bolt  | PR  | Title                                                                |
|-------|-----|----------------------------------------------------------------------|
| C.5   | #48 | Automation task filter controls on project-detail (kind + status)    |
| T6.3  | #49 | `handbook_freshness_check` — second non-mutating automation driver   |
| T6.4  | #50 | Minimal scheduler primitive (table + handler registry + tick)        |

All three followed the Validation Protocol: branch → implement → targeted tests → quality gates → docs → commit → push → PR → merge.

---

## Confirmed current state

- **201 tests, 96% coverage** (70% gate enforced; +15 tests across the three bolts)
- **13 Alembic migrations** (+1: `20260412_0013_add_automation_schedule`)
- **58 API endpoints** (+5: freshness endpoint, scheduler list/put/patch/tick)
- **13 ORM models** (+1: `AutomationScheduleRecord`)
- **3 static asset files** (C.5 enlarged operator.js filter logic + operator.css filter-bar styles)
- **Observer pattern now validated on five call-sites**: `draft-handbook`, `propose-source`, `snapshot_workflow_summary`, `handbook_freshness_check`, scheduler-driven runs (dispatched via `SCHEDULE_HANDLERS`)
- **Quality gates**: compileall + ruff (9 rule sets) + pytest with coverage — all green

---

## Architecture developments this sitting

### The dispatcher finally pays (N=2 non-mutating handlers)
T6.4 introduced `SCHEDULE_HANDLERS: dict[str, Callable[[Session, str], str]]` — resisted in T6.3 per the N=3 rule, honest at N=2 with a real second caller (the scheduler) that cannot use the route shape. Existing routes (`snapshot-summary`, `check-handbook-freshness`) still use their inline try/except observer shape. That is correct: refactoring them under the dispatcher before a third caller needs it would be speculation. The dispatcher lives next to the scheduler because *the scheduler* is the second caller.

### Scheduler is intentionally externally-triggered
No background thread, no APScheduler, no in-process clock. The tick is a `POST /api/v1/scheduler/tick` endpoint. Cadence is a deployment concern (cron, K8s CronJob, Windows Task Scheduler) — not a runtime concern. This avoids:
- Interaction between uvicorn workers and scheduled loops
- Lifecycle/shutdown fragility
- SQLite writer-lock contention between a background loop and request threads

When Harbor grows to a real async scheduler, this endpoint becomes the thing the scheduler calls. The contract stays.

### SQLite writer-lock discipline (third confirmation)
T6.0B forced `session.rollback()` before side-channel fail-observer. T6.4 adds the symmetric rule for the **success** path in a multi-iteration loop: `session.commit()` after `mark_automation_task_succeeded` so the request session releases the writer lock before the *next* iteration's `start_automation_task_observer` tries to acquire it. Without the commit, iteration 2 deadlocks on SQLite.

This is now a load-bearing pattern documented in `src/harbor/scheduler.py:execute_scheduled_handler`. Any future batch-processing call-site that mixes request-session writes with side-channel observer writes needs the same discipline.

### Per-project failure isolation in the tick
`scheduler_tick` catches exceptions per `(schedule, project)` pair. The observer has already rolled back and recorded the failure via the side-channel session before the exception propagates, so the caught exception is safe to swallow into the tick's `runs` list. This keeps the tick live: one broken project does not block the rest.

### Filter UX is pure client-side, localStorage-persisted
C.5's filter state lives entirely in the browser (`harbor.operator.automation-tasks.filters`). No new backend query param, no pagination plumbing. Works because the current task list fetches all rows per project; when per-project task counts grow large, server-side filtering becomes cheaper than client-side, and the `data-automation-tasks-filter` markers make that upgrade mechanical.

### Key files touched this session

| File                                                      | Role                                                              |
|-----------------------------------------------------------|-------------------------------------------------------------------|
| `src/harbor/static/operator.js`                           | Filter primitives, localStorage persistence, stale-value reset    |
| `src/harbor/static/operator.css`                          | `.filter-bar` styles                                              |
| `src/harbor/api/routes/operator_web.py`                   | Filter-bar HTML in automation-tasks section                       |
| `src/harbor/handbook_registry.py`                         | `compute_handbook_freshness(session, project_id)` pure helper     |
| `src/harbor/api/routes/handbook_freshness.py`             | T6.3 endpoint; observer pattern (T6.2 shape)                      |
| `src/harbor/persistence/models.py`                        | `AutomationScheduleRecord`                                        |
| `migrations/versions/20260412_0013_add_automation_schedule.py` | Schedule table migration                                     |
| `src/harbor/scheduler.py`                                 | `SCHEDULE_HANDLERS` dispatcher + registry + `scheduler_tick`      |
| `src/harbor/api/routes/scheduler.py`                      | GET / PUT / PATCH / POST-tick routes                              |
| `tests/test_handbook_freshness_api.py`                    | +4 tests                                                          |
| `tests/test_scheduler_api.py`                             | +9 tests                                                          |
| `tests/test_operator_web_shell.py`                        | +2 tests for C.5 filter markers + JS primitives                   |

---

## Candidate next steps

### Option A: C.6 — operator UX for the scheduler surface
Expose the scheduler on `/operator/scheduler` (or a panel on the projects page): list schedules, toggle enabled, edit interval, one-click tick. Pure UI bolt; contract is already stable.

### Option B: T6.5 — first genuinely project-less automation driver
Everything so far is per-project. A cross-project driver (e.g. `stale_source_sweep` that ranks sources project-agnostically, or `dormant_project_report`) would exercise the `project_id=None` path of `AutomationTaskRecord` and force the tick's project-iteration assumption to be questioned.

### Option C: C.7 — surface scheduler tick outcomes on the operator UI
The tick returns a rich `runs` array. Right now nothing shows it. An operator panel that displays the last tick's outcomes (succeeded / failed / skipped) would close the loop. Depends on (A) or stands alone.

### Recommended path
**C.6 first** (operator needs to see and control schedules), then **T6.5** (genuinely cross-project driver forces honest scheduler-shape re-evaluation), then **C.7** (outcomes surface) if still needed.

Rationale: a scheduler with no operator surface is an invisible cron — operators cannot trust what they cannot see. Once the surface is live, a project-less driver will reveal whether `scheduler_tick`'s "fan out across all projects" assumption needs to split.

---

## Validation commands

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_handbook_freshness_api.py tests/test_scheduler_api.py tests/test_operator_web_shell.py -q
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py smoke-operator-web-shell-slice
python .\tools\task_runner.py smoke-openai-chat-session-slice
```

---

## Lessons reinforced this sitting

1. **At N=2 real callers, the dispatcher pays — earlier than N=3.** T6.3 correctly resisted extraction at one route. T6.4's scheduler is a *second kind* of caller (batch loop, not one-shot request), so `SCHEDULE_HANDLERS` is justified. Heuristic: the N-threshold drops when the second caller cannot share the shape of the first.
2. **SQLite writer-lock discipline now has a symmetric success-path rule.** Commit after `mark_succeeded` in any multi-iteration loop that mixes request-session writes with side-channel observer writes. Documented inline in `execute_scheduled_handler`.
3. **Externally-triggered schedulers are honest until they aren't.** No background thread means no lifecycle complexity — *until* the deployment actually needs sub-minute ticks with guaranteed execution. The contract (a POST endpoint) survives the upgrade to any in-process scheduler later.
4. **Per-iteration failure catch is a deliberate product choice.** The tick swallows per-project exceptions because the observer has already persisted the failure. A fail-fast tick would be hostile to operators who expect "scheduled runs keep going."
5. **Client-side filter UX is fine until it isn't.** C.5 is intentionally client-side; the data attributes are the upgrade path to server-side filtering.

---

## Prompt for the new chat

Paste this into the new chat to prime context:

> Ich arbeite am Harbor-Projekt (projekt-partitioniertes Research-System, FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + pytest). Das lokale Repo liegt unter `C:\projekte\Harbor`; `main` ist canonical baseline. Wir folgen dem Harbor Engineering Manifest und dem Validation Protocol.
>
> Letzte Session (2026-04-12, drittes Sitting) hat 3 Bolts gemerged: C.5, T6.3, T6.4 (PRs #48–#50). Stand jetzt: **201 tests, 96% coverage, 13 migrations, 58 endpoints, 13 ORM models**. Observer-Pattern auf 5 Call-Sites (inkl. Scheduler-Dispatcher mit `SCHEDULE_HANDLERS`). Minimaler Scheduler-Primitive live (`automation_schedule` Tabelle + `POST /api/v1/scheduler/tick`, kein Background-Thread — externally triggered).
>
> Start-Lesereihenfolge:
> 1. `docs/_handoff/HANDOFF_2026-04-12_T6_4_to_next.md` (dieser Handoff)
> 2. `docs/_handoff/HANDOFF_2026-04-12_T6_2_to_next.md` (prior handoff)
> 3. `docs/PROJECT_STATE.md`
> 4. `docs/STRATEGY_ROADMAP_v0_1.md`
> 5. `docs/MASTERPLAN.md`, `docs/WORKING_AGREEMENT.md`, `docs/VALIDATION_PROTOCOL.md`
>
> Offene Optionen für den nächsten Bolt (Empfehlung: C.6 → T6.5 → C.7):
> - **C.6** — operator UX für Scheduler (Liste, enable/disable, interval, one-click tick)
> - **T6.5** — erster genuinely project-less automation driver (z. B. `stale_source_sweep` oder `dormant_project_report`) — fordert die Fan-out-Annahme des Ticks heraus
> - **C.7** — letzte Tick-Outcomes im Operator UI sichtbar machen
>
> Bitte lies zuerst den Handoff und bestätige dann, welchen Bolt wir als nächstes anpacken. Keine Implementierung ohne Discussed → Prepared → Applied → Validated → Accepted.

---

## Key metrics

| Metric                       | Before sitting | After sitting |
|------------------------------|----------------|---------------|
| Tests                        | 186            | 201 (+15)     |
| Coverage                     | 96%            | 96%           |
| Migrations                   | 12             | 13 (+1)       |
| Endpoints                    | 53             | 58 (+5)       |
| ORM models                   | 12             | 13 (+1)       |
| Observer call-sites          | 3              | 5             |
| Non-mutating automation drivers | 1           | 2             |
| Scheduler primitive          | —              | live (externally-triggered tick) |
| Bolts merged this sitting    | —              | 3 (#48–#50)   |
