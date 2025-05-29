"""
SearchPlugin: hybrid_search_function
 
Performs hybrid (vector + keyword) search for document chunks using Azure AI Search.
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
# from services.azure_search_service import AzureSearchService
from services.embedding_service import EmbeddingService
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="hybrid_search",
    description="Combine semantic and keyword search to find most relevant document chunks"
)
async def hybrid_search(args: KernelArguments) -> str:
    try:
        query = args["query"]
        top_k = int(args.get("top_k", 5))
        semantic_weight = float(args.get("semantic_weight", 0.8))  # optional
        filter_expr = args.get("filter", "")
 
        embedding_service = EmbeddingService.get_instance()
        query_embedding = await embedding_service.generate_embeddings(query)
 
        search_service = AzureSearchService.get_instance()
        results = await search_service.hybrid_search(
            query=query,
            query_vector=query_embedding,
            filter_expression=filter_expr or None,
            top_k=top_k
        )
 
        return json.dumps(results)
 
    except Exception as e:
        logger.error(f"[SearchPlugin] hybrid_search failed: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})