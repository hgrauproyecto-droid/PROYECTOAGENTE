from graph import create_multi_agent_graph
import pypdf
import requests
import streamlit as st

st.set_page_config(
    page_title="Sistema Multi-Agente con LangGraph",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Sistema Multi-Agente Autónomo con LangGraph & Gemini")
st.write(
    "Arquitectura distribuida en cascada con ciclos de autocorrección y"
    " control de estado."
)

api_key = st.secrets.get("GEMINI_API_KEY")
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL", "")

if not api_key:
    st.error(
        "⚠️ No se encontró la API Key de Gemini en los Secrets de Streamlit."
    )
else:
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
      st.success("¡Documento cargado al estado del sistema!")

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input(
      "Escribe la tarea compleja para el grafo multi-agente..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      status_placeholder = st.empty()
      status_placeholder.markdown(
          "🔄 *Ejecutando grafo LangGraph (Investigación ➔ Ejecución ➔"
          " Auditoría)...*"
      )

      try:
        if WEBHOOK_URL:
          requests.post(
              WEBHOOK_URL,
              json={"mensaje": prompt, "origen": "LangGraph System"},
              timeout=5,
          )

        initial_task = prompt
        if document_context:
          initial_task = (
              f"Documento de referencia:\n{document_context}\n\nTarea:"
              f" {prompt}"
          )

        # Inicializar y ejecutar el grafo
        app_graph = create_multi_agent_graph()
        initial_state = {
            "task": initial_task,
            "research_data": [],
            "code_generated": "",
            "execution_result": {},
            "audit_feedback": "",
            "audit_passed": False,
            "iterations": 0,
        }

        # Ejecución del grafo paso a paso
        final_state = app_graph.invoke(initial_state)

        status_placeholder.empty()
        final_output = f"""### 🔍 Resultado del Ciclo Multi-Agente LangGraph

#### 1. Investigación y Análisis:
{final_state['research_data'][0] if final_state['research_data'] else 'N/A'}

#### 2. Solución Técnica Desarrollada:
{final_state['code_generated']}

#### 3. Auditoría de Calidad y Validación:
{final_state['audit_feedback']}
"""

        st.markdown(final_output)
        st.session_state.messages.append(
            {"role": "assistant", "content": final_output}
        )
      except Exception as e:
        status_placeholder.empty()
        st.error(f"Error en la ejecución del grafo multi-agente: {e}")
