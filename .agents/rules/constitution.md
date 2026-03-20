# constitution.md: The Brownfield Cartographer

## 1. The Problem

Brownfield development is plagued by "Gravity Wells"—complex, undocumented sections of code where technical debt accumulates and architectural context is lost. Traditional documentation is static and stale, while automated tools often fail to provide the high-level semantic "why" behind the code.

## 2. The Solution

An autonomous intelligence suite that "excavates" codebase architecture like an archaeologist. It maps structural hierarchies, traces data lineage, and uses LLMs to synthesize purpose-driven documentation.

## 3. The Initial Plan

- **Phase 1-3**: Core Agents (`Surveyor`, `Hydrologist`, `Semanticist`) for data extraction.
- **Phase 4-5**: Orchestration layer to unify ingestion and state management.
- **Phase 6**: Frontend "Sector Detail View" with interactive visualizations.
- **Phase 7**: Hardening, stabilization, and full-repository stress testing.

## 4. Progress & Milestones

- **[2026-03-12]**: Unified `CartographyOrchestrator` implemented, resolving major ingestion bugs.
- **[2026-03-14]**: Successful ingestion of `networkx/networkx` (7,500+ nodes).
- **[2026-03-16]**: Interactive pyvis-based visualizations wired into the frontend via iframes.

## 5. Current State

The project is in a **Stable High-Performance state**.

- **Backend**: Python 3.13+, `fastapi`, `networkx`, `pyvis`, `pydantic`.
- **Frontend**: React (Vite), `tanstack/react-query`, `lucide-react`, Premium Dark/Cyberpunk CSS.
- **Documentation**: Fully automated generation of `CODEBASE.md` and `ONBOARDING.md`.

## 6. Goal

Become the "Google Maps" for universal legacy codebases—providing real-time, interactive, and semantic navigation for any software system.

## 7. GUI/CLI Parity Mandate

**All future features MUST be implemented in the core service layer first.**

The Brownfield Cartographer maintains 100% feature parity between its GUI and CLI interfaces through a shared core service architecture:

- **Core Service Layer** (`src/core/`): All business logic for analysis, mapping, visualization, and configuration MUST reside here.
- **GUI Layer** (`frontend/`, `src/services/`): Consumes core services for web-based interaction.
- **CLI Layer** (`cartograph.py`): Consumes the same core services for command-line interaction.

**Strict Rules:**
1. No "GUI-only" or "CLI-only" business logic is permitted.
2. Any new functionality must be exposed via both interfaces simultaneously.
3. Display/rendering logic is the ONLY exception (e.g., React components vs. Rich terminal output).
4. Both interfaces must generate identical artifacts (JSON, HTML, Markdown) for the same inputs.

**Enforcement:**
- All new features must include both GUI and CLI implementations.
- Integration tests must verify artifact parity between interfaces.
- Code reviews must reject PRs that violate this mandate.
