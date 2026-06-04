from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit import AuditRecord


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(
        self,
        *,
        user_id: str,
        action: str,
        memory_id: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> None:
        self.session.add(
            AuditRecord(user_id=user_id, action=action, memory_id=memory_id, payload=payload or {})
        )
        await self.session.flush()
