# Lessons Learned — T4.5A Delivery and Validation
Stand: 2026-04-10

## Context
T4.5A delivered the project-source-grounded chat baseline, but the path to the final green state exposed several delivery and validation weaknesses that must now become explicit Harbor method.

## What actually went wrong
1. Partial delivery artifacts were treated as if they were complete.
2. A route-level patch was attempted without preserving the existing prompt-builder contract.
3. A new API test was first attached to the wrong fixture and later under-wired relative to the established fake-client harness.
4. Failed artifacts were followed by further artifacts before the underlying root cause had been isolated from a clean base.
5. File-level accountability was too weak: it was not checked early enough that the artifact changed exactly the expected files.

## What fixed the situation
1. return to a verified clean repository base
2. snapshot the exact source files involved
3. re-cut one deterministic patch pinned to the clean base
4. preserve the existing builder contract and extend it minimally
5. attach the new test to the existing DB-backed and fake-client-aware harness
6. inspect the exact changed-file set immediately after apply
7. validate in this order: targeted pytest, relevant smokes, then quality-gates

## Permanent methodology changes
- `origin/main` remains the single source of truth.
- For multi-file updates, prefer full-file ZIP artifacts or one deterministic apply script.
- No new artifact after failure without reset and root-cause analysis from a verified base.
- No route-only patches when the real change spans builder, route, and tests.
- Reuse the established fixture and fake-client harness before inventing new test hosts.
- Confirm the exact changed-file set before spending time on deeper validation.

## Confirmed outcome
T4.5A is now locally green on branch `bolt/t4-5a-project-source-grounded-chat-baseline-v2`, and the next planned product bolt remains `T4.5B — source attribution / source visibility in chat`.
