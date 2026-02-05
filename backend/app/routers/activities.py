"""
Activities Router - list, get, filter activities.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List

from app.database import get_db
from app.models.activity import Activity

router = APIRouter()


@router.get("")
async def list_activities(
    sport_type: Optional[str] = Query(None, description="Filter by sport type: swim, bike, run"),
    from_date: Optional[date] = Query(None, description="Start date filter"),
    to_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Lista atividades com filtros"""
    query = db.query(Activity)
    
    if sport_type:
        query = query.filter(Activity.sport_type == sport_type)
    if from_date:
        query = query.filter(Activity.activity_date >= from_date)
    if to_date:
        query = query.filter(Activity.activity_date <= to_date)
    
    activities = query.order_by(Activity.activity_date.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "strava_id": a.strava_id,
            "name": a.name,
            "sport_type": a.sport_type,
            "date": a.activity_date.isoformat() if a.activity_date else None,
            "duration_seconds": a.duration_seconds,
            "distance_meters": a.distance_meters,
            "moving_time_seconds": a.moving_time_seconds,
            "avg_hr": a.avg_hr,
            "max_hr": a.max_hr,
            "avg_watts": a.avg_watts,
            "weighted_avg_watts": a.weighted_avg_watts,
            "avg_pace_sec_per_100m": a.avg_pace_sec_per_100m,
            "avg_pace_sec_per_km": a.avg_pace_sec_per_km,
            "tss": a.tss,
            "intensity_factor": a.intensity_factor
        }
        for a in activities
    ]


@router.get("/{activity_id}")
async def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """Detalhes de uma atividade"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return {
        "id": activity.id,
        "strava_id": activity.strava_id,
        "name": activity.name,
        "sport_type": activity.sport_type,
        "date": activity.activity_date.isoformat() if activity.activity_date else None,
        "duration_seconds": activity.duration_seconds,
        "distance_meters": activity.distance_meters,
        "moving_time_seconds": activity.moving_time_seconds,
        "avg_hr": activity.avg_hr,
        "max_hr": activity.max_hr,
        "avg_watts": activity.avg_watts,
        "weighted_avg_watts": activity.weighted_avg_watts,
        "avg_pace_sec_per_100m": activity.avg_pace_sec_per_100m,
        "avg_pace_sec_per_km": activity.avg_pace_sec_per_km,
        "tss": activity.tss,
        "intensity_factor": activity.intensity_factor,
        "streams_json": activity.streams_json
    }


@router.get("/stats/summary")
async def get_activity_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get activity statistics for the last N days"""
    from datetime import timedelta
    
    cutoff = date.today() - timedelta(days=days)
    activities = db.query(Activity).filter(Activity.activity_date >= cutoff).all()
    
    # Group by sport type
    by_sport = {}
    total_tss = 0
    total_duration = 0
    
    for a in activities:
        sport = a.sport_type or 'other'
        if sport not in by_sport:
            by_sport[sport] = {
                'count': 0,
                'total_tss': 0,
                'total_duration': 0,
                'total_distance': 0
            }
        by_sport[sport]['count'] += 1
        by_sport[sport]['total_tss'] += a.tss or 0
        by_sport[sport]['total_duration'] += a.moving_time_seconds or 0
        by_sport[sport]['total_distance'] += a.distance_meters or 0
        
        total_tss += a.tss or 0
        total_duration += a.moving_time_seconds or 0
    
    return {
        "period_days": days,
        "total_activities": len(activities),
        "total_tss": round(total_tss, 1),
        "total_duration_hours": round(total_duration / 3600, 1),
        "by_sport": by_sport
    }
