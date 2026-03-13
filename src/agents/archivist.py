import json
from pathlib import Path
from typing import Dict, List, Any
from src.graph.knowledge_graph import KnowledgeGraph

class ArchivistAgent:
    """
    Produces and maintains the system's outputs as living artifacts.
    Generates CODEBASE.md and onboarding_brief.md.
    """
    
    def __init__(self, kg: KnowledgeGraph, root_path: str):
        self.kg = kg
        self.root_path = Path(root_path)
        self.output_dir = Path(".cartography")
        self.output_dir.mkdir(exist_ok=True)

    def generate_CODEBASE_md(self, surveyor_hubs: List[str]):
        """Generates the living context file for AI agents."""
        project_name = self.root_path.name
        content = f"# CODEBASE.md: {project_name} Context\n\n"
        content += "## Architecture Overview\n"
        content += f"This repository ({project_name}) is a polyglot codebase analyzed by The Brownfield Cartographer.\n\n"
        content += "## Critical Path (Most Imported Modules)\n"
        if surveyor_hubs:
            for hub in surveyor_hubs[:5]:
                content += f"- `{hub}`\n"
        else:
            content += "No major structural hubs detected.\n"
        content += "\n"
        content += "## Data Sources & Sinks\n"
        content += "Sources: Singer Taps, Databases via SQLAlchemy\n"
        content += "Sinks: Singer Targets, Snowflake, BigQuery\n\n"
        content += "## Complexity & Debt\n"
        cycles = self.kg.graph.graph.get("circular_dependencies", [])
        content += f"Circular Dependencies: {len(cycles)} detected.\n"
        
        output_path = self.root_path / "CODEBASE.md"
        output_path.write_text(content)
        print(f"Generated {output_path}")

    def generate_onboarding_brief(self, day_one_answers: str):
        """Generates the FDE Day-One Brief."""
        output_path = self.root_path / "onboarding_brief.md"
        output_path.write_text(day_one_answers)
        print(f"Generated {output_path}")

    def save_lineage_graph(self, output_path: Path):
        """Saves a filtered lineage graph (functions and datasets)."""
        lineage_nodes = [n for n, d in self.kg.graph.nodes(data=True) 
                         if d.get("node_type") in ["function", "dataset", "transformation"]]
        lineage_subgraph = self.kg.graph.subgraph(lineage_nodes)
        
        data = {
            "nodes": [
                {"id": n, **d} for n, d in lineage_subgraph.nodes(data=True)
            ],
            "edges": [
                {"source": u, "target": v, **d} for u, v, d in lineage_subgraph.edges(data=True)
            ]
        }
        output_path.write_text(json.dumps(data, indent=2))
        print(f"Generated {output_path}")

    def save_semantic_index_jsonl(self, output_path: Path):
        """Exports the semantic index (path/purpose) to JSONL."""
        # Note: In a real scenario, this might pull from Qdrant, 
        # but for the artifact requirement, we'll derive it from the KnowledgeGraph nodes.
        with open(output_path, "w") as f:
            for node_id, node_data in self.kg.graph.nodes(data=True):
                if node_data.get("purpose"):
                    f.write(json.dumps({
                        "id": node_id,
                        "path": node_data.get("path", node_id),
                        "purpose": node_data["purpose"]
                    }) + "\n")
        print(f"Generated {output_path}")

    def save_state_json(self, output_path: Path, state: Dict):
        """Saves analysis state/metadata."""
        output_path.write_text(json.dumps(state, indent=2))
        print(f"Generated {output_path}")

    def save_trace(self, trace_log: List[Dict]):
        """Saves the cartography trace."""
        project_name = self.root_path.name
        output_path = self.output_dir / project_name / "cartography_trace.jsonl"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            for entry in trace_log:
                f.write(json.dumps(entry) + "\n")
        print(f"Generated {output_path}")

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    archivist = ArchivistAgent(kg, "targets/meltano")
    archivist.generate_CODEBASE_md(["meltano.core.project", "meltano.core.plugin_invoker"])
