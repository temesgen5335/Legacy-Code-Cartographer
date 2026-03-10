import os
from src.providers.base import BaseLLMProvider
from src.providers.gemini_provider import GeminiProvider

class LLMProviderFactory:
    """
    Factory to create the appropriate LLM provider based on configuration.
    """
    
    @staticmethod
    def get_provider(provider_type: str = "gemini", **kwargs) -> BaseLLMProvider:
        """
        Returns a provider instance. Defaulting to Gemini.
        """
        provider_type = provider_type.lower()
        
        if provider_type == "gemini":
            return GeminiProvider(**kwargs)
        # Placeholder for other providers
        # elif provider_type == "openai":
        #     return OpenAIProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

# Singleton-like access for global configuration
_default_provider = None

def get_default_provider() -> BaseLLMProvider:
    global _default_provider
    if _default_provider is None:
        # Initializing default from environment or hardcoded default
        _default_provider = LLMProviderFactory.get_provider(
            os.getenv("LLM_PROVIDER", "gemini")
        )
    return _default_provider
