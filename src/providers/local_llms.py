from src.providers.openai_compat import OpenAICompatProvider

class LMStudioProvider(OpenAICompatProvider):
    """Specialized provider for LM Studio running locally."""
    def __init__(self, base_url: str = "http://localhost:1234/v1", api_key: str = "lmstudio"):
        super().__init__(base_url=base_url, api_key=api_key)

class OllamaProvider(OpenAICompatProvider):
    """Specialized provider for Ollama running locally."""
    def __init__(self, base_url: str = "http://localhost:11434/v1", api_key: str = "ollama"):
        super().__init__(base_url=base_url, api_key=api_key)
