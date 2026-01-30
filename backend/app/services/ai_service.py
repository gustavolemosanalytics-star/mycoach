import logging
from typing import List, Optional, Dict
from openai import OpenAI
from ..config import get_settings
from ..models.workout import Workout
from ..models.wellness import WellnessEntry
import json

logger = logging.getLogger(__name__)
settings = get_settings()

from ..models.nutrition import NutritionProfile, MealLog, MealPlan

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = "gpt-4o" # As per NeuralNutri requirements

    def _is_available(self) -> bool:
        if not self.client:
            logger.warning("OpenAI client not initialized. Check OPENAI_API_KEY.")
            return False
        return True

    async def generate_workout_highlight(self, workout: Workout) -> Dict:
        """Generates an epic and technical highlight for a single workout."""
        if not self._is_available():
            return {"highlight": "Treino concluído com sucesso! (IA não configurada)", "technical_insight": ""}

        sport_map = {
            "run": "Corrida", "ride": "Ciclismo", "swim": "Natação", "strength": "Fortalecimento"
        }
        
        prompt = f"""
        Analise este treino de {sport_map.get(workout.sport_type, workout.sport_type)}:
        - Nome: {workout.name}
        - Distância: {workout.distance_km} km
        - Duração: {workout.duration_formatted}
        - Pace Médio: {workout.avg_pace}
        - FC Média: {workout.avg_heart_rate} bpm
        - Calorias: {workout.calories}
        
        Crie um resumo motivacional curto (máx 2 frases) e um insight técnico sobre o esforço.
        Responda em JSON: {{"highlight": "...", "technical_insight": "..."}}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é o MyCoach, um treinador de triathlon experiente, motivacional e focado em performance data-driven."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating AI highlight: {e}")
            return {"highlight": "Ótimo esforço no treino de hoje!", "technical_insight": "Continue mantendo a consistência."}

    async def generate_weekly_analysis(self, workouts: List[Workout], wellness: List[WellnessEntry]) -> Dict:
        """Analyzes the week's data to provide training load and recovery insights."""
        if not self._is_available():
            return {"summary": "Sem análise automática para esta semana.", "recommendation": "Mantenha o plano planejado."}

        total_km = sum(w.distance_km for w in workouts if w.distance_km)
        total_hours = sum(w.duration_seconds for w in workouts if w.duration_seconds) / 3600
        avg_mood = sum(e.mood for e in wellness) / len(wellness) if wellness else 0
        avg_energy = sum(e.energy_level for e in wellness) / len(wellness) if wellness else 0
        
        prompt = f"""
        Resumo da Semana:
        - Total de Km: {total_km:.1f} km
        - Total de Horas: {total_hours:.1f}h
        - Média de Humor: {avg_mood:.1f}/5
        - Média de Energia: {avg_energy:.1f}/5
        - Número de treinos: {len(workouts)}
        
        Como treinador, analise a relação entre o volume de treino e o bem-estar do atleta.
        Dê um resumo da semana e uma recomendação para a próxima.
        Responda em JSON: {{"summary": "...", "recommendation": "...", "status": "improving/fatigued/stable"}}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é o MyCoach, analisando o balanço entre carga e recuperação de um atleta de elite."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating weekly analysis: {e}")
            return {"summary": "Semana concluída com volume sólido.", "recommendation": "Escute seu corpo e priorize o descanso se necessário.", "status": "stable"}

    async def nutrition_chat(self, user_id: int, message: str, history: List[Dict], profile: NutritionProfile) -> Dict:
        """Copiloto Neural de Nutrição com suporte a ferramentas."""
        if not self._is_available():
            return {"message": "Serviço de nutrição temporariamente indisponível."}

        system_prompt = f"""
        Você é o Copiloto Neural do MyCoach, um Nutricionista IA avançado.
        Perfil do Usuário:
        - Objetivo: {profile.goal}
        - TDEE: {profile.tdee} kcal
        - Macros Alvo: P:{profile.target_protein}g, C:{profile.target_carbs}g, G:{profile.target_fat}g
        
        Sua missão é ajudar o usuário a atingir seus objetivos através de conselhos baseados em dados, 
        criação de planos alimentares (`save_meal_plan`) e registro de refeições (`log_meal`).
        Sempre responda de forma profissional, motivacional e baseada em evidências.
        """

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "log_meal",
                    "description": "Registra uma refeição consumida pelo usuário",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Nome da refeição (ex: Café da manhã)"},
                            "foods": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "amount": {"type": "number"},
                                        "unit": {"type": "string"},
                                        "calories": {"type": "integer"},
                                        "protein": {"type": "number"},
                                        "carbs": {"type": "number"},
                                        "fat": {"type": "number"}
                                    }
                                }
                            }
                        },
                        "required": ["name", "foods"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_meal_plan",
                    "description": "Salva um plano alimentar sugerido para o usuário",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "content": {"type": "object", "description": "Estrutura completa das refeições e macros"}
                        },
                        "required": ["title", "content"]
                    }
                }
            }
        ]

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-10:]) # Últimas 10 mensagens
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Retorna os tool_calls para serem processados pelo router/service
                return {
                    "message": response_message.content or "Processando sua solicitação...",
                    "tool_calls": tool_calls
                }
            
            return {"message": response_message.content}
        except Exception as e:
            logger.error(f"Error in nutrition chat: {e}")
            return {"message": "Desculpe, tive um problema ao processar sua solicitação de nutrição."}

ai_service = AIService()
