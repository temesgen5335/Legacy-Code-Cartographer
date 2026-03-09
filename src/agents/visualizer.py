from pyvis.network import Network
from pathlib import Path
from src.graph.knowledge_graph import KnowledgeGraph

class VisualizerAgent:
    """
    Generates interactive HTML visualizations of the KnowledgeGraph using pyvis.
    """
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def generate_html(self, output_path: str):
        """
        Creates an interactive HTML file representing the knowledge graph.
        """
        # Initialize pyvis network
        # height and width as strings, heading for the page
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
        
        # Configure physics for better layout of large graphs
        net.force_atlas_2based()
        
        # Add nodes
        for node_id, node_data in self.kg.graph.nodes(data=True):
            node_type = node_data.get("node_type", "unknown")
            label = node_id.split(":")[-1] # Simple label
            
            # Color coding based on node type
            color = "#97c2fc" # Default blue
            if node_type == "module":
                color = "#ffbb33" # Orange/Yellow
            elif node_type == "function":
                color = "#00ffcc" # Teal
            elif node_type == "dataset":
                color = "#ff4444" # Red
            elif node_type == "transformation":
                color = "#aa66cc" # Purple
                
            # Node scale based on PageRank if available
            size = 10 + (node_data.get("pagerank_score", 0) * 500)
            
            # Add node to pyvis
            net.add_node(
                node_id, 
                label=label, 
                title=f"Type: {node_type}\nPath: {node_id}", 
                color=color,
                size=size
            )
            
        # Add edges
        for source, target, edge_data in self.kg.graph.edges(data=True):
            edge_type = edge_data.get("edge_type", "links")
            net.add_edge(source, target, title=edge_type)
            
        # Save visualization
        net.save_graph(output_path)
        print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    # Test stub
    kg = KnowledgeGraph()
    # Add dummy data if needed
    viz = VisualizerAgent(kg)
    viz.generate_html("test_graph.html")
