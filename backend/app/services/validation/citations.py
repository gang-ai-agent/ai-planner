from app.schemas.agent_state import AgentState, ValidationResult


def validate_citations(state: AgentState) -> ValidationResult:
    if not state.retrieved_documents:
        return ValidationResult(
            rule_name="citations",
            passed=False,
            severity="medium",
            message="No source documents were attached to the itinerary.",
            suggested_fix="Retrieve trusted travel sources and attach citations before finalizing.",
        )
    return ValidationResult(rule_name="citations", passed=True, message="Citation check passed.")
