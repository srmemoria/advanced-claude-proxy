from typing import Any, Dict
from loguru import logger
from src.providers.base import BaseProvider
from src.providers.local_llms import LMStudioProvider, OllamaProvider
from src.providers.openai_compat import OpenAICompatProvider

class ProviderRegistry:
    """Routes requests to the correct provider based on the model or proxy header."""
    
    def __init__(self):
        self.providers = {
            "lmstudio": LMStudioProvider(),
            "ollama": OllamaProvider(),
        }

    def get_provider(self, auth_header: str) -> BaseProvider:
        """
        Determines the provider from the auth header.
        In free-claude-code, the token is passed like `freecc:provider/model`
        """
        if not auth_header:
            return self.providers["lmstudio"] # Default fallback to $0 local
            
        parts = auth_header.replace("Bearer ", "").split(":")
        
        provider_name = "lmstudio" # Default
        
        if len(parts) >= 2:
            model_string = parts[1]
            if model_string.startswith("ollama/"):
                provider_name = "ollama"
            elif model_string.startswith("lmstudio/"):
                provider_name = "lmstudio"
            elif model_string.startswith("openrouter/"):
                provider_name = "openrouter"
                
        logger.info(f"Registry routing request to: {provider_name}")
        return self.providers.get(provider_name, self.providers["lmstudio"])
