# AGENT.md: Governance & Collaboration Rules

This document serves as the primary instructions for any AI agents collaborating on "The Brownfield Cartographer".

## 🤖 Core Directives

1. **Never Bypass Orchestration**: All architectural changes must flow through `CartographyOrchestrator`. Direct agent-to-file manipulation without updating the `KnowledgeGraph` is prohibited.
2. **AST over Regex**: When analyzing code, use formal AST parsing. Regex is only permitted for non-structural text analysis.
3. **Graph Integrity**: Every node added to the `KnowledgeGraph` must include a `node_type` and relevant metadata (e.g., `loc`, `complexity`, `language`).
4. **Artifact Discipline - ROOT STORAGE ONLY**: 
   - **CRITICAL**: Analysis outputs MUST be saved in **root `.cartography/<project_name>/`** directory.
   - **NEVER** create `.cartography/` inside `targets/` or cloned repo directories.
   - The `ArchivistAgent` must accept `output_dir` parameter from `CartographyOrchestrator`.
   - Do not litter the root or `.git` folders with analysis artifacts.
5. **Visual Consistency**: The frontend uses a "Cyberpunk Premium" aesthetic (Gold `#d4af35`, Dark Blue `#0a0f18`, Slate `#1e293b`). Adhere to this palette for all UI updates.
6. **Test-Driven Hardening**: All service or agent modifications must pass existing integration tests (`tests/integration/`).
7. **Multi-Interface Compatibility**: All changes must work correctly across GUI, CLI (`cartograph.py`), and Interactive CLI (`cli.py`). Test all three interfaces before marking work complete.

## 🛠️ Implementation Strategy

- **Agents as Specialized Modules**: Each agent (`Surveyor`, `Hydrologist`, etc.) should remain focused on its specific domain.
- **State via JSON**: Use `knowledge_graph.json` as the exchange format between backend and frontend.
- **Visualization via Iframe**: Complex graph visualizations are generated as standalone HTML by `VisualizerAgent` and embedded via iframe in React. Do not attempt to re-implement pyvis logic in React components.

## 📜 Source of Truth

- **Project Goal**: Refer to `constitution.md`.
- **Current Tasks**: Refer to `task.md` (artifact directory).
- **Established Patterns**: Refer to `CONTEXT_BACKUP.md`.

## 🔄 Multi-Interface Parity Mandate

**Core Principle:** All business logic MUST reside in `src/core/` services and work identically across **all three interfaces**.

### Three Interfaces

1. **GUI** (`main.py gui`) - FastAPI + React frontend
2. **CLI** (`cartograph.py`) - Typer-based one-shot commands
3. **Interactive CLI** (`cli.py`) - REPL-style interactive commands

### Implementation Rules

When implementing new features:

1. **Start with Core Services**: Implement all analysis, mapping, or data generation logic in `src/core/` or `src/orchestrator.py`.
2. **Expose via All Interfaces**: Add corresponding endpoints/commands to GUI, CLI, and Interactive CLI.
3. **Verify Artifact Parity**: Ensure all three interfaces generate **identical** JSON/HTML/Markdown outputs to the **same location** (`.cartography/<project_name>/`).
4. **No Interface-Specific Logic**: Business logic in GUI services, CLI commands, or REPL commands is prohibited.
5. **Test All Three**: Before marking work complete, verify functionality in:
   - GUI: `python main.py gui` → Navigate to `http://127.0.0.1:5000`
   - CLI: `uv run python cartograph.py analyze <repo>`
   - Interactive CLI: `python cli.py` → `/analyze <repo>`

### Allowed Interface-Specific Code

- **GUI**: React components, FastAPI route handlers (routing only), WebSocket formatting, progress callbacks
- **CLI**: Typer command definitions, Rich console formatting, progress bars, table rendering
- **Interactive CLI**: REPL command parsing, Rich console output, command history, autocomplete

### Prohibited

- Duplicating analysis logic across interfaces
- Implementing features in only one or two interfaces
- Divergent artifact generation between interfaces
- Creating `.cartography/` folders in different locations per interface
- Different file naming conventions per interface

### Artifact Storage Rules

**CRITICAL PATH ALIGNMENT:**

```python
# ✅ CORRECT - All interfaces use this pattern
project_name = determine_project_name(repo_input)  # e.g., "dbt-labs_jaffle_shop"
out_dir = Path.cwd() / ".cartography" / project_name
orchestrator = CartographyOrchestrator(repo_path, out_dir=out_dir)

# ❌ WRONG - Never create .cartography inside repo
out_dir = repo_path / ".cartography"  # PROHIBITED

# ❌ WRONG - Never use different paths per interface
if is_gui:
    out_dir = Path(".cartography") / project_name
else:
    out_dir = Path("targets") / repo_name / ".cartography"  # PROHIBITED
```

**Required Artifacts (all interfaces must generate these):**
- `knowledge_graph.json`
- `semantic_index.json`
- `CODEBASE.md`
- `onboarding_brief.md`
- `cartography_trace.jsonl`
- `module_graph.html` (optional but recommended)
- `lineage_graph.html` (optional but recommended)

### Testing Checklist

Before completing any feature:

- [ ] Core logic implemented in `src/core/` or `src/orchestrator.py`
- [ ] GUI endpoint added and tested
- [ ] CLI command added and tested
- [ ] Interactive CLI command added and tested
- [ ] All three interfaces save artifacts to `.cartography/<project_name>/`
- [ ] Artifact content is identical across interfaces
- [ ] No `.cartography/` folders created inside `targets/`
- [ ] Error handling works consistently across interfaces
- [ ] Progress reporting works in all interfaces (WebSocket for GUI, Rich for CLIs)
