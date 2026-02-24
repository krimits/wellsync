# WellSync — Design Document
**Date**: 2026-02-18
**Course**: Ανάπτυξη Εφαρμογών Πληροφοριακών Συστημάτων, AUEB 2026
**Instructor**: Ι. Κωτίδης
**Status**: Approved

---

## 1. Overview

**WellSync** is an AI-powered holistic wellness web application targeting students and young adults (18–30). It tracks three domains — physical activity, nutrition, and mental state — and uses ML personalization to discover individual patterns and deliver adaptive daily recommendations.

### The Problem
Existing wellness apps are siloed: MyFitnessPal covers nutrition, Strava covers workouts, Headspace covers mental health. None correlate all three domains or adapt recommendations to each user's personal patterns over time.

### The Innovation
WellSync treats the user as a system: it collects daily check-in data (sleep, mood, energy, stress), activity logs, and meal logs, then applies per-user ML models to surface correlations (e.g., "your workout output drops 40% after <6h sleep combined with exam stress") and adjust daily recommendations dynamically.

---

## 2. Target Audience

**Primary**: Students and young professionals (18–30) who exercise casually or semi-regularly and want a unified view of their health without the complexity of clinical tools.

**Key pain points**:
- Inconsistent routines due to academic/work pressure
- No visibility into how sleep, diet, and mood affect physical performance
- Existing apps require too much manual input to be sustainable

---

## 3. Core User Loop

```
Morning
└── Daily Check-in (~2 min)
    ├── Sleep: hours (slider) + quality (1–5)
    ├── Mood: 1–5 scale (emoji-based)
    ├── Energy: 1–5 scale
    └── Stress: 1–5 scale

    ↓
    ML Engine computes "Readiness Score" (0–100)
    ↓
    Home screen shows today's recommendation card
    (e.g., "Light workout today — your readiness is 42/100")

During the Day
├── Log Workout: type, duration, perceived intensity (RPE 1–10)
└── Log Meal: category (balanced / junk / skipped) + optional notes

Evening
└── Dashboard refresh
    ├── Weekly correlation graphs
    └── Insight card ("This week: better sleep → +23% energy")
```

---

## 4. Features (MVP for Φ4)

### Must Have
- User registration & authentication (JWT)
- Daily check-in form (sleep, mood, energy, stress)
- Workout logging (type, duration, RPE)
- Meal logging (simplified — category + quality rating)
- Readiness Score calculation
- Daily recommendation card
- Dashboard with trend graphs (last 7 / 30 days)
- ML personalization (activates after 14 days of data)

### Nice to Have (if time allows)
- Weekly summary email/notification
- Goal setting (e.g., "exercise 3x/week")
- Streak tracking / gamification
- Export data as CSV

### Out of Scope
- Calorie counting / macros (too complex, not the focus)
- Wearable device integration
- Social/community features
- Native mobile app

---

## 5. Architecture

```
┌─────────────────────────────────────────────────────┐
│                    React Frontend                    │
│  (Dashboard, Check-in, Logging, Insights screens)   │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Backend                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  Auth (JWT) │  │  Logging API │  │ ML Service │  │
│  └─────────────┘  └──────────────┘  └────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐         ┌──────────▼────────┐
│  PostgreSQL DB │         │  ML Models (disk)  │
│  (user data,   │         │  (scikit-learn,    │
│   logs, scores)│         │   per-user pickle) │
└────────────────┘         └───────────────────┘
```

### Backend Structure (FastAPI)
```
backend/
├── main.py
├── routers/
│   ├── auth.py          # register, login, refresh
│   ├── checkin.py       # POST /checkin, GET /checkin/history
│   ├── logs.py          # POST /workout, POST /meal
│   ├── recommendations.py  # GET /recommendation/today
│   └── insights.py      # GET /insights/weekly
├── models/
│   ├── user.py
│   ├── checkin.py
│   ├── workout.py
│   └── meal.py
├── ml/
│   ├── readiness.py     # Readiness Score calculator
│   ├── personalizer.py  # Per-user model training & inference
│   └── insights.py      # Correlation analysis
└── database.py          # SQLAlchemy + PostgreSQL
```

### Frontend Structure (React)
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Home.jsx         # Dashboard + recommendation card
│   │   ├── CheckIn.jsx      # Daily check-in form
│   │   ├── LogWorkout.jsx
│   │   ├── LogMeal.jsx
│   │   └── Insights.jsx     # Correlation graphs
│   ├── components/
│   │   ├── ReadinessGauge.jsx
│   │   ├── RecommendationCard.jsx
│   │   ├── TrendChart.jsx   # Chart.js wrapper
│   │   └── NavBar.jsx
│   └── api/                 # Axios API client
```

---

## 6. Database Schema (key tables)

```sql
users            (id, email, password_hash, name, created_at)
checkins         (id, user_id, date, sleep_hours, sleep_quality,
                  mood, energy, stress, readiness_score)
workouts         (id, user_id, date, type, duration_min, rpe)
meals            (id, user_id, date, meal_type, quality, notes)
recommendations  (id, user_id, date, message, readiness_score, model_version)
```

---

## 7. ML Component

### Phase 1 — Cold Start (< 14 days of data)
Rule-based readiness score:
```
readiness = (sleep_hours/8 * 30) + (mood/5 * 25) + (energy/5 * 25) + ((6-stress)/5 * 20)
```
Recommendation rules:
- Score ≥ 75 → High intensity workout, balanced meal focus
- Score 45–74 → Moderate workout, prioritize sleep tonight
- Score < 45 → Rest/light activity, stress management

### Phase 2 — Personalized (≥ 14 days of data)
- **Model**: Ridge Regression (per user) — predicts workout RPE from check-in features
- **Training**: Retrained weekly, stored as pickle per user
- **Insights**: Pearson correlation between check-in metrics and workout performance
- **Input features**: sleep_hours, sleep_quality, mood, energy, stress, day_of_week
- **Output**: predicted_performance score → adjusts recommendation intensity

### Why scikit-learn
- Fits well with Python backend
- Lightweight (no GPU needed)
- Interpretable — easy to explain correlations in Φ3 presentation
- Per-user models stay small (~KB each)

---

## 8. Key Screens (Φ3 mockups)

| Screen | Purpose |
|--------|---------|
| **Home / Dashboard** | Readiness score gauge + today's recommendation card + quick log buttons |
| **Daily Check-in** | 5-question form with sliders and emoji selectors |
| **Log Workout** | Type selector, duration input, RPE slider |
| **Log Meal** | Meal type (breakfast/lunch/dinner/snack), quality rating, notes |
| **Insights** | Line charts: mood over time, sleep vs. workout performance, weekly averages |
| **Profile** | Goals, stats, ML model status ("Personalized mode active") |

---

## 9. Deliverable Map

| Phase | WellSync output |
|-------|----------------|
| Φ1 | Innovation form: "AI-powered cross-domain wellness personalization" |
| Φ2 | Slides: problem, idea, competitors, methodology |
| Φ3 | This design doc + UI mockups (Figma or hand-drawn) + tech architecture diagram |
| Φ4 | Full working prototype on GitHub + Docker Compose setup + demo with sample data |

---

## 10. Team Roles (suggested)

| Role | Responsibility |
|------|---------------|
| Backend Lead | FastAPI, DB schema, auth, logging endpoints |
| ML + Insights | Readiness engine, personalization, correlation analysis |
| Frontend Lead | React UI, Chart.js graphs, API integration |

> Note: roles can overlap given a 2–3 person team.

---

## 11. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| ML needs real user data to personalize | Ship rule-based system first; ML activates after 14 days |
| Scope creep | Stick to MVP features for Φ4; defer nice-to-haves |
| Time pressure (Φ4 deadline: 25–28/5) | Start backend + DB in parallel with Φ3 design |
| Complex correlation insights | Use simple Pearson correlation, visualize clearly |
