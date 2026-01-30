from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class NutritionGoal(str, enum.Enum):
    CUTTING = "cutting"
    BULKING = "bulking"
    MAINTENANCE = "maintenance"


class NutritionProfile(Base):
    """User nutrition profile and goals."""
    __tablename__ = "nutrition_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Biometrics
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    activity_level = Column(String(50), nullable=False)  # sedentary, light, moderate, active, very_active
    
    # Goals
    goal = Column(String(20), default=NutritionGoal.MAINTENANCE)
    
    # Calculated Targets
    tdee = Column(Integer, nullable=True)
    target_calories = Column(Integer, nullable=True)
    target_protein = Column(Integer, nullable=True)  # grams
    target_carbs = Column(Integer, nullable=True)    # grams
    target_fat = Column(Integer, nullable=True)      # grams
    
    # Constraints & Preferences
    restrictions = Column(JSON, nullable=True)  # List of restrictions
    preferences = Column(JSON, nullable=True)   # List of preferences
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="nutrition_profile")


class MealLog(Base):
    """Daily food/meal logs."""
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    name = Column(String(255), nullable=False)  # Breakfast, Lunch, Post-workout Snack, etc.
    time = Column(DateTime(timezone=True), nullable=True)
    
    # Content
    foods = Column(JSON, nullable=False)  # List of food items with details
    
    # Totals for this meal
    calories = Column(Integer, default=0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    
    # Source info (AI generated vs Manual)
    is_ai_generated = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meal_logs")


class MealPlan(Base):
    """Stored meal plans (Professional vs AI)."""
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Type: 'ai' or 'pro'
    plan_type = Column(String(20), default="ai")
    
    # Full plan structure
    content = Column(JSON, nullable=False)  # Days, meals, recipes, etc.
    
    is_active = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")
