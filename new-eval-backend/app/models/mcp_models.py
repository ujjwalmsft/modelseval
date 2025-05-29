"""
MCP Protocol-Based Models (Unified for all Agents)
 
Explicitly used for:
- Sending structured aggregated and individual requests to agents
- Returning consistent responses from agents explicitly
- Logging memory or background traces clearly
- Emitting aggregated Event Grid triggers explicitly
 
Supports explicitly: planner, reflection, evaluator, judge
"""
 
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
import time
 
def current_ts() -> int:
    """Returns current UNIX timestamp explicitly."""
    return int(time.time())
 
# 📨 Standard Message Envelope explicitly maintained
class MCPMessage(BaseModel):
    role: str                  # planner | reflection | evaluator | judge
    model_id: str
    mcp_thread_id: str
    session_id: str
    payload: Dict[str, Any]
    timestamp: int = Field(default_factory=current_ts)
 
# 📥 Explicit Incoming Agent Request explicitly maintained
class TaskRequest(BaseModel):
    event_type: str              # reflection | evaluator | judge
    model_id: Optional[str] = None
    prompt: str
    response: Optional[str] = None
    responses: Optional[Dict[str, Any]] = None  # Explicitly for aggregated handling
    session_id: str
    mcp_thread_id: str
    use_case_id: Optional[str] = "1"
 
# 📤 Explicit Agent Response model clearly maintained
class TaskResult(BaseModel):
    model_id: str
    mcp_thread_id: str
    agent: str                   # planner | reflection | evaluator | judge
    output: Dict[str, Any]
    latency_ms: Optional[float] = 0.0
    success: bool = True
    error: Optional[str] = None
 
# 🧠 Explicit Reflection Output schema explicitly maintained
class ReflectionResult(BaseModel):
    model_id: str
    thread_id: str
    insights: str
    matched_items: List[Dict[str, Any]]
    duration: float
    error: Optional[str] = None
 
# 🧪 Explicit Evaluation Output (Quantitative) schema explicitly maintained
class EvaluationResult(BaseModel):
    model_id: str
    thread_id: str
    BLEU: float = 0.0
    ROUGE_1: float = 0.0
    ROUGE_L: float = 0.0
    BERTScore: float = 0.0
    CosineSimilarity: float = 0.0
    duration: float = 0.0
    error: Optional[str] = None
 
# 🧑‍⚖️ Explicit Judge Output (Qualitative) schema explicitly maintained
class JudgeResult(BaseModel):
    model_id: str
    thread_id: str
    scores: Dict[str, float]
    reasons: Dict[str, str]
    raw_text: Optional[str] = None
    duration: float = 0.0
    error: Optional[str] = None
 
# 🧠 Explicit Planner Output schema clearly preserved
class PlannerOutput(BaseModel):
    model_id: str
    content: str
    response_time: float
    metrics: Dict[str, Any]
    safety: Optional[Dict[str, Any]] = None
 
# 🧠 Explicitly added Aggregated Planner Output schema
class AggregatedPlannerOutput(BaseModel):
    responses: Dict[str, PlannerOutput]
    session_id: str
    mcp_thread_id: str
    use_case_id: str = "1"
    timestamp: Optional[str] = None
 
# 🧾 Explicit Compare API Output schema explicitly updated and fixed
class CompareResponse(BaseModel):
    session_id: str
    mcp_thread_id: str
    use_case_id: str
    # Fixed explicitly: responses now clearly mapped to PlannerOutput schema
    responses: Dict[str, PlannerOutput]