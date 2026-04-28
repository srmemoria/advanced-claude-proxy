from loguru import logger
import json

class ContextCompressor:
    """Uses a local, fast model to compress chat history if it gets too long, saving tokens."""

    def __init__(self, token_limit: int = 15000):
        self.token_limit = token_limit

    def compress_history(self, messages: list[dict]) -> list[dict]:
        """
        Takes a list of Anthropic messages. If they exceed the limit (estimated),
        it attempts to compress older messages into a summary.
        """
        if len(messages) <= 4:
            return messages # Too short to compress
            
        # Very rough estimation of tokens
        est_tokens = sum(len(json.dumps(msg)) // 4 for msg in messages)
        
        if est_tokens < self.token_limit:
            return messages
            
        logger.info(f"Context size ({est_tokens} tokens) exceeds limit. Compressing history...")
        
        # In a real implementation, this would make an API call to Ollama (Llama 3 8B)
        # to generate a dense summary of messages[0:-3].
        
        # For scaffolding, we will simulate the compression by dropping older messages
        # and inserting a "System Summary" mock.
        
        summary_msg = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "[SYSTEM NOTE: Previous conversation has been compressed to save tokens.]\nSummary: The user is building an advanced proxy. They have implemented a Budget Manager, Plugins, and a Router."
                }
            ]
        }
        
        # Keep the summary and the last 3 messages
        compressed_messages = [summary_msg] + messages[-3:]
        
        logger.info(f"History compressed from {len(messages)} to {len(compressed_messages)} messages.")
        return compressed_messages

context_compressor = ContextCompressor()
