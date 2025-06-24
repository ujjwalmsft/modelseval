
# Agentic AI-based Model Evaluation Platform

The **Agentic AI-based Model Evaluation and Router Platform** is an advanced, structured, and scalable solution designed for architects, developers, and enterprises to evaluate Large and Small Language Models (LLMs/SLMs) and select the appropriate model based on recomended route. 
Leveraging technologies like Semantic Kernel (SK Python), Model Context Protocol (MCP), Azure AI Services (Azure OpenAI), Azure Cosmos DB, Azure Event Grid, and modern frontend frameworks (Next.js and React.js), this platform offers comprehensive comparative analyses of AI models.

## 🎯 Use Case Scenario
This platform caters to developers and AI architects needing detailed comparative analyses and insights into model performance. It efficiently manages evaluation workflows by capturing, analyzing, and comparing model responses across quantitative metrics (BLEU, ROUGE, Cosine Similarity) and qualitative assessments (personalization, relevance, fluency, coherence, creativity). Results are securely stored, interactively visualized, and clearly communicated through intuitive dashboards.

## 🤖 Why Agentic AI and Multi-Agent Systems?
This platform integrates Agentic AI with multi-agent orchestration via Semantic Kernel. Unlike traditional methods, Agentic AI dynamically adapts based on context, proactively requesting additional information if initial inputs are insufficient.

The multi-agent architecture enhances modularity, scalability, and maintainability. Each agent specializes in specific evaluation tasks, enabling independent development, easier troubleshooting, and adaptability to changing requirements.

## 🎯 Applicable Use Cases
- Quantitative analysis of AI model responses
- Qualitative assessments using advanced models (e.g., GPT-4o)
- Model comparison and benchmarking tailored to enterprise scenarios
- Structured evaluation workflows optimized for clear insights and model routing
- Multi-agent orchestration for complex AI evaluation tasks

## 🔑 Key Features
- Prebuilt workflows for quantitative and qualitative evaluations
- Seamless integration with Azure OpenAI (GPT-4o) and Azure AI Inference
- Real-time interactive dashboards built with Next.js and React.js
- Scalable structured data storage using Azure Cosmos DB
- Automated asynchronous agent processing via Azure Event Grid
- Modular architecture with defined schemas, components, and integration patterns
- Coherent session and conversation management through Model Context Protocol (MCP)

## 📌 Model Context Protocol (MCP)
The Model Context Protocol (MCP) ensures robust session and thread management, maintaining coherent conversation states and structured evaluations. MCP integrates closely with backend agents, Semantic Kernel workflows, and Cosmos DB to provide:

- Session context management
- Precise thread tracking and agent communication
- Consistent state persistence across evaluation phases

## 👥 Who Should Use This?
- AI developers and architects evaluating multiple models
- Innovation teams creating MVPs for rigorous model evaluation
- Business and technical stakeholders utilizing AI-driven decision-making
- Partners and system integrators delivering customized AI evaluation solutions

## 🧩 Platform Components
### 🚦 Agent Orchestration
- Semantic Kernel (SK v1.28.1+)
- Model Context Protocol (MCP)

### 💬 AI & Evaluations
- Azure OpenAI & Azure AI Inference
- Quantitative Metrics: BLEU, ROUGE-1, ROUGE-L, Cosine Similarity
- Qualitative Metrics: GPT-4o evaluations (personalization, relevance, fluency, coherence, creativity)

### 🗃️ Data Storage
- Azure Cosmos DB (structured threads, embeddings, evaluations, session metadata)

### 🖥️ Frontend
- Next.js & React.js (interactive visualizations and responsive dashboards)

### 📬 Async Processing
- Azure Event Grid

### 🚀 Backend Framework
- FastAPI (structured API endpoints)

### 📈 Monitoring & Observability
- Azure Monitor & Application Insights

## 🚀 Getting Started
Step 1: Clone the Repository
```bash
git clone <repository_url>
```
Step 2: Project Setup
**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Step 3: Configure Azure Services
Set Azure credentials and environment variables in:
```
backend/config/.env.dev
```
Step 4: Deployment
Deploy locally, via Docker, or using Azure App Service.

Step 5: Customization
Adapt evaluation workflows and integrations to your specific enterprise needs.

## 🔧 Technology Stack
| Component              | Technology                                                 |
|------------------------|------------------------------------------------------------|
| AI & NLP               | Azure OpenAI (GPT-4o), Azure AI Inference                  |
| Orchestration          | Semantic Kernel (SK Python v1.28.1+), MCP                  |
| Evaluation Metrics     | BLEU, ROUGE-1, ROUGE-L, Cosine Similarity, GPT-4o (Judge)  |
| Data Storage           | Azure Cosmos DB                                            |
| Frontend               | Next.js, React.js                                          |
| Backend                | FastAPI, Python                                            |
| Async Processing       | Azure Event Grid                                           |
| Observability          | Azure Monitor, Application Insights                        |

## 🔭 Project Roadmap
### Immediate:
- Reflection Agent: Debugging and integration of semantic memory retrieval
- Agentic Evaluations: Implementation to assess agent interactions and behaviors (Microsoft Build, May 2025)

### Long-term:
- Advanced Analytics Dashboard: Enhanced visual analytics for deeper insights
- Scalability & Optimization: Optimize for performance under heavy workloads
- Multilingual & Multi-document Support: Expand capabilities across languages and document types

## 🤝 Contributing
Feedback, feature requests, and contributions are highly encouraged. Please open issues or submit pull requests to support this solution.

## 📬 Contact
For co-engineering engagements, customized workshops, or enterprise deployment assistance, please contact:

**OCTO Depth Engagement Team**  
📧 [octodet@microsoft.com](mailto:octodet@microsoft.com)
