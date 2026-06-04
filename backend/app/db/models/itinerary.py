from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.user import User


class ItineraryRecord(Base, TimestampMixin):
    __tablename__ = "itineraries"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    destination: Mapped[str | None] = mapped_column(String, nullable=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    user: Mapped["User"] = relationship(back_populates="itineraries")
