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
from src.orchestrator import CartographyOrchestrator

router = APIRouter(prefix="/ingest", tags=["Codebase Ingestion"])

# Simple in-memory task tracker
active_tasks = {}

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
    try:
        # 0. Initializing
        await broadcast_progress(websocket, "INITIALIZING", f"Preparing analysis for {target}...", 5)
        
        # Determine target path
        if target.startswith("http"):
            from main import clone_github_repo
            await broadcast_progress(websocket, "CLONING", "Cloning repository from GitHub...", 10)
            target_path = clone_github_repo(target)
        else:
            target_path = Path(target)
            if not target_path.exists():
                raise Exception(f"Local path {target} does not exist")

        # Setup Orchestrator
        main_loop = asyncio.get_running_loop()

        async def web_progress_callback(msg: str):
            # Map orchestrator messages to phases/progress if possible, or just send as generic progress
            # For simplicity, we'll extract "Running X agent" and update progress
            phase = "ANALYZING"
            progress = 20
            if "Surveyor" in msg: 
                phase = "SURVEYOR"
                progress = 20
            elif "Hydrologist" in msg:
                phase = "HYDROLOGIST"
                progress = 40
            elif "Semanticist" in msg:
                phase = "SEMANTICIST"
                progress = 60
            elif "synthesis" in msg:
                phase = "SYNTHESIS"
                progress = 80
            elif "Serializing" in msg:
                phase = "ARCHIVIST"
                progress = 90
            
            await broadcast_progress(websocket, phase, msg, progress)

        # We need a sync-to-async bridge for the callback if orchestrator is sync
        def sync_callback(msg: str):
            asyncio.run_coroutine_threadsafe(web_progress_callback(msg), main_loop)

        orchestrator = CartographyOrchestrator(
            repo_path=target_path,
            repo_input=target,
            progress_callback=sync_callback
        )

        # Run analysis
        await broadcast_progress(websocket, "STARTING", "Orchestrator starting engine...", 15)
        
        # Run in a thread to not block the event loop
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, orchestrator.analyze, True) # True for incremental if possible

        await broadcast_progress(websocket, "COMPLETE", "Analysis complete. Sector secured.", 100)
        await websocket.send_json({"status": "success", "artifacts": results})

    except Exception as e:
        import traceback
        error_msg = f"Analysis Failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        await websocket.send_json({"phase": "ERROR", "message": error_msg, "progress": 0})
