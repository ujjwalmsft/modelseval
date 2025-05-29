"""
Completion Endpoint
 
Provides endpoints for direct model completions (single model, playground-style).
Useful for debugging, previews, or manual evaluation outside of compare flow.
 
Features:
- Supports optional system prompt
- Streams output (if supported)
- Logs to memory (CosmosDB thread)
"""
 
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
 
from services.semantic_kernel_service import SemanticKernelService
from services.cosmos_service import CosmosService
from semantic_kernel.functions.kernel_arguments import KernelArguments
 
logger = logging.getLogger(__name__)
router = APIRouter()
 
# Request and response schemas
 
class CompletionRequest(BaseModel):
    model_id: str
    prompt: str
    system_prompt: Optional[str] = "You are a helpful assistant."
    conversation_id: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1500
 
class CompletionResponse(BaseModel):
    content: str
    model_id: str
    metrics: Optional[dict]
    safety: Optional[dict] = None
 
@router.post("/completion", response_model=CompletionResponse)
async def generate_completion(request: CompletionRequest):
    """
    Generate a single model completion via CompletionPlugin.
    """
    logger.info(f"[CompletionAPI] Generating response for model: {request.model_id}")
 
    if not request.prompt or not request.model_id:
        raise HTTPException(status_code=400, detail="Prompt and model_id are required.")
 
    kernel = SemanticKernelService.get_instance().kernel
    cosmos = CosmosService.get_instance()
 
    args = KernelArguments({
        "prompt": request.prompt,
        "model_id": request.model_id,
        "deployment": request.model_id,
        "system_prompt": request.system_prompt or "You are a helpful assistant.",
        "temperature": str(request.temperature),
        "max_tokens": str(request.max_tokens),
        "conversation_id": request.conversation_id or f"{request.model_id}-{request.prompt[:10]}"
    })
 
    try:
        result = await kernel.invoke_async(
            plugin_name="CompletionPlugin",
            function_name="run_completion",
            arguments=args
        )
 
        parsed = result.json() if hasattr(result, 'json') else result
        content = parsed.get("content", "")
        metrics = parsed.get("metrics", {})
        safety = parsed.get("safety", {})
 
        # Save to memory (if conversation ID provided)
        if request.conversation_id:
            await cosmos.save_conversation_message(
                model_id=request.model_id,
                thread_id=request.conversation_id,
                role="assistant",
                content=content,
                token_count=metrics.get("totalTokens", 0)
            )
 
        return CompletionResponse(
            content=content,
            model_id=request.model_id,
            metrics=metrics,
            safety=safety
        )
 
    except Exception as e:
        logger.error(f"[CompletionAPI] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model failed to respond: {str(e)}")