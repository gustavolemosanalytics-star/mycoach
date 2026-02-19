import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class WeeklyAnalysisResponse(BaseModel):
    id: uuid.UUID
    week_start: date
    week_end: date
    overall_score: Optional[int] = None
    summary: Optional[str] = None
    coach_message: Optional[str] = None
    planned_vs_actual: Optional[dict] = None
    total_tss: Optional[float] = None
    total_duration_seconds: Optional[int] = None
    total_distance_meters: Optional[float] = None
    sessions_completed: Optional[int] = None
    sessions_planned: Optional[int] = None
    swim_analysis: Optional[dict] = None
    bike_analysis: Optional[dict] = None
    run_analysis: Optional[dict] = None
    load_analysis: Optional[dict] = None
    highlights: Optional[list] = None
    warnings: Optional[list] = None
    improvements: Optional[list] = None
    next_week_recommendations: Optional[dict] = None
    trends: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}
