from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.workout import Workout
from backend.models.user import User
from backend.schemas import WorkoutCreate, WorkoutOut
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/api/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutOut, status_code=201)
def create_workout(
    payload: WorkoutCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workout = Workout(user_id=user.id, **payload.model_dump())
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.get("/", response_model=List[WorkoutOut])
def list_workouts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Workout)
        .filter(Workout.user_id == user.id)
        .order_by(Workout.date.desc())
        .limit(30)
        .all()
    )
