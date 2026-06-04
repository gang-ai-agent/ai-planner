from datetime import date
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.guardrails import GuardrailEvent
from app.schemas.itinerary import Itinerary


class TravelStyle(StrEnum):
    LUXURY = "luxury"
    MID_RANGE = "mid_range"
    BUDGET = "budget"
    BACKPACKING = "backpacking"


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    role: str
    content: str


class TravelConstraint(BaseModel):
    name: str
    value: str
    hard: bool = True


class UserPreference(BaseModel):
    name: str
    value: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TravelRequirements(BaseModel):
    destination: str | None = None
    budget_min: float | None = None
    budget_max: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    duration_days: int | None = Field(default=None, ge=1)
    travelers: int | None = Field(default=None, ge=1)
    travel_style: TravelStyle | None = None
    interests: list[str] = []
    transportation_preferences: list[str] = []
    accommodation_preferences: list[str] = []
    special_constraints: list[str] = []


class ChatRequest(BaseModel):
    user_id: str
    message: str
    thread_id: str | None = None
    travel_requirements: TravelRequirements = Field(default_factory=TravelRequirements)


class ChatResponse(BaseModel):
    thread_id: str
    run_id: str
    status: str
    message: str
    follow_up_questions: list[str] = []
    itinerary: Itinerary | None = None
    guardrail_events: list[GuardrailEvent] = []
