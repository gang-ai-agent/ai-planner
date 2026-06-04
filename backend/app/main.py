from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.routes import chat, health, itineraries, memories, observability
from app.core.config import get_settings
from app.services.observability.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-powered vacation planning agent with memory, guardrails, RAG, and observability.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router, prefix="/api")
    app.include_router(itineraries.router, prefix="/api")
    app.include_router(memories.router, prefix="/api")
    app.include_router(observability.router, prefix="/api")
    register_error_handlers(app)
    return app


app = create_app()
