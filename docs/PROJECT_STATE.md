# Project State

## Current phase

A0.4 — Handbook, Blueprint, and Workflow baseline

## Completed

- A0.1 product scope and documentation bootstrap
- A0.2 domain model baseline
- A0.3 user stories and functional requirements baseline
- A0.4 handbook specification baseline
- A0.4 blueprint model baseline
- A0.4 workflow model baseline

## Current architecture posture

Harbor is currently defined as:

- a documentation-first project
- a project-partitioned research system
- a system with Postgres as system of record
- one canonical backend for website and Custom GPT
- explicit separation between source, evidence, analysis, and review
- explicit separation between project-local meaning and globally deduplicated artifacts
- a system designed for resume, review, refresh, and later monitoring

## Current validated functional posture

The current documentation baseline now defines:

- project partitioning
- project lifecycle
- research handbook as a versioned steering object
- blueprint reuse of archived projects
- workflow states for draft, active research, review, archive, and blueprint release
- refresh/discovery/monitoring as staged capability layers

## What is now clearer than in A0.3

A0.4 sharpens three critical areas:

1. the internal structure of the research handbook
2. the controlled reuse of archived projects via blueprints
3. the operator-facing workflow logic for create, research, review, refresh, archive, and resume

## Current repository posture

The repository is still documentation-first by design.

No implementation runtime is introduced by this tranche.

## Current green decisions

- Harbor remains project-partitioned
- Postgres remains the intended system of record
- handbook versioning is a core v1 requirement
- blueprint reuse uses import snapshots, not live inheritance
- workflow state is part of product design, not just UI behavior
- review and resume remain first-class requirements
- refresh is a v1 capability; agentic monitoring remains later-phase

## Open items for the next tranche

The next architectural step should define:

- system architecture baseline
- runtime surfaces
- storage families
- first API boundaries
- first web surface boundaries
- operational evidence posture

## Preferred next bolt

A0.5 — System architecture and runtime boundary baseline
