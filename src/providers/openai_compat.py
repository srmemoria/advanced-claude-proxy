import httpx
import json
from typing import Any, Dict, AsyncGenerator
from loguru import logger
from src.providers.base import BaseProvider

class OpenAICompatProvider(BaseProvider):
    """Translates Anthropic Messages API to OpenAI Chat API (used by LM Studio, Ollama, etc)."""

    def _translate_payload(self, anthropic_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Converts Anthropic payload to OpenAI payload."""
        messages = []
        
        # System prompt translation
        if "system" in anthropic_payload:
            system_content = anthropic_payload["system"]
            if isinstance(system_content, list):
                system_content = "\n".join([m.get("text", "") for m in system_content])
            messages.append({"role": "system", "content": system_content})

        # User/Assistant messages
        for msg in anthropic_payload.get("messages", []):
            content = msg.get("content", "")
            # Simple text translation for now. Multimodal needs more logic.
            if isinstance(content, list):
                text_content = " ".join([c.get("text", "") for c in content if c.get("type") == "text"])
                messages.append({"role": msg["role"], "content": text_content})
            else:
                messages.append({"role": msg["role"], "content": content})

        openai_payload = {
            "model": anthropic_payload.get("model", "default-model"),
            "messages": messages,
            "stream": True,
            "temperature": anthropic_payload.get("temperature", 0.7),
            "max_tokens": anthropic_payload.get("max_tokens", 4096)
        }
        return openai_payload

    async def stream_message(self, payload: Dict[str, Any]) -> AsyncGenerator[bytes, None]:
        openai_payload = self._translate_payload(payload)
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        logger.info(f"Routing to OpenAI Compat: {self.base_url} with model {openai_payload['model']}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST", 
                f"{self.base_url}/chat/completions",
                json=openai_payload,
                headers=headers
            ) as response:
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"Provider Error: {error_text}")
                    yield b'event: error\ndata: {"error": {"type": "api_error", "message": "Backend error"}}\n\n'
                    return

                # Send initial Anthropic event
                yield b'event: message_start\ndata: {"type": "message_start", "message": {"id": "msg_0", "type": "message", "role": "assistant", "model": "model", "content": [], "stop_reason": null, "stop_sequence": null, "usage": {"input_tokens": 0, "output_tokens": 0}}}\n\n'
                yield b'event: content_block_start\ndata: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}\n\n'

                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    # Translate to Anthropic content_block_delta
                                    anthropic_delta = {
                                        "type": "content_block_delta",
                                        "index": 0,
                                        "delta": {"type": "text_delta", "text": content}
                                    }
                                    yield f'event: content_block_delta\ndata: {json.dumps(anthropic_delta)}\n\n'.encode('utf-8')
                        except json.JSONDecodeError:
                            continue

                # Close the message
                yield b'event: content_block_stop\ndata: {"type": "content_block_stop", "index": 0}\n\n'
                yield b'event: message_stop\ndata: {"type": "message_stop"}\n\n'
