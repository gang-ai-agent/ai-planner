from app.core.config import Settings
from app.schemas.agent_state import AgentState


async def prompt_builder_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "prompt_builder"
    state.current_step = "prompt_building"
    memory_context = "; ".join(memory.content for memory in state.retrieved_memories[:5])
    if memory_context:
        state.evidence_summary = f"Relevant user memory: {memory_context}"
    return state
