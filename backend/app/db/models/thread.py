from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.run import AgentRun
    from app.db.models.user import User


class Thread(Base, TimestampMixin):
    __tablename__ = "conversation_threads"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    user: Mapped["User"] = relationship(back_populates="threads")
    runs: Mapped[list["AgentRun"]] = relationship(back_populates="thread")
