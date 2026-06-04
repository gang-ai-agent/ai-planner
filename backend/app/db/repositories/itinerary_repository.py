from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.itinerary import ItineraryRecord
from app.schemas.itinerary import Itinerary


class ItineraryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, itinerary_id: str) -> Itinerary | None:
        result = await self.session.execute(select(ItineraryRecord).where(ItineraryRecord.id == itinerary_id))
        record = result.scalar_one_or_none()
        if record is None:
            return None
        return Itinerary.model_validate(record.payload)

    async def create(self, *, user_id: str, itinerary: Itinerary) -> str:
        itinerary_id = str(uuid4())
        self.session.add(
            ItineraryRecord(
                id=itinerary_id,
                user_id=user_id,
                destination=itinerary.destination,
                payload=itinerary.model_dump(mode="json"),
            )
        )
        await self.session.flush()
        return itinerary_id
