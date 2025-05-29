"""
MemoryPlugin: retrieve_context_function
 
Retrieves top relevant memory entries scoped to a conversation thread
using vector similarity.
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.embedding_service import EmbeddingService
from services.cosmos_service import CosmosService
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="retrieve_context",
    description="Retrieve relevant memory entries from a specific thread using semantic similarity"
)
async def retrieve_context(arguments: KernelArguments) -> str:
    try:
        print(arguments, 'ARGUMENTS TO CHOOSE FROM AT RETRIEVE CONTEXT')
        model_id = arguments["model_id"]
        thread_id = arguments["thread_id"]
        query = arguments["query"]
        limit = int(arguments.get("limit", 5))
        min_relevance = float(arguments.get("min_relevance", 0.7))
 
        embedding_service = EmbeddingService.get_instance()
        query_vector = await embedding_service.generate_embeddings(query)
 
        cosmos = CosmosService.get_instance()
        container = await cosmos.get_container("memory")
 
        query_sql = """
        SELECT * FROM c
        WHERE c.collection = @collection
        """
        collection = f"model-memory-{model_id}"
        params = [{"name": "@collection", "value": collection}]
        results = await container.query_items(query=query_sql, parameters=params)
 
        matches = []
        async for item in results:
            if "embedding" not in item:
                continue
 
            similarity = embedding_service.calculate_similarity(query_vector, item["embedding"])
            if similarity >= min_relevance:
                if thread_id == "*" or item.get("metadata", {}).get("thread_id") == thread_id:
                    item["relevance"] = round(similarity, 4)
                    matches.append(item)
 
        sorted_matches = sorted(matches, key=lambda x: x["relevance"], reverse=True)[:limit]
        return json.dumps(sorted_matches)
 
    except Exception as e:
        logger.error(f"[MemoryPlugin] retrieve_context failed: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})