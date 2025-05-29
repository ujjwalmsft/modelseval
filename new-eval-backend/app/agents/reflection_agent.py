"""
ReflectionAgent (Without SignalR)
 
Purpose:
- Retrieve contextually similar past messages from semantic memory using vector search (Cosmos DB + EmbeddingPlugin).
- Persist reflection results explicitly in Cosmos DB (agent_results container).
 
Input:
- prompt (str): Current user input
- model_id (str): Used to scope memory collection
- session_id (str): Session/user identifier
- mcp_thread_id (str): Thread identifier
 
Output:
- Returns a block of top-N most relevant prior messages (or "" if none found).
- Explicitly persists results in Cosmos DB for frontend retrieval.
"""
 
import logging
import json
import time
from typing import Optional, Dict, Any
from services.semantic_kernel_service import SemanticKernelService
from services.cosmos_service import CosmosService
 
logger = logging.getLogger(__name__)
 
class ReflectionAgent:
    def __init__(self):
        self.sk = SemanticKernelService.get_instance()
        self.cosmos = CosmosService.get_instance()
 
    async def run(
        self,
        prompt: str,
        model_id: str,
        session_id: Optional[str],
        mcp_thread_id: Optional[str],
        top_k: int = 3,
        min_relevance: float = 0.7
    ) -> str:
        """
        Query memory and persist top-N context messages similar to the prompt.
 
        Args:
            prompt (str): The new user prompt
            model_id (str): Scope memory to this model's collection
            session_id (str): Session identifier
            mcp_thread_id (str): Thread-specific identifier
            top_k (int): Number of memory items to retrieve
            min_relevance (float): Minimum cosine similarity for inclusion
 
        Returns:
            str: Concatenated memory context block, or "" if none found
        """
        logger.info(f"[ReflectionAgent] Memory query started for thread={mcp_thread_id}, model={model_id}")
 
        try:
            # Run semantic memory query explicitly
            response = await self.sk.run_plugin_function(
                plugin_name="MemoryPlugin",
                function_name="search_memory",
                parameters={
                    "thread_id": mcp_thread_id,
                    "query": prompt,
                    "limit": str(top_k)
                }
            )
 
            memory_items = json.loads(response)
            if not isinstance(memory_items, list):
                logger.warning("[ReflectionAgent] Invalid memory query results format.")
                return ""
 
            # Filter results by explicit similarity threshold
            relevant_items = [
                item for item in memory_items if item.get("similarity", 0) >= min_relevance
            ]
 
            logger.info(f"[ReflectionAgent] Retrieved {len(relevant_items)} relevant memory items.")
 
            # Construct reflection result context block explicitly
            context_lines = [
                f"[Memory][{idx + 1}] {item.get('text', '').strip()}"
                for idx, item in enumerate(relevant_items)
            ]
            reflection_result = "\n\n".join(context_lines)
 
            # Explicitly persist reflection results to Cosmos DB
            await self.save_reflection_result(
                session_id=session_id,
                mcp_thread_id=mcp_thread_id,
                model_id=model_id,
                prompt=prompt,
                reflection_result=reflection_result,
                relevant_items=relevant_items
            )
 
            return reflection_result
 
        except Exception as e:
            logger.error(f"[ReflectionAgent] Memory query failed explicitly: {str(e)}", exc_info=True)
            return ""
 
    async def save_reflection_result(
        self,
        session_id: str,
        mcp_thread_id: str,
        model_id: str,
        prompt: str,
        reflection_result: str,
        relevant_items: list
    ) -> Dict[str, Any]:
        """
        Explicitly saves the reflection results into Cosmos DB agent_results container.
 
        Args:
            session_id (str): Session identifier
            mcp_thread_id (str): Thread identifier
            model_id (str): Model identifier
            prompt (str): Original user prompt
            reflection_result (str): Concatenated reflection results
            relevant_items (list): Raw relevant items data from memory
 
        Returns:
            dict: Operation status and item ID
        """
        try:
            now = int(time.time())
            doc_id = f"reflection-{session_id}-{model_id}-{now}"
 
            doc = {
                "id": doc_id,
                "session_id": session_id,
                "mcp_thread_id": mcp_thread_id,
                "model_id": model_id,
                "prompt": prompt,
                "reflection_result": reflection_result,
                "relevant_items": relevant_items,
                "timestamp": now,
                "type": "reflection"
            }
 
            container = await self.cosmos.get_container("agentsresults")
            print(container, 'container=>')
            logger.debug(f"[ReflectionAgent] Cosmos DB container: {container}")
            container.create_item(body=doc)
 
            logger.info(f"[ReflectionAgent] Reflection results explicitly persisted in Cosmos DB: {doc_id}")
 
            return {"status": "success", "id": doc_id}
 
        except Exception as e:
            logger.error(f"[ReflectionAgent] Failed to persist reflection result explicitly: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}