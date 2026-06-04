import json
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def main() -> None:
    config = json.loads(Path("infra/qdrant/collections.json").read_text())
    client = QdrantClient(url="http://localhost:6333")
    existing = {collection.name for collection in client.get_collections().collections}
    for collection in config["collections"]:
        name = collection["name"]
        if name in existing:
            print(f"Collection exists: {name}")
            continue
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=collection["vector_size"], distance=Distance[collection["distance"].upper()]),
        )
        print(f"Created collection: {name}")


if __name__ == "__main__":
    main()
