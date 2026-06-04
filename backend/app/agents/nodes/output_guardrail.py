from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.services.guardrails.output_safety import assess_output_safety


async def output_guardrail_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "output_guardrail"
    text = state.candidate_itinerary.model_dump_json() if state.candidate_itinerary else ""
    state.output_safety = assess_output_safety(text)
    if state.output_safety.decision == "block":
        state.status = "requires_human_review"
    else:
        state.final_itinerary = state.candidate_itinerary
    return state
