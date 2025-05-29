"""
App Configuration
 
Centralized config using environment variables (.env supported).
Includes:
- Azure credentials
- Cosmos DB & VectorDB
- Model deployments
- Embedding, safety, and SK plugin config
"""
 
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()  # Loads values from .env if available
 
class Settings(BaseSettings):
 
    # App core
    APP_NAME: str = "LLM Model Evaluation API"
    USE_SIMULATION: bool = os.getenv("USE_SIMULATION", "False").lower() == "true"
 
    # Azure OpenAI / AI Foundry
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
 
    # AI Foundry general config
    AI_FOUNDRY_OPENAI_ENDPOINT: str = os.getenv("AI_FOUNDRY_OPENAI_ENDPOINT", "")
    AI_FOUNDRY_OPENAI_KEY: str = os.getenv("AI_FOUNDRY_OPENAI_KEY", "")
    AI_FOUNDRY_MODEL_VERSION: str = os.getenv("AI_FOUNDRY_MODEL_VERSION", "2024-12-01-preview")

    # Model-specific endpoints
    LLAMA_AI_FOUNDRY_ENDPOINT: str = os.getenv("LLAMA_AI_FOUNDRY_ENDPOINT", "")
    LLAMA_AI_FOUNDRY_KEY: str = os.getenv("LLAMA_AI_FOUNDRY_KEY", "")
    PHI_AI_FOUNDRY_ENDPOINT: str = os.getenv("PHI_AI_FOUNDRY_ENDPOINT", "")
    PHI_AI_FOUNDRY_KEY: str = os.getenv("PHI_AI_FOUNDRY_KEY", "")
    DEEPSEEK_AI_FOUNDRY_ENDPOINT: str = os.getenv("DEEPSEEK_AI_FOUNDRY_ENDPOINT", "")
    DEEPSEEK_AI_FOUNDRY_KEY: str = os.getenv("DEEPSEEK_AI_FOUNDRY_KEY", "")
    
    # Model deployments
    GPT4_DEPLOYMENT: str = os.getenv("GPT4_DEPLOYMENT", "gpt-4")
    CLAUDE_DEPLOYMENT: str = os.getenv("CLAUDE_DEPLOYMENT", "claude-3")
    GEMINI_DEPLOYMENT: str = os.getenv("GEMINI_DEPLOYMENT", "gemini-pro")
    O1MINI_DEPLOYMENT: str = os.getenv("O1MINI_DEPLOYMENT", "gpt-4o-mini")
    PHI4_DEPLOYMENT: str = os.getenv("PHI4_DEPLOYMENT", "phi-4")
    LLAMA3_DEPLOYMENT: str = os.getenv("LLAMA3_DEPLOYMENT", "llama-3")
    GPT4_NANO_DEPLOYMENT: str = os.getenv("GPT4_NANO_DEPLOYMENT", "gpt-4.1-nano")
    DEEPSEEK_DEPLOYMENT: str = os.getenv("DEEPSEEK_DEPLOYMENT", "deepseek")
 
    # Cosmos DB (thread memory)
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    COSMOS_DATABASE: str = os.getenv("COSMOS_DATABASE", "llm-eval-db")
    COSMOS_CONTAINER: str = os.getenv("COSMOS_CONTAINER", "threads")
    COSMOS_VECTOR_CONTAINER: str = os.getenv("COSMOS_VECTOR_CONTAINER", "embeddings(semantic-memory)")
    COSMOS_VECTOR_ENABLED: bool = os.getenv("COSMOS_VECTOR_ENABLED", "true").lower() == "true"
    COSMOS_VECTOR_DIMENSIONS: int = int(os.getenv("COSMOS_VECTOR_DIMENSIONS", "1536"))
    COSMOS_VECTOR_SIMILARITY: str = os.getenv("COSMOS_VECTOR_SIMILARITY", "cosine")
    COSMOS_AGENT_RESULTS_CONTAINER: str = os.getenv("COSMOS_AGENT_RESULTS_CONTAINER", "agentsresults")
    COSMOS_SESSIONS_CONTAINER: str = os.getenv("COSMOS_SESSIONS_CONTAINER", "sessionstorage")
    
    # Embeddings
    EMBEDDING_MODEL_ID: str = os.getenv("EMBEDDING_MODEL_ID", "text-embedding-ada-002")
    EMBEDDING_DEPLOYMENT: str = os.getenv("EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    EMBEDDING_AZURE_ENDPOINT: str = os.getenv("EMBEDDING_AZURE_ENDPOINT", "")
    EMBEDDING_AZURE_API_KEY: str = os.getenv("EMBEDDING_AZURE_API_KEY", "")
    EMBEDDING_CHUNK_SIZE: int = int(os.getenv("EMBEDDING_CHUNK_SIZE", "1024"))
    EMBEDDING_CHUNK_OVERLAP: int = int(os.getenv("EMBEDDING_CHUNK_OVERLAP", "100"))
 
    # SignalR config (WebSocket)
    SIGNALR_CONNECTION_STRING: str = os.getenv("SIGNALR_CONNECTION_STRING", "")
    SIGNALR_HUB_NAME: str = os.getenv("SIGNALR_HUB_NAME", "evaluation")
 
    # Event Grid
    EVENT_GRID_TOPIC_ENDPOINT: str = os.getenv("EVENTGRID_TOPIC_ENDPOINT", "")
    EVENT_GRID_TOPIC_KEY: str = os.getenv("EVENT_GRID_TOPIC_KEY", "")
    EVENTGRID_TOPIC_NAME: str = os.getenv("EVENTGRID_TOPIC_NAME", "agent-events")
 
    AZURE_FUNC_NEGOTIATE_URL: str = os.getenv("AZURE_FUNC_NEGOTIATE_URL", "")

    # Azure AI Content Safety
    AZURE_CONTENT_SAFETY_ENDPOINT: str = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT", "")
    AZURE_CONTENT_SAFETY_KEY: str = os.getenv("AZURE_CONTENT_SAFETY_KEY", "")
 
    # Azure AI Search
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    AZURE_SEARCH_KEY: str = os.getenv("AZURE_SEARCH_KEY", "")
    AZURE_SEARCH_INDEX: str = os.getenv("AZURE_SEARCH_INDEX", "llm-rag-index")
 
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
 
    class Config:
        case_sensitive = True


# Initialize settings first
settings = Settings()

# Model-specific configuration
def get_model_config() -> Dict[str, Dict[str, Any]]:
    """
    Returns model-specific configuration including endpoints, API keys, and deployments.
    This is used for dynamic model selection in the Semantic Kernel service.
    """
    return {
        "llama": {
            "endpoint": settings.LLAMA_AI_FOUNDRY_ENDPOINT,
            "api_key": settings.LLAMA_AI_FOUNDRY_KEY,
            "deployment": settings.LLAMA3_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        },
        "phi4": {
            "endpoint": settings.PHI_AI_FOUNDRY_ENDPOINT,
            "api_key": settings.PHI_AI_FOUNDRY_KEY,
            "deployment": settings.PHI4_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        },
        "deepseek": {
            "endpoint": settings.DEEPSEEK_AI_FOUNDRY_ENDPOINT,
            "api_key": settings.DEEPSEEK_AI_FOUNDRY_KEY,
            "deployment": settings.DEEPSEEK_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        },
        # Default Azure OpenAI models
        "gpt4": {
            "endpoint": settings.AI_FOUNDRY_OPENAI_ENDPOINT,
            "api_key": settings.AI_FOUNDRY_OPENAI_KEY,
            "deployment": settings.GPT4_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        },
        "claude": {
            "endpoint": settings.AI_FOUNDRY_OPENAI_ENDPOINT,
            "api_key": settings.AI_FOUNDRY_OPENAI_KEY,
            "deployment": settings.CLAUDE_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        },
        "gemini": {
            "endpoint": settings.AI_FOUNDRY_OPENAI_ENDPOINT,
            "api_key": settings.AI_FOUNDRY_OPENAI_KEY, 
            "deployment": settings.GEMINI_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        },
        "o1mini": {
            "endpoint": settings.AI_FOUNDRY_OPENAI_ENDPOINT,
            "api_key": settings.AI_FOUNDRY_OPENAI_KEY,
            "deployment": settings.O1MINI_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        },
        "gpt4nano": {
            "endpoint": settings.AI_FOUNDRY_OPENAI_ENDPOINT,
            "api_key": settings.AI_FOUNDRY_OPENAI_KEY,
            "deployment": settings.GPT4_NANO_DEPLOYMENT,
            "api_version": settings.AI_FOUNDRY_MODEL_VERSION
        }
    }

# Default Azure OpenAI configuration
AZURE_OPENAI_CONFIG = {
    "endpoint": settings.AI_FOUNDRY_OPENAI_ENDPOINT,
    "api_key": settings.AI_FOUNDRY_OPENAI_KEY,
    "api_version": settings.AI_FOUNDRY_MODEL_VERSION
}

# Azure OpenAI embedding configuration
AZURE_EMBEDDING_CONFIG = {
    "endpoint": settings.EMBEDDING_AZURE_ENDPOINT or settings.AZURE_OPENAI_ENDPOINT,
    "api_key": settings.EMBEDDING_AZURE_API_KEY or settings.AZURE_OPENAI_API_KEY,
    "deployment": settings.EMBEDDING_DEPLOYMENT,
    "model_id": settings.EMBEDDING_MODEL_ID,
    "api_version": settings.AZURE_OPENAI_API_VERSION
}

# Initialize model configuration
AI_FOUNDRY_MODEL_CONFIG = get_model_config()