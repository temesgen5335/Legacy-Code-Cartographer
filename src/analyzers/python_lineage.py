import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor
from pathlib import Path
from typing import Dict, List, Set, Any
from src.models.nodes import TransformationNode, DatasetNode, StorageType
from src.graph.knowledge_graph import KnowledgeGraph

PY_LANGUAGE = Language(tspython.language())

class PythonDataFlowAnalyzer:
    """
    Extracts data lineage from Python code (pandas, PySpark, SQLAlchemy).
    """
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self.parser = Parser(PY_LANGUAGE)

    def analyze_file(self, file_path: Path):
        content = file_path.read_text(errors="ignore")
        tree = self.parser.parse(bytes(content, "utf8"))
        root = tree.root_node
        
        # Query for pandas read/write
        # (call function: (attribute object: (identifier) @obj name: (identifier) @method) arguments: (argument_list (string) @path))
        query_pandas = Query(PY_LANGUAGE, """
            (call
                function: (attribute
                    object: (identifier) @obj
                    attribute: (identifier) @method)
                arguments: (argument_list (string) @path .))
        """)
        
        cursor = QueryCursor(query_pandas)
        matches = cursor.matches(root)
        for _, captures in matches:
            method_node = captures.get("method")
            path_node = captures.get("path")
            
            if method_node and path_node:
                method = method_node[0].text.decode("utf8")
                path = path_node[0].text.decode("utf8").strip("'\"")
                
                if method.startswith("read_"):
                    # Source
                    ds_node = DatasetNode(
                        name=path, 
                        storage_type=StorageType.FILE,
                        source_file=str(file_path),
                        lineage_range=(method_node[0].start_point[0] + 1, method_node[0].end_point[0] + 1)
                    )
                    self.kg.add_dataset_node(f"ds:{path}", ds_node)
                    self.kg.add_edge(f"ds:{path}", f"trans:{str(file_path)}", "CONSUMES")
                elif method.startswith("to_"):
                    # Target
                    ds_node = DatasetNode(
                        name=path, 
                        storage_type=StorageType.FILE,
                        source_file=str(file_path),
                        lineage_range=(method_node[0].start_point[0] + 1, method_node[0].end_point[0] + 1)
                    )
                    self.kg.add_dataset_node(f"ds:{path}", ds_node)
                    self.kg.add_edge(f"trans:{str(file_path)}", f"ds:{path}", "PRODUCES")
                    
                    # Also create a transformation node
                    t_node = TransformationNode(
                        source_datasets=[], 
                        target_datasets=[path],
                        transformation_type="Python/Pandas",
                        source_file=str(file_path),
                        line_range=(method_node[0].start_point[0] + 1, method_node[0].end_point[0] + 1),
                        lineage_range=(method_node[0].start_point[0] + 1, method_node[0].end_point[0] + 1),
                        target_dataset_ref=path
                    )
                    self.kg.add_transformation_node(f"trans:{str(file_path)}", t_node)

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    analyzer = PythonDataFlowAnalyzer(kg)
    # Mock test
    mock_file = Path("test_df.py")
    mock_file.write_text("import pandas as pd\ndf = pd.read_csv('data.csv')\ndf.to_parquet('output.parquet')")
    analyzer.analyze_file(mock_file)
    print(f"Nodes: {len(kg.graph.nodes)}, Edges: {len(kg.graph.edges)}")
    import os
    os.remove(mock_file)
