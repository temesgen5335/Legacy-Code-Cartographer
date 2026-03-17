import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.orchestrator import CartographyOrchestrator
from src.graph.knowledge_graph import KnowledgeGraph

@pytest.fixture
def mock_repo(tmp_path):
    repo = tmp_path / "test_repo"
    repo.mkdir()
    (repo / "core.py").write_text("def run(): pass")
    (repo / "data.sql").write_text("SELECT * FROM users")
    return repo

@patch("google.genai.Client")
def test_orchestration_full_run(mock_genai, mock_repo, tmp_path):
    # Mock LLM
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "Mocked purpose."
    
    # Run orchestrator
    # We use a custom out_dir for the test to avoid polluting the actual project
    test_out_dir = tmp_path / ".cartography_test"
    orchestrator = CartographyOrchestrator(
        repo_path=mock_repo,
        out_dir=test_out_dir,
        repo_input=str(mock_repo)
    )
    
    results = orchestrator.analyze(incremental=False)
    
    # Verify artifacts exist in the specified output directory
    assert Path(results["knowledge_graph"]).exists()
    assert Path(results["codebase_md"]).exists()
    assert Path(results["onboarding_brief"]).exists()
    assert Path(results["trace"]).exists()
    
    # Verify content of knowledge graph
    kg = KnowledgeGraph.load(results["knowledge_graph"])
    assert len(kg.graph.nodes) > 0
    
    # Clean up
    import shutil
    if test_out_dir.exists():
        shutil.rmtree(test_out_dir)


@patch("google.genai.Client")
def test_orchestration_url_input_path(mock_genai, mock_repo, tmp_path):
    """
    Regression test: Exercises the URL code path in CartographyOrchestrator.__init__.
    Previously, urlparse was missing from imports and this branch silently failed
    when repo_input was a GitHub URL. Passing a URL here ensures the import is
    present and project_name derivation from URLs works correctly.
    """
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "Mocked."

    test_out_dir = tmp_path / ".cartography_url_test"

    # Simulate what the ingest service does: pass a GitHub URL as repo_input
    fake_url = "https://github.com/testorg/test-repo.git"
    orchestrator = CartographyOrchestrator(
        repo_path=mock_repo,
        out_dir=test_out_dir,
        repo_input=fake_url
    )

    # The project name should be derived from the URL, not the local path
    assert orchestrator.out_dir == test_out_dir  # explicit out_dir wins
    # but the key thing is it constructed without NameError

    import shutil
    if test_out_dir.exists():
        shutil.rmtree(test_out_dir)


@patch("google.genai.Client")
def test_orchestration_url_auto_outdir(mock_genai, mock_repo):
    """
    Exercises auto-derived out_dir from a GitHub URL (no explicit out_dir).
    Verifies urlparse correctly extracts project_name = 'testorg_test-repo'
    and constructs .cartography/<project_name>.
    """
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "Mocked."

    fake_url = "https://github.com/testorg/test-repo.git"
    orchestrator = CartographyOrchestrator(
        repo_path=mock_repo,
        repo_input=fake_url
    )

    # project name from URL path: testorg/test-repo.git -> testorg_test-repo
    expected_project = "testorg_test-repo"
    assert orchestrator.out_dir.name == expected_project
    assert ".cartography" in str(orchestrator.out_dir)

    import shutil
    if orchestrator.out_dir.exists():
        shutil.rmtree(orchestrator.out_dir)
