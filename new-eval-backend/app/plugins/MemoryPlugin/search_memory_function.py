"""
MemoryPlugin.search_memory
 
Search semantic memory for relevant context based on embeddings similarity.
"""
 
import logging
import json
import traceback
from typing import List, Dict, Any
import numpy as np
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.embedding_service import EmbeddingService
from services.cosmos_service import CosmosService
 
logger = logging.getLogger("app.plugins.MemoryPlugin.search_memory_function")
 
@kernel_function(
    name="search_memory",
    description="Search memory for relevant past prompts or responses"
)
@kernel_function(
    name="search_memory",
    description="Search memory for relevant past prompts or responses"
)
async def search_memory(args: KernelArguments) -> str:
    try:
        print(args, 'ARGUMENTS TO CHOOSE FROM AT SEARCH MEMORY')
        thread_id = args["thread_id"]
        query = args["query"]
        limit = int(args.get("limit", "5"))
        
        logger.info(f"[MemoryPlugin] Searching memory with query: '{query[:50]}...' for model {thread_id}")
        
        # Get embedding for query
        embedding_service = EmbeddingService.get_instance()
        logger.info(f"[MemoryPlugin] Generating query embedding")
        # This is async so we must await it
        query_embedding = await embedding_service.generate_embeddings(query)
        logger.info(f"[MemoryPlugin] Generated query embedding with dimension: {len(query_embedding)}")
        
        # Get container
        cosmos = CosmosService.get_instance()
        logger.info(f"[MemoryPlugin] Getting vector_container for embedding search")
        # This is async so we must await it
        container = await cosmos.get_container("embeddings(semantic-memory)")
        logger.info(f"[MemoryPlugin] Got container: {type(container)}")
        
        # Build query - Look specifically at model-memory-{model_id} collection
        sql = "SELECT * FROM c WHERE c.thread_id = @thread_id"
        params = [{"name": "@thread_id", "value": thread_id}]
        
        logger.info(f"[MemoryPlugin] Executing SQL query: {sql} with params: {params}")
        
        # Execute query - container.query_items is NOT async, so no await
        results = container.query_items(
            query=sql,
            parameters=params,
            enable_cross_partition_query=True  # Important for vector search
        )
        logger.info(f"[MemoryPlugin] Query executed, processing results")
        
        # Process results
        scored_results = []
        count = 0
        
        # Process the ItemPaged results
        for item in results:
            count += 1
            vector = item.get("embedding")
            if not vector:
                logger.warning(f"[MemoryPlugin] Item missing embedding vector: {item.get('id')}")
                continue
                
            # Calculate similarity
            score = embedding_service.calculate_similarity(query_embedding, vector)
            item["similarity"] = round(score, 4)
            
            # Remove the embedding vector to reduce response size
            item_copy = dict(item)
            item_copy.pop("embedding", None)
            scored_results.append(item_copy)
            
            if len(scored_results) >= limit:
                break
        
        logger.info(f"[MemoryPlugin] Found {len(scored_results)} relevant results from {count} total items")
        
        # Sort by similarity
        scored_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        
        return json.dumps(scored_results[:limit])
        
    except Exception as e:
        logger.error(f"[MemoryPlugin] search_memory failed: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps([])