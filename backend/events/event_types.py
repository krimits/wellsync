from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List

class EventType(str, Enum):
    MORNING_RECOMMENDATION = "morning_recommendation"
    EVENING_SUMMARY = "evening_summary"
    MODEL_RETRAINING = "model_retraining"

@dataclass
class WellnessEvent:
    type: EventType
    user_ids: List[int] = field(default_factory=list)
    fired_at: datetime = field(default_factory=datetime.utcnow)
