# Harbor Engineering Manifest v0.1

## Purpose

This manifest defines the engineering rules for Harbor.

Harbor is treated as a long-lived, operable, research system rather than an ad hoc prototype.

## Priority order

1. Correctness
2. Traceability
3. Operability
4. Maintainability
5. Testability
6. Delivery speed
7. Cleverness

## Core rules

### Small controlled bolts
Work is delivered in small, understandable tranches.

### One canonical backend
Website and Custom GPT must use the same backend.

### Docs are part of the system
If the docs are outdated, the system is degraded.

### No blind trust in AI output
AI-generated code or structure is untrusted until reviewed and validated.

### Honest state handling
Prepared is not the same as validated.
Accepted is not the same as merely discussed.

### Health and evidence first
Runtime work must establish health, logs, and repeatable commands early.

## Delivery rule

Repo updates should be delivered as complete file packages, preferably as flat-root ZIP artifacts for controlled application on the DEV-LAPTOP.

## Definition of done for a bolt

A bolt is done only when:
- purpose is clear
- files are consistent
- checks are run
- docs are updated
- project state is updated
- next step is explicit

## 2026-04-10 additions

### Artifact integrity over incremental improvisation
A generated delivery artifact must either contain every touched repository file or provide one deterministic apply script that writes every touched repository file. Partial artifacts are treated as invalid.

### Contract-preserving changes
If a feature spans route, builder, and tests, the bolt must update those layers coherently. It is not acceptable to patch one layer and infer the rest.

### Root-cause analysis before the next artifact
If an artifact fails in apply, import, test, smoke, or quality-gates, Harbor work returns to a verified clean base before another artifact is produced. No patching on top of a broken artifact.

### Use the established harness
New tests should extend the existing fixture and fake-client harness for the surface under change instead of inventing an ad hoc host.

## 2026-04-11 additions — Phase 1 hardening

### Migration chain integrity
The Alembic migration chain must remain linear and complete. Every `alembic upgrade head` against an empty database must produce all tables the ORM models define. This is validated by an automated test.

### Observability from day one
Every Harbor runtime must produce structured request logs. Unhandled exceptions must return a traceable `request_id` and log full context. Silence is not an acceptable failure mode.

### Single source of configuration
There must be exactly one `.env.example` at the repository root. Duplicate or legacy configuration files are treated as defects.

### Test fixtures are shared infrastructure
Shared fixtures live in `tests/conftest.py`. Per-file fixture duplication is treated as a maintainability defect. New tests extend `conftest.py` rather than defining their own client setup.

## 2026-04-11 additions — Phase 2 hardening

### Typed domain exceptions over string-based error matching
All domain errors must be expressed as typed exception classes (subclasses of `HarborError`). Route handlers must not catch `KeyError`/`ValueError` and translate them to `HTTPException`. Middleware exception handlers map domain types to HTTP status codes centrally.

### Request-scoped transaction boundary
Database sessions follow a commit-on-success / rollback-on-error pattern owned by the FastAPI dependency (`get_db_session`). Registry functions use `session.flush()` to obtain server-generated defaults; they must never call `session.commit()`. This ensures multi-step operations are atomic.

### Coverage quality gate
`pytest-cov` enforces a minimum coverage threshold (currently 60%) on every test run. The threshold is defined in `pyproject.toml` and applies automatically via `addopts`.

### No HTTPException in route handlers
Route files must not import or raise `HTTPException`. All error signalling uses the typed domain exception hierarchy. The only place HTTP status codes are assigned is in middleware exception handlers.

## 2026-04-11 additions — Phase 3 hardening

### Coverage excludes CLI-only surfaces
Operator CLI surfaces (`operator_surface.py`, `openai_operator_surface.py`) are excluded from coverage measurement because they are interactive CLI tools, not API code. The coverage gate applies to the API and domain layer only.

### Logging configuration must not disable application loggers
Alembic's `fileConfig()` must be called with `disable_existing_loggers=False`. Without this, alembic migration runs silently disable all Harbor loggers for the rest of the process.

### Error paths must be tested
Every exception handler registered in middleware must have a corresponding test that verifies the HTTP status code and response body. Untested error paths are treated as unverified behavior.

### Expanded lint rules are permanent
The expanded Ruff rule set (`E, F, I, B, UP, SIM, PIE, LOG, RUF`) is the baseline. New code must pass all rules. Regressions to a narrower rule set require justification.

## 2026-04-11 additions — Phase 4 hardening

### Validation edge cases must be tested at the registry boundary
Every validation branch in a registry function (entity-not-found, cross-entity ownership mismatch, lineage integrity) must have a corresponding API-level test that triggers the specific branch and asserts the correct HTTP status code.

### Input validation is tested at the API boundary
Pydantic `Field` constraints (`min_length`, `max_length`, `ge`) are tested through API calls, not unit tests on models. This ensures the full FastAPI validation pipeline (parsing, constraint checking, 422 response) is exercised.

### E2E workflow lifecycle tests verify state transitions
At least one test must exercise the full research workflow (project → campaign → run → candidate → review → source) in a single test, verifying disposition transitions, lineage integrity, and duplicate-guard behavior at every stage.

### Coverage gate tracks forward progress
The coverage threshold is raised with each hardening phase as new tests close gaps. The threshold must never regress. Current minimum: 70%, effective: 96%.
