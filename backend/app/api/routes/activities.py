import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, BackgroundTasks, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.activity import Activity
from app.models.user import User
from app.models.training_plan import SportType
from app.schemas.activity import ActivityUploadResponse, ActivityListItem, ActivityDetail
from app.services.parsers.fit_parser import parse_fit
from app.services.parsers.tcx_parser import parse_tcx
from app.services.analytics.training_metrics import (
    calc_tss,
    calc_trimp,
    calc_hr_drift,
    calc_pace_consistency,
    calc_time_in_hr_zones,
    calc_intensity_factor,
    calc_variability_index,
)
from app.services.file_service import upload_file, generate_file_key

router = APIRouter()


async def _run_ai_analysis(activity_id: uuid.UUID, db_url: str):
    """Background task to run AI analysis on an activity."""
    # Imported here to avoid circular imports; will be implemented in Phase 5
    try:
        from app.services.agents.coach_agent import analyze_activity_background
        await analyze_activity_background(activity_id, db_url)
    except ImportError:
        pass


@router.post("/upload", response_model=ActivityUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_activity(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    feeling: Optional[str] = Form(None),
    perceived_effort: Optional[int] = Form(None),
    athlete_notes: Optional[str] = Form(None),
    planned_session_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    filename = file.filename or ""

    # Parse file
    if filename.lower().endswith(".fit"):
        parsed = parse_fit(content)
    elif filename.lower().endswith(".tcx"):
        parsed = parse_tcx(content)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato não suportado. Use .FIT (preferencial) ou .TCX",
        )

    # Upload original to storage
    file_key = generate_file_key(str(current_user.id), filename)
    await upload_file(content, file_key)

    # Calculate TSS
    sport = parsed["sport"]
    tss = calc_tss(
        sport=sport,
        duration_s=parsed["total_timer_seconds"],
        distance_m=parsed["total_distance_meters"],
        avg_hr=parsed.get("avg_hr"),
        np=parsed.get("normalized_power"),
        ftp=current_user.ftp,
        threshold_pace=current_user.run_threshold_pace,
        css=current_user.css,
        hr_max=current_user.hr_max,
    )

    # Calculate additional metrics
    trimp = None
    if parsed.get("avg_hr") and current_user.hr_max:
        trimp = calc_trimp(
            duration_s=parsed["total_timer_seconds"],
            avg_hr=parsed["avg_hr"],
            hr_rest=current_user.hr_rest or 60,
            hr_max=current_user.hr_max,
        )

    hr_drift = calc_hr_drift(parsed.get("hr_stream") or [])
    pace_con = calc_pace_consistency(parsed.get("pace_stream") or [])

    # Time in HR zones
    time_in_zones = None
    hr_zone_dist = None
    if parsed.get("hr_stream") and current_user.hr_max:
        time_in_zones = calc_time_in_hr_zones(parsed["hr_stream"], current_user.hr_max)
        total_time = sum(time_in_zones.values())
        if total_time > 0:
            hr_zone_dist = {k: round(v / total_time * 100, 1) for k, v in time_in_zones.items()}

    # IF and VI
    intensity_factor = None
    variability_index = parsed.get("variability_index")
    if parsed.get("normalized_power") and current_user.ftp:
        intensity_factor = calc_intensity_factor(parsed["normalized_power"], current_user.ftp)

    # Map sport string to enum
    sport_enum = SportType(sport) if sport in [e.value for e in SportType] else SportType.RUN

    activity = Activity(
        user_id=current_user.id,
        sport=sport_enum,
        title=parsed["title"],
        start_time=parsed["start_time"],
        end_time=parsed.get("end_time"),
        source_file=file_key,
        source_format=parsed["source_format"],
        total_elapsed_seconds=parsed["total_elapsed_seconds"],
        total_timer_seconds=parsed["total_timer_seconds"],
        total_moving_seconds=parsed.get("total_moving_seconds"),
        total_distance_meters=parsed["total_distance_meters"],
        avg_pace_min_km=parsed.get("avg_pace_min_km"),
        max_pace_min_km=parsed.get("max_pace_min_km"),
        avg_speed_kmh=parsed.get("avg_speed_kmh"),
        max_speed_kmh=parsed.get("max_speed_kmh"),
        avg_hr=parsed.get("avg_hr"),
        max_hr=parsed.get("max_hr"),
        min_hr=parsed.get("min_hr"),
        hr_zone_distribution=hr_zone_dist,
        time_in_zones_seconds=time_in_zones,
        avg_cadence=parsed.get("avg_cadence"),
        max_cadence=parsed.get("max_cadence"),
        avg_power=parsed.get("avg_power"),
        max_power=parsed.get("max_power"),
        normalized_power=parsed.get("normalized_power"),
        intensity_factor=intensity_factor,
        variability_index=variability_index,
        total_ascent_m=parsed.get("total_ascent_m"),
        total_descent_m=parsed.get("total_descent_m"),
        avg_temperature_c=parsed.get("avg_temperature_c"),
        max_temperature_c=parsed.get("max_temperature_c"),
        calories=parsed.get("calories"),
        tss=tss,
        trimp=trimp,
        training_effect_aerobic=parsed.get("training_effect_aerobic"),
        training_effect_anaerobic=parsed.get("training_effect_anaerobic"),
        avg_ground_contact_time_ms=parsed.get("avg_ground_contact_time_ms"),
        avg_stride_length_m=parsed.get("avg_stride_length_m"),
        avg_vertical_oscillation_mm=parsed.get("avg_vertical_oscillation_mm"),
        avg_vertical_ratio_pct=parsed.get("avg_vertical_ratio_pct"),
        avg_ground_contact_balance_pct=parsed.get("avg_ground_contact_balance_pct"),
        avg_stroke_rate=parsed.get("avg_stroke_rate"),
        pool_length_m=parsed.get("pool_length_m"),
        total_lengths=parsed.get("total_lengths"),
        swolf=parsed.get("swolf"),
        perceived_effort=perceived_effort,
        feeling=feeling,
        athlete_notes=athlete_notes,
        hr_stream=parsed.get("hr_stream"),
        pace_stream=parsed.get("pace_stream"),
        power_stream=parsed.get("power_stream"),
        cadence_stream=parsed.get("cadence_stream"),
        altitude_stream=parsed.get("altitude_stream"),
        gps_stream=parsed.get("gps_stream"),
        laps_data=parsed.get("laps_data"),
    )

    # Link to planned session if provided
    if planned_session_id:
        try:
            activity.planned_session_id = uuid.UUID(planned_session_id)
        except ValueError:
            pass

    db.add(activity)
    await db.commit()
    await db.refresh(activity)

    # Trigger AI analysis in background
    from app.core.config import settings
    background_tasks.add_task(_run_ai_analysis, activity.id, settings.DATABASE_URL)

    return activity


@router.get("", response_model=list[ActivityListItem])
async def list_activities(
    limit: int = 20,
    offset: int = 0,
    sport: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Activity).where(Activity.user_id == current_user.id)

    if sport:
        try:
            sport_enum = SportType(sport)
            query = query.where(Activity.sport == sport_enum)
        except ValueError:
            pass

    query = query.order_by(desc(Activity.start_time)).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{activity_id}", response_model=ActivityDetail)
async def get_activity(
    activity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id,
            Activity.user_id == current_user.id,
        )
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Activity).where(
            Activity.id == activity_id,
            Activity.user_id == current_user.id,
        )
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    await db.delete(activity)
    await db.commit()
