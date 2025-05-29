"""
CompletionPlugin: stream_completion_function
 
Streams LLM responses chunk by chunk using OpenAI or Azure OpenAI clients.
Tracks partial output and usage metrics for real-time display.
"""
 
import json
import logging
import time
from typing import Optional, AsyncGenerator, Dict, Any
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from config import settings
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="stream_completion",
    description="Stream a completion from a supported LLM model"
)
async def stream_completion(arguments: KernelArguments) -> str:
    """
    Initiates a streaming response (stream generator is returned separately).
 
    Returns:
        JSON with generator ID (used in /stream/{generator_id})
    """
    try:
        # Extract parameters
        model_id = arguments["model_id"]
        prompt = arguments["prompt"]
        deployment = arguments.get("deployment", model_id)
        system_prompt = arguments.get("system_prompt", "You are a helpful assistant.")
        temperature = float(arguments.get("temperature", "0.7"))
        max_tokens = int(arguments.get("max_tokens", "2000"))
 
        from uuid import uuid4
        generator_id = f"stream-{uuid4().hex}"
 
        # Save stream request for later retrieval
        from services.stream_register import register_stream_request
        await register_stream_request(
            generator_id=generator_id,
            model_id=model_id,
            deployment=deployment,
            provider="Azure OpenAI",
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
 
        return json.dumps({
            "generator_id": generator_id,
            "status": "ready"
        })
 
    except Exception as e:
        logger.error(f"[StreamCompletion] Setup failed: {str(e)}")
        return json.dumps({
            "error": str(e),
            "status": "error"
        })