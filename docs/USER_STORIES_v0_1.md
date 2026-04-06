# Harbor – User Stories v0.1

Status: Draft baseline for product definition phase  
Phase: A0.3  
Scope: Initial user story set for Harbor

---

## 1. Purpose

This document defines the first user story baseline for Harbor.

The goal is to describe Harbor from the perspective of real usage instead of architecture alone. These user stories help separate:

- core needs,
- desirable later features,
- non-goals for v1,
- and workflow expectations that must be supported by the product model.

---

## 2. Primary actor

The primary actor is initially a single user who creates, reviews, and reuses research projects over time.

The same user may interact with Harbor through:

- the web interface,
- a Custom GPT connected to Harbor,
- and later optional monitoring or agentic flows.

---

## 3. User story themes

The initial story set is grouped into these themes:

1. Project creation and separation
2. Scope and handbook evolution
3. Source and evidence management
4. Review and resume
5. Refresh and update search
6. Blueprint and reuse
7. Analysis and research gaps
8. Operational trust and continuity

---

## 4. Project creation and separation

### US-001 — Create a new project

As a user, I want to create a new research project so that I can work on a topic in an explicitly separated project space.

### US-002 — See all my projects

As a user, I want to list my projects so that I can choose which one to continue, review, archive, or reuse.

### US-003 — Open one project without mixing others

As a user, I want to open exactly one project and work only within that project context so that different research topics do not get mixed.

### US-004 — Support short and large projects

As a user, I want Harbor to support both quick, small projects and more complex long-running research spaces so that the system remains useful across topic sizes.

### US-005 — Archive a finished project

As a user, I want to archive a project when it is complete or paused so that I can keep the evidence and history without leaving it in the active working set.

---

## 5. Scope and handbook evolution

### US-006 — Create an initial project scope

As a user, I want Harbor to help me define the initial scope of a project so that the research begins from a structured problem statement rather than an unstructured chat.

### US-007 — Refine scope over time

As a user, I want to expand, narrow, or correct a project scope later so that Harbor reflects the current research need rather than freezing an early draft forever.

### US-008 — Keep scope history

As a user, I want the project handbook to be versioned so that I can understand how the project definition evolved.

### US-009 — Distinguish in-scope and out-of-scope

As a user, I want explicit in-scope and out-of-scope boundaries so that research remains focused and later reviews remain understandable.

### US-010 — Reuse good project structure

As a user, I want past project structure to remain reusable so that I do not have to reinvent the same handbook logic for similar topics.

---

## 6. Source and evidence management

### US-011 — Add sources to a project

As a user, I want to add and store sources for a specific project so that evidence is tied to the right topic context.

### US-012 — Distinguish source from project-specific relevance

As a user, I want Harbor to separate the source itself from its project-specific role so that the same source can be relevant in one project and secondary in another.

### US-013 — Preserve evidence snapshots

As a user, I want Harbor to preserve source snapshots or artifacts where appropriate so that later analyses remain traceable to a concrete source state.

### US-014 — Store manually provided information

As a user, I want to add manually provided notes, files, or external findings so that the system can include non-automatically retrievable information.

### US-015 — Track source quality and review state

As a user, I want to classify and review sources so that I know which evidence is accepted, uncertain, duplicated, stale, or pending review.

---

## 7. Review and resume

### US-016 — Resume a project after a pause

As a user, I want to return to a project after days or months and quickly understand its current state so that I can continue without rebuilding context from memory.

### US-017 — Review what changed

As a user, I want to see what changed since my last review so that I can focus on new or updated material.

### US-018 — See open gaps and next actions

As a user, I want Harbor to show research gaps and next sensible actions so that project continuation is guided instead of vague.

### US-019 — Review unreviewed candidates

As a user, I want to inspect unreviewed sources or updates so that Harbor does not silently promote unverified findings into accepted knowledge.

---

## 8. Refresh and update search

### US-020 — Search initially for sources

As a user, I want to launch an initial research search for a project so that Harbor begins building a project-specific evidence base.

### US-021 — Refresh known sources

As a user, I want to re-run a refresh against known sources so that I can detect updates, changes, and possible staleness.

### US-022 — Search for new sources later

As a user, I want to search again for newly emerging sources so that Harbor supports iterative research instead of a one-time crawl.

### US-023 — Distinguish updates from noise

As a user, I want Harbor to distinguish meaningful changes from irrelevant noise so that update review remains practical.

---

## 9. Blueprint and reuse

### US-024 — Mark a project as blueprint-worthy

As a user, I want to mark a finished project as a blueprint candidate so that its structure can later be reused intentionally.

### US-025 — Create a new project from a blueprint

As a user, I want to derive a new project from a prior blueprint so that I can start from a proven structure instead of a blank slate.

### US-026 — Keep derived projects independent

As a user, I want a project created from a blueprint to become independent after creation so that changes do not silently propagate across projects.

### US-027 — Reuse only part of a prior project

As a user, I want to reuse only selected parts of a prior project later so that I can carry over useful patterns without cloning everything.

---

## 10. Analysis and research gaps

### US-028 — Request project-specific analyses

As a user, I want Harbor to create analyses based on the current project evidence so that I can answer structured questions from the collected material.

### US-029 — Separate analysis from evidence

As a user, I want Harbor to keep analyses distinct from primary evidence so that conclusions do not masquerade as original source facts.

### US-030 — Capture missing information explicitly

As a user, I want Harbor to record what could not be found or what requires manual input so that knowledge gaps remain visible instead of being forgotten.

---

## 11. Operational trust and continuity

### US-031 — Trust a canonical backend

As a user, I want the web app and Custom GPT to work against the same project state so that I do not get contradictory answers from different surfaces.

### US-032 — Preserve project history and runs

As a user, I want project activity, searches, refreshes, and review changes to remain inspectable so that Harbor stays trustworthy over time.

### US-033 — Grow toward monitored research

As a user, I want Harbor to be designed so that later monitoring and agentic discovery can be added without breaking the core model.

---

## 12. Priority view for v1

The following user stories are considered especially central for v1:

- US-001 through US-009
- US-011 through US-021
- US-024 through US-026
- US-028 through US-032

The following are important but may be only partially supported or deferred beyond v1:

- US-022
- US-023
- US-027
- US-033

---

## 13. Summary

The Harbor user story baseline shows that the product is fundamentally about:

- clean project separation,
- evolving project definition,
- evidence-aware research memory,
- review and continuation over time,
- explicit updates and refresh,
- and reusable project structures.

This confirms that Harbor should be treated as a project-based research operating system rather than a simple retrieval utility.
