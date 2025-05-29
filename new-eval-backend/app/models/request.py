"""
Compare Request and API Response Models
 
Defines explicitly:
- CompareRequest: User input schema for evaluating multiple LLMs.
- CompareResponse: Planner outputs explicitly aggregated per model.
 
Supports explicitly:
- Use Case 1: Zero-shot (no context provided)
- Use Case 2: Context-aware (user-provided context)
"""
 
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from models.mcp_models import PlannerOutput
 
# 📥 Compare Request Schema explicitly maintained
class CompareRequest(BaseModel):
    prompt: str = Field(..., description="The input prompt for the models.")
    models: List[str] = Field(
        default=["gpt4", "phi4", "llama", "gpt4nano"],
        description="List of model IDs explicitly selected for evaluation."
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system-level prompt explicitly guiding model behavior."
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Explicit session or user identifier."
    )
    mcp_thread_id: Optional[str] = Field(
        default=None,
        description="Explicit MCP context thread identifier."
    )
    use_case_id: Optional[str] = Field(
        default="1",
        description="Explicit use case: '1' = zero-shot, '2' = context-aware."
    )
    context: Optional[str] = Field(
        default=None,
        description="Explicit user-provided context or constraints for use case 2."
    )
 
# 📤 Compare Response Schema explicitly updated and aligned
class CompareResponse(BaseModel):
    session_id: str = Field(..., description="Session or user identifier explicitly maintained.")
    mcp_thread_id: str = Field(..., description="Explicit MCP context thread identifier.")
    use_case_id: str = Field(..., description="Explicitly indicating the use case executed ('1' or '2').")
    responses: Dict[str, PlannerOutput] = Field(
        ...,
        description="Explicitly aggregated PlannerOutput responses keyed by model_id."
    )