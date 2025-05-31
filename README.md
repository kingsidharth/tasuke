# Tasuke

A local-first automation stack that captures work-stream data (Slack, Granola notes), organises it into tasks & projects, and surfaces just-in-time actions through specialised AI agents.

## Project Structure

```
.venv/                 # root virtual env
requirements.txt
logs/                  # loguru JSON files (rotated daily)
storage/               # uploaded images, PDFs  (90‑day retention)
docs/
backend/
  tests/
  app/
    api/
    agents/
    db/
    tools/
  alembic/
  worker/
frontend/
  reflex_app/
scripts/
  fetch_granola.py
.env.example
README.md
```

## Setup

1. Create and activate a Python virtual environment in `.venv`.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in required secrets.
4. Run database migrations with Alembic.
5. Start the FastAPI backend and frontend frontend (see respective directories).

### Run Backend Server
From root (activate .venv first)
`uvicorn backend.app.main:app --reload --port 8000`

### Run Background Tasks 
Activate .venv first
Ensure redis is running `redis-server`
1. `celery -A backend.app.worker.embeddings.celery_app worker --loglevel=info`
2. `celery -A backend.app.worker.embeddings worker --loglevel=info`


### Run Frontend Server

## MVP Phases
See `docs/prd.md` for full product requirements and phase breakdown.

---

- FastAPI, SQLAlchemy, Alembic, Loguru, LangGraph, Reflex, PostgreSQL, pgvector
- All secrets/config in `.env` (never commit this file) 