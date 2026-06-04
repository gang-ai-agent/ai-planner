import re

from app.core.config import Settings
from app.db.qdrant import create_qdrant_client
from app.schemas.agent_state import AgentState
from app.schemas.observability import AgentError
from app.services.llm.provider import get_llm_provider
from app.services.rag.citation_service import citations_from_documents
from app.services.rag.query_translation import RetrievalQuery, build_retrieval_query
from app.services.rag.retriever import Retriever


async def retrieval_agent_node(state: AgentState, settings: Settings) -> AgentState:
    state.current_agent = "retrieval_agent"
    query = build_retrieval_query(state, target_language=settings.retrieval_query_language)
    query = await _localize_destination_from_corpus(state, settings, query)
    query = await _translate_query_with_llm_if_available(state, settings, query)
    state.retrieval_queries.append(query.original_query)
    if query.retrieval_query != query.original_query:
        state.retrieval_queries.append(query.retrieval_query)
    state.retrieved_documents = await Retriever(settings).retrieve(query=query.retrieval_query)
    state.source_citations = citations_from_documents(state.retrieved_documents)
    if state.retrieved_documents:
        snippets = [doc.snippet[:240] for doc in state.retrieved_documents[:3] if doc.snippet]
        state.evidence_summary = (
            f"Original user language: {query.original_language}. "
            f"Retrieval query language: {query.retrieval_language}. "
            f"Retrieval query: {query.retrieval_query}\n"
            + "\n".join(snippets)
        )
    return state


async def _localize_destination_from_corpus(
    state: AgentState, settings: Settings, query: RetrievalQuery
) -> RetrievalQuery:
    destination = state.travel_requirements.destination
    if (
        not settings.qdrant_enabled
        or settings.retrieval_query_language != "zh"
        or query.original_language != "en"
        or not destination
        or _contains_cjk(destination)
    ):
        return query
    localized = await _find_localized_name_in_corpus(settings, destination)
    if not localized:
        return query
    return RetrievalQuery(
        original_query=query.original_query,
        retrieval_query=f"{localized} {query.retrieval_query}",
        original_language=query.original_language,
        retrieval_language="zh",
    )


async def _find_localized_name_in_corpus(settings: Settings, english_name: str) -> str | None:
    client = create_qdrant_client(settings)
    next_offset = None
    scanned = 0
    english_pattern = re.escape(english_name)
    parenthetical_patterns = (
        re.compile(rf"([\u4e00-\u9fff]{{2,20}})[（(]\s*{english_pattern}\s*[）)]", re.IGNORECASE),
        re.compile(rf"\[([\u4e00-\u9fff]{{2,20}})[（(]\s*{english_pattern}\s*[）)]", re.IGNORECASE),
    )
    while scanned < 3000:
        points, next_offset = await client.scroll(
            collection_name=settings.qdrant_travel_collection,
            limit=100,
            offset=next_offset,
            with_payload=True,
            with_vectors=False,
        )
        if not points:
            break
        scanned += len(points)
        for point in points:
            payload = point.payload or {}
            text = " ".join(
                str(payload.get(key) or "")
                for key in ("title", "doc_id", "source_file", "text", "markdown")
            )
            if english_name.lower() not in text.lower():
                continue
            for pattern in parenthetical_patterns:
                match = pattern.search(text)
                if match:
                    return match.group(1)
            metadata_match = re.search(r"国家[:：]\s*([\u4e00-\u9fff]{2,20})", text)
            if metadata_match:
                return metadata_match.group(1)
        if next_offset is None:
            break
    return None


def _contains_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


async def _translate_query_with_llm_if_available(
    state: AgentState, settings: Settings, query: RetrievalQuery
) -> RetrievalQuery:
    if not settings.llm_enabled or query.original_language != "en" or settings.retrieval_query_language != "zh":
        return query
    prompt = f"""
Translate this travel retrieval query into concise Simplified Chinese search keywords.
Keep destination names, country names, city names, continent names, duration, month, travel style, and interests.
Return only the translated keyword query, no explanation.

User request:
{state.sanitized_user_input or state.raw_user_input or ""}

Current keyword query:
{query.retrieval_query}
""".strip()
    try:
        translated = await get_llm_provider(settings).complete(prompt)
    except Exception as exc:
        state.errors.append(
            AgentError(
                agent_name="retrieval_agent",
                error_type=exc.__class__.__name__,
                message=f"LLM query translation failed; using deterministic retrieval query: {exc}",
                recoverable=True,
            )
        )
        return query
    translated = " ".join(translated.replace("\n", " ").split())
    if not translated:
        return query
    return RetrievalQuery(
        original_query=query.original_query,
        retrieval_query=translated,
        original_language=query.original_language,
        retrieval_language="zh",
    )
