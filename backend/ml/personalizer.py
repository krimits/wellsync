"""
Per-user Ridge Regression personalizer.

Features: [sleep_hours, sleep_quality, mood, energy, stress]
Target:    energy value of the NEXT check-in (as proxy for 'how well the user
           will feel tomorrow given today's inputs')

Models are pickled under settings.ml_models_dir/user_{id}.pkl.
"""
import os
import pickle
from typing import List, Optional

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from backend.config import settings
from backend.models.checkin import CheckIn


def _model_path(user_id: int) -> str:
    os.makedirs(settings.ml_models_dir, exist_ok=True)
    return os.path.join(settings.ml_models_dir, f"user_{user_id}.pkl")


def _build_dataset(history: List[CheckIn]):
    """
    Build (X, y) from sorted check-in history.
    history: list of CheckIn ordered by date ascending.
    """
    sorted_history = sorted(history, key=lambda c: c.date)
    X, y = [], []
    for i in range(len(sorted_history) - 1):
        c = sorted_history[i]
        c_next = sorted_history[i + 1]
        X.append([
            c.sleep_hours,
            c.sleep_quality,
            c.mood,
            c.energy,
            c.stress,
        ])
        y.append(c_next.energy)
    return np.array(X), np.array(y)


def train_model(user_id: int, history: List[CheckIn]) -> Optional[Pipeline]:
    X, y = _build_dataset(history)
    if len(X) < 7:
        return None
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("ridge", Ridge(alpha=1.0)),
    ])
    model.fit(X, y)
    with open(_model_path(user_id), "wb") as f:
        pickle.dump(model, f)
    return model


def load_model(user_id: int) -> Optional[Pipeline]:
    path = _model_path(user_id)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def get_or_train_model(user_id: int, history: List[CheckIn]) -> Optional[Pipeline]:
    model = load_model(user_id)
    if model is not None:
        return model
    return train_model(user_id, history)


def retrain_model(user_id: int, history: List[CheckIn]) -> Optional[Pipeline]:
    """Force retrain and persist. Called by ModelRetrainingAgent."""
    return train_model(user_id, history)


def compute_correlations(history: List[CheckIn]) -> dict:
    """Return Pearson correlations for insights endpoint."""
    if len(history) < 5:
        return {}
    sorted_h = sorted(history, key=lambda c: c.date)
    sleep = np.array([c.sleep_hours for c in sorted_h])
    mood = np.array([c.mood for c in sorted_h])
    energy = np.array([c.energy for c in sorted_h])
    stress = np.array([c.stress for c in sorted_h])

    def safe_corr(a, b) -> float:
        if np.std(a) == 0 or np.std(b) == 0:
            return 0.0
        return round(float(np.corrcoef(a, b)[0, 1]), 3)

    return {
        "sleep_mood": safe_corr(sleep, mood),
        "sleep_energy": safe_corr(sleep, energy),
        "stress_energy": safe_corr(stress, energy),
        "mood_energy": safe_corr(mood, energy),
    }
