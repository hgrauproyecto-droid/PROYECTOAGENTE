from langgraph.graph import END, StateGraph
from nodes import quality_auditor_node, researcher_node, technical_executor_node
from state import AgentState


def create_multi_agent_graph():
  workflow = StateGraph(AgentState)

  # Agregar nodos
  workflow.add_node("investigador", researcher_node)
  workflow.add_node("ejecutor", technical_executor_node)
  workflow.add_node("auditor", quality_auditor_node)

  # Definir rutas y secuencia
  workflow.set_entry_point("investigador")
  workflow.add_edge("investigador", "ejecutor")
  workflow.add_edge("ejecutor", "auditor")

  # Enrutamiento condicional basado en la auditoría
  def decide_continuation(state: AgentState):
    if state["audit_passed"]:
      return END
    if state.get("iterations", 0) >= 2:  # Límite de seguridad de iteraciones
      return END
    return "ejecutor"

  workflow.add_conditional_edges(
      "auditor", decide_continuation, {END: END, "ejecutor": "ejecutor"}
  )

  return workflow.compile()
