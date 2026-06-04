from app.core.config import Settings
from app.core.constants import DEFAULT_TOP_K
from app.db.qdrant import create_qdrant_client
from app.schemas.rag import RetrievedDocument
from app.services.rag.embeddings import embed_texts


class Retriever:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievedDocument]:
        if not query:
            return []
        if not self.settings.qdrant_enabled:
            return self._fallback_documents(query)
        try:
            client = create_qdrant_client(self.settings)
            keyword_documents = await self._keyword_documents(client, query=query, top_k=top_k)
            vector = (
                await embed_texts([query], settings=self.settings, dimensions=self.settings.default_embedding_dim)
            )[0]
            response = await client.query_points(
                collection_name=self.settings.qdrant_travel_collection,
                query=vector,
                limit=top_k,
                with_payload=True,
            )
            documents: list[RetrievedDocument] = []
            for point in response.points:
                documents.append(self._document_from_point(point, score=float(point.score or 0.0)))
            if keyword_documents:
                return self._merge_documents(keyword_documents, documents, top_k=top_k)
            if documents:
                return documents[:top_k]
        except Exception:
            # Local development and unit tests should keep working when Qdrant is not running.
            pass
        return self._fallback_documents(query)

    async def _keyword_documents(self, client, query: str, top_k: int) -> list[RetrievedDocument]:
        keywords = list(dict.fromkeys(part for part in query.split() if len(part) >= 2))
        if not keywords:
            return []

        scored: list[tuple[float, RetrievedDocument]] = []
        next_offset = None
        scanned = 0
        while scanned < 1000:
            points, next_offset = await client.scroll(
                collection_name=self.settings.qdrant_travel_collection,
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
                header = " ".join(
                    str(payload.get(key) or "")
                    for key in ("title", "doc_id", "source_file")
                )
                destination_keywords = _destination_keywords(keywords)
                if destination_keywords and not any(keyword in header for keyword in destination_keywords):
                    continue
                haystack = " ".join(
                    str(payload.get(key) or "")
                    for key in ("title", "doc_id", "source_file", "text", "markdown")
                )
                score = self._keyword_score(haystack, header, keywords)
                if score > 0:
                    scored.append((score, self._document_from_point(point, score=min(score / 10.0, 1.0))))
            if next_offset is None:
                break

        scored.sort(key=lambda item: item[0], reverse=True)
        return [document for _, document in scored[:top_k]]

    def _keyword_score(self, haystack: str, header: str, keywords: list[str]) -> float:
        score = 0.0
        priority_keywords = set(keywords[:2])
        first_keyword = keywords[0] if keywords else ""
        for keyword in keywords:
            if keyword in haystack:
                score += 2.0 if keyword in priority_keywords else 1.0
            if keyword in header:
                score += 8.0 if keyword == first_keyword else 3.0
        return score

    def _document_from_point(self, point, score: float) -> RetrievedDocument:
        payload = point.payload or {}
        snippet = str(payload.get("markdown") or payload.get("text") or payload.get("snippet") or "")
        return RetrievedDocument(
            id=str(payload.get("chunk_id") or point.id),
            source_url=str(payload.get("source_url") or payload.get("url") or "").strip() or None,
            title=str(payload.get("title") or payload.get("doc_id") or payload.get("source_file") or ""),
            snippet=snippet[:1200],
            score=score,
            qdrant_point_id=str(point.id),
            metadata={
                key: str(value)
                for key, value in payload.items()
                if key not in {"text", "markdown", "links"}
            },
        )

    def _merge_documents(
        self, keyword_documents: list[RetrievedDocument], vector_documents: list[RetrievedDocument], top_k: int
    ) -> list[RetrievedDocument]:
        merged: list[RetrievedDocument] = []
        seen: set[str] = set()
        for document in [*keyword_documents, *vector_documents]:
            key = document.qdrant_point_id or document.id
            if key in seen:
                continue
            seen.add(key)
            merged.append(document)
            if len(merged) >= top_k:
                break
        return merged

    def _fallback_documents(self, query: str) -> list[RetrievedDocument]:
        return [
            RetrievedDocument(
                id="stub-travel-doc",
                source_url="https://example.com/travel-guide",
                title="Trusted travel guide placeholder",
                snippet=f"Curated travel context for {query}. Replace with Qdrant retrieval.",
                score=0.5,
                metadata={"trust_score": "0.8"},
            )
        ]


def _destination_keywords(keywords: list[str]) -> list[str]:
    destination_keywords: list[str] = []
    for keyword in keywords[:3]:
        if keyword in _GENERIC_QUERY_TERMS or any(char.isascii() and char.isalpha() for char in keyword):
            continue
        destination_keywords.append(keyword)
    return destination_keywords[:2]


_GENERIC_QUERY_TERMS = {
    "行程",
    "攻略",
    "景点",
    "交通",
    "门票",
    "预订",
    "历史",
    "文化",
    "古迹",
    "美食",
    "餐厅",
    "休闲",
    "慢节奏",
    "轻松",
    "城市观光",
    "城市漫步",
    "中端",
    "非豪华",
    "不奢侈",
}
