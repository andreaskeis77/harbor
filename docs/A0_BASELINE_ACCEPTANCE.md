# A0 Baseline Acceptance

Status: Draft acceptance control document  
Phase: A0.C1

## 1. Purpose

This document defines what must be true before Harbor moves from its
documentation-first A0 phase into runtime implementation.

It exists to prevent scope drift and to avoid starting T1.0 from an unclear
or contradictory baseline.

## 2. A0 baseline document set

The intended A0 baseline includes the following documents:

### Core governance
- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- `docs/HANDOFF_MANIFEST.md`
- `docs/HANDOFF_GUIDE.md`
- `docs/ENGINEERING_MANIFEST.md`
- `docs/WORKING_AGREEMENT.md`
- `docs/DELIVERY_PROTOCOL.md`
- `docs/VALIDATION_PROTOCOL.md`

### Product and architecture baseline
- `docs/PRODUCT_SCOPE_v0_1.md`
- `docs/DOMAIN_MODEL_v0_1.md`
- `docs/USER_STORIES_v0_1.md`
- `docs/FUNCTIONAL_REQUIREMENTS_v0_1.md`
- `docs/HANDBOOK_SPEC_v0_1.md`
- `docs/BLUEPRINT_MODEL_v0_1.md`
- `docs/WORKFLOW_MODEL_v0_1.md`
- `docs/SYSTEM_ARCHITECTURE_v0_1.md`
- `docs/RUNTIME_BOUNDARIES_v0_1.md`
- `docs/TECHNICAL_BOOTSTRAP_v0_1.md`
- `docs/REPOSITORY_SCAFFOLDING_v0_1.md`

## 3. Acceptance criteria

A0 is accepted only when all of the following are true:

1. **Presence**
   - the intended baseline files actually exist in the repository

2. **Consistency**
   - no major contradiction remains across:
     - product scope
     - domain model
     - functional requirements
     - system architecture
     - technical bootstrap

3. **Traceable execution order**
   - the order from A0 to T1.0 and beyond is visible in `MASTERPLAN.md`

4. **Current-state honesty**
   - `PROJECT_STATE.md` reflects the real accepted state, not just aspirational plans

5. **Handoff continuity**
   - the latest handoff accurately states:
     - what is accepted
     - what is not yet accepted
     - what the next recommended step is

## 4. Explicit non-acceptance signals

A0 is not accepted if any of the following is true:

- core A0 files are missing from the repo
- multiple docs imply different implementation start lines
- the repo state and the handoff state disagree materially
- T1.0 is started without an explicit accepted A0 baseline note

## 5. Acceptance output

When A0 is accepted, record it in a future handoff with wording equivalent to:

- A0 baseline accepted
- T1.0 implementation may begin from the accepted documentation baseline
