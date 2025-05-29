"""
MCP Agent Server Endpoint
 
Provides a test/debug endpoint to invoke agents dynamically using MCPRequest schema.
 
Supported agent types:
- planner
- reflection
- evaluator
- judge
"""
 
import logging
from fastapi import APIRouter, HTTPException
from mcp.protocol import MCPRequest, MCPResponse
from agents.planner_agent import PlannerAgent
from agents.reflection_agent import ReflectionAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.judge_agent import JudgeAgent
 
logger = logging.getLogger(__name__)
router = APIRouter()
 
@router.post("/agentic/invoke", response_model=MCPResponse)
async def invoke_agent(request: MCPRequest):
    """
    Dynamically invoke an agent using MCP protocol.
    Intended for local testing or admin control panels.
    """
    try:
        agent_type = request.event_type or "planner"
        logger.info(f"[MCPServer] Invoking agent: {agent_type}")
 
        if agent_type == "planner":
            agent = PlannerAgent()
            data = await agent.run(
                models=[request.model_id],
                prompt=request.prompt,
                session_id=request.session_id,
                mcp_thread_id=request.mcp_thread_id,
                system_prompt=request.system_prompt,
                use_case_id=request.use_case_id
            )
 
        elif agent_type == "reflection":
            agent = ReflectionAgent()
            result = await agent.run(
                prompt=request.prompt,
                model_id=request.model_id,
                session_id=request.session_id,
                mcp_thread_id=request.mcp_thread_id
            )
            data = result.dict()
 
        elif agent_type == "evaluator":
            result = await EvaluatorAgent.run(
                prompt=request.prompt,
                response=request.response,
                model_id=request.model_id,
                session_id=request.session_id,
                mcp_thread_id=request.mcp_thread_id
            )
            data = result.dict()
 
        elif agent_type == "judge":
            agent = JudgeAgent()
            result = await agent.run(
                prompt=request.prompt,
                response=request.response,
                model_id=request.model_id,
                session_id=request.session_id,
                mcp_thread_id=request.mcp_thread_id,
                use_case_id=request.use_case_id
            )
            data = result.dict()
 
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
 
        return MCPResponse(
            status="success",
            data=data,
            duration=0.0  # (optional: include duration if needed)
        )
 
    except Exception as e:
        logger.error(f"[MCPServer] Agent invocation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))