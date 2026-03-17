import pytest
import asyncio
from fastapi.testclient import TestClient
from main import cli
from src.services.server_manager import ServerManager
from unittest.mock import patch, MagicMock

# We'll use a local TestClient for the FastAPI app
try:
    from main import ServerManager
    manager = ServerManager(port=5005)
    app = manager.app
except ImportError:
    # Fallback if structure is slightly different
    from src.services.server_manager import ServerManager
    manager = ServerManager(port=5005)
    app = manager.app

client = TestClient(app)

def test_discovery_archives():
    response = client.get("/api/discovery/archives")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_discovery_project_not_found():
    response = client.get("/api/discovery/summary/non_existent_project")
    assert response.status_code == 404

@patch("src.services.ingest_service.run_ingest_process")
def test_ingest_websocket_connection(mock_run):
    # Mock the long running process
    mock_run.return_value = None
    
    with client.websocket_connect("/api/ingest/ws/test-project") as websocket:
        websocket.send_json({"target": "src"})
        # The websocket might send progress or just wait. 
        # Since we mocked run_ingest_process, it should just accept and finish.
        pass

def test_heartbeat():
    # Simple check if there's a heartbeat or health endpoint if implemented
    pass
