# WellSync — Agentic Loop Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend WellSync with a hybrid agentic loop: scheduled events trigger ML computation + Claude API calls that generate personalized natural-language recommendations stored per user, replacing the static rule-based output.

**Architecture:** APScheduler (embedded in FastAPI lifespan) fires `WellnessEvent` objects every hour; an `asyncio.Queue` holds them; `EventGateway` routes each event to the correct `Agent`; the `MorningRecommendationAgent` runs the ML readiness score, builds a context-rich prompt with the user's last 7 days of data, calls the Claude API, and stores the result in the `agent_outputs` DB table. The `GET /recommendation/today` endpoint reads from this pre-computed table (with ML-only fallback if no agent output yet exists).

**Tech Stack:** Python 3.10+, FastAPI + APScheduler, asyncio.Queue, anthropic SDK (Claude claude-haiku-4-5-20251001 for cost efficiency), SQLAlchemy 2.0, PostgreSQL, scikit-learn, React 18 + Vite + Chart.js, Docker Compose

**Supersedes:** `docs/plans/2026-02-18-wellsync-implementation.md` (Tasks 1–13 are the baseline; this plan adds Tasks 7–9 and modifies Tasks 1, 2, 6)

---

## Updated Project Structure

```
aeps-2026/
├── backend/
│   ├── main.py                    ← modified: lifespan starts scheduler
│   ├── database.py
│   ├── config.py                  ← modified: add ANTHROPIC_API_KEY
│   ├── models/
│   │   ├── __init__.py            ← modified: export AgentOutput
│   │   ├── user.py
│   │   ├── checkin.py
│   │   ├── workout.py
│   │   ├── meal.py
│   │   └── agent_output.py        ← NEW
│   ├── routers/
│   │   ├── auth.py
│   │   ├── checkin.py
│   │   ├── logs.py
│   │   ├── recommendations.py     ← modified: reads agent_outputs
│   │   └── insights.py
│   ├── ml/
│   │   ├── readiness.py
│   │   ├── personalizer.py
│   │   └── insights.py
│   ├── events/                    ← NEW package
│   │   ├── __init__.py
│   │   ├── event_types.py
│   │   ├── queue.py
│   │   └── gateway.py
│   ├── agents/                    ← NEW package
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── morning_agent.py
│   │   ├── evening_agent.py
│   │   └── retraining_agent.py
│   ├── scheduler.py               ← NEW
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_checkin.py
│   │   ├── test_logs.py
│   │   ├── test_recommendations.py ← modified
│   │   ├── test_ml.py
│   │   └── test_agents.py         ← NEW
│   └── requirements.txt           ← modified
├── frontend/
│   └── ...                        ← unchanged (Tasks 8–11 from old plan)
├── docker-compose.yml             ← modified: add ANTHROPIC_API_KEY env
├── .env.example                   ← modified: add ANTHROPIC_API_KEY
└── README.md
```

---

## Data Flow (Agentic Loop)

```
[APScheduler — every hour]
    ↓
 WellnessEvent(type="morning_recommendation", scheduled_for=06:00)
    ↓
 asyncio.Queue  ←─────────────────────────────────────┐
    ↓                                                  │
 EventGateway.route(event)                             │
    ↓                                                  │
 MorningRecommendationAgent.handle(event, db)          │
    ├─ fetch today's checkin for each user             │
    ├─ ML layer: compute readiness_score (scikit-learn)│
    ├─ build context prompt (7 days history)           │
    ├─ Claude API: generate natural language           │
    └─ store in agent_outputs table                   │
                                                       │
[GET /recommendation/today]                            │
    ├─ reads agent_outputs table (pre-computed)        │
    └─ fallback: if no output → ML-only response ──────┘
```

---

## Task M1 (Modified): Project Setup — Add Agentic Dependencies

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/config.py`
- Modify: `.env.example`
- Modify: `docker-compose.yml`

**Step 1: Update requirements.txt**

Add to the existing requirements from the baseline plan:

```
# Agentic loop additions
anthropic==0.28.0
apscheduler==3.10.4
```

Full `requirements.txt`:

```
fastapi==0.111.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
scikit-learn==1.5.0
pandas==2.2.2
numpy==1.26.4
pytest==8.2.0
httpx==0.27.0
pytest-asyncio==0.23.7
python-dotenv==1.0.1
alembic==1.13.1
pydantic-settings==2.2.1
anthropic==0.28.0
apscheduler==3.10.4
```

**Step 2: Update backend/config.py**

```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://wellsync:wellsync123@localhost:5432/wellsync"
    secret_key: str = "dev-secret-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    ml_models_dir: str = "./ml_models"
    anthropic_api_key: str = ""           # NEW
    agent_loop_interval_hours: int = 1    # NEW: how often scheduler fires

    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 3: Update .env.example**

```
DATABASE_URL=postgresql://wellsync:wellsync123@localhost:5432/wellsync
SECRET_KEY=dev-secret-change-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ML_MODELS_DIR=./ml_models
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
AGENT_LOOP_INTERVAL_HOURS=1
```

**Step 4: Update docker-compose.yml backend service env**

```yaml
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://wellsync:wellsync123@db:5432/wellsync
      SECRET_KEY: dev-secret-change-in-prod
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      AGENT_LOOP_INTERVAL_HOURS: 1
    depends_on:
      - db
    volumes:
      - ./backend:/app
      - ml_models:/app/ml_models
```

**Step 5: Verify install**

```bash
cd backend
pip install anthropic==0.28.0 apscheduler==3.10.4
python -c "import anthropic; import apscheduler; print('OK')"
```

Expected: `OK`

**Step 6: Commit**

```bash
git add backend/requirements.txt backend/config.py .env.example docker-compose.yml
git commit -m "feat: add anthropic SDK and APScheduler dependencies for agentic loop"
```

---

## Task M2 (Modified): Database — Add AgentOutput Model

**Files:**
- Create: `backend/models/agent_output.py`
- Modify: `backend/models/__init__.py`

**Step 1: Create backend/models/agent_output.py**

```python
# backend/models/agent_output.py
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime, Text, String
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class AgentOutput(Base):
    """Stores LLM-generated recommendations per user per day."""
    __tablename__ = "agent_outputs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    event_type = Column(String, nullable=False)       # "morning_recommendation", "evening_summary"
    readiness_score = Column(Float, nullable=True)    # ML-computed score
    intensity = Column(String, nullable=True)         # "high" / "moderate" / "low"
    llm_text = Column(Text, nullable=False)           # Claude's natural language output
    model_used = Column(String, default="claude-haiku-4-5-20251001")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
```

**Step 2: Update backend/models/__init__.py**

```python
from backend.models.user import User
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.meal import Meal
from backend.models.agent_output import AgentOutput
```

**Step 3: Run table creation**

```bash
python backend/create_tables.py
```

Expected: `Tables created.` (AgentOutput table now exists)

**Step 4: Commit**

```bash
git add backend/models/agent_output.py backend/models/__init__.py
git commit -m "feat: add AgentOutput model for storing LLM-generated recommendations"
```

---

## Task 7: Event System (event_types, queue, gateway)

**Files:**
- Create: `backend/events/__init__.py`
- Create: `backend/events/event_types.py`
- Create: `backend/events/queue.py`
- Create: `backend/events/gateway.py`
- Create: `backend/tests/test_agents.py` (partial — event routing tests)

**Step 1: Write failing tests for event routing**

```python
# backend/tests/test_agents.py
import pytest
import asyncio
from backend.events.event_types import WellnessEvent, EventType
from backend.events.queue import get_event_queue
from backend.events.gateway import EventGateway

def test_wellness_event_creation():
    event = WellnessEvent(type=EventType.MORNING_RECOMMENDATION)
    assert event.type == EventType.MORNING_RECOMMENDATION
    assert event.user_ids == []  # empty = all users

def test_wellness_event_specific_users():
    event = WellnessEvent(type=EventType.MORNING_RECOMMENDATION, user_ids=[1, 2, 3])
    assert event.user_ids == [1, 2, 3]

def test_gateway_routes_morning_event():
    gateway = EventGateway()
    handler = gateway.get_handler(EventType.MORNING_RECOMMENDATION)
    assert handler is not None

def test_gateway_routes_evening_event():
    gateway = EventGateway()
    handler = gateway.get_handler(EventType.EVENING_SUMMARY)
    assert handler is not None

def test_gateway_routes_retraining_event():
    gateway = EventGateway()
    handler = gateway.get_handler(EventType.MODEL_RETRAINING)
    assert handler is not None

@pytest.mark.asyncio
async def test_queue_put_and_get():
    queue = asyncio.Queue()
    event = WellnessEvent(type=EventType.MORNING_RECOMMENDATION)
    await queue.put(event)
    result = await queue.get()
    assert result.type == EventType.MORNING_RECOMMENDATION
```

**Step 2: Run tests — confirm they fail**

```bash
pytest backend/tests/test_agents.py -v
```

Expected: ImportError — modules don't exist yet.

**Step 3: Create backend/events/event_types.py**

```python
# backend/events/event_types.py
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List

class EventType(str, Enum):
    MORNING_RECOMMENDATION = "morning_recommendation"
    EVENING_SUMMARY = "evening_summary"
    MODEL_RETRAINING = "model_retraining"

@dataclass
class WellnessEvent:
    type: EventType
    user_ids: List[int] = field(default_factory=list)  # empty = process all active users
    fired_at: datetime = field(default_factory=datetime.utcnow)
```

**Step 4: Create backend/events/queue.py**

```python
# backend/events/queue.py
import asyncio
from typing import Optional

_event_queue: Optional[asyncio.Queue] = None

def get_event_queue() -> asyncio.Queue:
    """Return the singleton event queue. Created on first call."""
    global _event_queue
    if _event_queue is None:
        _event_queue = asyncio.Queue(maxsize=100)
    return _event_queue
```

**Step 5: Create backend/events/__init__.py**

```python
# backend/events/__init__.py
```

**Step 6: Create backend/events/gateway.py**

```python
# backend/events/gateway.py
from typing import Callable, Dict
from backend.events.event_types import EventType, WellnessEvent

class EventGateway:
    """Routes WellnessEvents to the correct agent handler."""

    def __init__(self) -> None:
        self._routes: Dict[EventType, Callable] = {}

    def register(self, event_type: EventType, handler: Callable) -> None:
        self._routes[event_type] = handler

    def get_handler(self, event_type: EventType) -> Callable:
        handler = self._routes.get(event_type)
        if handler is None:
            raise ValueError(f"No handler registered for event type: {event_type}")
        return handler

    async def dispatch(self, event: WellnessEvent, **kwargs) -> None:
        handler = self.get_handler(event.type)
        await handler(event, **kwargs)


def build_gateway() -> EventGateway:
    """Wire up gateway with all agent handlers. Import here to avoid circular deps."""
    from backend.agents.morning_agent import MorningRecommendationAgent
    from backend.agents.evening_agent import EveningInsightsAgent
    from backend.agents.retraining_agent import ModelRetrainingAgent

    gateway = EventGateway()
    gateway.register(EventType.MORNING_RECOMMENDATION, MorningRecommendationAgent().handle)
    gateway.register(EventType.EVENING_SUMMARY, EveningInsightsAgent().handle)
    gateway.register(EventType.MODEL_RETRAINING, ModelRetrainingAgent().handle)
    return gateway
```

**Step 7: Run tests — confirm they pass**

```bash
pytest backend/tests/test_agents.py::test_wellness_event_creation \
       backend/tests/test_agents.py::test_wellness_event_specific_users \
       backend/tests/test_agents.py::test_gateway_routes_morning_event \
       backend/tests/test_agents.py::test_gateway_routes_evening_event \
       backend/tests/test_agents.py::test_gateway_routes_retraining_event \
       backend/tests/test_agents.py::test_queue_put_and_get -v
```

Expected: 6 PASSED

**Step 8: Commit**

```bash
git add backend/events/ backend/tests/test_agents.py
git commit -m "feat: add event system (WellnessEvent, asyncio queue, EventGateway)"
```

---

## Task 8: Agent Handlers (Morning, Evening, Retraining)

**Files:**
- Create: `backend/agents/__init__.py`
- Create: `backend/agents/base.py`
- Create: `backend/agents/morning_agent.py`
- Create: `backend/agents/evening_agent.py`
- Create: `backend/agents/retraining_agent.py`
- Modify: `backend/tests/test_agents.py` (add agent behavior tests)

**Step 1: Add agent behavior tests**

Append to `backend/tests/test_agents.py`:

```python
# Add these imports at the top
from unittest.mock import patch, MagicMock, AsyncMock
from backend.agents.morning_agent import MorningRecommendationAgent
from backend.agents.morning_agent import build_recommendation_prompt

def test_prompt_contains_user_data():
    """Prompt must include key user metrics so Claude has context."""
    checkin = {
        "sleep_hours": 6.5, "sleep_quality": 3, "mood": 3,
        "energy": 2, "stress": 4, "readiness_score": 42.0
    }
    recent = [
        {"date": "2026-02-18", "readiness_score": 55.0, "mood": 4},
        {"date": "2026-02-17", "readiness_score": 62.0, "mood": 3},
    ]
    prompt = build_recommendation_prompt(checkin, recent_checkins=recent, user_name="Nikos")
    assert "6.5" in prompt          # sleep hours present
    assert "42" in prompt           # readiness score present
    assert "Nikos" in prompt        # personalized
    assert len(prompt) < 3000       # not too long (token cost)

@patch("backend.agents.morning_agent.anthropic.Anthropic")
def test_morning_agent_calls_claude(mock_anthropic_cls):
    """MorningRecommendationAgent calls Claude API with user context."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Rest today — low readiness detected.")]
    )

    agent = MorningRecommendationAgent()
    result = agent._call_claude("Some prompt about wellness")

    mock_client.messages.create.assert_called_once()
    assert "Rest today" in result

def test_intensity_from_score():
    from backend.agents.morning_agent import intensity_from_score
    assert intensity_from_score(80) == "high"
    assert intensity_from_score(55) == "moderate"
    assert intensity_from_score(30) == "low"
```

**Step 2: Run tests — confirm they fail**

```bash
pytest backend/tests/test_agents.py -v -k "prompt or claude or intensity"
```

Expected: ImportError — agents package doesn't exist yet.

**Step 3: Create backend/agents/__init__.py**

```python
# backend/agents/__init__.py
```

**Step 4: Create backend/agents/base.py**

```python
# backend/agents/base.py
from abc import ABC, abstractmethod
from backend.events.event_types import WellnessEvent
from sqlalchemy.orm import Session

class BaseAgent(ABC):
    """All agent handlers implement this interface."""

    @abstractmethod
    async def handle(self, event: WellnessEvent, db: Session) -> None:
        """Process a WellnessEvent. Must not raise — log errors and continue."""
        ...
```

**Step 5: Create backend/agents/morning_agent.py**

```python
# backend/agents/morning_agent.py
import logging
import anthropic
from datetime import date, timedelta
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.config import settings
from backend.events.event_types import WellnessEvent
from backend.ml.readiness import compute_readiness_score
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.user import User
from backend.models.agent_output import AgentOutput

logger = logging.getLogger(__name__)


def intensity_from_score(score: float) -> str:
    if score >= 75:
        return "high"
    elif score >= 45:
        return "moderate"
    return "low"


def build_recommendation_prompt(
    today_checkin: dict,
    recent_checkins: list[dict],
    user_name: str,
) -> str:
    """
    Build a context-rich prompt for Claude.
    Keep under ~600 tokens so claude-haiku-4-5-20251001 stays cheap.
    """
    history_lines = "\n".join(
        f"  - {c['date']}: readiness={c['readiness_score']:.0f}, mood={c['mood']}/5"
        for c in recent_checkins[:7]
    )
    return f"""You are WellSync, an AI wellness coach for university students.

User: {user_name}
Today ({date.today()}):
  Sleep: {today_checkin['sleep_hours']}h (quality {today_checkin['sleep_quality']}/5)
  Mood: {today_checkin['mood']}/5 | Energy: {today_checkin['energy']}/5 | Stress: {today_checkin['stress']}/5
  Readiness Score: {today_checkin['readiness_score']:.0f}/100

Recent history (last 7 days):
{history_lines if history_lines else '  No history yet.'}

Write a SHORT (2-3 sentences) personalized wellness recommendation for today.
Include: 1) one specific workout suggestion, 2) one nutrition tip.
Be direct, warm, and practical. No bullet points. Greek or English is fine.
"""


class MorningRecommendationAgent(BaseAgent):
    """
    Runs at 06:00 daily.
    For each active user with a today's check-in:
      1. Compute readiness score (ML layer)
      2. Build context prompt
      3. Call Claude API
      4. Store result in agent_outputs table
    """

    def _call_claude(self, prompt: str) -> str:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    async def handle(self, event: WellnessEvent, db: Session) -> None:
        today = date.today()

        # Determine which users to process
        query = db.query(CheckIn).filter(CheckIn.date == today)
        if event.user_ids:
            query = query.filter(CheckIn.user_id.in_(event.user_ids))
        todays_checkins = query.all()

        if not todays_checkins:
            logger.info("MorningRecommendationAgent: no check-ins found for today")
            return

        for checkin in todays_checkins:
            try:
                await self._process_user(checkin, db, today)
            except Exception as e:
                logger.error(
                    "MorningRecommendationAgent: failed for user %s: %s",
                    checkin.user_id, e
                )

    async def _process_user(self, checkin: CheckIn, db: Session, today: date) -> None:
        # Skip if output already exists for today
        existing = db.query(AgentOutput).filter(
            AgentOutput.user_id == checkin.user_id,
            AgentOutput.date == today,
            AgentOutput.event_type == "morning_recommendation",
        ).first()
        if existing:
            return

        user = db.query(User).filter(User.id == checkin.user_id).first()

        # Recent history (last 7 days)
        since = today - timedelta(days=7)
        recent = db.query(CheckIn).filter(
            CheckIn.user_id == checkin.user_id,
            CheckIn.date >= since,
            CheckIn.date < today,
        ).order_by(CheckIn.date.desc()).all()

        checkin_dict = {
            "sleep_hours": checkin.sleep_hours,
            "sleep_quality": checkin.sleep_quality,
            "mood": checkin.mood,
            "energy": checkin.energy,
            "stress": checkin.stress,
            "readiness_score": checkin.readiness_score or compute_readiness_score(
                checkin.sleep_hours, checkin.sleep_quality,
                checkin.mood, checkin.energy, checkin.stress
            ),
        }

        recent_dicts = [
            {"date": str(c.date), "readiness_score": c.readiness_score or 50.0, "mood": c.mood}
            for c in recent
        ]

        prompt = build_recommendation_prompt(checkin_dict, recent_dicts, user_name=user.name)
        llm_text = self._call_claude(prompt)

        output = AgentOutput(
            user_id=checkin.user_id,
            date=today,
            event_type="morning_recommendation",
            readiness_score=checkin_dict["readiness_score"],
            intensity=intensity_from_score(checkin_dict["readiness_score"]),
            llm_text=llm_text,
        )
        db.add(output)
        db.commit()
        logger.info("MorningRecommendationAgent: processed user %s", checkin.user_id)
```

**Step 6: Create backend/agents/evening_agent.py**

```python
# backend/agents/evening_agent.py
import logging
import anthropic
from datetime import date, timedelta
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.config import settings
from backend.events.event_types import WellnessEvent
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.user import User
from backend.models.agent_output import AgentOutput

logger = logging.getLogger(__name__)


class EveningInsightsAgent(BaseAgent):
    """
    Runs at 21:00 daily.
    Generates a brief end-of-day summary: what the user achieved,
    and one tip for tomorrow. Stored as 'evening_summary' in agent_outputs.
    """

    def _call_claude(self, prompt: str) -> str:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    async def handle(self, event: WellnessEvent, db: Session) -> None:
        today = date.today()

        query = db.query(CheckIn).filter(CheckIn.date == today)
        if event.user_ids:
            query = query.filter(CheckIn.user_id.in_(event.user_ids))
        todays_checkins = query.all()

        for checkin in todays_checkins:
            try:
                existing = db.query(AgentOutput).filter(
                    AgentOutput.user_id == checkin.user_id,
                    AgentOutput.date == today,
                    AgentOutput.event_type == "evening_summary",
                ).first()
                if existing:
                    continue

                user = db.query(User).filter(User.id == checkin.user_id).first()
                workouts_today = db.query(Workout).filter(
                    Workout.user_id == checkin.user_id,
                    Workout.date == today,
                ).all()

                workout_summary = ", ".join(
                    f"{w.type} {w.duration_min}min RPE{w.rpe}" for w in workouts_today
                ) or "no workout logged"

                prompt = f"""You are WellSync. Write a 1-2 sentence evening wrap-up for {user.name}.
Today: mood={checkin.mood}/5, energy={checkin.energy}/5, stress={checkin.stress}/5.
Workouts: {workout_summary}.
End with one short tip for a better tomorrow. Be warm and concise."""

                llm_text = self._call_claude(prompt)

                db.add(AgentOutput(
                    user_id=checkin.user_id,
                    date=today,
                    event_type="evening_summary",
                    llm_text=llm_text,
                ))
                db.commit()
            except Exception as e:
                logger.error("EveningInsightsAgent error for user %s: %s", checkin.user_id, e)
```

**Step 7: Create backend/agents/retraining_agent.py**

```python
# backend/agents/retraining_agent.py
import logging
from datetime import date
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.events.event_types import WellnessEvent
from backend.ml.personalizer import train_model
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.user import User

logger = logging.getLogger(__name__)


class ModelRetrainingAgent(BaseAgent):
    """
    Runs at 00:00 daily.
    Re-trains the Ridge Regression model for each user who has ≥14 check-ins.
    Uses existing personalizer.train_model().
    """

    async def handle(self, event: WellnessEvent, db: Session) -> None:
        users = db.query(User).all()

        for user in users:
            checkin_count = db.query(CheckIn).filter(CheckIn.user_id == user.id).count()
            if checkin_count < 14:
                continue  # Not enough data

            checkins = db.query(CheckIn).filter(CheckIn.user_id == user.id).all()
            workouts = db.query(Workout).filter(Workout.user_id == user.id).all()

            checkin_dicts = [
                {
                    "date": c.date,
                    "sleep_hours": c.sleep_hours,
                    "sleep_quality": c.sleep_quality,
                    "mood": c.mood,
                    "energy": c.energy,
                    "stress": c.stress,
                }
                for c in checkins
            ]
            workout_dicts = [{"date": w.date, "rpe": w.rpe} for w in workouts]

            try:
                train_model(user.id, checkin_dicts, workout_dicts)
                logger.info("ModelRetrainingAgent: retrained model for user %s", user.id)
            except Exception as e:
                logger.error("ModelRetrainingAgent: failed for user %s: %s", user.id, e)
```

**Step 8: Run all agent tests**

```bash
pytest backend/tests/test_agents.py -v
```

Expected: All PASSED (Claude call test uses mock, doesn't hit real API)

**Step 9: Commit**

```bash
git add backend/agents/ backend/tests/test_agents.py
git commit -m "feat: add MorningRecommendationAgent, EveningInsightsAgent, ModelRetrainingAgent with Claude API"
```

---

## Task 9: Scheduler Integration (APScheduler + FastAPI Lifespan)

**Files:**
- Create: `backend/scheduler.py`
- Modify: `backend/main.py`
- Create: `backend/tests/test_scheduler.py`

**Step 1: Write failing tests**

```python
# backend/tests/test_scheduler.py
from backend.scheduler import create_scheduler, SCHEDULE

def test_scheduler_has_three_jobs():
    """Exactly 3 jobs: morning, evening, retraining."""
    assert len(SCHEDULE) == 3

def test_morning_job_scheduled_at_6am():
    morning = next(j for j in SCHEDULE if j["event_type"] == "morning_recommendation")
    assert morning["hour"] == 6
    assert morning["minute"] == 0

def test_evening_job_scheduled_at_9pm():
    evening = next(j for j in SCHEDULE if j["event_type"] == "evening_summary")
    assert evening["hour"] == 21

def test_retraining_job_scheduled_at_midnight():
    retrain = next(j for j in SCHEDULE if j["event_type"] == "model_retraining")
    assert retrain["hour"] == 0
```

**Step 2: Run tests — confirm they fail**

```bash
pytest backend/tests/test_scheduler.py -v
```

Expected: ImportError — scheduler.py doesn't exist yet.

**Step 3: Create backend/scheduler.py**

```python
# backend/scheduler.py
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.events.event_types import WellnessEvent, EventType
from backend.events.queue import get_event_queue

logger = logging.getLogger(__name__)

# Declarative schedule — easy to modify or test
SCHEDULE = [
    {"event_type": "morning_recommendation", "hour": 6, "minute": 0},
    {"event_type": "evening_summary",        "hour": 21, "minute": 0},
    {"event_type": "model_retraining",       "hour": 0, "minute": 0},
]


async def _fire_event(event_type: str) -> None:
    """Enqueue a WellnessEvent for all users."""
    event = WellnessEvent(type=EventType(event_type))
    queue = get_event_queue()
    await queue.put(event)
    logger.info("Scheduler fired event: %s", event_type)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    for job in SCHEDULE:
        scheduler.add_job(
            _fire_event,
            trigger="cron",
            hour=job["hour"],
            minute=job["minute"],
            args=[job["event_type"]],
            id=job["event_type"],
            replace_existing=True,
        )
    return scheduler


async def run_event_loop(gateway, db_factory) -> None:
    """
    Long-running coroutine: reads events from queue and dispatches them.
    Runs as background task during FastAPI lifespan.
    """
    queue = get_event_queue()
    while True:
        event = await queue.get()
        db = db_factory()
        try:
            await gateway.dispatch(event, db=db)
        except Exception as e:
            logger.error("Event loop error for %s: %s", event.type, e)
        finally:
            db.close()
            queue.task_done()
```

**Step 4: Update backend/main.py to start scheduler**

```python
# backend/main.py
from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth, checkin, logs, recommendations, insights
from backend.scheduler import create_scheduler, run_event_loop
from backend.events.gateway import build_gateway
from backend.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start scheduler and event loop worker on startup; shut down cleanly."""
    gateway = build_gateway()
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("APScheduler started with %d jobs", len(scheduler.get_jobs()))

    # Background task: reads from queue and dispatches to agents
    loop_task = asyncio.create_task(run_event_loop(gateway, SessionLocal))

    yield  # App runs here

    scheduler.shutdown(wait=False)
    loop_task.cancel()
    try:
        await loop_task
    except asyncio.CancelledError:
        pass
    logger.info("Scheduler and event loop shut down")


app = FastAPI(title="WellSync API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(checkin.router)
app.include_router(logs.router)
app.include_router(recommendations.router)
app.include_router(insights.router)
```

**Step 5: Run scheduler tests**

```bash
pytest backend/tests/test_scheduler.py -v
```

Expected: 4 PASSED

**Step 6: Smoke test — start the server and verify scheduler fires**

```bash
cd backend && uvicorn main:app --reload
```

Expected log output within seconds:
```
INFO - APScheduler started with 3 jobs
```

**Step 7: Commit**

```bash
git add backend/scheduler.py backend/main.py backend/tests/test_scheduler.py
git commit -m "feat: integrate APScheduler with FastAPI lifespan and async event loop worker"
```

---

## Task M6 (Modified): Recommendation Endpoint — Read from agent_outputs

**Files:**
- Modify: `backend/routers/recommendations.py`
- Modify: `backend/tests/test_recommendations.py`

**Step 1: Update tests**

Replace `backend/tests/test_recommendations.py` with:

```python
# backend/tests/test_recommendations.py
import pytest
from datetime import date
from unittest.mock import patch

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"email": "a@b.com", "name": "A", "password": "pass"})
    resp = client.post("/auth/login", data={"username": "a@b.com", "password": "pass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_no_checkin_returns_prompt(client, auth_headers):
    response = client.get("/recommendation/today", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "no_checkin"

def test_recommendation_ml_fallback_when_no_agent_output(client, auth_headers):
    """When checked in but no LLM output yet: ML fallback with intensity + generic message."""
    client.post("/checkin", json={
        "sleep_hours": 8, "sleep_quality": 5, "mood": 5, "energy": 5, "stress": 1
    }, headers=auth_headers)
    response = client.get("/recommendation/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["readiness_score"] == 100.0
    assert data["intensity"] == "high"
    assert data["source"] == "ml_fallback"
    assert "message" in data

def test_recommendation_returns_llm_text_when_available(client, auth_headers):
    """When agent_output exists for today: return LLM text."""
    # First register and get user id
    from backend.database import SessionLocal
    from backend.models.user import User
    from backend.models.agent_output import AgentOutput

    client.post("/checkin", json={
        "sleep_hours": 7, "sleep_quality": 4, "mood": 4, "energy": 3, "stress": 2
    }, headers=auth_headers)

    db = SessionLocal()
    user = db.query(User).filter(User.email == "a@b.com").first()
    db.add(AgentOutput(
        user_id=user.id,
        date=date.today(),
        event_type="morning_recommendation",
        readiness_score=72.0,
        intensity="moderate",
        llm_text="Today, go for a moderate run and eat a protein-rich meal.",
    ))
    db.commit()
    db.close()

    response = client.get("/recommendation/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "agent"
    assert "moderate run" in data["llm_text"]
    assert data["intensity"] == "moderate"
```

**Step 2: Run tests — confirm they fail**

```bash
pytest backend/tests/test_recommendations.py -v
```

Expected: `source` key missing — old implementation doesn't have it.

**Step 3: Update backend/routers/recommendations.py**

```python
# backend/routers/recommendations.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.models.agent_output import AgentOutput
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.ml.readiness import compute_readiness_score, get_recommendation

router = APIRouter(prefix="/recommendation", tags=["recommendation"])

@router.get("/today")
def get_today_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    # No check-in yet today
    today_checkin = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.id,
        CheckIn.date == today,
    ).first()

    if not today_checkin:
        return {"status": "no_checkin", "message": "Complete your daily check-in to get a recommendation."}

    # Primary: return LLM-generated recommendation if available
    agent_output = db.query(AgentOutput).filter(
        AgentOutput.user_id == current_user.id,
        AgentOutput.date == today,
        AgentOutput.event_type == "morning_recommendation",
    ).first()

    if agent_output:
        return {
            "status": "ok",
            "source": "agent",
            "readiness_score": agent_output.readiness_score,
            "intensity": agent_output.intensity,
            "llm_text": agent_output.llm_text,
        }

    # Fallback: ML-only recommendation (agent hasn't run yet)
    score = today_checkin.readiness_score or compute_readiness_score(
        today_checkin.sleep_hours, today_checkin.sleep_quality,
        today_checkin.mood, today_checkin.energy, today_checkin.stress,
    )
    rec = get_recommendation(score)
    return {
        "status": "ok",
        "source": "ml_fallback",
        "readiness_score": score,
        **rec,
    }
```

**Step 4: Update RecommendationCard in frontend** (Task 10 in old plan)

The frontend card should render `llm_text` when `source == "agent"`, and the old `message` when `source == "ml_fallback"`. Modify `RecommendationCard.jsx`:

```jsx
// frontend/src/components/RecommendationCard.jsx
export default function RecommendationCard({ data }) {
  if (!data || data.status === "no_checkin") {
    return (
      <div style={{ padding: 16, background: "#f5f5f5", borderRadius: 8 }}>
        <p>Complete your <a href="/checkin">daily check-in</a> to get your recommendation.</p>
      </div>
    );
  }

  const isAgent = data.source === "agent";
  const bgColor = { high: "#e8f5e9", moderate: "#fff8e1", low: "#fce4ec" }[data.intensity] || "#f5f5f5";

  return (
    <div style={{ padding: 16, background: bgColor, borderRadius: 8, marginBottom: 16 }}>
      <div style={{ fontSize: 12, color: "#777", marginBottom: 4 }}>
        {isAgent ? "✨ AI-powered" : "ML recommendation"}
      </div>
      <p style={{ margin: 0, fontSize: 16, lineHeight: 1.5 }}>
        {isAgent ? data.llm_text : data.message}
      </p>
      {!isAgent && (
        <>
          <p><strong>Workout:</strong> {data.workout_suggestion}</p>
          <p><strong>Nutrition:</strong> {data.meal_suggestion}</p>
        </>
      )}
    </div>
  );
}
```

**Step 5: Run all tests**

```bash
pytest backend/tests/ -v
```

Expected: All PASSED

**Step 6: Commit**

```bash
git add backend/routers/recommendations.py backend/tests/test_recommendations.py \
        frontend/src/components/RecommendationCard.jsx
git commit -m "feat: recommendation endpoint uses LLM agent output with ML fallback"
```

---

## Remaining Tasks (Unchanged from Baseline Plan)

Execute these tasks exactly as specified in `2026-02-18-wellsync-implementation.md`:

| Task | Description | Reference |
|------|-------------|-----------|
| Task 2 | Database Models (User, CheckIn, Workout, Meal) | Old plan Task 2 |
| Task 3 | Authentication (JWT) | Old plan Task 3 |
| Task 4 | Check-in Endpoint + Readiness Score | Old plan Task 4 |
| Task 5 | Workout & Meal Logging | Old plan Task 5 |
| Task 6 (old) | ML Personalizer + Insights Endpoint | Old plan Task 7 |
| Task 8 (old) | React Frontend Setup | Old plan Task 8 |
| Task 9 (old) | Auth Screens | Old plan Task 9 |
| Task 10 (old) | Home Dashboard (use updated RecommendationCard) | Old plan Task 10 |
| Task 11 (old) | Check-in, Log, Insights Screens | Old plan Task 11 |
| Task 12 (old) | Demo Seed Script | Old plan Task 12 |
| Task 13 (old) | README + Final Cleanup | Old plan Task 13 |

---

## Complete Task Execution Order

```
M1 → M2 → Task 2 → Task 3 → Task 4 → Task 5
  → Task 6 (ML) → Task 7 (Events) → Task 8 (Agents)
  → Task 9 (Scheduler) → M6 (Recommendations)
  → Task 8–11 (Frontend) → Task 12 (Seed) → Task 13 (README)
```

---

## Manual Demo Test (Φ4 Presentation)

```bash
# 1. Start services
docker compose up --build

# 2. Register a user via the UI or curl
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@aueb.gr","name":"Demo","password":"demo1234"}'

# 3. Log in and get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=demo@aueb.gr&password=demo1234" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 4. Submit check-in
curl -X POST http://localhost:8000/checkin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sleep_hours":6.0,"sleep_quality":3,"mood":3,"energy":2,"stress":4}'

# 5. Manually trigger morning agent (without waiting for 06:00)
curl -X POST http://localhost:8000/internal/trigger-morning \
  -H "Authorization: Bearer $TOKEN"
# (Add this debug endpoint temporarily for the demo)

# 6. Get recommendation — should return LLM text
curl http://localhost:8000/recommendation/today \
  -H "Authorization: Bearer $TOKEN"
```

---

## Phase Checklist

| Deliverable | Status |
|-------------|--------|
| Φ1 form: "AI cross-domain wellness personalization" | [ ] |
| Φ2 slides: problem + idea + competitors + methodology | [ ] |
| Φ3 design doc + UI mockups | [ ] |
| Φ4 GitHub repo + Docker setup + working demo | [ ] |
| Agentic loop: events → queue → gateway → agents | [ ] |
| Claude API integration (MorningRecommendationAgent) | [ ] |
| ML fallback when LLM output not yet available | [ ] |
