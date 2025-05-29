"""
Direct test script for Cosmos DB agent result retrieval WITHOUT using CosmosService.

This script connects directly to Cosmos DB, queries the agentsresults container,
and fetches evaluator, judge, and reflection results for a given session/thread.
"""

import asyncio
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
import os
from dotenv import load_dotenv
load_dotenv()
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE")
COSMOS_AGENT_RESULTS_CONTAINER = os.getenv("COSMOS_AGENT_RESULTS_CONTAINER", "agentsresults")
print(f"Cosmos DB endpoint: {COSMOS_ENDPOINT}")
TEST_SESSION_ID = "sessioan1"
TEST_THREAD_ID = "threaad1"

async def get_agent_result_direct(session_id, agent, thread_id=None):
    async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
        db = client.get_database_client(COSMOS_DATABASE)
        container = db.get_container_client(COSMOS_AGENT_RESULTS_CONTAINER)
        query = "SELECT * FROM c WHERE c.session_id = @session_id AND c.agent = @agent"
        parameters = [
            {"name": "@session_id", "value": session_id},
            {"name": "@agent", "value": agent}
        ]
        if thread_id:
            query += " AND c.thread_id = @thread_id"
            parameters.append({"name": "@thread_id", "value": thread_id})

        items = [item async for item in container.query_items(
            query=query,
            parameters=parameters,
            # enable_cross_partition_query=True
        )]
        return items[0] if items else None

async def test_get_agent_result_direct():
    print(f"Testing retrieval for session_id={TEST_SESSION_ID}, thread_id={TEST_THREAD_ID}")
    for agent in ["evaluator", "judge", "reflection"]:
        print(f"\n--- Testing agent: {agent} ---")
        result = await get_agent_result_direct(TEST_SESSION_ID, agent, TEST_THREAD_ID)
        if result:
            print(f"Result for {agent}:")
            print(result)
        else:
            print(f"No result found for agent '{agent}' with session_id '{TEST_SESSION_ID}' and thread_id '{TEST_THREAD_ID}'.")

if __name__ == "__main__":
    asyncio.run(test_get_agent_result_direct())