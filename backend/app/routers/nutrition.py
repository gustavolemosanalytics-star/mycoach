from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.database import get_db
from app.models.user import User
from app.models.nutrition import NutritionProfile, MealLog, MealPlan
from app.schemas.nutrition import (
    NutritionProfileCreate, 
    NutritionProfileResponse, 
    NutritionProfileUpdate,
    MealLogCreate,
    MealLogResponse,
    DailyNutritionSummary
)
from app.utils.auth import get_current_user
from app.services.nutrition_service import nutrition_service
from app.services.ai_service import ai_service

router = APIRouter()


@router.post("/profile", response_model=NutritionProfileResponse)
async def create_or_update_profile(
    profile_data: NutritionProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user nutrition profile and calculate targets."""
    existing = db.query(NutritionProfile).filter(NutritionProfile.user_id == current_user.id).first()
    
    # Calculate TDEE and Targets
    tdee = nutrition_service.calculate_tdee(profile_data)
    targets = nutrition_service.calculate_targets(tdee, profile_data.goal)
    
    if existing:
        update_data = profile_data.model_dump()
        for field, value in update_data.items():
            setattr(existing, field, value)
        
        # Update calculated values
        existing.tdee = tdee
        existing.target_calories = targets["target_calories"]
        existing.target_protein = targets["target_protein"]
        existing.target_carbs = targets["target_carbs"]
        existing.target_fat = targets["target_fat"]
        
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new profile
    profile = NutritionProfile(
        user_id=current_user.id,
        tdee=tdee,
        **targets,
        **profile_data.model_dump()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profile", response_model=NutritionProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the user's nutrition profile."""
    profile = db.query(NutritionProfile).filter(NutritionProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Nutrition profile not found")
    return profile


@router.post("/log-meal", response_model=MealLogResponse)
async def log_meal(
    meal_data: MealLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a meal with its foods and macro totals."""
    # Process totals
    totals = nutrition_service.process_meal_totals(meal_data.foods)
    
    meal = MealLog(
        user_id=current_user.id,
        **totals,
        **meal_data.model_dump()
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


@router.get("/daily-summary", response_model=DailyNutritionSummary)
async def get_daily_summary(
    summary_date: date = date.today(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily nutrition summary including targets and all meal logs."""
    profile = db.query(NutritionProfile).filter(NutritionProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Please complete your nutrition profile first")
        
    meals = db.query(MealLog).filter(
        MealLog.user_id == current_user.id,
        MealLog.date == summary_date
    ).all()
    
    total_cal = sum(m.calories for m in meals)
    total_p = sum(m.protein for m in meals)
    total_c = sum(m.carbs for m in meals)
    total_f = sum(m.fat for m in meals)
    
    return DailyNutritionSummary(
        date=summary_date,
        total_calories=total_cal,
        total_protein=total_p,
        total_carbs=total_c,
        total_fat=total_f,
        target_calories=profile.target_calories or 0,
        target_protein=profile.target_protein or 0,
        target_carbs=profile.target_carbs or 0,
        target_fat=profile.target_fat or 0,
        meals=meals
    )


@router.post("/chat")
async def nutrition_ai_chat(
    message: str,
    history: List[Dict[str, Any]] = [],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI Nutrition Copilot chat with tool processing."""
    profile = db.query(NutritionProfile).filter(NutritionProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Please complete your nutrition profile first")

    response = await ai_service.nutrition_chat(current_user.id, message, history, profile)
    
    if "tool_calls" in response:
        import json
        results = []
        for tool_call in response["tool_calls"]:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            if function_name == "log_meal":
                totals = nutrition_service.process_meal_totals(args["foods"])
                meal = MealLog(
                    user_id=current_user.id,
                    date=date.today(),
                    **totals,
                    **args
                )
                db.add(meal)
                results.append(f"Refeição '{args['name']}' registrada com sucesso!")
            
            elif function_name == "save_meal_plan":
                plan = MealPlan(
                    user_id=current_user.id,
                    title=args["title"],
                    content=args["content"],
                    plan_type="ai"
                )
                db.add(plan)
                results.append(f"Plano alimentar '{args['title']}' salvo com sucesso!")
        
        db.commit()
        # Update response message to confirm actions
        response["message"] += "\n\n" + "\n".join(results)
        
    return response
