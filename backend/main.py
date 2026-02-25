from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.morning_agent import MorningRecommendationAgent
from backend.agents.evening_agent import EveningInsightsAgent
from backend.agents.retraining_agent import ModelRetrainingAgent
from backend.create_tables import create_all_tables
from backend.events.event_types import EventType
from backend.events.gateway import EventGateway
from backend.routers import auth, checkin, logs, recommendations, insights
from backend.scheduler import build_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_all_tables()

    gateway = EventGateway()
    morning_agent = MorningRecommendationAgent()
    evening_agent = EveningInsightsAgent()
    retraining_agent = ModelRetrainingAgent()

    gateway.register(EventType.MORNING_RECOMMENDATION, morning_agent.handle)
    gateway.register(EventType.EVENING_SUMMARY, evening_agent.handle)
    gateway.register(EventType.MODEL_RETRAINING, retraining_agent.handle)

    scheduler = build_scheduler(gateway)
    scheduler.start()
    app.state.scheduler = scheduler
    app.state.gateway = gateway

    yield

    # Shutdown
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="WellSync API",
    description="AI Holistic Wellness Coach",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(checkin.router, prefix="/checkin", tags=["checkin"])
app.include_router(logs.router, tags=["logs"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])


@app.get("/health")
def health():
    return {"status": "ok"}
