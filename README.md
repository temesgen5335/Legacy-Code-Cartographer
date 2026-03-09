# The Brownfield Cartographer 🗺️

Engineering Codebase Intelligence Systems for Rapid FDE Onboarding.

The Brownfield Cartographer is a multi-agent system that ingests any GitHub repository or local path and produces a living, queryable knowledge graph of the system's architecture, data flows, and semantic structure.

## Features

-   **Structural Analysis (Surveyor Agent)**: Uses `tree-sitter` for language-agnostic AST parsing. Builds module import graphs, identifies architectural hubs (PageRank), and detects circular dependencies.
-   **Data Lineage (Hydrologist Agent)**: Specialized for data engineering. Analyzes data flows across Python (pandas, PySpark), SQL (`sqlglot`), and configuration boundaries.
-   **Semantic Analysis (Semanticist Agent)**: Uses Gemini LLM to generate business-oriented purpose statements for every module.
-   **Semantic Search (Semantic Index)**: Vector-indexed knowledge base powered by **Qdrant** and Gemini embeddings.
-   **Living Context (Archivist Agent)**: Produces `CODEBASE.md` and `onboarding_brief.md` for instant architectural awareness.

## Quick Start

### Prerequisites

-   [uv](https://github.com/astral-sh/uv) for dependency management.
-   Google Gemini API Key (`GEMINI_API_KEY`).
-   Qdrant Cluster (Endpoint and API Key).

### Installation

```bash
git clone <this-repo-url>
cd "The Brownfield Cartographer"
uv sync
```

### Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_key
QDRANT_API_KEY=your_qdrant_key
QDRANT_CLUSTER_ENDPOINT=your_qdrant_endpoint
```

### Usage

Analyze a GitHub repository or local path:

```bash
# Analyze a GitHub repo
uv run main.py https://github.com/meltano/meltano #example

# Analyze a local path
uv run main.py /path/to/your/project
```

Results are stored in `.cartography/<project_name>/`.

## Architecture

1.  **Surveyor**: Static structure analyst.
2.  **Hydrologist**: Data flow & lineage analyst.
3.  **Semanticist**: LLM-powered purpose analyst.
4.  **Archivist**: Living context maintainer.

## License

MIT License - see [LICENSE](LICENSE) for details.
