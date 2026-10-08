from google import genai
from google.genai import types
import pypdf
import requests
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Agente con Memoria y RAG",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Agente Autónomo con Memoria y Base de Conocimiento (RAG)")
st.write(
    "Este agente cuenta con capacidad de automatización y lectura de documentos"
    " externos para enriquecer sus respuestas."
)

# Obtener la API Key y Webhook de forma segura
api_key = st.secrets.get("GEMINI_API_KEY")
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")

if not api_key:
    st.error(
        "⚠️ No se encontró la API Key de Gemini en los Secrets de Streamlit."
    )
else:
    # Inicializar el cliente
    client = genai.Client(api_key=api_key)

    # --- PANEL LATERAL PARA LA CAPA DE MEMORIA Y DOCUMENTOS (RAG) ---
    with st.sidebar:
        st.header("📂 Base de Conocimiento")
        st.write(
            "Sube un archivo de texto o PDF para que el agente lo lea y lo"
            " use como contexto."
        )
        uploaded_file = st.file_uploader(
            "Sube tu documento aquí", type=["txt", "pdf"]
        )

        document_context = ""
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                reader = pypdf.PdfReader(uploaded_file)
                for page in reader.pages:
                    document_context += page.extract_text() + "\n"
            else:
                document_context = uploaded_file.read().decode("utf-8")
            st.success("¡Documento cargado en la memoria del agente!")

    # Inicializar el historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input("Pregúntale algo al agente o sobre tu documento..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta integrando el documento subido
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown(
                "🧠 *Analizando memoria, contexto y generando respuesta...*"
            )

            try:
                # Disparar automatización externa si está configurada
                if WEBHOOK_URL:
                    payload = {
                        "mensaje": prompt,
                        "origen": "Streamlit Agent - RAG",
                    }
                    requests.post(WEBHOOK_URL, json=payload, timeout=5)

                # Construir el prompt completo uniendo el contexto del documento si existe
                final_prompt = prompt
                if document_context:
                    final_prompt = (
                        f"Utiliza el siguiente documento de referencia para"
                        f" responder a la pregunta del usuario:\n\n--- DOCUMENTO"
                        f" ---\n{document_context}\n\n--- PREGUNTA ---\n{prompt}"
                    )

                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres un Agente Autónomo avanzado con memoria"
                        " contextual. Analiza la información aportada en los"
                        " documentos de referencia y responde con precisión y"
                        " claridad."
                    ),
                    tools=[{"google_search": {}}],
                )

                response = client.models.generate_content(
                    model="gemini-3.8-flash", contents=final_prompt, config=config
                )

                status_placeholder.empty()
                answer = response.text
                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                status_placeholder.empty()
                st.error(
                    f"Ocurrió un error al procesar la memoria o la consulta: {e}"
                )
