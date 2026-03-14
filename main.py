import os
import sys
import click
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

from src.graph.knowledge_graph import KnowledgeGraph
from src.models.nodes import ModuleNode
from src.orchestrator import CartographyOrchestrator
from src.services.server_manager import ServerManager

load_dotenv()

def clone_github_repo(url: str) -> Path:
    """Clones a GitHub repo into targets/ and returns the local path."""
    parsed = urlparse(url)
    repo_name = parsed.path.strip("/").replace("/", "_")
    target_dir = Path("targets") / repo_name
    
    if not target_dir.exists():
        print(f"Cloning {url} into {target_dir}...")
        subprocess.run(["git", "clone", "--depth", "1", url, str(target_dir)], check=True)
    else:
        print(f"Repo already exists at {target_dir}")
    
    return target_dir

def run_ingest(path_or_url: str):
    """Headless ingestion logic using the new orchestrator."""
    if path_or_url.startswith("http"):
        target_path = clone_github_repo(path_or_url)
    else:
        target_path = Path(path_or_url)
    
    print(f"Initializing Orchestrator for: {target_path}")
    orchestrator = CartographyOrchestrator(target_path)
    results = orchestrator.analyze(incremental=True)
    
    print(f"Ingestion complete. Artifacts:")
    for key, path in results.items():
        print(f" - {key}: {path}")

@click.group()
def cli():
    """The Brownfield Cartographer CLI"""
    pass

@cli.command()
@click.argument('target')
def ingest(target):
    """Analyze a codebase (local path or GitHub URL)."""
    run_ingest(target)

@cli.command()
@click.option('--port', default=5000, help='Port to run the GUI on.')
def gui(port):
    """Start the integrated DeepWiki GUI."""
    manager = ServerManager(port=port)
    manager.start_gui()

if __name__ == "__main__":
    cli()
