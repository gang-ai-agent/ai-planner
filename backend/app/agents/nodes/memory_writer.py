from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.services.memory.memory_extractor import extract_memory_updates
from app.services.memory.memory_policy import decide_memory_writes


async def memory_writer_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "memory_writer"
    updates = extract_memory_updates(state.messages)
    state.memory_updates = updates
    state.memory_write_decisions = [decide_memory_writes(update) for update in updates]
    return state
