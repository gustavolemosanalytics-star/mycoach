import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import engine, Base
import app.models  # noqa: F401 — register all models with Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB: tables OK")
    yield


app = FastAPI(
    title="MyCoach API",
    description="Treinador pessoal inteligente para triathlon e corrida",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions so CORS headers are still present and error details are visible."""
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    print(f"UNHANDLED ERROR on {request.method} {request.url.path}:")
    print("".join(tb))
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url.path),
        },
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


@app.get("/debug/check")
async def debug_check():
    """Temporary debug endpoint — remove after deploy is confirmed working."""
    import sys
    checks = {"python": sys.version}

    # Test bcrypt/passlib
    try:
        from app.core.security import get_password_hash, verify_password
        hashed = get_password_hash("test123")
        ok = verify_password("test123", hashed)
        checks["bcrypt"] = {"ok": ok, "hash_prefix": hashed[:10]}
    except Exception as e:
        checks["bcrypt"] = {"error": str(e), "type": type(e).__name__}

    # Test DB
    try:
        from app.db.session import async_session
        from sqlalchemy import text
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            checks["db"] = {"ok": True}
    except Exception as e:
        checks["db"] = {"error": str(e), "type": type(e).__name__}

    # Test JWT
    try:
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": "test"})
        checks["jwt"] = {"ok": True, "token_prefix": token[:20]}
    except Exception as e:
        checks["jwt"] = {"error": str(e), "type": type(e).__name__}

    return checks
