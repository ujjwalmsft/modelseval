"""
MCP Protocol Schema
 
Defines standardized data models explicitly used across MCP thread-based agentic execution.
 
Explicitly includes:
- MCPRequest: Original payload sent explicitly to agents
- AggregatedMCPRequest: Clearly supports aggregated responses per session
- MCPResponse: Explicit generic agent response wrapper
- JudgeScore, EvaluationScore: Explicit detailed result schemas
- ReflectionRecord: Explicit semantic memory retrieval schema
- AgentEvent: Explicit Event Grid payload schema used by EventProcessor
"""
 
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List
 
 
class MCPRequest(BaseModel):
    """
    Original standardized agent invocation payload.
    """
    session_id: str
    mcp_thread_id: str
    model_id: str
    prompt: str
    response: Optional[str] = None
    use_case_id: str = "1"
    system_prompt: Optional[str] = None
    event_type: Optional[str] = None
 
 
class AggregatedModelResponse(BaseModel):
    """
    Explicit structure for individual model response within aggregated payload.
    """
    content: str
    metrics: Dict[str, Any]
 
 
class AggregatedMCPRequest(BaseModel):
    """
    New explicitly aggregated MCP request payload per session.
    Clearly used to trigger evaluation across multiple models simultaneously.
    """
    session_id: str
    mcp_thread_id: str
    prompt: str
    responses: Dict[str, AggregatedModelResponse]
    use_case_id: str = "1"
    system_prompt: Optional[str] = None
    event_type: Optional[str] = None
    timestamp: Optional[str] = None
 
 
class MCPResponse(BaseModel):
    """
    Generic agent response wrapper explicitly maintained.
    """
    status: str = "success"
    data: Dict[str, Any]
    duration: float
 
 
class JudgeScore(BaseModel):
    """
    Explicit qualitative scoring schema clearly maintained.
    """
    personalization: float
    relevance: float
    fluency: float
    coherence: float
    creativity: float
 
 
class EvaluationScore(BaseModel):
    """
    Explicit quantitative evaluation schema maintained.
    """
    BLEU: float = 0.0
    ROUGE_1: float = 0.0
    ROUGE_L: float = 0.0
    BERTScore: float = 0.0
    CosineSimilarity: float = 0.0
 
 
class ReflectionRecord(BaseModel):
    """
    Explicit schema for semantic memory retrieval records clearly retained.
    """
    id: str
    text: str
    similarity: float
    metadata: Dict[str, Any]
 
 
class AgentEvent(BaseModel):
    """
    Event Grid payload schema explicitly maintained.
    """
    event_type: str
    model_id: Optional[str] = None
    prompt: str
    response: Optional[str] = None
    responses: Optional[Dict[str, AggregatedModelResponse]] = None  # Aggregated responses explicitly added
    session_id: str
    mcp_thread_id: str
    use_case_id: Optional[str] = "1"
    timestamp: Optional[str] = None