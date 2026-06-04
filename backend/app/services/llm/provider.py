from typing import Protocol

from app.core.config import Settings
from app.services.llm.anthropic_client import AnthropicClient
from app.services.llm.local_client import LocalClient
from app.services.llm.openai_client import OpenAIClient


class LLMProvider(Protocol):
    async def complete(self, prompt: str) -> str:
        ...


def get_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "local":
        return LocalClient(settings)
    if provider == "openai":
        return OpenAIClient()
    if provider == "anthropic":
        return AnthropicClient()
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
