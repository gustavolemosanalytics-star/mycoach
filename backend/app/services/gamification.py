from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import List, Optional
from app.models.user import User
from app.models.workout import Workout
from app.models.wellness import WellnessEntry
from app.models.achievement import Achievement, UserAchievement, DEFAULT_ACHIEVEMENTS
from app.schemas.achievement import AchievementProgress


def seed_achievements(db: Session):
    """Seed default achievements if they don't exist."""
    for ach_data in DEFAULT_ACHIEVEMENTS:
        existing = db.query(Achievement).filter(Achievement.code == ach_data["code"]).first()
        if not existing:
            achievement = Achievement(**ach_data)
            db.add(achievement)
    db.commit()


def check_achievements(user_id: int, db: Session, workout: Optional[Workout] = None):
    """Check and award achievements after a workout."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
    
    # Ensure achievements are seeded
    if db.query(Achievement).count() == 0:
        seed_achievements(db)
    
    achievements = db.query(Achievement).all()
    
    for achievement in achievements:
        # Skip if already earned
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id,
            UserAchievement.progress == 100
        ).first()
        
        if existing:
            continue
        
        # Check requirements
        earned, progress, progress_data = check_requirement(user_id, db, achievement, workout)
        
        if earned:
            award_achievement(user_id, achievement.id, db, progress_data)
        elif progress > 0:
            update_progress(user_id, achievement.id, db, progress, progress_data)


def check_requirement(user_id: int, db: Session, achievement: Achievement, workout: Optional[Workout]) -> tuple:
    """Check if user meets achievement requirements. Returns (earned, progress%, progress_data)."""
    req = achievement.requirements or {}
    req_type = req.get("type")
    
    if req_type == "workout_count":
        target = req.get("count", 1)
        count = db.query(func.count(Workout.id)).filter(Workout.user_id == user_id).scalar()
        progress = min(100, int((count / target) * 100))
        return count >= target, progress, {"current": count, "target": target}
    
    elif req_type == "weekly_workouts":
        target = req.get("count", 5)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        count = db.query(func.count(Workout.id)).filter(
            Workout.user_id == user_id,
            Workout.start_date >= datetime.combine(week_start, datetime.min.time())
        ).scalar()
        progress = min(100, int((count / target) * 100))
        return count >= target, progress, {"current": count, "target": target}
    
    elif req_type == "tri_week":
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        sports = db.query(Workout.sport_type).filter(
            Workout.user_id == user_id,
            Workout.start_date >= datetime.combine(week_start, datetime.min.time())
        ).distinct().all()
        sport_set = {s[0] for s in sports}
        required = {"swim", "ride", "run"}
        completed = sport_set & required
        progress = min(100, int((len(completed) / 3) * 100))
        return required.issubset(sport_set), progress, {"completed": list(completed), "target": list(required)}
    
    elif req_type == "streak":
        target_days = req.get("days", 30)
        streak = calculate_streak(user_id, db)
        progress = min(100, int((streak / target_days) * 100))
        return streak >= target_days, progress, {"current": streak, "target": target_days}
    
    elif req_type == "single_distance":
        target_km = req.get("km", 42.195)
        sport = req.get("sport", "run")
        if workout and workout.sport_type == sport and workout.distance:
            km = workout.distance / 1000
            if km >= target_km:
                return True, 100, {"distance_km": km}
        return False, 0, {}
    
    elif req_type == "total_distance":
        target_km = req.get("km", 1000)
        sport = req.get("sport")
        query = db.query(func.sum(Workout.distance)).filter(Workout.user_id == user_id)
        if sport:
            query = query.filter(Workout.sport_type == sport)
        total = query.scalar() or 0
        total_km = total / 1000
        progress = min(100, int((total_km / target_km) * 100))
        return total_km >= target_km, progress, {"current_km": total_km, "target_km": target_km}
    
    elif req_type == "early_workouts":
        target = req.get("count", 10)
        before_hour = req.get("before_hour", 7)
        count = db.query(func.count(Workout.id)).filter(
            Workout.user_id == user_id,
            func.extract('hour', Workout.start_date) < before_hour
        ).scalar()
        progress = min(100, int((count / target) * 100))
        return count >= target, progress, {"current": count, "target": target}
    
    elif req_type == "late_workouts":
        target = req.get("count", 10)
        after_hour = req.get("after_hour", 20)
        count = db.query(func.count(Workout.id)).filter(
            Workout.user_id == user_id,
            func.extract('hour', Workout.start_date) >= after_hour
        ).scalar()
        progress = min(100, int((count / target) * 100))
        return count >= target, progress, {"current": count, "target": target}
    
    elif req_type == "personal_record" and workout:
        # Check if this workout has any PRs
        if workout.personal_records and len(workout.personal_records) > 0:
            return True, 100, {"records": workout.personal_records}
        return False, 0, {}
    
    elif req_type == "wellness_streak":
        target_days = req.get("days", 7)
        streak = calculate_wellness_streak(user_id, db)
        progress = min(100, int((streak / target_days) * 100))
        return streak >= target_days, progress, {"current": streak, "target": target_days}
    
    elif req_type == "sleep_hours":
        target_hours = req.get("hours", 8)
        target_days = req.get("days", 7)
        # Check last N days
        start_date = date.today() - timedelta(days=target_days)
        entries = db.query(WellnessEntry).filter(
            WellnessEntry.user_id == user_id,
            WellnessEntry.date >= start_date,
            WellnessEntry.sleep_duration_minutes >= target_hours * 60
        ).count()
        progress = min(100, int((entries / target_days) * 100))
        return entries >= target_days, progress, {"current": entries, "target": target_days}
    
    return False, 0, {}


def calculate_streak(user_id: int, db: Session) -> int:
    """Calculate current workout streak in days."""
    today = date.today()
    streak = 0
    current_date = today
    
    while True:
        has_workout = db.query(Workout).filter(
            Workout.user_id == user_id,
            func.date(Workout.start_date) == current_date
        ).first()
        
        if has_workout:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def calculate_wellness_streak(user_id: int, db: Session) -> int:
    """Calculate consecutive days with wellness entries."""
    today = date.today()
    streak = 0
    current_date = today
    
    while True:
        has_entry = db.query(WellnessEntry).filter(
            WellnessEntry.user_id == user_id,
            WellnessEntry.date == current_date
        ).first()
        
        if has_entry:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def award_achievement(user_id: int, achievement_id: int, db: Session, context: dict = None):
    """Award an achievement to a user."""
    user = db.query(User).filter(User.id == user_id).first()
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    
    if not user or not achievement:
        return
    
    # Create user achievement
    user_achievement = UserAchievement(
        user_id=user_id,
        achievement_id=achievement_id,
        progress=100,
        progress_data=context,
        context=context
    )
    db.add(user_achievement)
    
    # Award points
    user.total_points += achievement.points
    
    # Update level (500 points per level)
    user.level = (user.total_points // 500) + 1
    
    db.commit()


def update_progress(user_id: int, achievement_id: int, db: Session, progress: int, progress_data: dict):
    """Update progress towards an achievement."""
    existing = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.achievement_id == achievement_id
    ).first()
    
    if existing:
        existing.progress = progress
        existing.progress_data = progress_data
    else:
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            progress=progress,
            progress_data=progress_data
        )
        db.add(user_achievement)
    
    db.commit()


def check_wellness_achievements(user_id: int, db: Session):
    """Check wellness-related achievements."""
    check_achievements(user_id, db, None)


def calculate_all_progress(user_id: int, db: Session) -> List[AchievementProgress]:
    """Calculate progress for all unearned achievements."""
    # Ensure achievements are seeded
    if db.query(Achievement).count() == 0:
        seed_achievements(db)
    
    achievements = db.query(Achievement).filter(Achievement.is_hidden == False).all()
    progress_list = []
    
    for achievement in achievements:
        # Check if already earned
        earned = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id,
            UserAchievement.progress == 100
        ).first()
        
        if earned:
            continue
        
        is_earned, progress, progress_data = check_requirement(user_id, db, achievement, None)
        
        if progress > 0:
            progress_list.append(AchievementProgress(
                achievement=achievement,
                current_progress=progress_data.get("current", 0),
                target=progress_data.get("target", 100),
                percentage=progress,
                is_earned=is_earned
            ))
    
    return sorted(progress_list, key=lambda x: x.percentage, reverse=True)
