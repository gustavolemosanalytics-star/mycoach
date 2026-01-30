from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/performance-load")
async def get_performance_load(
    days: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate Training Load metrics (CTL/ATL/TSB approximation)."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.start_date >= start_date
    ).order_by(Workout.start_date).all()
    
    # We'll use a simplified model based on duration and intensity (or just duration if no HR)
    # CTL (Chronic Training Load) - 42 day moving average
    # ATL (Acute Training Load) - 7 day moving average
    
    history = []
    current_atl = 0.0
    current_ctl = 0.0
    
    # Alpha for exponentially weighted moving average
    atl_days = 7
    ctl_days = 42
    
    # Process day by day to build the curve
    date_map = {}
    for w in workouts:
        d = w.start_date.date()
        # Simple TSS estimation: (duration in min * intensity_factor)
        # For now, let's use: duration_min * (avg_hr / max_hr_estimate)
        intensity = (w.avg_heart_rate / 180) if w.avg_heart_rate else 0.7
        tss = (w.elapsed_time / 60) * intensity
        date_map[d] = date_map.get(d, 0) + tss

    # Generate daily points
    curr = start_date.date()
    today = datetime.utcnow().date()
    
    while curr <= today:
        daily_tss = date_map.get(curr, 0)
        
        # CTL = CTL_prev + (TSS - CTL_prev)/42
        current_ctl = current_ctl + (daily_tss - current_ctl) / ctl_days
        # ATL = ATL_prev + (TSS - ATL_prev)/7
        current_atl = current_atl + (daily_tss - current_atl) / atl_days
        
        history.append({
            "date": curr.isoformat(),
            "ctl": round(current_ctl, 1),
            "atl": round(current_atl, 1),
            "tsb": round(current_ctl - current_atl, 1),
            "tss": round(daily_tss, 1)
        })
        curr += timedelta(days=1)

    return history

@router.get("/hr-zones-distribution")
async def get_hr_zones_distribution(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Summarize time spent in HR zones across all workouts."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.start_date >= start_date,
        Workout.hr_zones.isnot(None)
    ).all()
    
    total_zones = [0, 0, 0, 0, 0] # Z1 to Z5
    for w in workouts:
        if w.hr_zones:
            for i in range(5):
                total_zones[i] += w.hr_zones.get(f"z{i+1}", 0)
                
    return [
        {"zone": "Z1 (Recuperação)", "value": total_zones[0]},
        {"zone": "Z2 (Aeróbico)", "value": total_zones[1]},
        {"zone": "Z3 (Tempo)", "value": total_zones[2]},
        {"zone": "Z4 (Limiar)", "value": total_zones[3]},
        {"zone": "Z5 (Anaeróbico)", "value": total_zones[4]},
    ]
