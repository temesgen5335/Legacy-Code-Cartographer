import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.agents.surveyor import SurveyorAgent
from src.agents.hydrologist import HydrologistAgent
from src.agents.semanticist import SemanticistAgent
from src.graph.knowledge_graph import KnowledgeGraph
from src.models.nodes import ModuleNode

@pytest.fixture
def mock_repo(tmp_path):
    repo = tmp_path / "mock_repo"
    repo.mkdir()
    (repo / "main.py").write_text("import os\ndef test(): pass")
    (repo / "utils.py").write_text("def helper(): pass")
    return repo

def test_surveyor_agent_run(mock_repo):
    kg = KnowledgeGraph()
    agent = SurveyorAgent(kg=kg)
    kg, modules, trace = agent.run(mock_repo)
    
    assert len(modules) == 2
    assert "main.py" in modules
    assert "utils.py" in modules
    assert any(n for n, d in kg.graph.nodes(data=True) if d.get("node_type") == "module")

def test_hydrologist_agent_run(mock_repo):
    kg = KnowledgeGraph()
    agent = HydrologistAgent(lineage_graph=kg)
    kg, trace = agent.run(mock_repo, lineage_graph=kg)
    
    # Simple check for completion trace
    assert any(t.action == "analysis_complete" for t in trace)

@patch("google.genai.Client")
def test_semanticist_agent_run(mock_genai, mock_repo):
    # Mock LLM response
    mock_client = MagicMock()
    mock_genai.return_value = mock_client
    mock_client.models.generate_content.return_value.text = "This is a mock purpose statement."
    
    kg = KnowledgeGraph()
    agent = SemanticistAgent(kg=kg, api_key="fake_key")
    
    modules = {
        "main.py": ModuleNode(path="main.py", name="main")
    }
    
    enriched_modules, trace = agent.run(mock_repo, modules)
    
    assert enriched_modules["main.py"].purpose_statement == "This is a mock purpose statement."
    assert any(t.action == "semantic_enrichment_complete" for t in trace)
