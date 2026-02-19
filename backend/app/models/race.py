import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RaceType(str, enum.Enum):
    # Triathlon
    SPRINT_TRI = "sprint_tri"
    OLYMPIC_TRI = "olympic_tri"
    HALF_IRONMAN = "half_ironman"
    IRONMAN = "ironman"
    # Running
    RUN_5K = "5k"
    RUN_10K = "10k"
    RUN_HALF_MARATHON = "half_marathon"
    RUN_MARATHON = "marathon"
    RUN_ULTRA = "ultra"


class RacePriority(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class TargetRace(Base):
    __tablename__ = "target_races"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    race_type: Mapped[RaceType] = mapped_column(Enum(RaceType), nullable=False)
    race_date: Mapped[date] = mapped_column(Date, nullable=False)
    priority: Mapped[RacePriority] = mapped_column(Enum(RacePriority), default=RacePriority.A)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metas de tempo (segundos)
    goal_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goal_swim_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goal_bike_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goal_run_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Detalhes do percurso
    swim_distance_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    bike_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    run_distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    bike_elevation_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    run_elevation_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    course_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="races")
    training_plans = relationship("TrainingPlan", back_populates="race")
