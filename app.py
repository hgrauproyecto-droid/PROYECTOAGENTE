from google import genai
from google.genai import types
import pypdf
import requests
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Sistema Multi-Agente Optimizado",
    page_icon="👥",
    layout="wide",
)

st.title("👥 Sistema Multi-Agente Autónomo Optimizado (Agentic AI)")
st.write(
    "Este sistema unifica las capacidades de investigación, ejecución y"
    " auditoría en una sola llamada eficiente para evitar límites de cuota."
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
        "Escribe la tarea compleja que requiere el equipo de agentes..."
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown(
                "🤖 *El equipo multi-agente está procesando, investigando y"
                " auditando tu solicitud...*"
            )

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
                        f"Petición del usuario:\n{prompt}"
                    )

                # Sistema multi-agente optimizado en una sola llamada de alta eficiencia
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres un Consejo Directivo y Sistema Multi-Agente"
                        " Autónomo integrado por tres fases consecutivas que"
                        " debes mostrar en tu respuesta:\n"
                        "1. 🔍 **[Agente Investigador]:** Recopila datos y"
                        " analiza contexto.\n"
                        "2. ⚙️ **[Agente Ejecutor Técnico]:** Desarrolla la"
                        " solución práctica o estructura técnica.\n"
                        "3. 🛡️ **[Agente Auditor de Calidad]:** Revisa posibles"
                        " fallos, optimiza y presenta el resultado final"
                        " impecable."
                    ),
                    tools=[
                        {"google_search": {}},
                        {"code_execution": {}},
                    ],
                )

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=base_context,
                    config=config,
                )

                status_placeholder.empty()
                final_answer = response.text
                st.markdown(final_answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": final_answer}
                )
            except Exception as e:
                status_placeholder.empty()
                st.error(f"Ocurrió un error en el sistema multi-agente: {e}")
