# WellSync — AI Holistic Wellness Coach

> AEPS 2026 · Ομάδα: krimits · Φ4 — Υλοποίηση

---

## Περιγραφή

Η WellSync είναι web εφαρμογή που συνδυάζει:
- **Daily check-in** (ύπνος / διάθεση / ενέργεια / στρες)
- **Workout & Meal logging**
- **AI agentic loop** (APScheduler → asyncio.Queue → EventGateway → Agents → Claude API)
- **Personalized ML** (Ridge Regression per user) + **RAG** (pgvector cosine similarity)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10 + FastAPI |
| ML | scikit-learn (Ridge Regression per user) |
| LLM | Anthropic API — claude-haiku-4-5-20251001 |
| Database | PostgreSQL + pgvector |
| Frontend | React 18 + Vite + Chart.js |
| Auth | JWT (python-jose) |
| Scheduling | APScheduler |
| Deploy | Docker Compose |

---

## Εκκίνηση (Docker Compose)

### Prerequisites
- Docker + Docker Compose
- Anthropic API key

### 1. Ρύθμιση περιβάλλοντος

```bash
cp .env.example .env
# Επεξεργάσου το .env και βάλε το ANTHROPIC_API_KEY
```

### 2. Build & Run

```bash
docker compose up --build
```

Οι υπηρεσίες:
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

### 3. Seed demo δεδομένα (προαιρετικό)

```bash
docker compose exec backend python -m backend.seed
```

Δημιουργεί χρήστη `demo@wellsync.app` / `wellsync123` με 20 ημέρες δεδομένα.

### 4. Ingestion RAG knowledge base (μια φορά)

```bash
docker compose exec backend python -m backend.knowledge.ingest
```

---

## Τοπική ανάπτυξη (χωρίς Docker)

### Backend

```bash
cd wellsync/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# PostgreSQL running locally (port 5432)
# DATABASE_URL=postgresql://wellsync:wellsync123@localhost:5432/wellsync

python -m backend.create_tables
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd wellsync/frontend
npm install
npm run dev
```

---

## API Endpoints

| Method | Path | Περιγραφή |
|--------|------|-----------|
| POST | `/auth/register` | Δημιουργία λογαριασμού |
| POST | `/auth/login` | Σύνδεση (JWT) |
| POST | `/checkin` | Ημερήσιο check-in |
| GET | `/checkin/history` | Ιστορικό check-ins |
| POST | `/workout` | Καταγραφή προπόνησης |
| GET | `/workout/history` | Ιστορικό προπονήσεων |
| POST | `/meal` | Καταγραφή γεύματος |
| GET | `/meal/history` | Ιστορικό γευμάτων |
| GET | `/recommendations/today` | Σημερινή σύσταση (agent + ML fallback) |
| GET | `/insights` | Συσχετισμοί + τάσεις |

---

## Αρχιτεκτονική Agentic Loop

```
APScheduler (08:00/21:00/03:00)
    ↓
asyncio.Queue
    ↓
EventGateway (registry dict)
    ↓
MorningRecommendationAgent
    ├── ML readiness score (cold-start <14 days | Ridge Regression ≥14 days)
    ├── RAG retrieval (pgvector cosine k=2)
    └── Claude claude-haiku-4-5-20251001
    ↓
agent_outputs table → GET /recommendations/today
```

---

## Δομή Project

```
wellsync/
├── backend/
│   ├── main.py            # FastAPI app + lifespan (scheduler)
│   ├── config.py          # Pydantic Settings
│   ├── database.py        # SQLAlchemy engine + session
│   ├── models/            # User, CheckIn, Workout, Meal, AgentOutput
│   ├── routers/           # auth, checkin, logs, recommendations, insights
│   ├── ml/                # readiness.py, personalizer.py
│   ├── agents/            # morning, evening, retraining
│   ├── events/            # event_types, queue, gateway
│   ├── knowledge/         # retriever.py, ingest.py, corpus/
│   ├── scheduler.py       # APScheduler configuration
│   └── seed.py            # Demo data seed script
├── frontend/
│   └── src/               # React 18 + Vite + Chart.js
├── migrations/
│   └── add_knowledge_chunks.sql
├── docker-compose.yml
└── README.md
```
