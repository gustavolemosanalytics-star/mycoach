"""Models package — 7 core models for My Coach v2"""
from app.models.user import User, SportModality, ExperienceLevel
from app.models.race import TargetRace, RaceType, RacePriority
from app.models.training_plan import (
    TrainingPlan, PlannedWeek, PlannedSession,
    PlanPhase, SportType, SessionIntensity,
)
from app.models.activity import Activity
from app.models.weekly_analysis import WeeklyAnalysis

__all__ = [
    "User", "SportModality", "ExperienceLevel",
    "TargetRace", "RaceType", "RacePriority",
    "TrainingPlan", "PlannedWeek", "PlannedSession",
    "PlanPhase", "SportType", "SessionIntensity",
    "Activity",
    "WeeklyAnalysis",
]
