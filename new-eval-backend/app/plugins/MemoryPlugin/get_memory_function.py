"""
MemoryPlugin: get_memory_content
 
Retrieves all memory items from a specific collection for a model.
Used by agents or admins to inspect stored memory.
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.cosmos_service import CosmosService
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="get_memory_content",
    description="Retrieve all memory records from a collection"
)
async def get_memory_content(arguments: KernelArguments) -> str:
    try:
        model_id = arguments["model_id"]
        collection_name = arguments["collection_name"]
 
        cosmos = CosmosService.get_instance()
        container = await cosmos.get_container("memory")
 
        query = """
        SELECT * FROM c WHERE c.collection = @collection AND c.metadata.model_id = @model_id
        """
        parameters = [
            {"name": "@collection", "value": collection_name},
            {"name": "@model_id", "value": model_id}
        ]
 
        results = await container.query_items(query=query, parameters=parameters)
        records = []
        async for item in results:
            records.append(item)
 
        return json.dumps(records)
 
    except Exception as e:
        logger.error(f"[MemoryPlugin] Error fetching memory: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})