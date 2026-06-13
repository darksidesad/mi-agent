from __future__ import annotations

from langchain_core.tools import tool
from tavily import TavilyClient

from src.config import settings

_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient(api_key=settings.tavily_api_key)
    return _client


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Busca noticias financieras recientes sobre una empresa LATAM en la web.

    Args:
        query: Consulta de búsqueda (nombre de empresa + contexto financiero).
        max_results: Número máximo de resultados a retornar.
    """
    client = _get_client()
    response = client.search(query=query, max_results=max_results)
    results = response.get("results", [])
    if not results:
        return "No se encontraron resultados."

    lines: list[str] = []
    for r in results:
        lines.append(f"**{r['title']}**\n{r['url']}\n{r.get('content', 'Sin contenido')}\n")
    return "\n---\n".join(lines)
