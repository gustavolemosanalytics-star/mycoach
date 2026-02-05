"""
Athlete model - athlete configuration and thresholds for TSS calculations.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class Athlete(Base):
    """
    Atleta (configurações e thresholds)
    Single record per user for now - can be extended to multi-user later.
    """
    __tablename__ = "athlete"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    weight_kg = Column(Float, default=78.0)
    height_cm = Column(Integer, default=171)
    
    # Thresholds para cálculo de TSS
    ftp_watts = Column(Integer, default=200)  # Functional Threshold Power (bike)
    css_pace_sec = Column(Integer, default=110)  # Critical Swim Speed (1:50/100m = 110s)
    run_threshold_pace_sec = Column(Integer, default=300)  # Pace limiar corrida (5:00/km = 300s)
    run_lthr = Column(Integer, default=165)  # Lactate Threshold Heart Rate
    fc_max = Column(Integer, default=185)
    
    # Metas
    target_weight_kg = Column(Float, default=74.0)
    tdee_kcal = Column(Integer, default=2582)
    target_deficit_pct = Column(Float, default=0.175)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
