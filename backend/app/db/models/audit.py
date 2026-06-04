from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AuditRecord(Base, TimestampMixin):
    __tablename__ = "memory_audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    memory_id: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
