from app.schemas.agent_state import AgentState, ValidationResult


def validate_accessibility(_: AgentState) -> ValidationResult:
    return ValidationResult(rule_name="accessibility", passed=True, message="Accessibility check placeholder passed.")
