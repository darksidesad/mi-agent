import pytest
from src.agent.graph import build_graph


def test_graph_compiles():
    graph = build_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_graph_returns_reporte():
    graph = build_graph()
    initial_state = {
        "empresa": "Test",
        "messages": [],
        "contexto_web": "",
        "contexto_rag": "",
        "reporte": "",
    }
    result = await graph.ainvoke(initial_state)
    assert "reporte" in result
    assert len(result["reporte"]) > 0
