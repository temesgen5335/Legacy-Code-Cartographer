import sqlglot
import os
from sqlglot import exp, parse_one
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from src.models.nodes import TransformationNode, DatasetNode, StorageType
from src.graph.knowledge_graph import KnowledgeGraph

class SQLLineageAnalyzer:
    """
    Parses SQL and dbt files to extract table-level data lineage.
    Uses sqlglot to handle multiple dialects.
    """
    
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def analyze_file(self, file_path: Path):
        """
        Extracts lineage from a SQL or dbt model file.
        """
        sql_content = file_path.read_text(errors="ignore")
        dialect = self._detect_dialect(sql_content)
        
        try:
            # Handle dbt ref() and source() by pre-processing or using sqlglot
            # For simplicity, we'll treat them as table names for now.
            # Real dbt parsing would require dbt-core or more complex regex.
            processed_sql = sql_content.replace("{{", "").replace("}}", "")
            
            expressions = sqlglot.parse(processed_sql, read=dialect)
            for expression in expressions:
                if expression:
                    self._extract_from_expression(expression, file_path)
        except Exception as e:
            # print(f"Error parsing SQL in {file_path}: {e}")
            pass

    def _extract_from_expression(self, expression: exp.Expression, file_path: Path):
        """
        Extracts tables from a single SQL expression.
        """
        tables = set()
        for table in expression.find_all(exp.Table):
            tables.add(table.name)
        
        # Determine if it's a 'Create Table As' or 'Insert Into' (Targets)
        targets = set()
        if isinstance(expression, exp.Create):
            if expression.this and isinstance(expression.this, exp.Table):
                targets.add(expression.this.name)
        elif isinstance(expression, exp.Insert):
            if expression.this and isinstance(expression.this, exp.Table):
                targets.add(expression.this.name)
        
        sources = list(tables - targets)
        if targets:
            trans_node = TransformationNode(
                source_datasets=sources,
                target_datasets=list(targets),
                transformation_type="SQL",
                source_file=str(file_path),
                line_range=(1, len(sql_content.splitlines())),
                lineage_range=(1, len(sql_content.splitlines())),
                sql_query_if_applicable=str(expression)[:500],
                source_dataset_ref=",".join(sources) if sources else None,
                target_dataset_ref=",".join(targets) if targets else None
            )
            self.kg.add_transformation_node(f"trans:{str(file_path)}", trans_node)
            
            # Add sources and targets as dataset nodes
            for s in sources:
                ds_s = DatasetNode(
                    name=s, 
                    storage_type=StorageType.TABLE,
                    source_file=str(file_path),
                    lineage_range=(1, len(sql_content.splitlines()))
                )
                self.kg.add_dataset_node(f"ds:{s}", ds_s)
                self.kg.add_edge(f"ds:{s}", f"trans:{str(file_path)}", "CONSUMES")
            for t in targets:
                ds_t = DatasetNode(
                    name=t, 
                    storage_type=StorageType.TABLE,
                    source_file=str(file_path),
                    is_source_of_truth=True,
                    lineage_range=(1, len(sql_content.splitlines()))
                )
                self.kg.add_dataset_node(f"ds:{t}", ds_t)
                self.kg.add_edge(f"trans:{str(file_path)}", f"ds:{t}", "PRODUCES")

    def _detect_dialect(self, content: str) -> Optional[str]:
        # Simple heuristic or default
        if "QUALIFY" in content.upper(): return "bigquery"
        if "ILIKES" in content.upper(): return "postgres"
        return None

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    analyzer = SQLLineageAnalyzer(kg)
    # Test on a simple SQL file if exists, or a mock
    mock_sql = Path("test.sql")
    mock_sql.write_text("CREATE TABLE target_table AS SELECT * FROM source_table JOIN other_table ON id")
    analyzer.analyze_file(mock_sql)
    print(f"Nodes: {len(kg.graph.nodes)}, Edges: {len(kg.graph.edges)}")
    os.remove(mock_sql)
