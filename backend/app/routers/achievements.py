from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.achievement import Achievement, UserAchievement
from app.schemas.achievement import (
    AchievementResponse, 
    UserAchievementResponse, 
    AchievementProgress,
    GamificationStats
)
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[AchievementResponse])
async def list_all_achievements(
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all available achievements."""
    query = db.query(Achievement).filter(Achievement.is_hidden == False)
    
    if category:
        query = query.filter(Achievement.category == category)
    
    return query.order_by(Achievement.sort_order).all()


@router.get("/me", response_model=List[UserAchievementResponse])
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's earned achievements."""
    user_achievements = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id,
        UserAchievement.progress == 100
    ).order_by(UserAchievement.earned_at.desc()).all()
    
    return user_achievements


@router.get("/me/stats", response_model=GamificationStats)
async def get_gamification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's gamification statistics."""
    # Get earned achievements
    earned = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id,
        UserAchievement.progress == 100
    ).all()
    
    # Get recent achievements (last 5)
    recent = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id,
        UserAchievement.progress == 100
    ).order_by(UserAchievement.earned_at.desc()).limit(5).all()
    
    # Get in-progress achievements
    in_progress_db = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id,
        UserAchievement.progress < 100
    ).all()
    
    in_progress = []
    for ua in in_progress_db:
        progress_data = ua.progress_data or {}
        in_progress.append(AchievementProgress(
            achievement=ua.achievement,
            current_progress=progress_data.get("current", 0),
            target=progress_data.get("target", 100),
            percentage=ua.progress,
            is_earned=False
        ))
    
    # Total achievements
    total_achievements = db.query(Achievement).filter(Achievement.is_hidden == False).count()
    
    # Calculate level progress
    points = current_user.total_points
    level = current_user.level
    points_for_current_level = (level - 1) * 500  # 500 points per level
    points_for_next_level = level * 500
    level_progress = ((points - points_for_current_level) / 500) * 100 if points >= points_for_current_level else 0
    points_to_next = points_for_next_level - points
    
    return GamificationStats(
        total_points=points,
        level=level,
        level_progress=min(level_progress, 100),
        points_to_next_level=max(0, points_to_next),
        achievements_earned=len(earned),
        achievements_total=total_achievements,
        recent_achievements=recent,
        in_progress=in_progress
    )


@router.get("/me/progress", response_model=List[AchievementProgress])
async def get_achievements_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress for all unarned achievements."""
    from app.services.gamification import calculate_all_progress
    return calculate_all_progress(current_user.id, db)
