import os
from typing import List, Optional
import google.generativeai as genai
from src.providers.base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini implementation of the Universal LLM Provider.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "models/gemini-pro-latest"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set in environment.")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.embedding_model = "models/gemini-embedding-001"

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        # Note: Gemini 1.5+ supports system_instruction in initialization
        # For simplicity in this base wrapper, we prepend it to the prompt if provided
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"
            
        response = self.model.generate_content(full_prompt)
        return response.text

    def generate_embedding(self, text: str) -> List[float]:
        result = genai.embed_content(
            model=self.embedding_model,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def get_model_name(self) -> str:
        return self.model_name
