# 🧠 Intelligence Brief Generator

> Sistema multi-agente de inteligencia artificial que genera briefs ejecutivos estratégicos combinando investigación web en tiempo real con contexto histórico vectorial, utilizando auto-crítica iterativa para refinamiento de calidad.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.74-1C3C3C.svg?style=flat)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-35%20passing-brightgreen.svg?style=flat)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Demo del Intelligence Brief Generator](0613.gif)

## 🎯 Qué hace

Este sistema recibe una query de investigación (ej: "análisis de mercado fintech LATAM") y genera un intelligence brief estructurado con:

- **Executive Summary** — Hallazgos clave en 2-3 párrafos
- **Análisis por Dimensión** — Deep dive en tendencias, competencia, regulación, tecnología y riesgos
- **Proyecciones** — Forecasting basado en datos
- **Recomendaciones** — Próximos pasos accionables
- **Atribución de Fuentes** — Cada afirmación vinculada a una fuente verificada

El sistema critica y refina iterativamente su propio output hasta alcanzar un score de calidad ≥ 8/10.

## 🏗️ Arquitectura

```
Query del Usuario
    │
    ▼
┌─────────────────────────────────────────────┐
│           ORCHESTRATOR (LangGraph)          │
│  StateGraph con edges condicionales         │
└──────┬──────────────┬──────────────┬────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌───────────┐ ┌─────────────┐
│   Tavily    │ │  Qdrant   │ │  OpenRouter │
│ Búsqueda    │ │ Vector DB │ │  Gateway    │
│ Web (tiempo │ │(contexto  │ │   LLM      │
│  real)      │ │histórico) │ │             │
└─────────────┘ └───────────┘ └─────────────┘
       │              │              │
       └──────┬───────┴──────┬───────┘
              ▼              ▼
       ┌─────────────┐ ┌──────────┐
       │  Sintetizar  │ │ Criticar │◄── Loop
       │  (generar)   │ │(validar) │    (máx 5x)
       └─────────────┘ └──────────┘
              │
              ▼
     Intelligence Brief
```

## 🛠️ Stack Técnico

| Capa | Tecnología | Propósito |
|------|-----------|-----------|
| **Orquestación** | LangGraph | Workflow de agentes con StateGraph, nodos y edges condicionales |
| **Investigación Web** | Tavily API | Búsqueda de noticias en tiempo real (últimas 72h) con rate limiting |
| **Base de Datos Vectorial** | Qdrant | Búsqueda semántica para contexto histórico de investigaciones |
| **Gateway LLM** | OpenRouter | Acceso multi-modelo con fallback automático |
| **Frontend** | Streamlit | UI interactiva con 3 pestañas |
| **Testing** | pytest | 35 tests (unit, integración, e2e) |
| **Containerización** | Docker | Deployment listo para producción |

## 📁 Estructura del Proyecto

```
intelligence-brief-agent/
├── app.py                          # Streamlit UI (3 pestañas)
├── scripts/
│   ├── main.py                     # Entry point CLI
│   ├── agents/
│   │   ├── orchestrator.py         # Controlador del pipeline
│   │   ├── researcher.py           # Búsqueda Tavily + Qdrant
│   │   └── synthesizer.py          # Generación de reportes con LLM
│   ├── tools/
│   │   ├── tavily_tool.py          # Búsqueda web con retry + rate limit
│   │   ├── qdrant_tool.py          # Vector DB con cosine similarity
│   │   └── openrouter_tool.py      # LLM multi-modelo con fallback
│   ├── graph/
│   │   ├── state.py                # Definición de estado TypedDict
│   │   └── workflow.py             # StateGraph de LangGraph
│   └── loops/
│       ├── self_critique.py        # Lógica de auto-crítica
│       └── iteration_manager.py    # Control del loop (máx 5, timeout)
├── tests/
│   ├── unit/                       # Tests de herramientas
│   ├── integration/                # Tests del workflow
│   └── e2e/                        # Tests del pipeline completo
├── docs/                           # PRD, DOD, Arquitectura
├── .opencode/                      # Definiciones de agentes + skills
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🔁 Flujo del Pipeline

```
1. DESCOMPONER    → Product Owner descompone la query en 5 dimensiones de análisis
2. INVESTIGAR     → Tavily (web) + Qdrant (historial) ejecutan en paralelo
3. SINTETIZAR     → LLM genera borrador inicial de 4000-7000 palabras
4. LOOP ENGINEERING:
   a. CRITICAR    → LLM identifica debilidades, sesgos y gaps
   b. REFINAR     → LLM reescribe corrigiendo los problemas detectados
   c. VALIDAR     → Score 0-10; si ≥8 → entregar, si no → volver al paso a
5. ALMACENAR      → Guardar brief + fuentes en Qdrant para futuras queries
6. ENTREGAR       → Mostrar en Streamlit + descargar como Markdown
```

## 🚀 Inicio Rápido

```bash
# Clonar
git clone https://github.com/darksidesad/mi-agent.git
cd mi-agent

# Entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar
cp .env.example .env
# Agregar tus API keys en .env

# Ejecutar CLI
python scripts/main.py "tu query de investigación"

# Ejecutar UI Streamlit
streamlit run app.py
```

## ⚡ Características Principales

- **Investigación Paralela** — Tavily + Qdrant ejecutan simultáneamente con `asyncio.gather()`
- **Loop Engineering** — Ciclo de auto-crítica y refinamiento (máximo 5 iteraciones)
- **Manejo de Rate Limits** — Retry con backoff exponencial (10s → 20s → 40s → 80s)
- **Contexto Histórico** — Cada investigación se guarda en Qdrant; futuras queries aprovechan hallazgos previos
- **Fallback Multi-modelo** — Cambio automático de modelo ante fallos
- **UI en Tiempo Real** — Progreso paso a paso del pipeline en Streamlit
- **Chat con Historial** — Preguntar sobre investigaciones pasadas almacenadas en Qdrant

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Suite específica
pytest tests/unit/ -v          # 25 tests unitarios
pytest tests/integration/ -v   # 3 tests de integración
pytest tests/e2e/ -v           # 7 tests end-to-end
```

## 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Test Coverage | 35/35 pasando |
| Tiempo Promedio Pipeline | ~90-150s (depende del modelo) |
| Tavily Free Tier | 1000 requests/mes |
| Costo LLM | $0 (modelos gratuitos) |
| Longitud Máxima Brief | 7000+ palabras |

## 🔧 Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| `TAVILY_API_KEY` | API key de Tavily Search | — |
| `OPENROUTER_API_KEY` | API key de OpenRouter LLM | — |
| `OPENROUTER_MODEL` | Modelo principal | `nex-agi/nex-n2-pro:free` |
| `QDRANT_URL` | URL de instancia Qdrant | `http://localhost:6333` |
| `MAX_LOOP_ITERATIONS` | Máximo de ciclos de crítica | `5` |
| `QUALITY_THRESHOLD` | Score mínimo para entregar | `8.0` |

## 👨‍💻 Autor

**[Tu Nombre]** — AI/ML Engineer

- LinkedIn: [tu-linkedin](https://linkedin.com/in/tu-perfil)
- GitHub: [@darksidesad](https://github.com/darksidesad)

---

*Construido con LangGraph, Tavily, Qdrant, OpenRouter y Streamlit*