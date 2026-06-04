# Memory Design

Conversation and planning state are persisted through LangGraph checkpoints in PostgreSQL. Long-term memories use PostgreSQL as the source of truth and Qdrant as a semantic search index. User memory queries must always filter by `user_id`.
