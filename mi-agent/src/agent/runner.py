from __future__ import annotations

from src.agent.graph import build_graph

graph = build_graph()


async def run_agent(empresa: str) -> dict:
    """Ejecuta el agente completo para una empresa dada."""
    initial_state = {
        "empresa": empresa,
        "messages": [],
        "contexto_web": "",
        "contexto_rag": "",
        "reporte": "",
    }
    result = await graph.ainvoke(initial_state)
    return result
