"""
SearchPlugin: semantic_search
 
Performs vector-based semantic search for relevant document chunks using Azure AI Search.
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
    name="semantic_search",
    description="Search documents using semantic (vector) similarity only"
)
async def semantic_search(args: KernelArguments) -> str:
    try:
        query = args["query"]
        top_k = int(args.get("top_k", 5))
        min_relevance = float(args.get("min_relevance", 0.7))
        filter_expr = args.get("filter", "")
 
        # Embed query
        embedding_service = EmbeddingService.get_instance()
        query_embedding = await embedding_service.generate_embeddings(query)
 
        # Search Azure vector DB
        search_service = AzureSearchService.get_instance()
        results = await search_service.vector_search(
            query_vector=query_embedding,
            filter_expression=filter_expr or None,
            top_k=top_k
        )
 
        # Filter by threshold
        filtered = [r for r in results if r.get("score", 0) >= min_relevance]
        return json.dumps(filtered)
 
    except Exception as e:
        logger.error(f"[SearchPlugin] semantic_search failed: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})