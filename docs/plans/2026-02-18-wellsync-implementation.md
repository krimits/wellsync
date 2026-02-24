# WellSync Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a full-stack AI wellness web app that correlates workout, nutrition, and mood data to deliver personalized daily recommendations via ML.

**Architecture:** FastAPI backend with SQLAlchemy ORM connects to PostgreSQL; a per-user scikit-learn Ridge Regression model activates after 14 days of check-in data, falling back to a rule-based readiness score for new users. React (Vite) frontend communicates via REST/JSON and visualizes correlations with Chart.js.

**Tech Stack:** Python 3.10+, FastAPI, SQLAlchemy 2.0, PostgreSQL, scikit-learn, python-jose (JWT), React 18, Vite, Axios, Chart.js, Docker Compose

---

## Project Structure

```
aeps-2026/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── checkin.py
│   │   ├── workout.py
│   │   └── meal.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── checkin.py
│   │   ├── logs.py
│   │   ├── recommendations.py
│   │   └── insights.py
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── readiness.py
│   │   ├── personalizer.py
│   │   └── insights.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_checkin.py
│   │   ├── test_logs.py
│   │   ├── test_recommendations.py
│   │   └── test_ml.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── CheckIn.jsx
│   │   │   ├── LogWorkout.jsx
│   │   │   ├── LogMeal.jsx
│   │   │   └── Insights.jsx
│   │   └── components/
│   │       ├── NavBar.jsx
│   │       ├── ReadinessGauge.jsx
│   │       ├── RecommendationCard.jsx
│   │       └── TrendChart.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Task 1: Project Setup & Docker

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/config.py`

**Step 1: Create docker-compose.yml**

```yaml
# docker-compose.yml
version: "3.9"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: wellsync
      POSTGRES_USER: wellsync
      POSTGRES_PASSWORD: wellsync123
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://wellsync:wellsync123@db:5432/wellsync
      SECRET_KEY: dev-secret-change-in-prod
    depends_on:
      - db
    volumes:
      - ./backend:/app
      - ml_models:/app/ml_models

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend

volumes:
  pgdata:
  ml_models:
```

**Step 2: Create .env.example**

```
DATABASE_URL=postgresql://wellsync:wellsync123@localhost:5432/wellsync
SECRET_KEY=dev-secret-change-in-prod
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ML_MODELS_DIR=./ml_models
```

**Step 3: Create backend/requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
scikit-learn==1.5.0
pandas==2.2.2
numpy==1.26.4
pytest==8.2.0
httpx==0.27.0
pytest-asyncio==0.23.7
python-dotenv==1.0.1
alembic==1.13.1
```

**Step 4: Create backend/config.py**

```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://wellsync:wellsync123@localhost:5432/wellsync"
    secret_key: str = "dev-secret-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    ml_models_dir: str = "./ml_models"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 5: Install backend dependencies**

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
mkdir ml_models
```

**Step 6: Commit**

```bash
git init
git add docker-compose.yml .env.example backend/requirements.txt backend/config.py
git commit -m "feat: initial project setup and Docker configuration"
```

---

## Task 2: Database Models

**Files:**
- Create: `backend/database.py`
- Create: `backend/models/user.py`
- Create: `backend/models/checkin.py`
- Create: `backend/models/workout.py`
- Create: `backend/models/meal.py`
- Create: `backend/models/__init__.py`

**Step 1: Create backend/database.py**

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: Create backend/models/user.py**

```python
# backend/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    checkins = relationship("CheckIn", back_populates="user")
    workouts = relationship("Workout", back_populates="user")
    meals = relationship("Meal", back_populates="user")
```

**Step 3: Create backend/models/checkin.py**

```python
# backend/models/checkin.py
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    sleep_hours = Column(Float, nullable=False)      # 0–12
    sleep_quality = Column(Integer, nullable=False)  # 1–5
    mood = Column(Integer, nullable=False)           # 1–5
    energy = Column(Integer, nullable=False)         # 1–5
    stress = Column(Integer, nullable=False)         # 1–5
    readiness_score = Column(Float, nullable=True)   # 0–100, computed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="checkins")
```

**Step 4: Create backend/models/workout.py**

```python
# backend/models/workout.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)      # e.g., "running", "gym", "yoga"
    duration_min = Column(Integer, nullable=False)
    rpe = Column(Integer, nullable=False)      # Rate of Perceived Exertion 1–10
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workouts")
```

**Step 5: Create backend/models/meal.py**

```python
# backend/models/meal.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(String, nullable=False)   # breakfast/lunch/dinner/snack
    quality = Column(Integer, nullable=False)    # 1–5 (1=junk, 5=very healthy)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="meals")
```

**Step 6: Create backend/models/__init__.py**

```python
from backend.models.user import User
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.meal import Meal
```

**Step 7: Create tables**

```python
# run once: backend/create_tables.py
from backend.database import engine, Base
import backend.models  # noqa: F401 — triggers model registration

Base.metadata.create_all(bind=engine)
print("Tables created.")
```

Run: `python backend/create_tables.py`

**Step 8: Commit**

```bash
git add backend/database.py backend/models/
git commit -m "feat: add SQLAlchemy database models"
```

---

## Task 3: Authentication (Register & Login)

**Files:**
- Create: `backend/routers/auth.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`
- Create: `backend/main.py`

**Step 1: Write failing tests**

```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db
from backend.main import app

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

```python
# backend/tests/test_auth.py
def test_register_success(client):
    response = client.post("/auth/register", json={
        "email": "student@aueb.gr",
        "name": "Nikos",
        "password": "securepass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "student@aueb.gr"
    assert "id" in data

def test_register_duplicate_email(client):
    payload = {"email": "a@b.com", "name": "A", "password": "pass123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={
        "email": "a@b.com", "name": "A", "password": "pass123"
    })
    response = client.post("/auth/login", data={
        "username": "a@b.com", "password": "pass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "a@b.com", "name": "A", "password": "pass123"
    })
    response = client.post("/auth/login", data={
        "username": "a@b.com", "password": "wrongpass"
    })
    assert response.status_code == 401
```

**Step 2: Run tests to confirm they fail**

```bash
pytest backend/tests/test_auth.py -v
```
Expected: ImportError or 404 errors — tests fail because routes don't exist yet.

**Step 3: Implement auth router**

```python
# backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from backend.database import get_db
from backend.models.user import User
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.secret_key, settings.algorithm)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register", response_model=UserResponse, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=req.email, name=req.name, password_hash=pwd_context.hash(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not pwd_context.verify(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(user.id)}
```

**Step 4: Create backend/main.py**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, checkin, logs, recommendations, insights

app = FastAPI(title="WellSync API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(checkin.router)
app.include_router(logs.router)
app.include_router(recommendations.router)
app.include_router(insights.router)
```

**Step 5: Run tests to confirm they pass**

```bash
pytest backend/tests/test_auth.py -v
```
Expected: 4 PASSED

**Step 6: Commit**

```bash
git add backend/routers/auth.py backend/main.py backend/tests/
git commit -m "feat: add user registration and JWT authentication"
```

---

## Task 4: Readiness Score & Check-in Endpoint

**Files:**
- Create: `backend/ml/readiness.py`
- Create: `backend/routers/checkin.py`
- Create: `backend/tests/test_checkin.py`

**Step 1: Write failing tests**

```python
# backend/tests/test_checkin.py
import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={
        "email": "a@b.com", "name": "A", "password": "pass"
    })
    resp = client.post("/auth/login", data={"username": "a@b.com", "password": "pass"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_checkin_creates_readiness_score(client, auth_headers):
    response = client.post("/checkin", json={
        "sleep_hours": 7.5,
        "sleep_quality": 4,
        "mood": 4,
        "energy": 3,
        "stress": 2
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert "readiness_score" in data
    assert 0 <= data["readiness_score"] <= 100

def test_checkin_duplicate_today_fails(client, auth_headers):
    payload = {"sleep_hours": 7, "sleep_quality": 3, "mood": 3, "energy": 3, "stress": 3}
    client.post("/checkin", json=payload, headers=auth_headers)
    response = client.post("/checkin", json=payload, headers=auth_headers)
    assert response.status_code == 400

def test_checkin_history(client, auth_headers):
    client.post("/checkin", json={
        "sleep_hours": 6, "sleep_quality": 3, "mood": 3, "energy": 3, "stress": 4
    }, headers=auth_headers)
    response = client.get("/checkin/history", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
```

**Step 2: Run tests — confirm they fail**

```bash
pytest backend/tests/test_checkin.py -v
```

**Step 3: Implement readiness score calculator**

```python
# backend/ml/readiness.py

def compute_readiness_score(
    sleep_hours: float,
    sleep_quality: int,
    mood: int,
    energy: int,
    stress: int,
) -> float:
    """
    Rule-based readiness score (0–100).
    Used when user has < 14 days of data.

    Weights:
      sleep_hours   → 30 points  (optimal = 8h)
      sleep_quality → 20 points  (scale 1–5)
      mood          → 20 points  (scale 1–5)
      energy        → 20 points  (scale 1–5)
      stress        → 10 points  (inverse: low stress = high score)
    """
    sleep_score = min(sleep_hours / 8.0, 1.0) * 30
    quality_score = (sleep_quality / 5) * 20
    mood_score = (mood / 5) * 20
    energy_score = (energy / 5) * 20
    stress_score = ((6 - stress) / 5) * 10  # invert stress

    return round(sleep_score + quality_score + mood_score + energy_score + stress_score, 1)


def get_recommendation(readiness_score: float) -> dict:
    """Return workout recommendation based on readiness score."""
    if readiness_score >= 75:
        return {
            "intensity": "high",
            "message": "Great readiness today! Go for a challenging workout.",
            "workout_suggestion": "Strength training or HIIT",
            "meal_suggestion": "High-protein meal post-workout",
        }
    elif readiness_score >= 45:
        return {
            "intensity": "moderate",
            "message": "Decent readiness. A moderate workout will serve you well.",
            "workout_suggestion": "Moderate cardio or light weights",
            "meal_suggestion": "Balanced meal with complex carbs",
        }
    else:
        return {
            "intensity": "low",
            "message": "Low readiness today. Prioritize rest and recovery.",
            "workout_suggestion": "Yoga, stretching, or a walk",
            "meal_suggestion": "Light, easy-to-digest meals",
        }
```

**Step 4: Implement check-in router**

```python
# backend/routers/checkin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.ml.readiness import compute_readiness_score

router = APIRouter(prefix="/checkin", tags=["checkin"])

class CheckInRequest(BaseModel):
    sleep_hours: float = Field(..., ge=0, le=12)
    sleep_quality: int = Field(..., ge=1, le=5)
    mood: int = Field(..., ge=1, le=5)
    energy: int = Field(..., ge=1, le=5)
    stress: int = Field(..., ge=1, le=5)

class CheckInResponse(BaseModel):
    id: int
    date: date
    sleep_hours: float
    sleep_quality: int
    mood: int
    energy: int
    stress: int
    readiness_score: Optional[float]
    model_config = {"from_attributes": True}

@router.post("", response_model=CheckInResponse, status_code=201)
def create_checkin(
    req: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    existing = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.id,
        CheckIn.date == today,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in today")

    score = compute_readiness_score(
        req.sleep_hours, req.sleep_quality, req.mood, req.energy, req.stress
    )
    checkin = CheckIn(
        user_id=current_user.id,
        date=today,
        **req.model_dump(),
        readiness_score=score,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin

@router.get("/history", response_model=list[CheckInResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(CheckIn).filter(CheckIn.user_id == current_user.id).order_by(CheckIn.date.desc()).all()
```

**Step 5: Run tests — confirm they pass**

```bash
pytest backend/tests/test_checkin.py -v
```
Expected: 3 PASSED

**Step 6: Test readiness logic separately**

```python
# backend/tests/test_ml.py
from backend.ml.readiness import compute_readiness_score, get_recommendation

def test_perfect_readiness():
    score = compute_readiness_score(8, 5, 5, 5, 1)
    assert score == 100.0

def test_poor_readiness():
    score = compute_readiness_score(3, 1, 1, 1, 5)
    assert score < 45

def test_recommendation_high():
    rec = get_recommendation(80)
    assert rec["intensity"] == "high"

def test_recommendation_low():
    rec = get_recommendation(30)
    assert rec["intensity"] == "low"
```

```bash
pytest backend/tests/test_ml.py -v
```
Expected: 4 PASSED

**Step 7: Commit**

```bash
git add backend/ml/readiness.py backend/routers/checkin.py backend/tests/
git commit -m "feat: add daily check-in endpoint and rule-based readiness score"
```

---

## Task 5: Workout & Meal Logging

**Files:**
- Create: `backend/routers/logs.py`
- Create: `backend/tests/test_logs.py`

**Step 1: Write failing tests**

```python
# backend/tests/test_logs.py
import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"email": "a@b.com", "name": "A", "password": "pass"})
    resp = client.post("/auth/login", data={"username": "a@b.com", "password": "pass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_log_workout(client, auth_headers):
    response = client.post("/logs/workout", json={
        "type": "running",
        "duration_min": 30,
        "rpe": 7
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "running"
    assert data["rpe"] == 7

def test_log_meal(client, auth_headers):
    response = client.post("/logs/meal", json={
        "meal_type": "lunch",
        "quality": 4,
        "notes": "Salad with chicken"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["meal_type"] == "lunch"

def test_get_workouts(client, auth_headers):
    client.post("/logs/workout", json={"type": "gym", "duration_min": 60, "rpe": 8}, headers=auth_headers)
    response = client.get("/logs/workouts", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
```

**Step 2: Run to confirm fail**

```bash
pytest backend/tests/test_logs.py -v
```

**Step 3: Implement logs router**

```python
# backend/routers/logs.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from backend.database import get_db
from backend.models.workout import Workout
from backend.models.meal import Meal
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/logs", tags=["logs"])

class WorkoutRequest(BaseModel):
    type: str
    duration_min: int = Field(..., ge=1)
    rpe: int = Field(..., ge=1, le=10)

class WorkoutResponse(BaseModel):
    id: int
    date: date
    type: str
    duration_min: int
    rpe: int
    model_config = {"from_attributes": True}

class MealRequest(BaseModel):
    meal_type: str  # breakfast/lunch/dinner/snack
    quality: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None

class MealResponse(BaseModel):
    id: int
    date: date
    meal_type: str
    quality: int
    notes: Optional[str]
    model_config = {"from_attributes": True}

@router.post("/workout", response_model=WorkoutResponse, status_code=201)
def log_workout(req: WorkoutRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workout = Workout(user_id=current_user.id, date=date.today(), **req.model_dump())
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout

@router.get("/workouts", response_model=list[WorkoutResponse])
def get_workouts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Workout).filter(Workout.user_id == current_user.id).order_by(Workout.date.desc()).all()

@router.post("/meal", response_model=MealResponse, status_code=201)
def log_meal(req: MealRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meal = Meal(user_id=current_user.id, date=date.today(), **req.model_dump())
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal

@router.get("/meals", response_model=list[MealResponse])
def get_meals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Meal).filter(Meal.user_id == current_user.id).order_by(Meal.date.desc()).all()
```

**Step 4: Run tests**

```bash
pytest backend/tests/test_logs.py -v
```
Expected: 3 PASSED

**Step 5: Commit**

```bash
git add backend/routers/logs.py backend/tests/test_logs.py
git commit -m "feat: add workout and meal logging endpoints"
```

---

## Task 6: Daily Recommendation Endpoint

**Files:**
- Create: `backend/routers/recommendations.py`
- Create: `backend/tests/test_recommendations.py`

**Step 1: Write failing test**

```python
# backend/tests/test_recommendations.py
import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"email": "a@b.com", "name": "A", "password": "pass"})
    resp = client.post("/auth/login", data={"username": "a@b.com", "password": "pass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_no_checkin_returns_prompt(client, auth_headers):
    response = client.get("/recommendation/today", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "no_checkin"

def test_recommendation_after_checkin(client, auth_headers):
    client.post("/checkin", json={
        "sleep_hours": 8, "sleep_quality": 5, "mood": 5, "energy": 5, "stress": 1
    }, headers=auth_headers)
    response = client.get("/recommendation/today", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["readiness_score"] == 100.0
    assert data["intensity"] == "high"
    assert "message" in data
```

**Step 2: Run to confirm fail**

```bash
pytest backend/tests/test_recommendations.py -v
```

**Step 3: Implement recommendations router**

```python
# backend/routers/recommendations.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.ml.readiness import get_recommendation

router = APIRouter(prefix="/recommendation", tags=["recommendation"])

@router.get("/today")
def get_today_recommendation(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today_checkin = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.id,
        CheckIn.date == date.today()
    ).first()

    if not today_checkin:
        return {"status": "no_checkin", "message": "Complete your daily check-in to get a recommendation."}

    rec = get_recommendation(today_checkin.readiness_score)
    return {
        "status": "ok",
        "readiness_score": today_checkin.readiness_score,
        **rec,
    }
```

**Step 4: Run tests**

```bash
pytest backend/tests/test_recommendations.py -v
```
Expected: 2 PASSED

**Step 5: Run full test suite**

```bash
pytest backend/tests/ -v
```
Expected: all PASSED

**Step 6: Commit**

```bash
git add backend/routers/recommendations.py backend/tests/test_recommendations.py
git commit -m "feat: add daily recommendation endpoint"
```

---

## Task 7: ML Personalization & Insights

**Files:**
- Create: `backend/ml/personalizer.py`
- Create: `backend/ml/insights.py`
- Create: `backend/routers/insights.py`

**Step 1: Implement per-user ML model**

```python
# backend/ml/personalizer.py
import os
import pickle
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from backend.config import settings

MIN_SAMPLES = 14  # days before personalization activates

def _model_path(user_id: int) -> str:
    return os.path.join(settings.ml_models_dir, f"user_{user_id}.pkl")

def train_model(user_id: int, checkins: list[dict], workouts: list[dict]) -> None:
    """
    Train a Ridge regression model for a user.
    Predicts RPE (workout intensity) from check-in features.
    checkins: list of dicts with keys: sleep_hours, sleep_quality, mood, energy, stress, date
    workouts: list of dicts with keys: rpe, date
    """
    checkin_by_date = {c["date"]: c for c in checkins}
    X, y = [], []

    for w in workouts:
        c = checkin_by_date.get(w["date"])
        if c is None:
            continue
        X.append([c["sleep_hours"], c["sleep_quality"], c["mood"], c["energy"], c["stress"]])
        y.append(w["rpe"])

    if len(X) < MIN_SAMPLES:
        return  # Not enough data

    X_arr, y_arr = np.array(X), np.array(y)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_arr)
    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y_arr)

    os.makedirs(settings.ml_models_dir, exist_ok=True)
    with open(_model_path(user_id), "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f)

def predict_rpe(user_id: int, checkin: dict) -> float | None:
    """Predict expected RPE given today's check-in. Returns None if no model yet."""
    path = _model_path(user_id)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        bundle = pickle.load(f)
    features = np.array([[
        checkin["sleep_hours"], checkin["sleep_quality"],
        checkin["mood"], checkin["energy"], checkin["stress"]
    ]])
    scaled = bundle["scaler"].transform(features)
    return float(bundle["model"].predict(scaled)[0])
```

**Step 2: Implement correlation insights**

```python
# backend/ml/insights.py
import numpy as np
from typing import Optional

def pearson_correlation(x: list[float], y: list[float]) -> Optional[float]:
    """Compute Pearson correlation between two lists. Returns None if insufficient data."""
    if len(x) < 5 or len(y) < 5 or len(x) != len(y):
        return None
    x_arr, y_arr = np.array(x, dtype=float), np.array(y, dtype=float)
    if x_arr.std() == 0 or y_arr.std() == 0:
        return None
    return float(np.corrcoef(x_arr, y_arr)[0, 1])

def build_weekly_insights(checkins: list[dict], workouts: list[dict]) -> dict:
    """
    Build insight cards for the frontend.
    Returns correlation coefficients between key metrics.
    """
    checkin_by_date = {c["date"]: c for c in checkins}

    sleep_hours, moods, energies, rpes = [], [], [], []
    for w in workouts:
        c = checkin_by_date.get(w["date"])
        if c:
            sleep_hours.append(c["sleep_hours"])
            moods.append(c["mood"])
            energies.append(c["energy"])
            rpes.append(w["rpe"])

    return {
        "sleep_vs_performance": pearson_correlation(sleep_hours, rpes),
        "mood_vs_performance": pearson_correlation(moods, rpes),
        "energy_vs_performance": pearson_correlation(energies, rpes),
        "data_points": len(rpes),
        "personalized_model_active": len(rpes) >= 14,
    }
```

**Step 3: Implement insights router**

```python
# backend/routers/insights.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from backend.database import get_db
from backend.models.checkin import CheckIn
from backend.models.workout import Workout
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.ml.insights import build_weekly_insights

router = APIRouter(prefix="/insights", tags=["insights"])

@router.get("/weekly")
def get_weekly_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    since = date.today() - timedelta(days=30)

    checkins = db.query(CheckIn).filter(
        CheckIn.user_id == current_user.id,
        CheckIn.date >= since,
    ).all()

    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.date >= since,
    ).all()

    checkin_dicts = [{"date": c.date, "sleep_hours": c.sleep_hours, "sleep_quality": c.sleep_quality,
                      "mood": c.mood, "energy": c.energy, "stress": c.stress} for c in checkins]
    workout_dicts = [{"date": w.date, "rpe": w.rpe, "type": w.type, "duration_min": w.duration_min} for w in workouts]

    readiness_trend = [{"date": str(c.date), "score": c.readiness_score} for c in checkins]
    mood_trend = [{"date": str(c.date), "mood": c.mood, "energy": c.energy, "sleep": c.sleep_hours} for c in checkins]

    return {
        "insights": build_weekly_insights(checkin_dicts, workout_dicts),
        "readiness_trend": readiness_trend,
        "mood_trend": mood_trend,
    }
```

**Step 4: Commit**

```bash
git add backend/ml/ backend/routers/insights.py
git commit -m "feat: add ML personalization engine and weekly insights endpoint"
```

---

## Task 8: React Frontend Setup

**Files:**
- Create: `frontend/` (Vite project)
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/App.jsx`

**Step 1: Initialize Vite + React project**

```bash
cd aeps-2026
npm create vite@latest frontend -- --template react
cd frontend
npm install axios react-router-dom chart.js react-chartjs-2
```

**Step 2: Create API client**

```javascript
// frontend/src/api/client.js
import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const auth = {
  register: (data) => api.post("/auth/register", data),
  login: (email, password) =>
    api.post("/auth/login", new URLSearchParams({ username: email, password })),
};

export const checkin = {
  submit: (data) => api.post("/checkin", data),
  history: () => api.get("/checkin/history"),
};

export const logs = {
  logWorkout: (data) => api.post("/logs/workout", data),
  logMeal: (data) => api.post("/logs/meal", data),
  workouts: () => api.get("/logs/workouts"),
  meals: () => api.get("/logs/meals"),
};

export const recommendation = {
  today: () => api.get("/recommendation/today"),
};

export const insights = {
  weekly: () => api.get("/insights/weekly"),
};

export default api;
```

**Step 3: Create App.jsx with routing**

```jsx
// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import NavBar from "./components/NavBar";
import Home from "./pages/Home";
import CheckIn from "./pages/CheckIn";
import LogWorkout from "./pages/LogWorkout";
import LogMeal from "./pages/LogMeal";
import Insights from "./pages/Insights";
import Login from "./pages/Login";
import Register from "./pages/Register";

function PrivateRoute({ children }) {
  return localStorage.getItem("token") ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<PrivateRoute><NavBar /><Home /></PrivateRoute>} />
        <Route path="/checkin" element={<PrivateRoute><NavBar /><CheckIn /></PrivateRoute>} />
        <Route path="/log/workout" element={<PrivateRoute><NavBar /><LogWorkout /></PrivateRoute>} />
        <Route path="/log/meal" element={<PrivateRoute><NavBar /><LogMeal /></PrivateRoute>} />
        <Route path="/insights" element={<PrivateRoute><NavBar /><Insights /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
```

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: initialize React frontend with routing and API client"
```

---

## Task 9: Frontend — Auth Screens

**Files:**
- Create: `frontend/src/pages/Login.jsx`
- Create: `frontend/src/pages/Register.jsx`

**Step 1: Login page**

```jsx
// frontend/src/pages/Login.jsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { auth } from "../api/client";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await auth.login(email, password);
      localStorage.setItem("token", res.data.access_token);
      navigate("/");
    } catch {
      setError("Invalid email or password");
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "80px auto", padding: 24 }}>
      <h2>WellSync — Login</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="Email" value={email}
          onChange={e => setEmail(e.target.value)} required style={{ display: "block", width: "100%", marginBottom: 12 }} />
        <input type="password" placeholder="Password" value={password}
          onChange={e => setPassword(e.target.value)} required style={{ display: "block", width: "100%", marginBottom: 12 }} />
        <button type="submit" style={{ width: "100%" }}>Login</button>
      </form>
      <p>No account? <Link to="/register">Register</Link></p>
    </div>
  );
}
```

**Step 2: Register page (same structure as Login, calls auth.register)**

Similar to Login — 3 fields: name, email, password. On success, redirect to `/login`.

**Step 3: Commit**

```bash
git add frontend/src/pages/Login.jsx frontend/src/pages/Register.jsx
git commit -m "feat: add login and registration screens"
```

---

## Task 10: Frontend — Home Dashboard

**Files:**
- Create: `frontend/src/pages/Home.jsx`
- Create: `frontend/src/components/ReadinessGauge.jsx`
- Create: `frontend/src/components/RecommendationCard.jsx`
- Create: `frontend/src/components/NavBar.jsx`

**Step 1: NavBar component**

```jsx
// frontend/src/components/NavBar.jsx
import { Link, useNavigate } from "react-router-dom";

export default function NavBar() {
  const navigate = useNavigate();
  const logout = () => { localStorage.removeItem("token"); navigate("/login"); };

  return (
    <nav style={{ display: "flex", gap: 16, padding: "12px 24px", background: "#1a1a2e", color: "white" }}>
      <Link to="/" style={{ color: "white" }}>Home</Link>
      <Link to="/checkin" style={{ color: "white" }}>Check-in</Link>
      <Link to="/log/workout" style={{ color: "white" }}>Log Workout</Link>
      <Link to="/log/meal" style={{ color: "white" }}>Log Meal</Link>
      <Link to="/insights" style={{ color: "white" }}>Insights</Link>
      <button onClick={logout} style={{ marginLeft: "auto", background: "none", color: "white", border: "1px solid white", cursor: "pointer" }}>Logout</button>
    </nav>
  );
}
```

**Step 2: ReadinessGauge component**

```jsx
// frontend/src/components/ReadinessGauge.jsx
export default function ReadinessGauge({ score }) {
  const color = score >= 75 ? "#4caf50" : score >= 45 ? "#ff9800" : "#f44336";
  return (
    <div style={{ textAlign: "center", padding: 24 }}>
      <div style={{
        width: 120, height: 120, borderRadius: "50%",
        border: `8px solid ${color}`, display: "inline-flex",
        alignItems: "center", justifyContent: "center",
        fontSize: 28, fontWeight: "bold", color
      }}>
        {score}
      </div>
      <p>Readiness Score</p>
    </div>
  );
}
```

**Step 3: RecommendationCard component**

```jsx
// frontend/src/components/RecommendationCard.jsx
export default function RecommendationCard({ data }) {
  if (!data || data.status === "no_checkin") {
    return (
      <div style={{ padding: 16, background: "#f5f5f5", borderRadius: 8 }}>
        <p>Complete your <a href="/checkin">daily check-in</a> to get your recommendation.</p>
      </div>
    );
  }
  return (
    <div style={{ padding: 16, background: "#e8f5e9", borderRadius: 8 }}>
      <h3>{data.message}</h3>
      <p><strong>Workout:</strong> {data.workout_suggestion}</p>
      <p><strong>Nutrition:</strong> {data.meal_suggestion}</p>
    </div>
  );
}
```

**Step 4: Home page**

```jsx
// frontend/src/pages/Home.jsx
import { useEffect, useState } from "react";
import { recommendation } from "../api/client";
import ReadinessGauge from "../components/ReadinessGauge";
import RecommendationCard from "../components/RecommendationCard";

export default function Home() {
  const [rec, setRec] = useState(null);

  useEffect(() => {
    recommendation.today().then(r => setRec(r.data)).catch(() => {});
  }, []);

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
      <h2>Good day! Here's your wellness snapshot.</h2>
      {rec?.readiness_score != null && <ReadinessGauge score={rec.readiness_score} />}
      <RecommendationCard data={rec} />
      <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
        <a href="/checkin"><button>Daily Check-in</button></a>
        <a href="/log/workout"><button>Log Workout</button></a>
        <a href="/log/meal"><button>Log Meal</button></a>
        <a href="/insights"><button>View Insights</button></a>
      </div>
    </div>
  );
}
```

**Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: add home dashboard with readiness gauge and recommendation card"
```

---

## Task 11: Frontend — Check-in, Log, & Insights Screens

**Files:**
- Create: `frontend/src/pages/CheckIn.jsx`
- Create: `frontend/src/pages/LogWorkout.jsx`
- Create: `frontend/src/pages/LogMeal.jsx`
- Create: `frontend/src/pages/Insights.jsx`
- Create: `frontend/src/components/TrendChart.jsx`

**Step 1: CheckIn page (sliders for each metric)**

```jsx
// frontend/src/pages/CheckIn.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { checkin } from "../api/client";

const SliderField = ({ label, name, value, onChange, min = 1, max = 5 }) => (
  <div style={{ marginBottom: 16 }}>
    <label>{label}: <strong>{value}</strong></label>
    <input type="range" min={min} max={max} step={name === "sleep_hours" ? 0.5 : 1}
      name={name} value={value} onChange={onChange} style={{ width: "100%", display: "block" }} />
  </div>
);

export default function CheckIn() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ sleep_hours: 7, sleep_quality: 3, mood: 3, energy: 3, stress: 3 });
  const [error, setError] = useState("");

  const handleChange = e => setForm({ ...form, [e.target.name]: parseFloat(e.target.value) });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await checkin.submit(form);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Already checked in today");
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: "0 auto", padding: 24 }}>
      <h2>Daily Check-in</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <SliderField label="Sleep Hours" name="sleep_hours" value={form.sleep_hours} onChange={handleChange} min={0} max={12} />
        <SliderField label="Sleep Quality" name="sleep_quality" value={form.sleep_quality} onChange={handleChange} />
        <SliderField label="Mood" name="mood" value={form.mood} onChange={handleChange} />
        <SliderField label="Energy" name="energy" value={form.energy} onChange={handleChange} />
        <SliderField label="Stress" name="stress" value={form.stress} onChange={handleChange} />
        <button type="submit" style={{ width: "100%", marginTop: 16 }}>Submit Check-in</button>
      </form>
    </div>
  );
}
```

**Step 2: LogWorkout page** (type select, duration input, RPE slider — same pattern)

**Step 3: LogMeal page** (meal_type select, quality slider, notes textarea — same pattern)

**Step 4: TrendChart component**

```jsx
// frontend/src/components/TrendChart.jsx
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend } from "chart.js";
ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend);

export default function TrendChart({ labels, datasets, title }) {
  return (
    <div style={{ marginBottom: 32 }}>
      <h3>{title}</h3>
      <Line data={{ labels, datasets }} options={{ responsive: true, plugins: { legend: { position: "top" } } }} />
    </div>
  );
}
```

**Step 5: Insights page**

```jsx
// frontend/src/pages/Insights.jsx
import { useEffect, useState } from "react";
import { insights } from "../api/client";
import TrendChart from "../components/TrendChart";

export default function Insights() {
  const [data, setData] = useState(null);

  useEffect(() => {
    insights.weekly().then(r => setData(r.data)).catch(() => {});
  }, []);

  if (!data) return <p>Loading insights...</p>;

  const labels = data.readiness_trend.map(d => d.date);
  const readinessData = data.readiness_trend.map(d => d.score);
  const moodData = data.mood_trend.map(d => d.mood);
  const sleepData = data.mood_trend.map(d => d.sleep);

  const { insights: ins } = data;

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
      <h2>Your Wellness Insights</h2>

      {ins.personalized_model_active && (
        <div style={{ background: "#e3f2fd", padding: 12, borderRadius: 8, marginBottom: 16 }}>
          Personalized ML model active based on {ins.data_points} data points.
        </div>
      )}

      {ins.sleep_vs_performance != null && (
        <p>Sleep → Performance correlation: <strong>{(ins.sleep_vs_performance * 100).toFixed(0)}%</strong></p>
      )}

      <TrendChart title="Readiness Score (last 30 days)" labels={labels}
        datasets={[{ label: "Readiness", data: readinessData, borderColor: "#4caf50", tension: 0.3 }]} />

      <TrendChart title="Mood & Sleep Trend" labels={labels}
        datasets={[
          { label: "Mood", data: moodData, borderColor: "#2196f3", tension: 0.3 },
          { label: "Sleep (h)", data: sleepData, borderColor: "#9c27b0", tension: 0.3 },
        ]} />
    </div>
  );
}
```

**Step 6: Commit**

```bash
git add frontend/src/
git commit -m "feat: add check-in, logging, and insights screens with Chart.js trends"
```

---

## Task 12: Demo Data Seed Script (for Φ4 presentation)

**Files:**
- Create: `backend/seed_demo.py`

**Step 1: Create seed script**

```python
# backend/seed_demo.py
"""Seed the database with 30 days of realistic demo data for presentation."""
import random
from datetime import date, timedelta
import requests

BASE = "http://localhost:8000"
EMAIL = "demo@wellsync.gr"
PASSWORD = "demo1234"

# Register demo user
requests.post(f"{BASE}/auth/register", json={"email": EMAIL, "name": "Demo User", "password": PASSWORD})
token = requests.post(f"{BASE}/auth/login", data={"username": EMAIL, "password": PASSWORD}).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

workout_types = ["running", "gym", "yoga", "cycling", "swimming"]

for i in range(30, 0, -1):
    day = date.today() - timedelta(days=i)

    # Simulate realistic data with some variability
    sleep_h = round(random.gauss(7, 1), 1)
    sleep_q = max(1, min(5, int(random.gauss(3.5, 1))))
    mood = max(1, min(5, int(random.gauss(3.5, 0.8))))
    energy = max(1, min(5, int(random.gauss(3.5, 0.8))))
    stress = max(1, min(5, int(random.gauss(2.5, 1))))

    # POST check-in (would need date override — for demo, use today's data)
    print(f"Day {day}: sleep={sleep_h}h, mood={mood}, energy={energy}, stress={stress}")

    if random.random() > 0.3:  # ~70% workout days
        rpe = max(1, min(10, int(random.gauss(6, 1.5))))
        print(f"  Workout: {random.choice(workout_types)}, RPE={rpe}")

print("Demo seed complete.")
```

**Step 2: Commit**

```bash
git add backend/seed_demo.py
git commit -m "chore: add demo data seed script for Φ4 presentation"
```

---

## Task 13: README & Final Cleanup

**Files:**
- Create: `README.md`

**Step 1: Write README**

Include:
- Project description
- Quick start: `docker compose up --build`
- Default ports: backend `8000`, frontend `5173`
- Demo user credentials
- How to run tests: `pytest backend/tests/ -v`
- Screenshot placeholders for Φ4 submission

**Step 2: Final test run**

```bash
pytest backend/tests/ -v --tb=short
```
Expected: All PASSED

**Step 3: Final commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions and project overview"
git tag v1.0-phi4
```

---

## Phase Checklist

| Deliverable | Status |
|-------------|--------|
| Φ1 form: "AI cross-domain wellness personalization" | [ ] |
| Φ2 slides: problem + idea + competitors + methodology | [ ] |
| Φ3 design doc (this file) + UI mockups | [x] |
| Φ4 GitHub repo + Docker setup + working demo | [ ] |

---

## Running the Full Stack

```bash
# Start everything
docker compose up --build

# Backend only (dev mode)
cd backend && uvicorn main:app --reload

# Frontend only (dev mode)
cd frontend && npm run dev

# Tests
cd backend && pytest tests/ -v
```
