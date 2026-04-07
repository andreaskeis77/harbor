# Harbor Project State

Status date: 2026-04-07  
Current phase: **T1.1 — Runtime configuration and local operator surface**

## 1. Current accepted baseline

The Harbor project has completed and accepted the A0 definition and architecture phase.

In addition, T1.0 is now technically validated with:

- repository scaffold in place
- Python package layout in place
- FastAPI bootstrap runtime in place
- `/healthz` and `/` endpoints working locally
- local quality gates green
- local test baseline green

## 2. What T1.1 adds

T1.1 sharpens the runtime and local operator posture without yet introducing domain persistence.

This tranche adds:

- typed runtime settings
- `.env`-driven configuration
- canonical local runtime directory handling
- local operator commands
- explicit local smoke path
- clearer local development command surface

## 3. Current runtime posture

Current local runtime posture:

- FastAPI application under `src/harbor/app.py`
- settings under `src/harbor/config.py`
- runtime utilities under `src/harbor/runtime.py`
- local operator surface under `src/harbor/operator_surface.py`
- quality gates via `tools/run_quality_gates.py`
- task runner via `tools/task_runner.py`

## 4. What is explicitly not in T1.1

Still intentionally deferred:

- Postgres connection layer
- schema migrations
- project persistence
- project API surface
- source ingest
- web dashboard
- Custom GPT action layer
- VPS deployment

## 5. Recommended next step

**T1.2 — Persistence foundation and Postgres baseline**

That next tranche should introduce:

- database settings boundary
- Postgres connection/session baseline
- first schema/migration posture
- explicit persistence bootstrap tests
- no product domain endpoints yet beyond what is necessary for persistence readiness
