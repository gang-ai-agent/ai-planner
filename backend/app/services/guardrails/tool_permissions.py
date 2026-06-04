from app.schemas.guardrails import ToolPermission

READ_ONLY_TOOLS = {
    "qdrant_search": ToolPermission(tool_name="qdrant_search", permission_scope="read", requires_confirmation=False),
    "memory_search": ToolPermission(tool_name="memory_search", permission_scope="read", requires_confirmation=False),
}


def get_tool_permission(tool_name: str) -> ToolPermission:
    return READ_ONLY_TOOLS.get(tool_name, ToolPermission(tool_name=tool_name))
