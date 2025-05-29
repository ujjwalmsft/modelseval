"""
compare.py
 
Main API endpoint for evaluating multiple LLMs explicitly.
 
Supports use cases explicitly:
1. Zero-shot (no context)
2. Context-aware (personalized)
 
Workflow explicitly:
- Run PlannerAgent to generate completions from selected models.
- Immediately save completions explicitly to Cosmos DB.
- Immediately return aggregated results explicitly via HTTP response.
- Trigger EvaluatorAgent, JudgeAgent, ReflectionAgent asynchronously via event processor explicitly (no SignalR).
"""
 
import logging
import uuid
import time
import re
from fastapi import APIRouter, HTTPException
from models.request import CompareRequest, CompareResponse, PlannerOutput
from agents.planner_agent import PlannerAgent
from services.cosmos_service import CosmosService
from services.semantic_kernel_service import SemanticKernelService
from background.event_processor import send_agent_trigger_event
 
router = APIRouter()
cosmos = CosmosService.get_instance()
sk_service = SemanticKernelService.get_instance()
logger = logging.getLogger(__name__)
 
def clean_think_tags(content: str) -> str:
    """Explicitly remove <think>...</think> blocks from model responses."""
    if not content:
        return ""
    cleaned = re.sub(r'<think>[\s\S]*?</think>', '', content)
    return cleaned.strip()
 
@router.post("/compare", response_model=CompareResponse)
async def compare_models(request: CompareRequest):
    """
    Handle evaluation requests explicitly for multiple LLMs without SignalR.
 
    Args:
        request (CompareRequest): Contains prompt, models, optional context.
 
    Returns:
        CompareResponse: Aggregated model responses explicitly via HTTP response.
    """
    try:
        # Explicit input validation
        if not request.prompt or not request.models:
            raise HTTPException(status_code=400, detail="Prompt and models are required.")
 
        # Explicit generation of session and MCP thread IDs
        session_id = request.session_id or str(uuid.uuid4())
        mcp_thread_id = request.mcp_thread_id or f"mcp-{session_id}"
        use_case_id = request.use_case_id or "1"
        context = request.context or ""
 
        full_prompt = f"{context}\n\n{request.prompt}" if use_case_id == "2" and context else request.prompt
        logger.info(f"[Compare] Session: {session_id}, MCP Thread: {mcp_thread_id}, Use Case: {use_case_id}")
 
        # Explicit PlannerAgent invocation
        planner = PlannerAgent()
        planner_output = await planner.run(
            prompt=full_prompt,
            models=request.models,
            session_id=session_id,
            mcp_thread_id=mcp_thread_id,
            system_prompt=request.system_prompt
        )
 
        aggregated_responses = {}
 
        # Explicitly aggregate and clean PlannerAgent responses
        for model_id, result in planner_output.items():
            cleaned_content = clean_think_tags(result.content)
            result.content = cleaned_content  # Update explicitly with cleaned content
            print(f"[Compare] Cleaned content for model {model_id}: {cleaned_content}")
            aggregated_responses[model_id] = PlannerOutput(
                model_id=model_id,
                content=cleaned_content,
                response_time=result.response_time,
                metrics=result.metrics,
                safety=result.safety
            )
 
            # UPDATED: Explicit Cosmos DB saving for THREAD container (uses mcp_thread_id)
            await cosmos.save_conversation_message(
                model_id=model_id,
                thread_id=mcp_thread_id,  # Changed from session_id to mcp_thread_id
                role="assistant",
                content=cleaned_content,
                token_count=result.metrics.get("totalTokens", 0)
            )
            print(f"[Compare] Saved response for model {model_id} to Cosmos DB threads container")
            
            # NEW: Explicit Cosmos DB saving for SESSION container
            try:
                await cosmos.save_session_metadata(
                    session_id=session_id,
                    metadata={
                        "model_id": model_id,  # Put model_id inside the metadata
                        "content": cleaned_content,
                        "role": "assistant", 
                        "timestamp": int(time.time()),
                        "token_count": result.metrics.get("totalTokens", 0),
                        "response_time": result.response_time,
                        "use_case_id": use_case_id
                    }
                )
                print(f"[Compare] Saved session data for model {model_id} to Cosmos DB sessionstorage container")
                logger.debug(f"[Compare] Saved session data for model {model_id} to sessionstorage container")
            except Exception as session_err:
                logger.error(f"[Compare] Failed to save session data: {str(session_err)}")
                
            # NEW: Call MemoryPlugin.save_conversation to generate and save embeddings
            try:
                # This will create and store embeddings in the vector container
                memory_result = await sk_service.run_plugin_function(
                    plugin_name="MemoryPlugin",
                    function_name="save_conversation",
                    parameters={
                        "model_id": model_id,
                        "conversation_id": mcp_thread_id,
                        "role": "assistant",
                        "content": cleaned_content,
                        "timestamp": str(int(time.time())),
                        "token_count": str(result.metrics.get("totalTokens", 0))
                    }
                )
                print(f"[Compare] Generated and saved embeddings for model {model_id}: {memory_result}")
                logger.info(f"[Compare] Generated and saved embeddings for model {model_id}")
            except Exception as embedding_err:
                logger.error(f"[Compare] Failed to save embeddings: {str(embedding_err)}")
 
        # Trigger Evaluator, Judge, Reflection agents explicitly via event processor
        event_payload = {
            "session_id": session_id,
            "thread_id": mcp_thread_id,
            "use_case_id": use_case_id,
            "prompt": full_prompt,
            "responses": {mid: resp.dict() for mid, resp in aggregated_responses.items()},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
 
        for agent in ["evaluator", "judge", "reflection"]:
            agent_payload = event_payload.copy()
            agent_payload["agent"] = agent
            await send_agent_trigger_event(agent_payload)
            logger.info(f"[Compare] Triggered {agent} agent explicitly for session {session_id}")
 
        # Explicit HTTP response with aggregated results
        return CompareResponse(
            session_id=session_id,
            mcp_thread_id=mcp_thread_id,
            use_case_id=use_case_id,
            responses=aggregated_responses
        )
 
    except Exception as e:
        logger.exception("[Compare] Evaluation failed explicitly")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")