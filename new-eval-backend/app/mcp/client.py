"""
MCP Client
 
Provides helper functions to invoke SK-compatible agents (Planner, Evaluator, Judge, Reflection)
using a standardized MCP thread context.
 
Responsibilities:
- Build KernelArguments with shared MCP fields
- Call Semantic Kernel plugins uniformly
- Return structured agent response
"""
 
import logging
from typing import Optional, Dict, Any
 
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel import Kernel
from services.semantic_kernel_service import SemanticKernelService
 
logger = logging.getLogger(__name__)
 
class MCPClient:
    def __init__(self):
        self.kernel: Kernel = SemanticKernelService.get_instance().kernel
 
    async def invoke_agent(
        plugin: str,
        function: str,
        model_id: str,
        prompt: str,
        response: Optional[str] = None,
        system_prompt: Optional[str] = None,
        mcp_thread_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
        additional_args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Invoke a Semantic Kernel plugin function under a given MCP context.
 
        Args:
            plugin (str): Plugin name (e.g., 'CompletionPlugin')
            function (str): Function name within plugin (e.g., 'run_completion')
            model_id (str): Target model
            prompt (str): Input prompt
            response (Optional[str]): Optional response (for evaluator/judge)
            system_prompt (Optional[str]): Optional system-level prompt
            mcp_thread_id (str): Shared thread ID
            temperature (float): Model temperature
            max_tokens (int): Max output tokens
            additional_args (dict): Any extra KernelArguments (e.g., metrics, scores)
 
        Returns:
            dict: JSON-parsed result from the agent plugin
        """
        try:
            args = KernelArguments({
                "prompt": prompt,
                "model_id": model_id,
                "deployment": model_id,
                "temperature": str(temperature),
                "max_tokens": str(max_tokens),
                "conversation_id": mcp_thread_id or f"{model_id}-{prompt[:10]}"
            })
 
            if response:
                args["response"] = response
            if system_prompt:
                args["system_prompt"] = system_prompt
 
            if additional_args:
                for k, v in additional_args.items():
                    args[k] = v
 
            logger.info(f"[MCPClient] Invoking {plugin}.{function} for model: {model_id}")
            result = await self.kernel.invoke_plugin_function_async(
                plugin_name=plugin,
                function_name=function,
                arguments=args
            )
 
            return result.json() if hasattr(result, 'json') else result
 
        except Exception as e:
            logger.error(f"[MCPClient] Error invoking {plugin}.{function}: {str(e)}")
            return {"error": str(e), "status": "failed"}