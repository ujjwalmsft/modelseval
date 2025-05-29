new-eval-backend/
├── app/
│   ├── agents/
│   │   ├── evaluator_agent.py          # Evaluates quantitative metrics (BLEU, ROUGE, etc.)
│   │   ├── judge_agent.py              # Evaluates qualitative metrics using GPT-4
│   │   ├── planner_agent.py            # Generates model completions based on prompts
│   │   └── reflection_agent.py         # Retrieves relevant semantic memory context
│
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── compare.py              # Endpoint to compare multiple model completions
│   │   │   ├── completion.py           # Endpoint for direct model completion
│   │   │   └── eventgrid_consumer.py   # Consumes Event Grid events for async processing
│   │   │
│   │   └── router.py                   # Aggregates all API routes
│
│   ├── background/
│   │   └── event_processor.py          # Processes async evaluation tasks via Event Grid
│
│   ├── core/
│   │   └── orchestrator.py             # Central coordinator for agent execution
│
│   ├── mcp/
│   │   ├── client.py                   # MCP client logic for communication
│   │   ├── protocol.py                 # MCP message protocol handling
│   │   └── server.py                   # MCP server implementation
│
│   ├── memory/
│   │   └── semantic_memory_service.py  # Manages semantic memory storage and retrieval
│
│   ├── models/
│   │   ├── request.py                  # Request and response model definitions
│   │   └── mcp_models.py               # MCP schema definitions
│
│   ├── plugins/
│   │   ├── ComparisonPlugin/
│   │   │   ├── analyze_metrics_function.py    # Plugin for quantitative metric analysis
│   │   │   ├── compare_responses_function.py  # Plugin for comparing model outputs
│   │   │   └── config.json                    # Semantic Kernel plugin configuration
│   │   │
│   │   ├── EmbeddingPlugin/
│   │   │   ├── batch_generate_embeddings_function.py # Batch embeddings generation
│   │   │   ├── generate_embeddings_function.py       # Single embedding generation
│   │   │   ├── process_chunks_function.py            # Processes embeddings in chunks
│   │   │   └── config.json                           # Embedding plugin configuration
│   │   │
│   │   ├── CompletionPlugin/
│   │   │   ├── run_completion_function.py     # Executes direct model completion
│   │   │   ├── stream_completion_function.py  # Streaming completions handler
│   │   │   ├── stream_handlers.py              # Streaming logic handler
│   │   │   └── config.json                    # Completion plugin configuration
│   │   │
│   │   ├── MemoryPlugin/
│   │   │   ├── save_conversation_function.py  # Saves conversation history explicitly
│   │   │   ├── search_memory_function.py      # Semantic memory search function
│   │   │   ├── retrieve_context_function.py   # Retrieves specific semantic memory context
│   │   │   ├── list_collection_function.py    # Lists available memory collections
│   │   │   ├── get_memory_function.py         # Retrieves semantic memory items
│   │   │   └── config.json                    # Memory plugin configuration
│   │   │
│   │   └── SearchPlugin/
│   │       ├── hybrid_search_function.py      # Combines keyword and semantic search
│   │       ├── semantic_search_function.py    # Semantic vector-based searching
│   │       └── config.json                    # Search plugin configuration
│
│   ├── services/
│   │   ├── content_safety_service.py          # Checks responses for harmful content
│   │   ├── cosmos_service.py                  # Manages Cosmos DB storage/retrieval
│   │   ├── embedding_service.py               # Embeddings service integration
│   │   └── semantic_kernel_service.py         # Semantic Kernel API integration
│
│   ├── config.py                              # Application-wide configuration settings
│   └── main.py                                # FastAPI application entry point
│
├── Dockerfile                                 # Dockerfile for backend containerization
├── docker-compose.yml                         # Docker compose configuration
├── requirements.txt                           # Python dependencies
├── .env                                       # Environment variables configuration
├── structure.md                               # Documentation for backend structure
└── .gitignore                                 # Git ignore configuration