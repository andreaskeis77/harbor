# Handoff: T1.5 Source and Project-Source First Slice

Date: 2026-04-07
Status: Green on package baseline
Phase: T1.5

## Scope completed

This tranche adds the first minimal source surface to Harbor.

Delivered:

- global source registry model
- project-source attachment model
- Alembic migration `20260407_0003`
- create/list source API
- attach/list project source API
- local smoke command for the source slice
- source slice tests

## Important design rule

A source is globally identifiable, but its relevance and review posture are project-local.

## Local proof expected

- `python .\tools\task_runner.py smoke-source-slice`
- `python .\tools\task_runner.py quality-gates`
- `python -m alembic upgrade head`
- live API proof for `/api/v1/sources`
- live API proof for `/api/v1/projects/{project_id}/sources`

## Recommended next step

Proceed to T1.6 — Search campaign and review queue baseline.
