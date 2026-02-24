from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    # e.g. "morning_recommendation", "evening_insights", "model_retraining"
    event_type = Column(String, nullable=False)
    # ML-derived readiness score at time of generation; nullable for non-checkin events
    readiness_score = Column(Float, nullable=True)
    # e.g. "low", "moderate", "high" — workout intensity suggestion
    intensity = Column(String, nullable=True)
    # Full LLM-generated text response
    llm_text = Column(Text, nullable=False)
    model_used = Column(String, nullable=False, default="claude-haiku-4-5-20251001")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="agent_outputs")
