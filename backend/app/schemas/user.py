from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str
    sport_focus: Optional[str] = "triathlon"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    sport_focus: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    sport_focus: str
    total_points: int
    level: int
    is_active: bool
    is_premium: bool
    strava_connected: bool = False
    garmin_connected: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_connections(cls, user):
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            sport_focus=user.sport_focus,
            total_points=user.total_points,
            level=user.level,
            is_active=user.is_active,
            is_premium=user.is_premium,
            strava_connected=user.strava_access_token is not None,
            garmin_connected=user.garmin_access_token is not None,
            created_at=user.created_at
        )


class UserStats(BaseModel):
    total_workouts: int
    total_distance_km: float
    total_time_hours: float
    total_calories: int
    current_streak: int
    best_streak: int
    achievements_count: int


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
