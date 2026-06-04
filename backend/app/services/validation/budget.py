from app.schemas.agent_state import AgentState, ValidationResult


def validate_budget(state: AgentState) -> ValidationResult:
    req = state.travel_requirements
    itinerary = state.candidate_itinerary
    if itinerary and req.budget_max and itinerary.estimated_total_cost and itinerary.estimated_total_cost > req.budget_max:
        return ValidationResult(rule_name="budget", passed=False, severity="high", message="Estimated cost exceeds budget.")
    return ValidationResult(rule_name="budget", passed=True, message="Budget check passed.")
