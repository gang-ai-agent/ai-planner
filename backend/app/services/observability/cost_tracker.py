from decimal import Decimal

from app.schemas.observability import TokenUsage


def estimate_cost(_: str | None, usage: TokenUsage) -> Decimal:
    return Decimal(usage.total_tokens) * Decimal("0.000001")
