"""
NutritionScenario model - predefined nutrition scenarios (A, B, C, D).
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, func
from app.database import Base


class NutritionScenario(Base):
    """
    Cenários de nutrição
    Predefined scenarios for different training situations.
    """
    __tablename__ = "nutrition_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    scenario_code = Column(String(10), unique=True, nullable=False)  # 'A', 'B', 'C', 'D'
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    total_calories = Column(Integer, nullable=False)
    protein_g = Column(Integer, nullable=False)
    carbs_g = Column(Integer, nullable=False)
    fat_g = Column(Integer, nullable=False)
    
    meals_json = Column(JSON, nullable=True)  # estrutura detalhada das refeições
    
    created_at = Column(DateTime, server_default=func.now())
