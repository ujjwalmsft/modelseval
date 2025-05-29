"""
PlannerAgent
 
Responsible explicitly for generating aggregated completions for all requested models
using Semantic Kernel and CompletionPlugin. Each model's response is explicitly saved
to Cosmos DB memory, and responses are aggregated explicitly for downstream event handling.
 
Assumptions explicitly preserved:
- Semantic Kernel v1.28.1+
- Plugins explicitly loaded dynamically via SemanticKernelService
- All completions explicitly written to Cosmos DB memory (threads container)
 
Updated explicitly to:
- Clearly aggregate responses per model with complete metadata.
- Explicitly maintain robust error handling and logging.
- Prevent duplicate assistant responses explicitly in Cosmos DB.
"""
 
import logging
import time
import json
from typing import List, Dict, Optional
from services.semantic_kernel_service import SemanticKernelService
from services.cosmos_service import CosmosService
from models.mcp_models import PlannerOutput
 
logger = logging.getLogger(__name__)
 
class PlannerAgent:
    def __init__(self):
        """Explicitly initializes Semantic Kernel and CosmosDB service instances."""
        self.sk_service = SemanticKernelService.get_instance()
        self.cosmos = CosmosService.get_instance()
        print(self.sk_service, 'SKS=>')
        logger.debug("[PlannerAgent] SemanticKernelService and CosmosService initialized successfully.")
 
    async def run(
        self,
        models: List[str],
        prompt: str,
        session_id: str,
        mcp_thread_id: str,
        system_prompt: Optional[str] = None,
        use_case_id: str = "1"
    ) -> Dict[str, PlannerOutput]:
        """
        Explicitly runs completions for each model via CompletionPlugin using Semantic Kernel,
        aggregates results, saves responses explicitly to Cosmos DB, and returns structured outputs.
 
        Args:
            models (List[str]): Explicit list of model identifiers (e.g., ['gpt4', 'phi4']).
            prompt (str): Explicit user input prompt (supports both use cases).
            session_id (str): Explicit UI/user session identifier.
            mcp_thread_id (str): Explicit Semantic Kernel memory thread identifier.
            system_prompt (Optional[str]): Explicit assistant behavior prompt.
            use_case_id (str): Explicit evaluation mode ("1": zero-shot, "2": context-enhanced).
 
        Returns:
            Dict[str, PlannerOutput]: Explicitly aggregated structured outputs per model.
        """
        logger.info(f"[PlannerAgent] Starting for session '{session_id}', thread '{mcp_thread_id}', models: {models}")
        start_time = time.time()
 
        completions: Dict[str, PlannerOutput] = {}
 
        # Explicit iteration over each model to generate completions
        for model_id in models:
            print
            logger.debug(f"[PlannerAgent] Preparing completion explicitly for model '{model_id}'")
 
            args = {
                "prompt": prompt,
                "model_id": model_id,
                "deployment": model_id,
                "system_prompt": system_prompt or "You are a helpful assistant.",
                "conversation_id": mcp_thread_id,
                "temperature": "0.7",
                "max_tokens": "2000"
            }
 
            try:
                # Explicit invocation of CompletionPlugin via Semantic Kernel
                print(f"[PlannerAgent] Invoking CompletionPlugin explicitly for model '{model_id}' with args: {args}")
                logger.debug(f"[PlannerAgent] Invoking CompletionPlugin explicitly for model '{model_id}' with args: {args}")
                result_str = await self.sk_service.run_plugin_function(
                    plugin_name="CompletionPlugin",
                    function_name="run_completion",
                    parameters=args
                )
                print(f"[PlannerAgent] Raw completion response explicitly received for model '{model_id}': {result_str}")
                logger.debug(f"[PlannerAgent] Raw completion response explicitly received for model '{model_id}': {result_str}")
 
                # Explicitly parse completion response JSON
                parsed = json.loads(result_str)
                content = parsed.get("content", "")
                metrics = parsed.get("metrics", {})
                safety = parsed.get("safety", None)
                latency = metrics.get("responseTime", 0.0)
 
                # Explicitly check and save assistant response without duplication
                cosmos_response = await self.cosmos.save_conversation_message(
                    model_id=model_id,
                    thread_id=mcp_thread_id,
                    role="assistant",
                    content=content,
                    token_count=metrics.get("totalTokens", 0)
                )
 
                if cosmos_response.get("status") == "duplicate_skipped":
                    logger.warning(f"[PlannerAgent] Duplicate response explicitly skipped for model '{model_id}'")
 
                # Explicit aggregation of completion output per model
                completions[model_id] = PlannerOutput(
                    model_id=model_id,
                    content=content,
                    response_time=latency,
                    metrics=metrics,
                    safety=safety
                )
 
                logger.info(f"[PlannerAgent] Completion explicitly processed successfully for model '{model_id}'")
 
            except Exception as e:
                # Explicit robust error handling and detailed logging
                logger.error(f"[PlannerAgent] Exception explicitly encountered for model '{model_id}': {str(e)}", exc_info=True)
                completions[model_id] = PlannerOutput(
                    model_id=model_id,
                    content=f"[ERROR] {str(e)}",
                    response_time=0.0,
                    metrics={},
                    safety=None
                )
 
        total_duration = time.time() - start_time
        logger.info(f"[PlannerAgent] Aggregated completions explicitly completed in {total_duration:.2f}s")
 
        return completions