from app.core.config import Settings
from app.core.security import sanitize_user_input
from app.schemas.agent_state import AgentState
from app.schemas.guardrails import GuardrailEvent, SafetyDecision
from app.services.guardrails.input_safety import assess_input_safety


async def input_guardrail_node(state: AgentState, settings: Settings) -> AgentState:
    state.current_agent = "input_guardrail"
    state.current_step = "input_guardrail"
    state.sanitized_user_input = sanitize_user_input(state.raw_user_input or "", settings.max_user_input_chars)
    state.input_safety = assess_input_safety(state.sanitized_user_input)
    state.guardrail_events.append(
        GuardrailEvent(
            layer="input",
            rule_id=state.input_safety.category,
            action_taken=state.input_safety.decision,
            trace_id=state.trace_id,
            details={"severity": state.input_safety.severity},
        )
    )
    if state.input_safety.decision == SafetyDecision.BLOCK:
        state.status = "blocked"
        state.final_response = "I cannot help with that request, but I can help plan a safe vacation itinerary."
    elif state.input_safety.decision == SafetyDecision.CLARIFY:
        state.status = "waiting_for_user"
        state.follow_up_questions.append("Could you rephrase your vacation planning request with the destination, timing, or travel goals?")
    return state
