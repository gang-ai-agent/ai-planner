from app.core.config import Settings
from app.schemas.agent_state import AgentState, PlanStep


async def planning_agent_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "planning_agent"
    state.current_step = "planning"
    state.plan_steps = [
        PlanStep(name="Destination analysis"),
        PlanStep(name="Attractions selection"),
        PlanStep(name="Accommodation planning"),
        PlanStep(name="Transportation planning"),
        PlanStep(name="Daily itinerary generation"),
    ]
    return state
