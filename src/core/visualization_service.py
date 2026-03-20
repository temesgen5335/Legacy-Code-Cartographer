"""
VisualizationService - Graph data generation and export logic.

This service handles all visualization data preparation,
decoupled from any UI layer (GUI or CLI).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from src.agents.visualizer import VisualizerAgent
from src.graph.data_lineage import DataLineageGraph
from src.graph.knowledge_graph import KnowledgeGraph


class VisualizationService:
    """
    Core service for visualization data generation.
    
    This service is UI-agnostic and can be used by both GUI and CLI.
    """
    
    def generate_module_graph(
        self,
        project_name: str,
        output_format: Literal["html", "json"] = "html",
        output_path: Path | None = None,
    ) -> dict[str, Any]:
        """
        Generate module graph visualization.
        
        Args:
            project_name: Name of the analyzed project
            output_format: Output format (html or json)
            output_path: Custom output path (optional)
        
        Returns:
            Dictionary with generation report and output path
        """
        cartography_dir = Path(".cartography")
        kg_path = cartography_dir / project_name / "knowledge_graph.json"
        
        if not kg_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")
        
        kg = KnowledgeGraph.load(kg_path)
        viz = VisualizerAgent(kg)
        
        if output_path is None:
            if output_format == "html":
                output_path = cartography_dir / project_name / "module_graph.html"
            else:
                output_path = cartography_dir / project_name / "module_graph.json"
        
        if output_format == "html":
            report = viz.generate_module_graph(str(output_path))
        else:
            # Export as JSON
            graph_data = self._export_graph_json(kg, "module")
            output_path.write_text(
                __import__("json").dumps(graph_data, indent=2),
                encoding="utf-8",
            )
            report = {
                "node_count": len(graph_data["nodes"]),
                "edge_count": len(graph_data["edges"]),
                "graph_type": "module",
            }
        
        return {
            "output_path": str(output_path),
            "output_format": output_format,
            "report": report,
        }
    
    def generate_lineage_graph(
        self,
        project_name: str,
        output_format: Literal["html", "json"] = "html",
        output_path: Path | None = None,
    ) -> dict[str, Any]:
        """
        Generate data lineage graph visualization.
        
        Args:
            project_name: Name of the analyzed project
            output_format: Output format (html or json)
            output_path: Custom output path (optional)
        
        Returns:
            Dictionary with generation report and output path
        """
        cartography_dir = Path(".cartography")
        kg_path = cartography_dir / project_name / "knowledge_graph.json"
        
        if not kg_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")
        
        kg = KnowledgeGraph.load(kg_path)
        viz = VisualizerAgent(kg)
        
        if output_path is None:
            if output_format == "html":
                output_path = cartography_dir / project_name / "lineage_graph.html"
            else:
                output_path = cartography_dir / project_name / "lineage_graph.json"
        
        if output_format == "html":
            report = viz.generate_lineage_graph(str(output_path))
        else:
            # Export as JSON
            graph_data = self._export_graph_json(kg, "lineage")
            output_path.write_text(
                __import__("json").dumps(graph_data, indent=2),
                encoding="utf-8",
            )
            report = {
                "node_count": len(graph_data["nodes"]),
                "edge_count": len(graph_data["edges"]),
                "graph_type": "lineage",
            }
        
        return {
            "output_path": str(output_path),
            "output_format": output_format,
            "report": report,
        }
    
    def get_lineage_data(
        self,
        project_name: str,
        node_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get lineage data for a project or specific node.
        
        Args:
            project_name: Name of the analyzed project
            node_id: Optional node ID to focus on
        
        Returns:
            Dictionary with lineage information
        """
        cartography_dir = Path(".cartography")
        kg_path = cartography_dir / project_name / "knowledge_graph.json"
        
        if not kg_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")
        
        dlg = DataLineageGraph()
        dlg.load(kg_path)
        
        if node_id:
            attrs = dlg.graph.nodes.get(node_id, {})
            blast_radius = dlg.blast_radius(node_id)
            upstream = dlg.upstream(node_id)
            return {
                "center": node_id,
                "blast_radius": blast_radius,
                "upstream": upstream,
                "connected_nodes": list(set([node_id] + blast_radius + upstream)),
                "source_file": attrs.get("source_file"),
                "node_type": attrs.get("node_type"),
            }
        
        return {
            "sources": dlg.find_sources(),
            "sinks": dlg.find_sinks(),
            "total_nodes": len(dlg.graph.nodes),
        }
    
    def _export_graph_json(
        self,
        kg: KnowledgeGraph,
        graph_type: Literal["module", "lineage"],
    ) -> dict[str, Any]:
        """Export graph as JSON data structure."""
        nodes = []
        edges = []
        
        if graph_type == "module":
            graph = kg.module_import_graph()
        else:
            graph = kg.graph
        
        # Export nodes
        for node_id, attrs in graph.nodes(data=True):
            node_data = {
                "id": node_id,
                "type": attrs.get("node_type", "unknown"),
                "attributes": dict(attrs),
            }
            nodes.append(node_data)
        
        # Export edges
        for source, target, attrs in graph.edges(data=True):
            edge_data = {
                "source": source,
                "target": target,
                "type": attrs.get("edge_type", "unknown"),
                "attributes": dict(attrs),
            }
            edges.append(edge_data)
        
        return {
            "graph_type": graph_type,
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
        }
