from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.services.validation.accessibility import validate_accessibility
from app.services.validation.budget import validate_budget
from app.services.validation.citations import validate_citations
from app.services.validation.routing import validate_routing
from app.services.validation.schedule import validate_schedule


async def validation_agent_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "validation_agent"
    validators = [validate_budget, validate_schedule, validate_routing, validate_accessibility, validate_citations]
    state.validation_results = [validator(state) for validator in validators]
    if any(not result.passed and result.severity in {"high", "critical"} for result in state.validation_results):
        state.status = "requires_human_review"
    return state
