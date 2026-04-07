# Harbor Postgres Baseline v0.1

Status: T1.2 baseline

## Role of Postgres

Postgres remains the Harbor system of record target.

At T1.2, Harbor introduces the configuration and wiring needed to move toward that target without yet depending on a live database for all development.

## Current configuration fields

- `HARBOR_POSTGRES_HOST`
- `HARBOR_POSTGRES_PORT`
- `HARBOR_POSTGRES_DB`
- `HARBOR_POSTGRES_USER`
- `HARBOR_POSTGRES_PASSWORD`
- `HARBOR_POSTGRES_ECHO`
- `HARBOR_POSTGRES_POOL_PRE_PING`

## Redaction rule

Harbor may display a redacted target such as:

`postgresql+psycopg://user:***@host:5432/dbname`

It must not display raw secrets in logs, operator commands, or public endpoints.

## Current readiness posture

### Configured = false
This is acceptable during local bootstrap.

Harbor must still:
- start
- pass quality gates
- report runtime settings honestly
- report DB status honestly

### Configured = true
Harbor may optionally check connectivity.

A failed connectivity check must fail loudly in the DB status path, not silently degrade into “everything is fine”.

## Next expected evolution

After T1.2, Postgres will be used by the first true Harbor domain slice:

- project registry persistence
- migrations for first domain tables
- project CRUD baseline
