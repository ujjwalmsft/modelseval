"""
MemoryPlugin: list_collection_function
 
Lists all memory collections available for a specific model_id.
Used for UI tools, diagnostics, and agents to explore scoped memory.
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.cosmos_service import CosmosService
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="list_collections",
    description="List all available memory collections for a specific model"
)
async def list_collections(arguments: KernelArguments) -> str:
    try:
        model_id = arguments["model_id"]
 
        cosmos = CosmosService.get_instance()
        container = await cosmos.get_container("memory")
 
        query = """
        SELECT DISTINCT c.collection FROM c
        WHERE c.metadata.model_id = @model_id
        """
        parameters = [{"name": "@model_id", "value": model_id}]
 
        items = await container.query_items(query=query, parameters=parameters)
        collections = []
 
        async for item in items:
            if "collection" in item:
                collections.append(item["collection"])
 
        return json.dumps(collections)
 
    except Exception as e:
        logger.error(f"[MemoryPlugin] list_collections failed: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})