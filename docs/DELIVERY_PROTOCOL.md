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

## 2026-04-10 artifact rules

For meaningful multi-file updates, the delivery artifact must additionally provide:
- a unique filename
- the exact expected changed-file set
- an apply step that starts from a verified git base
- no hidden dependency on a previously failed artifact

Preferred modes are:
1. ZIP artifact containing the full changed repository files with canonical paths
2. one deterministic Python apply script that writes every changed repository file

After apply, the changed-file set must be inspected immediately before validation continues.
