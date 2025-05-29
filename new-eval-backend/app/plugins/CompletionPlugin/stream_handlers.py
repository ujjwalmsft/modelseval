"""
Stream Handlers for LLM Completion
 
Handles chunked streaming from Azure OpenAI compatible models.
 
Used by:
- /stream/{generator_id}
- stream_register.get_streaming_generator
"""
 
import re
import logging
import asyncio
from typing import AsyncGenerator, Tuple, Optional
from config import settings
 
logger = logging.getLogger(__name__)
 
 
async def stream_azure_openai_completion(
    prompt: str,
    deployment: str,
    endpoint: str,
    api_key: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> AsyncGenerator[str, None]:
    """
    Stream completion using Azure OpenAI's chat.completions API.
 
    Yields:
        str: JSON string of each streamed chunk
    """
    try:
        from openai import AzureOpenAI
 
        client = AzureOpenAI(
            api_key=api_key,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=endpoint
        )
 
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
 
        stream = client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
 
        collected = ""
        prompt_tokens = len(prompt) // 4
 
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices[0].delta else ""
            collected += delta
            completion_tokens = len(collected) // 4
            yield _format_chunk(
                content=delta,
                collected=collected,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                status="streaming"
            )
            await asyncio.sleep(0.01)
 
        yield _format_chunk(
            content="",
            collected=collected,
            prompt_tokens=prompt_tokens,
            completion_tokens=len(collected) // 4,
            status="complete"
        )
 
    except Exception as e:
        logger.error(f"[StreamHandler] Streaming error: {str(e)}")
        yield json.dumps({
            "status": "error",
            "error": str(e)
        })
 
 
def _format_chunk(
    content: str,
    collected: str,
    prompt_tokens: int,
    completion_tokens: int,
    status: str
) -> str:
    return json.dumps({
        "content": content,
        "collected_content": collected,
        "status": status,
        "metrics": {
            "promptTokens": prompt_tokens,
            "completionTokens": completion_tokens,
            "totalTokens": prompt_tokens + completion_tokens
        }
    })