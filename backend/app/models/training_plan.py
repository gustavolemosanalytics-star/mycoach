import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PlanPhase(str, enum.Enum):
    BASE = "base"
    BUILD = "build"
    PEAK = "peak"
    TAPER = "taper"
    RECOVERY = "recovery"
    TRANSITION = "transition"


class SportType(str, enum.Enum):
    SWIM = "swim"
    BIKE = "bike"
    RUN = "run"
    STRENGTH = "strength"
    BRICK = "brick"
    REST = "rest"


class SessionIntensity(str, enum.Enum):
    RECOVERY = "recovery"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    RACE_PACE = "race_pace"


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    race_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("target_races.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Estrutura gerada pela IA
    periodization_structure: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="training_plans")
    race = relationship("TargetRace", back_populates="training_plans")
    planned_weeks = relationship("PlannedWeek", back_populates="plan", cascade="all, delete-orphan")


class PlannedWeek(Base):
    __tablename__ = "planned_weeks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_plans.id"), nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    phase: Mapped[PlanPhase] = mapped_column(Enum(PlanPhase), nullable=False)

    # Metas
    target_volume_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_tss: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_swim_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_bike_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_run_km: Mapped[float | None] = mapped_column(Float, nullable=True)

    coach_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    focus_areas: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    plan = relationship("TrainingPlan", back_populates="planned_weeks")
    planned_sessions = relationship(
        "PlannedSession", back_populates="week", cascade="all, delete-orphan"
    )


class PlannedSession(Base):
    __tablename__ = "planned_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    week_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("planned_weeks.id"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=seg, 6=dom
    sport: Mapped[SportType] = mapped_column(Enum(SportType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    intensity: Mapped[SessionIntensity] = mapped_column(Enum(SessionIntensity), nullable=False)

    # Metas
    target_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_tss: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_hr_zone: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_pace_min_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_power_watts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_swim_pace: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Estrutura detalhada
    workout_structure: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Vinculo com atividade realizada
    activity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("activities.id"), nullable=True
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    week = relationship("PlannedWeek", back_populates="planned_sessions")
    activity = relationship("Activity", back_populates="planned_session")
