import os
from pathlib import Path
from typing import Dict, List, Set, Any
from src.analyzers.python_lineage import PythonDataFlowAnalyzer
from src.analyzers.sql_lineage import SQLLineageAnalyzer
from src.graph.knowledge_graph import KnowledgeGraph

class HydrologistAgent:
    """
    Constructs the data lineage DAG by analyzing data sources, 
    transformations, and sinks across all languages.
    """
    
    def __init__(self, root_path: str, kg: KnowledgeGraph):
        self.root_path = Path(root_path)
        self.kg = kg
        self.python_analyzer = PythonDataFlowAnalyzer(kg)
        self.sql_analyzer = SQLLineageAnalyzer(kg)

    def analyze_all(self):
        """
        Traverses the codebase and extracts lineage from Python, SQL, and YAML.
        """
        for ext in [".py", ".sql", ".yaml", ".yml"]:
            for file_path in self.root_path.rglob(f"*{ext}"):
                if "venv" in str(file_path) or ".git" in str(file_path):
                    continue
                
                if file_path.suffix == ".py":
                    self.python_analyzer.analyze_file(file_path)
                elif file_path.suffix == ".sql":
                    self.sql_analyzer.analyze_file(file_path)
                elif file_path.suffix in [".yaml", ".yml"]:
                    self._analyze_config(file_path)

    def _analyze_config(self, file_path: Path):
        # Placeholder for dbt schema.yml or Airflow DAG configs
        pass

    def get_blast_radius(self, node_id: str) -> List[str]:
        return self.kg.blast_radius(node_id)

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    hydrologist = HydrologistAgent("targets/meltano", kg)
    hydrologist.analyze_all()
    print(f"Lineage analysis complete. Nodes: {len(kg.graph.nodes)}, Edges: {len(kg.graph.edges)}")
