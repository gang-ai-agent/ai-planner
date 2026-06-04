from app.schemas.guardrails import SafetyAssessment, SafetyDecision, SafetySeverity
from app.services.guardrails.prompt_injection import contains_prompt_injection

BLOCKED_PATTERNS = (
    "steal",
    "exfiltrate",
    "bypass payment",
    "fake passport",
    "ignore safety",
)


def assess_input_safety(text: str) -> SafetyAssessment:
    lowered = text.lower()
    if any(pattern in lowered for pattern in BLOCKED_PATTERNS):
        return SafetyAssessment(
            category="malicious_request",
            severity=SafetySeverity.HIGH,
            confidence=0.85,
            decision=SafetyDecision.BLOCK,
            reasons=["Request appears unrelated to safe travel planning or asks for misuse."],
        )
    if contains_prompt_injection(text):
        return SafetyAssessment(
            category="prompt_injection",
            severity=SafetySeverity.MEDIUM,
            confidence=0.75,
            decision=SafetyDecision.CLARIFY,
            reasons=["Input contains instruction-like text that may attempt to override the agent."],
        )
    if len(text.strip()) < 3:
        return SafetyAssessment(
            category="empty_or_unclear",
            severity=SafetySeverity.LOW,
            confidence=1.0,
            decision=SafetyDecision.CLARIFY,
            reasons=["Input is too short to plan a trip."],
        )
    return SafetyAssessment(category="safe", confidence=0.9, decision=SafetyDecision.ALLOW)
