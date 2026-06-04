from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.db.repositories.audit_repository import AuditRepository
from app.db.repositories.memory_repository import MemoryRepository
from app.schemas.memory import MemoryCreateRequest, MemoryRecord

router = APIRouter(prefix="/memories", tags=["memories"])


@router.get("/{user_id}", response_model=list[MemoryRecord])
async def list_memories(
    user_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> list[MemoryRecord]:
    return await MemoryRepository(session).list_for_user(user_id)


@router.post("/{user_id}", response_model=MemoryRecord, status_code=status.HTTP_201_CREATED)
async def create_memory(
    user_id: str,
    request: MemoryCreateRequest,
    session: AsyncSession = Depends(db_session_dependency),
) -> MemoryRecord:
    repository = MemoryRepository(session)
    memory = await repository.create(
        user_id=user_id,
        memory_type=request.memory_type,
        content=request.content,
        confidence=request.confidence,
        sensitivity=request.sensitivity,
    )
    await AuditRepository(session).record(user_id=user_id, action="memory_created", memory_id=memory.id)
    await session.commit()
    return memory


@router.delete("/{user_id}/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    user_id: str,
    memory_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> None:
    deleted = await MemoryRepository(session).delete_for_user(user_id=user_id, memory_id=memory_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    await AuditRepository(session).record(user_id=user_id, action="memory_deleted", memory_id=memory_id)
    await session.commit()
