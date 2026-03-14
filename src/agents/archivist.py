import json
from pathlib import Path
from typing import Dict, List, Any
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.schemas import TraceEvent, ModuleNode
from src.analyzers.git_history import GitVelocitySnapshot

class ArchivistAgent:
    """
    Produces and maintains the system's outputs as living artifacts.
    Generates CODEBASE.md and onboarding_brief.md.
    """
    
    def __init__(self, kg: KnowledgeGraph | None = None, root_path: str = "."):
        self.kg = kg or KnowledgeGraph()
        self.root_path = Path(root_path)
        self.output_dir = self.root_path / ".cartography"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_module_graph(self, kg: KnowledgeGraph) -> Path:
        dest = self.output_dir / "module_graph.json"
        kg.save(dest)
        return dest

    def write_lineage_graph(self, kg: KnowledgeGraph) -> Path:
        dest = self.output_dir / "lineage_graph.json"
        kg.save(dest)
        return dest

    def write_semantic_index(self, modules: dict[str, ModuleNode]) -> Path:
        dest = self.output_dir / "semantic_index.json"
        data = {path: mod.model_dump(mode="json") for path, mod in modules.items()}
        dest.write_text(json.dumps(data, indent=2))
        return dest

    def write_trace(self, trace: list[TraceEvent]) -> Path:
        dest = self.output_dir / "trace.json"
        data = [t.model_dump(mode="json") for t in trace]
        dest.write_text(json.dumps(data, indent=2))
        return dest

    def generate_codebase_md(
        self,
        modules: dict[str, ModuleNode],
        top_modules: list[str],
        scc: list[list[str]],
        sources: list[str],
        sinks: list[str],
        git_velocity_snapshot: GitVelocitySnapshot | None = None
    ) -> Path:
        """Generates the detailed CODEBASE.md artifact."""
        project_name = self.root_path.name
        content = f"# CODEBASE.md: {project_name} Strategy Guide\n\n"
        content += "## 🏗️ Architectural Core\n"
        content += "The following modules represent the structural hubs of this system:\n\n"
        for mod_id in top_modules:
            content += f"- `{mod_id}`\n"
        
        content += "\n## 🌀 Structural Debt (Circular Dependencies)\n"
        if scc:
            cycles = [c for c in scc if len(c) > 1]
            if cycles:
                content += f"Detected {len(cycles)} circular dependency clusters.\n"
                for i, cycle in enumerate(cycles[:5]):
                    content += f"  - Cluster {i+1}: {' -> '.join(cycle[:3])}...\n"
            else:
                content += "No circular dependencies detected in the core graph.\n"
        
        content += "\n## 🚰 Data Ingestion & Egress\n"
        content += f"Sources identified: {len(sources)}\n"
        content += f"Sinks identified: {len(sinks)}\n"
        
        output_path = self.output_dir / "CODEBASE.md"
        output_path.write_text(content)
        return output_path

    def generate_onboarding_brief(self, day_one_answers: str) -> Path:
        """Generates the FDE Day-One Brief."""
        output_path = self.output_dir / "onboarding_brief.md"
        output_path.write_text(day_one_answers)
        return output_path

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
