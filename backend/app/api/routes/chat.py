from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_planner_graph
from app.api.dependencies import db_session_dependency, settings_dependency
from app.core.config import Settings
from app.db.repositories.itinerary_repository import ItineraryRepository
from app.db.repositories.memory_repository import MemoryRepository
from app.db.repositories.run_repository import RunRepository
from app.schemas.agent_state import AgentState
from app.schemas.travel import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, settings: Settings = Depends(settings_dependency)) -> ChatResponse:
    state = AgentState.from_chat_request(request, max_retries=settings.max_agent_retries)
    result = await run_planner_graph(state, settings=settings)
    return ChatResponse(
        thread_id=result.thread_id,
        run_id=result.run_id,
        status=result.status,
        message=result.final_response or "I need a little more information before I can plan this trip.",
        follow_up_questions=result.follow_up_questions,
        itinerary=result.final_itinerary,
        guardrail_events=result.guardrail_events,
    )


@router.post("/persisted", response_model=ChatResponse)
async def persisted_chat(
    request: ChatRequest,
    settings: Settings = Depends(settings_dependency),
    session: AsyncSession = Depends(db_session_dependency),
) -> ChatResponse:
    state = AgentState.from_chat_request(request, max_retries=settings.max_agent_retries)
    result = await run_planner_graph(state, settings=settings)
    await RunRepository(session).ensure_thread_and_run(
        user_id=result.user_id,
        thread_id=result.thread_id,
        run_id=result.run_id,
        status=result.status,
    )
    if result.final_itinerary is not None:
        await ItineraryRepository(session).create(user_id=result.user_id, itinerary=result.final_itinerary)
    memory_repository = MemoryRepository(session)
    for decision in result.memory_write_decisions:
        if decision.should_write:
            await memory_repository.create(
                user_id=result.user_id,
                memory_type=decision.update.memory_type,
                content=decision.update.content,
                confidence=decision.update.confidence,
            )
    await session.commit()
    return ChatResponse(
        thread_id=result.thread_id,
        run_id=result.run_id,
        status=result.status,
        message=result.final_response or "I need a little more information before I can plan this trip.",
        follow_up_questions=result.follow_up_questions,
        itinerary=result.final_itinerary,
        guardrail_events=result.guardrail_events,
    )
