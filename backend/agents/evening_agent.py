"""
EveningInsightsAgent

Generates a brief evening summary: what went well, what to improve tomorrow.
"""
from datetime import date

import anthropic
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.config import settings
from backend.database import SessionLocal
from backend.events.event_types import WellnessEvent
from backend.models.agent_output import AgentOutput
from backend.models.checkin import CheckIn
from backend.models.meal import Meal
from backend.models.workout import Workout


class EveningInsightsAgent(BaseAgent):
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
        today = date.today()
        checkin = (
            db.query(CheckIn)
            .filter(CheckIn.user_id == user_id, CheckIn.date == today)
            .first()
        )
        if not checkin:
            return

        workouts = (
            db.query(Workout)
            .filter(Workout.user_id == user_id, Workout.date == today)
            .all()
        )
        meals = (
            db.query(Meal)
            .filter(Meal.user_id == user_id, Meal.date == today)
            .all()
        )

        workout_summary = (
            ", ".join(f"{w.type} {w.duration_min}min RPE={w.rpe}" for w in workouts)
            or "no workout logged"
        )
        meal_summary = (
            ", ".join(f"{m.meal_type}(q={m.quality})" for m in meals)
            or "no meals logged"
        )

        prompt = f"""You are WellSync evening coach. Write a 2-3 sentence evening reflection for today.

Today's data:
- Check-in: sleep={checkin.sleep_hours}h, mood={checkin.mood}/5, energy={checkin.energy}/5, stress={checkin.stress}/5
- Workouts: {workout_summary}
- Meals: {meal_summary}

Give one positive observation and one actionable tip for tomorrow. Be concise and encouraging."""

        try:
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            llm_text = message.content[0].text
        except Exception:
            llm_text = "Great job logging your day! Rest well and aim for 7-8 hours of sleep tonight."

        output = AgentOutput(
            user_id=user_id,
            date=today,
            event_type="evening_summary",
            readiness_score=None,
            intensity=None,
            llm_text=llm_text,
            model_used="claude-haiku-4-5-20251001",
        )
        db.add(output)
        db.commit()
