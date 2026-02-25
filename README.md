# WellSync

AI-powered holistic wellness coach (early implementation stage) built with FastAPI, React, PostgreSQL, and pgvector.

## Project Overview

WellSync is designed to combine:

- Daily wellness check-ins (sleep, mood, energy, stress)
- Workout and meal logging
- Personalized recommendations using ML + LLM
- Evidence-based context retrieval through a wellness knowledge base (RAG with pgvector)

The repository currently contains the core infrastructure and scaffolding for this architecture. The full feature set is still in progress.

## Course Context and Deliverables

This project is developed for the university course "Information Systems Application Development" (Spring 2026) and is organized around four graded phases:

- **F1 (15%)**: Innovation form submission (PDF)
- **F2 (15%)**: In-class idea presentation (slides + speaker flow)
- **F3 (20%)**: Technical design document (requirements, architecture, UI mockups)
- **F4 (50%)**: Implementation, GitHub repository, and final demo

Main planning and phase artifacts are tracked under `docs/`:

- `docs/F1/` for phase 1 material
- `docs/F2/` for slides and presentation script
- `docs/F3/` for technical design
- `docs/STATUS.md` for implementation progress and session status
- `docs/plans/` for architecture and execution plans

## Phase-to-Code Mapping (Academic View)

### F1 - Problem and Innovation Framing

- Value proposition and differentiation are documented in `docs/F1/wellsync-phi1-content.md`.
- Innovation pillars include ML personalization and evidence-based retrieval (RAG).

### F2 - Presentation Readiness

- Slide structure and narrative are documented in `docs/F2/wellsync-phi2-slides.md` and `docs/F2/wellsync-phi2-speaker-script.md`.
- The implementation architecture described here is aligned with that presentation material.

### F3 - Technical Design Specification

- Functional requirements, architecture, API scope, and data design are in `docs/F3/wellsync-phi3-technical-design.md`.
- The current codebase follows this document as the implementation blueprint.

### F4 - Implementation and Demo

- Executable code lives in `backend/`, `frontend/`, and `migrations/`.
- This README provides reproducible setup instructions for local execution and demonstration.

## Current Codebase Status

Implemented:

- Backend app bootstrap (`FastAPI`) with health endpoint
- Core configuration and database setup
- SQLAlchemy models:
  - `User`
  - `CheckIn`
  - `Workout`
  - `Meal`
  - `AgentOutput`
- Event system primitives (`event types`, `queue`, `gateway`)
- RAG utilities:
  - `backend/knowledge/retriever.py`
  - `backend/knowledge/ingest.py`
  - `backend/knowledge/corpus/*.txt`
- Migration for `knowledge_chunks` and pgvector extension
- Frontend Vite/React skeleton
- Docker setup for db/backend/frontend

Not fully implemented yet (planned):

- Full API routers (beyond health)
- Agent handlers and scheduler loop integration
- ML training/personalization workflows
- Complete frontend user experience

## Architecture

Three-service setup:

1. PostgreSQL + pgvector (`db`, port `5432`)
2. FastAPI backend (`backend`, port `8000`)
3. React/Vite frontend (`frontend`, port `5173`)

Key tech stack:

- Backend: Python 3.10, FastAPI, SQLAlchemy
- DB: PostgreSQL + pgvector
- ML: scikit-learn
- LLM integration target: Anthropic API
- Frontend: React 18 + Vite + Chart.js

## Repository Structure

```text
wellsync-main/
  backend/
    config.py
    database.py
    create_tables.py
    main.py
    models/
    events/
    knowledge/
    tests/
    requirements.txt
    Dockerfile
  frontend/
    src/
    package.json
    Dockerfile
  migrations/
    add_knowledge_chunks.sql
  docs/
  .env.example
  docker-compose.yml
```

## Environment Variables

Copy `.env.example` to `.env` and adjust values if needed:

```env
DATABASE_URL=postgresql://wellsync:wellsync123@localhost:5432/wellsync
SECRET_KEY=dev-secret-change-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ML_MODELS_DIR=./ml_models
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
AGENT_LOOP_INTERVAL_HOURS=1
```

Notes:

- `ANTHROPIC_API_KEY` is optional for basic setup, required for AI recommendation features.
- For production, replace development secrets and credentials.

## Quick Start (Docker)

From repository root:

```bash
docker compose up --build
```

Services:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- DB: `localhost:5432`

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok","service":"wellsync-api"}
```

## Local Development (Without Full Docker Compose)

### 1) Start database

```bash
docker compose up -d db
```

### 2) Backend setup and run

From project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python3 -m backend.create_tables
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

On Windows PowerShell, activation is:

```powershell
.venv\Scripts\Activate.ps1
```

### 3) Frontend setup and run

From `frontend/`:

```bash
npm install
npm run dev
```

## Database and RAG Setup

Apply pgvector migration:

```bash
psql $DATABASE_URL -f migrations/add_knowledge_chunks.sql
```

Ingest the knowledge corpus:

```bash
python -m backend.knowledge.ingest
```

This loads curated wellness snippets into `knowledge_chunks`.

## Testing

Run backend tests:

```bash
python3 -m pytest backend/tests/ -v
```

Quick syntax sanity check:

```bash
python3 -m py_compile backend/main.py
```

## Troubleshooting

- Backend cannot connect to DB:
  - verify `DATABASE_URL`
  - ensure db container is running
- `knowledge_chunks` missing:
  - run `migrations/add_knowledge_chunks.sql` first
- RAG ingestion errors:
  - verify `sentence-transformers` and `pgvector` are installed
- Frontend API calls failing:
  - check Vite proxy configuration in `frontend/vite.config.js`

## Roadmap (High-Level)

- Complete backend routers (check-in, workout, meal, recommendations, insights)
- Integrate scheduler + agent handlers into the FastAPI lifespan flow
- Implement full ML personalization pipeline and retraining loop
- Complete frontend feature pages and dashboard charts
- Add seed data and end-to-end demo scenario
- Expand test coverage (unit + integration) and stabilize deployment flow

## Submission and Demo Checklist

Before final academic submission/demo:

- Ensure `.env` is configured correctly for the target environment
- Run migration and RAG ingestion successfully
- Verify backend health endpoint and frontend startup
- Run backend tests and include results in demo notes
- Confirm `docs/STATUS.md` and relevant phase docs are up to date
- Validate that the GitHub repository reflects the final runnable state

## License

No license file is currently defined in this repository.
