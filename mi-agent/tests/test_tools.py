from src.tools.search_web import search_web
from src.tools.query_rag import query_rag
from src.tools.generate_report import generate_report


def test_search_web_returns_string():
    result = search_web.invoke({"query": "test"})
    assert isinstance(result, str)


def test_query_rag_returns_string():
    result = query_rag.invoke({"query": "test"})
    assert isinstance(result, str)


def test_generate_report_returns_string():
    result = generate_report.invoke({
        "empresa": "Test Corp",
        "contexto_web": "web data",
        "contexto_rag": "rag data",
    })
    assert isinstance(result, str)
    assert "Test Corp" in result
