from app.schemas.guardrails import SafetyAssessment, SafetyDecision, SafetySeverity
from app.services.guardrails.prompt_injection import contains_prompt_injection


def assess_output_safety(text: str) -> SafetyAssessment:
    if contains_prompt_injection(text):
        return SafetyAssessment(
            category="unsafe_output",
            severity=SafetySeverity.HIGH,
            confidence=0.8,
            decision=SafetyDecision.BLOCK,
            reasons=["Output appears to contain hidden or instruction-like text."],
        )
    return SafetyAssessment(category="safe_output", confidence=0.9, decision=SafetyDecision.ALLOW)
