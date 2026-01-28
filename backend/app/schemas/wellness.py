from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime


class WellnessBase(BaseModel):
    date: date
    
    # Mood & Energy (1-5)
    mood: Optional[int] = Field(None, ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    motivation: Optional[int] = Field(None, ge=1, le=5)
    
    # Sleep
    sleep_start: Optional[time] = None
    sleep_end: Optional[time] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    
    # Physical state
    muscle_soreness: Optional[int] = Field(None, ge=1, le=5)
    fatigue_level: Optional[int] = Field(None, ge=1, le=5)
    resting_heart_rate: Optional[int] = None
    
    # Stress
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    
    # Weight & Nutrition
    weight: Optional[float] = None
    water_intake: Optional[float] = None
    nutrition_quality: Optional[int] = Field(None, ge=1, le=5)
    
    # Notes
    notes: Optional[str] = None


class WellnessCreate(WellnessBase):
    pass


class WellnessUpdate(BaseModel):
    mood: Optional[int] = Field(None, ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    motivation: Optional[int] = Field(None, ge=1, le=5)
    sleep_start: Optional[time] = None
    sleep_end: Optional[time] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    muscle_soreness: Optional[int] = Field(None, ge=1, le=5)
    fatigue_level: Optional[int] = Field(None, ge=1, le=5)
    resting_heart_rate: Optional[int] = None
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    weight: Optional[float] = None
    water_intake: Optional[float] = None
    nutrition_quality: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class WellnessResponse(WellnessBase):
    id: int
    user_id: int
    sleep_duration_minutes: Optional[int] = None
    readiness_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WellnessTrend(BaseModel):
    """Wellness trends over time."""
    period_days: int
    avg_mood: Optional[float] = None
    avg_energy: Optional[float] = None
    avg_sleep_hours: Optional[float] = None
    avg_readiness: Optional[float] = None
    trend_direction: str = "stable"  # improving, declining, stable
