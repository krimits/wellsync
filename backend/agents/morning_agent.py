"""
MorningRecommendationAgent

Flow:
  1. Load last 7 days check-ins for user
  2. Compute readiness score (cold-start or Ridge)
  3. RAG: retrieve k=2 relevant wellness chunks from pgvector
  4. Build prompt → call Claude claude-haiku-4-5-20251001
  5. Persist AgentOutput row
"""
from datetime import date
from typing import List

import anthropic
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.config import settings
from backend.database import SessionLocal
from backend.events.event_types import WellnessEvent
from backend.ml.readiness import compute_readiness, _cold_start_score
from backend.models.agent_output import AgentOutput
from backend.models.checkin import CheckIn
from backend.models.workout import Workout


INTENSITY_MAP = {
    (1, 3): "rest",
    (4, 5): "light",
    (6, 7): "moderate",
    (8, 10): "high",
}


def _intensity(score: float) -> str:
    for (lo, hi), label in INTENSITY_MAP.items():
        if lo <= score <= hi:
            return label
    return "moderate"


def _build_prompt(user_id: int, readiness: float, checkins: List[CheckIn],
                  workouts: List[Workout], rag_chunks: List[str]) -> str:
    checkin_lines = "\n".join(
        f"  {c.date}: sleep={c.sleep_hours}h(quality {c.sleep_quality}/5), "
        f"mood={c.mood}/5, energy={c.energy}/5, stress={c.stress}/5"
        for c in checkins[-7:]
    )
    workout_lines = "\n".join(
        f"  {w.date}: {w.type} {w.duration_min}min RPE={w.rpe}"
        for w in workouts[-7:]
    ) or "  No workouts logged this week."

    rag_section = "\n".join(f"- {chunk}" for chunk in rag_chunks) if rag_chunks else "N/A"

    return f"""You are WellSync, an AI wellness coach. Generate a concise, friendly morning recommendation.

User data (last 7 days):
Check-ins:
{checkin_lines}
Workouts:
{workout_lines}

Today's readiness score: {readiness}/10
Suggested workout intensity: {_intensity(readiness)}

Evidence-based guidelines (retrieved):
{rag_section}

Write a short (3-4 sentences) personalised morning recommendation covering:
1. Workout suggestion for today based on readiness
2. One nutrition tip
3. One sleep/stress tip

Be warm, specific, and actionable. Do not repeat the raw numbers."""


class MorningRecommendationAgent(BaseAgent):
    async def handle(self, event: WellnessEvent, **kwargs) -> None:
        db: Session = kwargs.get("db") or SessionLocal()
        close_db = "db" not in kwargs
        try:
            for user_id in event.user_ids:
                await self._process_user(db, user_id)
        finally:
            if close_db:
                db.close()

    async def _process_user(self, db: Session, user_id: int) -> None:
        checkins = (
            db.query(CheckIn)
            .filter(CheckIn.user_id == user_id)
            .order_by(CheckIn.date.desc())
            .limit(14)
            .all()
        )
        if not checkins:
            return  # no data yet

        latest = checkins[0]
        readiness = compute_readiness(db, user_id, latest)

        workouts = (
            db.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.date.desc())
            .limit(7)
            .all()
        )

        # RAG retrieval
        rag_chunks: List[str] = []
        try:
            from backend.knowledge.retriever import WellnessRetriever
            query = f"readiness {readiness:.1f} sleep {latest.sleep_hours}h energy {latest.energy} stress {latest.stress}"
            retriever = WellnessRetriever(db)
            rag_chunks = retriever.retrieve(query, k=2)
        except Exception:
            pass  # RAG is optional; continue without it

        prompt = _build_prompt(user_id, readiness, list(reversed(checkins)), list(reversed(workouts)), rag_chunks)

        try:
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            llm_text = message.content[0].text
        except Exception as e:
            llm_text = f"[ML-only] Readiness {readiness}/10. Suggested intensity: {_intensity(readiness)}."

        output = AgentOutput(
            user_id=user_id,
            date=date.today(),
            event_type="morning_recommendation",
            readiness_score=readiness,
            intensity=_intensity(readiness),
            llm_text=llm_text,
            model_used="claude-haiku-4-5-20251001",
        )
        db.add(output)
        db.commit()
