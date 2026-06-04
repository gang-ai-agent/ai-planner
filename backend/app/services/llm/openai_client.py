class OpenAIClient:
    async def complete(self, prompt: str) -> str:
        return f"OpenAI completion placeholder for: {prompt[:80]}"
