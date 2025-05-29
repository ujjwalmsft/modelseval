"""
ComparisonPlugin: analyze_metrics_function.py
 
Purpose:
- Explicitly calculates quantitative evaluation metrics (BLEU, ROUGE-1, ROUGE-L, Semantic Cosine Similarity).
- Receives structured JSON payload (list of model responses with metadata).
- Returns structured JSON explicitly containing computed metrics.
 
Dependencies explicitly:
- nltk (for lightweight BLEU)
- rouge-score (for lightweight ROUGE metrics)
- numpy (for cosine similarity)
- Azure OpenAI SDK for embeddings (text-embedding-ada-002)
 
Heavy dependencies explicitly avoided:
- bert-score
- torch
- transformers
"""
 
import json
import logging
from typing import List, Dict, Any
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions import kernel_function
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
from openai import AzureOpenAI
import numpy as np
from config import settings
 
logger = logging.getLogger(__name__)
 
@kernel_function(
    name="analyze_metrics",
    description="Compute BLEU, ROUGE, and semantic cosine similarity metrics explicitly for model responses."
)
async def analyze_metrics(arguments: KernelArguments) -> str:
    try:
        print(f"[ComparisonPlugin] Analyzing metrics explicitly for models...")
        print(arguments, 'ARGUMENTS=>')
        prompt = arguments["prompt"]
        metrics_payload = json.loads(arguments["metrics"])
        model_responses = arguments.get("responses", {})
        
        # Use the server's embedding endpoint that we know works (from logs)
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint="https://macae-openai-7dfokqmjfelni.openai.azure.com",
            api_version="2023-05-15"
        )
 
        logger.info(f"[ComparisonPlugin] Received payload explicitly for {len(metrics_payload)} models.")
        reference = prompt.strip()
        
        if not reference:
            logger.warning(f"[ComparisonPlugin] Empty reference text, cannot compute metrics")
            return json.dumps({"error": "Empty reference text", "comparisons": []})
 
        # Generate embedding for prompt explicitly
        reference_embedding = get_embedding(client, reference)
        if not reference_embedding:
            logger.error(f"[ComparisonPlugin] Failed to generate embedding for reference text")
            return json.dumps({"error": "Failed to generate reference embedding", "comparisons": []})
 
        # Initialize ROUGE scorer explicitly
        rouge = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
 
        comparisons: List[Dict[str, Any]] = []
 
        for metric in metrics_payload:
            model_id = metric["model_id"]
            candidate = model_responses.get(model_id, "").strip()
            
            logger.info(f"[ComparisonPlugin] Model {model_id} response length: {len(candidate)} chars")
            logger.debug(f"[ComparisonPlugin] Model {model_id} response: '{candidate[:50]}...'")
            
            # Skip empty responses
            if not candidate:
                logger.warning(f"[ComparisonPlugin] Empty response for model {model_id}, skipping metrics")
                continue
 
            # Generate embedding explicitly for candidate
            candidate_embedding = get_embedding(client, candidate)
            if not candidate_embedding:
                logger.warning(f"[ComparisonPlugin] Failed to generate embedding for model {model_id}, skipping")
                continue
 
            # Cosine Similarity explicitly
            cosine_sim = cosine_similarity(reference_embedding, candidate_embedding)
 
            # BLEU Score explicitly
            try:
                bleu = sentence_bleu(
                    [reference.split()],
                    candidate.split(),
                    smoothing_function=SmoothingFunction().method1
                )
            except Exception as bleu_err:
                logger.warning(f"[ComparisonPlugin] Error calculating BLEU: {str(bleu_err)}")
                bleu = 0.0
 
            # ROUGE Scores explicitly
            try:
                rouge_scores = rouge.score(reference, candidate)
                rouge1_score = rouge_scores['rouge1'].fmeasure
                rougeL_score = rouge_scores['rougeL'].fmeasure
            except Exception as rouge_err:
                logger.warning(f"[ComparisonPlugin] Error calculating ROUGE: {str(rouge_err)}")
                rouge1_score = 0.0
                rougeL_score = 0.0
 
            # Calculate combined score (average of all metrics)
            combined_score = (bleu + rouge1_score + rougeL_score + cosine_sim) / 4.0
 
            comparison_result = {
                "model_id": model_id,
                "BLEU": round(bleu, 4),
                "ROUGE_1": round(rouge1_score, 4),
                "ROUGE_L": round(rougeL_score, 4),
                "SemanticCosineSimilarity": round(cosine_sim, 4),
                "CombinedScore": round(combined_score, 4),
                "metrics": {
                    "response_time": metric["timing"]["total_response_time"],
                    "tokens": metric["tokens"],
                    "tokens_per_second": round(
                        metric["tokens"]["total_tokens"] / metric["timing"]["total_response_time"], 2
                    ) if metric["timing"]["total_response_time"] > 0 else 0
                }
            }
 
            comparisons.append(comparison_result)
            logger.info(f"[ComparisonPlugin] Metrics for model '{model_id}': BLEU={bleu:.4f}, ROUGE1={rouge1_score:.4f}, SIM={cosine_sim:.4f}")
 
        result = {"comparisons": comparisons}
 
        logger.debug(f"[ComparisonPlugin] Completed metrics analysis explicitly.")
        return json.dumps(result)
 
    except Exception as e:
        logger.error(f"[ComparisonPlugin] Error explicitly calculating metrics: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e), "comparisons": []})
 
 
def get_embedding(client: AzureOpenAI, text: str, model="text-embedding-ada-002") -> List[float]:
    """Generate Azure OpenAI embeddings explicitly for semantic similarity."""
    # Check for empty text
    if not text or len(text.strip()) == 0:
        logger.warning(f"[ComparisonPlugin] Attempted to get embedding for empty text")
        # Return zeros instead of calling API with empty text
        return [0.0] * 1536  # Standard embedding dimension
    
    try:
        # Ensure text is properly sanitized for API
        text = text.strip()
        if len(text) > 8000:  # OpenAI has token limits
            text = text[:8000]
            
        response = client.embeddings.create(input=[text], model=model)
        embedding = response.data[0].embedding
        logger.debug(f"[ComparisonPlugin] Generated embedding with dimension: {len(embedding)}")
        return embedding
    except Exception as e:
        logger.error(f"[ComparisonPlugin] Error generating embedding: {str(e)}")
        # Return zeros as fallback
        return [0.0] * 1536
 
 
def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity explicitly between two embeddings."""
    try:
        vec_a_np = np.array(vec_a)
        vec_b_np = np.array(vec_b)
        
        # Check for zero vectors
        if np.all(vec_a_np == 0) or np.all(vec_b_np == 0):
            return 0.0
            
        similarity = np.dot(vec_a_np, vec_b_np) / (np.linalg.norm(vec_a_np) * np.linalg.norm(vec_b_np))
        
        # Handle NaN (can happen with very small numbers)
        if np.isnan(similarity):
            return 0.0
            
        logger.debug(f"[ComparisonPlugin] Cosine similarity: {similarity:.4f}")
        return similarity
    except Exception as e:
        logger.error(f"[ComparisonPlugin] Error calculating cosine similarity: {str(e)}")
        return 0.0