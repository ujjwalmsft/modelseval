"""
Semantic Memory Service
 
Provides helper functions for agents to:
- Search past conversations (vector similarity)
- Save memory items
- Retrieve memory context by thread or model
 
Uses Semantic Kernel plugins (MemoryPlugin).
"""
 
import logging
import json
from typing import List, Optional, Dict, Any
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel import Kernel
import traceback 
from services.semantic_kernel_service import SemanticKernelService
 
logger = logging.getLogger(__name__)
 
class SemanticMemoryService:
    def __init__(self):
        self.kernel: Kernel = SemanticKernelService.get_instance().kernel
 
    async def search_memory(
        self,
        model_id: str,
        prompt: str,
        thread_id: str = "*",
        limit: int = 5,
        min_relevance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search semantic memory for similar past prompts or responses.
        
                Args:
            model_id: Model scope for memory search
            prompt: Query string
            thread_id: Filter by thread_id (or '*' for all)
            limit: Max results
            min_relevance: Minimum score (0-1)
 
        Returns:
            List of memory items
        """
        logger.info(f"[Memory] Searching memory for model={model_id}, thread_id={thread_id}, prompt={prompt[:50]}...")

        args = KernelArguments({
            "model_id": model_id,
            "query": prompt,
            "limit": str(limit)
        })

        try:
            logger.info(f"[Memory] Invoking MemoryPlugin.search_memory for model: {model_id}")
            result = await self.kernel.invoke_plugin_function_async(
                plugin_name="MemoryPlugin",
                function_name="search_memory",
                arguments=args
            )
            logger.info(f"[Memory] Search_memory returned result type: {type(result)}")
            memory_list = json.loads(result)
            filtered_results = [item for item in memory_list if item.get("similarity", 0) >= min_relevance]
            logger.info(f"[Memory] Found {len(filtered_results)} relevant items (from {len(memory_list)} total)")
            return filtered_results

        except Exception as e:
            logger.error(f"[Memory] Memory search failed: {str(e)}")
            logger.error(f"[Memory] Error details: {traceback.format_exc()}")
            return []
 
    async def retrieve_context_by_thread(
        self,
        model_id: str,
        thread_id: str,
        query: str,
        limit: int = 5,
        min_relevance: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get memory content filtered by thread.
 
        Returns:
            List of memory entries relevant to query in given thread.
        """
        args = KernelArguments({
            "model_id": model_id,
            "thread_id": thread_id,
            "query": query,
            "limit": str(limit),
            "min_relevance": str(min_relevance)
        })
 
        try:
            result = await self.kernel.invoke_plugin_function_async(
                plugin_name="MemoryPlugin",
                function_name="retrieve_context",
                arguments=args
            )
            return json.loads(result)
        except Exception as e:
            logger.error(f"[Memory] Thread-specific context retrieval failed: {str(e)}")
            return []
 
    async def save_memory_item(
        self,
        model_id: str,
        collection: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a new memory entry to semantic memory.
 
        Args:
            model_id: Model scope
            collection: Collection name
            content: Text content to embed
            metadata: Optional JSON metadata
 
        Returns:
            bool success
        """
        args = KernelArguments({
            "model_id": model_id,
            "collection_name": collection,
            "content": content,
            "metadata": json.dumps(metadata or {})
        })
 
        try:
            result = await self.kernel.invoke_plugin_function_async(
                plugin_name="MemoryPlugin",
                function_name="save_memory_item",
                arguments=args
            )
            logger.info(f"[Memory] Memory item saved.")
            return True
        except Exception as e:
            logger.error(f"[Memory] Failed to save memory item: {str(e)}")
            return False