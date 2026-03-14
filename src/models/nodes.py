from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Any
from enum import Enum
from datetime import datetime

# --- Enums ---

class NodeType(str, Enum):
    module = "module"
    dataset = "dataset"
    function = "function"
    transformation = "transformation"

class EdgeType(str, Enum):
    IMPORTS = "IMPORTS"
    PRODUCES = "PRODUCES"
    CONSUMES = "CONSUMES"
    CALLS = "CALLS"
    CONFIGURES = "CONFIGURES"

class StorageType(str, Enum):
    TABLE = "table"
    FILE = "file"
    STREAM = "stream"
    API = "api"

# --- Nodes ---

class ModuleNode(BaseModel):
    path: str
    language: str = "unknown"
    purpose_statement: Optional[str] = None
    domain_cluster: Optional[str] = None
    complexity_score: float = 0.0
    change_velocity_30d: float = 0.0
    git_velocity_commit_count: int = 0
    git_velocity_last_commit_timestamp: str = ""
    git_velocity_time_window_days: int = 0
    git_velocity_history_status: str = "unknown"
    pagerank_score: float = 0.0
    is_dead_code_candidate: bool = False
    last_modified: datetime = Field(default_factory=datetime.now)

class DatasetNode(BaseModel):
    name: str
    storage_type: StorageType
    schema_snapshot: Optional[Dict] = None
    freshness_sla: Optional[str] = None
    owner: Optional[str] = None
    is_source_of_truth: bool = False
    source_file: Optional[str] = None
    lineage_range: Optional[tuple[int, int]] = None

class FunctionNode(BaseModel):
    qualified_name: str
    parent_module: str
    signature: str
    purpose_statement: Optional[str] = None
    call_count_within_repo: int = 0
    is_public_api: bool = True

class TransformationNode(BaseModel):
    source_datasets: List[str] = Field(default_factory=list)
    target_datasets: List[str] = Field(default_factory=list)
    transformation_type: str = "unknown"
    source_file: str = ""
    line_range: Optional[tuple[int, int]] = None
    lineage_range: Optional[tuple[int, int]] = None  # Explicit lineage focus
    sql_query_if_applicable: Optional[str] = None
    source_dataset_ref: Optional[str] = None  # Helper for direct identification
    target_dataset_ref: Optional[str] = None

# --- Edges ---

class GraphEdge(BaseModel):
    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ImportsEdge(GraphEdge):
    edge_type: EdgeType = EdgeType.IMPORTS

class ProducesEdge(GraphEdge):
    edge_type: EdgeType = EdgeType.PRODUCES

class ConsumesEdge(GraphEdge):
    edge_type: EdgeType = EdgeType.CONSUMES

class CallsEdge(GraphEdge):
    edge_type: EdgeType = EdgeType.CALLS

class ConfiguresEdge(GraphEdge):
    edge_type: EdgeType = EdgeType.CONFIGURES
