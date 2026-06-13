from __future__ import annotations

from langchain_core.tools import tool
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from src.config import settings

_client: QdrantClient | None = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return _client


@tool
def query_rag(query: str, empresa: str | None = None, top_k: int = 5) -> str:
    """Consulta los reportes financieros indexados en Qdrant (mi-rag).

    Args:
        query: Pregunta o búsqueda semántica sobre reportes financieros.
        empresa: Filtrar por nombre de empresa específica (opcional).
        top_k: Número de resultados a recuperar.
    """
    client = _get_client()
    collection = settings.qdrant_collection

    query_filter = None
    if empresa:
        query_filter = Filter(
            must=[FieldCondition(key="empresa", match=MatchValue(value=empresa))]
        )

    results = client.query_points(
        collection_name=collection,
        query=query,
        query_filter=query_filter,
        limit=top_k,
    )

    if not results.points:
        return "No se encontraron documentos relevantes en Qdrant."

    chunks: list[str] = []
    for point in results.points:
        payload = point.payload or {}
        texto = payload.get("text", payload.get("content", "Sin contenido"))
        fuente = payload.get("fuente", "desconocida")
        chunks.append(f"[Fuente: {fuente}]\n{texto}")
    return "\n\n---\n\n".join(chunks)
