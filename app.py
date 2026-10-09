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

st.title("👥 Sistema Multi-Agente Autónomo (Versión Estable con Respaldo)")
st.write(
    "Sistema optimizado con conmutación automática de servidores para evitar"
    " interrupciones por alta demanda."
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
            st.success("¡Documento cargado correctamente!")

    # Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Escribe tu consulta o tarea..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown(
                "🤖 *Procesando con respaldo automático de servidores...*"
            )

            try:
                if WEBHOOK_URL:
                    requests.post(
                        WEBHOOK_URL,
                        json={"mensaje": prompt, "origen": "Agent System"},
                        timeout=5,
                    )

                base_context = prompt
                if document_context:
                    base_context = (
                        f"Documento de referencia:\n{document_context}\n\n"
                        f"Consulta:\n{prompt}"
                    )

                # Lista de modelos de respaldo para evitar bloqueos por alta demanda
                models_to_try = [
                    "gemini-2.5-flash",
                    "gemini-flash-latest",
                    "gemini-2.0-flash",
                ]
                response = None
                last_error = None

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=base_context,
                            config=types.GenerateContentConfig(
                                system_instruction=(
                                    "Eres un sistema multi-agente autónomo"
                                    " estructurado en tres roles que debes"
                                    " presentar claramente en tu"
                                    " respuesta:\n1. 🔍 [Investigador]\n2. ⚙️"
                                    " [Ejecutor Técnico]\n3. 🛡️ [Auditor de"
                                    " Calidad]"
                                )
                            ),
                        )
                        break  # Si la conexión es exitosa, salimos del ciclo
                    except Exception as err:
                        last_error = err
                        continue

                if response is None:
                    raise last_error

                status_placeholder.empty()
                final_answer = response.text
                st.markdown(final_answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": final_answer}
                )
            except Exception as e:
                status_placeholder.empty()
                st.error(
                    f"⚠️ Los servidores están experimentando congestión"
                    f" temporal. Por favor, espera 10 segundos y vuelve a"
                    f" enviar tu mensaje. (Detalle: {e})"
                )
