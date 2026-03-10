from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers (Gemini, OpenAI, etc.)
    """
    
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generates a text completion based on the prompt."""
        pass
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generates a vector embedding for the given text."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Returns the name of the active model."""
        pass
