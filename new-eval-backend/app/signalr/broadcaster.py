import json
import logging
import time
import hmac
import base64
import hashlib
import urllib.parse
import httpx
from config import settings

logger = logging.getLogger(__name__)

class SignalRBroadcaster:
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'SignalRBroadcaster':
        """Get or create singleton instance of SignalRBroadcaster"""
        if cls._instance is None:
            cls._instance = SignalRBroadcaster()
        return cls._instance

    def __init__(self):
        """Initialize the SignalR broadcaster."""
        self.enabled = bool(settings.SIGNALR_CONNECTION_STRING and settings.SIGNALR_HUB_NAME)
        self.conn_string = settings.SIGNALR_CONNECTION_STRING
        self.hub_name = settings.SIGNALR_HUB_NAME
        
        # Parse connection string
        if self.enabled:
            try:
                conn_parts = self.conn_string.split(';')
                self.endpoint = next((p.split('=')[1] for p in conn_parts if p.startswith('Endpoint=')), '')
                self.key = next((p.split('=')[1] for p in conn_parts if p.startswith('AccessKey=')), '')
                
                if not self.endpoint or not self.key:
                    logger.error("[SignalR] Invalid connection string format")
                    self.enabled = False
                else:
                    # Remove any trailing slashes from endpoint
                    self.endpoint = self.endpoint.rstrip('/')
                    logger.info(f"[SignalR] Initialized with endpoint: {self.endpoint}")
            except Exception as e:
                logger.error(f"[SignalR] Initialization error: {str(e)}")
                self.enabled = False
        else:
            logger.warning("[SignalR] Not enabled (missing connection string or hub name)")

    def is_enabled(self) -> bool:
        return self.enabled

    def _generate_access_token(self) -> str:
        """Generate a shared access signature token for SignalR REST API."""
        expiry = int(time.time()) + 3600  # Token valid for 1 hour
        
        # Create the string to sign: {endpoint}\n{expiry}
        string_to_sign = f"{self.endpoint}\n{expiry}"
        
        # Create the signature
        key_bytes = base64.b64decode(self.key)
        hmac_obj = hmac.new(key_bytes, string_to_sign.encode('utf-8'), hashlib.sha256)
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        
        # URL encode the signature and endpoint
        encoded_signature = urllib.parse.quote(signature)
        encoded_endpoint = urllib.parse.quote(self.endpoint)
        
        # Format: SharedAccessSignature sr={url-encoded-resource}&sig={url-encoded-signature}&se={expiry}
        token = f"SharedAccessSignature sr={encoded_endpoint}&sig={encoded_signature}&se={expiry}"
        return token

    async def broadcast_message(self, group: str, data: dict, event_type: str = "update"):
        """
        Broadcast a message to all clients in a group.

        Args:
            group (str): Group name (typically session_id)
            data (dict): Payload to send
            event_type (str): Event label (e.g., "evaluator.result")
        """
        if not self.is_enabled():
            logger.warning("[SignalR] Broadcast attempted but SignalR is not enabled")
            return False

        try:
            # Format the message for WebPubSub
            message = {
                "event": event_type,
                "payload": data
            }
            
            # Format the endpoint URL correctly
            # Format: https://{service-name}.webpubsub.azure.com/api/hubs/{hub-name}/groups/{group-name}/messages
            service_domain = self.endpoint.replace("https://", "")
            url = f"{self.endpoint}/api/hubs/{self.hub_name}/groups/{group}/messages"
            
            # Generate the auth token
            auth_token = self._generate_access_token()
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": auth_token
            }
            
            # Debug information
            logger.info(f"[SignalR] Sending to URL: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"data": json.dumps(message)},
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200 or response.status_code == 202:
                    logger.info(f"[SignalR] Message broadcast to group: {group} | Event: {event_type}")
                    return True
                else:
                    logger.error(f"[SignalR] Broadcast failed with status {response.status_code}: {response.text}")
                    logger.error(f"[SignalR] Response headers: {response.headers}")
                    return False

        except Exception as e:
            logger.error(f"[SignalR] Broadcast failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def send_update(self, session_id: str, data: dict, event_type: str = "agent.update"):
        """Alias for broadcast_message with consistent naming"""
        return await self.broadcast_message(group=session_id, data=data, event_type=event_type)