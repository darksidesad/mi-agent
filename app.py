"""
Intelligence Brief Generator - Streamlit UI
"""
import os
import sys
import streamlit as st
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Intelligence Brief Generator",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Intelligence Brief Generator")

# --- Tabs ---
tab_generate, tab_database, tab_chat = st.tabs(["🚀 Generar Brief", "🗄️ Base de Datos", "💬 Chat con Historial"])

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuración")
    max_iterations = st.slider("Max iteraciones", 1, 10, 5)
    quality_threshold = st.slider("Score mínimo", 5.0, 10.0, 8.0, 0.5)
    timeout = st.slider("Timeout (segundos)", 60, 600, 300, 30)
    
    st.divider()
    st.header("📊 Estado")
    
    from scripts.tools.qdrant_tool import QdrantTool
    try:
        qdrant = QdrantTool()
        info = qdrant.get_collection_info()
        if "error" not in info:
            st.metric("Documentos en Qdrant", info.get("points_count", 0))
        else:
            st.warning("Qdrant no disponible")
    except Exception:
        st.warning("Qdrant no conectado")

# ===================== TAB 1: GENERAR BRIEF =====================
with tab_generate:
    st.subheader("Generar Intelligence Brief")
    
    query = st.text_area(
        "Escribe tu query de investigación:",
        height=100,
        placeholder="ej: análisis de mercado fintech LATAM",
    )
    
    examples = [
        "análisis de mercado fintech LATAM",
        "tendencias de IA en banca digital 2026",
        "regulación de criptomonedas en Europa",
    ]
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                st.session_state["gen_query"] = ex
                st.rerun()
    
    if "gen_query" in st.session_state and not query:
        query = st.session_state["gen_query"]
    
    generate = st.button("🚀 Generar Brief", type="primary", use_container_width=True)
    
    if generate and query:
        st.divider()
        st.subheader("🔄 Pipeline en ejecución")
        
        step1 = st.status("📦 Descomponiendo query en dimensiones...", expanded=False)
        step2 = st.status("🔍 Investigando fuentes...", expanded=False)
        step3 = st.status("✍️ Generando borrador...", expanded=False)
        step4 = st.status("🔄 Loop Engineering...", expanded=False)
        step5 = st.status("💾 Guardando en Qdrant...", expanded=False)
        
        from scripts.graph.state import create_initial_state
        from scripts.agents.orchestrator import OrchestratorAgent
        from scripts.loops.iteration_manager import IterationManager
        
        import asyncio
        
        async def run():
            manager = IterationManager(
                max_iterations=max_iterations,
                timeout_seconds=timeout,
                quality_threshold=quality_threshold,
            )
            
            state = create_initial_state(query)
            orchestrator = OrchestratorAgent()
            
            state = await orchestrator.decompose_query(state)
            dim_names = [d["name"] for d in state["analysis_dimensions"]]
            step1.write(f"Dimensiones: {', '.join(dim_names)}")
            step1.update(state="complete")
            
            state = await orchestrator.research_parallel(state)
            n_tavily = len(state.get("tavily_results", []))
            n_qdrant = len(state.get("qdrant_context", []))
            step2.write(f"🌐 Tavily: {n_tavily} resultados | 🗄️ Qdrant: {n_qdrant} contextos")
            step2.update(state="complete")
            
            state = await orchestrator.synthesize(state)
            brief_len = len(state.get("synthesized_brief", "") or "")
            step3.write(f"Borrador: {brief_len} caracteres")
            step3.update(state="complete")
            
            for iteration in range(max_iterations):
                state["loop_iteration"] = iteration + 1
                state = await orchestrator.self_critique(state)
                state = await orchestrator.refine(state)
                state = await orchestrator.validate(state)
                score = state.get("quality_score", 0.0)
                step4.write(f"Loop {iteration + 1}: score {score}/10")
                if score >= quality_threshold:
                    step4.write("✅ Calidad alcanzada")
                    break
            
            step4.update(state="complete")
            
            state = await orchestrator.deliver(state)
            step5.write("Guardado completo")
            step5.update(state="complete")
            
            return state
        
        state = asyncio.run(run())
        
        st.divider()
        col_score, col_iter, col_time = st.columns(3)
        with col_score:
            st.metric("Score", f"{state.get('quality_score', 0)}/10")
        with col_iter:
            st.metric("Iteraciones", state.get("loop_iteration", 0))
        with col_time:
            duration = state.get("metadata", {}).get("duration_seconds", 0)
            st.metric("Tiempo", f"{duration:.1f}s")
        
        brief = state.get("synthesized_brief", "")
        if brief:
            st.subheader("📄 Intelligence Brief")
            st.markdown(brief)
            
            st.download_button(
                label="📥 Descargar Brief",
                data=brief,
                file_name=f"brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
            )
            
            with st.expander("📊 Fuentes consultadas"):
                for i, r in enumerate(state.get("tavily_results", [])[:15], 1):
                    st.write(f"{i}. [{r.get('title', 'N/A')}]({r.get('url', '#')}) — {r.get('dimension', '')}")

# ===================== TAB 2: BASE DE DATOS =====================
with tab_database:
    st.subheader("🗄️ Contenido de Qdrant")
    st.caption("Todos los briefs y fuentes almacenados de investigaciones anteriores")
    
    if st.button("🔄 Actualizar datos", key="refresh_db"):
        st.rerun()
    
    try:
        qdrant = QdrantTool()
        points = qdrant.get_all_points(limit=100)
        
        if not points:
            st.info("La base de datos está vacía. Genera un brief primero para guardar datos.")
        else:
            st.metric("Total de documentos", len(points))
            
            # Filter by type
            types = list(set(p["type"] for p in points))
            selected_type = st.selectbox("Filtrar por tipo:", ["Todos"] + types)
            
            filtered = points if selected_type == "Todos" else [p for p in points if p["type"] == selected_type]
            
            for point in filtered:
                with st.expander(f"📋 {point.get('query', point.get('title', 'Sin título'))[:80]} — {point['date']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Tipo:** {point['type']}")
                        st.write(f"**Categoría:** {point['category']}")
                        st.write(f"**Fuente:** {point['source']}")
                        if point.get('url'):
                            st.write(f"**URL:** [{point['url']}]({point['url']})")
                    with col2:
                        st.write(f"**ID:** `{point['id'][:12]}...`")
                    
                    st.divider()
                    st.write(point["content"])
    except Exception as e:
        st.error(f"Error conectando a Qdrant: {e}")

# ===================== TAB 3: CHAT CON HISTORIAL =====================
with tab_chat:
    st.subheader("💬 Preguntar sobre investigaciones anteriores")
    st.caption("Busca en la base de datos de Qdrant usando lenguaje natural")
    
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []
    
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("📚 Fuentes encontradas"):
                    for s in msg["sources"]:
                        st.write(f"- [{s.get('query', s.get('title', 'N/A'))}] (score: {s.get('score', 0):.2f})")
    
    chat_input = st.chat_input("Pregunta sobre tus investigaciones...")
    
    if chat_input:
        st.session_state["chat_messages"].append({"role": "user", "content": chat_input})
        
        with st.chat_message("user"):
            st.write(chat_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Buscando en Qdrant..."):
                try:
                    from scripts.tools.openrouter_tool import OpenRouterTool
                    llm = OpenRouterTool()
                    
                    qdrant = QdrantTool()
                    results = qdrant.search_by_text_local(
                        text=chat_input,
                        embedding_func=llm.get_embedding,
                        limit=5,
                        score_threshold=0.3,
                    )
                    
                    if not results:
                        response = "No encontré información relevante en la base de datos. Genera un brief primero para poblar la base."
                        sources = []
                    else:
                        context = "\n\n".join([
                            f"[{r['category']}] {r['content']}"
                            for r in results
                        ])
                        
                        prompt = f"""Basándote en el siguiente contexto de investigaciones anteriores, responde la pregunta del usuario.

CONTEXTO:
{context}

PREGUNTA: {chat_input}

Responde de forma clara y concisa. Si el contexto no contiene suficiente información, dilo."""
                        
                        import asyncio
                        response = asyncio.run(llm.generate(
                            prompt,
                            system_prompt="Eres un asistente que responde preguntas basándose en investigaciones previas guardadas en la base de datos.",
                            max_tokens=1000,
                        ))
                        sources = results
                    
                    st.write(response)
                    
                    if sources:
                        with st.expander("📚 Fuentes encontradas"):
                            for s in sources:
                                st.write(f"- **{s.get('query', s.get('title', 'N/A'))}** (score: {s.get('score', 0):.2f})")
                    
                    st.session_state["chat_messages"].append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources,
                    })
                
                except Exception as e:
                    st.error(f"Error: {e}")

# --- Footer ---
st.divider()
st.caption("Stack: LangGraph | Tavily API | Qdrant | OpenRouter | Streamlit")