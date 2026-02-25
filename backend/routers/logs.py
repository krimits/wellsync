from datetime import date as DateType
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.meal import Meal
from backend.models.workout import Workout
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter()


# ---------- Workout Schemas ----------

class WorkoutRequest(BaseModel):
    date: DateType
    type: str = Field(..., min_length=1, max_length=100)
    duration_min: int = Field(..., ge=1, le=600)
    rpe: int = Field(..., ge=1, le=10)


class WorkoutResponse(BaseModel):
    id: int
    date: DateType
    type: str
    duration_min: int
    rpe: int

    class Config:
        from_attributes = True


# ---------- Meal Schemas ----------

class MealRequest(BaseModel):
    date: DateType
    meal_type: str = Field(..., pattern="^(breakfast|lunch|dinner|snack)$")
    quality: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None


class MealResponse(BaseModel):
    id: int
    date: DateType
    meal_type: str
    quality: int
    notes: Optional[str]

    class Config:
        from_attributes = True


# ---------- Workout Endpoints ----------

@router.post("/workout", response_model=WorkoutResponse, status_code=201, tags=["logs"])
def log_workout(
    body: WorkoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout = Workout(
        user_id=current_user.id,
        date=body.date,
        type=body.type,
        duration_min=body.duration_min,
        rpe=body.rpe,
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.get("/workout/history", response_model=List[WorkoutResponse], tags=["logs"])
def get_workout_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 30,
):
    return (
        db.query(Workout)
        .filter(Workout.user_id == current_user.id)
        .order_by(Workout.date.desc())
        .limit(limit)
        .all()
    )


# ---------- Meal Endpoints ----------

@router.post("/meal", response_model=MealResponse, status_code=201, tags=["logs"])
def log_meal(
    body: MealRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    meal = Meal(
        user_id=current_user.id,
        date=body.date,
        meal_type=body.meal_type,
        quality=body.quality,
        notes=body.notes,
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


@router.get("/meal/history", response_model=List[MealResponse], tags=["logs"])
def get_meal_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 30,
):
    return (
        db.query(Meal)
        .filter(Meal.user_id == current_user.id)
        .order_by(Meal.date.desc())
        .limit(limit)
        .all()
    )
