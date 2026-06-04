from app.schemas.agent_state import AgentState, ValidationResult


def validate_routing(_: AgentState) -> ValidationResult:
    return ValidationResult(rule_name="routing", passed=True, message="Routing check placeholder passed.")
