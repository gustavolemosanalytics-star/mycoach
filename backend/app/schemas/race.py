import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.race import RaceType, RacePriority


class RaceCreate(BaseModel):
    name: str
    race_type: RaceType
    race_date: date
    priority: RacePriority = RacePriority.A
    location: Optional[str] = None
    goal_time_seconds: Optional[int] = None
    goal_swim_seconds: Optional[int] = None
    goal_bike_seconds: Optional[int] = None
    goal_run_seconds: Optional[int] = None
    swim_distance_m: Optional[float] = None
    bike_distance_km: Optional[float] = None
    run_distance_km: Optional[float] = None
    bike_elevation_m: Optional[float] = None
    run_elevation_m: Optional[float] = None
    course_notes: Optional[str] = None


class RaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    race_type: RaceType
    race_date: date
    priority: RacePriority
    location: Optional[str] = None
    goal_time_seconds: Optional[int] = None
    goal_swim_seconds: Optional[int] = None
    goal_bike_seconds: Optional[int] = None
    goal_run_seconds: Optional[int] = None
    swim_distance_m: Optional[float] = None
    bike_distance_km: Optional[float] = None
    run_distance_km: Optional[float] = None
    bike_elevation_m: Optional[float] = None
    run_elevation_m: Optional[float] = None
    course_notes: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
