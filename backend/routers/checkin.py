from datetime import date as DateType
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.routers.auth import get_current_user
from backend.models.user import User

router = APIRouter()


# ---------- Schemas ----------

class CheckInRequest(BaseModel):
    date: DateType
    sleep_hours: float = Field(..., ge=0.0, le=12.0)
    sleep_quality: int = Field(..., ge=1, le=5)
    mood: int = Field(..., ge=1, le=5)
    energy: int = Field(..., ge=1, le=5)
    stress: int = Field(..., ge=1, le=5)


class CheckInResponse(BaseModel):
    id: int
    date: DateType
    sleep_hours: float
    sleep_quality: int
    mood: int
    energy: int
    stress: int
    readiness_score: Optional[float]

    class Config:
        from_attributes = True


# ---------- Endpoints ----------

@router.post("", response_model=CheckInResponse, status_code=201)
def create_checkin(
    body: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == current_user.id, CheckIn.date == body.date)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Check-in already exists for this date")

    checkin = CheckIn(
        user_id=current_user.id,
        date=body.date,
        sleep_hours=body.sleep_hours,
        sleep_quality=body.sleep_quality,
        mood=body.mood,
        energy=body.energy,
        stress=body.stress,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    # Compute readiness score immediately (cold-start formula)
    from backend.ml.readiness import compute_readiness
    score = compute_readiness(db, current_user.id, checkin)
    checkin.readiness_score = score
    db.commit()
    db.refresh(checkin)

    return checkin


@router.get("/history", response_model=List[CheckInResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 30,
):
    checkins = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == current_user.id)
        .order_by(CheckIn.date.desc())
        .limit(limit)
        .all()
    )
    return checkins
