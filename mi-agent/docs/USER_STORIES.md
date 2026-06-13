# User Stories — mi-agent v1.0

## Priorización MoSCoW

| Prioridad | Significado |
|-----------|-------------|
| **Must** | Requisito crítico para MVP. Sin esto no hay producto. |
| **Should** | Importante pero no bloqueante. Incluir si hay tiempo. |
| **Could** | Deseable. Mejora la experiencia pero no esencial. |
| **Won't** (v1) | Excluido de esta versión. Candidato para v1.1+. |

---

## MUST (v1.0 MVP)

### US-01: Configurar proyecto base
**Como** desarrollador del proyecto
**Quiero** tener el proyecto estructurado con pyproject.toml, dependencias y configuración
**Para que** el equipo pueda trabajar sobre una base sólida

**Criterios de aceptación:**
- [ ] pyproject.toml con todas las dependencias correctas (sin qdrant-client)
- [ ] .env.example con todas las variables documentadas
- [ ] src/config.py lee variables de entorno con Pydantic Settings
- [ ] `ruff check .` pasa sin errores
- [ ] `mypy src/` pasa sin errores (strict)

**Notas:** Eliminar dependencias de Qdrant (qdrant-client, qdrant_url, etc.)

---

### US-02: Tool search_web con Tavily
**Como** agente investigador
**Quiero** buscar noticias recientes de una empresa en la web via Tavily
**Para que** pueda recopilar información actualizada para el análisis

**Criterios de aceptación:**
- [ ] Herramienta `search_web` decorada con `@tool` de LangChain
- [ ] Usa TavilyClient con API key desde configuración
- [ ] Acepta parámetro `query: str` y `max_results: int = 5`
- [ ] Retorna string formateado con títulos, URLs y contenido
- [ ] Maneja caso vacío (sin resultados) con mensaje descriptivo
- [ ] Test unitario con mock de TavilyClient

---

### US-03: Grafo LangGraph con nodos researcher/analyst/reporter
**Como** agente investigador
**Quiero** un grafo orquestador con 3 nodos secuenciales
**Para que** el flujo de investigación sea determinista y observable

**Criterios de aceptación:**
- [ ] Grafo definido con StateGraph y AgentState TypedDict
- [ ] Nodo `researcher`: ejecuta search_web y retorna contexto_web
- [ ] Nodo `analyst`: pasa contexto al LLM para análisis
- [ ] Nodo `reporter`: genera reporte Markdown estructurado
- [ ] Flujo: researcher → analyst → reporter → END
- [ ] Grafo compilable con `build_graph()`
- [ ] Test de integración del grafo completo

---

### US-04: Tool generate_report con LLM
**Como** agente investigador
**Quiero** generar un reporte Markdown estructurado usando el LLM
**Para que** el output sea profesional y útil para el usuario

**Criterios de aceptación:**
- [ ] Herramienta `generate_report` decorada con `@tool`
- [ ] Acepta: empresa, contexto_web
- [ ] LLM genera reporte con secciones: Resumen Ejecutivo, Eventos Clave, Análisis de Riesgo, Fuentes
- [ ] Formato Markdown válido
- [ ] Incluye fecha de generación
- [ ] Test unitario con contexto mock

---

### US-05: API REST FastAPI
**Como** frontend (Streamlit)
**Quiero** un endpoint POST /report que reciba empresa y retorne reporte
**Para que** la UI pueda comunicarse con el agente

**Criterios de aceptación:**
- [ ] Endpoint POST /report con Pydantic models (ReportRequest, ReportResponse)
- [ ] Endpoint GET /health retorna {"status": "ok"}
- [ ] Manejo de errores con HTTPException (500)
- [ ] uvicorn sirve la app en host:port configurables
- [ ] Test de integración del endpoint

---

### US-06: UI Streamlit
**Como** usuario final
**Quiero** una interfaz web para ingresar nombre de empresa y ver el reporte
**Para que** pueda usar el agente sin conocimientos técnicos

**Criterios de aceptación:**
- [ ] text_input para nombre de empresa
- [ ] button "Generar Reporte"
- [ ] Spinner durante generación
- [ ] Renderizado del reporte Markdown
- [ ] Manejo de errores (conexión, timeout)
- [ ] Título y configuración de página

---

## SHOULD (v1.0 si hay tiempo)

### US-07: Manejo de errores robusto
**Como** desarrollador
**Quiero** que el agente maneje errores de red, API y LLM gracefully
**Para que** la aplicación no crashee y el usuario reciba feedback

**Criterios de aceptación:**
- [ ] Timeout configurable para Tavily y OpenRouter
- [ ] Retry simple (1 reintento) en caso de error de red
- [ ] Mensajes de error descriptivos en UI
- [ ] Logs estructurados en backend

---

### US-08: Tests unitarios completos
**Como** desarrollador
**Quiero** tests para cada tool, nodo y endpoint
**Para que** el código sea confiable y mantenible

**Criterios de aceptación:**
- [ ] Tests para search_web (mock Tavily)
- [ ] Tests para generate_report (mock LLM)
- [ ] Tests para cada nodo del grafo
- [ ] Tests para endpoints FastAPI
- [ ] Cobertura > 80%

---

### US-09: Prompt engineering optimizado
**Como** agente investigador
**Quiero** prompts bien diseñados para análisis financiero LATAM
**Para que** los reportes sean relevantes y de calidad

**Criterios de aceptación:**
- [ ] System prompt define rol de analista financiero LATAM
- [ ] Prompt incluye instrucciones de formato Markdown
- [ ] Prompt filtra por relevancia financiera (no general news)
- [ ] Prompt maneja caso de poca información disponible

---

## COULD (v1.0 si sobra tiempo)

### US-10: Filtros de fecha en búsqueda
**Como** agente investigador
**Quiero** que la búsqueda se enfoque en las últimas 2 semanas
**Para que** la información sea reciente y relevante

**Criterios de aceptación:**
- [ ] Tavily search con parámetro `days=14` (si soportado)
- [ ] Fallback: incluir fecha en el query string
- [ ] Prompt al LLM enfatiza "últimas 2 semanas"

---

### US-11: Cache simple de queries
**Como** desarrollador
**Quiero** cachear resultados de Tavily para queries repetidas
**Para que** se reduzca el uso de la API gratuita

**Criterios de aceptación:**
- [ ] Cache en memoria (dict con TTL)
- [ ] TTL configurable (default: 1 hora)
- [ ] Key: hash del query + empresa

---

## WON'T (excluido de v1)

| ID | Funcionalidad | Razón de exclusión |
|----|---------------|-------------------|
| W-01 | Qdrant / RAG local | mi-agent es independiente de mi-rag |
| W-02 | Embeddings | No se requiere búsqueda semántica |
| W-03 | Autenticación | Portfolio demo |
| W-04 | Persistencia de reportes | v1 es demo, no requiere historial |
| W-05 | Streaming SSE | Simplificación para v1 |
| W-06 | Docker | Deploy local suficiente en v1 |
| W-07 | CI/CD | Portfolio personal |
| W-08 | Multi-idioma | Inglés/español cubren LATAM |

---

## Dependencias entre stories

```
US-01 (Config)
  ├── US-02 (search_web)
  ├── US-03 (grafo) ← US-02
  │     └── US-04 (generate_report) ← US-03
  ├── US-05 (API) ← US-03
  │     └── US-06 (UI) ← US-05
  └── US-07 (errores) ← todos
```

---

## Estimación de esfuerzo

| Story | Esfuerzo | Prioridad |
|-------|----------|-----------|
| US-01 | 0.5h | Must |
| US-02 | 1h | Must |
| US-03 | 2h | Must |
| US-04 | 1.5h | Must |
| US-05 | 1h | Must |
| US-06 | 1h | Must |
| US-07 | 1.5h | Should |
| US-08 | 2h | Should |
| US-09 | 1h | Should |
| US-10 | 0.5h | Could |
| US-11 | 1h | Could |
| **Total** | **12h** | |

**MVP (Must):** 7h
**Completo (Should):** 10.5h
**Full (Could):** 12h

---

*Documento generado por Product Owner — mi-agent v1.0*
