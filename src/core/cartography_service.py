"""
CartographyService - Core analysis orchestration logic.

This service encapsulates all codebase analysis functionality,
decoupled from any UI layer (GUI or CLI).
"""
from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from src.analyzers.git_history import GitVelocitySnapshot, compute_git_velocity_snapshot
from src.agents.archivist import ArchivistAgent
from src.agents.hydrologist import HydrologistAgent
from src.agents.semanticist import SemanticistAgent
from src.agents.surveyor import SurveyorAgent
from src.agents.visualizer import VisualizerAgent
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.schemas import ModuleNode, TraceEvent


class AnalysisResult:
    """Structured result from a cartography analysis."""
    
    def __init__(
        self,
        project_name: str,
        artifacts: dict[str, str],
        metrics: dict[str, Any],
        trace: list[TraceEvent],
    ):
        self.project_name = project_name
        self.artifacts = artifacts
        self.metrics = metrics
        self.trace = trace
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "trace": [t.model_dump() for t in self.trace],
        }


class CartographyService:
    """
    Core service for codebase cartography analysis.
    
    This service is UI-agnostic and can be used by both GUI and CLI.
    """
    
    def __init__(self, progress_callback: Callable[[str], None] | None = None):
        self._progress_callback = progress_callback or self._default_progress
    
    def analyze_repository(
        self,
        repo_path: Path | str,
        repo_input: str | None = None,
        out_dir: Path | None = None,
        incremental: bool = True,
    ) -> AnalysisResult:
        """
        Perform full cartography analysis on a repository.
        
        Args:
            repo_path: Local path to the repository
            repo_input: Original input (URL or path) for metadata
            out_dir: Output directory for artifacts (default: .cartography/<project>)
            incremental: Whether to use incremental analysis mode
        
        Returns:
            AnalysisResult containing artifacts, metrics, and trace
        """
        from src.orchestrator import CartographyOrchestrator
        
        repo_path = Path(repo_path).resolve()
        
        # Determine project name
        if repo_input and repo_input.startswith("http"):
            parsed = urlparse(repo_input)
            project_name = parsed.path.strip("/").replace("/", "_")
            if project_name.endswith(".git"):
                project_name = project_name[:-4]
        else:
            project_name = repo_path.name
        
        # Use orchestrator for analysis
        orchestrator = CartographyOrchestrator(
            repo_path=repo_path,
            out_dir=out_dir,
            repo_input=repo_input or str(repo_path),
            progress_callback=self._progress_callback,
        )
        
        artifacts = orchestrator.analyze(incremental=incremental)
        
        # Load knowledge graph for metrics
        kg_path = Path(artifacts["knowledge_graph"])
        kg = KnowledgeGraph.load(kg_path)
        
        # Compute metrics
        metrics = self._compute_metrics(kg, project_name)
        
        # Load trace
        trace_path = Path(artifacts["trace"])
        trace = self._load_trace(trace_path)
        
        return AnalysisResult(
            project_name=project_name,
            artifacts=artifacts,
            metrics=metrics,
            trace=trace,
        )
    
    def clone_repository(self, url: str, target_dir: Path | None = None) -> Path:
        """
        Clone a GitHub repository.
        
        Args:
            url: GitHub repository URL
            target_dir: Target directory (default: targets/<repo_name>)
        
        Returns:
            Path to cloned repository
        """
        parsed = urlparse(url)
        repo_name = parsed.path.strip("/").replace("/", "_")
        
        if target_dir is None:
            target_dir = Path("targets") / repo_name
        
        if not target_dir.exists():
            self._progress(f"Cloning {url} into {target_dir}...")
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(target_dir)],
                check=True,
            )
        else:
            self._progress(f"Repository already exists at {target_dir}")
        
        return target_dir
    
    def get_project_summary(self, project_name: str) -> dict[str, Any]:
        """
        Get summary information for an analyzed project.
        
        Args:
            project_name: Name of the project
        
        Returns:
            Dictionary containing project summary
        """
        cartography_dir = Path(".cartography")
        kg_path = cartography_dir / project_name / "knowledge_graph.json"
        
        if not kg_path.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found")
        
        kg = KnowledgeGraph.load(kg_path)
        metrics = self._compute_metrics(kg, project_name)
        
        # Get architectural hubs
        pr_scores = kg.pagerank(module_import_only=True)
        hubs = []
        for node_id, attrs in kg.graph.nodes(data=True):
            if attrs.get("node_type") == "module":
                pr_score = pr_scores.get(node_id, 0)
                if pr_score > 0.05 or kg.graph.in_degree(node_id) > 5:
                    hubs.append({
                        "path": attrs.get("path", node_id),
                        "pagerank_score": pr_score,
                        "fan_in": kg.graph.in_degree(node_id),
                        "fan_out": kg.graph.out_degree(node_id),
                    })
        
        hubs.sort(key=lambda x: x["pagerank_score"], reverse=True)
        
        return {
            "project_name": project_name,
            "metrics": metrics,
            "architectural_hubs": hubs[:10],
            "node_count": len(kg.graph.nodes),
            "edge_count": len(kg.graph.edges),
        }
    
    def list_projects(self) -> list[dict[str, Any]]:
        """
        List all analyzed projects.
        
        Returns:
            List of project information dictionaries
        """
        cartography_dir = Path(".cartography")
        if not cartography_dir.exists():
            return []
        
        projects = []
        for item in cartography_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                kg_path = item / "knowledge_graph.json"
                if kg_path.exists():
                    try:
                        kg = KnowledgeGraph.load(kg_path)
                        projects.append({
                            "name": item.name,
                            "node_count": len(kg.graph.nodes),
                            "edge_count": len(kg.graph.edges),
                            "artifact_path": str(item),
                        })
                    except Exception:
                        continue
        
        return projects
    
    def _compute_metrics(self, kg: KnowledgeGraph, project_name: str) -> dict[str, Any]:
        """Compute standard metrics from a knowledge graph."""
        # System complexity (average complexity score)
        complexity_scores = [
            attrs.get("complexity_score", 0)
            for _, attrs in kg.graph.nodes(data=True)
            if attrs.get("node_type") == "module"
        ]
        avg_complexity = sum(complexity_scores) / max(len(complexity_scores), 1)
        
        # Dead code count
        dead_code_count = sum(
            1 for _, attrs in kg.graph.nodes(data=True)
            if attrs.get("is_dead_code_candidate")
        )
        
        # Primary ingestion point (node with highest out-degree + zero in-degree)
        sources = [
            n for n, d in kg.graph.nodes(data=True)
            if kg.graph.in_degree(n) == 0
        ]
        primary_source = min(sources, key=len) if sources else "Unknown"
        
        # Blast radius average
        blast_radius_total = sum(
            len(kg.downstream(n)) for n in kg.graph.nodes
        )
        blast_radius_avg = blast_radius_total / max(len(kg.graph.nodes), 1)
        
        return {
            "system_complexity": round(avg_complexity, 2),
            "confidence_score": 0.92,  # Placeholder
            "risk_index": dead_code_count,
            "primary_ingestion": primary_source,
            "blast_radius_avg": round(blast_radius_avg, 2),
            "node_count": len(kg.graph.nodes),
            "edge_count": len(kg.graph.edges),
        }
    
    def _load_trace(self, trace_path: Path) -> list[TraceEvent]:
        """Load trace events from JSON file."""
        try:
            with open(trace_path, "r") as f:
                data = json.load(f)
            return [TraceEvent(**event) for event in data]
        except Exception:
            return []
    
    def _progress(self, message: str) -> None:
        self._progress_callback(message)
    
    def _default_progress(self, message: str) -> None:
        print(f"[cartography] {message}")
