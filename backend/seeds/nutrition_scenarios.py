"""
Nutrition Scenarios seed data.
Per specification: A, B, C, D scenarios for different training situations.
"""

SCENARIOS = [
    {
        "scenario_code": "A",
        "name": "Treino em Jejum (5:30 AM)",
        "description": "Para dias de bike/corrida pela manhã em jejum",
        "total_calories": 2191,
        "protein_g": 173,
        "carbs_g": 230,
        "fat_g": 65,
        "meals_json": {
            "meals": [
                {
                    "time": "07:30",
                    "name": "Café Pós-Treino",
                    "description": "3 ovos mexidos + 2 fatias pão integral + 1 banana + café",
                    "calories": 488, "protein": 40, "carbs": 55, "fat": 12
                },
                {
                    "time": "09:30",
                    "name": "Lanche Matinal",
                    "description": "200g iogurte grego + 30g granola + 10g mel",
                    "calories": 342, "protein": 28, "carbs": 35, "fat": 10
                },
                {
                    "time": "12:00",
                    "name": "Almoço",
                    "description": "150g frango + 150g arroz + 60g feijão + salada + azeite",
                    "calories": 598, "protein": 45, "carbs": 65, "fat": 18
                },
                {
                    "time": "16:00",
                    "name": "Lanche da Tarde",
                    "description": "1 scoop whey + 1 banana + 15g pasta de amendoim",
                    "calories": 356, "protein": 22, "carbs": 40, "fat": 12
                },
                {
                    "time": "19:00",
                    "name": "Jantar",
                    "description": "150g peixe + 200g batata doce + 150g legumes",
                    "calories": 407, "protein": 38, "carbs": 35, "fat": 13
                }
            ]
        }
    },
    {
        "scenario_code": "B",
        "name": "Natação ao Meio-Dia (12h)",
        "description": "Para dias com natação no horário do almoço",
        "total_calories": 2129,
        "protein_g": 158,
        "carbs_g": 230,
        "fat_g": 65,
        "meals_json": {
            "meals": [
                {
                    "time": "07:30",
                    "name": "Café da Manhã",
                    "description": "2 ovos + 2 fatias pão integral + 1/2 abacate + café",
                    "calories": 426, "protein": 30, "carbs": 45, "fat": 14
                },
                {
                    "time": "09:30",
                    "name": "Lanche Pré-Natação",
                    "description": "1 banana + 100g iogurte natural (fácil digestão)",
                    "calories": 199, "protein": 8, "carbs": 35, "fat": 3
                },
                {
                    "time": "12:00",
                    "name": "TREINO NATAÇÃO",
                    "description": "45-60min",
                    "calories": 0, "protein": 0, "carbs": 0, "fat": 0
                },
                {
                    "time": "13:00",
                    "name": "Almoço Pós-Natação",
                    "description": "150g carne magra + 180g arroz + 50g feijão + salada + azeite",
                    "calories": 612, "protein": 48, "carbs": 70, "fat": 16
                },
                {
                    "time": "16:00",
                    "name": "Lanche da Tarde",
                    "description": "200g cottage + 1 maçã + 20g castanhas",
                    "calories": 383, "protein": 32, "carbs": 30, "fat": 15
                },
                {
                    "time": "19:00",
                    "name": "Jantar",
                    "description": "3 ovos (omelete) + 150g batata doce + 200g legumes + azeite",
                    "calories": 509, "protein": 40, "carbs": 50, "fat": 17
                }
            ]
        }
    },
    {
        "scenario_code": "C",
        "name": "Treino à Tarde (16-17h)",
        "description": "Para dias de corrida ou bike no período da tarde",
        "total_calories": 2050,
        "protein_g": 155,
        "carbs_g": 230,
        "fat_g": 58,
        "meals_json": {
            "meals": [
                {
                    "time": "07:30",
                    "name": "Café da Manhã",
                    "description": "2 ovos + 2 fatias pão integral + 1/2 abacate + café",
                    "calories": 419, "protein": 32, "carbs": 40, "fat": 15
                },
                {
                    "time": "09:30",
                    "name": "Lanche Matinal",
                    "description": "200g iogurte grego + 20g aveia + 1 col chá mel",
                    "calories": 292, "protein": 25, "carbs": 30, "fat": 8
                },
                {
                    "time": "12:00",
                    "name": "Almoço (moderado)",
                    "description": "130g frango + 130g arroz + 50g feijão + salada + azeite",
                    "calories": 519, "protein": 42, "carbs": 55, "fat": 15
                },
                {
                    "time": "15:00",
                    "name": "Pré-Treino",
                    "description": "1 banana grande + 100g iogurte desnatado",
                    "calories": 210, "protein": 8, "carbs": 40, "fat": 2
                },
                {
                    "time": "16:00",
                    "name": "TREINO",
                    "description": "Corrida/Bike 40-90min",
                    "calories": 0, "protein": 0, "carbs": 0, "fat": 0
                },
                {
                    "time": "19:00",
                    "name": "Jantar Pós-Treino",
                    "description": "180g carne/peixe + 200g batata doce + 150g legumes + azeite",
                    "calories": 610, "protein": 48, "carbs": 65, "fat": 18
                }
            ]
        }
    },
    {
        "scenario_code": "D",
        "name": "Dia de Descanso/Recovery",
        "description": "Segundas e dias de descanso ativo - deficit maior",
        "total_calories": 1787,
        "protein_g": 163,
        "carbs_g": 125,
        "fat_g": 71,
        "meals_json": {
            "meals": [
                {
                    "time": "07:30",
                    "name": "Café da Manhã",
                    "description": "3 ovos mexidos + 1 fatia pão integral + 1/2 abacate",
                    "calories": 382, "protein": 30, "carbs": 25, "fat": 18
                },
                {
                    "time": "09:30",
                    "name": "Lanche Matinal",
                    "description": "150g cottage + 15g castanhas + 1/2 maçã",
                    "calories": 248, "protein": 20, "carbs": 15, "fat": 12
                },
                {
                    "time": "12:00",
                    "name": "Almoço",
                    "description": "150g frango/peixe + 100g arroz + 40g feijão + salada abundante + azeite",
                    "calories": 495, "protein": 45, "carbs": 45, "fat": 15
                },
                {
                    "time": "16:00",
                    "name": "Lanche da Tarde",
                    "description": "1 scoop whey + 1/2 banana + 200ml água",
                    "calories": 264, "protein": 28, "carbs": 20, "fat": 8
                },
                {
                    "time": "19:00",
                    "name": "Jantar (low carb)",
                    "description": "150g salmão/tilápia + 250g legumes variados + azeite",
                    "calories": 398, "protein": 40, "carbs": 20, "fat": 18
                }
            ]
        }
    }
]


def seed_nutrition_scenarios(db):
    """Seed nutrition scenarios into database"""
    from app.models.nutrition_scenario import NutritionScenario
    
    for scenario in SCENARIOS:
        existing = db.query(NutritionScenario).filter_by(
            scenario_code=scenario['scenario_code']
        ).first()
        
        if not existing:
            new_scenario = NutritionScenario(
                scenario_code=scenario['scenario_code'],
                name=scenario['name'],
                description=scenario['description'],
                total_calories=scenario['total_calories'],
                protein_g=scenario['protein_g'],
                carbs_g=scenario['carbs_g'],
                fat_g=scenario['fat_g'],
                meals_json=scenario['meals_json']
            )
            db.add(new_scenario)
    
    db.commit()
    print("Nutrition scenarios seeded successfully!")


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    seed_nutrition_scenarios(db)
    db.close()
