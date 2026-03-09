# CODEBASE.md: apache_airflow.git Context

## Architecture Overview
This repository (apache_airflow.git) is a polyglot codebase analyzed by The Brownfield Cartographer.

## Critical Path (Most Imported Modules)
- `mod:providers-summary-docs/conf.py`
- `mod:airflow-core/hatch_build.py`
- `mod:dev/assign_cherry_picked_prs_with_milestone.py`
- `mod:dev/prune_old_dirs.py`
- `mod:dev/prepare_bulk_issues.py`

## Data Sources & Sinks
Sources: Singer Taps, Databases via SQLAlchemy
Sinks: Singer Targets, Snowflake, BigQuery

## Complexity & Debt
Circular Dependencies: 0 detected.
