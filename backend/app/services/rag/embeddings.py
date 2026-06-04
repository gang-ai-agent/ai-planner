import hashlib
import asyncio
import json
import math
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError


def _deterministic_embedding(text: str, dimensions: int = 1536) -> list[float]:
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    values = []
    for index in range(dimensions):
        byte = seed[index % len(seed)]
        values.append((byte / 255.0) - 0.5)
    norm = math.sqrt(sum(value * value for value in values)) or 1.0
    return [value / norm for value in values]


async def embed_texts(texts: list[str], settings: Settings | None = None, dimensions: int = 768) -> list[list[float]]:
    if settings and settings.embedding_provider.lower() == "ollama":
        try:
            return await asyncio.gather(*[_embed_ollama(text, settings) for text in texts])
        except ExternalServiceError:
            if settings.environment.lower() != "local":
                raise
    return [_deterministic_embedding(text, dimensions=dimensions) for text in texts]


async def _embed_ollama(text: str, settings: Settings) -> list[float]:
    return await asyncio.to_thread(_embed_ollama_sync, text, settings)


def _embed_ollama_sync(text: str, settings: Settings) -> list[float]:
    payload = json.dumps({"model": settings.ollama_embedding_model, "prompt": text}).encode("utf-8")
    http_request = request.Request(
        f"{settings.ollama_base_url.rstrip('/')}/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=settings.ollama_embedding_timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise ExternalServiceError(f"Ollama embedding request failed: {exc}") from exc

    try:
        data = json.loads(body)
        embedding = data["embedding"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ExternalServiceError("Ollama returned an unexpected embedding response shape.") from exc

    if not isinstance(embedding, list) or not embedding:
        raise ExternalServiceError("Ollama returned an empty embedding.")
    return [float(value) for value in embedding]
