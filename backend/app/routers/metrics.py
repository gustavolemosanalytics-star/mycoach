"""
Metrics Router - CTL/ATL/TSB, daily metrics, projections.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional

from app.database import get_db
from app.models.daily_metrics import DailyMetrics
from app.metrics.pmc_calculator import PMCCalculator

router = APIRouter()


@router.get("/daily")
async def get_daily_metrics(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Retorna métricas diárias (TSS, CTL, ATL, TSB)"""
    if not from_date:
        from_date = date.today() - timedelta(days=90)
    if not to_date:
        to_date = date.today()
    
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.date >= from_date,
        DailyMetrics.date <= to_date
    ).order_by(DailyMetrics.date).all()
    
    return [
        {
            "date": m.date.isoformat(),
            "daily_tss": m.daily_tss,
            "ctl": m.ctl,
            "atl": m.atl,
            "tsb": m.tsb,
            "calories_consumed": m.calories_consumed,
            "protein_g": m.protein_g,
            "carbs_g": m.carbs_g,
            "fat_g": m.fat_g,
            "weight_kg": m.weight_kg
        }
        for m in metrics
    ]


@router.get("/current")
async def get_current_form(db: Session = Depends(get_db)):
    """Retorna forma atual (CTL, ATL, TSB de hoje)"""
    today_metric = db.query(DailyMetrics).filter_by(date=date.today()).first()
    
    if today_metric:
        pmc = PMCCalculator()
        status = pmc.get_form_status(today_metric.tsb or 0)
        return {
            "date": date.today().isoformat(),
            "ctl": today_metric.ctl,
            "atl": today_metric.atl,
            "tsb": today_metric.tsb,
            "status": status,
            "data_status": "actual"
        }
    
    # Calculate based on last record
    last = db.query(DailyMetrics).order_by(DailyMetrics.date.desc()).first()
    if last:
        # Project forward with 0 TSS days
        pmc = PMCCalculator(last.ctl or 0, last.atl or 0)
        days_since = (date.today() - last.date).days
        
        for _ in range(days_since):
            metrics = pmc.update(0)
        
        status = pmc.get_form_status(metrics['tsb'])
        return {
            "date": date.today().isoformat(),
            "ctl": metrics['ctl'],
            "atl": metrics['atl'],
            "tsb": metrics['tsb'],
            "status": status,
            "data_status": "projected"
        }
    
    return {
        "date": date.today().isoformat(),
        "ctl": 0,
        "atl": 0,
        "tsb": 0,
        "status": {"text": "Sem dados", "color": "#999", "status": "no_data"},
        "data_status": "no_data"
    }


@router.get("/projection")
async def project_taper(
    target_date: date = Query(..., description="Target date for projection (e.g., race day)"),
    taper_intensity: float = Query(0.5, ge=0.1, le=1.0, description="Taper intensity (0.5 = reduce to 50%)"),
    db: Session = Depends(get_db)
):
    """Projeta forma até a data alvo (ex: dia da prova)"""
    # Get current form
    current = await get_current_form(db)
    
    if current['data_status'] == 'no_data':
        raise HTTPException(status_code=400, detail="No training data available for projection")
    
    days_to_target = (target_date - date.today()).days
    
    if days_to_target <= 0:
        raise HTTPException(status_code=400, detail="Target date must be in the future")
    
    pmc = PMCCalculator(current['ctl'], current['atl'])
    projection = pmc.project_taper(
        current['ctl'], 
        current['atl'], 
        days_to_target,
        taper_intensity
    )
    
    return {
        "current": current,
        "target_date": target_date.isoformat(),
        "days_to_target": days_to_target,
        "projection": projection,
        "race_day_form": pmc.get_form_status(projection[-1]['tsb']) if projection else None
    }


@router.get("/weekly-summary")
async def get_weekly_summary(
    weeks_back: int = Query(4, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Get weekly TSS summary"""
    from app.models.activity import Activity
    
    results = []
    today = date.today()
    
    for week in range(weeks_back):
        # Calculate week start (Monday) and end (Sunday)
        week_start = today - timedelta(days=today.weekday() + 7 * week)
        week_end = week_start + timedelta(days=6)
        
        # Get activities for the week
        activities = db.query(Activity).filter(
            Activity.activity_date >= week_start,
            Activity.activity_date <= week_end
        ).all()
        
        total_tss = sum(a.tss or 0 for a in activities)
        by_sport = {}
        
        for a in activities:
            sport = a.sport_type or 'other'
            if sport not in by_sport:
                by_sport[sport] = {'count': 0, 'tss': 0}
            by_sport[sport]['count'] += 1
            by_sport[sport]['tss'] += a.tss or 0
        
        results.append({
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "total_activities": len(activities),
            "total_tss": round(total_tss, 1),
            "by_sport": by_sport
        })
    
    return results
