import os
import sys
import click
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

from src.graph.knowledge_graph import KnowledgeGraph
from src.models.nodes import ModuleNode
from src.agents.surveyor import SurveyorAgent
from src.agents.hydrologist import HydrologistAgent
from src.agents.semanticist import SemanticistAgent
from src.agents.archivist import ArchivistAgent
from src.agents.visualizer import VisualizerAgent
from src.analyzers.semantic_index import SemanticIndex
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
    """Headless ingestion logic."""
    if path_or_url.startswith("http"):
        target_path = clone_github_repo(path_or_url)
    else:
        target_path = Path(path_or_url)
    
    project_name = target_path.name
    output_base = Path(".cartography") / project_name
    output_base.mkdir(parents=True, exist_ok=True)

    print(f"Starting Cartography on: {target_path}")
    kg = KnowledgeGraph()
    
    # 1. Surveyor (Structure)
    print("Phase 1: Surveyor Analysis...")
    surveyor = SurveyorAgent(str(target_path), kg)
    surveyor.analyze_all()
    
    # 2. Hydrologist (Lineage)
    print("Phase 2: Hydrologist Analysis...")
    hydrologist = HydrologistAgent(str(target_path), kg)
    hydrologist.analyze_all()
    
    # 3. Semanticist (Purpose)
    print("Phase 3: Semantic Analysis...")
    semanticist = SemanticistAgent(kg)
    semantic_index = SemanticIndex(collection_name=f"purposes_{project_name}")
    
    hubs = [n for n, d in kg.graph.nodes(data=True) if d.get("node_type") == "module"]
    hubs.sort(key=lambda n: kg.graph.nodes[n].get("pagerank_score", 0), reverse=True)
    
    for hub_id in hubs[:10]:
        node_attrs = kg.graph.nodes[hub_id]
        path = hub_id.replace("mod:", "")
        full_path = target_path / path
        if full_path.exists():
            code = full_path.read_text(errors="ignore")
            mod_data = {k: v for k, v in node_attrs.items() if k not in ['node_type', 'pagerank_score']}
            mod_node = ModuleNode(**mod_data)
            purpose = semanticist.generate_purpose_statement(mod_node, code)
            semantic_index.index_module(path, purpose)

    surveyor_summary = f"Analyzed {len(kg.graph.nodes)} nodes."
    hydrologist_summary = "Extracted data flows."
    day_one_answers = semanticist.answer_day_one_questions(surveyor_summary, hydrologist_summary)
    
    # 4. Archivist (Artifacts)
    print("Phase 4: Generating Artifacts...")
    archivist = ArchivistAgent(kg, str(target_path))
    archivist.generate_CODEBASE_md(hubs)
    archivist.generate_onboarding_brief(day_one_answers)
    
    # 5. Visualizer
    print("Phase 5: Generating Visualizations...")
    kg.save(str(output_base / "knowledge_graph.json"))
    visualizer = VisualizerAgent(kg)
    visualizer.generate_html(str(output_base / "interactive_graph.html"))
    
    # Final cleanup/move
    for art in ["CODEBASE.md", "onboarding_brief.md"]:
        src_art = target_path / art
        if not src_art.exists():
            src_art = Path(".") / art
        if src_art.exists():
            src_art.rename(output_base / art)
    
    print(f"Done! Results stored in {output_base}")

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
