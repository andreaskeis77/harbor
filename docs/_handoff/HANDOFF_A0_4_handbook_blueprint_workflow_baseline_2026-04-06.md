# HANDOFF A0.4 — Handbook, Blueprint, and Workflow baseline

Status: Ready for handoff  
Date: 2026-04-06  
Phase: A0.4

## Scope of this tranche

This tranche extends Harbor from product scope and domain structure into explicit
operating logic for:

- the Research Handbook
- blueprint-based reuse
- workflow states and transitions

## Delivered artifacts

- `docs/HANDBOOK_SPEC_v0_1.md`
- `docs/BLUEPRINT_MODEL_v0_1.md`
- `docs/WORKFLOW_MODEL_v0_1.md`

Updated:

- `README.md`
- `docs/INDEX.md`
- `docs/PROJECT_STATE.md`
- `docs/concepts/README.md`

## What is now clearer

Harbor is no longer defined only by scope and entities.

The project now has a first explicit answer to:

- how a project definition is structured
- how and when that definition changes
- how completed work becomes reusable
- how research state moves through draft, research, review, archive, and blueprint release

## Important decisions now captured

- handbook versioning is first-class
- archive and blueprint are not the same thing
- blueprint reuse uses snapshot import, not live inheritance
- resume and review are workflow primitives
- refresh is a distinct workflow from initial search

## Still open after A0.4

- exact runtime architecture
- exact API routes and command surface
- exact storage families beyond the system-of-record decision
- exact artifact storage posture
- search/retrieval orchestration internals
- health, logging, and run-evidence implementation structure

## Recommended next step

Proceed to:

**A0.5 — System architecture and runtime boundary baseline**

This next step should define:

- runtime layers
- first API surface boundaries
- web UI boundary
- persistence families
- artifact storage posture
- operational evidence posture

## Gate note

This tranche remains documentation-first by design.

No runtime code is introduced.
