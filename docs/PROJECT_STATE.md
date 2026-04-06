# Project State

## Current phase

A0.6 — Technical bootstrap and repository scaffolding baseline

## Completed

- A0.1 product scope baseline
- A0.2 domain model baseline
- A0.3 user stories and functional requirements baseline
- A0.4 handbook, blueprint, and workflow baseline
- A0.5 system architecture and runtime boundaries baseline

## What A0.6 adds

This tranche converts the prior conceptual baseline into a concrete technical starting posture for the first implementation bolt.

That means Harbor now has an explicit answer to:

- which repository folders should exist first
- which files are required before runtime code starts
- which technical surfaces belong in the first bootstrap tranche
- which concerns are intentionally deferred
- which minimal health, config, and startup posture should be introduced first

## Current product posture

Harbor is currently defined as a project-partitioned research operating system with:

- clearly separated projects
- versioned research handbooks
- project-local source evaluation
- explicit review and resume workflows
- blueprint-based reuse of archived projects
- refresh, discovery, and later monitoring as part of the design horizon

## Current architecture posture

The accepted phase-1 architecture baseline is:

- FastAPI application layer
- Postgres as system of record
- pgvector for semantic retrieval support
- filesystem artifact store for captured source artifacts
- shared backend for web UI and Custom GPT
- background-job surface for refresh, discovery, and later monitoring work

## Current implementation posture

The repository is still intentionally pre-runtime.

No production code, database migrations, or running services are introduced by A0.6.

Instead, A0.6 prepares the repository and technical bootstrap target so that the first implementation tranche can start in a controlled way.

## Current repository posture

The repository should now be understood as having four layers of maturity:

1. **Method baseline**
2. **Product and domain baseline**
3. **Architecture and runtime baseline**
4. **Technical bootstrap target**

The next phase will begin moving from documentation-first to implementation-first, but only in small, explicit bolts.

## Validated next target

The next recommended implementation entry is:

**T1.0 — Repository scaffold and technical bootstrap implementation**

This first implementation bolt should introduce only the minimum durable technical surface needed to start Harbor safely, such as:

- initial directory structure
- Python package root
- basic configuration surface
- app entrypoint skeleton
- health command or health endpoint skeleton
- initial database configuration contract
- initial artifact-root contract
- initial tests and validation hooks

## Important non-goals at this stage

Still not part of the current implementation baseline:

- full source acquisition implementation
- project CRUD implementation
- full web UI
- Custom GPT integration wiring
- background scheduler runtime
- agentic monitoring runtime
- full Postgres migration set
- full pgvector retrieval implementation

## Preferred next bolt

T1.0 — Repository scaffold and technical bootstrap implementation
