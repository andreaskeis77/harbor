# Harbor Handoff Guide v0.1

## Purpose

This guide defines how Harbor handoffs should be written.

A handoff is not just a summary. It must make the current state understandable and restartable.

## Every handoff should contain

1. phase / tranche identifier
2. date
3. status
4. completed scope
5. files added or changed
6. validated state
7. important open decisions
8. recommended next step
9. risks or caveats

## Naming convention

Recommended file naming:

`HANDOFF_<PHASE>_<short_description>_<YYYY-MM-DD>.md`

Example:

`HANDOFF_A0_1_product_scope_baseline_2026-04-06.md`

## Handoff quality rule

A handoff is only useful if another session can understand:

- what was decided
- what is not decided
- what files matter
- what should happen next
