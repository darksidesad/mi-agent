# 🧠 Intelligence Brief Generator

> Multi-agent AI system that generates executive-level intelligence briefs by combining real-time web research with historical vector context, using iterative self-critique for quality refinement.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.74-1C3C3C.svg?style=flat)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-35%20passing-brightgreen.svg?style=flat)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

This system takes a research query (e.g., "fintech market analysis LATAM") and produces a structured intelligence brief with:

- **Executive Summary** — Key findings in 2-3 paragraphs
- **Dimension Analysis** — Deep dive into market trends, competition, regulation, technology, and risks
- **Projections** — Data-backed trend forecasting
- **Recommendations** — Actionable next steps
- **Source Attribution** — Every claim linked to a verified source

The system iteratively critiques and refines its own output up to 5 times until quality score ≥ 8/10.

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│           ORCHESTRATOR (LangGraph)          │
│  StateGraph with conditional loop edges     │
└──────┬──────────────┬──────────────┬────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌───────────┐ ┌─────────────┐
│   Tavily    │ │  Qdrant   │ │  OpenRouter │
│ Web Search  │ │ Vector DB │ │   LLM API   │
│ (real-time) │ │(historical│ │ (推理+生成) │
└─────────────┘ └───────────┘ └─────────────┘
       │              │              │
       └──────┬───────┴──────┬───────┘
              ▼              ▼
       ┌─────────────┐ ┌──────────┐
       │  Synthesize  │ │ Critique │◄── Loop
       │  (generate)  │ │(validate)│    (max 5x)
       └─────────────┘ └──────────┘
              │
              ▼
     Intelligence Brief
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | LangGraph | Agent workflow with StateGraph, nodes, and conditional edges |
| **Web Research** | Tavily API | Real-time news search (last 72h) with rate limiting |
| **Vector Database** | Qdrant | Semantic search for historical research context |
| **LLM Gateway** | OpenRouter | Multi-model access with automatic fallback |
| **Frontend** | Streamlit | Interactive UI with 3 tabs |
| **Testing** | pytest | 35 tests (unit, integration, e2e) |
| **Containerization** | Docker | Production-ready deployment |

## 📁 Project Structure

```
intelligence-brief-agent/
├── app.py                          # Streamlit UI (3 tabs)
├── scripts/
│   ├── main.py                     # CLI entry point
│   ├── agents/
│   │   ├── orchestrator.py         # Pipeline controller
│   │   ├── researcher.py           # Tavily + Qdrant search
│   │   └── synthesizer.py          # LLM report generation
│   ├── tools/
│   │   ├── tavily_tool.py          # Web search with retry + rate limit
│   │   ├── qdrant_tool.py          # Vector DB with cosine similarity
│   │   └── openrouter_tool.py      # Multi-model LLM with fallback
│   ├── graph/
│   │   ├── state.py                # TypedDict state definition
│   │   └── workflow.py             # LangGraph StateGraph
│   └── loops/
│       ├── self_critique.py        # Auto-critique logic
│       └── iteration_manager.py    # Loop control (max 5, timeout)
├── tests/
│   ├── unit/                       # Tool tests (Tavily, Qdrant, OpenRouter)
│   ├── integration/                # Workflow tests
│   └── e2e/                        # Full pipeline tests
├── docs/                           # PRD, DOD, Architecture
├── .opencode/                      # Agent + skill definitions
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🔄 Pipeline Flow

```
1. DECOMPOSE    → Product Owner breaks query into 5 analysis dimensions
2. RESEARCH     → Tavily (web) + Qdrant (history) run in parallel
3. SYNTHESIZE   → LLM generates initial 4000-7000 word brief
4. LOOP ENGINEERING:
   a. CRITIQUE  → LLM identifies weaknesses, biases, gaps
   b. REFINE    → LLM rewrites fixing identified issues
   c. VALIDATE  → Score 0-10; if ≥8 → deliver, else → loop back
5. STORE        → Save brief + sources to Qdrant for future queries
6. DELIVER      → Display in Streamlit + download as Markdown
```

## 🚀 Getting Started

```bash
# Clone
git clone https://github.com/darksidesad/mi-agent.git
cd mi-agent

# Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your API keys to .env

# Run CLI
python scripts/main.py "your research query"

# Run Streamlit UI
streamlit run app.py
```

## ⚡ Key Features

- **Parallel Research** — Tavily + Qdrant execute simultaneously via `asyncio.gather()`
- **Loop Engineering** — Self-critique and refinement cycle (max 5 iterations)
- **Rate Limit Handling** — Exponential backoff retry (10s → 20s → 40s → 80s)
- **Historical Context** — Each research saves to Qdrant; future queries benefit from past findings
- **Multi-model Fallback** — Automatic model switching on failure
- **Real-time UI** — Step-by-step pipeline progress in Streamlit
- **Chat with History** — Ask questions about past research stored in Qdrant

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific suite
pytest tests/unit/ -v          # 25 unit tests
pytest tests/integration/ -v   # 3 integration tests
pytest tests/e2e/ -v           # 7 e2e tests
```

## 📊 Metrics

| Metric | Value |
|--------|-------|
| Test Coverage | 35/35 passing |
| Avg. Pipeline Time | ~90-150s (model dependent) |
| Tavily Free Tier | 1000 requests/month |
| LLM Cost | $0 (free tier models) |
| Max Brief Length | 7000+ words |

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `TAVILY_API_KEY` | Tavily search API key | — |
| `OPENROUTER_API_KEY` | OpenRouter LLM API key | — |
| `OPENROUTER_MODEL` | Primary model | `nex-agi/nex-n2-pro:free` |
| `QDRANT_URL` | Qdrant instance URL | `http://localhost:6333` |
| `MAX_LOOP_ITERATIONS` | Max critique cycles | `5` |
| `QUALITY_THRESHOLD` | Min score to deliver | `8.0` |

## 👨‍💻 Author

**[Tu Nombre]** — AI/ML Engineer

- LinkedIn: [tu-linkedin](https://linkedin.com/in/tu-perfil)
- GitHub: [@darksidesad](https://github.com/darksidesad)

---

*Built with LangGraph, Tavily, Qdrant, OpenRouter, and Streamlit*