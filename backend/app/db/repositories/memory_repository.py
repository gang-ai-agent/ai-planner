from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.memory import Memory
from app.schemas.memory import MemoryRecord, MemoryType


class MemoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(self, user_id: str) -> list[MemoryRecord]:
        result = await self.session.execute(
            select(Memory).where(Memory.user_id == user_id).order_by(Memory.updated_at.desc())
        )
        return [self._to_schema(row) for row in result.scalars().all()]

    async def create(
        self,
        *,
        user_id: str,
        memory_type: MemoryType,
        content: str,
        confidence: float,
        sensitivity: str = "normal",
        qdrant_point_id: str | None = None,
    ) -> MemoryRecord:
        record = Memory(
            id=str(uuid4()),
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            confidence=confidence,
            sensitivity=sensitivity,
            qdrant_point_id=qdrant_point_id,
        )
        self.session.add(record)
        await self.session.flush()
        return self._to_schema(record)

    async def delete_for_user(self, *, user_id: str, memory_id: str) -> bool:
        result = await self.session.execute(delete(Memory).where(Memory.user_id == user_id, Memory.id == memory_id))
        return bool(result.rowcount)

    def _to_schema(self, record: Memory) -> MemoryRecord:
        return MemoryRecord(
            id=record.id,
            type=MemoryType(record.memory_type),
            content=record.content,
            confidence=float(record.confidence),
            source="stored",
            qdrant_point_id=record.qdrant_point_id,
            sensitivity=record.sensitivity,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
