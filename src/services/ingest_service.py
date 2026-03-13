import asyncio
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import Dict, List, Any

from src.graph.knowledge_graph import KnowledgeGraph
from src.models.nodes import ModuleNode
from src.agents.surveyor import SurveyorAgent
from src.agents.hydrologist import HydrologistAgent
from src.agents.semanticist import SemanticistAgent
from src.agents.archivist import ArchivistAgent
from src.agents.visualizer import VisualizerAgent
from src.analyzers.semantic_index import SemanticIndex

router = APIRouter(prefix="/ingest", tags=["Codebase Ingestion"])

# Simple in-memory task tracker
active_tasks = {}

def clone_repo(url: str) -> Path:
    parsed = urlparse(url)
    repo_name = parsed.path.strip("/").replace("/", "_")
    target_dir = Path("targets") / repo_name
    target_dir.parent.mkdir(exist_ok=True)
    
    if not target_dir.exists():
        subprocess.run(["git", "clone", "--depth", "1", url, str(target_dir)], check=True)
    return target_dir

async def broadcast_progress(websocket: WebSocket, phase: str, message: str, progress: int):
    await websocket.send_json({
        "phase": phase,
        "message": message,
        "progress": progress
    })

@router.websocket("/ws/{project_name}")
async def ingest_ws(websocket: WebSocket, project_name: str):
    await websocket.accept()
    try:
        # This endpoint will wait for a start command via WebSocket or just start if requested
        # For simplicity, we'll wait for a "start" message with the target path/url
        data = await websocket.receive_json()
        target = data.get("target")
        
        if not target:
            await websocket.send_json({"error": "No target provided"})
            return

        await run_ingest_process(websocket, target)
        
    except WebSocketDisconnect:
        print(f"Ingestion WebSocket disconnected for {project_name}")
    except Exception as e:
        await websocket.send_json({"error": str(e)})

async def run_ingest_process(websocket: WebSocket, target: str):
    trace_log = []
    
    def log_trace(agent: str, action: str, details: str):
        entry = {"agent": agent, "action": action, "details": details, "timestamp": asyncio.get_event_loop().time()}
        trace_log.append(entry)

    try:
        # 0. Initializing
        await broadcast_progress(websocket, "INITIALIZING", f"Preparing analysis for {target}...", 5)
        
        if target.startswith("http"):
            await broadcast_progress(websocket, "CLONING", "Cloning repository from GitHub...", 10)
            target_path = clone_repo(target)
        else:
            target_path = Path(target)
            if not target_path.exists():
                raise Exception(f"Local path {target} does not exist")

        project_name = target_path.name
        output_base = Path(".cartography") / project_name
        output_base.mkdir(parents=True, exist_ok=True)
        
        kg = KnowledgeGraph()
        log_trace("System", "Start", f"Analyzing {project_name}")

        # 1. Surveyor
        await broadcast_progress(websocket, "SURVEYOR", "Mapping module structure and dependencies...", 20)
        surveyor = SurveyorAgent(str(target_path), kg)
        surveyor.analyze_all()
        log_trace("Surveyor", "Analyze", "Structural analysis complete")

        # 2. Hydrologist
        await broadcast_progress(websocket, "HYDROLOGIST", "Extracting data lineage and flow paths...", 40)
        hydrologist = HydrologistAgent(str(target_path), kg)
        hydrologist.analyze_all()
        log_trace("Hydrologist", "Analyze", "Lineage analysis complete")

        # 3. Semanticist
        await broadcast_progress(websocket, "SEMANTICIST", "Interrogating modules for purpose and domain...", 60)
        semanticist = SemanticistAgent(kg)
        semantic_index = SemanticIndex(collection_name=f"purposes_{project_name}")
        
        hubs = [n for n, d in kg.graph.nodes(data=True) if d.get("node_type") == "module"]
        hubs.sort(key=lambda n: kg.graph.nodes[n].get("pagerank_score", 0), reverse=True)
        
        # Analyze top 15 hubs for purpose
        for i, hub_id in enumerate(hubs[:15]):
            path = hub_id.replace("mod:", "")
            full_path = target_path / path
            if full_path.exists():
                code = full_path.read_text(errors="ignore")
                node_data = kg.graph.nodes[hub_id]
                # Filter out Graph related object if needed
                mod_node = ModuleNode(path=node_data.get("path", path), name=node_data.get("name", hub_id))
                purpose = semanticist.generate_purpose_statement(mod_node, code)
                kg.graph.nodes[hub_id]["purpose"] = purpose
                semantic_index.index_module(path, purpose)
            
            await broadcast_progress(websocket, "SEMANTICIST", f"Analyzed purpose for {path} ({i+1}/15)", 60 + int((i/15)*20))

        # 4. Archivist
        await broadcast_progress(websocket, "ARCHIVIST", "Generating structural intelligence artifacts...", 85)
        archivist = ArchivistAgent(kg, str(target_path))
        archivist.generate_CODEBASE_md(hubs)
        
        # Mocking summaries for brief
        surveyor_summary = f"Mapped {len(kg.graph.nodes)} code units and {len(kg.graph.edges)} relationships."
        hydrologist_summary = "Identified primary data ingestion and transformation sinks."
        day_one_answers = semanticist.answer_day_one_questions(surveyor_summary, hydrologist_summary)
        archivist.generate_onboarding_brief(day_one_answers)
        
        # New Artifacts
        archivist.save_lineage_graph(output_base / "lineage_graph.json")
        archivist.save_semantic_index_jsonl(output_base / "module_purpose_index.jsonl")
        archivist.save_state_json(output_base / "state.json", {
            "project": project_name,
            "status": "complete",
            "timestamp": asyncio.get_event_loop().time(),
            "target": str(target_path)
        })
        archivist.save_trace(trace_log)
        
        # Move markdown files to output_base
        for art in ["CODEBASE.md", "onboarding_brief.md"]:
            src_art = target_path / art
            if src_art.exists():
                dest = output_base / art
                if dest.exists(): dest.unlink()
                src_art.rename(dest)

        # 5. Visualizer
        await broadcast_progress(websocket, "VISUALIZER", "Rendering interactive structural maps...", 95)
        kg.save(str(output_base / "module_graph.json")) # Matching req
        viz = VisualizerAgent(kg)
        viz.generate_module_graph(str(output_base / "module_graph.html"))
        viz.generate_lineage_graph(str(output_base / "lineage_graph.html"))

        await broadcast_progress(websocket, "COMPLETE", "Analysis complete. Sector secured.", 100)

    except Exception as e:
        import traceback
        error_msg = f"Analysis Failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        await websocket.send_json({"phase": "ERROR", "message": error_msg, "progress": 0})
