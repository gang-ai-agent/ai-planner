import re

from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.schemas.travel import TravelStyle


async def intent_agent_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "intent_agent"
    state.current_step = "intent_analysis"
    req = state.travel_requirements
    _fill_requirements_from_text(state)
    missing = []
    if not req.destination:
        missing.append("destination")
    if not req.duration_days and not (req.start_date and req.end_date):
        missing.append("duration or travel dates")
    if not req.budget_max and not _has_flexible_budget_intent(state):
        missing.append("budget")
    state.unresolved_slots = missing
    if missing:
        state.follow_up_questions = [f"What is your preferred {slot}?" for slot in missing[:3]]
        state.status = "waiting_for_user"
    return state


def _fill_requirements_from_text(state: AgentState) -> None:
    text = state.sanitized_user_input or state.raw_user_input or ""
    req = state.travel_requirements
    if not req.destination:
        destination_patterns = [
            r"\bto\s+([A-Z][A-Za-z\s-]{2,40})(?:\s+under|\s+for|\s+in|\s+with|\.|,|$)",
            r"\bin\s+([A-Z][A-Za-z\s-]{2,40})(?:\s+under|\s+for|\s+with|\.|,|$)",
            r"去\s*([\u4e00-\u9fffA-Za-z\s-]{2,30})(?:旅游|旅行|玩|$|，|。)",
        ]
        for pattern in destination_patterns:
            match = re.search(pattern, text)
            if match:
                req.destination = match.group(1).strip()
                break

    if not req.duration_days:
        duration_match = re.search(r"(\d+)\s*(?:day|days|天|日)", text, flags=re.IGNORECASE)
        if duration_match:
            req.duration_days = int(duration_match.group(1))

    if not req.budget_max:
        budget_match = re.search(r"(?:under|below|budget|预算|不超过)\s*[$¥￥]?\s*(\d+(?:,\d{3})*(?:\.\d+)?)", text, flags=re.IGNORECASE)
        if budget_match:
            req.budget_max = float(budget_match.group(1).replace(",", ""))

    lowered = text.lower()
    if not req.travel_style:
        if "not a luxury" in lowered or "not luxury" in lowered or "non-luxury" in lowered:
            req.travel_style = TravelStyle.MID_RANGE
        elif "luxury" in lowered:
            req.travel_style = TravelStyle.LUXURY
        elif "backpacking" in lowered:
            req.travel_style = TravelStyle.BACKPACKING
        elif "budget" in lowered:
            req.travel_style = TravelStyle.BUDGET

    interest_aliases = {
        "history": ("history", "historical", "历史"),
        "art": ("art", "museum", "gallery", "艺术", "博物馆", "美术馆"),
        "food": ("food", "dining", "美食", "餐厅"),
        "shopping": ("shopping", "购物"),
        "leisure": ("leisure", "relax", "休闲", "轻松"),
    }
    existing = set(req.interests)
    for canonical, aliases in interest_aliases.items():
        if canonical not in existing and any(alias in lowered or alias in text for alias in aliases):
            req.interests.append(canonical)

    if _has_flexible_budget_intent(state):
        flexible_constraint = "Budget is flexible; avoid luxury positioning."
        if flexible_constraint not in req.special_constraints:
            req.special_constraints.append(flexible_constraint)


def _has_flexible_budget_intent(state: AgentState) -> bool:
    text = (state.sanitized_user_input or state.raw_user_input or "").lower()
    return any(
        phrase in text
        for phrase in (
            "don't care the spend",
            "dont care the spend",
            "don't care about spend",
            "dont care about spend",
            "no fixed budget",
            "budget is flexible",
            "flexible budget",
            "spend is flexible",
        )
    )
