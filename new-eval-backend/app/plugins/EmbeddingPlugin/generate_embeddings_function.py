"""
EmbeddingPlugin: generate_embeddings
 
Generates vector embeddings for a single input text.
Used in semantic memory, search, and evaluator metrics.
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.embedding_service import EmbeddingService
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="generate_embeddings",
    description="Generate vector embeddings for input text"
)
async def generate_embeddings(args: KernelArguments) -> str:
    try:
        text = args["text"]
        if not text or not text.strip():
            return json.dumps([])
 
        logger.info(f"[EmbeddingPlugin] Generating embedding for text: {text[:40]}...")
        embedding_service = EmbeddingService.get_instance()
        vector = await embedding_service.generate_embeddings(text)
 
        return json.dumps(vector)
 
    except Exception as e:
        logger.error(f"[EmbeddingPlugin] Error generating embedding: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})