"""
ModelRetrainingAgent

Retrain per-user Ridge Regression model when user has >= 14 check-ins.
"""
from sqlalchemy.orm import Session

from backend.agents.base import BaseAgent
from backend.database import SessionLocal
from backend.events.event_types import WellnessEvent
from backend.ml.personalizer import retrain_model, MIN_DAYS_FOR_PERSONALIZED
from backend.models.checkin import CheckIn


# MIN_DAYS_FOR_PERSONALIZED imported from readiness module
_MIN_DAYS = MIN_DAYS_FOR_PERSONALIZED


class ModelRetrainingAgent(BaseAgent):
    async def handle(self, event: WellnessEvent, **kwargs) -> None:
        db: Session = kwargs.get("db") or SessionLocal()
        close_db = "db" not in kwargs
        try:
            for user_id in event.user_ids:
                history = (
                    db.query(CheckIn)
                    .filter(CheckIn.user_id == user_id)
                    .all()
                )
                if len(history) >= _MIN_DAYS:
                    retrain_model(user_id, history)
        finally:
            if close_db:
                db.close()
