from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AgentEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str
    event_type: str
    duration_ms: int = 0
    model: str | None = None
    tokens: TokenUsage = Field(default_factory=TokenUsage)
    cost: Decimal = Decimal("0")


class AgentError(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_name: str
    error_type: str
    message: str
    recoverable: bool = True
