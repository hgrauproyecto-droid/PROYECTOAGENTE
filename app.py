from google import genai
from google.genai import types
import pypdf
import requests
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Sistema Multi-Agente Autónomo",
    page_icon="⚡",
    layout="wide",
)

st.title(
    "⚡ Sistema Multi-Agente Autónomo (Arquitectura Unificada de Alta"
    " Eficiencia)"
)
st.write(
    "Sistema optimizado para coordinar los tres roles especializados"
    " (Investigador, Ejecutor y Auditor) en una sola llamada estructurada para"
    " garantizar estabilidad total y evitar el error 429."
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
      st.success("¡Documento cargado correctamente en la memoria!")

  # Inicializar historial de chat
  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Entrada del usuario
  if prompt := st.chat_input(
      "Escribe la tarea compleja para el consejo multi-agente..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      status_placeholder = st.empty()
      status_placeholder.markdown(
          "🤖 *El consejo multi-agente está investigando, ejecutando y"
          " auditando tu solicitud...*"
      )

      try:
        # Disparar automatización externa si está configurada
        if WEBHOOK_URL:
          requests.post(
              WEBHOOK_URL,
              json={"mensaje": prompt, "origen": "Unified Agent System"},
              timeout=5,
          )

        base_context = prompt
        if document_context:
          base_context = (
              f"Documento de referencia de la Base de Conocimiento:\n"
              f"{document_context}\n\nConsulta o Tarea del Usuario:\n{prompt}"
          )

        # Instrucciones de sistema para estructurar los tres roles de forma interna y atómica
        system_instruction = (
            "Eres un Sistema Multi-Agente Autónomo de Nivel Empresarial."
            " Procesa la tarea del usuario estructurando tu respuesta final de"
            " manera clara en tres fases obligatorias:\n\n1. 🔍 **[Agente"
            " Investigador]:** Analiza el contexto, recopila datos técnicos"
            " clave y evalúa las fuentes o requerimientos.\n2. ⚙️ **[Agente"
            " Ejecutor Técnico]:** Desarrolla la solución práctica, código,"
            " arquitectura o guías detalladas solicitadas.\n3. 🛡️ **[Agente"
            " Auditor de Calidad]:** Revisa la solución, valida la robustez,"
            " la seguridad y emite el dictamen final de aprobación u"
            " optimización."
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=base_context,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[{"google_search": {}}],
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
        st.error(
            f"⚠️ Ocurrió un error al procesar la solicitud: {e}. Por favor,"
            f" intenta de nuevo en unos segundos."
        )
          
