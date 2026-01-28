from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class WorkoutBase(BaseModel):
    name: str
    sport_type: str = "run"
    start_date: datetime
    elapsed_time: int  # seconds
    description: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    distance: Optional[float] = None  # meters
    avg_heart_rate: Optional[float] = None
    max_heart_rate: Optional[int] = None
    avg_pace: Optional[float] = None
    calories: Optional[int] = None
    elevation_gain: Optional[float] = None
    avg_cadence: Optional[float] = None
    avg_power: Optional[float] = None


class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sport_type: Optional[str] = None


class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    source: str
    external_id: Optional[str] = None
    
    # Metrics
    distance: Optional[float] = None
    distance_km: float = 0
    moving_time: Optional[int] = None
    avg_pace: Optional[float] = None
    pace_formatted: str = "--:--"
    duration_formatted: str = "0:00"
    
    # Heart Rate
    avg_heart_rate: Optional[float] = None
    max_heart_rate: Optional[int] = None
    hr_zones: Optional[Dict[str, Any]] = None
    
    # Power
    avg_power: Optional[float] = None
    max_power: Optional[int] = None
    normalized_power: Optional[float] = None
    
    # Elevation
    elevation_gain: Optional[float] = None
    elevation_loss: Optional[float] = None
    
    # Energy
    calories: Optional[int] = None
    
    # Cadence
    avg_cadence: Optional[float] = None
    
    # GPS
    polyline: Optional[str] = None
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    
    # Analysis
    highlights: Optional[List[Dict[str, Any]]] = None
    training_load: Optional[float] = None
    personal_records: Optional[List[Dict[str, Any]]] = None
    
    # Splits
    splits: Optional[List[Dict[str, Any]]] = None
    
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutListResponse(BaseModel):
    workouts: List[WorkoutResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


class WorkoutSummary(BaseModel):
    """Summary statistics for a period."""
    total_workouts: int
    total_distance_km: float
    total_time_minutes: int
    total_calories: int
    avg_pace: Optional[float] = None
    avg_heart_rate: Optional[float] = None
    by_sport: Dict[str, Dict[str, float]]


class WeeklyStats(BaseModel):
    week_start: datetime
    week_end: datetime
    summary: WorkoutSummary
    workouts: List[WorkoutResponse]
    comparison_to_last_week: Optional[Dict[str, float]] = None
