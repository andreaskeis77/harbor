# Harbor Delivery Protocol

## Default delivery mode

Meaningful Harbor updates should be delivered as:
- a downloadable ZIP artifact
- canonical repository paths
- exact PowerShell apply commands
- exact git commands
- exact cleanup commands

## Naming rule

Downloaded delivery packages should use unique filenames.
Repository filenames should remain canonical whenever possible.

Example:
- download artifact: `harbor_t1_0_bootstrap_impl_T1_0_2026-04-06.zip`
- repo file: `docs/PROJECT_STATE.md`
