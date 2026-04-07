# Source Slice v0.1

## Purpose

T1.5 adds the first minimal source surface to Harbor.

This slice introduces two distinct concepts:

- a **global source registry**
- a **project-scoped source attachment**

This preserves Harbor's core rule that information can exist globally while still being evaluated and used inside a project-specific context.

## Scope of T1.5

Included:

- `Source`
- `ProjectSource`
- create/list global sources
- attach/list project sources
- first duplicate-protection for a project/source pair
- first live API proof for project-scoped source attachment

Not yet included:

- crawling
- snapshots
- source content extraction
- search campaigns
- review queues
- monitoring

## API surface

- `POST /api/v1/sources`
- `GET /api/v1/sources`
- `POST /api/v1/projects/{project_id}/sources`
- `GET /api/v1/projects/{project_id}/sources`

## Design rule

A source is global. Its use is project-local.
