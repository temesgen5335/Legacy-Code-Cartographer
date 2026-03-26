# The Legacy Code Cartographer

Engineering Codebase Intelligence Systems for Rapid FDE Onboarding.

The Legacy Code Cartographer / Brownfield Cartographer is a multi-agent system that ingests any GitHub repository or local path and produces a living, queryable knowledge graph of the system's architecture, data flows, and semantic structure.

## Features

-   **Structural Analysis (Surveyor Agent)**: Uses `tree-sitter` for language-agnostic AST parsing. Builds module import graphs, identifies architectural hubs (PageRank), and detects circular dependencies.
-   **Data Lineage (Hydrologist Agent)**: Specialized for data engineering. Analyzes data flows across Python (pandas, PySpark), SQL (`sqlglot`), and configuration boundaries.
-   **Semantic Analysis (Semanticist Agent)**: Uses Gemini LLM to generate business-oriented purpose statements for every module.
-   **Semantic Search (Semantic Index)**: Vector-indexed knowledge base powered by **Qdrant** and Gemini embeddings.
-   **Living Context (Archivist Agent)**: Produces `CODEBASE.md` and `onboarding_brief.md` for instant architectural awareness.
-   **Interactive REPL**: Persistent command-line interface with `/command` syntax for seamless workflow.
-   **Web GUI**: React-based dashboard with real-time WebSocket updates and interactive visualizations.

## Quick Start

### Prerequisites

-   [uv](https://github.com/astral-sh/uv) for dependency management.
-   Google Gemini API Key (`GEMINI_API_KEY`).
-   Qdrant Cluster (Endpoint and API Key) - Optional for semantic search.

### Installation

```bash
git clone <this-repo-url>
cd "The-Brownfield-Cartographer"
uv pip install -e .
```

This installs all dependencies including:
- Core analysis libraries (networkx, tree-sitter, sqlglot)
- LLM integration (google-genai, openai)
- CLI tools (typer, rich)
- Web framework (fastapi, uvicorn)
- Frontend dependencies (React via npm)

### Configuration

#### Option 1: Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_key
QDRANT_API_KEY=your_qdrant_key          # Optional
QDRANT_CLUSTER_ENDPOINT=your_endpoint   # Optional
```

#### Option 2: Interactive CLI Configuration

```bash
uv run python cli.py
# Then use /config_show to view current settings
```

Or use the Typer CLI:

```bash
uv run python cartograph.py config set --key llm.provider --value gemini
uv run python cartograph.py config set --key llm.api_key --value YOUR_KEY
```

Configuration is stored in `~/.cartographer/config.json`.

## Usage

The Brownfield Cartographer offers **three interfaces** with 100% feature parity:

### 1. Interactive REPL (Recommended)

The persistent interactive session allows you to execute multiple commands without re-invoking Python:

```bash
uv run python cli.py
```

**Interactive Commands:**

```
Legacy-Code-Cartographer > /help              # Show all commands
Legacy-Code-Cartographer > /list              # List analyzed projects
Legacy-Code-Cartographer > /analyze ./my-repo # Analyze a repository
Legacy-Code-Cartographer > /summary my-repo   # Show project summary
Legacy-Code-Cartographer > /map my-repo --view structure  # Generate graphs
Legacy-Code-Cartographer > /artifacts my-repo # List artifact paths
Legacy-Code-Cartographer > /config_show       # Display configuration
Legacy-Code-Cartographer > /whereami          # Show current directory
Legacy-Code-Cartographer > /clear             # Clear terminal
Legacy-Code-Cartographer > /exit              # Exit session
```

**Features:**
- ✅ Persistent session state
- ✅ Direct service integration (no subprocess overhead)
- ✅ Robust error handling (Ctrl+C cancels operation, doesn't crash)
- ✅ Rich terminal output with colors and tables
- ✅ `/command` syntax for intuitive workflow

### 2. Typer CLI (One-Shot Commands)

For scripting and automation, use the Typer-based CLI:

```bash
# Analyze a repository
uv run python cartograph.py analyze ./my-project
uv run python cartograph.py analyze https://github.com/user/repo.git

# List all projects
uv run python cartograph.py list

# View project summary
uv run python cartograph.py summary my-project --detailed

# Generate visualizations
uv run python cartograph.py map my-project --view structure
uv run python cartograph.py map my-project --view lineage --format json

# Manage configuration
uv run python cartograph.py config show
uv run python cartograph.py config set --key llm.model --value gemini-2.0-flash-exp
```

**All commands support:**
- `--help` for detailed usage
- `--verbose` for detailed logging
- `--full` for non-incremental analysis

### 3. Web GUI

Launch the interactive web dashboard:

```bash
uv run python main.py gui
```
For launching in a new build
```bash
uv run python main.py gui --build
```
Then navigate to `http://localhost:5001` in your browser.

**GUI Features:**
- 🎨 Interactive graph visualizations (pyvis-powered)
- 📊 Real-time analysis progress via WebSockets
- 📝 Rendered markdown documentation
- 🔍 Searchable semantic index
- 🗺️ Module structure and data lineage views

### 4. Headless Analysis (Legacy)

For backward compatibility, direct analysis is still supported:

```bash
# Analyze a GitHub repo
uv run python main.py ingest https://github.com/meltano/meltano

# Analyze a local path
uv run python main.py ingest /path/to/your/project
```

Results are stored in `.cartography/<project_name>/`.

## Output Artifacts

All analysis results are stored in `.cartography/<project_name>/`:

```
.cartography/my-project/
├── knowledge_graph.json      # Unified NetworkX graph (nodes + edges)
├── module_graph.html         # Interactive module structure visualization
├── lineage_graph.html        # Interactive data lineage visualization
├── CODEBASE.md              # Comprehensive architectural documentation
├── ONBOARDING_BRIEF.md      # Quick-start guide for new developers
├── semantic_index.json      # Module metadata with LLM-generated purposes
└── trace.json               # Analysis execution trace
```

**Access artifacts via:**
- **REPL**: `/artifacts <project>`
- **CLI**: Files are in `.cartography/<project>/`
- **GUI**: Navigate to project dashboard

## Architecture

### Multi-Agent System

1.  **Surveyor**: Static structure analyst using tree-sitter AST parsing
2.  **Hydrologist**: Data flow & lineage analyst for Python/SQL
3.  **Semanticist**: LLM-powered semantic purpose generator
4.  **Archivist**: Living documentation maintainer
5.  **Visualizer**: Interactive graph renderer (pyvis)
6.  **Navigator**: Advanced query engine (LangGraph)

### Core Service Layer

All business logic resides in `src/core/`:
- `CartographyService`: Analysis orchestration
- `VisualizationService`: Graph generation
- `ConfigService`: Settings management

**100% Feature Parity**: GUI, REPL, and CLI all use the same core services, ensuring identical outputs.

## Advanced Usage

### Incremental Analysis

By default, the system performs incremental analysis (only re-analyzes changed files):

```bash
# REPL
/analyze ./my-repo

# CLI
uv run python cartograph.py analyze ./my-repo --incremental
```

For full re-analysis:

```bash
# REPL
/analyze ./my-repo --full

# CLI
uv run python cartograph.py analyze ./my-repo --full
```

### Custom Output Directory

```bash
# CLI only
uv run python cartograph.py analyze ./my-repo --output /custom/path
```

### Export Graph Data as JSON

```bash
# REPL
/map my-project --view structure --format json

# CLI
uv run python cartograph.py map my-project --view structure --format json
```

### Batch Analysis

```bash
# Using CLI in a loop
for repo in repo1 repo2 repo3; do
    uv run python cartograph.py analyze ./$repo
done
```

### CI/CD Integration

```yaml
# .github/workflows/analyze.yml
- name: Analyze Codebase
  run: |
    uv pip install -e .
    uv run python cartograph.py analyze . --full
    uv run python cartograph.py map $(basename $(pwd)) --view both --format json
```

## Troubleshooting

### API Key Not Set

**Error**: `API key not configured`

**Solution**:
```bash
# Via REPL
/config_show  # Check current config

# Via CLI
uv run python cartograph.py config set --key llm.api_key --value YOUR_KEY

# Or set environment variable
export GEMINI_API_KEY=your_key
```

### Project Not Found

**Error**: `Project 'xyz' not found`

**Solution**:
```bash
# List available projects
# REPL: /list
# CLI: uv run python cartograph.py list

# Analyze the project first
# REPL: /analyze ./path/to/project
# CLI: uv run python cartograph.py analyze ./path/to/project
```

### Python Version Issues

The project requires Python 3.13+ for optimal performance. Python 3.14 is fully supported.

```bash
python3 --version  # Should be 3.13 or higher
```

### Module Import Errors

If you see `ModuleNotFoundError`:

```bash
# Reinstall dependencies
uv pip install -e .

# Or use uv run to ensure correct environment
uv run python cli.py
```

### REPL Session Frozen

If the REPL appears frozen:
- Press `Ctrl+C` to cancel the current operation
- Press `Ctrl+D` or type `/exit` to quit
- Use `/clear` to reset the terminal

## Documentation

- **CLI Guide**: See `CLI_README.md` for detailed CLI documentation
- **Constitution**: See `.agents/rules/constitution.md` for architectural principles
- **Agent Rules**: See `.agents/rules/agent.md` for development guidelines
- **Implementation Summary**: See `IMPLEMENTATION_SUMMARY.md` for technical details

## License

MIT License - see [LICENSE](LICENSE) for details.
