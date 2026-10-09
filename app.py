from google import genai
from google.genai import types
import pypdf
import requests
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Sistema Multi-Agente Ultra-Estable",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Sistema Multi-Agente Autónomo (Modo Ultra-Estable)")
st.write(
    "Arquitectura optimizada y ligera, libre de herramientas externas pesadas"
    " para garantizar respuestas fluidas y sin errores de cuota."
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
  if prompt := st.chat_input("Escribe tu consulta o tarea compleja..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      status_placeholder = st.empty()
      status_placeholder.markdown(
          "🤖 *Procesando con el motor optimizado y estable...*"
      )

      try:
        if WEBHOOK_URL:
          requests.post(
              WEBHOOK_URL,
              json={"mensaje": prompt, "origen": "Ultra-Stable System"},
              timeout=5,
          )

        base_context = prompt
        if document_context:
          base_context = (
              f"Documento de referencia:\n{document_context}\n\nConsulta del"
              f" usuario:\n{prompt}"
          )

        # Usamos gemini-1.5-flash sin herramientas de búsqueda para evitar límites de cuota
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=base_context,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Eres un Sistema Multi-Agente Autónomo de Nivel Empresarial."
                    " Responde y estructura la solución obligatoriamente en"
                    " tres fases claras:\n\n1. 🔍 [Agente Investigador]: Analiza"
                    " el problema y el contexto técnico.\n2. ⚙️ [Agente Ejecutor"
                    " Técnico]: Desarrolla el código, arquitectura o solución"
                    " detallada de forma profesional.\n3. 🛡️ [Agente Auditor de"
                    " Calidad]: Revisa posibles fallos, seguridad y emite el"
                    " dictamen final."
                )
            ),
        )

        status_placeholder.empty()
        final_output = response.text
        st.markdown(final_output)

        st.session_state.messages.append(
            {"role": "assistant", "content": final_output}
        )
      except Exception as e:
        status_placeholder.empty()
        st.error(f"Error en la ejecución: {e}")
