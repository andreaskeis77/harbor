# Handoff Manifest

Purpose: Define how Harbor preserves continuity across chats and work sessions.

## 1. Handoff rule

A handoff file is required whenever:
- a planning baseline changes materially
- a new implementation tranche is completed
- a release-like checkpoint is reached
- work is paused and likely to resume in a later chat

## 2. What a handoff must contain

Each handoff should state:
- title / phase / date
- scope completed
- files added or updated
- what was verified
- what was not verified
- current accepted state
- next recommended step
- active risks or cautions

## 3. Relationship to other docs

- `MASTERPLAN.md` = long-range direction
- `PROJECT_STATE.md` = current validated state
- `HANDOFF_*.md` = transfer note for a specific checkpoint

A handoff must not replace either the masterplan or project state.

## 4. Naming convention

Recommended pattern:

`HANDOFF_<PHASE>_<short_topic>_<YYYY-MM-DD>.md`

Example:

`HANDOFF_A0_1A_masterplan_and_handoff_governance_2026-04-06.md`

## 5. Minimum continuity rule

If work is handed to a new chat, the receiving chat should first read:

1. `docs/MASTERPLAN.md`
2. `docs/PROJECT_STATE.md`
3. latest file under `docs/_handoff/`

## 6. Governance update rule

Every major bolt should update:
- masterplan if long-range direction changed or was clarified
- project state to reflect actual accepted state
- a handoff file for the bolt itself
