"""
EmbeddingPlugin: process_chunks
 
Processes chunks by generating embeddings and attaching them to each item.
Used in document processing, memory indexing, and semantic RAG flows.
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.embedding_service import EmbeddingService
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="process_chunks",
    description="Generate embeddings for each document chunk and attach them to the chunk data"
)
async def process_chunks(args: KernelArguments) -> str:
    try:
        chunks_json = args["chunks"]
        batch_size = int(args.get("batch_size", 10))
        model = args.get("model", "text-embedding-ada-002")
 
        chunks = json.loads(chunks_json)
        if not isinstance(chunks, list) or not chunks:
            return json.dumps({"error": "No valid chunks provided"})
 
        # Filter valid text chunks
        clean_chunks = [chunk for chunk in chunks if "text" in chunk and chunk["text"].strip()]
        texts = [chunk["text"] for chunk in clean_chunks]
 
        if not texts:
            logger.warning("[EmbeddingPlugin] No valid text found in chunks.")
            return json.dumps([])
 
        logger.info(f"[EmbeddingPlugin] Generating embeddings for {len(texts)} chunks (batch size: {batch_size})")
 
        embedding_service = EmbeddingService.get_instance()
        embeddings = await embedding_service.batch_generate_embeddings(texts)
 
        for i, emb in enumerate(embeddings):
            clean_chunks[i]["embedding"] = emb
 
        return json.dumps(clean_chunks)
 
    except Exception as e:
        logger.error(f"[EmbeddingPlugin] Chunk processing failed: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})