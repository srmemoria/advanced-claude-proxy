from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from loguru import logger
import json

from src.security.auth import verify_token
from src.proxy.guardian import ConstitutionalGuardian
from src.proxy.budget import budget_manager
from src.providers.registry import ProviderRegistry
from src.plugins.manager import plugin_manager
from src.memory.compressor import context_compressor

router = APIRouter(prefix="/v1", tags=["Proxy"])
registry = ProviderRegistry()

@router.post("/messages")
async def proxy_messages(request: Request, _ = Depends(verify_token)):
    """
    Main endpoint for proxying Claude messages to local $0 providers.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    logger.debug(f"Received message payload: {body.get('model', 'unknown')}")

    # Guardian Check
    messages = body.get("messages", [])
    if messages:
        last_msg = messages[-1].get("content", "")
        if isinstance(last_msg, str) and not ConstitutionalGuardian.check_prompt(last_msg):
             raise HTTPException(status_code=403, detail="Prompt blocked by Constitutional Guardian.")

    # Compress Context
    if "messages" in body:
        body["messages"] = context_compressor.compress_history(body["messages"])

    # Inject Local Plugins
    local_tools = plugin_manager.get_tool_schemas()
    if local_tools:
        if "tools" not in body:
            body["tools"] = []
        body["tools"].extend(local_tools)
        logger.debug(f"Injected {len(local_tools)} local plugins into payload.")

    # Routing to Provider
    auth_header = request.headers.get("Authorization", "")
    provider = registry.get_provider(auth_header)
    provider_name = provider.__class__.__name__.lower()
    
    # Cost & Budget Check
    if not budget_manager.check_budget():
        raise HTTPException(status_code=402, detail="Payment Required: Hard budget limit reached. Proxy blocked to protect your wallet.")

    # In a real streaming scenario, we'd count tokens post-stream.
    # For scaffolding, we estimate based on payload.
    est_input_tokens = len(json.dumps(body)) // 4
    budget_manager.record_usage(
        provider="local" if "ollama" in provider_name or "lmstudio" in provider_name else "openrouter",
        input_tokens=est_input_tokens, 
        output_tokens=0 # Tracked during stream in full implementation
    )
    
    # Stream back to Claude CLI
    return StreamingResponse(
        provider.stream_message(body), 
        media_type="text/event-stream"
    )

@router.post("/git-hook")
async def git_hook_review(request: Request, _ = Depends(verify_token)):
    """
    Endpoint designed to be called by a local git pre-commit hook.
    It receives the git diff, queries the LanceDB memory for context,
    and returns a review or blocks the commit if severe issues are found.
    """
    try:
        body = await request.json()
        diff = body.get("diff", "")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body. Must contain 'diff'.")

    logger.info("Analyzing git diff for security and context...")
    
    # Check if diff mentions passwords or AWS keys
    if "password=" in diff.lower() or "akia" in diff.lower():
         logger.warning("Git Hook blocked commit: Potential secret leaked in diff.")
         return {"status": "blocked", "reason": "Hardcoded secrets detected."}

    # Simulate RAG context search
    related_files = context_compressor.compress_history([{"role": "user", "content": diff}])
    
    return {
        "status": "approved", 
        "suggested_message": "feat: updated components with secure proxy integration",
        "context_files_analyzed": len(related_files)
    }
