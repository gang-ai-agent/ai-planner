from app.core.config import Settings, get_settings
from app.db.postgres import get_session


def settings_dependency() -> Settings:
    return get_settings()


async def db_session_dependency():
    async for session in get_session():
        yield session
