# AI Vacation Planner

AI-powered vacation planning application scaffold with:

- Python FastAPI backend
- LangGraph-style agent workflow boundaries
- PostgreSQL canonical state and checkpoint target
- Qdrant vector search target
- Memory, guardrails, validation, and observability layers
- Next.js TypeScript frontend

## Run Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

## Infrastructure

```bash
docker compose up --build
```
