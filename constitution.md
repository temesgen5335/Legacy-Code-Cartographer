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

## 6. The Long-Term Vision

Become the "Google Maps" for legacy codebases—providing real-time, interactive, and semantic navigation for any software system.
