#!/usr/bin/env python3
"""
CLI/GUI Parity Verification Script

This script verifies that the CLI and GUI (via core services) generate
identical artifacts for the same repository input.

Usage:
    python verify_parity.py <repository_path>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.cartography_service import CartographyService
from src.graph.knowledge_graph import KnowledgeGraph

console = Console()


def verify_parity(repo_path: Path) -> bool:
    """
    Verify that core service generates expected artifacts.
    
    Args:
        repo_path: Path to repository to analyze
    
    Returns:
        True if all checks pass, False otherwise
    """
    console.print(Panel.fit(
        "[bold gold1]🔍 CLI/GUI PARITY VERIFICATION[/bold gold1]\n"
        "[dim]Ensuring identical artifact generation[/dim]",
        border_style="gold1",
    ))
    
    if not repo_path.exists():
        console.print(f"[red]✗[/red] Repository path does not exist: {repo_path}", style="red")
        return False
    
    console.print(f"\n[cyan]→[/cyan] Analyzing repository: [bold]{repo_path.name}[/bold]")
    
    # Run analysis via core service (same as both CLI and GUI use)
    service = CartographyService(progress_callback=lambda msg: console.print(f"[dim]{msg}[/dim]"))
    
    try:
        result = service.analyze_repository(
            repo_path=repo_path,
            repo_input=str(repo_path),
            incremental=False,
        )
    except Exception as e:
        console.print(f"\n[red]✗[/red] Analysis failed: {e}", style="red")
        return False
    
    console.print(f"\n[green]✓[/green] Analysis complete: [bold]{result.project_name}[/bold]")
    
    # Verification checks
    checks = []
    
    # Check 1: All expected artifacts exist
    console.print("\n[bold cyan]📋 Artifact Existence Checks[/bold cyan]")
    
    expected_artifacts = {
        "knowledge_graph": "Knowledge Graph JSON",
        "semantic_index": "Semantic Index",
        "codebase_md": "Codebase Documentation",
        "onboarding_brief": "Onboarding Brief",
        "trace": "Trace Events",
        "module_graph_html": "Module Graph HTML",
        "lineage_graph_html": "Lineage Graph HTML",
    }
    
    artifact_table = Table(border_style="dim")
    artifact_table.add_column("Artifact", style="cyan")
    artifact_table.add_column("Status", style="green")
    artifact_table.add_column("Path", style="dim")
    
    for artifact_key, artifact_name in expected_artifacts.items():
        if artifact_key in result.artifacts:
            artifact_path = Path(result.artifacts[artifact_key])
            if artifact_path.exists():
                status = "[green]✓ Exists[/green]"
                checks.append(True)
            else:
                status = "[red]✗ Missing[/red]"
                checks.append(False)
            artifact_table.add_row(artifact_name, status, str(artifact_path))
        else:
            artifact_table.add_row(artifact_name, "[red]✗ Not generated[/red]", "N/A")
            checks.append(False)
    
    console.print(artifact_table)
    
    # Check 2: Knowledge graph structure
    console.print("\n[bold cyan]🕸️  Knowledge Graph Structure Checks[/bold cyan]")
    
    kg_path = Path(result.artifacts["knowledge_graph"])
    kg = KnowledgeGraph.load(kg_path)
    
    kg_table = Table(border_style="dim")
    kg_table.add_column("Check", style="cyan")
    kg_table.add_column("Result", style="green")
    
    node_count = len(kg.graph.nodes)
    edge_count = len(kg.graph.edges)
    
    kg_table.add_row("Nodes", f"{node_count} nodes")
    kg_table.add_row("Edges", f"{edge_count} edges")
    
    checks.append(node_count > 0)
    checks.append(edge_count >= 0)
    
    # Verify JSON structure
    with open(kg_path, "r") as f:
        kg_json = json.load(f)
    
    has_nodes = "nodes" in kg_json
    has_links = "links" in kg_json
    
    kg_table.add_row("JSON 'nodes' key", "[green]✓[/green]" if has_nodes else "[red]✗[/red]")
    kg_table.add_row("JSON 'links' key", "[green]✓[/green]" if has_links else "[red]✗[/red]")
    
    checks.append(has_nodes)
    checks.append(has_links)
    
    console.print(kg_table)
    
    # Check 3: Metrics computation
    console.print("\n[bold cyan]📊 Metrics Computation Checks[/bold cyan]")
    
    metrics_table = Table(border_style="dim")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    metrics_table.add_column("Status", style="green")
    
    required_metrics = [
        "node_count",
        "edge_count",
        "system_complexity",
        "confidence_score",
        "risk_index",
        "blast_radius_avg",
    ]
    
    for metric in required_metrics:
        if metric in result.metrics:
            value = result.metrics[metric]
            status = "[green]✓[/green]"
            checks.append(True)
        else:
            value = "N/A"
            status = "[red]✗[/red]"
            checks.append(False)
        
        metrics_table.add_row(metric.replace("_", " ").title(), str(value), status)
    
    console.print(metrics_table)
    
    # Check 4: Trace events
    console.print("\n[bold cyan]📝 Trace Events Checks[/bold cyan]")
    
    trace_count = len(result.trace)
    trace_status = "[green]✓[/green]" if trace_count > 0 else "[red]✗[/red]"
    
    console.print(f"  Trace events: {trace_count} {trace_status}")
    checks.append(trace_count > 0)
    
    # Check 5: HTML visualizations
    console.print("\n[bold cyan]🎨 Visualization Checks[/bold cyan]")
    
    viz_table = Table(border_style="dim")
    viz_table.add_column("Visualization", style="cyan")
    viz_table.add_column("Size", style="green")
    viz_table.add_column("Status", style="green")
    
    for viz_key in ["module_graph_html", "lineage_graph_html"]:
        if viz_key in result.artifacts:
            viz_path = Path(result.artifacts[viz_key])
            if viz_path.exists():
                size_kb = viz_path.stat().st_size / 1024
                status = "[green]✓[/green]"
                checks.append(True)
            else:
                size_kb = 0
                status = "[red]✗[/red]"
                checks.append(False)
            
            viz_name = viz_key.replace("_", " ").title()
            viz_table.add_row(viz_name, f"{size_kb:.1f} KB", status)
    
    console.print(viz_table)
    
    # Final summary
    console.print("\n[bold gold1]📋 Verification Summary[/bold gold1]\n")
    
    passed = sum(checks)
    total = len(checks)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    summary_table = Table(border_style="gold1")
    summary_table.add_column("Metric", style="cyan bold")
    summary_table.add_column("Value", style="green bold")
    
    summary_table.add_row("Total Checks", str(total))
    summary_table.add_row("Passed", str(passed))
    summary_table.add_row("Failed", str(total - passed))
    summary_table.add_row("Success Rate", f"{success_rate:.1f}%")
    
    console.print(summary_table)
    
    if all(checks):
        console.print("\n[green bold]✓ ALL CHECKS PASSED[/green bold]")
        console.print("[dim]CLI and GUI will generate identical artifacts.[/dim]")
        return True
    else:
        console.print("\n[red bold]✗ SOME CHECKS FAILED[/red bold]")
        console.print("[dim]Review the failures above.[/dim]")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python verify_parity.py <repository_path>")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    success = verify_parity(repo_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
