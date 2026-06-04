from app.core.config import Settings
from app.schemas.agent_state import AgentState


async def response_agent_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "response_agent"
    if state.final_itinerary:
        state.final_response = state.final_itinerary.summary
        state.status = "completed"
    return state
