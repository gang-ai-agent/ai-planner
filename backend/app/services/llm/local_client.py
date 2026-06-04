import asyncio
import json
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError


class LocalClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout_seconds = settings.ollama_timeout_seconds

    async def complete(self, prompt: str) -> str:
        return await asyncio.to_thread(self._complete_sync, prompt)

    def _complete_sync(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ExternalServiceError(f"Ollama request failed for model {self.model}: {exc}") from exc

        try:
            data = json.loads(body)
            completion = data["response"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ExternalServiceError("Ollama returned an unexpected response shape.") from exc

        if not isinstance(completion, str) or not completion.strip():
            raise ExternalServiceError("Ollama returned an empty completion.")
        return completion.strip()
