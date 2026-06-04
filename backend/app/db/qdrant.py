from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import Settings
from app.core.constants import ITINERARY_COLLECTION, TRAVEL_KNOWLEDGE_COLLECTION, USER_MEMORY_COLLECTION


def create_qdrant_client(settings: Settings) -> AsyncQdrantClient:
    return AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=1.0)


async def ensure_qdrant_collections(settings: Settings) -> None:
    client = create_qdrant_client(settings)
    collection_names = {
        TRAVEL_KNOWLEDGE_COLLECTION,
        USER_MEMORY_COLLECTION,
        ITINERARY_COLLECTION,
    }
    existing = {collection.name for collection in (await client.get_collections()).collections}
    for collection_name in collection_names - existing:
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=settings.default_embedding_dim, distance=Distance.COSINE),
        )
