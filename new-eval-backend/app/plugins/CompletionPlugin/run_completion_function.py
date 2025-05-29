"""
CompletionPlugin: run_completion_function
 
Purpose:
- Explicitly generates a non-streaming LLM completion from a specified provider.
- Logs prompts and responses explicitly to Cosmos DB memory (thread storage).
- Returns completion content, associated metrics, and optional content safety check results.
 
Updates:
- Explicitly sanitizes conversation IDs to remove illegal characters for Cosmos DB storage.
- Robust logging and detailed inline debug statements for tracing execution.
"""
 
import json
import logging
import time
import re
from typing import Dict, Any
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions import kernel_function
from services.semantic_kernel_service import SemanticKernelService
from services.cosmos_service import CosmosService
from services.content_safety_service import ContentSafetyService
from config import settings
 
logger = logging.getLogger(__name__)
 
def sanitize_id(raw_id: str) -> str:
    """
    Explicitly sanitizes IDs for Cosmos DB compatibility by removing illegal characters.
 
    Args:
        raw_id (str): Original ID string.
 
    Returns:
        str: Sanitized ID suitable for Cosmos DB.
    """
    return re.sub(r'[^a-zA-Z0-9-_]', '_', raw_id)
 
@kernel_function(
    name="run_completion",
    description="Generate a completion from a specified model and log to memory explicitly."
)
async def run_completion(arguments: KernelArguments) -> str:
    start = time.time()
    try:
        model_id = arguments["model_id"]
        prompt = arguments["prompt"]
        deployment = arguments.get("deployment", model_id)
        system_prompt = arguments.get("system_prompt", "You are a helpful assistant.")
        conversation_id_raw = arguments.get("conversation_id", f"{model_id}-{prompt[:20]}")
        conversation_id = sanitize_id(conversation_id_raw)
        temperature = float(arguments.get("temperature", 0.7))
        max_tokens = int(arguments.get("max_tokens", 2000))
 
        kernel = SemanticKernelService.get_instance().kernel
        cosmos = CosmosService.get_instance()
 
        # Use Azure OpenAI SDK explicitly for chat completion
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
 
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
 
        response =  client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
 
        content = response.choices[0].message.content
        usage = response.usage
        latency = time.time() - start
 
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
 
        # Save prompt explicitly to memory
        await cosmos.save_conversation_message(
            model_id=model_id,
            thread_id=conversation_id,
            role="user",
            content=prompt,
            token_count=prompt_tokens
        )
 
        # Save response explicitly to memory
        await cosmos.save_conversation_message(
            model_id=model_id,
            thread_id=conversation_id,
            role="assistant",
            content=content,
            token_count=completion_tokens
        )
 
        # Optional content safety check explicitly executed
        safety_result = {}
        if settings.AZURE_CONTENT_SAFETY_KEY:
            safety_result = await ContentSafetyService().analyze_text(content)
            logger.debug(f"[CompletionPlugin] Content safety analysis result: {safety_result}")
 
        result_payload = {
            "content": content,
            "model": model_id,
            "metrics": {
                "responseTime": latency,
                "promptTokens": prompt_tokens,
                "completionTokens": completion_tokens,
                "totalTokens": total_tokens
            },
            "safety": safety_result,
            "id": conversation_id
        }
 
        logger.debug(f"[CompletionPlugin] Completion result payload: {result_payload}")
        print(f"[CompletionPlugin] Completion result payload: {result_payload}")
 
        return json.dumps(result_payload)
 
    except Exception as e:
        logger.error(f"[CompletionPlugin] Explicit error during completion: {str(e)}", exc_info=True)
        return json.dumps({
            "error": str(e),
            "status": "failed"
        })