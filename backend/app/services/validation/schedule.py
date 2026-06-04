from app.schemas.agent_state import AgentState, ValidationResult


def validate_schedule(state: AgentState) -> ValidationResult:
    itinerary = state.candidate_itinerary
    if not itinerary or not itinerary.days:
        return ValidationResult(rule_name="schedule", passed=False, severity="high", message="No itinerary days were generated.")
    expected_duration = state.travel_requirements.duration_days
    if expected_duration and len(itinerary.days) != expected_duration:
        return ValidationResult(
            rule_name="schedule",
            passed=False,
            severity="high",
            message=f"Itinerary generated {len(itinerary.days)} days for a {expected_duration}-day request.",
        )
    return ValidationResult(rule_name="schedule", passed=True, message="Schedule check passed.")
