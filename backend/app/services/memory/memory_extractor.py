from app.schemas.memory import MemoryType, MemoryUpdate
from app.schemas.travel import Message


def extract_memory_updates(messages: list[Message]) -> list[MemoryUpdate]:
    updates: list[MemoryUpdate] = []
    for message in messages:
        lowered = message.content.lower()
        if "prefer" in lowered or "i like" in lowered:
            updates.append(
                MemoryUpdate(
                    memory_type=MemoryType.USER_PREFERENCE,
                    content=message.content,
                    confidence=0.7,
                    source_message_id=message.id,
                )
            )
    return updates
