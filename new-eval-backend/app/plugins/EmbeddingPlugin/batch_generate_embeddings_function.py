"""
EmbeddingPlugin: batch_generate_embeddings
 
Generates embeddings for multiple text chunks in a single batch.
Ideal for processing documents, context, and memory indexing.
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.embedding_service import EmbeddingService
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="batch_generate_embeddings",
    description="Generate embeddings for multiple text chunks efficiently"
)
async def batch_generate_embeddings(args: KernelArguments) -> str:
    try:
        texts_json = args["texts"]
        model = args.get("model", "text-embedding-ada-002")
 
        texts = json.loads(texts_json)
 
        if not texts:
            logger.warning("[EmbeddingPlugin] No texts provided for batch embedding.")
            return json.dumps([])
 
        # Filter blank or whitespace-only strings
        clean_texts = [t for t in texts if isinstance(t, str) and t.strip()]
        if not clean_texts:
            return json.dumps([])
 
        logger.info(f"[EmbeddingPlugin] Generating batch embeddings for {len(clean_texts)} texts...")
 
        embedding_service = EmbeddingService.get_instance()
        vectors = await embedding_service.batch_generate_embeddings(clean_texts)
 
        return json.dumps(vectors)
 
    except json.JSONDecodeError:
        logger.error("[EmbeddingPlugin] Failed to parse input texts JSON.")
        return json.dumps({"error": "Invalid JSON format"})
    except Exception as e:
        logger.error(f"[EmbeddingPlugin] Batch embedding failed: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})