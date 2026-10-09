from typing import Any, Dict, List, TypedDict
from typing_extensions import Annotated
import operator


class AgentState(TypedDict):
  task: str
  research_data: Annotated[List[str], operator.add]
  code_generated: str
  execution_result: Dict[str, Any]
  audit_feedback: str
  audit_passed: bool
  iterations: int
