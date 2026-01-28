from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.wellness import WellnessEntry
from app.schemas.wellness import WellnessCreate, WellnessResponse, WellnessUpdate, WellnessTrend
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=WellnessResponse, status_code=status.HTTP_201_CREATED)
async def create_wellness_entry(
    wellness_data: WellnessCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update wellness entry for a date."""
    # Check if entry exists for this date
    existing = db.query(WellnessEntry).filter(
        WellnessEntry.user_id == current_user.id,
        WellnessEntry.date == wellness_data.date
    ).first()
    
    if existing:
        # Update existing entry
        update_data = wellness_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        existing.readiness_score = existing.calculate_readiness()
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new entry
    entry = WellnessEntry(
        user_id=current_user.id,
        **wellness_data.model_dump()
    )
    
    # Calculate sleep duration
    if entry.sleep_start and entry.sleep_end:
        start_dt = datetime.combine(wellness_data.date - timedelta(days=1), entry.sleep_start)
        end_dt = datetime.combine(wellness_data.date, entry.sleep_end)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        entry.sleep_duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
    
    # Calculate readiness score
    entry.readiness_score = entry.calculate_readiness()
    
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    # Check wellness achievements
    from app.services.gamification import check_wellness_achievements
    check_wellness_achievements(current_user.id, db)
    
    return entry


@router.get("/", response_model=List[WellnessResponse])
async def list_wellness_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List wellness entries."""
    query = db.query(WellnessEntry).filter(WellnessEntry.user_id == current_user.id)
    
    if start_date:
        query = query.filter(WellnessEntry.date >= start_date)
    if end_date:
        query = query.filter(WellnessEntry.date <= end_date)
    
    entries = query.order_by(desc(WellnessEntry.date)).limit(limit).all()
    return entries


@router.get("/today", response_model=Optional[WellnessResponse])
async def get_today_wellness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's wellness entry."""
    today = date.today()
    entry = db.query(WellnessEntry).filter(
        WellnessEntry.user_id == current_user.id,
        WellnessEntry.date == today
    ).first()
    return entry


@router.get("/trends", response_model=WellnessTrend)
async def get_wellness_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wellness trends over a period."""
    from sqlalchemy import func
    
    start_date = date.today() - timedelta(days=days)
    
    entries = db.query(WellnessEntry).filter(
        WellnessEntry.user_id == current_user.id,
        WellnessEntry.date >= start_date
    ).all()
    
    if not entries:
        return WellnessTrend(
            period_days=days,
            trend_direction="stable"
        )
    
    # Calculate averages
    moods = [e.mood for e in entries if e.mood]
    energies = [e.energy_level for e in entries if e.energy_level]
    sleep_hours = [e.sleep_duration_minutes / 60 for e in entries if e.sleep_duration_minutes]
    readiness = [e.readiness_score for e in entries if e.readiness_score]
    
    avg_mood = sum(moods) / len(moods) if moods else None
    avg_energy = sum(energies) / len(energies) if energies else None
    avg_sleep = sum(sleep_hours) / len(sleep_hours) if sleep_hours else None
    avg_readiness = sum(readiness) / len(readiness) if readiness else None
    
    # Determine trend (compare first half vs second half)
    half = len(entries) // 2
    if half > 0 and readiness:
        first_half = [e.readiness_score for e in entries[:half] if e.readiness_score]
        second_half = [e.readiness_score for e in entries[half:] if e.readiness_score]
        if first_half and second_half:
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            if second_avg > first_avg + 5:
                trend = "improving"
            elif second_avg < first_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return WellnessTrend(
        period_days=days,
        avg_mood=round(avg_mood, 1) if avg_mood else None,
        avg_energy=round(avg_energy, 1) if avg_energy else None,
        avg_sleep_hours=round(avg_sleep, 1) if avg_sleep else None,
        avg_readiness=round(avg_readiness, 1) if avg_readiness else None,
        trend_direction=trend
    )


@router.get("/{entry_date}", response_model=WellnessResponse)
async def get_wellness_by_date(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wellness entry for a specific date."""
    entry = db.query(WellnessEntry).filter(
        WellnessEntry.user_id == current_user.id,
        WellnessEntry.date == entry_date
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wellness entry not found for this date"
        )
    
    return entry


@router.put("/{entry_date}", response_model=WellnessResponse)
async def update_wellness_entry(
    entry_date: date,
    wellness_update: WellnessUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a wellness entry."""
    entry = db.query(WellnessEntry).filter(
        WellnessEntry.user_id == current_user.id,
        WellnessEntry.date == entry_date
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wellness entry not found"
        )
    
    update_data = wellness_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    # Recalculate sleep duration and readiness
    if entry.sleep_start and entry.sleep_end:
        start_dt = datetime.combine(entry_date - timedelta(days=1), entry.sleep_start)
        end_dt = datetime.combine(entry_date, entry.sleep_end)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        entry.sleep_duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
    
    entry.readiness_score = entry.calculate_readiness()
    
    db.commit()
    db.refresh(entry)
    
    return entry


@router.delete("/{entry_date}")
async def delete_wellness_entry(
    entry_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a wellness entry."""
    entry = db.query(WellnessEntry).filter(
        WellnessEntry.user_id == current_user.id,
        WellnessEntry.date == entry_date
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wellness entry not found"
        )
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Wellness entry deleted successfully"}
