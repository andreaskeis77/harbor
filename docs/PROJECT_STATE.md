# Harbor Project State

## Current phase

T1.0 — Repository scaffold and technical bootstrap implementation

## Accepted baseline behind the current phase

The A0 baseline is accepted.

That means the following areas are established at documentation level:
- product scope
- domain model
- user stories
- functional requirements
- handbook model
- blueprint model
- workflow model
- system architecture
- runtime boundaries
- technical bootstrap intent
- consolidation and acceptance controls

## Current implementation target

The current target is intentionally small and controlled.

T1.0 should only establish:
- canonical repository scaffold
- Python package layout
- minimal FastAPI app
- `/healthz`
- minimal tests
- minimal quality-gate scripts
- repo-local config example
- run-ready local bootstrap path

## What is explicitly not in T1.0

T1.0 does not yet try to implement:
- project persistence
- handbook persistence
- source ingestion
- embeddings
- pgvector runtime
- background jobs
- website workflows beyond minimal runtime
- GPT actions

## Current recommended next step after T1.0

T1.1 — Runtime configuration and local operator surface
