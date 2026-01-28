from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WellnessEntry(Base):
    """Daily wellness/mood tracking entry."""
    __tablename__ = "wellness_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Mood & Energy (1-5 scale)
    mood = Column(Integer, nullable=True)  # 1=Very Bad, 5=Excellent
    energy_level = Column(Integer, nullable=True)  # 1=Exhausted, 5=Energized
    motivation = Column(Integer, nullable=True)  # 1=No motivation, 5=Highly motivated
    
    # Sleep tracking
    sleep_start = Column(Time, nullable=True)  # Bedtime
    sleep_end = Column(Time, nullable=True)  # Wake time
    sleep_quality = Column(Integer, nullable=True)  # 1-5 scale
    sleep_duration_minutes = Column(Integer, nullable=True)  # Calculated or manual
    
    # Physical state
    muscle_soreness = Column(Integer, nullable=True)  # 1=None, 5=Very Sore
    fatigue_level = Column(Integer, nullable=True)  # 1=Fresh, 5=Very Fatigued
    resting_heart_rate = Column(Integer, nullable=True)  # bpm
    hrv = Column(Float, nullable=True)  # Heart Rate Variability (if available)
    
    # Stress & Mental
    stress_level = Column(Integer, nullable=True)  # 1=Relaxed, 5=Very Stressed
    
    # Weight tracking
    weight = Column(Float, nullable=True)  # kg
    
    # Hydration
    water_intake = Column(Float, nullable=True)  # liters
    
    # Nutrition adherence (1-5)
    nutrition_quality = Column(Integer, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Readiness score (calculated)
    readiness_score = Column(Float, nullable=True)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wellness_entries")

    def __repr__(self):
        return f"<WellnessEntry {self.date} - User {self.user_id}>"
    
    def calculate_readiness(self) -> float:
        """Calculate readiness score based on wellness metrics."""
        scores = []
        weights = []
        
        # Sleep quality (highest weight)
        if self.sleep_quality:
            scores.append(self.sleep_quality * 20)  # Convert 1-5 to 20-100
            weights.append(0.25)
        
        # Energy level
        if self.energy_level:
            scores.append(self.energy_level * 20)
            weights.append(0.20)
        
        # Mood
        if self.mood:
            scores.append(self.mood * 20)
            weights.append(0.15)
        
        # Muscle soreness (inverse)
        if self.muscle_soreness:
            scores.append((6 - self.muscle_soreness) * 20)  # Invert scale
            weights.append(0.15)
        
        # Fatigue (inverse)
        if self.fatigue_level:
            scores.append((6 - self.fatigue_level) * 20)
            weights.append(0.15)
        
        # Stress (inverse)
        if self.stress_level:
            scores.append((6 - self.stress_level) * 20)
            weights.append(0.10)
        
        if not scores:
            return None
        
        # Weighted average
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        return round(weighted_sum / total_weight, 1)
