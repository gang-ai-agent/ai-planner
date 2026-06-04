from fastapi import APIRouter, Depends

from app.api.dependencies import settings_dependency
from app.core.config import Settings

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/runtime")
async def runtime_summary() -> dict[str, str]:
    return {"tracing": "langsmith", "metrics": "opentelemetry", "logs": "json"}


@router.get("/settings")
async def runtime_settings(settings: Settings = Depends(settings_dependency)) -> dict[str, object]:
    return {
        "qdrant_enabled": settings.qdrant_enabled,
        "qdrant_memory_enabled": settings.qdrant_memory_enabled,
        "qdrant_travel_collection": settings.qdrant_travel_collection,
        "default_embedding_dim": settings.default_embedding_dim,
        "embedding_provider": settings.embedding_provider,
        "ollama_embedding_model": settings.ollama_embedding_model,
        "llm_enabled": settings.llm_enabled,
        "llm_provider": settings.llm_provider,
        "ollama_model": settings.ollama_model,
        "ollama_timeout_seconds": settings.ollama_timeout_seconds,
    }
