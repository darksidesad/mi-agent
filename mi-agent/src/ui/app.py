import streamlit as st
import httpx

st.set_page_config(page_title="mi-agent", page_icon=":chart_with_upwards_trend:")
st.title("mi-agent — Investigador Financiero LATAM")

empresa = st.text_input("Nombre de la empresa", placeholder="Ej: Ecopetrol, Bancolombia...")

if st.button("Generar Reporte") and empresa:
    with st.spinner(f"Generando reporte para {empresa}..."):
        try:
            response = httpx.post(
                "http://localhost:8000/report",
                json={"empresa": empresa},
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            st.markdown(data["reporte"])
        except httpx.HTTPStatusError as e:
            st.error(f"Error del servidor: {e.response.status_code}")
        except Exception as e:
            st.error(f"Error de conexión: {e}")
