"""
Semantic Kernel Service for AI orchestration.

Provides a centralized service for interacting with Microsoft Semantic Kernel,
managing plugins, and executing AI operations through a unified interface.
"""

import logging
import os
import sys
import importlib.util
import inspect
import traceback
from typing import Dict, Any, List, Optional, Union, Callable, Set, AsyncGenerator
import json
import time
import semantic_kernel as sk
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from semantic_kernel.functions.kernel_arguments import KernelArguments

from config import settings

# Configure logging
logger = logging.getLogger(__name__)

class SemanticKernelService:
    """
    Singleton service for Semantic Kernel integration throughout the application.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'SemanticKernelService':
        """Get or create the singleton instance of SemanticKernelService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the Semantic Kernel service."""
        if SemanticKernelService._instance is not None:
            raise RuntimeError("Use get_instance() to get the singleton instance")
            
        self.kernel = Kernel()
        self.initialized = False
        self.loaded_plugins: Set[str] = set()
        # Store functions directly for execution
        self.plugin_functions: Dict[str, Dict[str, Callable]] = {}
        
        logger.info("Semantic Kernel service initialized (not yet loaded)")
    
    async def initialize(self) -> None:
        """Initialize Semantic Kernel and load plugins."""
        if self.initialized:
            logger.info("Semantic Kernel already initialized")
            return
 
        logger.info("[SK] Initializing Semantic Kernel service...")
        
        # Configure chat completion service from Azure AI Foundry
        if hasattr(settings, 'AI_FOUNDRY_OPENAI_ENDPOINT') and settings.AI_FOUNDRY_OPENAI_ENDPOINT:
            # Azure AI Foundry for chat completion
            self.kernel.add_service(
                AzureChatCompletion(
                    service_id="chat_completion",
                    deployment_name=settings.O1MINI_DEPLOYMENT,
                    endpoint=settings.AI_FOUNDRY_OPENAI_ENDPOINT,
                    api_key=settings.AI_FOUNDRY_OPENAI_KEY,
                    api_version=settings.AI_FOUNDRY_MODEL_VERSION
                )
            )
            logger.info(f"Added Azure AI Foundry chat service with deployment: {settings.O1MINI_DEPLOYMENT}")
        
        # Configure embedding service from Azure OpenAI
        if hasattr(settings, 'EMBEDDING_AZURE_ENDPOINT') and settings.EMBEDDING_AZURE_ENDPOINT:
            # Fixed: Using correct method for SK 1.28.1
            self.kernel.add_service(
                AzureTextEmbedding(
                    service_id="embedding",
                    deployment_name=settings.EMBEDDING_DEPLOYMENT,
                    endpoint=settings.EMBEDDING_AZURE_ENDPOINT,
                    api_key=settings.EMBEDDING_AZURE_API_KEY,
                    api_version="2023-05-15"
                )
            )
            logger.info(f"Added Azure OpenAI embedding service with deployment: {settings.EMBEDDING_DEPLOYMENT}")
        else:
            logger.warning("Azure OpenAI embedding endpoint not configured, embeddings will not be available")
        
        # Load plugins from directories
        await self._load_plugins()
        
        self.initialized = True
        logger.info(f"[SK] Semantic Kernel initialized with {len(self.loaded_plugins)} plugins")
    
    async def _load_plugins(self) -> None:
        """Discover and load all available plugins."""
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
        
        if not os.path.exists(plugins_dir):
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return
            
        # Get all directories in the plugins directory (each is a potential plugin)
        plugin_dirs = [d for d in os.listdir(plugins_dir) 
                    if os.path.isdir(os.path.join(plugins_dir, d)) and not d.startswith('__')]
        
        for plugin_name in plugin_dirs:
            try:
                plugin_path = os.path.join(plugins_dir, plugin_name)
                functions_added = 0
                
                # Create a map of functions for this plugin
                plugin_functions = {}
                
                # Find all Python files in the plugin directory that might contain functions
                for file in os.listdir(plugin_path):
                    if file.endswith(".py") and not file.startswith("__"):
                        module_name = f"app.plugins.{plugin_name}.{file[:-3]}"  # Use proper module naming
                        file_path = os.path.join(plugin_path, file)
                        
                        try:
                            # Load module dynamically
                            spec = importlib.util.spec_from_file_location(module_name, file_path)
                            if spec is None:
                                logger.warning(f"Could not load spec for {module_name}")
                                continue
                                
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = module  # Add to sys.modules to avoid reload issues
                            
                            spec.loader.exec_module(module)
                            print(f"Loaded module {module_name}")
                            logger.debug(f"Loaded module {module_name}")
                            
                            # Find all functions in the module with kernel_function decorator
                            for name, obj in inspect.getmembers(module):
                                # Filter for just functions that don't start with underscore
                                if inspect.isfunction(obj) and not name.startswith("_"):
                                    # Add function to our map
                                    plugin_functions[name] = obj
                                    functions_added += 1
                                    logger.debug(f"Added function {name} to {plugin_name}")
                        
                        except Exception as module_error:
                            logger.error(f"Error loading module {module_name}: {str(module_error)}")
                            logger.error(traceback.format_exc())
                            continue
                
                # If no functions found, continue to next plugin
                if functions_added == 0:
                    logger.warning(f"No kernel functions found in plugin: {plugin_name}")
                    continue
                
                # Store the plugin functions
                self.plugin_functions[plugin_name] = plugin_functions
                self.loaded_plugins.add(plugin_name)
                
                logger.info(f"Loaded plugin: {plugin_name} with {functions_added} functions")
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
                logger.error(traceback.format_exc())

    async def chat_completion(
        self,
        model_id: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Execute a chat completion request with the given model.
        
        Args:
            model_id: The ID of the model to use (e.g., "gpt4")
            messages: List of message objects with "role" and "content" keys
            temperature: Temperature setting for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Completion text response
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            # We'll use run_plugin_function with CompletionPlugin.run_completion
            # but adapt it to work with messages format
            
            # Convert messages to a prompt format
            system_content = ""
            user_content = ""
            
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                elif msg["role"] == "user":
                    user_content += f"{msg['content']}\n"
            
            parameters = {
                "prompt": user_content.strip(),
                "model_id": model_id,
                "system_prompt": system_content,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response_str = await self.run_plugin_function(
                plugin_name="CompletionPlugin",
                function_name="run_completion",
                parameters=parameters
            )
            
            return response_str
            # try:
            #     response_json = json.loads(response_str)
            #     return response_json.get("content", response_str)
            # except json.JSONDecodeError:
            #     return response_str
                
        except Exception as e:
            logger.error(f"[SemanticKernelService] Error in chat_completion: {str(e)}")
            logger.error(traceback.format_exc())
            return f"Error: {str(e)}"



    async def run_plugin_function(self,
                                plugin_name: str,
                                function_name: str,
                                parameters: Dict[str, Any]) -> str:
        """
        Run a plugin function with the given parameters, dynamically selecting
        the appropriate endpoint based on the model_id parameter.
        """
        from config import AI_FOUNDRY_MODEL_CONFIG

        
        if not self.initialized:
           await self.initialize()
        
        try:
            # Extract model_id from parameters
            model_id = parameters.get("model_id", "").lower()
            logger.info(f"[SemanticKernelService] Running {plugin_name}.{function_name} for model: {model_id}")
            
            # Check if this is a model with a specific AI Foundry endpoint
            model_config = AI_FOUNDRY_MODEL_CONFIG.get(model_id)
            
            # If the model has specific configuration and we're running a completion
            if model_config and plugin_name == "CompletionPlugin" and function_name == "run_completion":
                # Extract parameters
                prompt = parameters.get("prompt", "")
                system_prompt = parameters.get("system_prompt", "You are a helpful assistant.")
                temperature = float(parameters.get("temperature", 0.7))
                max_tokens = int(parameters.get("max_tokens", 2000))
                conversation_id = parameters.get("conversation_id", f"{model_id}-{time.time()}")
                
                # Log the endpoint we're using
                logger.info(f"[SemanticKernelService] Using model-specific endpoint for {model_id}: {model_config['endpoint']}")
                
                start_time = time.time()
                content = ""  # Default empty content
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0
                
                # Use different clients for different model types
                if model_id in ["llama", "phi4", "deepseek"]:
                    # Use Azure AI Inference client for AI Foundry models
                    try:
                        from azure.ai.inference import ChatCompletionsClient
                        from azure.ai.inference.models import SystemMessage, UserMessage
                        from azure.core.credentials import AzureKeyCredential
                        
                        client = ChatCompletionsClient(
                            endpoint=model_config["endpoint"],
                            credential=AzureKeyCredential(model_config["api_key"])
                        )
                        
                        messages = [
                            SystemMessage(content=system_prompt),
                            UserMessage(content=prompt)
                        ]
                        
                        logger.info(f"[SemanticKernelService] Sending request to {model_id} with prompt: {prompt[:100]}...")
                        
                        response = client.complete(
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            model=model_config["deployment"]
                        )
                        
                        content = response.choices[0].message.content
                        
                        # Print the full response for debugging
                        logger.info(f"[SemanticKernelService] {model_id.upper()} RESPONSE: {content}")
                        
                        # AI Inference doesn't provide usage stats directly like OpenAI
                        # Estimate token usage based on length
                        prompt_tokens = len(prompt) // 4
                        completion_tokens = len(content) // 4
                        total_tokens = prompt_tokens + completion_tokens
                        
                    except Exception as e:
                        logger.error(f"[SemanticKernelService] AI Foundry error for {model_id}: {str(e)}")
                        logger.error(traceback.format_exc())
                        content = f"Error with {model_id}: {str(e)}"
                        
                else:
                    # Use AzureOpenAI client for standard Azure OpenAI models
                    try:
                        from openai import AzureOpenAI
                        
                        client = AzureOpenAI(
                            api_key=model_config["api_key"],
                            api_version=model_config["api_version"],
                            azure_endpoint=model_config["endpoint"]
                        )
                        
                        messages = [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                        
                        logger.info(f"[SemanticKernelService] Sending request to {model_id} with prompt: {prompt[:100]}...")
                        
                        response = client.chat.completions.create(
                            model=model_config["deployment"],
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        
                        content = response.choices[0].message.content
                        
                        # Print the full response for debugging
                        logger.info(f"[SemanticKernelService] {model_id.upper()} RESPONSE: {content}")
                        
                        prompt_tokens = response.usage.prompt_tokens
                        completion_tokens = response.usage.completion_tokens
                        total_tokens = response.usage.total_tokens
                        
                    except Exception as e:
                        logger.error(f"[SemanticKernelService] Azure OpenAI error for {model_id}: {str(e)}")
                        logger.error(traceback.format_exc())
                        content = f"Error with {model_id}: {str(e)}"
                
                latency = time.time() - start_time
                
                # Create result format matching run_completion_function output
                result = {
                    "content": content,
                    "model": model_id,
                    "metrics": {
                        "responseTime": latency,
                        "promptTokens": prompt_tokens,
                        "completionTokens": completion_tokens,
                        "totalTokens": total_tokens
                    },
                    "safety": {},
                    "id": conversation_id
                }
                
                # Save to memory (optional - similar to what run_completion would do)
                from services.cosmos_service import CosmosService
                cosmos = CosmosService.get_instance()
                await cosmos.save_conversation_message(
                    model_id=model_id,
                    thread_id=conversation_id,
                    role="user",
                    content=prompt,
                    token_count=prompt_tokens
                )
                await cosmos.save_conversation_message(
                    model_id=model_id,
                    thread_id=conversation_id,
                    role="assistant",
                    content=content,
                    token_count=completion_tokens
                )
                
                return json.dumps(result)
                
            else:
                # For other plugins or non-configured models, use the standard method
                if not plugin_name in self.plugin_functions or not function_name in self.plugin_functions[plugin_name]:
                    raise ValueError(f"Plugin function {plugin_name}.{function_name} not found")
                    
                function = self.plugin_functions[plugin_name][function_name]
                
                # Convert dict to KernelArguments
                from semantic_kernel.functions.kernel_arguments import KernelArguments
                kernel_args = KernelArguments(**parameters)
                
                # Execute the function
                result = await function(kernel_args)
                return result
                
        except Exception as e:
            logger.error(f"[SemanticKernelService] Error in run_plugin_function: {str(e)}")
            logger.error(traceback.format_exc())
            return json.dumps({"error": str(e), "content": f"Error: {str(e)}"})
        
    async def run_batch_completions(
        self,
        prompt: str,
        models: List[str],
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute batch completions explicitly for multiple models.
 
        Args:
            prompt: User-provided prompt.
            models: List of model identifiers.
            system_prompt: Optional system prompt.
            temperature: Generation temperature.
            max_tokens: Maximum token limit.
            session_id: Session identifier for logging.
 
        Returns:
            Aggregated model responses explicitly.
        """
        if not self.initialized:
            await self.initialize()
 
        aggregated_results = {}
        for model_id in models:
            logger.info(f"[SKService] Batch completion for model '{model_id}'")
            parameters = {
                "prompt": prompt,
                "model_id": model_id,
                "system_prompt": system_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "conversation_id": session_id or f"{model_id}-{int(time.time())}"
            }
            response_str = await self.run_plugin_function(
                plugin_name="CompletionPlugin",
                function_name="run_completion",
                parameters=parameters
            )
            try:
                response_json = json.loads(response_str)
            except json.JSONDecodeError:
                response_json = {"content": response_str}
 
            aggregated_results[model_id] = response_json
 
            # Save to Cosmos DB
            await self.cosmos.save_conversation_message(
                model_id=model_id,
                thread_id=parameters["conversation_id"],
                role="assistant",
                content=response_json.get("content", ""),
                token_count=response_json.get("metrics", {}).get("totalTokens", 0)
            )
 
        return aggregated_results   
    
         
    async def _execute_plugin_function(self, kernel, plugin_name: str, function_name: str, parameters: Dict[str, Any]) -> str:
        """Internal method to execute a plugin function with the given kernel."""
        try:
            # Get the plugin function
            if plugin_name not in self.plugin_functions or function_name not in self.plugin_functions[plugin_name]:
                raise ValueError(f"Plugin function {plugin_name}.{function_name} not found")
            
            # Convert parameters to KernelArguments if needed
            from semantic_kernel.orchestration.kernel_arguments import KernelArguments
            if not isinstance(parameters, KernelArguments):
                parameters = KernelArguments(**parameters)
            
            # Try various SK API versions
            try:
                # Semantic Kernel 1.x API style
                result = await kernel.invoke_skill_async(
                    skill_name=plugin_name,
                    function_name=function_name,
                    parameters=parameters
                )
            except (AttributeError, TypeError):
                try:
                    # Semantic Kernel 0.4.x API style
                    result = await kernel.invoke_async(
                        plugin_name,
                        function_name,
                        parameters
                    )
                except (AttributeError, TypeError):
                    # Semantic Kernel older API style
                    result = await kernel.invoke_function_async(
                        skill_name=plugin_name,
                        function_name=function_name,
                        arguments=parameters
                    )
            
            # Handle result types that might come back
            if hasattr(result, "result"):  # SKFunctionResult type
                return result.result
            elif hasattr(result, "value"):   # Some SK versions return object with .value
                return result.value
            else:
                # Just return as string
                return str(result)
                
        except Exception as e:
            logger.error(f"Error executing plugin function: {str(e)}")
            logger.error(traceback.format_exc())
            return f"Error: {str(e)}"


    async def run_streaming_function(self,
                                  plugin_name: str,
                                  function_name: str,
                                  parameters: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Execute a streaming plugin function and yield results.
        
        Args:
            plugin_name: Name of the plugin to use
            function_name: Name of the function to call
            parameters: Dictionary of parameters to pass to the function
            
        Yields:
            Streaming results from the function
        """
        # Make sure kernel is initialized
        if not self.initialized:
            await self.initialize()
        
        # Check if plugin is loaded
        if plugin_name not in self.loaded_plugins:
            yield f"Error: Plugin '{plugin_name}' not found"
            return
        
        try:
            # Check if function exists in the plugin
            if plugin_name not in self.plugin_functions:
                yield f"Error: Plugin '{plugin_name}' functions not found"
                return
                
            if function_name not in self.plugin_functions[plugin_name]:
                yield f"Error: Function '{function_name}' not found in plugin '{plugin_name}'"
                return
                
            # Get the function directly
            function = self.plugin_functions[plugin_name][function_name]
            
            # Create kernel arguments from parameters dict
            kernel_args = KernelArguments(**parameters)
            
            # Execute the streaming function
            if not inspect.isasyncgenfunction(function):
                yield f"Error: Function '{function_name}' is not a streaming function"
                return
                
            async for chunk in function(kernel_args):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error executing streaming function {plugin_name}.{function_name}: {str(e)}")
            logger.error(traceback.format_exc())
            yield f"Error: {str(e)}"
    
    async def list_plugins(self) -> List[str]:
        """Get a list of all loaded plugins."""
        if not self.initialized:
            await self.initialize()
                
        return list(self.loaded_plugins)

    async def list_plugin_functions(self, plugin_name: str) -> List[str]:
        """Get a list of all functions in a plugin."""
        if not self.initialized:
            await self.initialize()
                
        if plugin_name not in self.plugin_functions:
            return []
            
        return list(self.plugin_functions[plugin_name].keys())

    async def get_semantic_kernel_version(self) -> str:
        """Return the version of semantic_kernel package."""
        import semantic_kernel
        return semantic_kernel.__version__
        
    async def run_llm_prompt(self, 
                        prompt: str, 
                        system_prompt: Optional[str] = None,
                        temperature: float = 0.7,
                        max_tokens: int = 500) -> str:
        """
        Run a prompt through the configured LLM.
        
        Args:
            prompt: User prompt to send to the LLM
            system_prompt: Optional system prompt for the LLM
            temperature: Temperature for generation (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response as a string
        """
        # Make sure kernel is initialized
        if not self.initialized:
            await self.initialize()
        
        try:
            # Set up execution settings
            execution_settings = {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.95
            }
            
            # Create arguments
            kernel_args = KernelArguments(
                execution_settings=execution_settings
            )
            
            # Set system and user messages
            if system_prompt:
                kernel_args["system_prompt"] = system_prompt
                
            # Run the prompt
            result = await self.kernel.invoke_prompt(
                prompt=prompt,
                arguments=kernel_args
            )
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error running LLM prompt: {str(e)}")
            logger.error(traceback.format_exc())
            return f"Error: {str(e)}"
            
    async def initialize_if_needed(self) -> None:
        """Initialize the service if not already initialized."""
        if not self.initialized:
            await self.initialize()