# Lessons Learned — H1 Phase 1 Hardening
Stand: 2026-04-11

## Context
An external project review identified that Harbor's functional core was solid but had accumulated silent non-functional gaps: a split migration path, zero application logging, duplicated test fixtures, and a stale configuration file. H1 was inserted as a cross-cutting hardening bolt to close these gaps before further feature work.

## What was found

### 1. Split migration path (P0 — operational break)
`alembic.ini` pointed at `migrations/` while newer OpenAI migrations lived in a separate `alembic/versions/`. Both the dry-run-log migration and the review-queue-extension migration claimed the same `down_revision`, creating an invisible branch conflict. Tests were green because they used `Base.metadata.create_all()` instead of the real Alembic chain — the gap was completely masked.

**Root cause:** The OpenAI migrations were authored in a parallel `alembic/` directory, likely due to a tooling default, and never consolidated back into the canonical `migrations/` path.

**Fix:** Moved both OpenAI migrations to `migrations/versions/`, assigned new sequential revision IDs (`0009`, `0010`), and chained them after the last existing migration (`0008`). Removed the orphaned `alembic/` directory.

### 2. Zero observability
Not a single `import logging` existed in the application code. No request logging, no error correlation, no startup message. In production, a failure would leave no trace.

**Fix:** Introduced `harbor.api.middleware` with structured request logging (method, path, status, duration, request-id) and a global exception handler that returns a traceable `request_id` on unhandled errors.

### 3. Test fixture duplication
11 test files contained identical 15-line fixture blocks. A change to the DB setup pattern required 11 simultaneous edits — a maintainability trap.

**Fix:** Extracted the shared `client` fixture into `tests/conftest.py`. Per-file fixtures are now reserved for genuinely unique setups (like the OpenAI no-DB client).

### 4. Stale configuration artifacts
`config/.env.example` used obsolete key names (`HARBOR_ENV` instead of `HARBOR_ENVIRONMENT`, `HARBOR_DEBUG` which doesn't exist). It was misleading for anyone setting up the system.

**Fix:** Removed `config/.env.example` and the empty `config/` directory. Root `.env.example` is the single canonical source.

## Permanent methodology changes

### Migration integrity is a first-class test
Every `pytest` run now validates:
- `alembic upgrade head` creates all expected tables
- the migration chain is linear (single head, single base)
- Alembic-created tables match ORM model definitions

This prevents the specific class of bug where tests pass via `create_all()` while the real migration chain is broken.

### Observability is not optional, even for local systems
Even a single-operator local system needs request logs and error traces. The debugging cost of silence far exceeds the implementation cost of structured logging. This is now a manifest rule.

### Test infrastructure is shared infrastructure
The established harness rule from T4.5A now has concrete infrastructure: `conftest.py` provides the canonical DB-backed client. New test files extend this rather than copying it.

## What this hardening bolt did NOT change
- No new features, routes, or domain logic
- No changes to the OpenAI adapter behavior
- No changes to the operator web shell
- No changes to the chat surface
- No schema changes (migration content is identical, only location and chain order changed)

## Continuous improvement protocol
This is the second lessons-learned document in Harbor (after T4.5A). The pattern is now established:
1. Every bolt produces a lessons-learned document if it surfaces new methodology insights
2. Permanent changes are reflected in `ENGINEERING_MANIFEST.md`
3. The validation protocol is updated if new validation categories emerge
4. The next bolt inherits these rules automatically

## Confirmed outcome
H1 is locally green on branch `bolt/t4-5a-project-source-grounded-chat-baseline-v2`:
- 59 tests pass (including 3 new migration integrity tests, 4 new middleware tests)
- quality-gates green (compileall, ruff, pytest)
- migration chain verified: 10 migrations, single head, single base, all ORM tables present
