from app.agents.nodes.intent_agent import _fill_requirements_from_text
from app.schemas.agent_state import AgentState
from app.schemas.travel import ChatRequest
from app.services.rag.query_translation import build_retrieval_query


def test_builds_chinese_retrieval_query_from_english_trip_request() -> None:
    prompt = (
        "I want go to Italy for a 10 days vacation next month in July. "
        "I'd like a leisure non-pressure vacation enjoy the city history and culture, "
        "I also love the food, and enjoy city touring. I don't care the spend, "
        "but to be clear it's not a luxury trip."
    )
    state = AgentState.from_chat_request(ChatRequest(user_id="u1", message=prompt), max_retries=3)
    _fill_requirements_from_text(state)

    query = build_retrieval_query(state, target_language="zh")

    assert query.original_language == "en"
    assert query.retrieval_language == "zh"
    assert "Italy" in query.retrieval_query
    assert "10天" in query.retrieval_query
    assert "7月" in query.retrieval_query
    assert "历史" in query.retrieval_query
    assert "美食" in query.retrieval_query
    assert "中端" in query.retrieval_query
    assert "非豪华" in query.retrieval_query


def test_keeps_chinese_query_in_chinese() -> None:
    prompt = "我想去意大利玩10天，喜欢历史文化和美食，轻松一点，不要豪华。"
    state = AgentState.from_chat_request(ChatRequest(user_id="u1", message=prompt), max_retries=3)
    _fill_requirements_from_text(state)

    query = build_retrieval_query(state, target_language="zh")

    assert query.original_language == "zh"
    assert query.retrieval_language == "zh"
    assert "意大利" in query.retrieval_query
