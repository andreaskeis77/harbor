# Project Registry Vertical Slice v0.1

## Purpose

T1.3 introduces the first real Harbor product object with persistence, API surface, migration baseline, and tests.

## Scope

Included in T1.3:

- first persisted model: `Project`
- project registry table
- ORM model
- Pydantic request/response schemas
- create/list/get project API
- first migration
- vertical slice tests
- local operator smoke for the project slice

## Project fields in this slice

The initial slice keeps the object intentionally small:

- `project_id`
- `title`
- `short_description`
- `status`
- `project_type`
- `blueprint_status`
- `created_at`
- `updated_at`

## Why this slice matters

This is the first point where Harbor stops being only runtime infrastructure and starts being a persisted product system.

The slice proves:

- persistence wiring
- request/response validation
- service layering
- testable vertical flow
- future compatibility for handbook and source slices

## Explicit exclusions

Not part of T1.3:

- handbook persistence
- project review state model
- project archival logic beyond field values
- sources
- source snapshots
- UI
- GPT integration
