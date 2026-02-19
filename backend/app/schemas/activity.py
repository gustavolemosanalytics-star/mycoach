import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.training_plan import SportType


class ActivityUploadResponse(BaseModel):
    id: uuid.UUID
    sport: SportType
    title: str
    start_time: datetime
    total_elapsed_seconds: int
    total_distance_meters: float
    avg_hr: Optional[int] = None
    max_hr: Optional[int] = None
    avg_pace_min_km: Optional[float] = None
    avg_power: Optional[int] = None
    normalized_power: Optional[int] = None
    tss: Optional[float] = None
    ai_score: Optional[int] = None
    ai_analysis: Optional[dict] = None
    source_format: Optional[str] = None

    model_config = {"from_attributes": True}


class ActivityListItem(BaseModel):
    id: uuid.UUID
    sport: SportType
    title: str
    start_time: datetime
    total_elapsed_seconds: int
    total_distance_meters: float
    avg_pace_min_km: Optional[float] = None
    avg_hr: Optional[int] = None
    tss: Optional[float] = None
    ai_score: Optional[int] = None
    feeling: Optional[str] = None

    model_config = {"from_attributes": True}


class ActivityDetail(BaseModel):
    id: uuid.UUID
    sport: SportType
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    source_format: Optional[str] = None

    total_elapsed_seconds: int
    total_timer_seconds: int
    total_moving_seconds: Optional[int] = None
    total_distance_meters: float

    avg_pace_min_km: Optional[float] = None
    max_pace_min_km: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    max_speed_kmh: Optional[float] = None

    avg_hr: Optional[int] = None
    max_hr: Optional[int] = None
    min_hr: Optional[int] = None
    hr_zone_distribution: Optional[dict] = None
    time_in_zones_seconds: Optional[dict] = None

    avg_cadence: Optional[int] = None
    max_cadence: Optional[int] = None

    avg_power: Optional[int] = None
    max_power: Optional[int] = None
    normalized_power: Optional[int] = None
    intensity_factor: Optional[float] = None
    variability_index: Optional[float] = None

    total_ascent_m: Optional[float] = None
    total_descent_m: Optional[float] = None

    avg_temperature_c: Optional[float] = None

    calories: Optional[int] = None
    tss: Optional[float] = None
    trimp: Optional[float] = None
    training_effect_aerobic: Optional[float] = None
    training_effect_anaerobic: Optional[float] = None

    avg_ground_contact_time_ms: Optional[int] = None
    avg_stride_length_m: Optional[float] = None
    avg_vertical_oscillation_mm: Optional[float] = None
    avg_vertical_ratio_pct: Optional[float] = None

    avg_stroke_rate: Optional[float] = None
    pool_length_m: Optional[int] = None
    total_lengths: Optional[int] = None
    swolf: Optional[float] = None

    perceived_effort: Optional[int] = None
    feeling: Optional[str] = None
    athlete_notes: Optional[str] = None

    hr_stream: Optional[list] = None
    pace_stream: Optional[list] = None
    power_stream: Optional[list] = None
    cadence_stream: Optional[list] = None
    altitude_stream: Optional[list] = None
    laps_data: Optional[list] = None

    ai_analysis: Optional[dict] = None
    ai_score: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
