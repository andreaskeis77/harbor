# Harbor Delivery Protocol v0.1

## Purpose

This protocol defines how Harbor artifacts should be delivered during the build-out.

## Default delivery form

Preferred default:

- complete files
- correct relative repository paths
- one clearly named package or folder tree
- exact DEV-LAPTOP apply instructions

## Package naming rule

External delivery packages should use unique names so that repeated deliveries do not get mixed up.

Recommended pattern:

`harbor_<scope_or_tranche>_<YYYY-MM-DD>.zip`

Examples:

- `harbor_bootstrap_A0_1_2026-04-06.zip`
- `harbor_domain_model_A0_2_2026-04-07.zip`

## Internal repository naming rule

Inside the repository, canonical file names should remain stable unless there is a real reason to rename them.
The package name should be unique; the repository structure should stay clean.
