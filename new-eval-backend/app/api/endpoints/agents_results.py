"""
Agent Results Retrieval Endpoints

Provides endpoints to fetch evaluator, judge, and reflection results
for a given session (and optionally thread) from Cosmos DB.
"""

from fastapi import APIRouter, HTTPException, Query
from services.cosmos_service import CosmosService
from typing import Optional

import logging

logger = logging.getLogger("agents_results")
router = APIRouter(prefix="", tags=["Agent Results"])

@router.get("/{session_id}")
async def get_all_agent_results(
    session_id: str,
    thread_id: Optional[str] = Query(None, description="Optional thread ID to filter results")
):
    """
    Fetch all agent results (evaluator, judge, reflection) for a session.
    Optionally filter by thread_id.
    """
    logger.info(f"[get_all_agent_results] Called with session_id={session_id}, thread_id={thread_id}")
    cosmos = CosmosService()
    results = {}

    for agent in ["evaluator", "judge", "reflection"]:
        logger.info(f"[get_all_agent_results] Fetching agent result for agent={agent}")
        agent_result = await cosmos.get_agent_result(session_id, agent, thread_id)
        if agent_result:
            logger.info(f"[get_all_agent_results] Found result for agent={agent}")
            results[agent] = agent_result.get("results", {})
        else:
            logger.warning(f"[get_all_agent_results] No result found for agent={agent}")
            results[agent] = None

    if not any(results.values()):
        logger.error(f"[get_all_agent_results] No agent results found for session_id={session_id}")
        raise HTTPException(status_code=404, detail="No agent results found for this session.")

    logger.info(f"[get_all_agent_results] Returning results for session_id={session_id}")
    return results

@router.get("/{session_id}/{agent}")
async def get_agent_result(
    session_id: str,
    agent: str,
    thread_id: Optional[str] = Query(None)
):
    """
    Fetch a specific agent's results (evaluator, judge, or reflection) for a session.
    Optionally filter by thread_id.
    """
    logger.info(f"[get_agent_result] Called with session_id={session_id}, agent={agent}, thread_id={thread_id}")
    if agent not in ["evaluator", "judge", "reflection"]:
        logger.error(f"[get_agent_result] Invalid agent type: {agent}")
        raise HTTPException(status_code=400, detail="Invalid agent type.")

    cosmos = CosmosService()
    result = await cosmos.get_agent_result(session_id, agent, thread_id)
    if not result:
        logger.warning(f"[get_agent_result] No results found for agent={agent} in session_id={session_id}")
        raise HTTPException(status_code=404, detail="No results found")
    return result