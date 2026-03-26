import os
import json
from fastapi import APIRouter, HTTPException, Response
from typing import List, Dict, Optional
from pathlib import Path
from src.models.schemas import DeepWikiReport, NodeVirtualized, Archive, HubTableEntry, CodebaseHealthScore, RiskCard

router = APIRouter(prefix="/discovery", tags=["Discovery"])

CARTOGRAPHY_DIR = Path(".cartography")

@router.get("/archives", response_model=List[Archive])
async def get_archives():
    """
    Returns a list of all analyzed codebases found in .cartography.
    """
    archives = []
    if not CARTOGRAPHY_DIR.exists():
        return []
    
    for item in CARTOGRAPHY_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            archives.append(Archive(
                name=item.name,
                description=f"Structural intelligence for {item.name}.",
                sector="Codebase Archive", # Could be parsed from metadata if available
                artifact_count=len(list(item.iterdir())),
                last_updated="2026-03-11" # Should ideally be from fstat
            ))
    return archives

@router.get("/summary/{project_name}", response_model=DeepWikiReport)
async def get_summary(project_name: str):
    """
    Returns the DeepWiki-style summary report for a project using real data.
    """
    from src.graph.knowledge_graph import KnowledgeGraph
    
    kg_path = CARTOGRAPHY_DIR / project_name / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail="Project analysis not found")
    
    kg = KnowledgeGraph()
    kg.load(kg_path)
    
    # Process nodes to find hubs and metrics
    hubs = []
    pr_scores = kg.pagerank(module_import_only=True)
    
    for node_id, attrs in kg.graph.nodes(data=True):
        if attrs.get("node_type") == "module":
            pr_score = pr_scores.get(node_id, 0)
            fan_in = kg.graph.in_degree(node_id)
            
            if pr_score > 0.05 or fan_in > 5:
                hubs.append(HubTableEntry(
                    node_id=node_id,
                    path=attrs.get("path", node_id),
                    pagerank_score=pr_score,
                    fan_out=kg.graph.out_degree(node_id),
                    fan_in=fan_in,
                    purpose=attrs.get("purpose_statement", "Auto-indexed module")
                ))

    # Sort hubs by PageRank
    hubs.sort(key=lambda x: x.pagerank_score, reverse=True)
    
    # Calculate health metrics
    maintainability = 85.0 # Basic baseline
    br_avg = 0
    if len(kg.graph.nodes) > 0:
        br_total = sum(len(kg.downstream(n)) for n in kg.graph.nodes)
        br_avg = round(br_total / len(kg.graph.nodes), 2)

    return DeepWikiReport(
        project_name=project_name,
        summary=f"Analysis of {project_name} reveals a structural topology with {len(kg.graph.nodes)} interconnected artifacts. Critical paths centered around {len(hubs)} identified hubs.",
        health_score=CodebaseHealthScore(
            maintainability=maintainability,
            blast_radius_avg=br_avg,
            circular_dependencies_count=0 # Placeholder for SCC logic
        ),
        risk_cards=[
            RiskCard(
                title="Hub Centralization",
                severity="medium",
                description="High concentration of dependencies in core utility modules.",
                impact_nodes=[h.path for h in hubs[:3]]
            )
        ],
        architectural_hubs=hubs[:10],
        data_lineage_summary="Multi-stage dependency graph based on static analysis.",
        last_updated="2026-03-11"
    )

@router.get("/metrics/{project_name}")
async def get_metrics(project_name: str):
    """
    Returns specific metrics for the Sector Dashboard cards.
    """
    from src.graph.knowledge_graph import KnowledgeGraph
    kg_path = CARTOGRAPHY_DIR / project_name / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    kg = KnowledgeGraph()
    kg.load(kg_path)

    # Simplified complexity metric
    complexity = sum(attrs.get("complexity_score", 0) for _, attrs in kg.graph.nodes(data=True)) / max(len(kg.graph.nodes), 1)
    
    # Confidence Score (Placeholder)
    confidence = 0.92 

    # Risk Index (Circular dependencies + Dead code)
    dead_code = sum(1 for _, attrs in kg.graph.nodes(data=True) if attrs.get("is_dead_code_candidate"))
    
    # Primary Ingestion Point (Node with highest out-degree + is_source_of_truth)
    sources = [n for n, d in kg.graph.nodes(data=True) if kg.graph.in_degree(n) == 0]
    primary_source = min(sources, key=len) if sources else "Unknown"

    return {
        "systemComplexity": round(complexity, 2),
        "confidenceScore": confidence,
        "riskIndex": dead_code,
        "primaryIngestion": primary_source
    }

@router.get("/lineage/{project_name}")
async def get_lineage(project_name: str, node_id: Optional[str] = None):
    """
    Returns lineage data, optionally centered around a specific node.
    """
    from src.graph.data_lineage import DataLineageGraph
    kg_path = CARTOGRAPHY_DIR / project_name / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    dlg = DataLineageGraph()
    dlg.load(kg_path)

    if node_id:
        attrs = dlg.graph.nodes.get(node_id, {})
        blast_radius = dlg.blast_radius(node_id)
        upstream = dlg.upstream(node_id)
        return {
            "center": node_id,
            "blastRadius": blast_radius,
            "upstream": upstream,
            "connectedNodes": list(set([node_id] + blast_radius + upstream)),
            "source_file": attrs.get("source_file"),
            "lineage_range": attrs.get("lineage_range"),
            "transformation_type": attrs.get("transformation_type")
        }
    
    return {
        "sources": dlg.find_sources(),
        "sinks": dlg.find_sinks(),
        "totalNodes": len(dlg.graph.nodes)
    }

@router.get("/lineage/html/{project_name}")
async def get_lineage_html(project_name: str):
    """
    Serves the interactive lineage graph HTML.
    """
    path = CARTOGRAPHY_DIR / project_name / "lineage_graph.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Lineage graph HTML not found")
        
    return Response(content=path.read_text(encoding="utf-8"), media_type="text/html")

@router.get("/semantic/{project_name}")
async def get_semantic_index(project_name: str):
    """
    Returns all modules with their purpose statements for the virtualized table.
    """
    from src.graph.knowledge_graph import KnowledgeGraph
    kg_path = CARTOGRAPHY_DIR / project_name / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    kg = KnowledgeGraph()
    kg.load(kg_path)

    modules = []
    for node_id, attrs in kg.graph.nodes(data=True):
        if attrs.get("node_type") == "module":
            modules.append({
                "id": node_id,
                "path": attrs.get("path", node_id),
                "purpose": attrs.get("purpose_statement", "No purpose extracted."),
                "language": attrs.get("language", "unknown"),
                "complexity": attrs.get("complexity_score", 0)
            })
    
    return modules

@router.get("/graph/{project_name}/module")
async def get_graph(project_name: str):
    # (Existing graph endpoint logic updated to use KnowledgeGraph)
    from src.graph.knowledge_graph import KnowledgeGraph
    kg_path = CARTOGRAPHY_DIR / project_name / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail=f"Knowledge graph not found at {kg_path}")
    
    kg = KnowledgeGraph()
    kg.load(kg_path)
    
    rf_nodes = []
    rf_edges = []
    
    for i, (node_id, attrs) in enumerate(kg.graph.nodes(data=True)):
        rf_nodes.append({
            "id": node_id,
            "position": {"x": (i % 5) * 200, "y": (i // 5) * 150},
            "data": { 
                "label": node_id.split(":")[-1],
                "type": attrs.get("node_type", "unknown"),
                "isHub": attrs.get("pagerank_score", 0) > 0.05
            }
        })
    
    for u, v, attrs in kg.graph.edges(data=True):
        rf_edges.append({
            "id": f"e-{u}-{v}",
            "source": u,
            "target": v,
            "label": attrs.get("edge_type", "")
        })
        
    return {"nodes": rf_nodes, "edges": rf_edges}

@router.get("/graph/{project_name}/module_graph.html")
async def get_module_graph_html(project_name: str):
    """
    Serves the interactive module graph HTML.
    """
    path = CARTOGRAPHY_DIR / project_name / "module_graph.html"
    if not path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Module graph HTML not found at {path}. Ensure analysis completed successfully."
        )
        
    return Response(content=path.read_text(), media_type="text/html")

@router.get("/projects/{project_name}/artifacts/{file_name}")
async def get_artifact(project_name: str, file_name: str):
    """
    Serves generated markdown reports and other artifacts.
    """
    path = CARTOGRAPHY_DIR / project_name / file_name
    if not path.exists():
        # Try case-insensitive or common variations
        if file_name == "CODEBASE.md":
            path = CARTOGRAPHY_DIR / project_name / "codebase.md"
        elif file_name == "ONBOARDING_BRIEF.md":
            path = CARTOGRAPHY_DIR / project_name / "onboarding_brief.md"
            
        if not path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Artifact '{file_name}' not found at {CARTOGRAPHY_DIR / project_name}. Available files: {list((CARTOGRAPHY_DIR / project_name).glob('*')) if (CARTOGRAPHY_DIR / project_name).exists() else 'directory not found'}"
            )
        
    return Response(content=path.read_text(), media_type="text/markdown")

@router.get("/docs/{project_name}/{file_name}")
async def get_doc_file(project_name: str, file_name: str):
    path = CARTOGRAPHY_DIR / project_name / file_name
    if not path.exists():
        # Try case-insensitive or common variations
        if file_name == "CODEBASE.md":
            path = CARTOGRAPHY_DIR / project_name / "codebase.md"
        elif file_name == "ONBOARDING_BRIEF.md":
            path = CARTOGRAPHY_DIR / project_name / "onboarding_brief.md"
            
        if not path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Document '{file_name}' not found at {CARTOGRAPHY_DIR / project_name}. Available files: {list((CARTOGRAPHY_DIR / project_name).glob('*')) if (CARTOGRAPHY_DIR / project_name).exists() else 'directory not found'}"
            )
        
    return Response(content=path.read_text(), media_type="text/markdown")
