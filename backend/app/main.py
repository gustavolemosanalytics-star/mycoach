import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine, Base
import app.models  # noqa: F401 — register all models with Base.metadata

db_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_ready
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        db_ready = True
        print("DB: tables OK")
    except Exception:
        print("DB: create_all failed, trying clean slate...")
        traceback.print_exc()
        try:
            async with engine.begin() as conn:
                await conn.execute(text("DROP SCHEMA public CASCADE"))
                await conn.execute(text("CREATE SCHEMA public"))
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            db_ready = True
            print("DB: clean slate OK")
        except Exception:
            print("DB: clean slate ALSO failed, app starting without DB")
            traceback.print_exc()
    yield


app = FastAPI(
    title="MyCoach API",
    description="Treinador pessoal inteligente para triathlon e corrida",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — wide open for debugging, lock down later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"status": "healthy", "db": db_ready}


@app.get("/debug/db")
async def debug_db():
    """Temporary debug endpoint to test DB connection."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT current_database(), current_user, version()"))
            row = result.fetchone()
            tables = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            table_list = [r[0] for r in tables.fetchall()]
        return {
            "connected": True,
            "database": row[0],
            "user": row[1],
            "version": row[2],
            "tables": table_list,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
