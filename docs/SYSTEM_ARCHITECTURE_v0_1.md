# Harbor System Architecture v0.1

## Phase-1 recommended posture

- FastAPI for the application surface
- Postgres as system of record
- pgvector later for semantic retrieval
- filesystem artifact store for raw snapshots and durable evidence
- website and Custom GPT on one canonical backend
- background work for refresh and later monitoring

## Core design rule

Canonical truth, derived retrieval structures, and candidate findings must remain separate.
