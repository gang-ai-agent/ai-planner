from collections.abc import Awaitable, Callable

from langgraph.graph import END, StateGraph

from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.services.observability.tracing import trace_node

from app.agents.nodes.context_sanitizer import context_sanitizer_node
from app.agents.nodes.critic_agent import critic_agent_node
from app.agents.nodes.input_guardrail import input_guardrail_node
from app.agents.nodes.intent_agent import intent_agent_node
from app.agents.nodes.memory_retrieval import memory_retrieval_node
from app.agents.nodes.memory_writer import memory_writer_node
from app.agents.nodes.output_guardrail import output_guardrail_node
from app.agents.nodes.planning_agent import planning_agent_node
from app.agents.nodes.prompt_builder import prompt_builder_node
from app.agents.nodes.reasoning_agent import reasoning_agent_node
from app.agents.nodes.response_agent import response_agent_node
from app.agents.nodes.retrieval_agent import retrieval_agent_node
from app.agents.nodes.validation_agent import validation_agent_node

Node = Callable[[AgentState, Settings], Awaitable[AgentState]]

STOP_STATUSES = {"blocked", "requires_human_review", "waiting_for_user", "failed"}


def _next_or_end(next_node: str) -> Callable[[dict[str, object]], str]:
    def route(state_dict: dict[str, object]) -> str:
        status = state_dict.get("status")
        return END if status in STOP_STATUSES else next_node

    return route


def build_planner_graph(settings: Settings):
    node_sequence: list[tuple[str, Node]] = [
        ("input_guardrail", input_guardrail_node),
        ("memory_retrieval", memory_retrieval_node),
        ("intent_agent", intent_agent_node),
        ("prompt_builder", prompt_builder_node),
        ("planning_agent", planning_agent_node),
        ("retrieval_agent", retrieval_agent_node),
        ("context_sanitizer", context_sanitizer_node),
        ("reasoning_agent", reasoning_agent_node),
        ("validation_agent", validation_agent_node),
        ("critic_agent", critic_agent_node),
        ("output_guardrail", output_guardrail_node),
        ("response_agent", response_agent_node),
        ("memory_writer", memory_writer_node),
    ]

    graph = StateGraph(dict)

    for name, node in node_sequence:
        async def run_node(state_dict: dict[str, object], node_name: str = name, node_func: Node = node) -> dict[str, object]:
            state = AgentState.model_validate(state_dict)
            result = await trace_node(node_name, node_func, state, settings)
            return result.model_dump(mode="json")

        graph.add_node(name, run_node)

    graph.set_entry_point(node_sequence[0][0])

    for index, (name, _) in enumerate(node_sequence):
        if index == len(node_sequence) - 1:
            graph.add_edge(name, END)
            continue
        next_name = node_sequence[index + 1][0]
        graph.add_conditional_edges(name, _next_or_end(next_name), {next_name: next_name, END: END})

    return graph.compile()


async def run_planner_graph(state: AgentState, settings: Settings) -> AgentState:
    graph = build_planner_graph(settings)
    result = await graph.ainvoke(state.model_dump(mode="json"))
    return AgentState.model_validate(result)
