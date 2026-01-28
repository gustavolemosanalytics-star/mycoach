from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Achievement(Base):
    """Achievement definitions (badges)."""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # e.g., "first_workout", "week_warrior"
    
    # Display info
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="🏆")  # Emoji or icon name
    
    # Categorization
    category = Column(String(50), default="general")  # general, streak, distance, speed, triathlon
    tier = Column(String(20), default="bronze")  # bronze, silver, gold, platinum
    
    # Points awarded
    points = Column(Integer, default=10)
    
    # Requirements (stored as JSON for flexibility)
    requirements = Column(JSON, nullable=True)
    # Example: {"type": "streak", "days": 30} or {"type": "distance", "km": 1000, "sport": "run"}
    
    # Display order
    sort_order = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)  # Secret achievements
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")

    def __repr__(self):
        return f"<Achievement {self.code}: {self.title}>"


class UserAchievement(Base):
    """User's earned achievements."""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    
    # When earned
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Progress (for achievements that can be partially completed)
    progress = Column(Integer, default=100)  # 0-100 percentage
    progress_data = Column(JSON, nullable=True)  # {"current": 15, "target": 30}
    
    # Context of achievement (e.g., which workout triggered it)
    context = Column(JSON, nullable=True)
    
    # Notification sent
    notified = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    def __repr__(self):
        return f"<UserAchievement User {self.user_id} - Achievement {self.achievement_id}>"


# Default achievements to seed
DEFAULT_ACHIEVEMENTS = [
    {
        "code": "first_workout",
        "title": "First Steps",
        "description": "Complete your first workout",
        "icon": "🏃",
        "category": "general",
        "tier": "bronze",
        "points": 10,
        "requirements": {"type": "workout_count", "count": 1}
    },
    {
        "code": "week_warrior",
        "title": "Week Warrior",
        "description": "Complete 5 workouts in a single week",
        "icon": "🔥",
        "category": "streak",
        "tier": "silver",
        "points": 50,
        "requirements": {"type": "weekly_workouts", "count": 5}
    },
    {
        "code": "triathlete",
        "title": "Triathlete",
        "description": "Complete swim, bike, and run workouts in the same week",
        "icon": "🏊",
        "category": "triathlon",
        "tier": "gold",
        "points": 100,
        "requirements": {"type": "tri_week", "sports": ["swim", "ride", "run"]}
    },
    {
        "code": "consistency_30",
        "title": "Consistency King",
        "description": "Maintain a 30-day workout streak",
        "icon": "👑",
        "category": "streak",
        "tier": "gold",
        "points": 500,
        "requirements": {"type": "streak", "days": 30}
    },
    {
        "code": "iron_distance",
        "title": "Iron Will",
        "description": "Complete an Ironman-distance triathlon (3.8km swim, 180km bike, 42.2km run)",
        "icon": "🦾",
        "category": "triathlon",
        "tier": "platinum",
        "points": 1000,
        "requirements": {"type": "iron_distance"}
    },
    {
        "code": "speed_demon",
        "title": "Speed Demon",
        "description": "Set a new personal record",
        "icon": "⚡",
        "category": "speed",
        "tier": "silver",
        "points": 75,
        "requirements": {"type": "personal_record"}
    },
    {
        "code": "early_bird",
        "title": "Early Bird",
        "description": "Complete 10 workouts before 7 AM",
        "icon": "🌅",
        "category": "general",
        "tier": "silver",
        "points": 50,
        "requirements": {"type": "early_workouts", "count": 10, "before_hour": 7}
    },
    {
        "code": "night_owl",
        "title": "Night Owl",
        "description": "Complete 10 workouts after 8 PM",
        "icon": "🌙",
        "category": "general",
        "tier": "silver",
        "points": 50,
        "requirements": {"type": "late_workouts", "count": 10, "after_hour": 20}
    },
    {
        "code": "centurion",
        "title": "Centurion",
        "description": "Complete 100 total workouts",
        "icon": "💯",
        "category": "general",
        "tier": "gold",
        "points": 200,
        "requirements": {"type": "workout_count", "count": 100}
    },
    {
        "code": "marathon_finisher",
        "title": "Marathon Finisher",
        "description": "Complete a marathon (42.195 km run)",
        "icon": "🏅",
        "category": "distance",
        "tier": "gold",
        "points": 300,
        "requirements": {"type": "single_distance", "km": 42.195, "sport": "run"}
    },
    {
        "code": "half_marathon",
        "title": "Half Marathon Hero",
        "description": "Complete a half marathon (21.1 km run)",
        "icon": "🎖️",
        "category": "distance",
        "tier": "silver",
        "points": 150,
        "requirements": {"type": "single_distance", "km": 21.1, "sport": "run"}
    },
    {
        "code": "1000km_run",
        "title": "1000K Club",
        "description": "Run a total of 1000 kilometers",
        "icon": "🛤️",
        "category": "distance",
        "tier": "platinum",
        "points": 500,
        "requirements": {"type": "total_distance", "km": 1000, "sport": "run"}
    },
    {
        "code": "wellness_streak_7",
        "title": "Self-Aware",
        "description": "Log wellness data for 7 consecutive days",
        "icon": "🧘",
        "category": "wellness",
        "tier": "bronze",
        "points": 30,
        "requirements": {"type": "wellness_streak", "days": 7}
    },
    {
        "code": "perfect_sleep",
        "title": "Sleep Champion",
        "description": "Log 8+ hours of sleep for 7 consecutive days",
        "icon": "😴",
        "category": "wellness",
        "tier": "silver",
        "points": 75,
        "requirements": {"type": "sleep_hours", "hours": 8, "days": 7}
    }
]
