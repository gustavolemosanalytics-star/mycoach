from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.workout import Workout
from app.schemas.workout import (
    WorkoutCreate, 
    WorkoutResponse, 
    WorkoutUpdate, 
    WorkoutListResponse,
    WorkoutSummary,
    WeeklyStats
)
from app.utils.auth import get_current_user
from app.database import SessionLocal
from app.services.garmin_service import garmin_service

from fastapi import BackgroundTasks
from app.services.ai_service import ai_service

router = APIRouter()

async def generate_and_save_highlight(w_id: int):
    """Background task to generate and save AI highlight."""
    with SessionLocal() as session:
        w = session.query(Workout).get(w_id)
        if w:
            highlight = await ai_service.generate_workout_highlight(w)
            w.highlights = highlight
            session.commit()

@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_data: WorkoutCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new manual workout."""
    workout = Workout(
        user_id=current_user.id,
        source="manual",
        **workout_data.model_dump()
    )
    
    # Calculate pace if distance and time available
    if workout.distance and workout.elapsed_time:
        workout.avg_pace = (workout.elapsed_time / (workout.distance / 1000))
    
    db.add(workout)
    db.commit()
    db.refresh(workout)
    
    # Check for achievements
    from app.services.gamification import check_achievements
    check_achievements(current_user.id, db, workout)
    
    background_tasks.add_task(generate_and_save_highlight, workout.id)
    
    return workout


@router.post("/upload-tcx", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def upload_tcx(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a Garmin TCX file and create a workout from it."""
    if not file.filename.endswith('.tcx'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .tcx file.")
    
    try:
        content = await file.read()
        parsed_data = garmin_service.parse_tcx(content)
        
        # Create Workout from parsed data
        workout = Workout(
            user_id=current_user.id,
            source="garmin",
            name=parsed_data["name"],
            sport_type=parsed_data["sport_type"],
            start_date=datetime.fromisoformat(parsed_data["start_date"].replace('Z', '+00:00')),
            elapsed_time=int(parsed_data["total_time"]),
            moving_time=int(parsed_data["total_time"]),
            distance=parsed_data["total_distance"],
            avg_heart_rate=parsed_data["avg_hr"],
            max_heart_rate=parsed_data["max_hr"],
            calories=parsed_data["calories"],
            track_points=parsed_data["track_points"],
            laps=parsed_data["laps"]
        )

        # Set start lat/lng from first trackpoint
        if parsed_data["track_points"]:
            first_pt = parsed_data["track_points"][0]
            workout.start_lat = first_pt.get('lat')
            workout.start_lng = first_pt.get('lng')

        # Calculate pace
        if workout.distance and workout.elapsed_time:
            workout.avg_pace = (workout.elapsed_time / (workout.distance / 1000))

        db.add(workout)
        db.commit()
        db.refresh(workout)

        # Achievements and AI
        from app.services.gamification import check_achievements
        check_achievements(current_user.id, db, workout)
        background_tasks.add_task(generate_and_save_highlight, workout.id)

        return workout

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing TCX file: {str(e)}")


@router.get("/", response_model=WorkoutListResponse)
async def list_workouts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sport_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's workouts with pagination and filters."""
    query = db.query(Workout).filter(Workout.user_id == current_user.id)
    
    if sport_type:
        query = query.filter(Workout.sport_type == sport_type)
    if start_date:
        query = query.filter(Workout.start_date >= start_date)
    if end_date:
        query = query.filter(Workout.start_date <= end_date)
    
    total = query.count()
    workouts = query.order_by(desc(Workout.start_date)).offset((page - 1) * per_page).limit(per_page).all()
    
    return WorkoutListResponse(
        workouts=workouts,
        total=total,
        page=page,
        per_page=per_page,
        has_more=(page * per_page) < total
    )


@router.get("/summary", response_model=WorkoutSummary)
async def get_workout_summary(
    days: int = Query(7, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workout summary for a period."""
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.start_date >= start_date
    ).all()
    
    total_distance = sum(w.distance or 0 for w in workouts)
    total_time = sum(w.elapsed_time or 0 for w in workouts)
    total_calories = sum(w.calories or 0 for w in workouts)
    
    # By sport breakdown
    by_sport = {}
    for w in workouts:
        sport = w.sport_type
        if sport not in by_sport:
            by_sport[sport] = {"count": 0, "distance_km": 0, "time_minutes": 0}
        by_sport[sport]["count"] += 1
        by_sport[sport]["distance_km"] += (w.distance or 0) / 1000
        by_sport[sport]["time_minutes"] += (w.elapsed_time or 0) / 60
    
    return WorkoutSummary(
        total_workouts=len(workouts),
        total_distance_km=round(total_distance / 1000, 2),
        total_time_minutes=int(total_time / 60),
        total_calories=total_calories,
        by_sport=by_sport
    )


@router.get("/weekly", response_model=WeeklyStats)
async def get_weekly_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current week's statistics."""
    from datetime import date
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.start_date >= datetime.combine(week_start, datetime.min.time()),
        Workout.start_date <= datetime.combine(week_end, datetime.max.time())
    ).order_by(desc(Workout.start_date)).all()
    
    total_distance = sum(w.distance or 0 for w in workouts)
    total_time = sum(w.elapsed_time or 0 for w in workouts)
    total_calories = sum(w.calories or 0 for w in workouts)
    
    by_sport = {}
    for w in workouts:
        sport = w.sport_type
        if sport not in by_sport:
            by_sport[sport] = {"count": 0, "distance_km": 0, "time_minutes": 0}
        by_sport[sport]["count"] += 1
        by_sport[sport]["distance_km"] += (w.distance or 0) / 1000
        by_sport[sport]["time_minutes"] += (w.elapsed_time or 0) / 60
    
    summary = WorkoutSummary(
        total_workouts=len(workouts),
        total_distance_km=round(total_distance / 1000, 2),
        total_time_minutes=int(total_time / 60),
        total_calories=total_calories,
        by_sport=by_sport
    )
    
    return WeeklyStats(
        week_start=datetime.combine(week_start, datetime.min.time()),
        week_end=datetime.combine(week_end, datetime.max.time()),
        summary=summary,
        workouts=workouts
    )


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workout by ID."""
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_update: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workout."""
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    update_data = workout_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout, field, value)
    
    db.commit()
    db.refresh(workout)
    
    return workout


@router.delete("/{workout_id}")
async def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workout."""
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    db.delete(workout)
    db.commit()
    
    return {"message": "Workout deleted successfully"}
