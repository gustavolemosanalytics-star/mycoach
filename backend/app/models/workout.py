from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class WorkoutSource(str, enum.Enum):
    STRAVA = "strava"
    GARMIN = "garmin"
    MANUAL = "manual"


class SportType(str, enum.Enum):
    RUN = "run"
    RIDE = "ride"
    SWIM = "swim"
    WALK = "walk"
    STRENGTH = "strength"
    YOGA = "yoga"
    OTHER = "other"


class Workout(Base):
    """Workout/Activity model."""
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Source info
    source = Column(String(20), default=WorkoutSource.MANUAL)
    external_id = Column(String(100), nullable=True, unique=True)  # Strava/Garmin activity ID
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sport_type = Column(String(50), default=SportType.RUN)
    
    # Time
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    elapsed_time = Column(Integer, nullable=False)  # seconds
    moving_time = Column(Integer, nullable=True)  # seconds
    
    # Distance & Pace
    distance = Column(Float, nullable=True)  # meters
    avg_pace = Column(Float, nullable=True)  # seconds per km
    max_pace = Column(Float, nullable=True)
    
    # Heart Rate
    avg_heart_rate = Column(Float, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    hr_zones = Column(JSON, nullable=True)  # Time in each HR zone
    
    # Power (for cycling/running with power meter)
    avg_power = Column(Float, nullable=True)  # watts
    max_power = Column(Integer, nullable=True)
    normalized_power = Column(Float, nullable=True)
    
    # Elevation
    elevation_gain = Column(Float, nullable=True)  # meters
    elevation_loss = Column(Float, nullable=True)
    max_elevation = Column(Float, nullable=True)
    min_elevation = Column(Float, nullable=True)
    
    # Calories & Energy
    calories = Column(Integer, nullable=True)
    
    # Cadence
    avg_cadence = Column(Float, nullable=True)
    max_cadence = Column(Integer, nullable=True)
    
    # Swimming specific
    pool_length = Column(Integer, nullable=True)  # meters
    total_strokes = Column(Integer, nullable=True)
    avg_stroke_rate = Column(Float, nullable=True)
    
    # Weather (if available)
    temperature = Column(Float, nullable=True)  # celsius
    humidity = Column(Float, nullable=True)  # percentage
    wind_speed = Column(Float, nullable=True)  # km/h
    
    # GPS and Sensor data streams
    polyline = Column(Text, nullable=True)  # Encoded polyline for map
    track_points = Column(JSON, nullable=True)  # List of {lat, lng, alt, heart_rate, cadence, time}
    start_lat = Column(Float, nullable=True)
    start_lng = Column(Float, nullable=True)
    
    # Splits/Laps data
    splits = Column(JSON, nullable=True)  # Array of split data
    laps = Column(JSON, nullable=True)  # Array of lap data
    
    # AI-generated highlights and analysis
    highlights = Column(JSON, nullable=True)  # Auto-generated insights
    training_load = Column(Float, nullable=True)  # TSS or equivalent
    
    # Personal Records achieved in this workout
    personal_records = Column(JSON, nullable=True)
    
    # Raw data from source (for debugging/reprocessing)
    raw_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workouts")

    def __repr__(self):
        return f"<Workout {self.name} - {self.sport_type}>"
    
    @property
    def duration_formatted(self) -> str:
        """Return formatted duration string."""
        hours = self.elapsed_time // 3600
        minutes = (self.elapsed_time % 3600) // 60
        seconds = self.elapsed_time % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    @property
    def distance_km(self) -> float:
        """Return distance in kilometers."""
        return round(self.distance / 1000, 2) if self.distance else 0
    
    @property
    def pace_formatted(self) -> str:
        """Return formatted pace string (min/km)."""
        if not self.avg_pace:
            return "--:--"
        minutes = int(self.avg_pace // 60)
        seconds = int(self.avg_pace % 60)
        return f"{minutes}:{seconds:02d}"
