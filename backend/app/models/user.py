from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for athletes."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    sport_focus = Column(String(50), default="triathlon")  # triathlon, marathon, ultra
    
    # Strava Integration
    strava_athlete_id = Column(Integer, nullable=True, unique=True)
    strava_access_token = Column(String(500), nullable=True)
    strava_refresh_token = Column(String(500), nullable=True)
    strava_token_expires_at = Column(DateTime, nullable=True)
    
    # Garmin Integration
    garmin_user_id = Column(String(255), nullable=True, unique=True)
    garmin_access_token = Column(String(500), nullable=True)
    garmin_refresh_token = Column(String(500), nullable=True)
    garmin_token_expires_at = Column(DateTime, nullable=True)
    
    # Gamification
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    timezone = Column(String(50), default="America/Sao_Paulo")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    wellness_entries = relationship("WellnessEntry", back_populates="user", cascade="all, delete-orphan")
    user_achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
