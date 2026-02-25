"""
APScheduler-based event scheduler embedded in FastAPI lifespan.

Fires WellnessEvents at:
  - 08:00 daily → MORNING_RECOMMENDATION
  - 21:00 daily → EVENING_SUMMARY
  - 03:00 daily → MODEL_RETRAINING
"""
import asyncio
import logging
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.events.event_types import EventType, WellnessEvent
from backend.events.gateway import EventGateway
from backend.events.queue import get_event_queue
from backend.models.user import User

logger = logging.getLogger(__name__)


def _all_user_ids(db: Session) -> List[int]:
    return [row.id for row in db.query(User.id).all()]


async def _fire_event(event_type: EventType, gateway: EventGateway) -> None:
    queue = get_event_queue()
    db = SessionLocal()
    try:
        user_ids = _all_user_ids(db)
        if not user_ids:
            return
        event = WellnessEvent(type=event_type, user_ids=user_ids)
        await queue.put(event)
        await gateway.dispatch(event, db=db)
    except Exception as e:
        logger.error("Scheduler error for %s: %s", event_type, e)
    finally:
        db.close()


def build_scheduler(gateway: EventGateway) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Athens")

    scheduler.add_job(
        _fire_event,
        "cron",
        hour=8,
        minute=0,
        args=[EventType.MORNING_RECOMMENDATION, gateway],
        id="morning_recommendation",
    )
    scheduler.add_job(
        _fire_event,
        "cron",
        hour=21,
        minute=0,
        args=[EventType.EVENING_SUMMARY, gateway],
        id="evening_summary",
    )
    scheduler.add_job(
        _fire_event,
        "cron",
        hour=3,
        minute=0,
        args=[EventType.MODEL_RETRAINING, gateway],
        id="model_retraining",
    )

    return scheduler
