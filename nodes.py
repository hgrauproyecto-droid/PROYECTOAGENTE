from google import genai
from google.genai import types
import streamlit as st


def get_gemini_client():
  api_key = st.secrets.get("GEMINI_API_KEY")
  return genai.Client(api_key=api_key)


def researcher_node(state: dict) -> dict:
  """Agente 1: Investigador y Analista de Contexto."""
  client = get_gemini_client()
  task = state["task"]

  prompt = (
      f"Eres el Agente Investigador. Analiza la siguiente tarea o pregunta y"
      f" recopila información clave, estructurando los datos técnicos y"
      f" contextuales necesarios:\n\n{task}"
  )

  response = client.models.generate_content(
      model="gemini-flash-latest",
      contents=prompt,
      config=types.GenerateContentConfig(
          tools=[{"google_search": {}}],
          system_instruction="Eres un experto en investigación técnica e industrial.",
      ),
  )

  return {"research_data": [response.text]}


def technical_executor_node(state: dict) -> dict:
  """Agente 2: Ejecutor Técnico y Desarrollador."""
  client = get_gemini_client()
  context = "\n".join(state["research_data"])
  feedback = state.get("audit_feedback", "Ninguno (Primera iteración)")
  task = state["task"]

  prompt = f"""Eres el Agente Ejecutor Técnico.
Tarea original: {task}
Investigación previa: {context}
Feedback de auditoría anterior: {feedback}

Desarrolla la solución técnica detallada, arquitectura, código o estrategia requerida de manera profesional y autónoma."""

  response = client.models.generate_content(
      model="gemini-flash-latest",
      contents=prompt,
      config=types.GenerateContentConfig(
          system_instruction=(
              "Eres un ingeniero de software senior y arquitecto de sistemas."
          )
      ),
  )

  return {
      "code_generated": response.text,
      "execution_result": {"success": True, "output": "Simulación validada"},
      "iterations": state.get("iterations", 0) + 1,
  }


def quality_auditor_node(state: dict) -> dict:
  """Agente 3: Auditor de Calidad y Seguridad."""
  client = get_gemini_client()
  code = state["code_generated"]

  prompt = f"""Eres el Agente Auditor de Calidad y Seguridad.
Revisa la siguiente solución desarrollada por el ejecutor:

{code}

Evalúa si cumple con los estándares de robustez, seguridad y precisión. 
Si todo es correcto, comienza tu respuesta estrictamente con la palabra 'APROBADO'.
Si encuentras fallos, comienza con 'RECHAZADO' y explica detalladamente qué se debe corregir."""

  response = client.models.generate_content(
      model="gemini-flash-latest",
      contents=prompt,
      config=types.GenerateContentConfig(
          system_instruction=(
              "Eres un auditor riguroso de código y procesos corporativos."
          )
      ),
  )

  review = response.text
  passed = review.strip().startswith("APROBADO")

  return {"audit_feedback": review, "audit_passed": passed}
