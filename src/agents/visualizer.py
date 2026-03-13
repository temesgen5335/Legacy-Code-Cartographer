from pyvis.network import Network
from pathlib import Path
from src.graph.knowledge_graph import KnowledgeGraph

class VisualizerAgent:
    """
    Generates interactive HTML visualizations of the KnowledgeGraph using pyvis.
    """
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def generate_html(self, output_path: str, filter_type: str = "all"):
        """
        Creates an interactive HTML file representing the knowledge graph.
        filter_type: "module" (only modules), "lineage" (func/data), or "all".
        """
        net = Network(height="750px", width="100%", bgcolor="#0a0f18", font_color="white", directed=True)
        net.force_atlas_2based()
        
        # Filter nodes
        relevant_nodes = []
        for node_id, node_data in self.kg.graph.nodes(data=True):
            node_type = node_data.get("node_type", "unknown")
            
            if filter_type == "module" and node_type != "module":
                continue
            if filter_type == "lineage" and node_type not in ["function", "dataset", "transformation"]:
                continue
            
            label = node_id.split(":")[-1]
            color = "#94a3b8" 
            if node_type == "module": color = "#d4af35" # Gold
            elif node_type == "function": color = "#10b981" # Emerald
            elif node_type == "dataset": color = "#ef4444" # Red
                
            size = 10 + (node_data.get("pagerank_score", 0) * 500)
            net.add_node(node_id, label=label, title=f"Type: {node_type}\nPath: {node_id}", color=color, size=size)
            relevant_nodes.append(node_id)
            
        # Add edges
        for source, target, edge_data in self.kg.graph.edges(data=True):
            if source in relevant_nodes and target in relevant_nodes:
                edge_type = edge_data.get("edge_type", "links")
                net.add_edge(source, target, title=edge_type, color="#1e293b", arrows="to")
            
        net.save_graph(output_path)
        print(f"Visualization ({filter_type}) saved to {output_path}")

    def generate_module_graph(self, output_path: str):
        self.generate_html(output_path, filter_type="module")

    def generate_lineage_graph(self, output_path: str):
        self.generate_html(output_path, filter_type="lineage")

if __name__ == "__main__":
    # Test stub
    kg = KnowledgeGraph()
    # Add dummy data if needed
    viz = VisualizerAgent(kg)
    viz.generate_html("test_graph.html")
