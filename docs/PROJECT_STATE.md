# Harbor Project State

Stand: 2026-04-06 (Europe/Berlin)

## Current phase

A0.1 — Product Scope Baseline and Repository Bootstrap

## Product intent

Harbor is intended to become a project-partitioned research operating system.

The system is meant to support:

- short, simple research projects
- larger and longer-running research projects
- clean project separation
- versioned project scope and handbook management
- source collection, evidence capture, and later retrieval
- review and resume workflows
- later refresh, discovery, monitoring, and agent-assisted update flows
- one shared backend for website and Custom GPT

## Current green decisions

The following foundational decisions are accepted:

- product name: `Harbor`
- system role: project-partitioned research system, not just a chat RAG
- system of record: `Postgres`
- project separation is a hard architecture rule
- archived projects may become blueprints
- blueprint reuse must start as snapshot-based reuse, not live inheritance
- website and Custom GPT must use the same backend truth

## Current repository posture

This repository currently starts in a documentation-first bootstrap state.

There is not yet an accepted implementation baseline for:

- backend framework
- data model DDL
- web stack
- scheduling runtime
- source ingestion runtime
- retrieval strategy
- embedding strategy
- authentication posture
- VPS deployment scripts

## Current goal of this tranche

Create a clean baseline for the next architecture and modeling steps by establishing:

- repository bootstrap files
- docs navigation
- product scope baseline
- engineering and working rules
- initial handoff baseline

## Immediate next required documents

The next tranche should define at minimum:

1. `Domain Model v0.1`
2. `User Stories v0.1`
3. `Functional Requirements v0.1`
4. `Research Handbook Specification v0.1`
5. `Blueprint Model v0.1`
6. `Search / Refresh / Review Workflow v0.1`

## Working assumption for repository root

Canonical DEV-LAPTOP root:

`C:\projekte\Harbor`

## Open decisions after A0.1

Still open:

- exact repo directory layout for implementation phase
- exact Postgres posture
- artifact storage structure on disk
- metadata schema baseline
- search/retrieval architecture
- initial source acquisition scope
- operator web UX
- Custom GPT action surface
- health, smoke, and deployment conventions
