from google import genai
from google.genai import types
import pypdf
import requests
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Sistema Multi-Agente Autónomo",
    page_icon="👥",
    layout="wide",
)

st.title("👥 Sistema Multi-Agente Autónomo en Cascada (Agentic AI)")
st.write(
    "Este sistema coordina tres agentes especializados (Investigador,"
    " Ejecutor y Auditor) para resolver tus tareas con precisión"
    " empresarial."
)

# Obtener credenciales de forma segura
api_key = st.secrets.get("GEMINI_API_KEY")
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")

if not api_key:
    st.error(
        "⚠️ No se encontró la API Key de Gemini en los Secrets de Streamlit."
    )
else:
    client = genai.Client(api_key=api_key)

    # Panel lateral para la base de conocimiento (RAG)
    with st.sidebar:
        st.header("📂 Base de Conocimiento (RAG)")
        uploaded_file = st.file_uploader(
            "Sube tu documento de referencia", type=["txt", "pdf"]
        )
        document_context = ""
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                reader = pypdf.PdfReader(uploaded_file)
                for page in reader.pages:
                    document_context += page.extract_text() + "\n"
            else:
                document_context = uploaded_file.read().decode("utf-8")
            st.success("¡Documento cargado en el sistema multi-agente!")

    # Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input(
        "Escribe la tarea compleja que requiere un equipo de agentes..."
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status_placeholder = st.empty()

            try:
                # Disparar automatización externa si está configurada
                if WEBHOOK_URL:
                    requests.post(
                        WEBHOOK_URL,
                        json={"mensaje": prompt, "origen": "Multi-Agent System"},
                        timeout=5,
                    )

                base_context = prompt
                if document_context:
                    base_context = (
                        f"Documento de referencia:\n{document_context}\n\n"
                        f"Petición:\n{prompt}"
                    )

                # --- PASO 1: AGENTE INVESTIGADOR ---
                status_placeholder.markdown(
                    "🔍 **[Agente 1/3] Investigador:** Recopilando datos y"
                    " analizando contexto..."
                )
                config_research = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres el Agente Investigador. Tu trabajo es"
                        " recopilar información clave, buscar en internet"
                        " datos actualizados y estructurar la base de"
                        " conocimiento inicial para la tarea."
                    ),
                    tools=[{"google_search": {}}],
                )
                research_res = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=base_context,
                    config=config_research,
                )
                research_data = research_res.text

                # --- PASO 2: AGENTE EJECUTOR ---
                status_placeholder.markdown(
                    "⚙️ **[Agente 2/3] Ejecutor Técnico:** Desarrollando la"
                    " solución práctica..."
                )
                config_executor = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres el Agente Ejecutor Técnico. Toma la investigación"
                        " previa y desarrolla la solución práctica, código,"
                        " estrategia o contenido requerido de forma detallada."
                    ),
                    tools=[{"code_execution": {}}],
                )
                executor_res = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=(
                        f"Resultados de investigación:\n{research_data}\n\nTarea"
                        f" original: {prompt}"
                    ),
                    config=config_executor,
                )
                executor_data = executor_res.text

                # --- PASO 3: AGENTE AUDITOR ---
                status_placeholder.markdown(
                    "🛡️ **[Agente 3/3] Auditor de Calidad:** Revisando"
                    " errores y emitiendo el resultado final..."
                )
                config_auditor = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres el Agente Auditor de Calidad y Seguridad. Revisa"
                        " la solución desarrollada por el ejecutor, detecta"
                        " posibles fallos, optimízala y presenta el resultado"
                        " final impecable al usuario."
                    ),
                )
                auditor_res = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=(
                        f"Solución preliminar a auditar:\n{executor_data}"
                    ),
                    config=config_auditor,
                )

                status_placeholder.empty()
                final_answer = auditor_res.text

                # Mostrar resultado final coordinado
                st.markdown(final_answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": final_answer}
                )
            except Exception as e:
                status_placeholder.empty()
                st.error(f"Ocurrió un error en el flujo multi-agente: {e}")
