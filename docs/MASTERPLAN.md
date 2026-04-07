# Harbor Masterplan

## 1. Product target

Harbor is a project-partitioned research operating system.

It is not merely a chat-based RAG surface. Its long-term target is a governed
system for:

- project-specific research definition
- source collection and evidence storage
- review and resume workflows
- refresh and discovery workflows
- blueprint reuse
- later monitoring and agentic candidate generation

## 2. Canonical phase order

### A0 — product / domain / architecture definition
Accepted.

### T1 — technical bootstrap and local single-node foundation
Current active implementation phase.

### T2 — first vertical product slices
Planned after local technical foundation is stable.

### T3 — VPS preview deployment and hosted runtime
Planned after first stable local slices exist.

### T4 — Custom GPT integration on canonical backend
Planned after stable hosted API surface exists.

### T5 — refresh / discovery expansion
Planned after source and project fundamentals are stable.

### T6 — monitoring / agentic candidate generation
Later phase. Not part of current delivery focus.

## 3. Current implementation sequence

1. T1.0 repository scaffold and bootstrap runtime
2. T1.1 runtime configuration and local operator surface
3. T1.2 persistence foundation and Postgres baseline
4. T1.3 first project storage slice
5. T2.0 first vertical domain slice: projects + handbook
6. T2.x source and snapshot model
7. T3.x hosted runtime and VPS operations
8. T4.x GPT integration
9. T5/T6 refresh, discovery, monitoring, agentic evolution

## 4. Principle for moving forward

Do not widen Harbor horizontally too early.

The next priority is not more concept sprawl. The next priority is a disciplined,
testable transition from bootstrap runtime into persistence and then the first
real Harbor product slice.
