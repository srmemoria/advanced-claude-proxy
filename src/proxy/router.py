from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger
from typing import Dict, Any

from src.security.auth import verify_token
from src.proxy.guardian import ConstitutionalGuardian

router = APIRouter(prefix="/v1", tags=["Proxy"])

@router.post("/messages")
async def proxy_messages(request: Request, _ = Depends(verify_token)):
    """
    Main endpoint for proxying Claude messages.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    logger.debug(f"Received message payload: {body.get('model', 'unknown')}")

    # Example: Check the last user message with Guardian
    messages = body.get("messages", [])
    if messages:
        last_msg = messages[-1].get("content", "")
        if isinstance(last_msg, str) and not ConstitutionalGuardian.check_prompt(last_msg):
             raise HTTPException(status_code=403, detail="Prompt blocked by Constitutional Guardian.")

    # In a full implementation, this would route to ProviderManager.
    # For scaffolding, we return a mock response.
    return {
        "id": "msg_mock",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "This is a mock response from Advanced Claude Proxy."
            }
        ],
        "model": body.get("model", "unknown-model"),
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 10
        }
    }
