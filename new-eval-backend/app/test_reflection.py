"""
Agent Results Debug Test Script (Corrected and Aligned)
 
Explicitly designed to test and debug EvaluatorAgent, JudgeAgent, and ReflectionAgent individually.
Includes detailed debug print statements and inline documentation for full visibility and easy debugging.
 
Alignments:
- Corrected the argument mismatch explicitly for EvaluatorAgent (removed `thread_id`).
- Matched exact method signatures explicitly for EvaluatorAgent, JudgeAgent, and ReflectionAgent.
 
Usage:
- Explicitly run within your backend environment to validate agent functionalities.
"""
 
import asyncio
import logging
import json
from agents.evaluator_agent import EvaluatorAgent
from agents.judge_agent import JudgeAgent
from agents.reflection_agent import ReflectionAgent
from models.mcp_models import PlannerOutput
 
# Explicit setup for logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING) 
# Dummy Test Data explicitly for testing purposes
TEST_SESSION_ID = "test-session-001"
TEST_THREAD_ID = "test-thread-001"
TEST_PROMPT = "Explain quantum computing in simple terms."
 
TEST_MODEL_OUTPUTS = {
    "gpt4": PlannerOutput(
        model_id="gpt4",
        content="Quantum computing uses quantum bits to solve complex problems faster than classical computers.",
        response_time=1.2,
        metrics={"promptTokens": 10, "completionTokens": 20, "totalTokens": 30},
        safety=None
    ),
    "phi4": PlannerOutput(
        model_id="phi4",
        content="Quantum computing leverages quantum mechanics principles to process information differently from classical computers.",
        response_time=1.1,
        metrics={"promptTokens": 12, "completionTokens": 22, "totalTokens": 34},
        safety=None
    )
}
 
async def test_evaluator_agent():
    """
    Explicitly tests EvaluatorAgent without 'thread_id' argument (fixed as per error log).
    """
    logger.info("[EvaluatorAgent Test] Starting explicitly...")
    evaluator = EvaluatorAgent()
    result = await evaluator.run(
        prompt=TEST_PROMPT,
        model_outputs=TEST_MODEL_OUTPUTS,
        session_id=TEST_SESSION_ID
    )
    print("\n🟢 EvaluatorAgent Result:")
    for model_id, output in result.items():
        print(f"Model: {model_id}")
        print(json.dumps(output.metrics, indent=4))
 
async def test_judge_agent():
    """
    Explicitly tests JudgeAgent with correct parameters.
    """
    logger.info("[JudgeAgent Test] Starting explicitly...")
    judge = JudgeAgent()
    result = await judge.run(
        prompt=TEST_PROMPT,
        model_outputs=TEST_MODEL_OUTPUTS,
        session_id=TEST_SESSION_ID
    )
    print("\n🔵 JudgeAgent Result:")
    for model_id, output in result.items():
        print(f"Model: {model_id}")
        print(json.dumps(output.metrics.get("judgeScores", {}), indent=4))
 
async def test_reflection_agent():
    """
    Explicitly tests ReflectionAgent with correct parameters.
    """
    logger.info("[ReflectionAgent Test] Starting explicitly...")
    reflection = ReflectionAgent()
    result = await reflection.run(
        prompt=TEST_PROMPT,
        model_id="gpt4",
        session_id=TEST_SESSION_ID,
        mcp_thread_id=TEST_THREAD_ID,
        top_k=3,
        min_relevance=0.7
    )
    print("\n🟣 ReflectionAgent Result:")
    print(result if result else "[ReflectionAgent] No relevant memory found explicitly.")
 
async def main():
    """
    Main method explicitly executing each agent's test sequentially.
    """
    logger.info("[Debug Test] Explicitly running all agent tests sequentially...\n")
 
    try:
        await test_evaluator_agent()
    except Exception as e:
        logger.error(f"[EvaluatorAgent Test] Explicit error: {str(e)}")
 
    try:
        await test_judge_agent()
    except Exception as e:
        logger.error(f"[JudgeAgent Test] Explicit error: {str(e)}")
 
    try:
        await test_reflection_agent()
    except Exception as e:
        logger.error(f"[ReflectionAgent Test] Explicit error: {str(e)}")
 
    logger.info("\n✅ [Debug Test] All agent tests explicitly completed.")
 
if __name__ == "__main__":
    asyncio.run(main())