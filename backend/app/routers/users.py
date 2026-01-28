from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserStats
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return UserResponse.from_orm_with_connections(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm_with_connections(current_user)


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics."""
    from app.models.workout import Workout
    from sqlalchemy import func
    
    # Get workout stats
    stats = db.query(
        func.count(Workout.id).label('total_workouts'),
        func.sum(Workout.distance).label('total_distance'),
        func.sum(Workout.elapsed_time).label('total_time'),
        func.sum(Workout.calories).label('total_calories')
    ).filter(Workout.user_id == current_user.id).first()
    
    # Get achievements count
    from app.models.achievement import UserAchievement
    achievements_count = db.query(func.count(UserAchievement.id)).filter(
        UserAchievement.user_id == current_user.id
    ).scalar()
    
    # Calculate streaks (simplified)
    current_streak = 0  # TODO: Implement streak calculation
    best_streak = 0
    
    return UserStats(
        total_workouts=stats.total_workouts or 0,
        total_distance_km=round((stats.total_distance or 0) / 1000, 2),
        total_time_hours=round((stats.total_time or 0) / 3600, 2),
        total_calories=stats.total_calories or 0,
        current_streak=current_streak,
        best_streak=best_streak,
        achievements_count=achievements_count or 0
    )


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account."""
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}
