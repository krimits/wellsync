"""
Readiness score computation.

Cold start (<14 check-ins): deterministic weighted formula.
Personalized (>=14 check-ins): Ridge Regression per user.
"""
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.checkin import CheckIn


_COLD_START_WEIGHTS = {
    "sleep": 0.35,
    "mood": 0.25,
    "energy": 0.25,
    "stress": 0.15,  # inverted: (10 - stress*2) normalised
}
MIN_DAYS_FOR_PERSONALIZED = 14


def _cold_start_score(checkin: CheckIn) -> float:
    """Deterministic readiness score in range [1, 10]."""
    sleep_norm = (checkin.sleep_hours / 8.0) * 5.0  # map 0-12h → 0-7.5, cap at 5
    sleep_norm = min(sleep_norm, 5.0)
    stress_inv = 6 - checkin.stress  # 1→5, 5→1
    score = (
        _COLD_START_WEIGHTS["sleep"] * sleep_norm
        + _COLD_START_WEIGHTS["mood"] * checkin.mood
        + _COLD_START_WEIGHTS["energy"] * checkin.energy
        + _COLD_START_WEIGHTS["stress"] * stress_inv
    )
    # score is in [1,5] range; normalise to [1,10]
    return round(min(max(score * 2, 1.0), 10.0), 2)


def compute_readiness(
    db: Session, user_id: int, current_checkin: CheckIn
) -> float:
    history = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user_id)
        .order_by(CheckIn.date.desc())
        .all()
    )
    if len(history) < MIN_DAYS_FOR_PERSONALIZED:
        return _cold_start_score(current_checkin)

    # Personalized: use persisted model
    from backend.ml.personalizer import get_or_train_model
    model = get_or_train_model(user_id, history)
    if model is None:
        return _cold_start_score(current_checkin)

    import numpy as np
    X = np.array([[
        current_checkin.sleep_hours,
        current_checkin.sleep_quality,
        current_checkin.mood,
        current_checkin.energy,
        current_checkin.stress,
    ]])
    pred = model.predict(X)[0]
    # pred is energy_next_day (1-5); scale to [1,10]
    return round(min(max(pred * 2, 1.0), 10.0), 2)
