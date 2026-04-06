# HANDOFF A0.2 - Domain Model Baseline

Status: Green for handoff
Date: 2026-04-06
Phase: A0.2

## Completed in this tranche

- added the first Harbor domain model baseline
- updated the repository navigation
- updated project state to reflect the new phase
- aligned README navigation with the current product-definition posture

## Delivered artifacts

- `docs/DOMAIN_MODEL_v0_1.md`
- `docs/INDEX.md`
- `docs/PROJECT_STATE.md`
- `README.md`

Added handoff:
- `docs/_handoff/HANDOFF_A0_2_domain_model_baseline_2026-04-06.md`

## What the model now clarifies

The Harbor model now explicitly distinguishes between:

- project and handbook
- source and project-source
- source and snapshot
- evidence and analysis
- accepted knowledge and candidate intake
- archived project and reusable blueprint

It also establishes the first stable layer model for:

- project definition
- research materials
- interpretations
- operations
- reuse

## Important design consequences

- project partitioning is the primary business boundary
- blueprint reuse is snapshot-based by default
- review decisions are historical domain objects, not just mutable flags
- future monitoring and agent flows must create reviewable candidates rather than silently mutate accepted truth

## What remains open

Still open:

- user stories and functional requirements
- exact relational schema
- first API surface
- first UI/read model set
- first search/review/refresh workflow spec

## Recommended next tranche

A0.3 - User Stories and Functional Requirements Baseline

This next tranche should define:

- the main user journeys
- must/should/could functional requirements
- v1 boundary vs later phases
- operator actions for review/resume/search/refresh/blueprint use

## Gate assessment

- product-definition gate: green for A0.2
- runtime gate: not started by design
- deployment gate: not started by design
