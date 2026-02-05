"""
Athlete Router - athlete configuration and weight tracking.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from typing import Optional

from app.database import get_db
from app.models.athlete import Athlete
from app.models.daily_metrics import DailyMetrics

router = APIRouter()


class AthleteConfig(BaseModel):
    name: Optional[str] = None
    weight_kg: float = 78.0
    height_cm: int = 171
    ftp_watts: int = 200
    css_pace_sec: int = 110
    run_threshold_pace_sec: int = 300
    run_lthr: int = 165
    fc_max: int = 185
    target_weight_kg: float = 74.0
    tdee_kcal: int = 2582
    target_deficit_pct: float = 0.175


class WeightLog(BaseModel):
    weight_kg: float
    date_str: Optional[str] = None


@router.get("/config")
async def get_athlete_config(db: Session = Depends(get_db)):
    """Retorna configurações do atleta"""
    athlete = db.query(Athlete).first()
    
    if not athlete:
        return AthleteConfig()
    
    return {
        "id": athlete.id,
        "name": athlete.name,
        "weight_kg": athlete.weight_kg,
        "height_cm": athlete.height_cm,
        "ftp_watts": athlete.ftp_watts,
        "css_pace_sec": athlete.css_pace_sec,
        "run_threshold_pace_sec": athlete.run_threshold_pace_sec,
        "run_lthr": athlete.run_lthr,
        "fc_max": athlete.fc_max,
        "target_weight_kg": athlete.target_weight_kg,
        "tdee_kcal": athlete.tdee_kcal,
        "target_deficit_pct": athlete.target_deficit_pct,
        "created_at": athlete.created_at.isoformat() if athlete.created_at else None,
        "updated_at": athlete.updated_at.isoformat() if athlete.updated_at else None
    }


@router.put("/config")
async def update_athlete_config(config: AthleteConfig, db: Session = Depends(get_db)):
    """Atualiza configurações do atleta"""
    athlete = db.query(Athlete).first()
    
    if not athlete:
        athlete = Athlete()
        db.add(athlete)
    
    for key, value in config.dict().items():
        if value is not None:
            setattr(athlete, key, value)
    
    db.commit()
    db.refresh(athlete)
    
    return {
        "id": athlete.id,
        "name": athlete.name,
        "weight_kg": athlete.weight_kg,
        "height_cm": athlete.height_cm,
        "ftp_watts": athlete.ftp_watts,
        "css_pace_sec": athlete.css_pace_sec,
        "run_threshold_pace_sec": athlete.run_threshold_pace_sec,
        "run_lthr": athlete.run_lthr,
        "fc_max": athlete.fc_max,
        "target_weight_kg": athlete.target_weight_kg,
        "tdee_kcal": athlete.tdee_kcal,
        "target_deficit_pct": athlete.target_deficit_pct,
        "message": "Configurações atualizadas com sucesso"
    }


@router.post("/weight")
async def log_weight(data: WeightLog, db: Session = Depends(get_db)):
    """Registra peso"""
    target_date = date.fromisoformat(data.date_str) if data.date_str else date.today()
    
    # Update daily metrics
    daily = db.query(DailyMetrics).filter_by(date=target_date).first()
    if not daily:
        daily = DailyMetrics(date=target_date)
        db.add(daily)
    
    daily.weight_kg = data.weight_kg
    
    # Also update athlete current weight
    athlete = db.query(Athlete).first()
    if athlete:
        athlete.weight_kg = data.weight_kg
    
    db.commit()
    
    return {"date": target_date.isoformat(), "weight_kg": data.weight_kg}


@router.get("/weight-history")
async def get_weight_history(
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get weight history"""
    from datetime import timedelta
    
    cutoff = date.today() - timedelta(days=days)
    
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.date >= cutoff,
        DailyMetrics.weight_kg.isnot(None)
    ).order_by(DailyMetrics.date).all()
    
    athlete = db.query(Athlete).first()
    target = athlete.target_weight_kg if athlete else 74.0
    current = athlete.weight_kg if athlete else None
    
    return {
        "target_weight": target,
        "current_weight": current,
        "history": [
            {"date": m.date.isoformat(), "weight_kg": m.weight_kg}
            for m in metrics
        ]
    }


@router.get("/thresholds")
async def get_thresholds(db: Session = Depends(get_db)):
    """Get formatted thresholds for display"""
    athlete = db.query(Athlete).first()
    
    if not athlete:
        athlete = Athlete()
    
    def format_pace(seconds):
        """Format seconds to mm:ss"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    return {
        "bike": {
            "ftp_watts": athlete.ftp_watts,
            "description": f"FTP: {athlete.ftp_watts}W"
        },
        "run": {
            "threshold_pace_sec": athlete.run_threshold_pace_sec,
            "threshold_pace_formatted": format_pace(athlete.run_threshold_pace_sec) + "/km",
            "lthr": athlete.run_lthr,
            "description": f"Limiar: {format_pace(athlete.run_threshold_pace_sec)}/km @ {athlete.run_lthr}bpm"
        },
        "swim": {
            "css_pace_sec": athlete.css_pace_sec,
            "css_pace_formatted": format_pace(athlete.css_pace_sec) + "/100m",
            "description": f"CSS: {format_pace(athlete.css_pace_sec)}/100m"
        },
        "heart_rate": {
            "fc_max": athlete.fc_max,
            "lthr": athlete.run_lthr,
            "description": f"FC Máx: {athlete.fc_max}bpm"
        }
    }
