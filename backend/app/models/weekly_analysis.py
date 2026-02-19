import uuid
from datetime import date, datetime

from sqlalchemy import Integer, Float, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class WeeklyAnalysis(Base):
    __tablename__ = "weekly_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    week_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("planned_weeks.id"), nullable=True
    )
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    week_end: Mapped[date] = mapped_column(Date, nullable=False)

    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    coach_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Planejado vs Realizado
    planned_vs_actual: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Metricas agregadas
    total_tss: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_distance_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sessions_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sessions_planned: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Analise por modalidade
    swim_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    bike_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    run_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Carga e fadiga
    load_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Insights
    highlights: Mapped[list | None] = mapped_column(JSON, nullable=True)
    warnings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    improvements: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Recomendacoes para proxima semana
    next_week_recommendations: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Tendencias
    trends: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="weekly_analyses")
    week = relationship("PlannedWeek")
