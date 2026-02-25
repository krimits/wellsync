from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.meal import Meal
from backend.models.user import User
from backend.schemas import DashboardStats, CheckInOut, WorkoutOut, MealOut
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_checkins = db.query(func.count(CheckIn.id)).filter(CheckIn.user_id == user.id).scalar()
    total_workouts = db.query(func.count(Workout.id)).filter(Workout.user_id == user.id).scalar()
    total_meals = db.query(func.count(Meal.id)).filter(Meal.user_id == user.id).scalar()

    avg_sleep = db.query(func.avg(CheckIn.sleep_hours)).filter(CheckIn.user_id == user.id).scalar()
    avg_mood = db.query(func.avg(CheckIn.mood)).filter(CheckIn.user_id == user.id).scalar()
    avg_energy = db.query(func.avg(CheckIn.energy)).filter(CheckIn.user_id == user.id).scalar()
    avg_stress = db.query(func.avg(CheckIn.stress)).filter(CheckIn.user_id == user.id).scalar()

    recent_checkins = (
        db.query(CheckIn).filter(CheckIn.user_id == user.id)
        .order_by(CheckIn.date.desc()).limit(7).all()
    )
    recent_workouts = (
        db.query(Workout).filter(Workout.user_id == user.id)
        .order_by(Workout.date.desc()).limit(5).all()
    )
    recent_meals = (
        db.query(Meal).filter(Meal.user_id == user.id)
        .order_by(Meal.date.desc()).limit(5).all()
    )

    return DashboardStats(
        total_checkins=total_checkins or 0,
        total_workouts=total_workouts or 0,
        total_meals=total_meals or 0,
        avg_sleep_hours=round(float(avg_sleep), 1) if avg_sleep else None,
        avg_mood=round(float(avg_mood), 1) if avg_mood else None,
        avg_energy=round(float(avg_energy), 1) if avg_energy else None,
        avg_stress=round(float(avg_stress), 1) if avg_stress else None,
        recent_checkins=recent_checkins,
        recent_workouts=recent_workouts,
        recent_meals=recent_meals,
    )
