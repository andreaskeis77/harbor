# Harbor Masterplan

## Product direction

Harbor is a project-partitioned research operating system, not a generic chat-RAG.

## Phase sequence

### A0 — Definition and architecture
Accepted.

### T1.0 — Runtime bootstrap
Accepted.

### T1.1 — Runtime configuration and local operator surface
Accepted.

### T1.2 — Persistence foundation and Postgres baseline
Accepted with the current tranche.

### T1.3 — Project registry vertical slice
Planned next.

Target outcome:
- create project
- list projects
- read project
- first persistence-backed Harbor domain object

### T1.4 — Handbook persistence baseline
Planned after T1.3.

### T1.5 — Source registry baseline
Planned after T1.4.

### T2.x — Search / refresh / review / GPT / VPS
Deferred until the local product spine is real.

## Current recommendation

Do not jump to ingestion, GPT actions, or VPS rollout yet.

Build the Harbor product spine in this order:

1. persistence baseline
2. project registry
3. handbook persistence
4. source baseline
5. search / refresh
6. GPT surface
7. VPS preview
