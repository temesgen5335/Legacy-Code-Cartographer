from __future__ import annotations
from collections import deque
from src.graph.knowledge_graph import KnowledgeGraph

class DataLineageGraph(KnowledgeGraph):
    """
    Specialized graph for data lineage tracing and blast radius analysis.
    """
    def blast_radius(self, node_id: str) -> list[str]:
        """
        Identifies all downstream nodes impacted by a change to the given node.
        """
        if node_id not in self.graph:
            return []
        impacted: list[str] = []
        visited: set[str] = {node_id}
        queue: deque[str] = deque([node_id])
        while queue:
            current = queue.popleft()
            for neighbor in sorted(self.graph.successors(current)):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                impacted.append(neighbor)
                queue.append(neighbor)
        return impacted

    def find_sources(self) -> list[str]:
        """Nodes with zero in-degree (Entry points)."""
        return sorted([node for node in self.graph.nodes if self.graph.in_degree(node) == 0])

    def find_sinks(self) -> list[str]:
        """Nodes with zero out-degree (Final destinations)."""
        return sorted([node for node in self.graph.nodes if self.graph.out_degree(node) == 0])
