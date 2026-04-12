# Handoff: T6.0B to next phase

**Date**: 2026-04-12
**From session**: H5.0A through T6.0B (9 bolts in one session)
**Branch**: `main` (all merged)
**Last PR**: #43 (T6.0B)

---

## Session delivery summary

Nine sequential bolts merged to `main`:

| Bolt | PR | Title |
|------|----|-------|
| H5.0A | #35 | Source-review workflow in operator web shell |
| H5.0B | #36 | Handbook version history surface in operator web shell |
| H5.1A | #37 | Extract BASE_SCRIPT → `src/harbor/static/operator.js` |
| H5.1B | #38 | Extract CHAT_SCRIPT → `src/harbor/static/chat.js` |
| H5.1C | #39 | Extract BASE_CSS → `src/harbor/static/operator.css` |
| T6.0A | #40 | Automation task registry (observability baseline) |
| C.1   | #41 | Collapsible operator section-cards (localStorage-persisted) |
| C.2   | #42 | Automation task log panel on project-detail |
| T6.0B | #43 | Side-channel observer — failures survive rollback |

All bolts followed the Harbor Validation Protocol: branch → implement → targeted tests → quality gates → docs → commit → push → PR → merge.

---

## Confirmed current state

- **172 tests, 96% coverage** (70% gate enforced; +37 tests this session)
- **12 Alembic migrations** (linear chain, integrity-tested; `automation_task_registry` added)
- **51 API endpoints** (+2 read-only automation task endpoints)
- **12 ORM models** (`AutomationTaskRecord` added)
- **3 static asset files** under `src/harbor/static/`: `operator.js`, `chat.js`, `operator.css`
- **24 engineering manifest rules**
- **Quality gates**: compileall + ruff (9 rule sets) + pytest with coverage — all green

---

## What this session delivered (the full arc)

### H5 — T5 hardening (complete)
- H5.0A/B: operator web shell gained source-review workflow and handbook version history
- H5.1A/B/C: ~4000 lines of embedded HTML/CSS/JS extracted to dedicated static assets; subsequent UI bolts became focused edits in three files instead of one monolith

### T6.0A/B — automation observability baseline
- **T6.0A**: `automation_task_registry` (registry + migration + API + `draft-handbook` as first instrumented call-site). State machine: `pending → running → succeeded|failed`. Shipped with an explicit limitation: failures inside the request transaction would not be recorded if the transaction rolled back.
- **T6.0B**: closed that gap with a **side-channel observer pattern**:
  - `start_automation_task_observer` — uses a dedicated session; records `running` atomically
  - request session handles the actual work; on success calls `mark_automation_task_succeeded` on the **same** session (single-writer-safe)
  - on failure: `session.rollback()` (releases SQLite write lock) → `fail_automation_task_observer` on a dedicated session persists the failure even though the main transaction rolled back
  - SQLite `connect_args` gained `timeout=5.0` as a defensive default

### C.1/C.2 — UX consolidation (partial)
- C.1: all 14 operator section-cards collapsible; per-operator localStorage persistence under `harbor.operator.section.<key>`
- C.2: new automation task log panel on project-detail (kind / trigger / status / timestamps / result-or-error badges) — makes T6.0A visible end-to-end

---

## Architecture context

### Side-channel observer pattern

Key insight: observer responsibilities split along **session boundaries**, not database-engine boundaries.

| Transition | Session | Why |
|------------|---------|-----|
| start → running | side-channel (dedicated) | Must persist even if caller fails before writing anything |
| running → succeeded | request session | Request session already holds the write lock; single-writer-safe |
| running → failed | side-channel (after request rollback) | Request session's write lock must be released first; otherwise deadlock |

This generalizes beyond SQLite: in Postgres MVCC hides the deadlock symptom, but the honest coupling (observer visibility bounded by session commit points) remains.

### Key files touched this session

| File | Role |
|------|------|
| `src/harbor/automation_task_registry.py` | Registry + observer helpers |
| `src/harbor/api/routes/openai_adapter.py` | `draft-handbook` instrumented through observer |
| `src/harbor/api/routes/operator_web.py` | Section-card `data-section-key`, automation tasks panel, handbook-version-history, source-review surfaces |
| `src/harbor/static/operator.js` | `initSectionCollapsibles`, `renderAutomationTasks`, review/handbook renderers |
| `src/harbor/static/chat.js` | Extracted from CHAT_SCRIPT |
| `src/harbor/static/operator.css` | Extracted BASE_CSS + collapsibles + status badges |
| `src/harbor/persistence/session.py` | SQLite `timeout=5.0` |
| `migrations/versions/*_automation_task_registry.py` | New migration |
| `tests/test_automation_task_registry_{unit,api}.py` | 37 new tests, includes observer coverage |

---

## Candidate next steps

### Option A: T6.1 — second call-site
Instrument `propose-source` from chat through the observer to prove the pattern generalizes beyond `draft-handbook`. Small (single call-site), validates the registry + observer shape on a second real flow, unlocks confidence for T6.2+ (actual automation drivers).

### Option B: C.3 — unified status/toast feedback
Replace scattered `data-*-status` mounts in operator.js with one unified status/toast mechanism. Reduces accumulated UX debt before adding more operator actions.

### Option C: C.4 — review queue as central pending-actions view
Surface all pending review items (candidates, sources, handbook drafts) in one consolidated queue instead of per-project discovery.

### Recommended path
**T6.1 first** — it's the smallest bolt that validates the most recent architectural decision (observer pattern). C.3/C.4 are worthwhile but don't validate new architecture; they're UX tidying and can follow.

---

## Validation commands

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_automation_task_registry_unit.py tests/test_automation_task_registry_api.py -q
python .\tools\task_runner.py quality-gates
python .\tools\task_runner.py smoke-operator-web-shell-slice
python .\tools\task_runner.py smoke-openai-chat-session-slice
```

---

## Lessons learned

See `docs/LESSONS_LEARNED_2026-04-12_H5_T6_C_session.md` for the full analysis. Key reinforced rules:

1. Ship observability before automation — T6.0A is a Task Log, nothing more, and that's what lets T6.1+ be safe.
2. Keep one concern per bolt even when bundling feels faster.
3. Don't hide limitations — write them into the next bolt's scope (T6.0A docstring → T6.0B PR body).
4. Default to editing static files, not generating them from Python strings.
5. Writer locks are a property of the session, not the database — observer patterns must respect session boundaries.

---

## Prompt for the new chat

Paste this into the new chat to prime context:

> Ich arbeite am Harbor-Projekt (projekt-partitioniertes Research-System, FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic + pytest). Das lokale Repo liegt unter `C:\projekte\Harbor` und `main` ist der canonical baseline. Wir folgen dem Harbor Engineering Manifest und dem Validation Protocol: kleine, single-concern Bolts; jeder Bolt = branch → implement → targeted tests → `python .\tools\task_runner.py quality-gates` → docs → commit → push → PR → merge.
>
> Letzte Session (2026-04-12) hat 9 Bolts gemerged: H5.0A/B, H5.1A/B/C, T6.0A, C.1, C.2, T6.0B (PRs #35–#43). Stand jetzt: 172 tests, 96% coverage, 12 migrations, 51 endpoints, 12 ORM models, static assets extrahiert (`operator.js`, `chat.js`, `operator.css`), automation task registry + side-channel observer pattern live.
>
> Start-Lesereihenfolge:
> 1. `docs/_handoff/HANDOFF_2026-04-12_T6_0B_to_next.md`
> 2. `docs/LESSONS_LEARNED_2026-04-12_H5_T6_C_session.md`
> 3. `docs/PROJECT_STATE.md`
> 4. `docs/STRATEGY_ROADMAP_v0_1.md`
> 5. `docs/MASTERPLAN.md`, `docs/WORKING_AGREEMENT.md`, `docs/VALIDATION_PROTOCOL.md`
>
> Offene Optionen für den nächsten Bolt (Empfehlung: T6.1):
> - **T6.1** — `propose-source` aus dem Chat durch den Observer instrumentieren (validiert das T6.0B-Pattern auf einem zweiten Call-Site)
> - **C.3** — unified status/toast feedback (ersetzt verstreute `data-*-status` mounts)
> - **C.4** — review queue als zentrale pending-actions view
>
> Bitte lies zuerst den Handoff und bestätige dann, welchen Bolt wir als nächstes anpacken. Keine Implementierung ohne Discussed → Prepared → Applied → Validated → Accepted.

---

## Key metrics

| Metric | Value |
|--------|-------|
| Tests | 172 (+37 this session) |
| Coverage | 96% |
| Migrations | 12 |
| Endpoints | 51 (+2) |
| ORM models | 12 (+1) |
| Static asset files | 3 (new) |
| Bolts merged this session | 9 (#35–#43) |
| Engineering rules | 24 |
