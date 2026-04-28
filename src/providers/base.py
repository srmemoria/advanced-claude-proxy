from typing import Any, Dict, List, AsyncGenerator, Optional
from loguru import logger

class BaseProvider:
    """Base class for all API providers."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key

    async def stream_message(self, payload: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        """Streams a message from the provider and yields Anthropic-compatible SSE events."""
        raise NotImplementedError
