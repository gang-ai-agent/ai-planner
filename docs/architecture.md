# Architecture

The system is split into a FastAPI backend, a Next.js frontend, PostgreSQL for canonical state, and Qdrant for vector search. Agent workflow code lives in `backend/app/agents`, while services provide memory, guardrails, RAG, validation, and observability.
