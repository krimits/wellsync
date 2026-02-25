from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.meal import Meal
from backend.models.user import User
from backend.schemas import MealCreate, MealOut
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/api/meals", tags=["meals"])


@router.post("/", response_model=MealOut, status_code=201)
def create_meal(
    payload: MealCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    meal = Meal(user_id=user.id, **payload.model_dump())
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


@router.get("/", response_model=List[MealOut])
def list_meals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Meal)
        .filter(Meal.user_id == user.id)
        .order_by(Meal.date.desc())
        .limit(30)
        .all()
    )
