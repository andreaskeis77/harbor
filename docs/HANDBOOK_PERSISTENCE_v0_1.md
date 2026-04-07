# Handbook Persistence v0.1

## Scope

T1.4 introduces the second real Harbor product slice after project registration:
versioned handbook persistence per project.

## What this slice adds

- persisted handbook version records linked to a project
- current-handbook read surface
- write-new-version handbook surface
- handbook version-history surface
- tests for empty state, first version, second version, and history ordering

## API surface

- `GET /api/v1/projects/{project_id}/handbook`
- `PUT /api/v1/projects/{project_id}/handbook`
- `GET /api/v1/projects/{project_id}/handbook/versions`

## Behavioral rules

- a project may initially have no handbook versions
- reading the current handbook in that state returns `has_handbook=false` and `current=null`
- every write creates a new version row
- the current handbook is the row with the highest `version_number` for that project
- handbook history is returned newest first

## Out of scope

This slice does not yet add:

- handbook section-level structure
- handbook diff rendering
- handbook approval workflow
- blueprint linkage to handbook modules
- source or evidence linkage from handbook sections

## Why this matters

The handbook is the central steering object for Harbor. Persisting it as a versioned system-of-record object is the point where Harbor moves from a project registry to a real research workspace.
