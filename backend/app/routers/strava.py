"""
Strava Router - OAuth flow and activity sync endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Optional

from app.database import get_db
from app.services.strava_client import strava_client, StravaClient
from app.models.strava_tokens import StravaTokens
from app.models.activity import Activity
from app.models.athlete import Athlete
from app.models.daily_metrics import DailyMetrics
from app.metrics.tss_calculator import TSSCalculator
from app.metrics.pmc_calculator import PMCCalculator
from app.config import get_settings

settings = get_settings()
router = APIRouter()


def get_strava_tokens(db: Session) -> Optional[StravaTokens]:
    """Get stored Strava tokens"""
    return db.query(StravaTokens).first()


def save_strava_tokens(db: Session, data: dict):
    """Save or update Strava tokens"""
    tokens = db.query(StravaTokens).first()
    if not tokens:
        tokens = StravaTokens(
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            expires_at=data['expires_at'],
            athlete_id=data.get('athlete', {}).get('id')
        )
        db.add(tokens)
    else:
        tokens.access_token = data['access_token']
        tokens.refresh_token = data['refresh_token']
        tokens.expires_at = data['expires_at']
        if data.get('athlete'):
            tokens.athlete_id = data['athlete']['id']
    db.commit()
    return tokens


def get_athlete_config(db: Session) -> dict:
    """Get athlete configuration for TSS calculation"""
    athlete = db.query(Athlete).first()
    if athlete:
        return {
            'ftp_watts': athlete.ftp_watts,
            'css_pace_sec': athlete.css_pace_sec,
            'run_threshold_pace_sec': athlete.run_threshold_pace_sec,
            'run_lthr': athlete.run_lthr,
            'fc_max': athlete.fc_max
        }
    return {
        'ftp_watts': 200,
        'css_pace_sec': 110,
        'run_threshold_pace_sec': 300,
        'run_lthr': 165,
        'fc_max': 185
    }


@router.get("/auth")
async def strava_auth_url():
    """Retorna URL para autenticação Strava"""
    url = strava_client.get_auth_url()
    return {"url": url}


@router.get("/callback")
async def strava_callback(code: str, db: Session = Depends(get_db)):
    """Callback do OAuth Strava"""
    try:
        tokens = strava_client.exchange_token(code)
        save_strava_tokens(db, tokens)
        return {
            "status": "connected",
            "athlete_id": tokens.get('athlete', {}).get('id'),
            "message": "Strava conectado com sucesso!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na autenticação: {str(e)}")


@router.post("/sync")
async def sync_strava(
    days_back: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Sincroniza atividades do Strava"""
    # Load tokens
    tokens = get_strava_tokens(db)
    if not tokens:
        raise HTTPException(status_code=400, detail="Strava não conectado. Autorize primeiro em /strava/auth")
    
    # Set tokens on client
    strava_client.set_tokens(tokens.access_token, tokens.refresh_token, tokens.expires_at)
    
    # Get athlete config for TSS calculation
    config = get_athlete_config(db)
    calculator = TSSCalculator(config)
    
    # Fetch activities
    after = datetime.now() - timedelta(days=days_back)
    try:
        activities = strava_client.get_activities(after=after)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar atividades: {str(e)}")
    
    # Update tokens if refreshed
    if strava_client.access_token != tokens.access_token:
        save_strava_tokens(db, {
            'access_token': strava_client.access_token,
            'refresh_token': strava_client.refresh_token,
            'expires_at': strava_client.expires_at
        })
    
    synced = []
    sport_map = {
        'Ride': 'bike', 'VirtualRide': 'bike',
        'Run': 'run', 'VirtualRun': 'run',
        'Swim': 'swim'
    }
    
    for act in activities:
        # Check if already exists
        existing = db.query(Activity).filter_by(strava_id=act['id']).first()
        if existing:
            continue
        
        # Calculate TSS
        tss = calculator.calc_tss(act)
        intensity_factor = calculator.get_intensity_factor(act)
        
        # Map sport type
        sport_type = sport_map.get(act.get('sport_type') or act.get('type'), 'other')
        
        # Calculate pace based on type
        avg_pace_100m = None
        avg_pace_km = None
        distance = act.get('distance', 0)
        moving_time = act.get('moving_time', 0)
        
        if sport_type == 'swim' and distance:
            avg_pace_100m = int((moving_time / distance) * 100)
        elif sport_type == 'run' and distance:
            avg_pace_km = int((moving_time / distance) * 1000)
        
        # Parse activity date
        activity_date = datetime.fromisoformat(
            act['start_date_local'].replace('Z', '')
        ).date()
        
        # Create activity record
        new_activity = Activity(
            strava_id=act['id'],
            sport_type=sport_type,
            name=act.get('name'),
            duration_seconds=act.get('elapsed_time'),
            moving_time_seconds=moving_time,
            distance_meters=distance,
            avg_hr=act.get('average_heartrate'),
            max_hr=act.get('max_heartrate'),
            avg_watts=act.get('average_watts'),
            weighted_avg_watts=act.get('weighted_average_watts'),
            avg_pace_sec_per_100m=avg_pace_100m,
            avg_pace_sec_per_km=avg_pace_km,
            tss=tss,
            intensity_factor=intensity_factor,
            activity_date=activity_date
        )
        
        db.add(new_activity)
        synced.append({
            'name': new_activity.name,
            'sport': sport_type,
            'tss': tss,
            'date': activity_date.isoformat()
        })
    
    db.commit()
    
    # Recalculate daily metrics
    await recalculate_daily_metrics(db)
    
    return {
        "synced_activities": len(synced),
        "activities": synced
    }


async def recalculate_daily_metrics(db: Session):
    """Recalculate CTL/ATL/TSB for all days with activities"""
    # Get all activities grouped by date
    activities = db.query(Activity).order_by(Activity.activity_date).all()
    
    if not activities:
        return
    
    # Group by date and sum TSS
    daily_tss = {}
    for act in activities:
        d = act.activity_date
        if d not in daily_tss:
            daily_tss[d] = 0
        daily_tss[d] += act.tss or 0
    
    # Fill in missing days
    if daily_tss:
        start = min(daily_tss.keys())
        end = max(daily_tss.keys())
        current = start
        while current <= end:
            if current not in daily_tss:
                daily_tss[current] = 0
            current += timedelta(days=1)
    
    # Calculate CTL/ATL/TSB
    pmc = PMCCalculator()
    
    for d in sorted(daily_tss.keys()):
        metrics = pmc.update(daily_tss[d])
        
        # Update or create daily metrics
        daily = db.query(DailyMetrics).filter_by(date=d).first()
        if not daily:
            daily = DailyMetrics(date=d)
            db.add(daily)
        
        daily.daily_tss = daily_tss[d]
        daily.ctl = metrics['ctl']
        daily.atl = metrics['atl']
        daily.tsb = metrics['tsb']
    
    db.commit()


@router.get("/status")
async def strava_status(db: Session = Depends(get_db)):
    """Check Strava connection status"""
    tokens = get_strava_tokens(db)
    if not tokens:
        return {"connected": False}
    
    return {
        "connected": True,
        "athlete_id": tokens.athlete_id,
        "expires_at": tokens.expires_at,
        "is_expired": datetime.now().timestamp() >= tokens.expires_at
    }
