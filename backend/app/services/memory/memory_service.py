from app.core.config import Settings
from app.core.constants import DEFAULT_TOP_K, USER_MEMORY_COLLECTION
from app.db.qdrant import create_qdrant_client
from app.schemas.memory import MemoryRecord
from app.services.rag.embeddings import embed_texts


class MemoryService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def retrieve_user_memories(self, user_id: str, query: str, top_k: int = DEFAULT_TOP_K) -> list[MemoryRecord]:
        if not query:
            return []
        if not self.settings.qdrant_memory_enabled:
            return []
        try:
            client = create_qdrant_client(self.settings)
            vector = (
                await embed_texts([query], settings=self.settings, dimensions=self.settings.default_embedding_dim)
            )[0]
            response = await client.query_points(
                collection_name=USER_MEMORY_COLLECTION,
                query=vector,
                limit=top_k,
                query_filter={
                    "must": [
                        {
                            "key": "user_id",
                            "match": {"value": user_id},
                        }
                    ]
                },
                with_payload=True,
            )
            memories: list[MemoryRecord] = []
            for point in response.points:
                payload = point.payload or {}
                memories.append(
                    MemoryRecord(
                        id=str(payload.get("memory_id") or point.id),
                        type=payload.get("memory_type", "user_preference"),
                        content=str(payload.get("content") or payload.get("text") or ""),
                        confidence=float(payload.get("confidence") or 0.5),
                        source="qdrant",
                        qdrant_point_id=str(point.id),
                        sensitivity=str(payload.get("sensitivity") or "normal"),
                    )
                )
            return memories
        except Exception:
            # The graph should still operate during local development when Qdrant is not running.
            return []
