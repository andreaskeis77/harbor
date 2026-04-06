# HANDOFF A0.5 — System Architecture and Runtime Boundaries

Status: Green for architecture baseline  
Date: 2026-04-06  
Phase: A0.5

## Completed in this tranche

- introduced first system architecture baseline for Harbor
- defined recommended phase-1 platform posture
- defined runtime boundaries across interaction, backend, jobs, storage, and acquisition
- aligned project state and documentation index to the new phase

## Accepted baseline

The current recommended posture is:

- FastAPI as canonical backend
- Postgres as system of record
- pgvector-enabled semantic retrieval support
- filesystem artifact storage on VPS
- web UI plus Custom GPT against one backend
- explicit background work posture for search/refresh/indexing

## Why this matters

Harbor is now clearly framed as a project-partitioned research operating system, not
a prompt-only RAG shell. This tranche prevents premature architectural drift toward
hidden chat state, uncontrolled synchronous work, or vector-store-centric design.

## Open items after A0.5

Still open:

- exact repository scaffolding
- exact implementation package layout
- exact job execution mechanism
- exact auth and config posture
- exact artifact directory scheme
- exact health/smoke protocol
- first technical bootstrap files

## Recommended next tranche

A0.6 — Technical bootstrap and repository scaffolding baseline

This should define:

- initial repo tree beyond docs
- config and runtime file posture
- first src/tests/tools/config directories
- bootstrap rules for local and VPS runtime
- minimal health and smoke contract
