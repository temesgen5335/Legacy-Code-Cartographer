# AGENT.md: Governance & Collaboration Rules

This document serves as the primary instructions for any AI agents collaborating on "The Brownfield Cartographer".

## 🤖 Core Directives

1. **Never Bypass Orchestration**: All architectural changes must flow through `CartographyOrchestrator`. Direct agent-to-file manipulation without updating the `KnowledgeGraph` is prohibited.
2. **AST over Regex**: When analyzing code, use formal AST parsing. Regex is only permitted for non-structural text analysis.
3. **Graph Integrity**: Every node added to the `KnowledgeGraph` must include a `node_type` and relevant metadata (e.g., `loc`, `complexity`, `language`).
4. **Artifact Discipline**: Analysis outputs MUST be saved in `.cartography/<project_name>/`. Do not litter the root or `.git` folders.
5. **Visual Consistency**: The frontend uses a "Cyberpunk Premium" aesthetic (Gold `#d4af35`, Dark Blue `#0a0f18`, Slate `#1e293b`). Adhere to this palette for all UI updates.
6. **Test-Driven Hardening**: All service or agent modifications must pass existing integration tests (`tests/integration/`).

## 🛠️ Implementation Strategy

- **Agents as Specialized Modules**: Each agent (`Surveyor`, `Hydrologist`, etc.) should remain focused on its specific domain.
- **State via JSON**: Use `knowledge_graph.json` as the exchange format between backend and frontend.
- **Visualization via Iframe**: Complex graph visualizations are generated as standalone HTML by `VisualizerAgent` and embedded via iframe in React. Do not attempt to re-implement pyvis logic in React components.

## 📜 Source of Truth

- **Project Goal**: Refer to `constitution.md`.
- **Current Tasks**: Refer to `task.md` (artifact directory).
- **Established Patterns**: Refer to `CONTEXT_BACKUP.md`.

## 🔄 GUI/CLI Parity Mandate

**Core Principle:** All business logic MUST reside in `src/core/` services.

When implementing new features:
1. **Start with Core Services**: Implement all analysis, mapping, or data generation logic in `src/core/`.
2. **Expose via Both Interfaces**: Add corresponding endpoints/commands to both GUI and CLI.
3. **Verify Artifact Parity**: Ensure both interfaces generate identical JSON/HTML/Markdown outputs.
4. **No Interface-Specific Logic**: Business logic in GUI services or CLI commands is prohibited.

**Allowed Interface-Specific Code:**
- GUI: React components, FastAPI route handlers (routing only), WebSocket formatting
- CLI: Typer command definitions, Rich console formatting, progress display

**Prohibited:**
- Duplicating analysis logic in GUI and CLI
- Implementing features in only one interface
- Divergent artifact generation between interfaces
