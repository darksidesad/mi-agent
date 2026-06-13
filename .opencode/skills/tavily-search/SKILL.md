---
name: tavily-search
description: Skill para búsqueda web en tiempo real usando Tavily API. Usa cuando se necesiten noticias recientes o información actualizada de la web.
---

# Tavily Search Skill

## Configuración
- API Key: `TAVILY_API_KEY` (variable de entorno)
- Rate limit: 1000 requests/mes (plan free)
- Endpoints: `search`, `search` (con filtros)

## Uso
```python
from tavily import TavilyClient

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Búsqueda básica
results = client.search(
    query="fintech LATAM 2026",
    search_depth="advanced",
    max_results=5,
    include_answer=True
)

# Búsqueda con filtros de tiempo
results = client.search(
    query="AI regulations Europe",
    search_depth="basic",
    days=7,  # Últimos 7 días
    max_results=10
)
```

## Parámetros
- `search_depth`: "basic" | "advanced"
- `max_results`: 1-20
- `include_answer`: bool (resumen generado)
- `include_raw_content`: bool (contenido completo)
- `days`: int (filtro de tiempo)

## Ejemplo de respuesta
```json
{
  "answer": "Resumen generado por Tavily...",
  "results": [
    {
      "title": "...",
      "url": "https://...",
      "content": "...",
      "score": 0.95,
      "published_date": "2026-06-10"
    }
  ]
}
```