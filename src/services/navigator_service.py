"""
Navigator Service - Agent-powered graph analysis tools.

Provides blast_radius and trace_lineage endpoints for the Navigator interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.graph.knowledge_graph import KnowledgeGraph

router = APIRouter(prefix="/navigator", tags=["Navigator"])

CARTOGRAPHY_DIR = Path(".cartography")


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────

class BlastRadiusRequest(BaseModel):
    project_id: str
    node_path: str


class BlastRadiusResponse(BaseModel):
    node_path: str
    downstream_count: int
    downstream_nodes: List[str]
    downstream_edges: List[Dict[str, str]]
    blast_radius_score: float


class TraceLineageRequest(BaseModel):
    project_id: str
    node_path: str


class LineageHop(BaseModel):
    node: str
    node_type: str
    storage_type: Optional[str] = None
    transformation_type: Optional[str] = None
    source_datasets: List[str] = []


class TraceLineageResponse(BaseModel):
    node_path: str
    path_length: int
    upstream_path: List[str]
    primary_source: Optional[str]
    lineage_chain: List[LineageHop]


class NodeDetailsResponse(BaseModel):
    id: str
    path: str
    node_type: str
    label: str
    domain_cluster: Optional[str] = None
    purpose_statement: Optional[str] = None
    git_velocity: Optional[int] = None
    complexity_score: Optional[float] = None
    public_api: List[Dict[str, str]] = []
    sql_query: Optional[str] = None
    storage_type: Optional[str] = None
    freshness_sla: Optional[str] = None
    source_code: Optional[str] = None
    dependencies: Dict[str, List[str]] = {}


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/blast_radius", response_model=BlastRadiusResponse)
async def blast_radius(request: BlastRadiusRequest):
    """
    Calculate blast radius - all downstream dependencies for a given node.
    
    Returns nodes that depend on the specified node (directly or transitively).
    """
    kg_path = CARTOGRAPHY_DIR / request.project_id / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    kg = KnowledgeGraph.load(kg_path)
    
    # Find node by path
    node_id = _find_node_by_path(kg, request.node_path)
    if not node_id:
        raise HTTPException(status_code=404, detail=f"Node not found: {request.node_path}")
    
    # Get all downstream dependencies
    downstream_ids = kg.downstream(node_id)
    
    # Get downstream nodes with their paths
    downstream_nodes = []
    for nid in downstream_ids:
        attrs = kg.graph.nodes.get(nid, {})
        path = attrs.get("path") or attrs.get("name") or nid
        downstream_nodes.append(path)
    
    # Get edges between source and downstream nodes
    downstream_edges = []
    for target_id in downstream_ids:
        # Check if there's a direct edge
        if kg.graph.has_edge(node_id, target_id):
            edge_attrs = kg.graph.edges[node_id, target_id]
            target_attrs = kg.graph.nodes.get(target_id, {})
            target_path = target_attrs.get("path") or target_attrs.get("name") or target_id
            
            downstream_edges.append({
                "source": request.node_path,
                "target": target_path,
                "relationship": edge_attrs.get("edge_type", "DEPENDS_ON")
            })
    
    # Calculate blast radius score
    total_nodes = kg.graph.number_of_nodes()
    blast_radius_score = len(downstream_ids) / max(total_nodes, 1)
    
    return BlastRadiusResponse(
        node_path=request.node_path,
        downstream_count=len(downstream_ids),
        downstream_nodes=downstream_nodes,
        downstream_edges=downstream_edges,
        blast_radius_score=round(blast_radius_score, 4)
    )


@router.post("/trace_lineage", response_model=TraceLineageResponse)
async def trace_lineage(request: TraceLineageRequest):
    """
    Trace lineage upstream - follow the path back to the primary source.
    
    Returns the complete lineage chain from the specified node to its origin.
    """
    kg_path = CARTOGRAPHY_DIR / request.project_id / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    kg = KnowledgeGraph.load(kg_path)
    
    # Find node by path
    node_id = _find_node_by_path(kg, request.node_path)
    if not node_id:
        raise HTTPException(status_code=404, detail=f"Node not found: {request.node_path}")
    
    # Trace upstream lineage
    lineage_chain = []
    upstream_path = []
    current_id = node_id
    visited = set()
    
    while current_id and current_id not in visited:
        visited.add(current_id)
        attrs = kg.graph.nodes.get(current_id, {})
        node_type = attrs.get("node_type", "unknown")
        path = attrs.get("path") or attrs.get("name") or current_id
        
        # Get upstream nodes (predecessors)
        upstream_nodes = list(kg.graph.predecessors(current_id))
        source_datasets = []
        for pred_id in upstream_nodes:
            pred_attrs = kg.graph.nodes.get(pred_id, {})
            pred_path = pred_attrs.get("path") or pred_attrs.get("name") or pred_id
            source_datasets.append(pred_path)
        
        # Add to lineage chain
        lineage_chain.append(LineageHop(
            node=path,
            node_type=node_type,
            storage_type=attrs.get("storage_type"),
            transformation_type=attrs.get("transformation_type"),
            source_datasets=source_datasets
        ))
        upstream_path.append(path)
        
        # Check if this is a source node (no predecessors or marked as source)
        if not upstream_nodes or node_type == "source" or kg.graph.in_degree(current_id) == 0:
            break
        
        # Follow the primary upstream path (first predecessor)
        current_id = upstream_nodes[0] if upstream_nodes else None
    
    # Primary source is the last node in the chain
    primary_source = upstream_path[-1] if upstream_path else None
    
    return TraceLineageResponse(
        node_path=request.node_path,
        path_length=len(lineage_chain),
        upstream_path=upstream_path,
        primary_source=primary_source,
        lineage_chain=lineage_chain
    )


@router.get("/node/{project_id}/{node_id}", response_model=NodeDetailsResponse)
async def get_node_details(project_id: str, node_id: str):
    """
    Get detailed metadata for a specific node.
    
    Returns comprehensive information including purpose statements, metrics,
    code snippets, and dependency information.
    """
    kg_path = CARTOGRAPHY_DIR / project_id / "knowledge_graph.json"
    if not kg_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    kg = KnowledgeGraph.load(kg_path)
    
    # Decode node_id (may be URL encoded)
    from urllib.parse import unquote
    node_id = unquote(node_id)
    
    if node_id not in kg.graph:
        raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
    
    attrs = kg.graph.nodes[node_id]
    node_type = attrs.get("node_type", "unknown")
    path = attrs.get("path") or attrs.get("name") or node_id
    
    # Extract label
    label = Path(path).name if "/" in path else path
    
    # Get dependencies
    imports = [kg.graph.nodes.get(n, {}).get("path", n) for n in kg.graph.successors(node_id)]
    imported_by = [kg.graph.nodes.get(n, {}).get("path", n) for n in kg.graph.predecessors(node_id)]
    
    # Extract public API if available
    public_api = []
    if "public_functions" in attrs:
        for func in attrs.get("public_functions", [])[:10]:  # Limit to 10
            if isinstance(func, dict):
                public_api.append({
                    "name": func.get("name", ""),
                    "signature": func.get("signature", ""),
                    "docstring": func.get("docstring", "")
                })
            elif isinstance(func, str):
                public_api.append({
                    "name": func,
                    "signature": f"def {func}(...)",
                    "docstring": ""
                })
    
    # Get source code preview
    source_code = None
    if "source_code" in attrs:
        source_code = str(attrs["source_code"])[:500]  # First 500 chars
    elif "content" in attrs:
        source_code = str(attrs["content"])[:500]
    
    return NodeDetailsResponse(
        id=node_id,
        path=path,
        node_type=node_type,
        label=label,
        domain_cluster=attrs.get("domain_cluster"),
        purpose_statement=attrs.get("purpose_statement"),
        git_velocity=attrs.get("change_velocity_30d") or attrs.get("git_velocity"),
        complexity_score=attrs.get("complexity_score"),
        public_api=public_api,
        sql_query=attrs.get("sql_query") or attrs.get("query"),
        storage_type=attrs.get("storage_type"),
        freshness_sla=attrs.get("freshness_sla"),
        source_code=source_code,
        dependencies={
            "imports": imports,
            "imported_by": imported_by
        }
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def _find_node_by_path(kg: KnowledgeGraph, path: str) -> Optional[str]:
    """
    Find a node ID by its path.
    
    Tries multiple strategies:
    1. Direct match on node_id
    2. Match on 'path' attribute
    3. Match on 'name' attribute
    4. Fuzzy match on path suffix
    """
    # Direct match
    if path in kg.graph:
        return path
    
    # Search by path attribute
    for node_id, attrs in kg.graph.nodes(data=True):
        node_path = attrs.get("path") or attrs.get("name")
        if node_path == path:
            return node_id
        
        # Fuzzy match - check if path ends with the search term
        if node_path and path in node_path:
            return node_id
    
    # Try with mod: prefix
    if not path.startswith("mod:"):
        prefixed = f"mod:{path}"
        if prefixed in kg.graph:
            return prefixed
    
    return None
