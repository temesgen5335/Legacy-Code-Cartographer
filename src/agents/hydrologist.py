from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set, Any, Callable
from src.analyzers.python_lineage import PythonDataFlowAnalyzer
from src.analyzers.sql_lineage import SQLLineageAnalyzer
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.schemas import TraceEvent

class HydrologistAgent:
    """
    Constructs the data lineage DAG by analyzing data sources, 
    transformations, and sinks across all languages.
    """
    
    def __init__(self, lineage_graph: KnowledgeGraph | None = None):
        self.kg = lineage_graph or KnowledgeGraph()
        self.python_analyzer = PythonDataFlowAnalyzer(self.kg)
        self.sql_analyzer = SQLLineageAnalyzer(self.kg)

    def run(
        self, 
        repo_path: Path, 
        lineage_graph: KnowledgeGraph, 
        include_files: Set[str] | None = None,
        progress_callback: Callable[[str], None] | None = None
    ) -> tuple[KnowledgeGraph, list[TraceEvent]]:
        """
        Runs the full lineage analysis suite.
        """
        self.kg = lineage_graph
        self.python_analyzer.kg = lineage_graph # sync
        self.sql_analyzer.kg = lineage_graph
        
        trace: list[TraceEvent] = []
        files_to_analyze = []
        
        extensions = [".py", ".sql", ".yaml", ".yml"]
        if include_files:
            for rel_path in include_files:
                p = repo_path / rel_path
                if p.suffix in extensions and p.exists():
                    files_to_analyze.append(p)
        else:
            for ext in extensions:
                files_to_analyze.extend(list(repo_path.rglob(f"*{ext}")))

        total = len(files_to_analyze)
        for i, file_path in enumerate(files_to_analyze):
            if any(p in ["venv", ".git", ".cartography"] for p in file_path.parts):
                continue
            
            if progress_callback:
                progress_callback(f"Hydrologist analyzing ({i+1}/{total}): {file_path.name}")
            
            try:
                if file_path.suffix == ".py":
                    self.python_analyzer.analyze_file(file_path)
                elif file_path.suffix == ".sql":
                    self.sql_analyzer.analyze_file(file_path)
                elif file_path.suffix in [".yaml", ".yml"]:
                    self._analyze_config(file_path)
            except Exception as e:
                trace.append(TraceEvent(
                    agent="hydrologist",
                    action="file_analysis_failed",
                    evidence={"file": str(file_path), "error": str(e)},
                    confidence="low"
                ))

        trace.append(TraceEvent(
            agent="hydrologist",
            action="analysis_complete",
            evidence={"files_processed": total, "node_count": len(self.kg.graph.nodes)},
            confidence="high"
        ))
        
        return self.kg, trace

    def _analyze_config(self, file_path: Path):
        # Placeholder for dbt schema.yml or Airflow DAG configs
        pass

    def find_sources(self, graph: KnowledgeGraph) -> list[str]:
        """Identifies root nodes in the lineage graph (no incoming edges)."""
        sources = []
        for node in graph.graph.nodes:
            if graph.graph.in_degree(node) == 0:
                sources.append(node)
        return sources

    def find_sinks(self, graph: KnowledgeGraph) -> list[str]:
        """Identifies leaf nodes in the lineage graph (no outgoing edges)."""
        sinks = []
        for node in graph.graph.nodes:
            if graph.graph.out_degree(node) == 0:
                sinks.append(node)
        return sinks

    def blast_radius(self, node_id: str) -> dict[str, Any]:
        impacted = self.kg.blast_radius(node_id)
        return {
            "target": node_id,
            "impacted_nodes": impacted,
            "impact_count": len(impacted)
        }

    def what_feeds_table(self, table_name: str) -> dict[str, Any]:
        """Finds all upstream nodes feeding a table."""
        node_id = f"ds:{table_name}"
        if node_id not in self.kg.graph:
            # Try raw name
            node_id = table_name
            if node_id not in self.kg.graph:
                return {"target": table_name, "error": "Table not found in lineage graph."}
        
        upstream = self.kg.upstream(node_id)
        return {
            "target": table_name,
            "full_upstream": upstream,
            "direct_upstream": [n for n in self.kg.graph.predecessors(node_id)]
        }

    def what_depends_on_output(self, table_name: str) -> dict[str, Any]:
        """Finds all downstream nodes consuming a table."""
        node_id = f"ds:{table_name}"
        if node_id not in self.kg.graph:
            node_id = table_name
            if node_id not in self.kg.graph:
                return {"target": table_name, "error": "Table not found in lineage graph."}
        
        downstream = self.kg.downstream(node_id)
        return {
            "target": table_name,
            "full_downstream": downstream,
            "direct_downstream": [n for n in self.kg.graph.successors(node_id)]
        }
