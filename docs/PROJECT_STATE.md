# Project State

## Current phase

A0.x — Planning and documentation baseline

## Current status summary

Harbor has a documentation-first baseline.

Confirmed on repo:
- A0.1 bootstrap and scope baseline is committed and pushed
- repository exists and tracks `main`
- masterplan governance is being introduced so that long-range direction is held inside the repo and not in transient chat context

Prepared in working conversation but not yet treated as fully validated baseline in this document:
- domain model baseline
- user stories and functional requirements baseline
- handbook / blueprint / workflow baseline
- system architecture / runtime boundary baseline
- technical bootstrap / repository scaffolding baseline

These items may exist as prepared delivery packages, but the project should distinguish between:
- discussed / drafted
- applied locally
- committed and pushed
- accepted as baseline

## Why this distinction matters

Harbor must not lose control over what is:
- merely discussed in chat
- generated as a candidate artifact
- actually present in the repository
- actually accepted as the current baseline

## Canonical planning rule

Harbor uses the following documentation layers:

1. `docs/MASTERPLAN.md`
   - long-range direction
   - phase order
   - major goals
   - deferred topics
   - phase entry/exit logic

2. `docs/PROJECT_STATE.md`
   - current validated state
   - what is truly accepted
   - what is next
   - current risks and open points

3. `docs/_handoff/HANDOFF_*.md`
   - per-step transfer notes
   - evidence of what happened
   - what was verified
   - what still needs action

## Current recommended next step

Before starting T1.0 implementation, consolidate the A0 documentation baseline and decide which A0 documents are officially accepted into the repo baseline.

## Current risks

- confusing drafted artifacts with validated baseline
- losing roadmap continuity across chat handoffs
- starting implementation before the accepted planning surface is stable

## Working recommendation

From this point onward, every meaningful planning or implementation bolt should update:

- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- one new file under `docs/_handoff/`
