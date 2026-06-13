from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from src.agent.llm import llm
from src.tools.search_web import search_web
from src.tools.query_rag import query_rag
from src.tools.generate_report import generate_report

tools = [search_web, query_rag, generate_report]
tools_by_name = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)


class AgentState(TypedDict):
    empresa: str
    messages: Annotated[list[BaseMessage], add_messages]
    contexto_web: str
    contexto_rag: str
    reporte: str


def researcher_node(state: AgentState) -> dict:
    """Nodo investigador: busca en web y consulta RAG."""
    empresa = state["empresa"]

    web_result = search_web.invoke({
        "query": f"noticias financieras recientes {empresa} LATAM 2024 2025"
    })
    rag_result = query_rag.invoke({
        "query": f"reporte financiero {empresa}",
        "empresa": empresa,
    })

    return {"contexto_web": web_result, "contexto_rag": rag_result}


def analyst_node(state: AgentState) -> dict:
    """Nodo analista: usa el LLM para interpretar los datos recolectados."""
    empresa = state["empresa"]
    contexto = f"Empresa: {empresa}\n\nContexto Web:\n{state['contexto_web']}\n\nContexto RAG:\n{state['contexto_rag']}"

    response = llm_with_tools.invoke([
        {"role": "system", "content": (
            "Eres un analista financiero experto en empresas LATAM. "
            "Analiza la información proporcionada y genera insights clave."
        )},
        {"role": "user", "content": contexto},
    ])
    return {"messages": [response]}


def reporter_node(state: AgentState) -> dict:
    """Nodo reportero: genera el reporte final estructurado."""
    empresa = state["empresa"]

    report = generate_report.invoke({
        "empresa": empresa,
        "contexto_web": state["contexto_web"],
        "contexto_rag": state["contexto_rag"],
    })
    return {"reporte": report, "messages": [{"role": "assistant", "content": report}]}


def should_continue(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("reporter", reporter_node)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "reporter")
    graph.add_edge("reporter", END)

    return graph.compile()
