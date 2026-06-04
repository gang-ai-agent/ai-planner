from app.core.config import Settings
from app.schemas.agent_state import AgentState
from app.services.guardrails.prompt_injection import assess_retrieved_document


async def context_sanitizer_node(state: AgentState, _: Settings) -> AgentState:
    state.current_agent = "context_sanitizer"
    safe_docs = []
    for doc in state.retrieved_documents:
        assessment = assess_retrieved_document(doc)
        state.retrieval_safety.append(assessment)
        if assessment.allowed:
            safe_docs.append(doc)
    state.retrieved_documents = safe_docs
    return state
