"""
API Router
 
Wires all endpoint routes into FastAPI.
Central router for all FastAPI endpoints. This file registers:
- Compare endpoint (evaluation entry)
- Completion endpoint (LLM preview)
- Event Grid consumer (background agent triggers)
"""
 
from fastapi import APIRouter
from api.endpoints import compare, completion
from api.endpoints.eventgrid_consumer import router as eventgrid_router
from api.endpoints import signalr
from api.endpoints.agents_results import router as agents_results_router
router = APIRouter()
 
# Model comparison and evaluation
router.include_router(compare.router, prefix="/compare", tags=["compare"])

# Agent results retrieval
router.include_router(agents_results_router,tags=["Agent Results"])

# Direct model completions + streaming
router.include_router(completion.router, prefix="/completion", tags=["completion"])
 
# Azure Event Grid (POST events)
router.include_router(eventgrid_router, prefix="/eventgrid", tags=["eventgrid"])

router.include_router(signalr.router, prefix="/signalr", tags=["signalr"])

