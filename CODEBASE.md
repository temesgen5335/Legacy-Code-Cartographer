# CODEBASE.md: System Context

## Architecture Overview
Meltano is an ELT orchestration platform written in Python and uses SQL/YAML for plugin configuration.

## Critical Path (Most Imported Modules)
- `mod:noxfile.py`
- `mod:tests/conftest.py`
- `mod:tests/test_meta.py`
- `mod:tests/asserts.py`
- `mod:scripts/alembic_freeze.py`

## Data Sources & Sinks
Sources: Singer Taps, Databases via SQLAlchemy
Sinks: Singer Targets, Snowflake, BigQuery

## Complexity & Debt
Circular Dependencies: 0 detected.
