# Harbor Masterplan

## Product direction

Harbor is a project-partitioned research operating system, not a generic chat-RAG.

The sequence stays:

- A0 — accepted product / architecture / governance baseline
- T1 — local technical bootstrap and first vertical slices
- T2 — broader research workflow surface
- T3 — VPS preview/runtime stabilization
- T4 — Custom GPT integration against the canonical backend
- T5 — refresh / discovery / monitoring evolution

## Current accepted state

Accepted:
- A0 baseline
- T1.0 runtime bootstrap
- T1.1 runtime configuration and local operator surface
- T1.2 persistence foundation and Postgres baseline
- T1.3 project registry vertical slice
- T1.4 handbook persistence baseline

Current focus:
- T1.5 source / project-source first slice

## T1 sequence

### T1.0
- repository scaffold
- FastAPI runtime
- health endpoint
- quality gates

### T1.1
- runtime settings
- operator commands
- local smoke surface

### T1.2
- persistence package
- Postgres config
- DB status surface
- Alembic baseline

### T1.3
- first project persistence model
- first migration
- create/list/get project API
- project registry tests

### T1.4
- handbook persistence baseline
- handbook version history
- read/write current handbook API
- handbook version list API

### T1.5
- source registry
- project-source attachment registry
- create/list source API
- attach/list project source API
- first duplicate-protection for project/source

## Explicit non-goals right now

Not now:
- UI build-out
- Custom GPT actions
- vector search
- source crawling
- monitoring agents
- multi-user collaboration

## Transition rule

We continue with small vertical slices.
Every slice updates:
- `MASTERPLAN.md`
- `PROJECT_STATE.md`
- one `HANDOFF_*.md`
