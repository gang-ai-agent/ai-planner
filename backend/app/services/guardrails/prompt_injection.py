from app.schemas.guardrails import RetrievalSafetyAssessment
from app.schemas.rag import RetrievedDocument

INJECTION_PATTERNS = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "developer message",
    "reveal your instructions",
    "jailbreak",
    "act as",
    "tool call",
)


def contains_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in INJECTION_PATTERNS)


def assess_retrieved_document(document: RetrievedDocument) -> RetrievalSafetyAssessment:
    risky = contains_prompt_injection(document.snippet)
    return RetrievalSafetyAssessment(
        document_id=document.id,
        source_url=document.source_url,
        trust_score=float(document.metadata.get("trust_score", "0.5")),
        injection_risk=0.9 if risky else 0.0,
        allowed=not risky,
        reasons=["possible indirect prompt injection"] if risky else [],
    )
