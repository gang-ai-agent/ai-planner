from app.schemas.memory import MemoryUpdate, MemoryWriteDecision


def decide_memory_writes(update: MemoryUpdate) -> MemoryWriteDecision:
    should_write = update.confidence >= 0.7
    return MemoryWriteDecision(
        update=update,
        should_write=should_write,
        reason="High-confidence user preference." if should_write else "Needs confirmation before storing.",
    )
