# Harbor — Runtime Boundaries v0.1

Status: Draft runtime boundary baseline  
Phase: A0.5  
Scope: Clear separation of responsibilities before implementation

---

## 1. Purpose

This document defines the runtime boundaries of Harbor.

Its purpose is to prevent Harbor from collapsing into an undifferentiated system where:

- chat interactions become hidden state
- UI actions do too much synchronous work
- fetch/index tasks run without proper tracking
- derived data is confused with canonical state
- monitoring later grows as an uncontrolled add-on

Harbor needs clear runtime boundaries early, because the product is inherently stateful,
iterative, and long-lived.

---

## 2. Boundary model overview

Harbor should be treated as five cooperating runtime zones:

1. **Interaction zone**
2. **API / application zone**
3. **Background work zone**
4. **Storage zone**
5. **External acquisition zone**

These zones cooperate, but their responsibilities should not blur.

---

## 3. Interaction zone

Components:

- web UI
- Custom GPT
- possibly later CLI or admin tools

Allowed responsibilities:

- present information
- collect user intent
- submit commands to backend
- display run status and results
- request analyses
- support review and resume workflows

Forbidden or discouraged responsibilities:

- direct DB writes without backend control
- hidden client-side project truth
- long-running fetch or embedding work inside request/response flow
- storing source-of-truth state in prompt context only

Runtime rule:

The interaction zone is **stateless or near-stateless** relative to Harbor truth.

---

## 4. API / application zone

Components:

- FastAPI application
- domain services
- command handlers
- query handlers
- validation layer
- auth boundary

Responsibilities:

- own the canonical command surface
- validate project operations
- persist canonical state
- orchestrate synchronous business logic
- create background jobs when work should be deferred
- expose stable contracts to web and GPT

This zone is the **business core**.

Runtime rule:

If an operation changes Harbor truth, it should flow through this zone.

---

## 5. Background work zone

Components:

- worker process or job runner
- scheduled task capability later
- retry and failure handling
- execution status updates

Responsibilities:

- execute long-running acquisition tasks
- parse fetched artifacts
- chunk content
- generate embeddings
- perform refresh runs
- later perform discovery/monitoring runs
- detect and record deltas
- populate review queues and candidate items

Runtime rule:

Work that may be slow, failure-prone, retried, or repeated must be modeled as a run in
this zone, not hidden inside a synchronous user request.

---

## 6. Storage zone

Components:

- Postgres
- pgvector structures
- artifact filesystem storage
- possibly later cache structures

Responsibilities:

- store durable project and workflow state
- store derived searchable content
- retain raw source evidence where needed
- preserve lineage between runs, artifacts, chunks, and analyses

Runtime rule:

The storage zone owns durable system memory.  
The interaction zone must not become a substitute for it.

---

## 7. External acquisition zone

Components:

- public-web fetches
- PDF retrieval
- forum/article retrieval
- user manual uploads
- later explicitly permitted authenticated acquisition

Characteristics:

- slow
- unreliable
- rate-limited
- legally/policy sensitive
- variable in quality and format

Runtime rule:

Acquisition is never trusted by default.  
External content becomes Harbor knowledge only through registration, extraction, review,
and explicit project binding.

---

## 8. Command vs. query boundary

Harbor should clearly separate:

- **commands** that change system state
- **queries** that read and assemble information

Examples of commands:

- create project
- edit handbook
- archive project
- mark project as blueprint
- assign source to project
- trigger refresh run
- accept or reject a candidate

Examples of queries:

- list projects
- show current handbook version
- list open gaps
- show project timeline
- show sources changed since last review
- retrieve relevant evidence for a question

This separation improves reasoning, auditing, and future testability.

---

## 9. Synchronous vs. asynchronous boundary

Harbor should not force every action to be async, but must decide clearly what belongs
inline and what belongs out-of-band.

### 9.1 Usually synchronous

- create/update project metadata
- create/edit handbook
- archive project
- mark blueprint status
- add manual gap
- create review decision
- list projects and project state
- query already indexed evidence

### 9.2 Usually asynchronous

- web fetches across multiple targets
- PDF extraction
- chunk generation
- embedding generation
- refresh runs
- discovery runs
- monitoring runs
- larger diff/delta calculations
- bulk reprocessing

Runtime rule:

Slow work should produce a trackable run, not a hanging interaction.

---

## 10. Canonical truth vs. derived truth boundary

Harbor must distinguish between:

### 10.1 Canonical truth

- project definitions
- handbook versions
- source registrations
- project/source bindings
- review decisions
- gap records
- run records
- blueprint lineage

### 10.2 Derived truth

- chunks
- embeddings
- semantic search results
- summaries
- analyses
- ranking scores
- delta suggestions
- candidate prioritization

Derived truth is valuable, but it must remain attributable and replaceable.

---

## 11. Review boundary

Harbor must support a boundary between:

- newly acquired or detected information
- accepted project knowledge

Therefore later agentic or scheduled work should create:

- candidates
- deltas
- review tasks
- recommendations

It should not silently rewrite accepted project conclusions.

This is one of Harbor’s most important runtime guards.

---

## 12. Blueprint boundary

Blueprint reuse must also respect runtime boundaries.

Allowed in v1:

- explicit user selection of blueprint
- explicit creation of new project from blueprint snapshot
- explicit lineage recording

Not allowed in v1:

- hidden live synchronization between blueprint and derived project
- background mutation of child projects when a blueprint changes
- implicit inheritance chains that are hard to audit

---

## 13. Resume boundary

Resume is not just another search.

Resume should be a specific backend-supported query surface that can answer:

- what changed since last meaningful interaction
- what remains unresolved
- what requires review
- what the next action should be

This should be assembled from canonical metadata plus selected derived information.

---

## 14. Monitoring boundary

Monitoring belongs beyond v1, but the boundary should be defined now.

Monitoring should later mean:

- scheduled refresh/discovery logic
- project-scoped policies
- run records
- delta or candidate generation
- user-visible outcomes and review queues

Monitoring should not mean:

- autonomous hidden browsing without policy
- untracked state mutation
- opaque long-lived prompt context

---

## 15. Failure boundary

Harbor should fail visibly at the correct layer.

Examples:

- network fetch failed -> background run failure or warning
- extraction failed -> artifact parse failure
- handbook validation failed -> API-layer validation error
- missing evidence -> analysis should state insufficient support
- external auth required -> explicit research gap or blocked-source status

Failure must be captured where it happens, but surfaced in the project experience.

---

## 16. Minimal runtime surfaces for v1

v1 should at least establish these runtime surfaces:

- project CRUD surface
- handbook version surface
- source/project-source surface
- search/refresh trigger surface
- run status surface
- review decision surface
- project dashboard/resume query surface
- analysis retrieval surface
- health surface

---

## 17. Operational implication for the next phase

The technical bootstrap should now create scaffolding that respects these runtime
boundaries from the beginning.

That means:

- not mixing UI and business logic
- not treating vector search as the only persistence concern
- not hiding background work in request handlers
- not storing project truth in chat state
- not postponing run metadata until later

---

## 18. Exit criteria for this document

This runtime-boundary baseline is successful when Harbor now has:

- clear interaction vs. backend separation
- clear sync vs. async separation
- clear canonical vs. derived truth separation
- clear review boundary
- clear blueprint boundary
- clear monitoring boundary
- clear failure visibility expectations
