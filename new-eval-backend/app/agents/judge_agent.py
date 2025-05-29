"""
JudgeAgent.py
 
Purpose:
- Performs explicit qualitative evaluation of model responses using GPT-4o.
- Assesses attributes explicitly: personalization, relevance, fluency, coherence, creativity.
 
Inputs:
- prompt (str): Original user query.
- model_outputs (Dict[str, PlannerOutput]): Model responses.
 
Outputs:
- Updates model_outputs explicitly with qualitative metrics under:
  model_outputs[model_id].metrics["judgeScores"]
 
Updates:
- Improved parsing logic explicitly expects structured JSON output from GPT-4o.
"""
 
import logging
import json
import re
from typing import Dict, Any
from models.mcp_models import PlannerOutput
from services.semantic_kernel_service import SemanticKernelService
from config import settings
 
logger = logging.getLogger(__name__)
 
class JudgeAgent:
    def __init__(self):
        self.sk = SemanticKernelService.get_instance()
        self.model_id = settings.GPT4_DEPLOYMENT or "gpt4"
 
    async def run(
        self,
        prompt: str,
        model_outputs: Dict[str, PlannerOutput],
        session_id: str
    ) -> Dict[str, PlannerOutput]:
        """
        Explicitly perform qualitative evaluation using structured JSON parsing.
 
        Args:
            prompt (str): Original prompt explicitly provided.
            model_outputs (Dict[str, PlannerOutput]): Model response objects.
 
        Returns:
            Dict[str, PlannerOutput]: Model outputs explicitly updated with qualitative judge scores.
        """
        logger.info(f"[JudgeAgent] Starting qualitative evaluation explicitly with {self.model_id} (No SignalR).")
 
        try:
            user_prompt = self._build_user_prompt(prompt, model_outputs)
 
            messages = [
                {"role": "system", "content": "You are an expert evaluator of LLM outputs. Respond ONLY with structured JSON."},
                {"role": "user", "content": user_prompt}
            ]
 
            result_obj = await self.sk.chat_completion(
                model_id=self.model_id,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
 
            logger.info(f"[JudgeAgent] Raw GPT-4o evaluation response type: {type(result_obj)}")
            print(f"[JudgeAgent] Raw GPT-4o response type: {type(result_obj)}")
            
            # Only log a portion of the result to avoid cluttering the logs
            if isinstance(result_obj, dict):
                log_sample = {k: v[:200] + "..." if isinstance(v, str) and len(v) > 200 else v 
                             for k, v in result_obj.items()}
                logger.info(f"[JudgeAgent] Response sample: {log_sample}")
                print(f"[JudgeAgent] Response keys: {result_obj.keys()}")
            
            # And then pass the result object directly:
            parsed_scores = self._extract_scores(result_obj)
            
            logger.info(f"[JudgeAgent] Parsed qualitative scores: {parsed_scores}")
            print(f"[JudgeAgent] Parsed qualitative scores: {parsed_scores}")
 
            # Update model_outputs explicitly with judge scores
            for model_id, judge_data in parsed_scores.items():
                if model_id in model_outputs:
                    model_outputs[model_id].metrics["judgeScores"] = judge_data
                    logger.info(f"[JudgeAgent] Qualitative scores explicitly updated for model '{model_id}'")
                    print(f"[JudgeAgent] Processed scores for model '{model_id}': {judge_data}")
 
            logger.info(f"[JudgeAgent] Qualitative evaluation explicitly completed for {len(parsed_scores)} models.")
 
        except Exception as e:
            logger.error(f"[JudgeAgent] Explicit qualitative evaluation failed: {str(e)}", exc_info=True)
            print(f"[JudgeAgent] CRITICAL ERROR: {str(e)}")
 
        return model_outputs
 
    def _build_user_prompt(self, prompt: str, model_outputs: Dict[str, PlannerOutput]) -> str:
        """
        Constructs explicit evaluation prompt for GPT-4o.
 
        Returns:
            str: Explicit evaluation prompt.
        """
        user_prompt = f"Evaluate the following responses to the prompt:\n\nPrompt:\n{prompt}\n\n"
        for model_id, output in model_outputs.items():
            user_prompt += f"Response from {model_id}:\n{output.content.strip()}\n\n"
 
        user_prompt += (
            "Provide explicit JSON ratings for each response with numerical scores (1-10) and brief reasons:\n"
            "{\n"
            "  \"model_id\": {\n"
            "    \"personalization\": score,\n"
            "    \"relevance\": score,\n"
            "    \"fluency\": score,\n"
            "    \"coherence\": score,\n"
            "    \"creativity\": score,\n"
            "    \"reasons\": {\n"
            "      \"personalization\": \"reason\",\n"
            "      \"relevance\": \"reason\",\n"
            "      \"fluency\": \"reason\",\n"
            "      \"coherence\": \"reason\",\n"
            "      \"creativity\": \"reason\"\n"
            "    }\n"
            "  },\n"
            "  ...\n"
            "}"
        )
        return user_prompt
    
    def _clean_json_string(self, json_str: str) -> str:
        """
        Aggressively cleans a JSON string to make it parseable.
        
        Args:
            json_str: The raw JSON string that might have formatting issues
            
        Returns:
            A cleaned JSON string ready for parsing
        """
        # Display the original string for debugging
        print(f"[DEBUG] Original JSON string sample: '{json_str[:50]}...'")
        print(f"[DEBUG] Original string length: {len(json_str)}")
        
        # First, remove any BOM or invisible characters at the beginning
        if json_str and len(json_str) > 0:
            # Print the first few characters for debugging
            print(f"[DEBUG] First 5 chars as hex: {' '.join([hex(ord(c)) for c in json_str[:5]])}")
            
            # Check for BOM or other invisible markers
            if ord(json_str[0]) > 127 or json_str[0].isspace():
                print(f"[DEBUG] Removing first character: hex {hex(ord(json_str[0]))}")
                json_str = json_str[1:]
        
        # Aggressive whitespace cleanup
        json_str = json_str.strip()
        print(f"[DEBUG] After strip: '{json_str[:50]}...'")
        
        # CRITICAL FIX: Unescape the string to convert \n to actual newlines and \" to actual quotes
        print(f"[DEBUG] Before unescaping, first 10 chars: {[c for c in json_str[:10]]}")
        try:
            # This is the key fix: Convert escape sequences to actual characters
            json_str = json_str.encode().decode('unicode_escape')
            print(f"[DEBUG] After unescaping, string starts with: '{json_str[:50]}...'")
            print(f"[DEBUG] After unescaping, first 10 chars: {[c for c in json_str[:10]]}")
        except Exception as e:
            print(f"[DEBUG] Unescaping failed: {str(e)}")
        
        # Ensure the JSON starts with an opening brace
        if not json_str.startswith('{'):
            # Find the first opening brace
            brace_pos = json_str.find('{')
            if brace_pos >= 0:
                print(f"[DEBUG] Found opening brace at position {brace_pos}, trimming prefix")
                json_str = json_str[brace_pos:]
                print(f"[DEBUG] After brace trimming: '{json_str[:50]}...'")
        
        # Final sanity check - ensure we have a valid JSON start
        print(f"[DEBUG] Final cleaned JSON starts with: '{json_str[:20]}...'")
        return json_str
    
    def _extract_scores(self, result_obj) -> Dict[str, Dict]:
        """
        Parses GPT-4o structured JSON response explicitly into a dict.
        Handles both string and dict inputs to accommodate different response formats.
        """
        try:
            # STEP 1: Determine input type with detailed logging
            print(f"[DEBUG] Extract scores input type: {type(result_obj)}")
            logger.info(f"[JudgeAgent] Extract scores input type: {type(result_obj)}")
            
            # STEP 2: Extract content based on type
            if isinstance(result_obj, dict) and "content" in result_obj:
                result_str = result_obj["content"]
                print(f"[DEBUG] Extracted content from dict, type: {type(result_str)}")
                print(f"[DEBUG] Content starts with: {result_str[:50]}")
                logger.info(f"[JudgeAgent] Extracted content string ({len(result_str)} chars)")
            else:
                result_str = str(result_obj)
                print(f"[DEBUG] Converted input to string, length: {len(result_str)}")
                logger.info(f"[JudgeAgent] Converted input to string ({len(result_str)} chars)")
            
            # STEP 3: Extract JSON from markdown with detailed debugging
            json_content = ""
            if "```json" in result_str:
                print(f"[DEBUG] Found markdown JSON block")
                parts = result_str.split("```json", 1)
                if len(parts) > 1 and "```" in parts[1]:
                    # Get raw JSON content from between the markdown delimiters
                    json_content = parts[1].split("```", 1)[0]
                    print(f"[DEBUG] Extracted JSON from markdown, length: {len(json_content)}")
                    
                    # Show byte-by-byte info for first few characters to debug invisible chars
                    if json_content:
                        print("[DEBUG] Character-by-character inspection of first 10 bytes:")
                        for i, char in enumerate(json_content[:10]):
                            print(f"Position {i}: '{char}' (ASCII: {ord(char)}, Hex: {hex(ord(char))})")
                    
                    print(f"[DEBUG] JSON starts with: {json_content[:50]}")
                    print(f"[DEBUG] JSON ends with: {json_content[-50:] if len(json_content) > 50 else json_content}")
                else:
                    print(f"[DEBUG] Missing closing ``` in markdown")
            else:
                print(f"[DEBUG] No markdown JSON block found, trying regex")
                match = re.search(r'\{.*\}', result_str, re.DOTALL)
                if match:
                    json_content = match.group(0)
                    print(f"[DEBUG] Extracted JSON with regex, length: {len(json_content)}")
                else:
                    print(f"[DEBUG] No JSON-like content found")
                    return {}
            
            logger.info(f"[JudgeAgent] Extracted JSON content ({len(json_content)} chars)")
            
            # STEP 4: Parse the extracted JSON with careful error handling
            print(f"[DEBUG] Attempting to parse JSON: {json_content[:100]}...")
            
            # Try multiple parsing strategies
            # Strategy 1: Normal parsing with strip
            try:
                cleaned_json = json_content.strip()
                print(f"[DEBUG] Parsing with basic strip(), JSON starts with: {cleaned_json[:20]}")
                parsed_json = json.loads(cleaned_json)
                print(f"[DEBUG] Successfully parsed with basic strip()")
            except json.JSONDecodeError as je1:
                print(f"[DEBUG] Basic strip failed: {je1}")
                
                # Strategy 2: Aggressive cleaning
                try:
                    cleaned_json = self._clean_json_string(json_content)
                    print(f"[DEBUG] Parsing with aggressive cleaning, JSON starts with: {cleaned_json[:20]}")
                    parsed_json = json.loads(cleaned_json)
                    print(f"[DEBUG] Successfully parsed with aggressive cleaning")
                except json.JSONDecodeError as je2:
                    print(f"[DEBUG] Aggressive cleaning failed: {je2}")
                    
                    # Strategy 3: Manual JSON construction - last resort
                    try:
                        print("[DEBUG] Attempting to manually extract JSON structure")
                        # Find potential model IDs
                        model_patterns = re.finditer(r'"([^"]+)":\s*{', json_content)
                        manual_json = {}
                        
                        for match in model_patterns:
                            model_id = match.group(1)
                            print(f"[DEBUG] Found potential model ID: {model_id}")
                            
                            # Extract scores for this model using regex
                            scores = {}
                            score_matches = re.finditer(r'"([^"]+)":\s*(\d+)', json_content)
                            for score_match in score_matches:
                                metric, value = score_match.groups()
                                if metric in ["personalization", "relevance", "fluency", "coherence", "creativity"]:
                                    scores[metric] = int(value)
                            
                            if scores:  # Only add if we found some scores
                                manual_json[model_id] = scores
                                print(f"[DEBUG] Extracted scores for {model_id}: {scores}")
                        
                        if manual_json:
                            parsed_json = manual_json
                            print(f"[DEBUG] Constructed JSON manually: {parsed_json}")
                        else:
                            print("[DEBUG] Failed to extract any model scores manually")
                            return {}
                            
                    except Exception as je3:
                        print(f"[DEBUG] Manual JSON construction failed: {je3}")
                        logger.error(f"[JudgeAgent] All JSON parsing methods failed")
                        return {}
            
            # If we got here, we have a parsed JSON object
            print(f"[DEBUG] Parsed JSON successfully, type: {type(parsed_json)}")
            print(f"[DEBUG] Successfully parsed JSON, keys: {list(parsed_json.keys())}")
            logger.info(f"[JudgeAgent] Successfully parsed JSON with {len(parsed_json)} models")
            
            # STEP 5: Process model scores with validation
            structured_scores: Dict[str, Dict] = {}
            for model_id, scores in parsed_json.items():
                print(f"[DEBUG] Processing scores for model: {model_id}")
                
                # Validate score object
                if not isinstance(scores, dict):
                    print(f"[DEBUG] Invalid scores format for {model_id}: {scores}")
                    continue
                
                # Extract and validate individual scores
                structured_scores[model_id] = {
                    "personalization": int(scores.get("personalization", 0)),
                    "relevance": int(scores.get("relevance", 0)),
                    "fluency": int(scores.get("fluency", 0)),
                    "coherence": int(scores.get("coherence", 0)),
                    "creativity": int(scores.get("creativity", 0)),
                    "reasons": scores.get("reasons", {})
                }
                print(f"[DEBUG] Processed scores for {model_id}: {structured_scores[model_id]}")
            
            logger.info(f"[JudgeAgent] Processed scores for {len(structured_scores)} models")
            return structured_scores
        
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON decode error: {e}")
            print(f"[DEBUG] Failed to parse: '{str(result_obj)[:200]}...'")
            logger.error(f"[JudgeAgent] JSON parsing error explicitly: {str(e)}")
            logger.error(f"[JudgeAgent] Raw text that failed to parse: {str(result_obj)[:200]}...")
            return {}
        except Exception as e:
            print(f"[DEBUG] General exception: {e}")
            print(f"[DEBUG] Exception type: {type(e)}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            logger.error(f"[JudgeAgent] Error extracting scores: {str(e)}")
            return {}