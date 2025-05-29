"""
Streaming Request Registry (Ephemeral)
 
Manages registered LLM streaming generators (in-memory).
Used to match generator_id to the correct request on /stream/{id}.
 
Supports:
- Original individual streaming requests (fully preserved)
- Explicitly aggregated streaming requests for multiple model completions
"""
 
import logging
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
 
logger = logging.getLogger(__name__)
 
# In-memory registry (could be Redis in production)
_stream_registry: Dict[str, Dict[str, Any]] = {}
 
# Clean-up after this many seconds (default 10 min)
STREAM_TIMEOUT_SECONDS = 600
 
async def register_stream_request(
    generator_id: str,
    model_id: Optional[str],
    deployment: Optional[str],
    provider: Optional[str],
    endpoint: Optional[str],
    api_key: Optional[str],
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    is_aggregated: bool = False,
    models: Optional[Dict[str, Any]] = None
) -> None:
    """
    Store streaming request metadata for later generator lookup.
 
    Args:
        generator_id: Unique identifier for the stream.
        model_id: ID of the individual model (None for aggregated streams).
        deployment: Model deployment details.
        provider: Service provider (e.g., Azure).
        endpoint: API endpoint URL.
        api_key: API key for model access.
        prompt: User prompt to be streamed.
        system_prompt: Optional system prompt.
        temperature: Generation temperature.
        max_tokens: Maximum token limit.
        is_aggregated: Whether the stream handles aggregated results.
        models: Dict of model details if aggregated stream.
    """
    _stream_registry[generator_id] = {
        "model_id": model_id,
        "deployment": deployment,
        "provider": provider,
        "endpoint": endpoint,
        "api_key": api_key,
        "prompt": prompt,
        "system_prompt": system_prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "generator": None,
        "status": "registered",
        "is_aggregated": is_aggregated,
        "models": models or {}
    }
 
    stream_type = "aggregated" if is_aggregated else "single"
    logger.info(f"[StreamRegister] Registered {stream_type} stream: {generator_id}")
    asyncio.create_task(_expire_generator(generator_id))
 
async def register_streaming_generator(generator_id: str, generator: AsyncGenerator) -> None:
    """
    Attach a generator to an existing registered request.
 
    Args:
        generator_id: Unique stream identifier.
        generator: AsyncGenerator instance handling the stream.
    """
    if generator_id in _stream_registry:
        _stream_registry[generator_id]["generator"] = generator
        _stream_registry[generator_id]["status"] = "ready"
        logger.info(f"[StreamRegister] Generator attached: {generator_id}")
    else:
        logger.warning(f"[StreamRegister] Attempted to attach generator to non-existent stream: {generator_id}")
 
async def get_stream_request(generator_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve stream metadata.
 
    Args:
        generator_id: Unique stream identifier.
 
    Returns:
        Stream request metadata or None if not found.
    """
    return _stream_registry.get(generator_id)
 
async def get_streaming_generator(generator_id: str) -> Optional[AsyncGenerator]:
    """
    Retrieve the streaming generator.
 
    Args:
        generator_id: Unique stream identifier.
 
    Returns:
        AsyncGenerator instance or None if not found.
    """
    req = _stream_registry.get(generator_id)
    return req.get("generator") if req else None
 
async def delete_stream_request(generator_id: str) -> bool:
    """
    Delete stream metadata.
 
    Args:
        generator_id: Unique stream identifier.
 
    Returns:
        True if deleted, False if not found.
    """
    if generator_id in _stream_registry:
        del _stream_registry[generator_id]
        logger.info(f"[StreamRegister] Deleted stream: {generator_id}")
        return True
    logger.warning(f"[StreamRegister] Attempted to delete non-existent stream: {generator_id}")
    return False
 
async def _expire_generator(generator_id: str):
    """
    Expire and delete stream metadata after timeout.
 
    Args:
        generator_id: Unique stream identifier.
    """
    await asyncio.sleep(STREAM_TIMEOUT_SECONDS)
    if generator_id in _stream_registry:
        logger.info(f"[StreamRegister] Expiring stream due to timeout: {generator_id}")
        await delete_stream_request(generator_id)