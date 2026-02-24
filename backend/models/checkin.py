from datetime import datetime

from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    # Sleep hours: 0.0 – 12.0
    sleep_hours = Column(Float, nullable=False)
    # All scale fields: 1–5
    sleep_quality = Column(Integer, nullable=False)
    mood = Column(Integer, nullable=False)
    energy = Column(Integer, nullable=False)
    stress = Column(Integer, nullable=False)
    # Computed by ML pipeline; null until first prediction run
    readiness_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="checkins")
