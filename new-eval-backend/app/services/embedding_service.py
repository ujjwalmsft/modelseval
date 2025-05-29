"""
Embedding Service Singleton
 
Provides access to Azure OpenAI (or OpenAI) embedding API
for single text, batch processing, and cosine similarity.
 
Used by:
- EmbeddingPlugin
- MemoryPlugin
- EvaluatorAgent
- ReflectionAgent
- ComparisonPlugin
"""
 
import logging
import traceback
import numpy as np
from typing import List
from config import settings
 
logger = logging.getLogger(__name__)
 
class EmbeddingService:
    _instance = None
 
    def __init__(self):
        self.client = None
        self.model = settings.EMBEDDING_DEPLOYMENT
        self.endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.api_key = settings.AZURE_OPENAI_API_KEY
        self.api_version = settings.AZURE_OPENAI_API_VERSION
        self.initialized = False
 
    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = EmbeddingService()
        return cls._instance
 
    async def _ensure_initialized(self):
        if self.initialized:
            return
        try:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            self.initialized = True
            logger.info("[EmbeddingService] Initialized AzureOpenAI client")
        except Exception as e:
            logger.error(f"[EmbeddingService] Initialization failed: {str(e)}")
            raise
 
    async def generate_embeddings(self, text: str) -> List[float]:
        try:
            # Log before generating embedding with truncated text preview
            logger.info(f"[EmbeddingService] Generating embedding for text: '{text[:50]}...' ({len(text)} chars)")
            
            await self._ensure_initialized()
            
            # Log the API call to Azure
            logger.info(f"[EmbeddingService] Calling Azure OpenAI embedding API with model: {self.model}")
            
            result = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            
            # Enhanced success logging with more details
            embedding_dim = len(result.data[0].embedding)
            logger.info(f"[EmbeddingService] Successfully generated embedding with dimension: {embedding_dim}")
            logger.info(f"[EmbeddingService] Embedding sample (first 3 values): {result.data[0].embedding[:3]}")
            
            return result.data[0].embedding
            
        except Exception as e:
            # Enhanced error logging
            logger.error(f"[EmbeddingService] Failed to embed text: {str(e)}")
            logger.error(f"[EmbeddingService] Text that failed (truncated): '{text[:100]}...'")
            logger.error(traceback.format_exc())
            return []
 
    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            logger.info(f"[EmbeddingService] Batch embedding {len(texts)} texts")
            logger.info(f"[EmbeddingService] First text sample: '{texts[0][:50]}...'")
            
            await self._ensure_initialized()
            
            result = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            
            # Log success with details
            logger.info(f"[EmbeddingService] Successfully generated {len(result.data)} embeddings")
            
            return [item.embedding for item in result.data]
            
        except Exception as e:
            logger.error(f"[EmbeddingService] Batch embedding failed: {str(e)}")
            logger.error(traceback.format_exc())
            return [[] for _ in texts]
        
        
    def calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            sim = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            return sim
        except Exception as e:
            logger.error(f"[EmbeddingService] Similarity calc failed: {str(e)}")
            return 0.0