"""
TrainingPlan and PlannedSession models - training plan structure.
"""
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class TrainingPlan(Base):
    """
    Plano de treino (semanas/fases)
    """
    __tablename__ = "training_plan"

    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer, nullable=False)
    phase = Column(String(20))  # 'BASE', 'BUILD', 'PEAK', 'TAPER', 'RACE'
    
    target_tss = Column(Integer, nullable=True)
    target_ctl = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    sessions = relationship("PlannedSession", back_populates="plan", cascade="all, delete-orphan")


class PlannedSession(Base):
    """
    Sessões planejadas dentro de um plano de treino.
    """
    __tablename__ = "planned_sessions"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("training_plan.id"), nullable=False)
    
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    sport_type = Column(String(20))
    session_name = Column(String(100))
    description = Column(Text, nullable=True)
    
    duration_minutes = Column(Integer, nullable=True)
    target_tss = Column(Integer, nullable=True)
    target_zone = Column(String(10), nullable=True)  # 'Z2', 'Z3', 'Z4', etc.
    
    completed = Column(Boolean, default=False)
    actual_activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    
    plan = relationship("TrainingPlan", back_populates="sessions")
