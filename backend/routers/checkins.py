from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.models.user import User
from backend.schemas import CheckInCreate, CheckInOut
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/api/checkins", tags=["checkins"])


@router.post("/", response_model=CheckInOut, status_code=201)
def create_checkin(
    payload: CheckInCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existing = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user.id, CheckIn.date == payload.date)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Check-in already exists for this date")

    checkin = CheckIn(user_id=user.id, **payload.model_dump())
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


@router.get("/", response_model=List[CheckInOut])
def list_checkins(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user.id)
        .order_by(CheckIn.date.desc())
        .limit(30)
        .all()
    )
