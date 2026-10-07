from google import genai
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Mi Agente IA Autónomo", page_icon="🤖", layout="centered"
)

st.title("🤖 Mi Agente IA Generativo y Autónomo")
st.write(
    "Este agente corre en la nube de forma gratuita gracias a Google AI Studio y"
    " Streamlit Cloud."
)

# Obtener la API Key de forma segura desde los secretos de Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ No se encontró la API Key de Gemini. Configúrala en los 'Secrets'"
        " de la configuración de tu app en Streamlit Cloud."
    )
else:
    # Inicializar el cliente de Google GenAI
    client = genai.Client(api_key=api_key)

    # Inicializar el historial de chat en la sesión
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores en pantalla
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada del usuario en la parte inferior
    if prompt := st.chat_input("¿Qué deseas hacer hoy?"):
        # Guardar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta del agente
        with st.chat_message("assistant"):
            with st.spinner("El agente está pensando..."):
                try:
                    # Llamada al modelo Gemini Flash
                    response = client.models.generate_content(
                        model="gemini-3.8-flash", contents=prompt
                    )
                    answer = response.text
                    st.markdown(answer)

                    # Guardar respuesta en el historial
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    st.error(f"Ocurrió un error al conectar con la IA: {e}")
