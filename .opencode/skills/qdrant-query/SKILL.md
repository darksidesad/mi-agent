---
name: qdrant-query
description: Skill para búsquedas vectoriales en Qdrant. Usa cuando se necesite recuperar contexto histórico o similar semántico.
---

# Qdrant Query Skill

## Configuración
- URL: `QDRANT_URL` (variable de entorno)
- API Key: `QDRANT_API_KEY` (variable de entorno)
- Collection: `intelligence_briefs`

## Uso
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Búsqueda por similitud
results = client.search(
    collection_name="intelligence_briefs",
    query_vector=[0.1, 0.2, ...],  # Embedding de la query
    limit=10,
    score_threshold=0.7
)

# Búsqueda con filtros
results = client.search(
    collection_name="intelligence_briefs",
    query_vector=embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="metadata.category",
                match=MatchValue(value="fintech")
            )
        ]
    ),
    limit=5
)
```

## Parámetros
- `limit`: int (max resultados)
- `score_threshold`: float (0-1, similitud mínima)
- `query_filter`: Filter (filtros de metadata)

## Metadata indexing
```json
{
  "source": "tavily|qdrant",
  "category": "fintech|regulation|market|...",
  "date": "2026-06-10",
  "language": "es|en",
  "relevance_score": 0.95
}
```