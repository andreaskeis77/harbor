# Runtime Configuration v0.1

Status: T1.1 baseline

## 1. Purpose

This document defines the runtime configuration posture for Harbor before domain
persistence is introduced.

## 2. Goals

The runtime configuration model must:

- be typed
- be inspectable
- support local development first
- later extend cleanly to VPS deployment
- separate secrets from tracked repo defaults

## 3. Current posture

The current runtime settings are defined in `src/harbor/config.py` using a typed
settings model.

Configuration sources:

1. code defaults
2. `.env.example` as documentation baseline
3. `.env` for local non-tracked overrides
4. environment variables

## 4. Required settings classes in T1.1

The current baseline includes at least:

- app identity
- app version
- runtime environment name
- host and port
- reload flag
- log level
- API prefix
- local data root
- local var root
- optional Postgres DSN placeholder

## 5. Current non-goals

T1.1 does not yet introduce:

- split settings per environment file family
- secret manager integration
- structured database pool settings
- advanced deployment matrix
- multi-runtime profile inheritance

## 6. Exit criteria

T1.1 runtime configuration is successful when:

- effective settings can be shown locally
- local development can run via typed settings
- runtime directories are created predictably
- `.env` posture is documented and repo-safe
