from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ── Auth ──────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── CheckIn ───────────────────────────────────────────────
class CheckInCreate(BaseModel):
    date: date
    sleep_hours: float
    sleep_quality: int
    mood: int
    energy: int
    stress: int


class CheckInOut(BaseModel):
    id: int
    user_id: int
    date: date
    sleep_hours: float
    sleep_quality: int
    mood: int
    energy: int
    stress: int
    readiness_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Workout ───────────────────────────────────────────────
class WorkoutCreate(BaseModel):
    date: date
    type: str
    duration_min: int
    rpe: int


class WorkoutOut(BaseModel):
    id: int
    user_id: int
    date: date
    type: str
    duration_min: int
    rpe: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Meal ──────────────────────────────────────────────────
class MealCreate(BaseModel):
    date: date
    meal_type: str
    quality: int
    notes: Optional[str] = None


class MealOut(BaseModel):
    id: int
    user_id: int
    date: date
    meal_type: str
    quality: int
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_checkins: int
    total_workouts: int
    total_meals: int
    avg_sleep_hours: Optional[float] = None
    avg_mood: Optional[float] = None
    avg_energy: Optional[float] = None
    avg_stress: Optional[float] = None
    recent_checkins: List[CheckInOut] = []
    recent_workouts: List[WorkoutOut] = []
    recent_meals: List[MealOut] = []
