# PRD — mi-agent v1.0

## Datos del documento

| Campo | Valor |
|-------|-------|
| Producto | mi-agent |
| Versión | 1.0.0 |
| Autor | Product Owner |
| Fecha | 2026-06-12 |
| Estado | Activo |

---

## 1. Visión del producto

**mi-agent** es un agente investigador financiero autónomo que, dado el nombre de una empresa LATAM, busca noticias recientes en la web (últimas 2 semanas), sintetiza la información mediante LLM y genera un reporte estructurado en Markdown con: resumen ejecutivo, eventos clave, análisis de riesgo y fuentes citadas.

### Diferenciador clave vs mi-rag

| Aspecto | mi-rag | mi-agent |
|---------|--------|----------|
| Fuente de datos | PDFs estáticos subidos por usuario | Web en tiempo real (Tavily API) |
| Mecanismo | Búsqueda semántica (embeddings + Qdrant) | Agente con herramientas (LangGraph) |
| Estado | Stateless | Stateful (grafo con nodos y aristas) |
| Complejidad | RAG simple | Orquestación multi-nodo con tool-calling |
| Dependencias | Qdrant, embeddings | Solo Tavily + LLM (sin DB vectorial) |

---

## 2. Objetivos

### 2.1 Objetivos de negocio
- Demostrar capacidad de construir agentes autónomos con LangGraph
- Complementar el portafolio de IA (mi-rag = búsqueda; mi-agent = investigación)
- Mantener costo $0 usando tiers gratuitos (Tavily free, OpenRouter free tier)

### 2.2 Objetivos técnicos
- Arquitectura limpia: separación de capas (agent, tools, api, ui)
- Configuración reutilizable desde mi-rag (misma API key OpenRouter)
- Deployable con Docker
- Testeable (pytest + pytest-asyncio)

---

## 3. Alcance v1.0

### 3.1 IN — funcionalidades incluidas

| ID | Funcionalidad | Descripción |
|----|---------------|-------------|
| F-01 | Input de empresa | Usuario ingresa nombre de empresa LATAM via UI |
| F-02 | Búsqueda web | Tool search_web usa Tavily API para buscar noticias de las últimas 2 semanas |
| F-03 | LLM analysis | OpenRouter procesa resultados y genera análisis textual |
| F-04 | Reporte Markdown | Output estructurado con: Resumen Ejecutivo, Eventos Clave, Análisis de Riesgo, Fuentes |
| F-05 | API REST | FastAPI expone POST /report con input empresa y output markdown |
| F-06 | UI Streamlit | Frontend interactivo para consultar reportes |
| F-07 | Health check | GET /health para monitoreo |

### 3.2 OUT — funcionalidades excluidas (v1.0+)

| ID | Funcionalidad | Razón |
|----|---------------|-------|
| X-01 | Qdrant / RAG local | mi-agent es independiente de mi-rag |
| X-02 | Embeddings / Qdrant | No se requiere búsqueda semántica |
| X-03 | Autenticación | Portfolio demo, no producto en producción |
| X-04 | Historial de reportes | No persistencia en v1 |
| X-05 | Streaming SSE | Simplificación para v1 |
| X-06 | Multi-idioma | Inglés y español cubren LATAM |

---

## 4. Requisitos no funcionales

| Requisito | Métrica |
|-----------|---------|
| Latencia | < 30s para reporte completo |
| Disponibilidad | Local (desarrollo), Docker (futuro) |
| Seguridad | API keys en .env, nunca en código |
| Mantenibilidad | Ruff linting, mypy strict |
| Costo | $0/mes (Tavily free: 1000 búsquedas/mes; OpenRouter free tier) |

---

## 5. Stack tecnológico

| Capa | Tecnología | Versión |
|------|------------|---------|
| Orquestación | LangGraph | >=0.2.0 |
| LLM Framework | LangChain Core | >=0.3.0 |
| LLM Provider | OpenRouter (Llama 3.1 8B free) | - |
| Búsqueda Web | Tavily API | >=0.5.0 |
| Backend | FastAPI + Uvicorn | >=0.115.0 |
| Frontend | Streamlit | >=1.40.0 |
| HTTP Client | httpx | >=0.28.0 |
| Validación | Pydantic | >=2.9.0 |
| Linting | Ruff | >=0.8.0 |
| Type Check | Mypy (strict) | >=1.13.0 |
| Testing | Pytest + pytest-asyncio | >=8.3.0 |
| Python | >=3.11 | - |

---

## 6. Arquitectura de alto nivel

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│   FastAPI    │────▶│  LangGraph   │
│   (UI)      │     │   (API)      │     │   (Agent)    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                    ┌──────────┼──────────┐
                                    ▼          ▼          ▼
                              ┌──────────┐ ┌────────┐ ┌──────────┐
                              │  Tavily  │ │  LLM   │ │  Report  │
                              │  (Web)   │ │ (OpenR)│ │ (Gen)    │
                              └──────────┘ └────────┘ └──────────┘
```

### Flujo principal

1. Usuario ingresa nombre de empresa en Streamlit
2. Streamlit llama a POST /report de FastAPI
3. FastAPI invoca LangGraph runner
4. LangGraph ejecuta grafo:
   - **Nodo researcher**: llama search_web (Tavily) → resultado web
   - **Nodo analyst**: pasa contexto web al LLM → análisis
   - **Nodo reporter**: genera reporte Markdown estructurado
5. FastAPI retorna reporte a Streamlit
6. Streamlit renderiza Markdown

---

## 7. Estructura del reporte de salida

```markdown
# Reporte: {Empresa}

## Resumen Ejecutivo
[2-3 párrafos con síntesis de la situación actual de la empresa]

## Eventos Clave (últimas 2 semanas)
- [Fecha] Evento 1
- [Fecha] Evento 2
- [Fecha] Evento 3

## Análisis de Riesgo
| Riesgo | Nivel | Descripción |
|--------|-------|-------------|
| ... | Alto/Medio/Bajo | ... |

## Fuentes
1. [Título](URL) — Fecha
2. [Título](URL) — Fecha

---
*Reporte generado automáticamente por mi-agent — {fecha}*
```

---

## 8. Configuración y variables de entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| OPENROUTER_API_KEY | API key de OpenRouter | Sí |
| OPENROUTER_MODEL | Modelo LLM (default: meta-llama/llama-3.1-8b-instruct:free) | No |
| TAVILY_API_KEY | API key de Tavily | Sí |
| API_HOST | Host del backend (default: 0.0.0.0) | No |
| API_PORT | Puerto del backend (default: 8000) | No |

**NOTA**: Se eliminan qdrant_url, qdrant_api_key, qdrant_collection. mi-agent NO usa Qdrant.

---

## 9. API Endpoints

### POST /report
```json
Request:  { "empresa": "Ecopetrol" }
Response: { "empresa": "Ecopetrol", "reporte": "# Reporte: Ecopetrol\n..." }
```

### GET /health
```json
Response: { "status": "ok" }
```

---

## 10. Restricciones y dependencias

- **Tavily Free Tier**: 1000 búsquedas/mes, 5 resultados por query
- **OpenRouter Free Tier**: Rate limits variables por modelo
- **Sin persistencia**: Reportes no se guardan en v1
- **Sin autenticación**: API abierta para demo
- **Sin Docker**: Deploy local con `uvicorn` y `streamlit run` en v1

---

## 11. Métricas de éxito

| Métrica | Target |
|---------|--------|
| Tiempo de generación de reporte | < 30 segundos |
| Cobertura de código con tests | > 80% |
| Errores de linting (ruff) | 0 |
| Errores de tipado (mypy strict) | 0 |
| Costo mensual | $0 |

---

## 12. Riesgos identificados

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Tavily rate limit | Alto | Cache simple de queries frecuentes (v1.1) |
| LLM free tier lento | Medio | Timeout configurable, fallback a otro modelo |
| Resultados web irrelevantes | Medio | Prompt engineering con filtros de fecha |
| Sin persistencia | Bajo | v1 es demo, no requiere historial |

---

## 13. roadmap futuro (post v1)

- v1.1: Cache de resultados web
- v1.2: Streaming SSE para UI
- v1.3: Historial de reportes (SQLite)
- v2.0: Integración con mi-rag (contexto híbrido)
- v2.1: Auth + multi-usuario
- v2.2: Deploy Docker + CI/CD

---

*Documento generado por Product Owner — mi-agent v1.0*
