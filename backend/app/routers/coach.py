"""
Coach Router - AI chat and analysis endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, timedelta

from app.database import get_db
from app.ai.coach import ai_coach
from app.models.athlete import Athlete
from app.models.activity import Activity
from app.models.daily_metrics import DailyMetrics

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    history: Optional[List[dict]] = None


def get_athlete_data(db: Session) -> dict:
    """Get athlete data for AI context"""
    athlete = db.query(Athlete).first()
    if athlete:
        return {
            'weight_kg': athlete.weight_kg,
            'target_weight_kg': athlete.target_weight_kg,
            'ftp_watts': athlete.ftp_watts,
            'css_pace_sec': athlete.css_pace_sec,
            'run_threshold_pace_sec': athlete.run_threshold_pace_sec,
            'fc_max': athlete.fc_max
        }
    return {
        'weight_kg': 78,
        'target_weight_kg': 74,
        'ftp_watts': 200,
        'css_pace_sec': 110,
        'run_threshold_pace_sec': 300,
        'fc_max': 185
    }


def get_current_metrics(db: Session) -> dict:
    """Get current metrics for AI context"""
    # Get today's metrics
    today = db.query(DailyMetrics).filter_by(date=date.today()).first()
    
    # Get recent activities
    cutoff = date.today() - timedelta(days=7)
    activities = db.query(Activity).filter(
        Activity.activity_date >= cutoff
    ).order_by(Activity.activity_date.desc()).limit(5).all()
    
    # Calculate weekly TSS
    weekly_tss = sum(a.tss or 0 for a in activities)
    
    # Get weight
    athlete = db.query(Athlete).first()
    weight = athlete.weight_kg if athlete else None
    
    return {
        'ctl': today.ctl if today else 0,
        'atl': today.atl if today else 0,
        'tsb': today.tsb if today else 0,
        'weight': weight,
        'weekly_tss': weekly_tss,
        'recent_activities': [
            {
                'date': a.activity_date.isoformat(),
                'sport_type': a.sport_type,
                'moving_time_seconds': a.moving_time_seconds,
                'tss': a.tss
            }
            for a in activities
        ]
    }


@router.post("/chat")
async def chat_with_coach(data: ChatMessage, db: Session = Depends(get_db)):
    """Chat with AI coach"""
    athlete_data = get_athlete_data(db)
    current_metrics = get_current_metrics(db)
    
    response = await ai_coach.chat(
        user_message=data.message,
        athlete_data=athlete_data,
        current_metrics=current_metrics,
        conversation_history=data.history
    )
    
    return {
        "response": response,
        "context": {
            "ctl": current_metrics['ctl'],
            "atl": current_metrics['atl'],
            "tsb": current_metrics['tsb']
        }
    }


@router.get("/weekly-analysis")
async def get_weekly_analysis(db: Session = Depends(get_db)):
    """Get AI analysis of the current week"""
    # Get this week's data
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    activities = db.query(Activity).filter(
        Activity.activity_date >= week_start,
        Activity.activity_date <= week_end
    ).all()
    
    # Get current metrics
    metrics = db.query(DailyMetrics).filter_by(date=today).first()
    
    weekly_data = {
        'total_tss': sum(a.tss or 0 for a in activities),
        'target_tss': 400,  # Default target, could come from training plan
        'completed': len(activities),
        'planned': 6,  # Default, could come from training plan
        'compliance': (len(activities) / 6) * 100 if activities else 0,
        'ctl': metrics.ctl if metrics else 0,
        'tsb': metrics.tsb if metrics else 0,
        'sessions': [
            {
                'day': a.activity_date.strftime('%A'),
                'sport_type': a.sport_type,
                'name': a.name,
                'completed': True,
                'planned_tss': a.tss,
                'actual_tss': a.tss
            }
            for a in activities
        ]
    }
    
    analysis = await ai_coach.analyze_week(weekly_data)
    
    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "data": weekly_data,
        "analysis": analysis
    }


@router.get("/nutrition-suggestion")
async def get_nutrition_suggestion(db: Session = Depends(get_db)):
    """Get AI nutrition scenario suggestion for today"""
    athlete = db.query(Athlete).first()
    
    if not athlete:
        athlete_weight = 78
        target_weight = 74
    else:
        athlete_weight = athlete.weight_kg
        target_weight = athlete.target_weight_kg
    
    # For now, use a simple plan - could come from planned sessions
    today_plan = {
        'sport_type': 'rest',
        'session_name': 'Dia de descanso',
        'duration_min': 0,
        'target_tss': 0,
        'time': 'N/A'
    }
    
    # Check if there's an activity today
    today_activity = db.query(Activity).filter(
        Activity.activity_date == date.today()
    ).first()
    
    if today_activity:
        today_plan = {
            'sport_type': today_activity.sport_type,
            'session_name': today_activity.name,
            'duration_min': (today_activity.moving_time_seconds or 0) / 60,
            'target_tss': today_activity.tss,
            'time': '05:30'  # Assume morning
        }
    
    suggestion = await ai_coach.suggest_nutrition_scenario(
        today_plan=today_plan,
        current_weight=athlete_weight,
        target_weight=target_weight
    )
    
    return {
        "today_plan": today_plan,
        "suggestion": suggestion
    }
