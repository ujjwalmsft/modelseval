"""
Cosmos DB Service 
 
Responsibilities:
- Threaded conversation storage (role-based logs).
- Session metadata storage (separate from threads).
- Vector embedding storage for semantic memory.
- Explicit persistence of aggregated agent (Evaluator, Judge, Reflection) results for frontend retrieval.
 
Containers explicitly managed:
- threads
- embeddings(semantic-memory)
- agentsresults
- sessions
 
Used explicitly by:
- MemoryPlugin
- ReflectionAgent
- JudgeAgent
- CompletionPlugin
- EventProcessor (aggregated agent results persistence)
"""
 
import logging
import traceback
import time
import re
from typing import Dict, Any, List, Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from config import settings
 
logger = logging.getLogger(__name__)
 
class CosmosService:
    _instance = None
 
    def __init__(self):
        self.initialized = False
        self.client = None
        self.database = None
        self.threads_container = None
        self.vector_container = None
        self.agent_results_container = None
        self.sessions_container = None
        self.initialize()
 
    @classmethod
    def get_instance(cls) -> "CosmosService":
        if cls._instance is None:
            cls._instance = CosmosService()
            cls._instance.initialize()
        return cls._instance
 
    def initialize(self):
        """Initialize CosmosDB containers explicitly."""
        try:
            self.client = CosmosClient(settings.COSMOS_ENDPOINT, settings.COSMOS_KEY)
            self.database = self.client.create_database_if_not_exists(settings.COSMOS_DATABASE)

            # List all containers in the database for debugging
            container_names = [container['id'] for container in self.database.list_containers()]
            logger.info(f"[CosmosService] Containers found in DB: {container_names}")

            # Container for threaded conversations
            self.threads_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_CONTAINER,
                partition_key=PartitionKey(path="/modelId"),
                offer_throughput=400
            )
            logger.info(f"[CosmosService] threads_container initialized: {self.threads_container}")

            # Container for vector embeddings
            self.vector_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_VECTOR_CONTAINER,
                partition_key=PartitionKey(path="/collection"),
                offer_throughput=400
            )
            logger.info(f"[CosmosService] vector_container initialized: {self.vector_container}")

            # Container for agent results
            self.agent_results_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_AGENT_RESULTS_CONTAINER,
                partition_key=PartitionKey(path="/session_id"),
                offer_throughput=400
            )
            logger.info(f"[CosmosService] agent_results_container initialized: {self.agent_results_container}")

            # Container for session metadata
            self.sessions_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_SESSIONS_CONTAINER,
                partition_key=PartitionKey(path="/session_id"),
                offer_throughput=400
            )
            logger.info(f"[CosmosService] sessions_container initialized: {self.sessions_container}")

            self.initialized = True
            logger.info("[CosmosService] CosmosDB initialized successfully.")

        except Exception as e:
            logger.error(f"[CosmosService] Initialization error: {str(e)}")
            logger.error(traceback.format_exc())
            self.initialized = False
 
    def _sanitize_id(self, raw_id: str) -> str:
        """Sanitize IDs explicitly to remove illegal Cosmos DB characters."""
        return re.sub(r"[^a-zA-Z0-9-_]", "-", raw_id)
 
    async def get_container(self, container_name: str):
        """Explicitly retrieve a Cosmos container by name."""
        containers = {
            "threads": self.threads_container,
            "embeddings(semantic-memory)": self.vector_container,
            "agentsresults": self.agent_results_container,
            "sessions": self.sessions_container,
        }
        if container_name not in containers:
            raise ValueError(f"Unknown container name: {container_name}")
        return containers[container_name]
 
    async def save_conversation_message(self, model_id: str, thread_id: str, role: str, content: str, token_count: int = 0) -> Dict[str, Any]:
        """Save or update conversation messages explicitly, avoiding duplicates."""
        try:
            sanitized_thread_id = self._sanitize_id(thread_id)
            full_id = f"{model_id}-{sanitized_thread_id}"
            now = int(time.time())
 
            try:
                item = self.threads_container.read_item(item=full_id, partition_key=model_id)
                # Prevent duplicate assistant messages explicitly
                if item["messages"] and item["messages"][-1]["content"] == content and role == "assistant":
                    logger.warning("[CosmosService] Duplicate assistant message detected; skipping insertion.")
                    return {"status": "duplicate_skipped", "thread_id": thread_id}
 
                item["messages"].append({
                    "role": role,
                    "content": content,
                    "timestamp": now,
                    "tokenCount": token_count
                })
                item["metadata"]["lastUpdated"] = now
                item["metadata"]["tokenCount"] += token_count
                if role == "user":
                    item["metadata"]["promptTokens"] += token_count
                else:
                    item["metadata"]["completionTokens"] += token_count
 
                self.threads_container.replace_item(item=full_id, body=item)
                logger.info(f"[CosmosService] Updated thread '{thread_id}' for model '{model_id}'.")
                return {"status": "updated", "thread_id": thread_id}
 
            except exceptions.CosmosResourceNotFoundError:
                doc = {
                    "id": full_id,
                    "modelId": model_id,
                    "created": now,
                    "messages": [{
                        "role": role,
                        "content": content,
                        "timestamp": now,
                        "tokenCount": token_count
                    }],
                    "metadata": {
                        "tokenCount": token_count,
                        "lastUpdated": now,
                        "promptTokens": token_count if role == "user" else 0,
                        "completionTokens": token_count if role == "assistant" else 0
                    }
                }
                self.threads_container.create_item(body=doc)
                logger.info(f"[CosmosService] Created new thread '{thread_id}' for model '{model_id}'.")
                return {"status": "created", "thread_id": thread_id}
 
        except Exception as e:
            logger.error(f"[CosmosService] Error saving conversation message: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}
 
    async def save_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Explicitly save session metadata."""
        try:
            sanitized_session_id = self._sanitize_id(session_id)
            doc_id = f"session-{sanitized_session_id}"
            now = int(time.time())
 
            doc = {
                "id": doc_id,
                "sessionId": session_id,
                "metadata": metadata,
                "timestamp": now,
                "lastUpdated": now
            }
 
            # Use upsert_item instead of create_item
            result = self.sessions_container.upsert_item(body=doc)
            logger.info(f"[CosmosService] Upserted session metadata '{session_id}'.")
            return {"status": "upserted", "id": doc_id}

        except Exception as e:
            logger.error(f"[CosmosService] Error saving session metadata: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}

    def save_embedding(self, text, embedding, collection, reference_id, metadata):
        try:
            print(f"[CosmosService] Saving embedding to {collection} with ID: {reference_id}")
            logger.info(f"[CosmosService] Saving embedding to {collection} with ID: {reference_id}")
            
            doc = {
                "id": f"v-{reference_id}",
                "collection": collection,
                "model_id": metadata.get("model_id"),
                "text": text,
                "embedding": embedding,
                "metadata": metadata
            }
            
            # ADD THIS LINE:
            result = self.vector_container.create_item(body=doc)
            
            print(f"[CosmosService] Successfully saved embedding with ID: {result['id']}")
            logger.info(f"[CosmosService] Successfully saved embedding with ID: {result['id']}")
            
            return {"status": "success", "id": doc["id"]}
        except Exception as e:
            print(f"[CosmosService] Error saving embedding: {str(e)}")
            logger.error(f"[CosmosService] Error saving embedding: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def save_agent_results(self, session_id: str, thread_id: str, agent: str, use_case_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Explicitly save agent evaluation results."""
        try:
            doc_id = f"{agent}-{self._sanitize_id(session_id)}"
            now = int(time.time())

            doc = {
                "id": doc_id,
                "session_id": session_id,    # <-- FIXED: snake_case
                "thread_id": thread_id,      # <-- FIXED: snake_case
                "agent": agent,
                "use_case_id": use_case_id,  # <-- FIXED: snake_case
                "results": results,
                "timestamp": now,
                "lastUpdated": now
            }

            try:
                existing = self.agent_results_container.read_item(item=doc_id, partition_key=session_id)
                doc["timestamp"] = existing["timestamp"]
                self.agent_results_container.replace_item(item=doc_id, body=doc)
                logger.info(f"[CosmosService] Updated agent results '{agent}' for session '{session_id}'.")
                return {"status": "updated", "id": doc_id}

            except exceptions.CosmosResourceNotFoundError:
                self.agent_results_container.create_item(body=doc)
                logger.info(f"[CosmosService] Created new agent results '{agent}' for session '{session_id}'.")
                return {"status": "created", "id": doc_id}

        except Exception as e:
            logger.error(f"[CosmosService] Error saving agent results: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}
    


    async def get_agent_result(self, session_id: str, agent: str, thread_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            query = "SELECT * FROM c WHERE c.session_id = @session_id AND c.agent = @agent"
            parameters = [
                {"name": "@session_id", "value": session_id},
                {"name": "@agent", "value": agent}
            ]
            if thread_id:
                query += " AND c.thread_id = @thread_id"
                parameters.append({"name": "@thread_id", "value": thread_id})

            items = list(self.agent_results_container.query_items(
                query=query,
                parameters=parameters
            ))
            return items[0] if items else None
        except Exception as e:
            logger.error(f"[CosmosService] Error retrieving agent result: {str(e)}")
            logger.error(traceback.format_exc())
            return None