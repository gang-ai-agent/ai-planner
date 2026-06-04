from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class SafetyDecision(StrEnum):
    ALLOW = "allow"
    CLARIFY = "clarify"
    BLOCK = "block"
    HUMAN_REVIEW = "human_review"


class SafetySeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyAssessment(BaseModel):
    category: str = "general"
    severity: SafetySeverity = SafetySeverity.LOW
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    decision: SafetyDecision = SafetyDecision.ALLOW
    reasons: list[str] = []


class GuardrailEvent(BaseModel):
    layer: str
    rule_id: str
    action_taken: SafetyDecision
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str | None = None
    details: dict[str, str] = {}


class RetrievalSafetyAssessment(BaseModel):
    document_id: str
    source_url: str | None = None
    trust_score: float = Field(default=0.5, ge=0.0, le=1.0)
    injection_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    allowed: bool = True
    reasons: list[str] = []


class ToolPermission(BaseModel):
    tool_name: str
    permission_scope: str = "read"
    requires_confirmation: bool = True


class OutputValidationResult(BaseModel):
    schema_valid: bool = True
    citations_valid: bool = True
    policy_valid: bool = True
    redactions_applied: list[str] = []
