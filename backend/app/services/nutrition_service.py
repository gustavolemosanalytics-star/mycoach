from typing import List, Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.nutrition import NutritionProfile, MealLog, NutritionGoal
from app.schemas.nutrition import NutritionProfileCreate, MealLogCreate


class NutritionService:
    """Service to handle nutrition logic like TDEE calculation and meal processing."""

    def calculate_tdee(self, profile: NutritionProfileCreate) -> int:
        """
        Calculate Total Daily Energy Expenditure using Mifflin-St Jeor Equation.
        BMR = (10 * weight) + (6.25 * height) - (5 * age) + s
        s = +5 for male, -161 for female
        """
        s = 5 if profile.gender.lower() == "male" else -161
        bmr = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) + s
        
        # Activity multipliers
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        factor = multipliers.get(profile.activity_level.lower(), 1.2)
        return int(bmr * factor)

    def calculate_targets(self, tdee: int, goal: str) -> Dict[str, int]:
        """Calculate target calories and macros based on goal."""
        # Adjust calories based on goal
        if goal == NutritionGoal.CUTTING:
            target_calories = int(tdee * 0.8) # 20% deficit
        elif goal == NutritionGoal.BULKING:
            target_calories = int(tdee * 1.1) # 10% surplus
        else:
            target_calories = tdee
            
        # Standard balanced distribution: 30% Protein, 40% Carbs, 30% Fat
        # (Protein: 4kcal/g, Carbs: 4kcal/g, Fat: 9kcal/g)
        protein_p = 0.30
        carbs_p = 0.40
        fat_p = 0.30
        
        target_protein = int((target_calories * protein_p) / 4)
        target_carbs = int((target_calories * carbs_p) / 4)
        target_fat = int((target_calories * fat_p) / 9)
        
        return {
            "target_calories": target_calories,
            "target_protein": target_protein,
            "target_carbs": target_carbs,
            "target_fat": target_fat
        }

    def process_meal_totals(self, foods: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate totals for a list of food items."""
        totals = {
            "calories": 0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0
        }
        
        for food in foods:
            totals["calories"] += food.get("calories", 0)
            totals["protein"] += food.get("protein", 0.0)
            totals["carbs"] += food.get("carbs", 0.0)
            totals["fat"] += food.get("fat", 0.0)
            
        return totals


nutrition_service = NutritionService()
