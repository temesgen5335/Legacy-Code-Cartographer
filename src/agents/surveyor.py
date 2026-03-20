import os
import tree_sitter_python as tspython
import tree_sitter_sql as tssql
from tree_sitter import Language, Parser, Query, QueryCursor
from pathlib import Path
from typing import Dict, List, Set, Any, Callable
import subprocess
import networkx as nx
from src.models.nodes import ModuleNode, FunctionNode
from src.models.schemas import TraceEvent
from src.graph.knowledge_graph import KnowledgeGraph

# Initialize languages
PY_LANGUAGE = Language(tspython.language())
SQL_LANGUAGE = Language(tssql.language())

class SurveyorAgent:
    """
    Performs deep static analysis of the codebase using tree-sitter.
    Extracts imports, public APIs, and class hierarchies.
    """
    
    def __init__(self, root_path: str | Path | None = None, kg: KnowledgeGraph | None = None):
        self.root_path = Path(root_path) if root_path else None
        self.kg = kg or KnowledgeGraph()
        self.py_parser = Parser(PY_LANGUAGE)
        self.sql_parser = Parser(SQL_LANGUAGE)

    def analyze_module(self, file_path: Path) -> ModuleNode:
        """
        Analyzes a single module (file) and extracts structural information.
        """
        content = file_path.read_text(errors="ignore")
        relative_path = str(file_path.relative_to(self.root_path))
        
        module_node = ModuleNode(
            path=relative_path,
            language="python" if file_path.suffix == ".py" else "sql",
        )
        
        if file_path.suffix == ".py":
            self._analyze_python(file_path, content, module_node)
        elif file_path.suffix == ".sql":
            self._analyze_sql(file_path, content, module_node)
            
        module_node.change_velocity_30d = self.extract_git_velocity(file_path)
        self.kg.add_module_node(module_node)
        return module_node

    def run(
        self, 
        repo_path: Path, 
        include_files: Set[str] | None = None,
        progress_callback: Callable[[str], None] | None = None
    ) -> tuple[KnowledgeGraph, dict[str, ModuleNode], list[TraceEvent]]:
        """
        Runs the full structural analysis.
        """
        self.root_path = repo_path
        trace: list[TraceEvent] = []
        modules = {}
        
        extensions = [".py", ".sql"]
        files_to_analyze = []
        
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
                progress_callback(f"Surveyor analyzing ({i+1}/{total}): {file_path.name}")
            
            try:
                mod = self.analyze_module(file_path)
                modules[mod.path] = mod
            except Exception as e:
                trace.append(TraceEvent(
                    agent="surveyor",
                    action="module_analysis_failed",
                    evidence={"file": str(file_path), "error": str(e)},
                    confidence="low"
                ))
        
        self.build_import_graph()
        
        trace.append(TraceEvent(
            agent="surveyor",
            action="analysis_complete",
            evidence={"modules_processed": len(modules), "node_count": len(self.kg.graph.nodes)},
            confidence="high"
        ))
        
        return self.kg, modules, trace

    def _analyze_python(self, file_path: Path, content: str, module_node: ModuleNode):
        tree = self.py_parser.parse(bytes(content, "utf8"))
        root = tree.root_node
        
        # 1. Extract Imports
        query_imports = Query(PY_LANGUAGE, """
            (import_statement (dotted_name) @name)
            (import_from_statement (dotted_name) @module)
        """)
        cursor = QueryCursor(query_imports)
        try:
            matches = cursor.matches(root)
            for _, captures in matches:
                if "name" in captures:
                    for node in captures["name"]:
                        imp = node.text.decode("utf8")
                        self.kg.add_edge(f"mod:{module_node.path}", f"mod:{imp}", "IMPORTS")
                if "module" in captures:
                    for node in captures["module"]:
                        imp = node.text.decode("utf8")
                        self.kg.add_edge(f"mod:{module_node.path}", f"mod:{imp}", "IMPORTS")
        except Exception as e:
            # print(f"Error parsing imports in {module_node.path}: {e}")
            pass

        # 2. Extract Classes
        query_classes = Query(PY_LANGUAGE, "(class_definition name: (identifier) @name)")
        cursor = QueryCursor(query_classes)
        try:
            matches = cursor.matches(root)
            for _, captures in matches:
                if "name" in captures:
                    pass
        except Exception:
            pass

        # 3. Extract Functions (Public API)
        query_funcs = Query(PY_LANGUAGE, "(function_definition name: (identifier) @name)")
        cursor = QueryCursor(query_funcs)
        try:
            matches = cursor.matches(root)
            for _, captures in matches:
                name_node = captures.get("name")
                if name_node:
                    name = name_node[0].text.decode("utf8")
                    if not name.startswith("_"):
                        func_node = FunctionNode(
                            qualified_name=f"{module_node.path}:{name}",
                            parent_module=module_node.path,
                            signature=name,
                            is_public_api=True
                        )
                        self.kg.add_function_node(func_node)
        except Exception:
            pass

    def _analyze_sql(self, file_path: Path, content: str, module_node: ModuleNode):
        pass

    def extract_git_velocity(self, file_path: Path, days: int = 30) -> float:
        """Estimates change velocity using git log."""
        try:
            # Optimized by avoiding shell=True and using a simpler command
            result = subprocess.run(
                ["git", "log", f"--since={days} days ago", "--oneline", "--", str(file_path)],
                capture_output=True,
                text=True,
                cwd=self.root_path,
                timeout=2 # Strict timeout per file
            )
            if result.returncode == 0:
                return float(len(result.stdout.strip().split("\n"))) if result.stdout.strip() else 0.0
            return 0.0
        except subprocess.TimeoutExpired:
            return 0.0
        except Exception:
            return 0.0

    def build_import_graph(self):
        """
        Analyzes the import graph, identifies hubs (PageRank) and circular dependencies.
        """
        import_subgraph = nx.DiGraph()
        for u, v, d in self.kg.graph.edges(data=True):
            if d.get("edge_type") == "IMPORTS":
                import_subgraph.add_edge(u, v)
        
        if len(import_subgraph) > 0:
            pagerank = nx.pagerank(import_subgraph)
            for node_id, score in pagerank.items():
                if node_id in self.kg.graph:
                    self.kg.graph.nodes[node_id]["pagerank_score"] = score
            
            cycles = list(nx.simple_cycles(import_subgraph))
            self.kg.graph.graph["circular_dependencies"] = cycles

if __name__ == "__main__":
    from src.graph.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    surveyor = SurveyorAgent(repo_path="targets/davidhalter_jedi.git", kg=kg)
    surveyor.run(repo_path=Path("targets/davidhalter_jedi.git"))
    kg.save(".cartography/meltano_graph.json")
    print(f"Analysis complete. Nodes: {len(kg.graph.nodes)}, Edges: {len(kg.graph.edges)}")
    print(f"Cycles detected: {len(kg.graph.graph.get('circular_dependencies', []))}")
