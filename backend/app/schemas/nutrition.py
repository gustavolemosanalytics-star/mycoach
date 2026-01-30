from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class NutritionProfileBase(BaseModel):
    weight: float
    height: float
    age: int
    gender: str
    activity_level: str
    goal: str = "maintenance"
    restrictions: Optional[List[str]] = None
    preferences: Optional[List[str]] = None


class NutritionProfileCreate(NutritionProfileBase):
    pass


class NutritionProfileUpdate(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    restrictions: Optional[List[str]] = None
    preferences: Optional[List[str]] = None


class NutritionProfileResponse(NutritionProfileBase):
    id: int
    user_id: int
    tdee: Optional[int] = None
    target_calories: Optional[int] = None
    target_protein: Optional[int] = None
    target_carbs: Optional[int] = None
    target_fat: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MealItem(BaseModel):
    name: str
    amount: float
    unit: str
    calories: int
    protein: float
    carbs: float
    fat: float


class MealLogBase(BaseModel):
    name: str
    date: date
    time: Optional[datetime] = None
    foods: List[MealItem]


class MealLogCreate(BaseModel):
    name: str
    date: date
    time: Optional[datetime] = None
    foods: List[Dict[str, Any]] # Raw foods data, will be processed


class MealLogResponse(MealLogBase):
    id: int
    user_id: int
    calories: int
    protein: float
    carbs: float
    fat: float
    created_at: datetime

    class Config:
        from_attributes = True


class DailyNutritionSummary(BaseModel):
    date: date
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
    target_calories: int
    target_protein: int
    target_carbs: int
    target_fat: int
    meals: List[MealLogResponse]
