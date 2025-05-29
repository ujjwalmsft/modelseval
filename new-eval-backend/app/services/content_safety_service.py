"""
Content Safety Service
 
Analyzes LLM responses for safety violations using Azure AI Content Safety.
 
Categories scored:
- Hate
- Sexual
- Violence
- Self-Harm
"""
 
import logging
import traceback
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from config import settings
 
logger = logging.getLogger(__name__)
 
class ContentSafetyService:
    def __init__(self):
        self.enabled = settings.AZURE_CONTENT_SAFETY_KEY and settings.AZURE_CONTENT_SAFETY_ENDPOINT
        self.client = None
 
        if self.enabled:
            try:
                self.client = ContentSafetyClient(
                    endpoint=settings.AZURE_CONTENT_SAFETY_ENDPOINT,
                    credential=AzureKeyCredential(settings.AZURE_CONTENT_SAFETY_KEY)
                )
                logger.info("[ContentSafety] Client initialized.")
            except Exception as e:
                logger.error(f"[ContentSafety] Initialization failed: {str(e)}")
                self.enabled = False
 
    def is_enabled(self) -> bool:
        return self.enabled
 
    async def analyze_text(self, text: str) -> dict:
        if not self.is_enabled():
            return {"enabled": False}
 
        try:
            options = AnalyzeTextOptions(text=text)
            response = self.client.analyze_text(options)
 
            return {
                "is_safe": max([
                    response.hate_result.severity if response.hate_result else 0,
                    response.sexual_result.severity if response.sexual_result else 0,
                    response.violence_result.severity if response.violence_result else 0,
                    response.self_harm_result.severity if response.self_harm_result else 0
                ]) < 4,
                "categories": {
                    "hate": response.hate_result.severity if response.hate_result else 0,
                    "sexual": response.sexual_result.severity if response.sexual_result else 0,
                    "violence": response.violence_result.severity if response.violence_result else 0,
                    "self_harm": response.self_harm_result.severity if response.self_harm_result else 0
                }
            }
 
        except Exception as e:
            logger.error(f"[ContentSafety] Text analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e), "is_safe": False}