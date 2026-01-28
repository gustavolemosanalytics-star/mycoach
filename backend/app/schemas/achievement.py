from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class AchievementResponse(BaseModel):
    id: int
    code: str
    title: str
    description: str
    icon: str
    category: str
    tier: str
    points: int
    is_hidden: bool

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    id: int
    achievement: AchievementResponse
    earned_at: datetime
    progress: int
    progress_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AchievementProgress(BaseModel):
    """Progress towards an achievement."""
    achievement: AchievementResponse
    current_progress: int
    target: int
    percentage: float
    is_earned: bool


class GamificationStats(BaseModel):
    """User's gamification statistics."""
    total_points: int
    level: int
    level_progress: float  # 0-100 progress to next level
    points_to_next_level: int
    achievements_earned: int
    achievements_total: int
    recent_achievements: List[UserAchievementResponse]
    in_progress: List[AchievementProgress]
