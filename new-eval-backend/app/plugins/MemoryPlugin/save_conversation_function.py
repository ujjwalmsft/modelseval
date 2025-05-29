"""
MemoryPlugin: save_conversation
 
Saves a conversation exchange to Cosmos DB and vector memory (if enabled).
Used by CompletionPlugin and agents for logging and semantic recall.
"""
 
import json
import logging
import traceback
import time
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.cosmos_service import CosmosService
from services.embedding_service import EmbeddingService
from config import settings
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="save_conversation",
    description="Save a conversation message to memory and vector store"
)
async def save_conversation(arguments: KernelArguments) -> str:
    try:
        model_id = arguments["model_id"]
        conversation_id = arguments["conversation_id"]
        role = arguments["role"]
        content = arguments["content"]
        timestamp = arguments.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
 
        token_count = int(arguments.get("token_count", len(content) // 4))
 
        # Save to Cosmos thread memory
        cosmos = CosmosService.get_instance()
        logger.info(f"[MemoryPlugin] Saving {role} message to thread {conversation_id} for model {model_id}")
        
        # This is async so we must await it
        result = await cosmos.save_conversation_message(
            model_id=model_id,
            thread_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count
        )
 
        logger.info(f"[MemoryPlugin] Saved {role} message to thread {conversation_id}")
 
        # Also embed and store to vector DB (semantic memory)
        if settings.COSMOS_VECTOR_ENABLED:
            logger.info(f"[MemoryPlugin] Vector storage enabled, generating embedding for {len(content)} chars")
            embedding_service = EmbeddingService.get_instance()
            
            # This is async so we must await it
            vector = await embedding_service.generate_embeddings(content)
            logger.info(f"[MemoryPlugin] Generated embedding with dimension: {len(vector)}")
            
            metadata = {
                "thread_id": conversation_id,
                "model_id": model_id,
                "timestamp": timestamp,
                "type": role
            }
            
            # Generate unique reference ID
            reference_id = f"{model_id}-{conversation_id}-{int(time.time())}"
            logger.info(f"[MemoryPlugin] Generated reference ID: {reference_id}")
            
            # Since save_embedding is NOT async, we don't await it
            result = cosmos.save_embedding(
                text=content,
                embedding=vector,
                collection=f"model-memory-{model_id}", 
                reference_id=reference_id,
                metadata=metadata
            )
            
            
            if result["status"] == "success":
                logger.info(f"[MemoryPlugin] Successfully saved embedding with ID: {result['id']}")
            else:
                logger.error(f"[MemoryPlugin] Failed to save embedding: {result.get('error', 'Unknown error')}")
 
        return json.dumps({
            "status": "success",
            "thread_id": conversation_id,
            "model_id": model_id,
            "role": role
        })
 
    except Exception as e:
        logger.error(f"[MemoryPlugin] Error saving conversation: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})
            