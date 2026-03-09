import networkx as nx
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from src.models.nodes import ModuleNode, DatasetNode, FunctionNode, TransformationNode

class KnowledgeGraph:
    """
    Central data store for the codebase intelligence system.
    Combines NetworkX for structure/lineage and JSON for serialization.
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: Union[ModuleNode, DatasetNode, FunctionNode, TransformationNode], node_type: str):
        node_id = self._get_node_id(node, node_type)
        self.graph.add_node(node_id, **node.model_dump(), node_type=node_type)

    def add_edge(self, source_id: str, target_id: str, edge_type: str, **kwargs):
        self.graph.add_edge(source_id, target_id, edge_type=edge_type, **kwargs)

    def _get_node_id(self, node: Any, node_type: str) -> str:
        if node_type == "module":
            return f"mod:{node.path}"
        elif node_type == "dataset":
            return f"ds:{node.name}"
        elif node_type == "function":
            return f"func:{node.qualified_name}"
        elif node_type == "transformation":
            return f"trans:{node.source_file}"
        return str(id(node))

    def save(self, path: str):
        data = nx.node_link_data(self.graph)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def load(self, path: str):
        with open(path, "r") as f:
            data = json.load(f)
        self.graph = nx.node_link_graph(data)

    def get_lineage(self, dataset_name: str, direction: str = "upstream") -> List[str]:
        """
        Traces data lineage for a dataset.
        """
        node_id = f"ds:{dataset_name}"
        if node_id not in self.graph:
            return []
        
        if direction == "upstream":
            return list(nx.ancestors(self.graph, node_id))
        else:
            return list(nx.descendants(self.graph, node_id))

    def blast_radius(self, module_path: str) -> List[str]:
        """
        Identifies all downstream dependents of a module.
        """
        node_id = f"mod:{module_path}"
        if node_id not in self.graph:
            return []
        return list(nx.descendants(self.graph, node_id))
