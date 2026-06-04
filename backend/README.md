# AI Vacation Planner Backend

FastAPI backend for an agentic vacation planner with LangGraph orchestration, PostgreSQL checkpoints, Qdrant vector search, memory, guardrails, and observability.

## Local Run

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

By default the backend uses a local Ollama model:

```bash
ollama pull granite4.1:3b
ollama serve
```

Configure with `LLM_PROVIDER=local`, `OLLAMA_BASE_URL=http://localhost:11434`, and `OLLAMA_MODEL=granite4.1:3b`.

## Test

```bash
pytest
```
