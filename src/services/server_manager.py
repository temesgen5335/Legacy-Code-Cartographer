import uvicorn
import webbrowser
import threading
import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

class ServerManager:
    """
    Manages the FastAPI server lifecycle and GUI integration.
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        self.host = host
        self.port = port
        self.app = FastAPI(title="The Brownfield Cartographer API")
        
        # We will mount static files if the frontend build exists
        self._setup_static_files()
        self._setup_routes()

    def _setup_static_files(self):
        # Path to pre-built frontend
        dist_path = Path("frontend/dist")
        if dist_path.exists():
            self.app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="static")
            print(f"Mounted GUI from {dist_path}")
        else:
            print("Warning: frontend/dist not found. GUI static files will not be served.")

    def _setup_routes(self):
        @self.app.get("/api/health")
        async def health():
            return {"status": "ok", "version": "0.1.0"}
            
        # Placeholder for Archivist, Discovery, and Chat services
        # from backend.src.services.archivist import router as archivist_router
        # self.app.include_router(archivist_router)

    def start_gui(self):
        """Starts the server and opens the browser."""
        def open_browser():
            # Wait a bit for the server to start
            time.sleep(1.5)
            url = f"http://{self.host}:{self.port}"
            print(f"Opening GUI at {url}")
            webbrowser.open(url)

        # Start browser in a separate thread
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)

if __name__ == "__main__":
    # Test stub
    manager = ServerManager()
    manager.start_gui()
