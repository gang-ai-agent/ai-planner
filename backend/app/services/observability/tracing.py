import time
from collections.abc import Awaitable, Callable

from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.schemas.observability import AgentEvent


async def trace_node(
    name: str,
    node: Callable[[AgentState, Settings], Awaitable[AgentState]],
    state: AgentState,
    settings: Settings,
) -> AgentState:
    started = time.perf_counter()
    result = await node(state, settings)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    result.agent_events.append(AgentEvent(agent_name=name, event_type="node_completed", duration_ms=elapsed_ms))
    return result
