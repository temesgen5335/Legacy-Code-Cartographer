import os
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class SemanticIndex:
    """
    Handles semantic search for codebase knowledge.
    Uses Qdrant for vector storage and Gemini for embeddings.
    """
    
    def __init__(self, collection_name: str = "module_purposes"):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.qdrant_url = os.environ.get("QDRANT_CLUSTER_ENDPOINT")
        self.qdrant_key = os.environ.get("QDRANT_API_KEY")
        
        self.collection_name = collection_name
        
        if self.gemini_key:
            self.genai_client = genai.Client(api_key=self.gemini_key)
        else:
            self.genai_client = None
            
        if self.qdrant_url and self.qdrant_key:
            self.qdrant_client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_key,
            )
            self._ensure_collection()
        else:
            self.qdrant_client = None

    def _ensure_collection(self):
        """Creates the collection if it doesn't exist."""
        collections = self.qdrant_client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        target_size = 3072 # Gemini gemini-embedding-001 size
        
        if exists:
            # Check existing dimension
            info = self.qdrant_client.get_collection(self.collection_name)
            # Accessing size from vectors_config.params
            current_size = info.config.params.vectors.size
            if current_size != target_size:
                print(f"Collection {self.collection_name} dimension mismatch ({current_size} != {target_size}). Recreating...")
                self.qdrant_client.delete_collection(self.collection_name)
                exists = False

        if not exists:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=target_size,
                    distance=models.Distance.COSINE,
                ),
            )

    def _get_embedding(self, text: str) -> List[float]:
        """Generates embedding for the given text."""
        if not self.genai_client:
            return []
        
        try:
            result = self.genai_client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def index_module(self, path: str, purpose: str):
        """Indexes a module's purpose statement."""
        if not self.qdrant_client or not purpose:
            return
        
        embedding = self._get_embedding(purpose)
        if not embedding:
            return
        
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=hash(path) & 0xFFFFFFFFFFFFFFFF, # Simple hash for ID
                    vector=embedding,
                    payload={"path": path, "purpose": purpose}
                )
            ]
        )

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Searches for modules related to the query."""
        if not self.qdrant_client:
            return []
        
        query_vector = self._get_embedding(query)
        if not query_vector:
            return []
        
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [res.payload for res in results]

if __name__ == "__main__":
    idx = SemanticIndex(collection_name="test_collection")
    if idx.qdrant_client:
        print("Qdrant connected and index ready.")
        idx.index_module("test.py", "This module handles user authentication and session management.")
        results = idx.search("How do I log in?")
        print(f"Search results: {results}")
    else:
        print("Qdrant not configured.")
