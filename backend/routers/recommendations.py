"""
GET /recommendations/today

Returns today's morning recommendation.
Primary source: agent_outputs table (MorningRecommendationAgent output).
Fallback: ML-only readiness score if no agent output yet.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models.agent_output import AgentOutput
from backend.models.checkin import CheckIn
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter()


class RecommendationResponse(BaseModel):
    date: date
    readiness_score: Optional[float]
    intensity: Optional[str]
    recommendation: str
    source: str  # "agent" | "ml_fallback" | "no_data"


@router.get("/today", response_model=RecommendationResponse)
def get_today_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    # Primary: agent output
    agent_output = (
        db.query(AgentOutput)
        .filter(
            AgentOutput.user_id == current_user.id,
            AgentOutput.date == today,
            AgentOutput.event_type == "morning_recommendation",
        )
        .order_by(AgentOutput.created_at.desc())
        .first()
    )
    if agent_output:
        return RecommendationResponse(
            date=today,
            readiness_score=agent_output.readiness_score,
            intensity=agent_output.intensity,
            recommendation=agent_output.llm_text,
            source="agent",
        )

    # Fallback: compute ML readiness from latest check-in
    latest_checkin = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == current_user.id)
        .order_by(CheckIn.date.desc())
        .first()
    )
    if not latest_checkin:
        return RecommendationResponse(
            date=today,
            readiness_score=None,
            intensity=None,
            recommendation="Log your first check-in to get personalised recommendations!",
            source="no_data",
        )

    from backend.ml.readiness import compute_readiness
    from backend.agents.morning_agent import _intensity
    score = compute_readiness(db, current_user.id, latest_checkin)
    intensity = _intensity(score)
    text = (
        f"Your readiness score is {score}/10 — suggesting {intensity} activity today. "
        "Your personalised AI recommendation will be ready after your morning check-in is processed."
    )
    return RecommendationResponse(
        date=today,
        readiness_score=score,
        intensity=intensity,
        recommendation=text,
        source="ml_fallback",
    )
