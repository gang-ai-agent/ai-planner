from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.services.memory.memory_service import MemoryService


async def memory_retrieval_node(state: AgentState, settings: Settings) -> AgentState:
    state.current_agent = "memory_retrieval"
    service = MemoryService(settings)
    state.retrieved_memories = await service.retrieve_user_memories(
        user_id=state.user_id,
        query=state.sanitized_user_input or "",
    )
    return state
