# Local Operator Surface v0.1

Status: T1.1 baseline

## 1. Purpose

This document defines the minimum local operator command surface for Harbor.

The goal is to make local execution reproducible and easier to hand off across
chat sessions and engineering steps.

## 2. Required local tasks

The T1.1 baseline includes these commands:

- `quality-gates`
- `show-settings`
- `smoke-local`
- `run-dev`

## 3. Canonical command entry

The canonical entry for local operator tasks is:

```powershell
python .\tools\task_runner.py <command>
```

## 4. Why this matters

This keeps local engineering from drifting into ad hoc command memory.

The operator surface is part of the system contract, not a side note.

## 5. Current command meanings

### `quality-gates`
Runs compile, lint, and test validation.

### `show-settings`
Prints the effective runtime settings summary.

### `smoke-local`
Runs root, health, and runtime checks through an in-process client.

### `run-dev`
Starts the local uvicorn development server with settings-derived host, port,
and reload behavior.

## 6. Later expansion

Later phases may add:

- migration commands
- DB bootstrap commands
- project seeding commands
- snapshot inspection commands
- VPS smoke commands
