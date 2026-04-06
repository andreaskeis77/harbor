# Project State

## Current phase

A0.3 — User Stories and Functional Requirements Baseline

## Completed

- A0.1 product scope baseline
- A0.2 domain model baseline
- A0.3 user stories baseline
- A0.3 functional requirements baseline

## Current validated state

Harbor is still in a documentation-first architecture phase.

The repository now defines:

- the product purpose and scope,
- the principle of strict project partitioning,
- the first core domain model,
- the first user story set,
- the first functional requirement baseline,
- the blueprint and reuse direction,
- the review/resume operating model,
- the refresh/discovery/monitoring direction.

## Current product posture

Harbor is currently defined as a project-partitioned research system, not merely a chat-based RAG utility.

The product baseline now assumes:

- Postgres as the system of record,
- one canonical backend for web and Custom GPT,
- project-local scope and review state,
- explicit separation between sources, snapshots, extracts, analyses and review decisions,
- archived projects as optional blueprint candidates,
- manual initial search and refresh in v1,
- agentic monitoring only as a later evolution.

## Open points after A0.3

Still open for the next tranche:

- research handbook specification in a stricter structural form,
- blueprint model and reuse rules in more detail,
- workflow model for search, refresh, review and resume,
- initial system architecture,
- initial API surface,
- initial web information architecture,
- initial metadata / storage model,
- first ADR set.

## Recommended next step

Proceed to **A0.4 — Handbook, Blueprint, and Workflow Model Baseline**.

That tranche should define:

- the exact Research Handbook structure,
- blueprint eligibility and reuse mechanics,
- review/resume workflow states,
- search/refresh workflow boundaries,
- candidate vs accepted knowledge transitions.

## Current repository posture

Still documentation-first by design.

No runtime code, ingestion code, web code, or deployment code has been introduced yet.
