import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import SportModality, ExperienceLevel


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    modality: SportModality
    experience_level: ExperienceLevel = ExperienceLevel.INTERMEDIATE
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    hr_max: Optional[int] = None
    hr_rest: Optional[int] = None
    hr_threshold: Optional[int] = None
    ftp: Optional[int] = None
    css: Optional[float] = None
    run_threshold_pace: Optional[float] = None
    weekly_hours_available: float = 10.0
    training_days_per_week: int = 6


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    birth_date: Optional[datetime] = None
    hr_max: Optional[int] = None
    hr_rest: Optional[int] = None
    hr_threshold: Optional[int] = None
    ftp: Optional[int] = None
    css: Optional[float] = None
    run_threshold_pace: Optional[float] = None
    vo2max_estimate: Optional[float] = None
    weekly_hours_available: Optional[float] = None
    training_days_per_week: Optional[int] = None
    experience_level: Optional[ExperienceLevel] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    modality: SportModality
    experience_level: ExperienceLevel
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    birth_date: Optional[datetime] = None
    hr_max: Optional[int] = None
    hr_rest: Optional[int] = None
    hr_threshold: Optional[int] = None
    ftp: Optional[int] = None
    css: Optional[float] = None
    run_threshold_pace: Optional[float] = None
    vo2max_estimate: Optional[float] = None
    weekly_hours_available: float
    training_days_per_week: int
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    modality: SportModality


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
