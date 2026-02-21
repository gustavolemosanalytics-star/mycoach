from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine, Base
import app.models  # noqa: F401 — register all models with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try create_all first; if it fails (old schema conflict), nuke and retry
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables OK")
    except Exception as e:
        print(f"create_all failed ({e}), dropping old schema and retrying...")
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created (clean slate)")
    yield


app = FastAPI(
    title="MyCoach API",
    description="Treinador pessoal inteligente para triathlon e corrida",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for now, lock down later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from app.api.routes import auth, profile, activities, plans  # noqa: E402

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(activities.router, prefix="/api/v1/activities", tags=["Activities"])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["Plans"])


@app.get("/")
async def root():
    return {"message": "MyCoach API v2.0", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
