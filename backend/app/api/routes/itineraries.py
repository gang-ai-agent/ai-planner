from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import db_session_dependency
from app.db.repositories.itinerary_repository import ItineraryRepository
from app.schemas.itinerary import Itinerary

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


@router.get("/{itinerary_id}", response_model=Itinerary)
async def get_itinerary(
    itinerary_id: str,
    session: AsyncSession = Depends(db_session_dependency),
) -> Itinerary:
    itinerary = await ItineraryRepository(session).get(itinerary_id)
    if itinerary is None:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary
