"""
ComparisonPlugin: compare_responses
 
Uses GPT-4 to score model responses on:
- personalization, fluency, relevance, coherence, creativity
"""
 
import json
import logging
import traceback
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from services.semantic_kernel_service import SemanticKernelService
 
logger = logging.getLogger(__name__)
sk = SemanticKernelService.get_instance()
 
@kernel_function(
    name="compare_responses",
    description="Use GPT-4 to judge model responses qualitatively across criteria"
)
async def compare_responses(args: KernelArguments) -> str:
    try:
        responses = json.loads(args["responses"])
        query = args["query"]
        criteria = args.get("criteria", "personalization,fluency,relevance,coherence,creativity")
 
        # Format prompt
        system_prompt = (
            "You are an expert evaluator. Score each response from 1–10 per criterion "
            f"({criteria}). Also provide justification for each."
        )
        prompt_text = f"Prompt: {query}\n\n"
 
        for resp in responses:
            prompt_text += f"--- Response from {resp['model_id']} ---\n{resp['text']}\n\n"
 
        user_prompt = (
            f"Evaluate the above responses.\n"
            f"For each of these criteria ({criteria}), assign a score and provide reasons."
        )
 
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text + user_prompt}
        ]
 
        completion = await sk.chat_completion(
            model_id="gpt4",
            messages=messages,
            max_tokens=2048,
            temperature=0.2
        )
 
        return completion
 
    except Exception as e:
        logger.error(f"[compare_responses] Error: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({"error": str(e)})