#!/usr/bin/env python3
"""
The Brownfield Cartographer - Interactive CLI

A powerful command-line interface for automated brownfield codebase intelligence.
Achieves 100% feature parity with the GUI through shared core services.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint
from rich.syntax import Syntax
from rich.markdown import Markdown

from src.core.cartography_service import CartographyService
from src.core.visualization_service import VisualizationService
from src.core.config_service import ConfigService

app = typer.Typer(
    name="cartograph",
    help="  The Brownfield Cartographer - Automated Codebase Intelligence",
    add_completion=False,
)

console = Console()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYZE COMMAND
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def analyze(
    target: str = typer.Argument(..., help="Repository path or GitHub URL"),
    incremental: bool = typer.Option(True, "--incremental/--full", help="Use incremental analysis mode"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Custom output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔍 Run full system scan on a codebase.
    
    Performs comprehensive structural analysis, data lineage extraction,
    and semantic documentation generation.
    
    Examples:
        cartograph analyze ./my-project
        cartograph analyze https://github.com/user/repo.git
        cartograph analyze ./legacy-code --full --verbose
    """
    console.print(Panel.fit(
        "[bold gold1]🗺️  BROWNFIELD CARTOGRAPHER[/bold gold1]\n"
        "[dim]Automated Codebase Intelligence System[/dim]",
        border_style="gold1",
    ))
    
    service = CartographyService(progress_callback=_create_progress_callback(verbose))
    
    # Handle GitHub URLs
    if target.startswith("http"):
        console.print(f"\n[cyan]→[/cyan] Cloning repository from [bold]{target}[/bold]...")
        try:
            repo_path = service.clone_repository(target)
            console.print(f"[green]✓[/green] Repository cloned to [bold]{repo_path}[/bold]")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to clone repository: {e}", style="red")
            raise typer.Exit(1)
    else:
        repo_path = Path(target)
        if not repo_path.exists():
            console.print(f"[red]✗[/red] Path does not exist: {target}", style="red")
            raise typer.Exit(1)
    
    # Run analysis
    console.print(f"\n[cyan]→[/cyan] Analyzing [bold]{repo_path.name}[/bold]...")
    console.print(f"[dim]Mode: {'Incremental' if incremental else 'Full'}[/dim]\n")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Running analysis...", total=None)
            
            result = service.analyze_repository(
                repo_path=repo_path,
                repo_input=target,
                out_dir=Path(output_dir) if output_dir else None,
                incremental=incremental,
            )
            
            progress.update(task, completed=True)
        
        # Display results
        _display_analysis_results(result)
        
        console.print(f"\n[green]✓[/green] Analysis complete! Artifacts saved to:")
        console.print(f"  [bold cyan]{Path(result.artifacts['knowledge_graph']).parent}[/bold cyan]")
        
    except Exception as e:
        console.print(f"\n[red]✗[/red] Analysis failed: {e}", style="red")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# MAP COMMAND
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def map(
    project: str = typer.Argument(..., help="Project name"),
    view: str = typer.Option("structure", "--view", "-v", help="View type: structure, lineage, or both"),
    format: str = typer.Option("html", "--format", "-f", help="Output format: html or json"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Custom output path"),
):
    """
    🗺️  Generate graph visualizations.
    
    Creates interactive HTML visualizations or JSON data exports
    for structural maps and data lineage graphs.
    
    Examples:
        cartograph map my-project --view structure
        cartograph map my-project --view lineage --format json
        cartograph map my-project --view both
    """
    console.print(Panel.fit(
        f"[bold gold1]📊 Generating Graph: {view.upper()}[/bold gold1]",
        border_style="gold1",
    ))
    
    viz_service = VisualizationService()
    
    try:
        if view in ["structure", "both"]:
            console.print(f"\n[cyan]→[/cyan] Generating module structure graph...")
            result = viz_service.generate_module_graph(
                project_name=project,
                output_format=format,
                output_path=Path(output) if output else None,
            )
            _display_graph_result(result, "Module Structure")
        
        if view in ["lineage", "both"]:
            console.print(f"\n[cyan]→[/cyan] Generating data lineage graph...")
            result = viz_service.generate_lineage_graph(
                project_name=project,
                output_format=format,
                output_path=Path(output) if output else None,
            )
            _display_graph_result(result, "Data Lineage")
        
        if view not in ["structure", "lineage", "both"]:
            console.print(f"[red]✗[/red] Invalid view type: {view}", style="red")
            console.print("[dim]Valid options: structure, lineage, both[/dim]")
            raise typer.Exit(1)
        
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}", style="red")
        console.print(f"[dim]Run 'cartograph analyze' first to create the project.[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to generate graph: {e}", style="red")
        raise typer.Exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG COMMAND
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def config(
    action: str = typer.Argument("show", help="Action: show, set, reset, export, import"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Configuration key"),
    value: Optional[str] = typer.Option(None, "--value", "-v", help="Configuration value"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="File path for export/import"),
):
    """
    ⚙️  Manage configuration settings.
    
    Configure LLM providers, language settings, and analysis options.
    
    Examples:
        cartograph config show
        cartograph config set --key llm.provider --value gemini
        cartograph config set --key llm.api_key --value sk-...
        cartograph config export --file config.json
        cartograph config reset
    """
    config_service = ConfigService()
    
    if action == "show":
        _display_config(config_service)
    
    elif action == "set":
        if not key or value is None:
            console.print("[red]✗[/red] --key and --value are required for 'set' action", style="red")
            raise typer.Exit(1)
        
        config_service.set_config(key, value)
        console.print(f"[green]✓[/green] Configuration updated: [bold]{key}[/bold] = {value}")
    
    elif action == "reset":
        confirm = typer.confirm("Reset all configuration to defaults?")
        if confirm:
            config_service.reset_config()
            console.print("[green]✓[/green] Configuration reset to defaults")
        else:
            console.print("[yellow]![/yellow] Reset cancelled")
    
    elif action == "export":
        if not file:
            console.print("[red]✗[/red] --file is required for 'export' action", style="red")
            raise typer.Exit(1)
        
        config_service.export_config(file)
        console.print(f"[green]✓[/green] Configuration exported to [bold]{file}[/bold]")
    
    elif action == "import":
        if not file:
            console.print("[red]✗[/red] --file is required for 'import' action", style="red")
            raise typer.Exit(1)
        
        config_service.import_config(file)
        console.print(f"[green]✓[/green] Configuration imported from [bold]{file}[/bold]")
    
    else:
        console.print(f"[red]✗[/red] Invalid action: {action}", style="red")
        console.print("[dim]Valid actions: show, set, reset, export, import[/dim]")
        raise typer.Exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# LIST COMMAND
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def list():
    """
    📋 List all analyzed projects.
    
    Shows all projects that have been analyzed and their metrics.
    """
    console.print(Panel.fit(
        "[bold gold1]📋 ANALYZED PROJECTS[/bold gold1]",
        border_style="gold1",
    ))
    
    service = CartographyService()
    projects = service.list_projects()
    
    if not projects:
        console.print("\n[yellow]![/yellow] No analyzed projects found.")
        console.print("[dim]Run 'cartograph analyze <path>' to analyze a codebase.[/dim]")
        return
    
    table = Table(title=f"\n{len(projects)} Projects", border_style="gold1")
    table.add_column("Project", style="cyan bold")
    table.add_column("Nodes", justify="right", style="green")
    table.add_column("Edges", justify="right", style="blue")
    table.add_column("Artifact Path", style="dim")
    
    for project in projects:
        table.add_row(
            project["name"],
            str(project["node_count"]),
            str(project["edge_count"]),
            project["artifact_path"],
        )
    
    console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY COMMAND
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def summary(
    project: str = typer.Argument(..., help="Project name"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed information"),
):
    """
    📊 Show project summary and metrics.
    
    Displays key metrics, architectural hubs, and health scores.
    
    Examples:
        cartograph summary my-project
        cartograph summary my-project --detailed
    """
    service = CartographyService()
    
    try:
        summary_data = service.get_project_summary(project)
        _display_project_summary(summary_data, detailed)
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}", style="red")
        raise typer.Exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def _create_progress_callback(verbose: bool):
    """Create a progress callback function."""
    def callback(message: str):
        if verbose:
            console.print(f"[dim]{message}[/dim]")
    return callback


def _display_analysis_results(result):
    """Display analysis results in a formatted table."""
    console.print("\n[bold gold1]📊 Analysis Results[/bold gold1]\n")
    
    # Metrics table
    metrics_table = Table(title="System Metrics", border_style="cyan")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", justify="right", style="green bold")
    
    metrics = result.metrics
    metrics_table.add_row("Nodes", str(metrics["node_count"]))
    metrics_table.add_row("Edges", str(metrics["edge_count"]))
    metrics_table.add_row("System Complexity", str(metrics["system_complexity"]))
    metrics_table.add_row("Confidence Score", f"{metrics['confidence_score']:.1%}")
    metrics_table.add_row("Risk Index", str(metrics["risk_index"]))
    metrics_table.add_row("Blast Radius (avg)", str(metrics["blast_radius_avg"]))
    
    console.print(metrics_table)
    
    # Artifacts tree
    console.print("\n[bold gold1]📁 Generated Artifacts[/bold gold1]\n")
    tree = Tree("🗂️  Artifacts", style="gold1")
    
    for name, path in result.artifacts.items():
        tree.add(f"[cyan]{name}[/cyan]: [dim]{path}[/dim]")
    
    console.print(tree)


def _display_graph_result(result, graph_name: str):
    """Display graph generation result."""
    report = result["report"]
    
    console.print(f"[green]✓[/green] {graph_name} generated successfully")
    console.print(f"  [dim]Format:[/dim] [bold]{result['output_format']}[/bold]")
    console.print(f"  [dim]Output:[/dim] [cyan]{result['output_path']}[/cyan]")
    console.print(f"  [dim]Nodes:[/dim] {report.get('node_count', 'N/A')}")
    console.print(f"  [dim]Edges:[/dim] {report.get('edge_count', 'N/A')}")


def _display_config(config_service: ConfigService):
    """Display current configuration."""
    config = config_service.get_config()
    
    console.print(Panel.fit(
        "[bold gold1]⚙️  CONFIGURATION[/bold gold1]",
        border_style="gold1",
    ))
    
    # LLM Configuration
    console.print("\n[bold cyan]🤖 LLM Configuration[/bold cyan]")
    llm_table = Table(show_header=False, border_style="dim")
    llm_table.add_column("Key", style="cyan")
    llm_table.add_column("Value", style="green")
    
    llm_config = config.get("llm", {})
    llm_table.add_row("Provider", llm_config.get("provider", "N/A"))
    llm_table.add_row("Model", llm_config.get("model", "N/A"))
    llm_table.add_row("API Key", "***" if llm_config.get("api_key") else "[red]Not set[/red]")
    
    console.print(llm_table)
    
    # Language Configuration
    console.print("\n[bold cyan]💬 Language Support[/bold cyan]")
    lang_table = Table(show_header=False, border_style="dim")
    lang_table.add_column("Language", style="cyan")
    lang_table.add_column("Enabled", style="green")
    
    lang_config = config.get("languages", {})
    for lang, enabled in lang_config.items():
        status = "[green]✓[/green]" if enabled else "[red]✗[/red]"
        lang_table.add_row(lang.capitalize(), status)
    
    console.print(lang_table)
    
    # Analysis Configuration
    console.print("\n[bold cyan]🔍 Analysis Options[/bold cyan]")
    analysis_table = Table(show_header=False, border_style="dim")
    analysis_table.add_column("Option", style="cyan")
    analysis_table.add_column("Value", style="green")
    
    analysis_config = config.get("analysis", {})
    for key, value in analysis_config.items():
        if type(value).__name__ in ('list', 'tuple'):
            value = ", ".join(str(v) for v in value[:3]) + ("..." if len(value) > 3 else "")
        analysis_table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(analysis_table)
    
    console.print(f"\n[dim]Config file: {config_service.CONFIG_FILE}[/dim]")


def _display_project_summary(summary_data: dict, detailed: bool):
    """Display project summary."""
    console.print(Panel.fit(
        f"[bold gold1]📊 PROJECT SUMMARY: {summary_data['project_name']}[/bold gold1]",
        border_style="gold1",
    ))
    
    # Metrics
    console.print("\n[bold cyan]📈 Metrics[/bold cyan]")
    metrics = summary_data["metrics"]
    
    metrics_table = Table(show_header=False, border_style="dim")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", justify="right", style="green bold")
    
    metrics_table.add_row("Total Nodes", str(summary_data["node_count"]))
    metrics_table.add_row("Total Edges", str(summary_data["edge_count"]))
    metrics_table.add_row("System Complexity", str(metrics["system_complexity"]))
    metrics_table.add_row("Confidence Score", f"{metrics['confidence_score']:.1%}")
    metrics_table.add_row("Risk Index", str(metrics["risk_index"]))
    metrics_table.add_row("Blast Radius (avg)", str(metrics["blast_radius_avg"]))
    
    console.print(metrics_table)
    
    # Architectural Hubs
    console.print("\n[bold cyan]🏛️  Architectural Hubs (Top 5)[/bold cyan]")
    hubs_table = Table(border_style="dim")
    hubs_table.add_column("Path", style="cyan")
    hubs_table.add_column("PageRank", justify="right", style="yellow")
    hubs_table.add_column("Fan-In", justify="right", style="green")
    hubs_table.add_column("Fan-Out", justify="right", style="blue")
    
    for hub in summary_data["architectural_hubs"][:5]:
        hubs_table.add_row(
            hub["path"],
            f"{hub['pagerank_score']:.4f}",
            str(hub["fan_in"]),
            str(hub["fan_out"]),
        )
    
    console.print(hubs_table)
    
    if detailed and len(summary_data["architectural_hubs"]) > 5:
        console.print(f"\n[dim]... and {len(summary_data['architectural_hubs']) - 5} more hubs[/dim]")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
