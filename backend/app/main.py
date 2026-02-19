from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="MyCoach API",
    description="Treinador pessoal inteligente para triathlon e corrida",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
]
# Allow any Railway-generated domain
if settings.APP_ENV == "production":
    origins.append("https://*.up.railway.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.up\.railway\.app",
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
