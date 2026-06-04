import pytest

from app.agents.graph import run_planner_graph
from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.schemas.travel import ChatRequest, TravelRequirements


@pytest.mark.asyncio
async def test_complete_stub_trip_flow() -> None:
    request = ChatRequest(
        user_id="u1",
        message="Plan a 3 day budget food trip to Montreal.",
        travel_requirements=TravelRequirements(destination="Montreal", budget_max=1200, duration_days=3, travelers=2),
    )
    state = AgentState.from_chat_request(request, max_retries=3)
    result = await run_planner_graph(state, Settings(llm_provider="stub"))
    assert result.status == "completed"
    assert result.final_itinerary is not None
