from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.itinerary import ItineraryRecord
    from app.db.models.memory import Memory
    from app.db.models.thread import Thread


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)

    threads: Mapped[list["Thread"]] = relationship(back_populates="user")
    memories: Mapped[list["Memory"]] = relationship(back_populates="user")
    itineraries: Mapped[list["ItineraryRecord"]] = relationship(back_populates="user")
