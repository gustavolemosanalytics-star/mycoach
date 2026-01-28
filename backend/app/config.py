from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    app_name: str = "MyCoach API"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://localhost:5432/mycoach"
    
    # JWT Authentication
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Strava API
    strava_client_id: Optional[str] = None
    strava_client_secret: Optional[str] = None
    strava_redirect_uri: str = "http://localhost:8000/api/integrations/strava/callback"
    
    # Garmin API
    garmin_client_id: Optional[str] = None
    garmin_client_secret: Optional[str] = None
    garmin_redirect_uri: str = "http://localhost:8000/api/integrations/garmin/callback"
    
    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:5173"
    
    # AI (OpenAI)
    openai_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
