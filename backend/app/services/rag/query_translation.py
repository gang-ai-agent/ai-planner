from dataclasses import dataclass

from app.schemas.agent_state import AgentState


@dataclass(frozen=True)
class RetrievalQuery:
    original_query: str
    retrieval_query: str
    original_language: str
    retrieval_language: str


CONTINENT_TERMS = {
    "europe": "欧洲",
    "asia": "亚洲",
    "north america": "北美洲",
    "south america": "南美洲",
    "africa": "非洲",
    "oceania": "大洋洲",
    "australia": "大洋洲",
    "antarctica": "南极洲",
}

INTEREST_TERMS = {
    "art": "艺术 博物馆 美术馆",
    "food": "美食 餐厅 当地特色",
    "history": "历史 文化 古迹",
    "leisure": "休闲 慢节奏 轻松",
    "shopping": "购物 市场 特色街区",
}

STYLE_TERMS = {
    "luxury": "豪华 高端",
    "mid_range": "中端 非豪华",
    "budget": "经济 预算",
    "backpacking": "背包 客栈 低预算",
}

MONTH_TERMS = {
    "january": "1月",
    "february": "2月",
    "march": "3月",
    "april": "4月",
    "may": "5月",
    "june": "6月",
    "july": "7月",
    "august": "8月",
    "september": "9月",
    "october": "10月",
    "november": "11月",
    "december": "12月",
}


def build_retrieval_query(state: AgentState, target_language: str = "zh") -> RetrievalQuery:
    original_query = state.sanitized_user_input or state.raw_user_input or ""
    original_language = detect_language(original_query)
    if target_language != "zh" or original_language == "zh":
        return RetrievalQuery(
            original_query=original_query,
            retrieval_query=_compact(" ".join(_query_parts(state, original_query, translate=False))),
            original_language=original_language,
            retrieval_language=original_language,
        )

    return RetrievalQuery(
        original_query=original_query,
        retrieval_query=_compact(" ".join(_query_parts(state, original_query, translate=True))),
        original_language=original_language,
        retrieval_language="zh",
    )


def detect_language(text: str) -> str:
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        return "zh"
    return "en"


def _query_parts(state: AgentState, original_query: str, translate: bool) -> list[str]:
    req = state.travel_requirements
    lowered = original_query.lower()
    parts: list[str] = []

    if req.destination:
        parts.append(_destination_term(req.destination, translate))
    elif original_query:
        parts.append(original_query)

    if req.duration_days:
        parts.append(f"{req.duration_days}天" if translate else f"{req.duration_days} days")

    for month, term in MONTH_TERMS.items():
        if month in lowered:
            parts.append(term if translate else month)
            break

    for interest in req.interests:
        if translate:
            parts.append(INTEREST_TERMS.get(interest, interest))
        else:
            parts.append(interest)

    if req.travel_style:
        style = req.travel_style.value
        parts.append(STYLE_TERMS.get(style, style) if translate else style)

    for constraint in req.special_constraints:
        if translate and "avoid luxury" in constraint.lower():
            parts.append("非豪华 不奢侈")
        else:
            parts.append(constraint)

    if translate:
        if "city touring" in lowered or "city tour" in lowered:
            parts.append("城市观光 城市漫步")
        if "culture" in lowered:
            parts.append("文化")
        if "non-pressure" in lowered or "leisure" in lowered:
            parts.append("慢节奏 不赶行程")
        parts.append("行程 攻略 景点 交通 门票 预订")
    elif original_query:
        parts.append(original_query)

    return parts


def _destination_term(destination: str, translate: bool) -> str:
    if not translate:
        return destination
    return CONTINENT_TERMS.get(destination.lower(), destination)


def _compact(query: str) -> str:
    return " ".join(query.split())
