# Architecture

## Diagrama del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR AGENT                        │
│  (LangGraph StateGraph - Controlador principal del pipeline)    │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  PRODUCT OWNER  │ │    ARCHITECT    │ │   QA AGENT      │
│  - Descompone   │ │  - Diseña grafo │ │  - Valida       │
│  - Dimensiones  │ │  - Modelos      │ │  - Score        │
│  - Prioridades  │ │  - Estrategia   │ │  - Feedback     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │               │               │
              ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LANGGRAPH STATE GRAPH                       │
│  query → decompose → research → synthesize → validate → deliver │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│  TAVILY API     │                     │  QDRANT DB      │
│  - Noticias     │                     │  - Contexto     │
│  - Web search   │                     │  - Histórico    │
│  - Filtros      │                     │  - Embeddings   │
└─────────────────┘                     └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  OPENROUTER     │
                    │  - Claude 3.5   │
                    │  - GPT-4o       │
                    │  - Modelos LLM  │
                    └─────────────────┘
```

## Flujo de Datos

1. **Input**: Query del usuario
2. **Decompose**: Product Owner genera dimensiones
3. **Research** (paralelo):
   - Tavily: noticias recientes (72h)
   - Qdrant: contexto histórico
4. **Synthesize**: Combinar fuentes, eliminar redundancias
5. **Loop Engineering**: Refinar iterativamente
6. **Validate**: QA Agent verifica calidad
7. **Output**: Intelligence Brief estructurado

## Stack Técnico

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| Orquestación | LangGraph | Grafo de agentes |
| Búsqueda web | Tavily API | Noticias en tiempo real |
| Memoria | Qdrant | Contexto histórico |
| LLMs | OpenRouter | Modelos multi-proveedor |
| Validación | QA Agent | Factualidad y calidad |