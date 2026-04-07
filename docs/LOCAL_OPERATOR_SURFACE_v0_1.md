# Harbor Local Operator Surface v0.1

Status: accepted local operator baseline

## Purpose

This document describes the local command surface for Harbor operators on the DEV-LAPTOP.

## Current commands

- `python .\tools\task_runner.py show-settings`
- `python .\tools\task_runner.py show-db-settings`
- `python .\tools\task_runner.py db-status`
- `python .\tools\task_runner.py smoke-local`
- `python .\tools\task_runner.py quality-gates`
- `python .\tools\task_runner.py run-dev`

## Design rule

The operator surface is intentionally small, explicit, and Windows-friendly.

It exists to reduce ad-hoc command drift and to make later VPS and runbook work easier.

## Current boundaries

The operator surface is currently for:

- local runtime inspection
- local smoke checks
- quality-gate execution
- local dev server startup
- persistence-configuration inspection

It is not yet a full production operator console.
