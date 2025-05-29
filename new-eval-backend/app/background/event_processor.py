"""
Event Processor
 
Receives aggregated async tasks via Azure Event Grid, runs the specified agent
(Evaluator, Judge, Reflection) on aggregated model responses, and explicitly
saves the results to Cosmos DB or relevant backend storage for later retrieval.
 
Explicitly removes SignalR dependency—results are persisted directly, frontend
retrieves via API polling or Cosmos DB queries.
 
Triggered explicitly by:
- eventgrid_consumer.py (POST /eventgrid)
 
Event Payload Structure:
{
    "agent": "evaluator" | "judge" | "reflection",
    "session_id": "abc123",
    "thread_id": "mcp-abc123",
    "use_case_id": "1" or "2",
    "prompt": "...",
    "responses": {
        "model_id_1": {"content": "...", "metrics": {...}},
        "model_id_2": {"content": "...", "metrics": {...}},
        ...
    },
    "timestamp": "2025-05-17T10:00:00Z"
}
"""
 
import logging
from typing import Dict, Any
from agents.evaluator_agent import EvaluatorAgent
from agents.judge_agent import JudgeAgent
from agents.reflection_agent import ReflectionAgent
from services.cosmos_service import CosmosService
import time
from types import SimpleNamespace  # Add this import for converting dicts to objects
 
logger = logging.getLogger(__name__)
cosmos = CosmosService.get_instance()

def convert_to_dict(obj):
    """Convert SimpleNamespace objects back to dictionaries for JSON serialization."""
    if isinstance(obj, SimpleNamespace):
        return {k: convert_to_dict(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_dict(i) for i in obj]
    else:
        return obj

async def process_agent_event(event: Dict[str, Any]):
    try:
        agent = event.get("agent")
        session_id = event.get("session_id")
        thread_id = event.get("thread_id")
        use_case_id = event.get("use_case_id")
        prompt = event.get("prompt")
        responses = event.get("responses")
 
        if not all([agent, session_id, thread_id, prompt, responses]):
            logger.warning(f"[EventProcessor] Missing fields in event: {event}")
            return
 
        logger.info(f"[EventProcessor] Processing aggregated '{agent}' for session '{session_id}'")
 
        aggregated_results = {}
 
        # Convert dictionaries to objects with attributes
        object_responses = {}
        for model_id, response_data in responses.items():
            if isinstance(response_data, dict):
                # Convert dict to object with attributes
                object_responses[model_id] = SimpleNamespace(**response_data)
            else:
                object_responses[model_id] = response_data
 
        if agent == "evaluator":
            evaluator = EvaluatorAgent()
            result = await evaluator.run(
                prompt=prompt,
                model_outputs=object_responses,  # Pass objects instead of dicts
                session_id=session_id
            )
            aggregated_results = result
 
        elif agent == "judge":
            judge = JudgeAgent()
            result = await judge.run(
                prompt=prompt,
                model_outputs=object_responses,  # Pass objects instead of dicts
                session_id=session_id
            )
            aggregated_results = result
 
        elif agent == "reflection":
            reflector = ReflectionAgent()
            for model_id, response_data in responses.items():
                # Access content from the object or dictionary
                content = ""
                if isinstance(response_data, dict):
                    content = response_data.get("content", "")
                else:
                    content = getattr(response_data, "content", "")
                    
                reflection_result = await reflector.run(
                    prompt=content,
                    model_id=model_id,
                    session_id=session_id,
                    mcp_thread_id=thread_id
                )
                aggregated_results[model_id] = reflection_result
 
        else:
            logger.warning(f"[EventProcessor] Unsupported agent type: {agent}")
            return
 
        # Fix container name to match what's in CosmosService
        cosmos_result = {
            "id": f"{agent}-{session_id}",
            "session_id": session_id,
            "thread_id": thread_id,
            "use_case_id": use_case_id,
            "agent": agent,
            "results": convert_to_dict(aggregated_results),
            "timestamp": event.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        }
        
        # Fix: Use agent_results_container instead of agents_results_container
        cosmos.agent_results_container.create_item(body=cosmos_result)
        logger.info(f"[EventProcessor] Results saved explicitly to CosmosDB for {agent}, session {session_id}")
 
        logger.info(f"[EventProcessor] Completed '{agent}' processing for session '{session_id}'")
 
    except Exception as e:
        logger.error(f"[EventProcessor] Exception during '{agent}' processing: {str(e)}", exc_info=True)

# ----------------- Utility Function (unchanged) -----------------
 
import httpx
from config import settings
 
async def send_agent_trigger_event(event_payload: Dict[str, Any]):
    """
    Sends custom aggregated events explicitly to Azure Event Grid to trigger agent processing.
    """
    topic_endpoint = settings.EVENT_GRID_TOPIC_ENDPOINT
    topic_key = settings.EVENT_GRID_TOPIC_KEY
    logger.info(f"[EventProcessor] Using Event Grid endpoint: {topic_endpoint}")
    logger.debug(f"[EventProcessor] EventGrid key prefix: {topic_key[:5]}...")
 
    headers = {
        "aeg-sas-key": topic_key,
        "Content-Type": "application/json"
    }
    wrapped_event = [
        {
            "id": event_payload.get("id", f"evt-{event_payload['agent']}-{event_payload['session_id']}"),
            "eventType": "AgentTrigger",
            "subject": f"/agents/{event_payload['agent']}",
            "eventTime": event_payload.get("timestamp"),
            "data": event_payload,
            "dataVersion": "1.0"
        }
    ]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(topic_endpoint, headers=headers, json=wrapped_event)
            response.raise_for_status()
            logger.info(f"[EventProcessor] Event Grid published for '{event_payload['agent']}', session '{event_payload['session_id']}'")
 
    except Exception as e:
        logger.warning(f"[EventProcessor] Event Grid publishing failed: {str(e)}")
        return False
 
    return True