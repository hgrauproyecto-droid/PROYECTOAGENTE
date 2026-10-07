from google import genai
from google.genai import types
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Sistema Multi-Agente con Roles Dinámicos",
    page_icon="👥",
    layout="centered",
)

st.title("👥 Sistema Multi-Agente con Roles Dinámicos")
st.write(
    "Este agente analiza tu solicitud, selecciona al **experto ideal** de"
    " forma automática y resuelve la tarea usando internet."
)

# Obtener la API Key de forma segura
api_key = st.secrets.get("GEMINI_API_KEY")

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
    if prompt := st.chat_input("¿Qué tarea compleja deseas resolver hoy?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta con asignación dinámica de roles
        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.markdown(
                "🔄 *Analizando la tarea y asignando al rol experto ideal...*"
            )

            try:
                # CONFIGURACIÓN DE ROLES EXPERTOS AUTOMÁTICos
                config = types.GenerateContentConfig(
                    system_instruction=(
                        "Eres un Meta-Agente Orquestador experto. Analiza la"
                        " petición del usuario y adopta automáticamente el rol"
                        " profesional más adecuado para resolverla (por"
                        " ejemplo: Ingeniero de Software Senior, Consultor de"
                        " Negocios, Redactor Creativo, Científico de Datos o"
                        " Investigador). Estructura tu respuesta indicando"
                        " primero qué rol experto has asumido para desarrollar"
                        " la tarea de forma óptima."
                    ),
                    tools=[{"google_search": {}}],
                )

                response = client.models.generate_content(
                    model="gemini-3.8-flash", contents=prompt, config=config
                )

                status_placeholder.empty()  # Limpiar el mensaje de carga
                answer = response.text
                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                status_placeholder.empty()
                st.error(f"Ocurrió un error al conectar con la IA: {e}")
