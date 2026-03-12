from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union

class RiskCard(BaseModel):
    """Represents a specific architectural or design risk."""
    title: str
    severity: str  # "high", "medium", "low"
    description: str
    impact_nodes: List[str]
    remediation: Optional[str] = None

class HubTableEntry(BaseModel):
    """Data for the 'Architectural Hubs' table."""
    node_id: str
    path: str
    pagerank_score: float
    fan_out: int
    fan_in: int
    purpose: Optional[str] = None

class CodebaseHealthScore(BaseModel):
    """Overall health metrics for the codebase."""
    maintainability: float = Field(..., ge=0, le=100)
    blast_radius_avg: float
    circular_dependencies_count: int
    test_coverage_estimate: Optional[float] = None

class DeepWikiReport(BaseModel):
    """The full report schema for a codebase assessment."""
    project_name: str
    summary: str
    health_score: CodebaseHealthScore
    risk_cards: List[RiskCard]
    architectural_hubs: List[HubTableEntry]
    data_lineage_summary: str
    last_updated: str

class NodeVirtualized(BaseModel):
    """Compact node representation for virtualized UI lists."""
    id: str
    label: str
    node_type: str
    change_velocity: float
    pagerank_rank: int
    is_dead_end: bool

class Archive(BaseModel):
    """Represents an archived codebase in the landing page."""
    name: str
    description: str
    sector: str
    artifact_count: int
    last_updated: str
