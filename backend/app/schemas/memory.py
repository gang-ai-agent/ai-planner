from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class MemoryType(StrEnum):
    USER_PREFERENCE = "user_preference"
    EPISODIC_TRIP = "episodic_trip"
    ACCESSIBILITY = "accessibility"
    DIETARY = "dietary"
    SYSTEM = "system"


class MemoryRecord(BaseModel):
    id: str
    type: MemoryType = MemoryType.USER_PREFERENCE
    content: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = "user"
    qdrant_point_id: str | None = None
    sensitivity: str = "normal"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryUpdate(BaseModel):
    memory_type: MemoryType
    content: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_message_id: str | None = None


class MemoryWriteDecision(BaseModel):
    update: MemoryUpdate
    should_write: bool
    reason: str


class MemoryCreateRequest(BaseModel):
    memory_type: MemoryType = MemoryType.USER_PREFERENCE
    content: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    sensitivity: str = "normal"
