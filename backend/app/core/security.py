from app.schemas.guardrails import SafetyAssessment, SafetyDecision
from app.services.guardrails.redaction import redact_sensitive_text


def sanitize_user_input(text: str, max_chars: int) -> str:
    normalized = " ".join(text.replace("\x00", "").split())
    return redact_sensitive_text(normalized[:max_chars])


def is_blocked(assessment: SafetyAssessment | None) -> bool:
    return assessment is not None and assessment.decision == SafetyDecision.BLOCK
