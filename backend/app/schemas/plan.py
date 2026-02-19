import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.training_plan import PlanPhase, SportType, SessionIntensity


class GeneratePlanRequest(BaseModel):
    race_id: uuid.UUID
    start_date: Optional[date] = None


class GenerateWeekRequest(BaseModel):
    pass  # Uses path param week_id


class PlannedSessionResponse(BaseModel):
    id: uuid.UUID
    day_of_week: int
    sport: SportType
    title: str
    description: Optional[str] = None
    intensity: SessionIntensity
    target_duration_minutes: Optional[int] = None
    target_distance_meters: Optional[float] = None
    target_tss: Optional[float] = None
    target_hr_zone: Optional[int] = None
    target_pace_min_km: Optional[float] = None
    target_power_watts: Optional[int] = None
    target_swim_pace: Optional[float] = None
    workout_structure: Optional[dict] = None
    activity_id: Optional[uuid.UUID] = None
    is_completed: bool

    model_config = {"from_attributes": True}


class PlannedWeekResponse(BaseModel):
    id: uuid.UUID
    week_number: int
    start_date: date
    end_date: date
    phase: PlanPhase
    target_volume_hours: Optional[float] = None
    target_tss: Optional[float] = None
    target_swim_meters: Optional[float] = None
    target_bike_km: Optional[float] = None
    target_run_km: Optional[float] = None
    coach_notes: Optional[str] = None
    focus_areas: Optional[dict] = None
    planned_sessions: list[PlannedSessionResponse] = []

    model_config = {"from_attributes": True}


class TrainingPlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    total_weeks: int
    is_active: bool
    periodization_structure: Optional[dict] = None
    planned_weeks: list[PlannedWeekResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class TrainingPlanListItem(BaseModel):
    id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    total_weeks: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CurrentWeekResponse(BaseModel):
    week: Optional[PlannedWeekResponse] = None
    plan_name: Optional[str] = None
    race_name: Optional[str] = None
    race_date: Optional[date] = None
