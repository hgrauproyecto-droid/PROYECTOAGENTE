from google import genai
from google.genai import types
import requests  # Librería para conectar con automatizaciones
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Agente con Automatización Externa",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Agente Autónomo Integrado al Ecosistema")
st.write(
    "Este agente procesa tus solicitudes con Gemini y puede disparar"
    " automatizaciones externas mediante Webhooks."
)

# Obtener la API Key de forma segura
api_key = st.secrets.get("GEMINI_API_KEY")
# URL de tu Webhook de n8n o Make (puedes guardarla también en los Secrets de Streamlit)
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")

if not api_key:
    st.error(
        "⚠️ No se encontró la API Key de Gemini en los Secrets de Streamlit."
    )
else:
    # Inicializar el cliente
    client = genai.Client(api_key=api_key)

    # Inicializar el historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario
    if prompt := st.chat_input(
        "Escribe una tarea o instrucción para el agente..."
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta y opcionalmente disparar automatización
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown(
                "⚙️ *Procesando tarea y evaluando automatización...*"
            )

            try:
                # 1. Si hay un Webhook configurado, enviamos los datos a la capa de automatización (n8n/Make)
                if WEBHOOK_URL:
                    payload = {"mensaje": prompt, "origen": "Streamlit Agent"}
                    requests.post(WEBHOOK_URL, json=payload, timeout=5)

                # 2. Configuración del modelo y herramientas principales
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres un Agente Autónomo avanzado conectado al"
                        " ecosistema de automatización. Resuelve la tarea del"
                        " usuario de forma profesional y clara."
                    ),
                    tools=[{"google_search": {}}],
                )

                response = client.models.generate_content(
                    model="gemini-3.8-flash", contents=prompt, config=config
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
                    f"Ocurrió un error al procesar la solicitud o el webhook: {e}"
                )
