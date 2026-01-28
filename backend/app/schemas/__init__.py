"""Schemas package"""
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token, TokenData
from app.schemas.workout import WorkoutCreate, WorkoutResponse, WorkoutUpdate, WorkoutListResponse
from app.schemas.wellness import WellnessCreate, WellnessResponse, WellnessUpdate
from app.schemas.achievement import AchievementResponse, UserAchievementResponse

__all__ = [
    "UserCreate", "UserResponse", "UserUpdate", "Token", "TokenData",
    "WorkoutCreate", "WorkoutResponse", "WorkoutUpdate", "WorkoutListResponse",
    "WellnessCreate", "WellnessResponse", "WellnessUpdate",
    "AchievementResponse", "UserAchievementResponse"
]
