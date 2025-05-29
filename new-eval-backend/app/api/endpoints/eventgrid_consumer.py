"""
Event Grid Consumer (Without SignalR)
 
Handles Azure Event Grid POST payloads explicitly, managing asynchronous processing of aggregated agent events.
 
Endpoint:
- POST /eventgrid
 
Functionalities explicitly included:
- Handles Azure Event Grid subscription validation explicitly.
- Delegates aggregated agent tasks clearly to `process_agent_event()` for async processing.
- Comprehensive logging and error handling explicitly added.
 
SignalR explicitly removed; agent results persisted directly to Cosmos DB.
"""
 
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from background.event_processor import process_agent_event
import logging
 
router = APIRouter()
logger = logging.getLogger(__name__)
 
@router.post("/eventgrid")
async def handle_eventgrid(request: Request):
    """
    Receives and explicitly processes aggregated events from Azure Event Grid.
 
    Expected Payload:
    - Subscription validation events (handled explicitly)
    - Aggregated agent tasks (Evaluator, Judge, Reflection), processed via `process_agent_event()`
    """
    try:
        body = await request.json()
        logger.info(f"[EventGridConsumer] Received payload: {body}")
 
        # Explicit subscription validation handling
        if isinstance(body, list) and body and body[0].get("eventType") == "Microsoft.EventGrid.SubscriptionValidationEvent":
            validation_code = body[0]["data"]["validationCode"]
            logger.info("[EventGridConsumer] Subscription validation event explicitly handled.")
            return JSONResponse(content={"validationResponse": validation_code})
 
        # Explicitly handle aggregated agent event payload
        events_processed = 0
        if isinstance(body, list):
            for event in body:
                data = event.get("data", {})
                await process_agent_event(data)
                events_processed += 1
                logger.info("[EventGridConsumer] Aggregated agent event explicitly processed (list item).")
        elif isinstance(body, dict):
            await process_agent_event(body.get("data", body))
            events_processed = 1
            logger.info("[EventGridConsumer] Aggregated agent event explicitly processed (dict item).")
 
        logger.info(f"[EventGridConsumer] Successfully processed {events_processed} event(s).")
 
        return {"status": "processed", "events_processed": events_processed}
 
    except Exception as e:
        logger.error(f"[EventGridConsumer] Error explicitly processing event: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))