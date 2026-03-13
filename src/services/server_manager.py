import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.services.discovery_service import router as discovery_router
from src.services.chat_service import router as chat_router
from src.services.ingest_service import router as ingest_router

class ServerManager:
    """
    Manages the FastAPI server lifecycle and GUI integration.
    """
    
    def __init__(self, port: int = 5000):
        self.port = port
        self.app = FastAPI(title="The Brownfield Cartographer")
        
        # Priority 1: API Routes
        self._setup_routes()
        
        # Priority 2: Static Files & SPA Routing
        self._setup_static_files()

    def _setup_static_files(self):
        """Mounts the frontend build as static files and handles SPA routing."""
        build_dir = Path("frontend/dist")
        if build_dir.exists():
            print(f"Mounted GUI from {build_dir}")
            # Mount assets specifically
            self.app.mount("/assets", StaticFiles(directory=build_dir / "assets"), name="assets")
            
            # Mount other root files like vite.svg
            for item in build_dir.iterdir():
                if item.is_file() and item.name != "index.html":
                    self.app.mount(f"/{item.name}", StaticFiles(directory=build_dir), name=f"root_{item.name}")

            @self.app.get("/{full_path:path}")
            async def serve_spa(full_path: str):
                # This catch-all serves index.html for any path not matched by previous routers
                index_path = build_dir / "index.html"
                if index_path.exists():
                    from fastapi.responses import FileResponse
                    return FileResponse(index_path)
                return {"error": "Frontend build not found"}
        else:
            print(f"Warning: frontend/dist not found at {build_dir}. Please run 'npm run build'.")

    def _setup_routes(self):
        """Registers the API routers."""
        self.app.include_router(discovery_router, prefix="/api")
        self.app.include_router(chat_router, prefix="/api")
        self.app.include_router(ingest_router, prefix="/api")

    def start_gui(self):
        """Starts the server and opens the browser."""
        print(f"Starting GUI at http://127.0.0.1:{self.port}")
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)

if __name__ == "__main__":
    manager = ServerManager(port=5001)
    manager.start_gui()
