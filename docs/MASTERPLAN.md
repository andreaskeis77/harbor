# Harbor Masterplan

## Product direction

Harbor is a project-partitioned research operating system, not a generic chat-RAG.

The sequence stays:

- A0 — accepted product / architecture / governance baseline
- T1 — local technical bootstrap and manual operator flow release baseline
- T2 — operator web surface
- T3 — OpenAI adapter layer against the canonical backend
- T4 — chat surface against the canonical backend
- T5 — refresh / discovery / monitoring evolution

## Current accepted state

Accepted:
- A0 baseline
- T1.0 runtime bootstrap
- T1.1 runtime configuration and local operator surface
- T1.2 persistence foundation and Postgres baseline
- T1.3 project registry vertical slice
- T1.4 handbook persistence baseline
- T1.5 source / project-source first slice
- T1.6A search campaign registry baseline
- T1.6B review queue baseline
- T1.7A search run registry baseline
- T1.7B search result candidate baseline
- T1.8 candidate-to-review promotion
- T1.9 review-queue-to-source promotion
- T1.10 duplicate guards for promotion flow
- T1.11 workflow summary and lineage surface
- T1.12 docs + runbook + release hygiene
- T1.13 `v0.1.0-alpha` release cut

Current focus:
- T2.0 operator web shell

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

### T1.6A
- search campaign registry
- create/list/get search campaign API
- project-scoped campaign tests
- smoke search campaign slice

### T1.6B
- review queue baseline
- create/list review queue API
- project-scoped review queue tests
- smoke review queue slice

### T1.7A
- search run registry
- create/list/get search run API
- campaign-scoped run tests
- smoke search run slice

### T1.7B
- search result candidate registry
- create/list candidate API
- run-scoped candidate tests
- smoke search result candidate slice

### T1.8
- candidate-to-review promotion
- promotion lineage on review queue items
- smoke candidate-review promotion slice

### T1.9
- review-queue-to-source promotion
- candidate accepted-state handoff
- smoke review-queue-source promotion slice

### T1.10
- duplicate guards for promotion flow
- idempotence protection on promotion endpoints
- smoke duplicate-guard slice

### T1.11
- project workflow summary
- lineage surface
- smoke workflow summary slice

### T1.12
- README / PROJECT_STATE / INDEX sync
- alpha runbook
- alpha release checklist
- release hygiene documentation

### T1.13
- `v0.1.0-alpha` release cut
- tagged manual operator baseline

## T2 sequence

### T2.0
- operator web shell
- project list
- project detail page
- workflow summary surface
- read-heavy views for campaigns, runs, candidates, review queue, project sources
- web shell must call Harbor APIs only

### T2.1
- operator actions UI
- targeted promote / create / operator actions over existing APIs
- no parallel business logic outside the backend

### T2.2
- UX / API hardening
- validation polish
- error handling polish
- pagination / filtering / consistency improvements as needed

## Explicit non-goals right now

Not now:
- direct DB-driven web UI logic
- OpenAI integration
- chat surface
- source crawling automation
- monitoring agents
- multi-user collaboration

## Transition rule

We continue with small vertical slices.
Every slice updates:
- `MASTERPLAN.md`
- `PROJECT_STATE.md`
- one `HANDOFF_*.md`

For T2, the web layer remains a thin client over Harbor APIs.
