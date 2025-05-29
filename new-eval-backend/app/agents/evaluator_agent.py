"""
EvaluatorAgent.py
 
Purpose:
- Explicitly performs quantitative evaluation of model responses using metrics:
  BLEU, ROUGE-1, ROUGE-L, BERTScore, Cosine Similarity.
- Leverages Semantic Kernel plugin: ComparisonPlugin.analyze_metrics.
 
Inputs:
- prompt (str): Original user query explicitly passed for context.
- model_outputs (Dict[str, PlannerOutput]): Model responses and initial metrics.
 
Outputs:
- Explicitly updates model_outputs in-place with computed quantitative metrics under:
  model_outputs[model_id].metrics["comparison"].
- No real-time SignalR broadcasting; all metrics are handled asynchronously and stored explicitly in backend.
"""
 
import logging
import json
from typing import Dict
from models.mcp_models import PlannerOutput
from services.semantic_kernel_service import SemanticKernelService
 
logger = logging.getLogger(__name__)
 
class EvaluatorAgent:
    def __init__(self):
        self.sk = SemanticKernelService.get_instance()
 
    async def run(
        self,
        prompt: str,
        model_outputs: Dict[str, PlannerOutput],
        session_id: str
    ) -> Dict[str, PlannerOutput]:
        """
        Execute quantitative evaluation of model outputs explicitly without real-time broadcasting.
 
        Args:
            prompt (str): Original input prompt explicitly provided.
            model_outputs (Dict[str, PlannerOutput]): Model responses.
 
        Returns:
            Dict[str, PlannerOutput]: Model outputs explicitly enhanced with quantitative metrics.
        """
        logger.info("[EvaluatorAgent] Starting quantitative evaluation explicitly without SignalR...")
        print(model_outputs, 'MODELOUTPSD=>')
        try:
            # Prepare explicit payload for Semantic Kernel evaluation
            metrics_payload = [
                {
                    "model_id": model_id,
                    "timing": {"total_response_time": output.response_time},
                    "tokens": {
                        "prompt_tokens": output.metrics.get("promptTokens", 0),
                        "completion_tokens": output.metrics.get("completionTokens", 0),
                        "total_tokens": output.metrics.get("totalTokens", 0)
                    },
                    "cost": {"total_cost": 0.0}  # Placeholder for potential billing integration
                }
                for model_id, output in model_outputs.items()
            ]
 
            payload_str = json.dumps(metrics_payload)
            print(f"[EvaluatorAgent] Explicit metrics payload: {payload_str}")
            logger.debug(f"[EvaluatorAgent] Explicit metrics payload: {payload_str}")
                # Extract response content for metrics calculation
            model_responses = {
                model_id: output.content 
                for model_id, output in model_outputs.items()
            }
            print(model_responses, 'MODEL_RESPONSES=>')
            logger.debug(f"[EvaluatorAgent] Model responses for metrics: {model_responses}")
            # Invoke Semantic Kernel ComparisonPlugin explicitly for evaluation
            response = await self.sk.run_plugin_function(
                plugin_name="ComparisonPlugin",
                function_name="analyze_metrics",
                parameters={
                "metrics": payload_str,
                "prompt": prompt,  # Add the prompt parameter which is already available
                "responses": model_responses 
                }
            )
 
            result = json.loads(response)
            comparisons = result.get("comparisons", [])
            print(f"[EvaluatorAgent] Explicit comparison results: {comparisons}")
            logger.debug(f"[EvaluatorAgent] Explicit comparison results: {comparisons}")
 
            # Update model outputs explicitly with quantitative metrics
            for comp in comparisons:
                model_id = comp.get("model_id")
                if model_id and model_id in model_outputs:
                    model_outputs[model_id].metrics["comparison"] = comp
                    logger.info(f"[EvaluatorAgent] Metrics explicitly updated for model '{model_id}'")
                    message_payload = {
                        "model_id": model_id,
                        "BLEU": comp.get("BLEU"),
                        "ROUGE_1": comp.get("ROUGE_1"),
                        "ROUGE_L": comp.get("ROUGE_L"),
                        "BERTScore": comp.get("BERTScore"),
                        "CosineSimilarity": comp.get("CosineSimilarity"),
                        "duration": model_outputs[model_id].response_time
                    }
                    print(f"[EvaluatorAgent] Explicitly processed metrics for model '{model_id}': {message_payload}")
 
            logger.info(f"[EvaluatorAgent] Quantitative evaluation completed explicitly for {len(comparisons)} models.")
 
        except Exception as e:
            logger.error(f"[EvaluatorAgent] Explicit evaluation error: {str(e)}", exc_info=True)
 
        return model_outputs