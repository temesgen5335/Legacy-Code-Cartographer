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
        """
        Generates the living context file for AI agents.
        """
        content = "# CODEBASE.md: System Context\n\n"
        
        content += "## Architecture Overview\n"
        content += "Meltano is an ELT orchestration platform written in Python and uses SQL/YAML for plugin configuration.\n\n"
        
        content += "## Critical Path (Most Imported Modules)\n"
        for hub in surveyor_hubs[:5]:
            content += f"- `{hub}`\n"
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
        """
        Generates the FDE Day-One Brief.
        """
        output_path = self.root_path / "onboarding_brief.md"
        output_path.write_text(day_one_answers)
        print(f"Generated {output_path}")

    def save_trace(self, trace_log: List[Dict]):
        output_path = self.output_dir / "cartography_trace.jsonl"
        with open(output_path, "w") as f:
            for entry in trace_log:
                f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    archivist = ArchivistAgent(kg, "targets/meltano")
    archivist.generate_CODEBASE_md(["meltano.core.project", "meltano.core.plugin_invoker"])
