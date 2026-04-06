# Project State

## Current phase

A0.5 — System architecture and runtime boundary baseline

## Completed

- A0.1 product scope baseline
- A0.2 domain model baseline
- A0.3 user stories and functional requirements baseline
- A0.4 handbook, blueprint, and workflow baseline
- A0.5 system architecture and runtime boundary baseline

## Current validated posture

Harbor is currently in a documentation-first architecture phase.

The current accepted baseline includes:

- Harbor is a project-partitioned research system, not a generic chat RAG
- Postgres is the system of record
- Website and Custom GPT must share one canonical backend
- projects are strictly separated at the business layer
- the Research Handbook is the core steering object per project
- archived projects can become explicit blueprints
- refresh and later monitoring are part of the product direction
- agentic behavior is deferred beyond v1 and must not write unchecked truth

## Current architectural posture

The recommended phase-1 architecture posture is:

- FastAPI backend as the canonical application/API surface
- Postgres as the canonical transactional and metadata store
- pgvector-enabled semantic retrieval capability in the same platform posture
- filesystem-based artifact storage on the VPS for raw snapshots and evidence files
- browser-based web UI for project operations and review
- Custom GPT as a natural-language control surface over the same backend
- background job layer for search, refresh, parsing, chunking, indexing, and review queues

## Runtime boundary posture

The current runtime boundary is explicitly split into:

- interaction layer
- application/API layer
- orchestration/jobs layer
- storage layer
- external acquisition layer

The system must not collapse these concerns into one undifferentiated chat workflow.

## What is intentionally not decided yet

Still open for the next phase:

- exact repo scaffolding for src/tests/tools/config/runtime files
- exact web stack details for v1 UI
- exact background-job mechanism
- exact auth posture for website and GPT-facing API usage
- exact artifact directory structure
- exact health/smoke/release evidence commands
- first implementation tranche layout

## Preferred next bolt

A0.6 — Technical bootstrap and repository scaffolding baseline
