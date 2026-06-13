from __future__ import annotations

from langchain_core.tools import tool


@tool
def generate_report(
    empresa: str,
    contexto_web: str,
    contexto_rag: str,
) -> str:
    """Genera un reporte financiero estructurado combinando fuentes web y RAG.

    Args:
        empresa: Nombre de la empresa analizada.
        contexto_web: Resultados de la búsqueda web.
        contexto_rag: Resultados de la consulta RAG.
    """
    return f"""# Reporte Financiero: {empresa}

## Resumen Ejecutivo
Este reporte fue generado combinando información de noticias recientes y reportes financieros históricos indexados.

---

## Fuentes Web (Noticias Recientes)
{contexto_web if contexto_web else "No se encontraron noticias recientes."}

---

## Fuentes RAG (Reportes Históricos)
{contexto_rag if contexto_rag else "No se encontraron reportes históricos."}

---

*Reporte generado automáticamente por mi-agent.*
"""
