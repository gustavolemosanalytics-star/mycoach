"""
StravaTokens model - OAuth token storage for Strava integration.
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, func
from app.database import Base


class StravaTokens(Base):
    """
    Tokens Strava
    Stores OAuth tokens for Strava API access.
    """
    __tablename__ = "strava_tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires_at = Column(BigInteger, nullable=False)
    athlete_id = Column(BigInteger, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
