# Handoff — T1.4 Handbook Persistence Baseline

Status: Ready for handoff  
Phase: T1.4  
Date: 2026-04-07

## Scope of this tranche

T1.4 adds the second real Harbor product slice after project registration:
versioned handbook persistence per project.

## Delivered in this tranche

- handbook version persistence model
- handbook service module
- handbook API routes for current, write, and version history
- migration for handbook version table
- smoke command for handbook slice
- tests covering empty state and version creation/history

## Local proof expectation

- `python .\tools\task_runner.py smoke-handbook-slice`
- `python .\tools\task_runner.py quality-gates`
- handbook endpoints work when a DB URL is configured and the migration has been applied

## Recommended next step

T1.5 — Source and project-source first slice
