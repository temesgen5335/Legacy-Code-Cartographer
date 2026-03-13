from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class StorageType(str, Enum):
    TABLE = "table"
    FILE = "file"
    STREAM = "stream"
    API = "api"

class ModuleNode(BaseModel):
    path: str
    language: str = "unknown"
    purpose_statement: Optional[str] = None
    domain_cluster: Optional[str] = None
    complexity_score: float = 0.0
    change_velocity_30d: float = 0.0
    is_dead_code_candidate: bool = False
    last_modified: datetime = Field(default_factory=datetime.now)

class DatasetNode(BaseModel):
    name: str
    storage_type: StorageType
    schema_snapshot: Optional[Dict] = None
    freshness_sla: Optional[str] = None
    owner: Optional[str] = None
    is_source_of_truth: bool = False

class FunctionNode(BaseModel):
    qualified_name: str
    parent_module: str
    signature: str
    purpose_statement: Optional[str] = None
    call_count_within_repo: int = 0
    is_public_api: bool = True

class TransformationNode(BaseModel):
    source_datasets: List[str]
    target_datasets: List[str]
    transformation_type: str
    source_file: str
    line_range: tuple[int, int]
    sql_query_if_applicable: Optional[str] = None
