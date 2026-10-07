from google import genai
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Mi Agente IA", page_icon="🤖", layout="centered"
)

st.title("🤖 Mi Agente IA en la Nube")
st.write(
    "Este agente opera con el modelo optimizado de Google AI Studio y Streamlit"
    " Cloud."
)

# Obtener la API Key de forma segura
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "⚠️ No se encontró la API Key en los Secrets de Streamlit. Configúrala"
        " en Settings."
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
    if prompt := st.chat_input("Escribe tu mensaje o tarea aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner("El agente está respondiendo..."):
                try:
                    # Usamos el modelo correcto y vigente que exige Google
                    response = client.models.generate_content(
                        model="gemini-3.8-flash", contents=prompt
                    )
                    answer = response.text
                    st.markdown(answer)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as e:
                    st.error(f"Ocurrió un error: {e}")
