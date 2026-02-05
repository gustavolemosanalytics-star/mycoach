"""
DailyMetrics model - CTL, ATL, TSB tracking and daily nutrition.
"""
from sqlalchemy import Column, Integer, Float, Date, DateTime, func
from app.database import Base


class DailyMetrics(Base):
    """
    Métricas diárias (CTL, ATL, TSB)
    One record per day containing training load and nutrition data.
    """
    __tablename__ = "daily_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    
    # TSS do dia (soma de todas atividades)
    daily_tss = Column(Float, default=0)
    
    # Performance Management Chart
    ctl = Column(Float, nullable=True)  # Chronic Training Load (fitness)
    atl = Column(Float, nullable=True)  # Acute Training Load (fatigue)
    tsb = Column(Float, nullable=True)  # Training Stress Balance (form)
    
    # Nutrição do dia
    calories_consumed = Column(Integer, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    
    # Peso
    weight_kg = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
