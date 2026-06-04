class AnthropicClient:
    async def complete(self, prompt: str) -> str:
        return f"Anthropic completion placeholder for: {prompt[:80]}"
