"""
Activity model - activities synced from Strava with TSS calculation.
"""
from sqlalchemy import Column, Integer, BigInteger, String, Float, Date, DateTime, JSON, func
from app.database import Base


class Activity(Base):
    """
    Atividades (sincronizadas do Strava)
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    strava_id = Column(BigInteger, unique=True, nullable=True, index=True)
    sport_type = Column(String(20))  # 'swim', 'bike', 'run'
    name = Column(String(255))
    
    # Métricas básicas
    duration_seconds = Column(Integer)
    distance_meters = Column(Float)
    moving_time_seconds = Column(Integer)
    
    # Métricas de intensidade
    avg_hr = Column(Integer, nullable=True)
    max_hr = Column(Integer, nullable=True)
    avg_watts = Column(Integer, nullable=True)  # bike
    weighted_avg_watts = Column(Integer, nullable=True)  # NP (Normalized Power)
    avg_pace_sec_per_100m = Column(Integer, nullable=True)  # natação
    avg_pace_sec_per_km = Column(Integer, nullable=True)  # corrida
    
    # TSS calculado
    tss = Column(Float, nullable=True)
    intensity_factor = Column(Float, nullable=True)
    
    # Dados brutos (opcional)
    streams_json = Column(JSON, nullable=True)  # dados segundo a segundo
    
    activity_date = Column(Date, index=True)
    created_at = Column(DateTime, server_default=func.now())
