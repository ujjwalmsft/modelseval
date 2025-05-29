"""
SignalR Endpoint

Provides a negotiation endpoint for the frontend to establish
WebSocket connections with the Azure SignalR service.
"""

import logging
import time
import hmac
import base64
import hashlib
import urllib.parse
from fastapi import APIRouter, HTTPException, Depends
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/negotiate")
async def negotiate():
    """
    Generate a SignalR connection token for frontend clients.
    
    Returns:
        dict: Contains URL and access token for SignalR connection
    """
    if not settings.SIGNALR_CONNECTION_STRING:
        raise HTTPException(status_code=503, detail="SignalR not configured")
    
    try:
        # Parse the connection string
        conn_parts = settings.SIGNALR_CONNECTION_STRING.split(';')
        endpoint = next((p.split('=')[1] for p in conn_parts if p.startswith('Endpoint=')), '')
        key = next((p.split('=')[1] for p in conn_parts if p.startswith('AccessKey=')), '')
        
        if not endpoint or not key:
            raise ValueError("Invalid SignalR connection string format")
        
        # Create a signed token
        hub_name = settings.SIGNALR_HUB_NAME
        expiry = int(time.time()) + 3600  # 1 hour from now
        
        # Construct the string to sign
        string_to_sign = f"{endpoint}\n{expiry}"
        
        # Create signature
        key_bytes = base64.b64decode(key)
        hmac_obj = hmac.new(key_bytes, string_to_sign.encode(), hashlib.sha256)
        signature = base64.b64encode(hmac_obj.digest()).decode()
        
        # Create the token URL
        token = {
            'url': f"{endpoint}/client/?hub={hub_name}",
            'accessToken': f"SharedAccessSignature sr={urllib.parse.quote_plus(endpoint)}&sig={urllib.parse.quote_plus(signature)}&se={expiry}"
        }
        
        logger.info("[SignalR] Negotiation successful")
        return token
        
    except Exception as e:
        logger.error(f"[SignalR] Negotiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SignalR negotiation failed: {str(e)}")