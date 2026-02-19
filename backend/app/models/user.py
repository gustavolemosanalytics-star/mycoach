import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SportModality(str, enum.Enum):
    TRIATHLON = "triathlon"
    RUNNING = "running"


class ExperienceLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Modalidade e experiencia
    modality: Mapped[SportModality] = mapped_column(Enum(SportModality), nullable=False)
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel), default=ExperienceLevel.INTERMEDIATE
    )

    # Dados fisicos
    birth_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Metricas fisiologicas
    hr_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hr_rest: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hr_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ftp: Mapped[int | None] = mapped_column(Integer, nullable=True)  # bike watts - triathlon only
    css: Mapped[float | None] = mapped_column(Float, nullable=True)  # min/100m - triathlon only
    run_threshold_pace: Mapped[float | None] = mapped_column(Float, nullable=True)  # sec/km
    vo2max_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Disponibilidade
    weekly_hours_available: Mapped[float] = mapped_column(Float, default=10.0)
    training_days_per_week: Mapped[int] = mapped_column(Integer, default=6)

    # Relationships
    races = relationship("TargetRace", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    training_plans = relationship("TrainingPlan", back_populates="user", cascade="all, delete-orphan")
    weekly_analyses = relationship("WeeklyAnalysis", back_populates="user", cascade="all, delete-orphan")
