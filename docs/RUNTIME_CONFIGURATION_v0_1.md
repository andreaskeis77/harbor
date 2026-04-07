# Harbor Runtime Configuration v0.1

Status: accepted runtime configuration baseline

## Purpose

Harbor runtime configuration must be explicit, typed, and inspectable.

## Current configuration areas

- app identity
- environment
- host / port / reload
- data root
- artifact root
- var root
- log root
- report root
- Postgres host / port / db / user / password / echo / pool pre-ping

## Configuration sources

1. code defaults
2. `.env`
3. environment variables

## Important rule

Secrets must not be committed to Git.

`.env.example` documents the expected shape, but real credentials belong only in local non-tracked `.env` files or environment variables.
