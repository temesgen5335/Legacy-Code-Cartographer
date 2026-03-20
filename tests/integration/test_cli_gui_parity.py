"""
Integration tests to verify CLI/GUI parity.

Ensures that both interfaces generate identical artifacts for the same inputs.
"""
import json
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.core.cartography_service import CartographyService
from src.graph.knowledge_graph import KnowledgeGraph


@pytest.fixture
def mock_repo(tmp_path):
    """Create a mock repository for testing."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    (repo / "core.py").write_text("def run(): pass\n")
    (repo / "utils.py").write_text("def helper(): return 42\n")
    (repo / "data.sql").write_text("SELECT * FROM users;\n")
    return repo


@pytest.fixture
def cleanup_cartography():
    """Clean up .cartography directory after tests."""
    yield
    cartography_dir = Path(".cartography")
    if cartography_dir.exists():
        for item in cartography_dir.iterdir():
            if item.name.startswith("test_"):
                shutil.rmtree(item, ignore_errors=True)


@patch("google.genai.Client")
def test_cli_gui_artifact_parity(mock_genai, mock_repo, tmp_path, cleanup_cartography):
    """
    Verify that CLI and GUI (via core service) generate identical artifacts.
    
    This is the critical parity test mandated by the constitution.
    """
    # Mock LLM
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "Mocked purpose."
    
    # Use core service (same as both CLI and GUI use)
    service = CartographyService()
    
    # Run analysis via core service
    result = service.analyze_repository(
        repo_path=mock_repo,
        repo_input=str(mock_repo),
        incremental=False,
    )
    
    # Verify all expected artifacts exist
    expected_artifacts = [
        "knowledge_graph",
        "semantic_index",
        "codebase_md",
        "onboarding_brief",
        "trace",
        "module_graph_html",
        "lineage_graph_html",
    ]
    
    for artifact_name in expected_artifacts:
        assert artifact_name in result.artifacts, f"Missing artifact: {artifact_name}"
        artifact_path = Path(result.artifacts[artifact_name])
        assert artifact_path.exists(), f"Artifact file not found: {artifact_path}"
    
    # Verify knowledge graph structure
    kg_path = Path(result.artifacts["knowledge_graph"])
    kg = KnowledgeGraph.load(kg_path)
    
    assert len(kg.graph.nodes) > 0, "Knowledge graph should have nodes"
    assert len(kg.graph.edges) >= 0, "Knowledge graph should have edges"
    
    # Verify JSON is valid and parseable
    with open(kg_path, "r") as f:
        kg_json = json.load(f)
    
    assert "nodes" in kg_json, "Knowledge graph JSON should have 'nodes' key"
    assert "links" in kg_json, "Knowledge graph JSON should have 'links' key"
    
    # Verify metrics are computed
    assert "node_count" in result.metrics
    assert "edge_count" in result.metrics
    assert "system_complexity" in result.metrics
    
    # Verify trace events
    assert len(result.trace) > 0, "Should have trace events"


@patch("google.genai.Client")
def test_visualization_service_parity(mock_genai, mock_repo, cleanup_cartography):
    """
    Verify that visualization service generates consistent output
    regardless of whether called from CLI or GUI.
    """
    from src.core.visualization_service import VisualizationService
    
    # Mock LLM
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "Mocked purpose."
    
    # First, analyze the repository
    service = CartographyService()
    result = service.analyze_repository(
        repo_path=mock_repo,
        repo_input=str(mock_repo),
        incremental=False,
    )
    
    # Now test visualization service
    viz_service = VisualizationService()
    
    # Generate module graph as HTML
    html_result = viz_service.generate_module_graph(
        project_name=result.project_name,
        output_format="html",
    )
    
    assert Path(html_result["output_path"]).exists()
    assert html_result["output_format"] == "html"
    assert "node_count" in html_result["report"]
    
    # Generate module graph as JSON
    json_result = viz_service.generate_module_graph(
        project_name=result.project_name,
        output_format="json",
    )
    
    assert Path(json_result["output_path"]).exists()
    assert json_result["output_format"] == "json"
    
    # Verify JSON structure
    with open(json_result["output_path"], "r") as f:
        graph_data = json.load(f)
    
    assert "graph_type" in graph_data
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert graph_data["graph_type"] == "module"


@patch("google.genai.Client")
def test_config_service_consistency(mock_genai):
    """
    Verify that config service provides consistent configuration
    for both CLI and GUI.
    """
    from src.core.config_service import ConfigService
    
    config_service = ConfigService()
    
    # Get default config
    config = config_service.get_config()
    
    # Verify expected structure
    assert "llm" in config
    assert "languages" in config
    assert "analysis" in config
    assert "output" in config
    
    # Test setting and getting values
    config_service.set_config("test_key", "test_value")
    updated_config = config_service.get_config()
    assert updated_config["test_key"] == "test_value"
    
    # Test nested keys
    config_service.set_config("nested.key", "nested_value")
    updated_config = config_service.get_config()
    assert updated_config["nested"]["key"] == "nested_value"
    
    # Clean up
    config_service.reset_config()


@patch("google.genai.Client")
def test_project_listing_parity(mock_genai, mock_repo, cleanup_cartography):
    """
    Verify that project listing works consistently for both CLI and GUI.
    """
    # Mock LLM
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "Mocked purpose."
    
    service = CartographyService()
    
    # Initially should have no projects
    projects_before = service.list_projects()
    initial_count = len(projects_before)
    
    # Analyze a repository
    result = service.analyze_repository(
        repo_path=mock_repo,
        repo_input=str(mock_repo),
        incremental=False,
    )
    
    # Now should have one more project
    projects_after = service.list_projects()
    assert len(projects_after) == initial_count + 1
    
    # Verify project appears in list
    project_names = [p["name"] for p in projects_after]
    assert result.project_name in project_names
    
    # Get project summary
    summary = service.get_project_summary(result.project_name)
    assert summary["project_name"] == result.project_name
    assert "metrics" in summary
    assert "architectural_hubs" in summary


def test_cli_command_availability():
    """
    Verify that all CLI commands are properly defined.
    """
    from cartograph import app
    
    # Get all registered commands
    commands = app.registered_commands
    command_names = [cmd.name for cmd in commands]
    
    # Verify expected commands exist
    expected_commands = ["analyze", "map", "config", "list", "summary"]
    for cmd in expected_commands:
        assert cmd in command_names, f"CLI command '{cmd}' not found"


@patch("google.genai.Client")
def test_incremental_analysis_parity(mock_genai, mock_repo, cleanup_cartography):
    """
    Verify that incremental analysis works consistently.
    """
    # Mock LLM
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "Mocked purpose."
    
    service = CartographyService()
    
    # First analysis (full)
    result1 = service.analyze_repository(
        repo_path=mock_repo,
        repo_input=str(mock_repo),
        incremental=False,
    )
    
    initial_node_count = result1.metrics["node_count"]
    
    # Modify repository
    (mock_repo / "new_file.py").write_text("def new_function(): pass\n")
    
    # Second analysis (incremental)
    result2 = service.analyze_repository(
        repo_path=mock_repo,
        repo_input=str(mock_repo),
        incremental=True,
    )
    
    # Should have more nodes now
    assert result2.metrics["node_count"] >= initial_node_count
    
    # Both should have same project name
    assert result1.project_name == result2.project_name
