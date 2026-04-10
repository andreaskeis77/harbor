# Harbor Engineering Manifest v0.1

## Purpose

This manifest defines the engineering rules for Harbor.

Harbor is treated as a long-lived, operable, research system rather than an ad hoc prototype.

## Priority order

1. Correctness
2. Traceability
3. Operability
4. Maintainability
5. Testability
6. Delivery speed
7. Cleverness

## Core rules

### Small controlled bolts
Work is delivered in small, understandable tranches.

### One canonical backend
Website and Custom GPT must use the same backend.

### Docs are part of the system
If the docs are outdated, the system is degraded.

### No blind trust in AI output
AI-generated code or structure is untrusted until reviewed and validated.

### Honest state handling
Prepared is not the same as validated.
Accepted is not the same as merely discussed.

### Health and evidence first
Runtime work must establish health, logs, and repeatable commands early.

## Delivery rule

Repo updates should be delivered as complete file packages, preferably as flat-root ZIP artifacts for controlled application on the DEV-LAPTOP.

## Definition of done for a bolt

A bolt is done only when:
- purpose is clear
- files are consistent
- checks are run
- docs are updated
- project state is updated
- next step is explicit

## 2026-04-10 additions

### Artifact integrity over incremental improvisation
A generated delivery artifact must either contain every touched repository file or provide one deterministic apply script that writes every touched repository file. Partial artifacts are treated as invalid.

### Contract-preserving changes
If a feature spans route, builder, and tests, the bolt must update those layers coherently. It is not acceptable to patch one layer and infer the rest.

### Root-cause analysis before the next artifact
If an artifact fails in apply, import, test, smoke, or quality-gates, Harbor work returns to a verified clean base before another artifact is produced. No patching on top of a broken artifact.

### Use the established harness
New tests should extend the existing fixture and fake-client harness for the surface under change instead of inventing an ad hoc host.
