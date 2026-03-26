#!/usr/bin/env python3
"""
The Brownfield Cartographer - Interactive REPL

A persistent, interactive command-line interface for brownfield codebase intelligence.
Enter commands with /command syntax and maintain session state across operations.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.markdown import Markdown

from src.core.cartography_service import CartographyService
from src.core.visualization_service import VisualizationService
from src.core.config_service import ConfigService
from src.orchestrator import CartographyOrchestrator
from src.graph.knowledge_graph import KnowledgeGraph

console = Console()


class CartographerREPL:
    """Interactive REPL for the Brownfield Cartographer."""
    
    def __init__(self):
        self.config = ConfigService()
        self.verbose = False
        self.running = True
        self.current_project: Optional[str] = None
        self.cwd = Path.cwd()
        
        # Create progress callback for CartographyService
        def progress_callback(msg: str):
            if self.verbose:
                console.print(f"[dim]{msg}[/dim]")
        
        self.cartography_service = CartographyService(progress_callback=progress_callback)
        self.visualization_service = VisualizationService()
        
        # Command registry
        self.commands = {
            'help': self.cmd_help,
            'list': self.cmd_list,
            'analyze': self.cmd_analyze,
            'summary': self.cmd_summary,
            'map': self.cmd_map,
            'config_show': self.cmd_config_show,
            'artifacts': self.cmd_artifacts,
            'clear': self.cmd_clear,
            'whereami': self.cmd_whereami,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
        }
    
    def show_welcome(self):
        """Display welcome screen."""
        welcome_text = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║         THE LEGACY CODE CARTOGRAPHER - Interactive REPL              ║
║                                                                      ║
║        Automated Codebase Intelligence System                        ║
║        Persistent Session • Direct Service Integration               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Welcome to the Legacy Code Cartographer interactive session!

Type /help to see available commands
Type /exit or /quit to leave the session
Press Ctrl+C to cancel current operation
Press Ctrl+D for quick exit

Ready to map your brownfield codebase...
"""
        console.print(welcome_text, style="gold1")
    
    def get_prompt(self) -> str:
        """Get the command prompt."""
        return "[bold gold1]Legacy-Code-Cartographer >[/bold gold1] "
    
    def parse_command(self, user_input: str) -> tuple[str, list[str]]:
        """
        Parse user input into command and arguments.
        
        Args:
            user_input: Raw user input
        
        Returns:
            Tuple of (command, arguments)
        """
        user_input = user_input.strip()
        
        # Remove leading slash if present
        if user_input.startswith('/'):
            user_input = user_input[1:]
        
        # Split into command and args
        parts = user_input.split()
        if not parts:
            return '', []
        
        command = parts[0].lower()
        args = parts[1:]
        
        return command, args
    
    def execute_command(self, command: str, args: list[str]):
        """
        Execute a command with given arguments.
        
        Args:
            command: Command name
            args: Command arguments
        """
        if not command:
            return
        
        if command in self.commands:
            try:
                self.commands[command](args)
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠[/yellow] Operation cancelled by user", style="yellow")
            except Exception as e:
                console.print(f"[red]✗[/red] Error executing command: {e}", style="red")
                if '--debug' in args or os.getenv('DEBUG'):
                    console.print_exception()
        else:
            console.print(f"[red]✗[/red] Unknown command: /{command}", style="red")
            console.print("[dim]Type /help to see available commands[/dim]")
    
    # ─────────────────────────────────────────────────────────────────────────
    # COMMAND IMPLEMENTATIONS
    # ─────────────────────────────────────────────────────────────────────────
    
    def cmd_help(self, args: list[str]):
        """Display help information."""
        help_table = Table(title="Available Commands", border_style="gold1", show_header=True)
        help_table.add_column("Command", style="cyan bold", width=30)
        help_table.add_column("Description", style="white")
        
        commands_info = [
            ("/help", "Show this help message"),
            ("/list", "Display all analyzed projects"),
            ("/analyze <path_or_url>", "Run full analysis pipeline on a repository"),
            ("/summary <project>", "Show executive summary of a project"),
            ("/map <project> --view <type>", "Generate visualizations (structure/lineage/both)"),
            ("/config_show", "Display LLM and environment configuration"),
            ("/artifacts <project>", "List all artifact file paths for a project"),
            ("/clear", "Clear the terminal screen"),
            ("/whereami", "Show current working directory"),
            ("/exit or /quit", "Exit the interactive session"),
        ]
        
        for cmd, desc in commands_info:
            help_table.add_row(cmd, desc)
        
        console.print("\n")
        console.print(help_table)
        console.print("\n[dim]Tip: Press Ctrl+C to cancel any running operation[/dim]")
        console.print("[dim]Tip: Press Ctrl+D for quick exit[/dim]\n")
    
    def cmd_list(self, args: list[str]):
        """List all analyzed projects."""
        console.print("\n[cyan]→[/cyan] Loading analyzed projects...\n")
        
        projects = self.cartography_service.list_projects()
        
        if not projects:
            console.print("[yellow]![/yellow] No analyzed projects found.")
            console.print("[dim]Run /analyze <path> to analyze a codebase.[/dim]\n")
            return
        
        table = Table(title=f"{len(projects)} Analyzed Projects", border_style="gold1")
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
        console.print()
    
    def cmd_analyze(self, args: list[str]):
        """Analyze a repository."""
        if not args:
            console.print("[red]✗[/red] Missing argument: <path_or_url>", style="red")
            console.print("[dim]Usage: /analyze <path_or_url> [--full] [--verbose][/dim]\n")
            return
        
        target = args[0]
        incremental = '--full' not in args
        verbose = '--verbose' in args
        
        console.print(Panel.fit(
            "[bold gold1]🗺️  STARTING ANALYSIS[/bold gold1]\n"
            f"[dim]Target: {target}[/dim]",
            border_style="gold1",
        ))
        
        # Handle GitHub URLs
        if target.startswith("http"):
            console.print(f"\n[cyan]→[/cyan] Cloning repository from [bold]{target}[/bold]...")
            try:
                repo_path = self.cartography_service.clone_repository(target)
                console.print(f"[green]✓[/green] Repository cloned to [bold]{repo_path}[/bold]")
            except Exception as e:
                console.print(f"[red]✗[/red] Failed to clone repository: {e}", style="red")
                return
        else:
            repo_path = Path(target)
            if not repo_path.exists():
                console.print(f"[red]✗[/red] Path does not exist: {target}", style="red")
                return
        
        # Run analysis
        console.print(f"\n[cyan]→[/cyan] Analyzing [bold]{repo_path.name}[/bold]...")
        console.print(f"[dim]Mode: {'Incremental' if incremental else 'Full'}[/dim]\n")
        
        try:
            result = self.cartography_service.analyze_repository(
                repo_path=repo_path,
                repo_input=target,
                incremental=incremental,
            )
            
            # Display results
            console.print("\n[bold gold1]📊 Analysis Complete[/bold gold1]\n")
            
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
            
            console.print(f"\n[green]✓[/green] Artifacts saved to:")
            console.print(f"  [bold cyan]{Path(result.artifacts['knowledge_graph']).parent}[/bold cyan]\n")
            
        except Exception as e:
            console.print(f"\n[red]✗[/red] Analysis failed: {e}", style="red")
            if verbose or '--debug' in args:
                console.print_exception()
    
    def cmd_summary(self, args: list[str]):
        """Show project summary."""
        if not args:
            console.print("[red]✗[/red] Missing argument: <project>", style="red")
            console.print("[dim]Usage: /summary <project> [--detailed][/dim]\n")
            return
        
        project = args[0]
        detailed = '--detailed' in args
        
        console.print(f"\n[cyan]→[/cyan] Loading summary for [bold]{project}[/bold]...\n")
        
        try:
            summary_data = self.cartography_service.get_project_summary(project)
            
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
            
            console.print()
            
        except FileNotFoundError as e:
            console.print(f"[red]✗[/red] {e}", style="red")
            console.print("[dim]Run /list to see available projects[/dim]\n")
        except Exception as e:
            console.print(f"[red]✗[/red] Error loading summary: {e}", style="red")
    
    def cmd_map(self, args: list[str]):
        """Generate visualizations."""
        if not args:
            console.print("[red]✗[/red] Missing argument: <project>", style="red")
            console.print("[dim]Usage: /map <project> --view <structure|lineage|both> [--format html|json][/dim]\n")
            return
        
        project = args[0]
        
        # Parse view type
        view = "structure"
        if '--view' in args:
            view_idx = args.index('--view')
            if view_idx + 1 < len(args):
                view = args[view_idx + 1]
        
        # Parse format
        format_type = "html"
        if '--format' in args:
            format_idx = args.index('--format')
            if format_idx + 1 < len(args):
                format_type = args[format_idx + 1]
        
        console.print(Panel.fit(
            f"[bold gold1]📊 Generating Graph: {view.upper()}[/bold gold1]",
            border_style="gold1",
        ))
        
        try:
            if view in ["structure", "both"]:
                console.print(f"\n[cyan]→[/cyan] Generating module structure graph...")
                result = self.visualization_service.generate_module_graph(
                    project_name=project,
                    output_format=format_type,
                )
                self._display_graph_result(result, "Module Structure")
            
            if view in ["lineage", "both"]:
                console.print(f"\n[cyan]→[/cyan] Generating data lineage graph...")
                result = self.visualization_service.generate_lineage_graph(
                    project_name=project,
                    output_format=format_type,
                )
                self._display_graph_result(result, "Data Lineage")
            
            if view not in ["structure", "lineage", "both"]:
                console.print(f"[red]✗[/red] Invalid view type: {view}", style="red")
                console.print("[dim]Valid options: structure, lineage, both[/dim]")
            
            console.print()
            
        except FileNotFoundError as e:
            console.print(f"[red]✗[/red] {e}", style="red")
            console.print("[dim]Run /analyze first to create the project.[/dim]\n")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to generate graph: {e}", style="red")
    
    def cmd_config_show(self, args: list[str]):
        """Display configuration."""
        console.print("\n")
        console.print(Panel.fit(
            "[bold gold1]⚙️  CONFIGURATION[/bold gold1]",
            border_style="gold1",
        ))
        
        config = self.config_service.get_config()
        
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
        
        console.print(f"\n[dim]Config file: {self.config_service.CONFIG_FILE}[/dim]\n")
    
    def cmd_artifacts(self, args: list[str]):
        """List artifact file paths for a project."""
        if not args:
            console.print("[red]✗[/red] Missing argument: <project>", style="red")
            console.print("[dim]Usage: /artifacts <project>[/dim]\n")
            return
        
        project = args[0]
        cartography_dir = Path(".cartography")
        project_dir = cartography_dir / project
        
        if not project_dir.exists():
            console.print(f"[red]✗[/red] Project not found: {project}", style="red")
            console.print("[dim]Run /list to see available projects[/dim]\n")
            return
        
        console.print(f"\n[bold gold1]📁 Artifacts for: {project}[/bold gold1]\n")
        
        # Define expected artifacts
        artifacts = {
            "Knowledge Graph": "knowledge_graph.json",
            "Module Graph (HTML)": "module_graph.html",
            "Lineage Graph (HTML)": "lineage_graph.html",
            "Codebase Documentation": "CODEBASE.md",
            "Onboarding Brief": "ONBOARDING_BRIEF.md",
            "Semantic Index": "semantic_index.json",
            "Trace Events": "trace.json",
        }
        
        tree = Tree(f"🗂️  {project_dir.absolute()}", style="gold1")
        
        for name, filename in artifacts.items():
            artifact_path = project_dir / filename
            if artifact_path.exists():
                size_kb = artifact_path.stat().st_size / 1024
                tree.add(f"[green]✓[/green] [cyan]{name}[/cyan]: [dim]{artifact_path.absolute()}[/dim] [yellow]({size_kb:.1f} KB)[/yellow]")
            else:
                tree.add(f"[red]✗[/red] [dim]{name}: Not found[/dim]")
        
        console.print(tree)
        console.print()
    
    def cmd_clear(self, args: list[str]):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')
        console.print("[green]✓[/green] Terminal cleared\n")
    
    def cmd_whereami(self, args: list[str]):
        """Show current working directory."""
        console.print(f"\n[bold cyan]Current Working Directory:[/bold cyan]")
        console.print(f"  [yellow]{self.cwd.absolute()}[/yellow]\n")
    
    def cmd_exit(self, args: list[str]):
        """Exit the REPL."""
        console.print("\n[gold1]👋 Exiting Legacy Code Cartographer...[/gold1]")
        console.print("[dim]Thank you for mapping your brownfield codebase![/dim]\n")
        self.running = False
    
    # ─────────────────────────────────────────────────────────────────────────
    # HELPER METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    def _display_graph_result(self, result: dict, graph_name: str):
        """Display graph generation result."""
        report = result["report"]
        
        console.print(f"[green]✓[/green] {graph_name} generated successfully")
        console.print(f"  [dim]Format:[/dim] [bold]{result['output_format']}[/bold]")
        console.print(f"  [dim]Output:[/dim] [cyan]{result['output_path']}[/cyan]")
        console.print(f"  [dim]Nodes:[/dim] {report.get('node_count', 'N/A')}")
        console.print(f"  [dim]Edges:[/dim] {report.get('edge_count', 'N/A')}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # MAIN REPL LOOP
    # ─────────────────────────────────────────────────────────────────────────
    
    def run(self):
        """Run the interactive REPL."""
        self.show_welcome()
        
        while self.running:
            try:
                # Get user input
                user_input = console.input(self.get_prompt())
                
                # Parse and execute command
                command, args = self.parse_command(user_input)
                self.execute_command(command, args)
                
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                console.print("\n[yellow]⚠[/yellow] Use /exit or /quit to leave the session\n")
                continue
            
            except EOFError:
                # Handle Ctrl+D gracefully
                console.print("\n")
                self.cmd_exit([])
                break
            
            except Exception as e:
                console.print(f"\n[red]✗[/red] Unexpected error: {e}", style="red")
                if os.getenv('DEBUG'):
                    console.print_exception()
                console.print()


def main():
    """Main entry point."""
    repl = CartographerREPL()
    repl.run()


if __name__ == "__main__":
    main()
