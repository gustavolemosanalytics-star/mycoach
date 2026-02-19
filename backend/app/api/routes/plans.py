import uuid
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.race import TargetRace
from app.models.training_plan import TrainingPlan, PlannedWeek, PlannedSession, PlanPhase, SportType, SessionIntensity
from app.models.weekly_analysis import WeeklyAnalysis
from app.schemas.race import RaceCreate, RaceResponse
from app.schemas.plan import (
    GeneratePlanRequest,
    TrainingPlanResponse,
    TrainingPlanListItem,
    PlannedWeekResponse,
    CurrentWeekResponse,
)
from app.schemas.analysis import WeeklyAnalysisResponse
from app.services.agents.coach_agent import generate_periodization, generate_weekly_plan, analyze_week

router = APIRouter()


# ============================================================
# Races
# ============================================================

@router.post("/races", response_model=RaceResponse, status_code=status.HTTP_201_CREATED)
async def create_race(
    data: RaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    race = TargetRace(user_id=current_user.id, **data.model_dump())
    db.add(race)
    await db.commit()
    await db.refresh(race)
    return race


@router.get("/races", response_model=list[RaceResponse])
async def list_races(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TargetRace)
        .where(TargetRace.user_id == current_user.id, TargetRace.is_active == True)
        .order_by(TargetRace.race_date)
    )
    return result.scalars().all()


@router.delete("/races/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_race(
    race_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TargetRace).where(TargetRace.id == race_id, TargetRace.user_id == current_user.id)
    )
    race = result.scalar_one_or_none()
    if not race:
        raise HTTPException(status_code=404, detail="Prova não encontrada")
    await db.delete(race)
    await db.commit()


# ============================================================
# Periodization & Plans
# ============================================================

@router.post("/generate", response_model=TrainingPlanResponse)
async def generate_plan(
    data: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get race
    result = await db.execute(
        select(TargetRace).where(TargetRace.id == data.race_id, TargetRace.user_id == current_user.id)
    )
    race = result.scalar_one_or_none()
    if not race:
        raise HTTPException(status_code=404, detail="Prova não encontrada")

    start = data.start_date or date.today()

    # Build athlete profile
    athlete_profile = {
        "experience_level": current_user.experience_level.value,
        "weekly_hours_available": current_user.weekly_hours_available,
        "training_days_per_week": current_user.training_days_per_week,
        "hr_max": current_user.hr_max,
        "ftp": current_user.ftp,
        "css": current_user.css,
        "run_threshold_pace": current_user.run_threshold_pace,
    }

    race_data = {
        "name": race.name,
        "race_type": race.race_type.value,
        "race_date": race.race_date.isoformat(),
        "goal_time_seconds": race.goal_time_seconds,
    }

    # Call AI to generate periodization
    periodization = await generate_periodization(
        athlete_profile=athlete_profile,
        target_race=race_data,
        start_date=start.isoformat(),
        modality=current_user.modality.value,
    )

    if "error" in periodization and not periodization.get("total_weeks"):
        raise HTTPException(status_code=500, detail=f"Erro ao gerar periodização: {periodization['error']}")

    total_weeks = periodization.get("total_weeks", 16)
    end = start + timedelta(weeks=total_weeks)

    # Deactivate existing plans
    result = await db.execute(
        select(TrainingPlan).where(
            TrainingPlan.user_id == current_user.id,
            TrainingPlan.is_active == True,
        )
    )
    for old_plan in result.scalars():
        old_plan.is_active = False

    # Create plan
    plan = TrainingPlan(
        user_id=current_user.id,
        race_id=race.id,
        name=f"Plano para {race.name}",
        start_date=start,
        end_date=end,
        total_weeks=total_weeks,
        periodization_structure=periodization,
    )
    db.add(plan)
    await db.flush()

    # Create weeks from overview
    weekly_overview = periodization.get("weekly_overview", [])
    for week_info in weekly_overview:
        week_num = week_info.get("week", 1)
        week_start = start + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6)

        phase_str = week_info.get("phase", "base").lower()
        try:
            phase = PlanPhase(phase_str)
        except ValueError:
            phase = PlanPhase.BASE

        week = PlannedWeek(
            plan_id=plan.id,
            week_number=week_num,
            start_date=week_start,
            end_date=week_end,
            phase=phase,
            target_volume_hours=week_info.get("target_hours"),
            target_tss=week_info.get("target_tss"),
            coach_notes=week_info.get("focus"),
        )
        db.add(week)

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(TrainingPlan)
        .options(selectinload(TrainingPlan.planned_weeks).selectinload(PlannedWeek.planned_sessions))
        .where(TrainingPlan.id == plan.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[TrainingPlanListItem])
async def list_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TrainingPlan)
        .where(TrainingPlan.user_id == current_user.id)
        .order_by(TrainingPlan.created_at.desc())
    )
    return result.scalars().all()


@router.get("/current-week", response_model=CurrentWeekResponse)
async def get_current_week(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    result = await db.execute(
        select(TrainingPlan)
        .options(
            selectinload(TrainingPlan.planned_weeks).selectinload(PlannedWeek.planned_sessions),
            selectinload(TrainingPlan.race),
        )
        .where(
            TrainingPlan.user_id == current_user.id,
            TrainingPlan.is_active == True,
        )
    )
    plan = result.scalar_one_or_none()

    if not plan:
        return CurrentWeekResponse()

    # Find current week
    current_week = None
    for week in plan.planned_weeks:
        if week.start_date <= today <= week.end_date:
            current_week = week
            break

    return CurrentWeekResponse(
        week=current_week,
        plan_name=plan.name,
        race_name=plan.race.name if plan.race else None,
        race_date=plan.race.race_date if plan.race else None,
    )


@router.post("/weeks/{week_id}/generate", response_model=PlannedWeekResponse)
async def generate_week_sessions(
    week_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get week with plan
    result = await db.execute(
        select(PlannedWeek)
        .options(selectinload(PlannedWeek.plan).selectinload(TrainingPlan.race))
        .where(PlannedWeek.id == week_id)
    )
    week = result.scalar_one_or_none()
    if not week or week.plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Semana não encontrada")

    athlete_profile = {
        "experience_level": current_user.experience_level.value,
        "weekly_hours_available": current_user.weekly_hours_available,
        "training_days_per_week": current_user.training_days_per_week,
        "hr_max": current_user.hr_max,
        "ftp": current_user.ftp,
        "css": current_user.css,
        "run_threshold_pace": current_user.run_threshold_pace,
    }

    race_data = None
    if week.plan.race:
        race_data = {
            "name": week.plan.race.name,
            "race_type": week.plan.race.race_type.value,
            "race_date": week.plan.race.race_date.isoformat(),
            "goal_time_seconds": week.plan.race.goal_time_seconds,
        }

    # Call AI
    plan_data = await generate_weekly_plan(
        athlete_profile=athlete_profile,
        target_race=race_data,
        current_phase=week.phase.value,
        week_number=week.week_number,
        total_weeks=week.plan.total_weeks,
        previous_week_analysis=None,
        load_history={"ctl": 0, "atl": 0, "tsb": 0},
        modality=current_user.modality.value,
    )

    # Update week metadata
    if plan_data.get("target_volume_hours"):
        week.target_volume_hours = plan_data["target_volume_hours"]
    if plan_data.get("target_tss"):
        week.target_tss = plan_data["target_tss"]
    if plan_data.get("coach_notes"):
        week.coach_notes = plan_data["coach_notes"]
    if plan_data.get("focus_areas"):
        week.focus_areas = plan_data["focus_areas"]

    # Create sessions
    for session_data in plan_data.get("sessions", []):
        sport_str = session_data.get("sport", "run").lower()
        try:
            sport = SportType(sport_str)
        except ValueError:
            sport = SportType.RUN

        intensity_str = session_data.get("intensity", "moderate").lower()
        try:
            intensity = SessionIntensity(intensity_str)
        except ValueError:
            intensity = SessionIntensity.MODERATE

        session = PlannedSession(
            week_id=week.id,
            day_of_week=session_data.get("day_of_week", 0),
            sport=sport,
            title=session_data.get("title", "Treino"),
            description=session_data.get("description"),
            intensity=intensity,
            target_duration_minutes=session_data.get("target_duration_minutes"),
            target_distance_meters=session_data.get("target_distance_meters"),
            target_tss=session_data.get("target_tss"),
            target_hr_zone=session_data.get("target_hr_zone"),
            workout_structure=session_data.get("workout_structure"),
        )
        db.add(session)

    await db.commit()

    # Reload
    result = await db.execute(
        select(PlannedWeek)
        .options(selectinload(PlannedWeek.planned_sessions))
        .where(PlannedWeek.id == week.id)
    )
    return result.scalar_one()


@router.post("/weeks/{week_id}/analyze", response_model=WeeklyAnalysisResponse)
async def analyze_week_endpoint(
    week_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.activity import Activity

    # Get week
    result = await db.execute(
        select(PlannedWeek)
        .options(selectinload(PlannedWeek.planned_sessions))
        .where(PlannedWeek.id == week_id)
    )
    week = result.scalar_one_or_none()
    if not week:
        raise HTTPException(status_code=404, detail="Semana não encontrada")

    # Get activities for this week
    result = await db.execute(
        select(Activity).where(
            Activity.user_id == current_user.id,
            Activity.start_time >= week.start_date.isoformat(),
            Activity.start_time <= (week.end_date + timedelta(days=1)).isoformat(),
        )
    )
    activities = result.scalars().all()

    week_activities = []
    for act in activities:
        week_activities.append({
            "sport": act.sport.value if act.sport else "run",
            "total_timer_seconds": act.total_timer_seconds,
            "total_distance_meters": act.total_distance_meters,
            "avg_hr": act.avg_hr,
            "tss": act.tss or 0,
        })

    planned_week_data = {
        "target_volume_hours": week.target_volume_hours,
        "target_tss": week.target_tss,
        "sessions_planned": len(week.planned_sessions),
        "sessions_completed": sum(1 for s in week.planned_sessions if s.is_completed),
        "phase": week.phase.value,
    }

    athlete_profile = {
        "hr_max": current_user.hr_max,
        "ftp": current_user.ftp,
    }

    # Call AI
    analysis_result = await analyze_week(
        week_activities=week_activities,
        planned_week=planned_week_data,
        athlete_profile=athlete_profile,
        load_history={"ctl": 0, "atl": 0, "tsb": 0},
        modality=current_user.modality.value,
    )

    # Save analysis
    total_tss = sum(a.get("tss", 0) for a in week_activities)
    total_duration = sum(a.get("total_timer_seconds", 0) for a in week_activities)

    analysis = WeeklyAnalysis(
        user_id=current_user.id,
        week_id=week.id,
        week_start=week.start_date,
        week_end=week.end_date,
        overall_score=analysis_result.get("overall_score"),
        summary=analysis_result.get("summary"),
        coach_message=analysis_result.get("coach_message"),
        planned_vs_actual=analysis_result.get("planned_vs_actual"),
        total_tss=total_tss,
        total_duration_seconds=total_duration,
        sessions_completed=planned_week_data["sessions_completed"],
        sessions_planned=planned_week_data["sessions_planned"],
        load_analysis=analysis_result.get("load_analysis"),
        highlights=analysis_result.get("highlights"),
        warnings=analysis_result.get("warnings"),
        improvements=analysis_result.get("improvements"),
        next_week_recommendations=analysis_result.get("next_week_recommendations"),
        trends=analysis_result.get("trends"),
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis
