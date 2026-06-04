from app.schemas.agent_state import AgentState
from app.schemas.travel import ChatRequest


def test_agent_state_from_chat_request() -> None:
    state = AgentState.from_chat_request(ChatRequest(user_id="u1", message="Plan a trip"), max_retries=3)
    assert state.user_id == "u1"
    assert state.messages[0].content == "Plan a trip"
    assert state.max_retries == 3
