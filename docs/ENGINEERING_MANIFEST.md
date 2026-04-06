# Harbor Engineering Manifest v0.1

## 1. Purpose

This manifest defines the top-level engineering rules for Harbor.

Harbor is not a throwaway notebook project. It is intended to become a durable, inspectable,
operable research system with strong emphasis on project separation, evidence integrity,
traceability, recoverability, and documentation quality.

## 2. Priority order

When goals conflict, the order is:

1. correctness and provenance integrity
2. project separation and state clarity
3. reproducibility and recoverability
4. operational robustness
5. understandability and maintainability
6. testability and observability
7. implementation speed
8. elegance or technical novelty

## 3. Core principles

### 3.1 Small tranches
Work is delivered in clearly scoped, reviewable tranches.

### 3.2 Docs are part of the system
If docs are stale, the system is partially stale.

### 3.3 No blind trust in AI output
AI-generated structure, code, summaries, or classifications are untrusted until reviewed.

### 3.4 Source, evidence, and analysis are different things
Harbor must never silently collapse raw sources, extracted evidence, and AI-generated
analysis into one undifferentiated truth layer.

### 3.5 Project partitioning is sacred
Cross-project contamination is a system defect, not a cosmetic issue.

### 3.6 Resume and review are first-class requirements
The system must be designed so that a paused project can be resumed without hidden context.

### 3.7 Explicit reuse only
Blueprint reuse must be deliberate and documented.

## 4. Architecture rules

### 4.1 One canonical backend
The website and the Custom GPT must use the same backend state.

### 4.2 System of record
Postgres is the planned system of record unless a later ADR changes that decision.

### 4.3 Metadata-first posture
Runs, source changes, review status, and provenance are product assets, not implementation detail.

### 4.4 Snapshot before inference
Where feasible, Harbor should store the source state used for later reasoning.

### 4.5 No silent architecture drift
Important architectural direction changes require explicit documentation.

## 5. Delivery rules

### 5.1 Complete files by default
Harbor changes should be delivered as complete files with clear target paths.

### 5.2 Explicit execution context
Commands must explicitly state whether they run on:
- DEV-LAPTOP
- VPS-USER
- VPS-ADMIN

### 5.3 Validation before progress
A tranche is not green if required validation is still red.

## 6. Definition of done for a tranche

A tranche is done only when:

- scope is clear
- files are internally consistent
- documentation is updated
- validation expectations are stated
- next step is clear
- no critical ambiguity is hidden
