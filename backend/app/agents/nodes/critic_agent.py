from app.core.config import Settings
from app.schemas.agent_state import AgentState, CriticFinding


async def critic_agent_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "critic_agent"
    if not state.retrieved_documents:
        state.critic_feedback.append(
            CriticFinding(
                severity="medium",
                message="Itinerary has no trusted retrieved evidence yet.",
                suggested_improvement="Run RAG retrieval with destination-specific trusted sources.",
            )
        )
    return state
