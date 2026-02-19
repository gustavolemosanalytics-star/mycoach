import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.training_plan import SportType


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Geral
    sport: Mapped[SportType] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_format: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Tempo
    total_elapsed_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_timer_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_moving_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Distancia e velocidade
    total_distance_meters: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_pace_min_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_pace_min_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Frequencia Cardiaca
    avg_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hr_zone_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    time_in_zones_seconds: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Cadencia
    avg_cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_cadence: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Potencia (bike)
    avg_power: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_power: Mapped[int | None] = mapped_column(Integer, nullable=True)
    normalized_power: Mapped[int | None] = mapped_column(Integer, nullable=True)
    intensity_factor: Mapped[float | None] = mapped_column(Float, nullable=True)
    variability_index: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Elevacao
    total_ascent_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_descent_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Temperatura
    avg_temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Carga
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tss: Mapped[float | None] = mapped_column(Float, nullable=True)
    trimp: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_effect_aerobic: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_effect_anaerobic: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Running Dynamics (Garmin)
    avg_ground_contact_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avg_stride_length_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_vertical_oscillation_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_vertical_ratio_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_ground_contact_balance_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Swim Metrics
    avg_stroke_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_stroke_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pool_length_m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_lengths: Mapped[int | None] = mapped_column(Integer, nullable=True)
    swolf: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Sensacao do atleta
    perceived_effort: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-10 RPE
    feeling: Mapped[str | None] = mapped_column(String(20), nullable=True)
    athlete_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Streams 1Hz (para graficos)
    hr_stream: Mapped[list | None] = mapped_column(JSON, nullable=True)
    pace_stream: Mapped[list | None] = mapped_column(JSON, nullable=True)
    power_stream: Mapped[list | None] = mapped_column(JSON, nullable=True)
    cadence_stream: Mapped[list | None] = mapped_column(JSON, nullable=True)
    altitude_stream: Mapped[list | None] = mapped_column(JSON, nullable=True)
    gps_stream: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Laps
    laps_data: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Analise IA
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="activities")
    planned_session = relationship("PlannedSession", back_populates="activity", uselist=False)
