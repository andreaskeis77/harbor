# Project State — Harbor

## Current phase

T1.2 — Persistence foundation and Postgres baseline

## Confirmed completed

- A0 accepted baseline
- T1.0 repository scaffold and runtime bootstrap
- T1.1 runtime configuration and local operator surface
- T1.2 persistence foundation and Postgres baseline

## Current runtime posture

Harbor now has:

- FastAPI bootstrap runtime
- runtime settings loaded through `.env` / environment variables
- local operator commands through `tools/task_runner.py`
- persistence package boundary under `src/harbor/persistence/`
- SQLAlchemy base and session bootstrap
- optional Postgres configuration and connectivity check
- `/healthz`, `/runtime`, and `/db/status` endpoints
- local quality gates and smoke checks

## Current persistence posture

The persistence layer is intentionally still minimal.

It now includes:

- typed Postgres configuration in runtime settings
- redacted connection visibility
- SQLAlchemy engine factory
- session factory boundary
- declarative base
- lightweight DB status service
- Alembic baseline scaffolding

It does **not** yet include:

- Harbor domain tables
- project persistence
- handbook persistence
- source persistence
- pgvector usage in runtime logic

## Current release posture

Local runtime and local operator surface are green.

The current next step is to build the first real persistence-backed Harbor domain slice on top of the new baseline.

## Recommended next step

T1.3 — Project registry vertical slice
