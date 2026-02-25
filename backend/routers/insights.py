"""
GET /insights

Returns correlation statistics and recent trends for the authenticated user.
"""
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.models.user import User
from backend.models.workout import Workout
from backend.routers.auth import get_current_user

router = APIRouter()


class TrendPoint(BaseModel):
    date: date
    sleep_hours: float
    mood: int
    energy: int
    stress: int
    readiness_score: Optional[float]


class WorkoutSummary(BaseModel):
    total_sessions: int
    total_minutes: int
    avg_rpe: Optional[float]


class InsightsResponse(BaseModel):
    correlations: dict
    trends: List[TrendPoint]
    workout_summary_30d: WorkoutSummary
    days_logged: int


@router.get("", response_model=InsightsResponse)
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = date.today() - timedelta(days=30)

    checkins = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == current_user.id, CheckIn.date >= since)
        .order_by(CheckIn.date.asc())
        .all()
    )

    workouts = (
        db.query(Workout)
        .filter(Workout.user_id == current_user.id, Workout.date >= since)
        .all()
    )

    # Correlations
    from backend.ml.personalizer import compute_correlations
    all_checkins = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == current_user.id)
        .all()
    )
    correlations = compute_correlations(all_checkins)

    # Trend points
    trends = [
        TrendPoint(
            date=c.date,
            sleep_hours=c.sleep_hours,
            mood=c.mood,
            energy=c.energy,
            stress=c.stress,
            readiness_score=c.readiness_score,
        )
        for c in checkins
    ]

    # Workout summary
    total_min = sum(w.duration_min for w in workouts)
    avg_rpe = (
        round(sum(w.rpe for w in workouts) / len(workouts), 1)
        if workouts else None
    )

    return InsightsResponse(
        correlations=correlations,
        trends=trends,
        workout_summary_30d=WorkoutSummary(
            total_sessions=len(workouts),
            total_minutes=total_min,
            avg_rpe=avg_rpe,
        ),
        days_logged=len(checkins),
    )
