from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.routers import (
    auth, users, workouts, wellness, achievements, integrations, 
    insights, nutrition, analytics, groups, strava, activities, metrics, athlete, coach
)

settings = get_settings()

app = FastAPI(
    title="MyCoach API",
    description="API para plataforma de coaching de triatletas e maratonistas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["Workouts"])
app.include_router(wellness.router, prefix="/api/wellness", tags=["Wellness"])
app.include_router(achievements.router, prefix="/api/achievements", tags=["Achievements"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(insights.router, prefix="/api/insights", tags=["AI Insights"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])

# New routers per specification
app.include_router(strava.router, prefix="/api/strava", tags=["Strava"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(athlete.router, prefix="/api/athlete", tags=["Athlete"])
app.include_router(coach.router, prefix="/api/coach", tags=["Coach"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to MyCoach API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy"}
