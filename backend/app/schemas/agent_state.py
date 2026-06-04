from decimal import Decimal
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.guardrails import GuardrailEvent, RetrievalSafetyAssessment, SafetyAssessment
from app.schemas.itinerary import Itinerary, ItineraryVersion
from app.schemas.memory import MemoryRecord, MemoryUpdate, MemoryWriteDecision
from app.schemas.observability import AgentError, AgentEvent, TokenUsage
from app.schemas.rag import RetrievedDocument, SourceCitation
from app.schemas.travel import ChatRequest, Message, TravelConstraint, TravelRequirements, UserPreference


class PlanStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: Literal["pending", "running", "completed", "failed"] = "pending"
    input: dict[str, object] = {}
    output: dict[str, object] = {}
    dependencies: list[str] = []


class ValidationResult(BaseModel):
    rule_name: str
    passed: bool
    severity: str = "low"
    message: str
    suggested_fix: str | None = None


class CriticFinding(BaseModel):
    severity: str = "low"
    message: str
    suggested_improvement: str | None = None


class AgentState(BaseModel):
    schema_version: str = "1.0"

    user_id: str
    thread_id: str
    run_id: str
    trace_id: str | None = None

    current_agent: str | None = None
    current_step: str = "input_guardrail"
    status: Literal[
        "running",
        "waiting_for_user",
        "blocked",
        "requires_human_review",
        "retrying",
        "failed",
        "completed",
    ] = "running"

    messages: list[Message] = []
    raw_user_input: str | None = None
    sanitized_user_input: str | None = None

    input_safety: SafetyAssessment | None = None
    retrieval_safety: list[RetrievalSafetyAssessment] = []
    output_safety: SafetyAssessment | None = None
    guardrail_events: list[GuardrailEvent] = []

    follow_up_questions: list[str] = []
    unresolved_slots: list[str] = []
    travel_requirements: TravelRequirements = Field(default_factory=TravelRequirements)
    constraints: list[TravelConstraint] = []
    preferences: list[UserPreference] = []
    accessibility_requirements: list[str] = []

    retrieved_memories: list[MemoryRecord] = []
    memory_updates: list[MemoryUpdate] = []
    memory_write_decisions: list[MemoryWriteDecision] = []

    plan_steps: list[PlanStep] = []
    active_plan_step_id: str | None = None
    candidate_itinerary: Itinerary | None = None
    itinerary_versions: list[ItineraryVersion] = []
    final_itinerary: Itinerary | None = None

    retrieval_queries: list[str] = []
    retrieved_documents: list[RetrievedDocument] = []
    evidence_summary: str | None = None
    source_citations: list[SourceCitation] = []

    validation_results: list[ValidationResult] = []
    critic_feedback: list[CriticFinding] = []
    retry_count: int = 0
    max_retries: int = 3

    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    estimated_cost_usd: Decimal = Decimal("0")
    agent_events: list[AgentEvent] = []
    errors: list[AgentError] = []

    final_response: str | None = None

    @classmethod
    def from_chat_request(cls, request: ChatRequest, max_retries: int) -> "AgentState":
        thread_id = request.thread_id or str(uuid4())
        run_id = str(uuid4())
        return cls(
            user_id=request.user_id,
            thread_id=thread_id,
            run_id=run_id,
            raw_user_input=request.message,
            messages=[Message(role="user", content=request.message)],
            travel_requirements=request.travel_requirements,
            max_retries=max_retries,
        )
