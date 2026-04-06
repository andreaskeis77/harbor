# Harbor — System Architecture v0.1

Status: Draft architectural baseline  
Phase: A0.5  
Scope: First durable system architecture before technical bootstrap

---

## 1. Purpose

This document defines the recommended phase-1 system architecture for Harbor.

It translates the prior product and domain work into a durable technical target picture
that is suitable for:

- development on the DEV-LAPTOP
- later deployment to the VPS
- one canonical backend for web and Custom GPT
- long-lived project state and evidence storage
- controlled future evolution toward refresh, monitoring, and agentic assistance

This is **not** yet an implementation document. It is the architecture baseline that
should guide the first technical bootstrap.

---

## 2. Architectural thesis

Harbor is **not** primarily a chatbot with a vector store attached.

Harbor is a **project-partitioned research operating system** with:

- a canonical application/backend layer
- persistent project state
- governed source and evidence storage
- controlled analysis artifacts
- resumable workflows
- later refresh and monitoring jobs

Therefore the architecture must be built around **application state, provenance, and
workflow control**, not around prompt-only interaction.

---

## 3. Recommended phase-1 architecture posture

Phase 1 should use the following posture:

- **FastAPI** for the canonical backend and API surface
- **Postgres** as the system of record
- **pgvector** for semantic retrieval in the same storage posture
- **filesystem artifact storage** on the VPS for raw fetched files and evidence payloads
- **web UI** for browse/review/operations
- **Custom GPT** as a natural-language front end calling the same backend
- **background jobs** for fetch, parse, refresh, chunk, embed, and review queue updates

This posture is recommended because it gives:

- one canonical truth
- strong fit for project state and workflow history
- acceptable semantic retrieval capability
- good VPS suitability
- clear separation of interactive requests from longer-running work
- later extensibility toward monitoring without redesigning the product core

---

## 4. Major layers

### 4.1 Interaction layer

This layer includes all user-facing entry points.

Primary entry points:

- Harbor web UI
- Harbor API clients
- Custom GPT actions against Harbor backend

Responsibilities:

- project selection
- handbook display/edit
- search and refresh triggers
- review and resume interaction
- analysis requests
- project/blueprint lifecycle actions

Non-responsibilities:

- direct database mutation logic in the UI
- long-running fetch/index logic
- hidden private state outside the backend

### 4.2 Application/API layer

This is the canonical Harbor backend.

Recommended implementation posture:

- FastAPI service
- domain services and command/query boundaries
- validation and orchestration of writes
- authentication/authorization boundary
- stable API contract for web and GPT

Responsibilities:

- project lifecycle control
- handbook versioning
- source/project-source management
- artifact registration
- review decision capture
- search/refresh/discovery run creation
- resume/status query surfaces
- analysis artifact persistence

### 4.3 Orchestration and jobs layer

This layer handles work that should not run inline with UI requests.

Examples:

- web fetch jobs
- PDF or HTML extraction jobs
- chunking and embedding jobs
- refresh jobs
- change detection
- monitoring jobs later
- candidate queue generation

Responsibilities:

- safe execution of longer-running work
- status updates back to Harbor metadata
- retry/failure visibility
- evidence capture for each run

### 4.4 Storage layer

Recommended components:

- Postgres for canonical relational state
- pgvector for semantic search support
- filesystem artifact store for raw files and snapshots

Responsibilities:

- durable project state
- durable handbook versions
- durable source metadata
- durable review, gap, and analysis records
- durable source snapshots and evidence artifacts
- searchable chunk/index records

### 4.5 External acquisition layer

This layer covers public-web and later semi-automated source access.

Examples:

- public websites
- PDFs
- forums
- news pages
- hotel/provider pages
- user-uploaded/manual input
- later login-gated sources only via explicit policy

This layer must be treated as variable-quality and failure-prone.

---

## 5. Canonical data ownership

Harbor must define one owner for each class of truth.

### 5.1 Backend-owned truth

The backend owns:

- projects
- handbook versions
- project/source relationships
- review decisions
- research gaps
- search and refresh runs
- analysis artifacts
- blueprint lineage
- operational run state

### 5.2 Artifact-store-owned binaries

The filesystem artifact store owns:

- downloaded raw HTML/PDF/text files where retained
- rendered evidence files
- snapshots
- export artifacts
- possibly later diff/evidence bundles

### 5.3 Derived search structures

Vector/index/chunk structures are derived from stored content and metadata.

They are important, but they are **not** the canonical source of truth.

---

## 6. Why Postgres is the center

Postgres is recommended as the system center because Harbor is not only an analytical
or append-only dataset project. It is a workflow and state management system.

Harbor needs strong support for:

- evolving project state
- version history
- explicit relationships
- review decisions
- resumable workflows
- job and run metadata
- future concurrent reads/writes
- web application usage patterns

DuckDB may still become useful later for exports, analytics slices, or offline
analysis, but it should not be the canonical system center for Harbor v1.

---

## 7. Search posture

Harbor should support two complementary retrieval modes.

### 7.1 Structured retrieval

Examples:

- list my active projects
- show sources for project X
- show unreviewed candidates
- show latest refresh runs
- show blueprint lineage
- show open research gaps

This is relational and metadata-driven.

### 7.2 Semantic retrieval

Examples:

- find relevant evidence about house reefs
- retrieve chunks related to seasonality
- surface prior research notes close to a new question

This is vector-assisted and content-driven.

Harbor must support both, without pretending that vector search alone is the whole system.

---

## 8. Project partitioning in the architecture

Project separation is mandatory at the business layer and should be reflected in all
key data paths.

Required implications:

- every major domain object must be project-bound or explicitly globally owned
- project-bound queries must not accidentally bleed across projects
- review state is project-local
- analysis artifacts are project-local
- gaps are project-local
- blueprint use must record lineage explicitly

A source may exist globally, but its role in a project is modeled through a project-local
relationship object.

---

## 9. Blueprint architecture posture

Archived projects may become blueprints.

Recommended v1 posture:

- blueprint creation is explicit
- blueprint use creates a new project snapshot
- derived project becomes independent after creation
- lineage is recorded in metadata
- no live inheritance in v1

This keeps the architecture stable and reduces hidden coupling.

---

## 10. Job and run architecture posture

Harbor should treat long-running or repeated work as explicit runs.

Examples:

- search campaign run
- refresh run
- artifact extraction run
- embedding run
- later monitoring run

Every run should capture:

- run type
- start/end timestamps
- status
- target project
- trigger source
- summary or error payload
- downstream artifacts or output references

This is essential for later reliability, auditing, and user-visible status.

---

## 11. Web architecture posture

The web UI should initially be an operator-grade application, not a pixel-perfect
productized consumer shell.

v1 UI priorities should be:

- project list and project dashboard
- handbook display/edit
- sources and candidates
- review queues
- refresh/search actions
- gaps and analyses
- blueprint actions

The web layer should stay thin relative to business logic.

---

## 12. Custom GPT posture

Custom GPT is a primary interaction path, but not the business core.

Recommended posture:

- GPT calls Harbor actions/API
- Harbor validates and executes stateful operations
- GPT returns project-aware answers grounded in Harbor data
- GPT does not maintain separate shadow project state

Typical GPT requests include:

- listing projects
- opening project context
- showing scope and gaps
- triggering refresh/search workflows
- asking for project-grounded analyses

---

## 13. Security and secret posture

Phase-1 architecture rules:

- no secrets in the repo
- server-side API keys only
- backend owns access to any external AI or fetch credentials
- browser clients do not hold privileged service keys
- auth-gated acquisition is explicitly governed, not improvised

---

## 14. Observability posture

Harbor is not ready for serious use without operational evidence.

Minimum architectural expectations:

- health endpoint
- structured logs
- visible job/run status
- error visibility
- artifact/run linkage
- inspectable current project state

---

## 15. VPS posture

Harbor should be deployable to the VPS with a simple, inspectable runtime model.

Expected phase-1 runtime posture:

- one backend service
- one database service posture
- one web-facing application posture
- one artifact root on disk
- one clear config/secret posture
- one documented recovery path

Avoid premature service sprawl in v1.

---

## 16. Explicit non-goals for this architectural phase

Not yet required here:

- distributed microservice architecture
- multi-tenant enterprise topology
- autonomous agent mesh
- broad login/session automation
- real-time event streaming complexity
- overly abstract plugin systems

---

## 17. Exit criteria for A0.5

This architecture baseline is successful when Harbor now has:

- one recommended system-center posture
- one canonical API/backend posture
- one explicit storage posture
- one explicit job/runtime posture
- one explicit web/GPT relationship
- one explicit project partitioning rule
- one explicit blueprint inheritance posture
- one clear boundary into the technical bootstrap phase
