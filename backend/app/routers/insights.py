from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
from ..database import get_db
from ..utils.auth import get_current_user
from ..models.user import User
from ..models.workout import Workout
from ..models.wellness import WellnessEntry
from ..services.ai_service import ai_service

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("/weekly-analysis")
async def get_weekly_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates an AI-driven analysis of the last 7 days of training and wellness."""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.start_date >= seven_days_ago
    ).all()
    
    wellness = db.query(WellnessEntry).filter(
        WellnessEntry.user_id == current_user.id,
        WellnessEntry.date >= seven_days_ago.date()
    ).all()
    
    if not workouts and not wellness:
        return {
            "summary": "Você ainda não tem dados suficientes esta semana para uma análise.",
            "recommendation": "Comece registrando seu primeiro treino ou entrada de bem-estar!",
            "status": "stable"
        }
    
    analysis = await ai_service.generate_weekly_analysis(workouts, wellness)
    return analysis

@router.get("/workout/{workout_id}/highlight")
async def get_workout_highlight(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates an AI highlight for a specific workout."""
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
        
    highlight = await ai_service.generate_workout_highlight(workout)
    
    # Optional: Update workout model with highlight if not already present
    # workout.ai_highlight = highlight.get("highlight")
    # workout.ai_technical_insight = highlight.get("technical_insight")
    # db.commit()
    
    return highlight
