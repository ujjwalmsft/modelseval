"""
Evaluation Orchestrator
 
Acts explicitly as the central hub in the hybrid agentic evaluation workflow.
 
Responsibilities explicitly preserved and enhanced:
- Accepts an explicit evaluation request (CompareRequest).
- Explicitly generates MCP thread IDs if not provided.
- Invokes PlannerAgent explicitly to generate aggregated model completions.
- Explicitly publishes exactly one aggregated Event Grid event per agent:
    - ReflectionAgent
    - EvaluatorAgent
    - JudgeAgent
 
Explicitly designed NOT to block for asynchronous agent results.
"""
 
import uuid
import logging
import time
from typing import List, Dict, Optional, Tuple
from agents.planner_agent import PlannerAgent
from background.event_processor import send_agent_trigger_event
from models.mcp_models import PlannerOutput
 
logger = logging.getLogger(__name__)
 
class EvaluationOrchestrator:
    def __init__(self):
        """Initializes the orchestrator explicitly with a PlannerAgent instance."""
        self.planner = PlannerAgent()
        print(self.planner, 'PLANNER=>')
        logger.debug("[Orchestrator] PlannerAgent initialized successfully.")
 
    async def execute(
        self,
        models: List[str],
        prompt: str,
        session_id: str,
        system_prompt: Optional[str] = None,
        use_case_id: str = "1",
        mcp_thread_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, PlannerOutput]]:
        """
        Main orchestration entry point explicitly adjusted for aggregated evaluations.
 
        Args:
            models (List[str]): List of explicit model IDs to evaluate.
            prompt (str): Explicit user prompt for evaluation (with or without context).
            session_id (str): Explicit unique identifier for the current session.
            system_prompt (Optional[str]): Explicit optional system-level prompt context.
            use_case_id (str): Explicit evaluation mode: "1" (zero-shot) or "2" (context-aware).
            mcp_thread_id (Optional[str]): Explicit MCP thread identifier, generated if absent.
 
        Returns:
            Tuple[str, Dict[str, PlannerOutput]]:
                - MCP thread ID explicitly used in the evaluation.
                - Aggregated outputs explicitly from PlannerAgent for each model.
        """
        if not mcp_thread_id:
            mcp_thread_id = f"{session_id[:8]}-{uuid.uuid4().hex[:8]}"
            print(f"[Orchestrator] Generated MCP thread ID: {mcp_thread_id}")
            logger.debug(f"[Orchestrator] Explicitly generated MCP thread ID: {mcp_thread_id}")
 
        logger.info(f"[Orchestrator] Starting evaluation explicitly for session: {session_id}, thread: {mcp_thread_id}")
 
        # Step 1: Explicitly run PlannerAgent for aggregated completions
        try:
            planner_output = await self.planner.run(
                models=models,
                prompt=prompt,
                session_id=session_id,
                mcp_thread_id=mcp_thread_id,
                system_prompt=system_prompt,
                use_case_id=use_case_id
            )
            print(planner_output, 'PLANNEROUT=>')
            logger.debug(f"[Orchestrator] PlannerAgent output explicitly received: {planner_output}")
            logger.debug(f"[Orchestrator] PlannerAgent outputs explicitly received: {planner_output.keys()}")
        except Exception as e:
            logger.error(f"[Orchestrator] Error during PlannerAgent execution: {str(e)}")
            raise
 
        aggregated_responses = {
            model_id: {
                "content": output.content,
                "metrics": output.metrics
            } for model_id, output in planner_output.items()
        }
 
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"[Orchestrator] Aggregated responses explicitly prepared at {timestamp}")
        print(aggregated_responses, 'AGGREGATED=>')
        logger.debug(f"[Orchestrator] Aggregated responses explicitly prepared at {timestamp}")
 
        # Step 2: Explicitly publish one aggregated Event Grid event per agent
        for agent in ["reflection", "evaluator", "judge"]:
            event_payload = {
                "agent": agent,
                "session_id": session_id,
                "thread_id": mcp_thread_id,
                "use_case_id": use_case_id,
                "prompt": prompt,
                "responses": aggregated_responses,
                "timestamp": timestamp
            }
 
            try:
                await send_agent_trigger_event(event_payload)
                logger.info(f"[Orchestrator] Explicitly published event for agent '{agent}', session '{session_id}'")
            except Exception as e:
                logger.error(f"[Orchestrator] Failed to publish event explicitly for agent '{agent}': {str(e)}")
 
        return mcp_thread_id, planner_output