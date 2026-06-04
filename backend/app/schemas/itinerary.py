from pydantic import BaseModel


class ItineraryActivity(BaseModel):
    time: str | None = None
    title: str
    location: str | None = None
    notes: str | None = None
    importance: str | None = None
    duration: str | None = None
    transport: str | None = None
    ticket: str | None = None
    reservation_required: bool | None = None
    local_specialty: bool = True
    estimated_cost: float | None = None
    citation_ids: list[str] = []


class ItineraryDay(BaseModel):
    day_number: int
    title: str
    activities: list[ItineraryActivity] = []


class MainRouteStop(BaseModel):
    name: str
    stop_type: str = "city_or_area"
    arrival_time_required: str | None = None
    transportation: str | None = None
    estimated_transport_cost: float | None = None
    estimated_total_cost: float | None = None
    background: str
    major_attractions: list[str] = []
    activities: list[str] = []
    local_food: list[str] = []
    shopping: list[str] = []


class DestinationDetailPlan(BaseModel):
    stop_name: str
    highlights: list[ItineraryActivity] = []
    optional_adjustments: list[str] = []
    brief_background: str


class AlternativeOption(BaseModel):
    title: str
    reason: str
    estimated_time: str | None = None
    estimated_cost: float | None = None


class Itinerary(BaseModel):
    destination: str | None = None
    summary: str
    main_route: list[MainRouteStop] = []
    detail_plans: list[DestinationDetailPlan] = []
    alternative_options: list[AlternativeOption] = []
    days: list[ItineraryDay] = []
    estimated_total_cost: float | None = None
    citations: list[str] = []


class ItineraryVersion(BaseModel):
    version: int
    itinerary: Itinerary
    reason: str = "initial"
