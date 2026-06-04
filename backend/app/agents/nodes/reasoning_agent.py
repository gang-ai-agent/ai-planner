import json
import re
from dataclasses import dataclass, field

from pydantic import ValidationError

from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.schemas.itinerary import AlternativeOption, DestinationDetailPlan, Itinerary, ItineraryActivity, ItineraryDay, MainRouteStop
from app.schemas.observability import AgentError
from app.schemas.rag import RetrievedDocument
from app.services.llm.provider import get_llm_provider
from app.services.rag.retriever import Retriever


@dataclass
class RouteStop:
    name: str
    days: int
    country: str | None = None
    source_names: set[str] = field(default_factory=set)
    attractions: list[str] = field(default_factory=list)
    foods: list[str] = field(default_factory=list)
    shopping: list[str] = field(default_factory=list)

    @property
    def retrieval_name(self) -> str:
        return " ".join(part for part in (self.name, self.country) if part)


async def reasoning_agent_node(state: AgentState, settings: Settings) -> AgentState:
    state.current_agent = "reasoning_agent"
    try:
        state.candidate_itinerary = await _hierarchical_itinerary(state, settings)
        return state
    except Exception as exc:
        state.errors.append(
            AgentError(
                agent_name="reasoning_agent",
                error_type=exc.__class__.__name__,
                message=f"Hierarchical itinerary generation fell back to direct LLM/template output: {exc}",
                recoverable=True,
            )
        )

    if settings.llm_enabled:
        prompt = _build_itinerary_prompt(state)
        try:
            completion = await get_llm_provider(settings).complete(prompt)
            state.candidate_itinerary = _parse_itinerary_completion(completion)
            return state
        except Exception as exc:
            state.errors.append(
                AgentError(
                    agent_name="reasoning_agent",
                    error_type=exc.__class__.__name__,
                    message=f"LLM itinerary generation fell back to template output: {exc}",
                    recoverable=True,
                )
            )

    state.candidate_itinerary = _single_destination_itinerary(state)
    return state


async def _hierarchical_itinerary(state: AgentState, settings: Settings) -> Itinerary:
    req = state.travel_requirements
    destination = req.destination or "your destination"
    duration = req.duration_days or 3
    interests = set(req.interests)
    await _expand_continent_to_country_context(state, settings, destination, duration)
    candidates = _route_candidates_from_documents(state.retrieved_documents, fallback_destination=destination)
    route = await _select_route(state, settings, candidates, duration)
    await _retrieve_stop_details(state, settings, route, interests)
    _enrich_route_from_documents(route, state.retrieved_documents)

    focus = _primary_focus(interests)
    main_route = [
        MainRouteStop(
            name=stop.name,
            arrival_time_required="Use live maps or flight/train search for exact travel time; reserve extra arrival buffer.",
            transportation=_transportation_for_stop(stop),
            estimated_transport_cost=None,
            estimated_total_cost=req.budget_max,
            background=_background_from_retrieval(state, stop),
            major_attractions=_with_fallback(stop.attractions, f"Historic and cultural highlights in {stop.name}"),
            activities=[focus, "neighborhood walking route", "local dining"],
            local_food=_with_fallback(stop.foods, "local specialties from the retrieved guide"),
            shopping=_with_fallback(stop.shopping, "markets, museum shops, and specialty streets from the retrieved guide"),
        )
        for stop in route
    ]

    return Itinerary(
        destination=destination,
        summary=f"A {duration}-day data-driven {focus} itinerary across {', '.join(stop.name for stop in route)}.",
        main_route=main_route,
        detail_plans=[
            DestinationDetailPlan(
                stop_name=stop.name,
                highlights=_city_highlights(stop, interests),
                optional_adjustments=[
                    "If weather is poor, replace outdoor walking with a museum or covered market.",
                    "If the pace feels too tight, turn one attraction block into cafe time or a neighborhood walk.",
                    "If tickets are sold out, keep the exterior route and swap in a nearby district from the retrieved guide.",
                ],
                brief_background=_background_from_retrieval(state, stop)[:500],
            )
            for stop in route
        ],
        alternative_options=[
            AlternativeOption(title="Slower pace", reason="Reduce pressure and leave more free choice time.", estimated_time="half day"),
            AlternativeOption(title="Food-focused swap", reason="Replace one attraction block with a market, food street, or cooking class."),
            AlternativeOption(title="History/art deep dive", reason="Add one major museum or guided historical walk if that matches the user's interest."),
        ],
        days=_build_days_from_route(route, interests),
        estimated_total_cost=req.budget_max,
        citations=_citations_for_route(state, route),
    )


async def _expand_continent_to_country_context(
    state: AgentState, settings: Settings, destination: str, duration: int
) -> None:
    if not settings.qdrant_enabled or not _is_continent_request(destination):
        return
    countries = _country_values_from_documents(state.retrieved_documents)
    if not countries:
        return
    retriever = Retriever(settings)
    max_countries = max(1, min(5, round(duration / 4)))
    existing_ids = {doc.qdrant_point_id or doc.id for doc in state.retrieved_documents}
    for country in countries[:max_countries]:
        query = f"{country} 城市 行程 攻略 景点 美食 交通 门票"
        state.retrieval_queries.append(query)
        documents = await retriever.retrieve(query=query, top_k=4)
        for document in documents:
            key = document.qdrant_point_id or document.id
            if key not in existing_ids:
                state.retrieved_documents.append(document)
                existing_ids.add(key)


async def _select_route(
    state: AgentState, settings: Settings, candidates: list[RouteStop], duration: int
) -> list[RouteStop]:
    if settings.llm_enabled and candidates:
        selected = await _select_route_with_llm(state, settings, candidates, duration)
        if selected:
            return selected
    return _select_route_from_candidates(candidates, duration)


async def _select_route_with_llm(
    state: AgentState, settings: Settings, candidates: list[RouteStop], duration: int
) -> list[RouteStop]:
    candidate_lines = "\n".join(
        f"- name={candidate.name}; country={candidate.country or ''}; sources={', '.join(sorted(candidate.source_names))[:180]}"
        for candidate in candidates[:20]
    )
    prompt = f"""
You are choosing route stops for a vacation planner.
Use only the candidate places listed below. Do not invent countries or cities.
Return JSON only, no Markdown.

Schema:
{{"stops":[{{"name":"place name from candidates","country":"country if known","days":number,"reason":"short reason"}}]}}

User request: {state.sanitized_user_input or state.raw_user_input or ""}
Duration: {duration} days
Known interests: {", ".join(state.travel_requirements.interests) or "balanced culture, food, and city touring"}
Candidates:
{candidate_lines}
Rules:
- Pick a realistic number of stops for the duration.
- The days must sum exactly to {duration}.
- For continent-level requests, pick countries/cities from different candidate countries when useful.
- For country-level requests, pick city/area candidates within that country when available.
""".strip()
    completion = await get_llm_provider(settings).complete(prompt)
    try:
        data = json.loads(_strip_markdown_json(completion))
        stops = data.get("stops", [])
    except (json.JSONDecodeError, AttributeError):
        return []

    by_name = {candidate.name.lower(): candidate for candidate in candidates}
    selected: list[RouteStop] = []
    for item in stops:
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        source = by_name.get(name.lower())
        if not source:
            continue
        days = _positive_int(item.get("days")) or source.days
        selected.append(_copy_stop(source, days=days, country=str(item.get("country") or source.country or "") or None))
    return _normalize_days(selected, duration)


def _select_route_from_candidates(candidates: list[RouteStop], duration: int) -> list[RouteStop]:
    if not candidates:
        return []
    max_stops = max(1, min(5, round(duration / 3)))
    selected = candidates[:max_stops]
    return _normalize_days(selected, duration)


def _normalize_days(route: list[RouteStop], duration: int) -> list[RouteStop]:
    if not route:
        return route
    base = max(1, duration // len(route))
    remaining = duration - base * len(route)
    normalized = []
    for index, stop in enumerate(route):
        normalized.append(_copy_stop(stop, days=base + (1 if index < remaining else 0)))
    return normalized


def _route_candidates_from_documents(documents: list[RetrievedDocument], fallback_destination: str) -> list[RouteStop]:
    scored: dict[tuple[str, str | None], tuple[int, RouteStop]] = {}
    for doc in documents:
        text = _document_text(doc)
        country = _first_metadata_value(text, "国家")
        for city in [*_title_place_values(text), *_city_values(text)]:
            if _is_weak_place_name(city):
                continue
            key = (city, country)
            score, candidate = scored.get(key, (0, RouteStop(name=city, days=1, country=country)))
            candidate.source_names.add(doc.title)
            scored[key] = (score + _candidate_score(doc, city, country), candidate)

    if not scored:
        return [RouteStop(name=fallback_destination, days=1)]

    ordered = sorted(scored.values(), key=lambda item: item[0], reverse=True)
    return [candidate for _, candidate in ordered]


def _country_values_from_documents(documents: list[RetrievedDocument]) -> list[str]:
    scored: dict[str, int] = {}
    for doc in documents:
        text = _document_text(doc)
        country = _first_metadata_value(text, "国家")
        if country:
            scored[country] = scored.get(country, 0) + _candidate_score(doc, country, None)
    return [country for country, _ in sorted(scored.items(), key=lambda item: item[1], reverse=True)]


def _city_values(text: str) -> list[str]:
    cities = []
    for match in re.finditer(r"城市[:：]\s*([^\n\r‣|_。；;]{1,80})", text):
        raw = match.group(1)
        for city in re.split(r"[,，、/]| and ", raw):
            city = _clean_place_name(city)
            if city:
                cities.append(city)
    return list(dict.fromkeys(cities))


def _title_place_values(text: str) -> list[str]:
    values = []
    for match in re.finditer(r"([\u4e00-\u9fff]{2,12}?)(?:旅游攻略|攻略)", text):
        value = _clean_place_name(match.group(1))
        if value:
            values.append(value)
    return list(dict.fromkeys(values))


def _first_metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"{key}[:：]\s*([^\n\r‣|_。；;]{{1,40}})", text)
    return _clean_place_name(match.group(1)) if match else None


def _candidate_score(doc: RetrievedDocument, city: str, country: str | None) -> int:
    title = doc.title or ""
    score = 1
    if city in title:
        score += 8
    if country and country in title:
        score += 3
    score += int((doc.score or 0) * 10)
    return score


async def _retrieve_stop_details(
    state: AgentState, settings: Settings, route: list[RouteStop], interests: set[str]
) -> None:
    if not settings.qdrant_enabled:
        return
    retriever = Retriever(settings)
    interest_terms = _chinese_interest_terms(interests)
    existing_ids = {doc.qdrant_point_id or doc.id for doc in state.retrieved_documents}
    for stop in route:
        query = f"{stop.retrieval_name} {interest_terms} 休闲 慢节奏 景点 美食 交通 门票 行程"
        state.retrieval_queries.append(query)
        documents = await retriever.retrieve(query=query, top_k=4)
        for document in documents:
            key = document.qdrant_point_id or document.id
            if key not in existing_ids:
                state.retrieved_documents.append(document)
                existing_ids.add(key)


def _enrich_route_from_documents(route: list[RouteStop], documents: list[RetrievedDocument]) -> None:
    for stop in route:
        snippets = [_document_text(doc) for doc in _documents_for_stop(documents, stop)]
        combined = " ".join(snippets)
        stop.attractions = _extract_list_after_markers(
            combined, markers=("知名景点有", "景点有", "景点包括", "主要景点", "必去")
        )
        stop.foods = _extract_list_after_markers(
            combined, markers=("美食", "当地特色", "特色菜", "餐厅")
        )
        stop.shopping = _extract_list_after_markers(
            combined, markers=("购物", "市场", "商店", "街区")
        )


def _extract_list_after_markers(text: str, markers: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    for marker in markers:
        for match in re.finditer(rf"{re.escape(marker)}[^。；;\n\r]{{0,8}}[:：]?([^。；;\n\r]{{2,120}})", text):
            for value in re.split(r"[、,，/]|以及|和|及", match.group(1)):
                value = _clean_candidate_value(value)
                if value and value not in values:
                    values.append(value)
                if len(values) >= 6:
                    return values
    return values


def _build_days_from_route(route: list[RouteStop], interests: set[str]) -> list[ItineraryDay]:
    days: list[ItineraryDay] = []
    day_number = 1
    for stop in route:
        for local_day in range(1, stop.days + 1):
            days.append(
                ItineraryDay(
                    day_number=day_number,
                    title=f"Day {day_number}: {stop.name}",
                    activities=_activities_for_stop_day(stop, local_day, interests),
                )
            )
            day_number += 1
    return days


def _city_highlights(stop: RouteStop, interests: set[str]) -> list[ItineraryActivity]:
    return [
        *_activities_for_stop_day(stop, 1, interests),
        ItineraryActivity(
            time="Backup",
            title=f"Flexible walk in {stop.name}",
            location=stop.name,
            notes="Use this as a lighter substitute if timed tickets, heat, or energy level make the main plan too tight.",
            importance="optional",
            duration="1.5-2 hours",
            transport="walk or short transit hop",
            reservation_required=False,
            local_specialty=True,
        ),
    ]


def _activities_for_stop_day(stop: RouteStop, local_day: int, interests: set[str]) -> list[ItineraryActivity]:
    attractions = _with_fallback(stop.attractions, f"Historic center of {stop.name}", f"Major cultural site in {stop.name}")
    foods = _with_fallback(stop.foods, "local specialties")
    if local_day == 1:
        return [
            ItineraryActivity(
                time="Morning",
                title=attractions[0],
                location=stop.name,
                notes=f"Start with a signature sight from the retrieved guide to anchor {stop.name} historically and geographically.",
                importance="must_see",
                duration="2-3 hours",
                transport="walk or public transit",
                ticket="Reserve ahead if timed entry is available.",
                reservation_required=True,
                estimated_cost=35,
            ),
            ItineraryActivity(
                time="Afternoon",
                title=f"Slow city walk in {stop.name}",
                location=stop.name,
                notes="A low-pressure neighborhood block for city touring, cafes, small shops, and unscheduled discoveries.",
                importance="recommended",
                duration="2 hours",
                transport="walking route",
                reservation_required=False,
                estimated_cost=0,
            ),
            ItineraryActivity(
                time="Evening",
                title=f"Local dinner: {foods[0]}",
                location=stop.name,
                notes=f"Keep dinner local and relaxed; prioritize {', '.join(foods[:3])}.",
                importance="recommended",
                duration="1.5 hours",
                transport="near the day's final neighborhood",
                ticket="Book a mid-range restaurant if dining at peak time.",
                reservation_required=True,
                estimated_cost=45,
            ),
        ]
    if local_day == 2:
        return [
            ItineraryActivity(
                time="Morning",
                title=attractions[min(1, len(attractions) - 1)],
                location=stop.name,
                notes="Use the second day for deeper history, art, or culture without overloading the schedule.",
                importance="must_see" if {"history", "art"} & interests else "recommended",
                duration="2-3 hours",
                transport="public transit or walk",
                ticket="Reserve ahead for major museums and limited-entry sites.",
                reservation_required=True,
                estimated_cost=30,
            ),
            ItineraryActivity(
                time="Afternoon",
                title=f"Food and market time in {stop.name}",
                location=stop.name,
                notes=f"Sample {', '.join(foods[:3])}; keep this flexible rather than a formal tour.",
                importance="recommended",
                duration="2 hours",
                transport="walking route",
                reservation_required=False,
                local_specialty=True,
                estimated_cost=25,
            ),
        ]
    return [
        ItineraryActivity(
            time="Morning",
            title=attractions[min(2, len(attractions) - 1)],
            location=stop.name,
            notes="Use the extra day for a slower major sight, then keep the afternoon open.",
            importance="recommended",
            duration="2-3 hours",
            transport="public transit or taxi",
            reservation_required=True,
            estimated_cost=30,
        ),
        ItineraryActivity(
            time="Afternoon",
            title="Open rest block",
            location=stop.name,
            notes="Deliberately unscheduled time for heat, jet lag, laundry, cafes, or a spontaneous neighborhood.",
            importance="optional",
            duration="2-3 hours",
            reservation_required=False,
            local_specialty=True,
        ),
    ]


def _build_itinerary_prompt(state: AgentState) -> str:
    req = state.travel_requirements
    destination = req.destination or "the user's requested destination"
    duration = req.duration_days or 3
    context = state.evidence_summary or "No retrieved context is available yet."
    interests = ", ".join(req.interests) if req.interests else "balanced local highlights, food, and neighborhoods"
    constraints = "; ".join(req.special_constraints) if req.special_constraints else "none"

    return f"""
You are the itinerary reasoning agent for an AI vacation planner.
Create a practical itinerary as valid JSON only. Do not wrap it in Markdown.

Destination: {destination}
Duration: {duration} days
Travelers: {req.travelers or "unspecified"}
Budget max: {req.budget_max or "unspecified"}
Travel style: {req.travel_style or "unspecified"}
Interests: {interests}
Transportation preferences: {", ".join(req.transportation_preferences) or "unspecified"}
Accommodation preferences: {", ".join(req.accommodation_preferences) or "unspecified"}
Constraints: {constraints}
Context: {context}
User message: {state.sanitized_user_input or state.raw_user_input or ""}
Requirements:
- Write valid JSON matching the Itinerary schema used by the API.
- Choose countries/cities from retrieved context, not from memory.
- Match user interests and keep the pace realistic.
""".strip()


def _parse_itinerary_completion(completion: str) -> Itinerary:
    text = _strip_markdown_json(completion)
    try:
        data = json.loads(text)
        return Itinerary.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("LLM completion was not a valid itinerary JSON document.") from exc


def _strip_markdown_json(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return stripped


def _background_from_retrieval(state: AgentState, stop: RouteStop) -> str:
    doc = _retrieved_doc_for_stop(state, stop)
    if doc and doc.snippet:
        return f"{stop.name} plan context from retrieved travel knowledge: {doc.snippet[:420]}"
    return (
        f"{stop.name} should be introduced through its history, culture, arts, major landmarks, "
        "local activities, food traditions, and practical shopping areas. Verify current opening hours and ticket rules."
    )


def _retrieved_doc_for_stop(state: AgentState, stop: RouteStop) -> RetrievedDocument | None:
    documents = _documents_for_stop(state.retrieved_documents, stop)
    return documents[0] if documents else None


def _documents_for_stop(documents: list[RetrievedDocument], stop: RouteStop) -> list[RetrievedDocument]:
    title_matches = [doc for doc in documents if stop.name.lower() in (doc.title or "").lower()]
    if title_matches:
        return title_matches
    return [doc for doc in documents if _doc_matches_stop(doc, stop)]


def _doc_matches_stop(doc: RetrievedDocument, stop: RouteStop) -> bool:
    text = _document_text(doc).lower()
    return stop.name.lower() in text or bool(stop.country and stop.country.lower() in text and stop.name in text)


def _citations_for_route(state: AgentState, route: list[RouteStop]) -> list[str]:
    ordered_urls = [
        doc.source_url
        for stop in route
        if (doc := _retrieved_doc_for_stop(state, stop)) and doc.source_url
    ]
    ordered_urls.extend(doc.source_url for doc in state.retrieved_documents if doc.source_url)
    return list(dict.fromkeys(ordered_urls))[:8]


def _single_destination_itinerary(state: AgentState) -> Itinerary:
    req = state.travel_requirements
    destination = req.destination or "your destination"
    duration = req.duration_days or 3
    stop = RouteStop(name=destination, days=duration)
    return Itinerary(
        destination=destination,
        summary=f"A {duration}-day itinerary for {destination}.",
        main_route=[
            MainRouteStop(
                name=destination,
                background=_background_from_retrieval(state, stop),
                major_attractions=[f"Historic and cultural highlights in {destination}"],
                activities=["neighborhood walking route", "local dining"],
                local_food=["local specialties"],
                shopping=["local markets and specialty streets"],
            )
        ],
        detail_plans=[
            DestinationDetailPlan(
                stop_name=destination,
                highlights=_city_highlights(stop, set(req.interests)),
                brief_background=_background_from_retrieval(state, stop)[:500],
            )
        ],
        days=_build_days_from_route([stop], set(req.interests)),
        citations=_citations_for_route(state, [stop]),
    )


def _primary_focus(interests: set[str]) -> str:
    if {"history", "历史"} & interests:
        return "history"
    if {"art", "museums", "艺术", "博物馆"} & interests:
        return "art and museum"
    if {"food", "美食"} & interests:
        return "food and culture"
    if {"leisure", "relax", "休闲"} & interests:
        return "relaxed"
    return "culture and local highlights"


def _chinese_interest_terms(interests: set[str]) -> str:
    terms = []
    if "history" in interests:
        terms.append("历史 文化 古迹")
    if "food" in interests:
        terms.append("美食 餐厅 当地特色")
    if "art" in interests:
        terms.append("艺术 博物馆 美术馆")
    if "leisure" in interests:
        terms.append("休闲 慢节奏")
    return " ".join(terms) or "文化 美食 城市观光"


def _transportation_for_stop(stop: RouteStop) -> str:
    if stop.country:
        return f"Use rail, transit, walking routes, and short taxi hops as appropriate within {stop.name}, {stop.country}."
    return f"Use public transit, walking routes, and short taxi hops as appropriate within {stop.name}."


def _document_text(doc: RetrievedDocument) -> str:
    return " ".join(part for part in (doc.title, doc.snippet, doc.source_url or "") if part)


def _clean_place_name(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\(.*?\)|（.*?）|\[.*?]", "", value).strip(" \t-_:：，,。")
    return cleaned[:40] or None


def _clean_candidate_value(value: str) -> str | None:
    cleaned = re.sub(r"\[([^\]]+)]\([^)]+\)", r"\1", value)
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = cleaned.strip(" \t-_:：，,。；;|‣*")
    if len(cleaned) < 2 or len(cleaned) > 40:
        return None
    if any(token in cleaned.lower() for token in ("http", "booking", "unsplash", "youtube")):
        return None
    return cleaned


def _is_weak_place_name(value: str) -> bool:
    return value in {"未知", "unknown", "Unknown"} or len(value) < 2


def _with_fallback(values: list[str], *fallbacks: str) -> list[str]:
    return values if values else list(fallbacks)


def _copy_stop(stop: RouteStop, days: int | None = None, country: str | None = None) -> RouteStop:
    return RouteStop(
        name=stop.name,
        days=days if days is not None else stop.days,
        country=country if country is not None else stop.country,
        source_names=set(stop.source_names),
        attractions=list(stop.attractions),
        foods=list(stop.foods),
        shopping=list(stop.shopping),
    )


def _positive_int(value: object) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _is_continent_request(destination: str) -> bool:
    normalized = destination.strip().lower()
    return normalized in {
        "europe",
        "asia",
        "north america",
        "south america",
        "africa",
        "oceania",
        "australia",
        "antarctica",
        "欧洲",
        "亚洲",
        "北美洲",
        "南美洲",
        "非洲",
        "大洋洲",
        "南极洲",
    }
