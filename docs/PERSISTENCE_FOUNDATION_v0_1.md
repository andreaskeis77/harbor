# Harbor Persistence Foundation v0.1

Status: T1.2 baseline

## Purpose

This document defines the first persistence-layer baseline for Harbor.

It does **not** yet define Harbor domain tables. It defines the technical spine that later domain persistence must use.

## Objectives of T1.2

- establish a dedicated persistence package
- introduce typed Postgres settings
- introduce SQLAlchemy engine/session boundaries
- introduce declarative base
- prepare migration posture
- expose safe operator and HTTP visibility into DB configuration and readiness

## Current persistence building blocks

### 1. Runtime settings
Harbor runtime settings now include Postgres-specific configuration.

### 2. Engine factory
The engine is built only when Postgres is configured.

### 3. Session factory
The session boundary exists, even though Harbor domain sessions are not yet used by business endpoints.

### 4. Declarative base
A canonical SQLAlchemy declarative base exists for future Harbor models.

### 5. DB status service
A lightweight status service reports:
- whether Postgres is configured
- the redacted connection target
- whether a connectivity check was requested
- the outcome of the check

### 6. Migration baseline
Alembic scaffolding exists so later schema evolution can become disciplined early rather than retrofitted late.

## Explicit non-goals of T1.2

T1.2 does not yet include:

- Harbor domain models
- project tables
- handbook tables
- source tables
- vector search tables
- ingestion persistence

## Exit criteria

T1.2 is successful when:

- runtime settings expose Postgres configuration clearly
- operator commands can show DB posture
- an optional DB connectivity path exists
- the codebase has a clean persistence package boundary
- quality gates remain green
