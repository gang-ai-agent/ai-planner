class PlannerError(Exception):
    """Base exception for planner-specific failures."""


class GuardrailViolation(PlannerError):
    """Raised when a request or output violates a configured guardrail."""


class ExternalServiceError(PlannerError):
    """Raised when a model, database, or vector service call fails."""
