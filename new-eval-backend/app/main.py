"""
Main FastAPI App Entry Point
 
- Initializes Semantic Kernel and services
- Registers all routers
- Configures CORS, startup checks
"""
 
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
 
from api import router
from services.semantic_kernel_service import SemanticKernelService
 
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
 
# FastAPI app instance
app = FastAPI(
    title="LLM Evaluation Backend",
    description="Multi-agent GenAI backend with MCP, Semantic Memory, and SignalR",
    version="1.0.0"
)
 
# Enable CORS (allow all origins for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
 
# Include API routes
app.include_router(router.router, prefix="/api")
 
@app.on_event("startup")
async def on_startup():
    """
    Initialize Semantic Kernel and test plugin loading
    """
    try:
        logger.info("[Startup] Initializing Semantic Kernel...")
        sk = SemanticKernelService.get_instance()
        await sk.initialize()
        logger.info("[Startup] Semantic Kernel initialized")
    except Exception as e:
        logger.error(f"[Startup] SK init failed: {str(e)}", exc_info=True)
 
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
 
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"[Error] Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
 
# Optional: local dev entry
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)