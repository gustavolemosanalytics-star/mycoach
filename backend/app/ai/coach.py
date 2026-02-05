"""
AI Coach Module - OpenAI integration for personalized coaching.
"""
import openai
from datetime import date
from typing import Optional, List, Dict
import json

from app.config import get_settings

settings = get_settings()


class AICoach:
    """
    Módulo de IA para análise e recomendações personalizadas.
    Integra com OpenAI GPT-4 para respostas contextualizadas.
    """
    
    SYSTEM_PROMPT = """Você é um coach de triathlon experiente ajudando Gustavo, 
um atleta de 30 anos preparando para um Ironman 70.3 (1000m natação, 40km bike, 10km corrida).

DADOS DO ATLETA:
- Peso atual: {weight_kg}kg | Meta: {target_weight}kg
- FTP Bike: {ftp}W | CSS Natação: {css}/100m | Pace Limiar Corrida: {run_pace}/km
- FC Máx: {fc_max}bpm

CONTEXTO DO PLANO:
- Prova alvo: 12/04/2026
- Periodização: Base → Recovery → Build → Peak → Taper → Race
- Treina às 5:30 AM em jejum (maioria das sessões)
- Equipamento: rolo smart, piscina 25m, equipamentos de força em casa

SUAS RESPONSABILIDADES:
1. Analisar dados de treino e dar feedback
2. Sugerir ajustes na nutrição baseado no cenário do dia
3. Alertar sobre sinais de overtraining (TSB muito negativo)
4. Motivar e manter o atleta focado
5. Responder dúvidas técnicas sobre treino e nutrição

CENÁRIOS NUTRICIONAIS:
- A: Treino jejum manhã → café completo pós-treino
- B: Natação meio-dia → lanche leve pré, almoço pós
- C: Treino à tarde → pré-treino leve, jantar completo
- D: Descanso → deficit maior para acelerar perda de peso

REGRAS:
- Seja direto e prático
- Use dados concretos quando disponíveis
- Priorize recuperação se TSB < -15
- Sugira redução se compliance < 80%
- Comemore conquistas e PRs
"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def _format_pace(self, seconds: int) -> str:
        """Formata pace em mm:ss"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    def _build_context(self, athlete_data: dict, metrics: dict) -> str:
        """Constrói contexto atual para o prompt"""
        recent_activities = self._format_recent_activities(metrics.get('recent_activities', []))
        nutrition = self._format_nutrition(metrics.get('today_nutrition', {}))
        
        return f"""
ESTADO ATUAL ({date.today()}):
- Peso: {metrics.get('weight', 'N/A')}kg
- CTL (Fitness): {metrics.get('ctl', 0):.1f}
- ATL (Fadiga): {metrics.get('atl', 0):.1f}
- TSB (Forma): {metrics.get('tsb', 0):.1f}
- TSS últimos 7 dias: {metrics.get('weekly_tss', 0):.0f}

ÚLTIMAS ATIVIDADES:
{recent_activities}

NUTRIÇÃO HOJE:
{nutrition}
"""
    
    def _format_recent_activities(self, activities: list) -> str:
        if not activities:
            return "Nenhuma atividade recente"
        
        lines = []
        for act in activities[:5]:
            duration_min = act.get('duration_min', act.get('moving_time_seconds', 0) / 60)
            lines.append(
                f"- {act.get('date', 'N/A')}: {act.get('sport_type', 'N/A').upper()} | "
                f"{duration_min:.0f}min | TSS: {act.get('tss', 0):.0f}"
            )
        return "\n".join(lines)
    
    def _format_nutrition(self, nutrition: dict) -> str:
        if not nutrition:
            return "Sem registro de nutrição hoje"
        
        return (
            f"Calorias: {nutrition.get('calories', 0)} kcal | "
            f"Proteína: {nutrition.get('protein', 0)}g | "
            f"Carbs: {nutrition.get('carbs', 0)}g | "
            f"Gordura: {nutrition.get('fat', 0)}g"
        )
    
    async def chat(
        self, 
        user_message: str, 
        athlete_data: dict, 
        current_metrics: dict,
        conversation_history: List[dict] = None
    ) -> str:
        """
        Processa mensagem do usuário e retorna resposta do coach.
        """
        if not self.client:
            return "AI Coach não configurado. Configure OPENAI_API_KEY no .env"
        
        system_prompt = self.SYSTEM_PROMPT.format(
            weight_kg=athlete_data.get('weight_kg', 78),
            target_weight=athlete_data.get('target_weight_kg', 74),
            ftp=athlete_data.get('ftp_watts', 200),
            css=self._format_pace(athlete_data.get('css_pace_sec', 110)),
            run_pace=self._format_pace(athlete_data.get('run_threshold_pace_sec', 300)),
            fc_max=athlete_data.get('fc_max', 185)
        )
        
        context = self._build_context(athlete_data, current_metrics)
        
        messages = [
            {"role": "system", "content": system_prompt + "\n\n" + context}
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro na comunicação com IA: {str(e)}"
    
    async def analyze_week(self, weekly_data: dict) -> Dict:
        """
        Análise automática da semana com insights.
        """
        if not self.client:
            return {"error": "AI Coach não configurado"}
        
        prompt = f"""
Analise a semana de treino e forneça:
1. Resumo do volume e intensidade
2. Pontos positivos
3. Pontos de atenção
4. Recomendação para próxima semana

DADOS DA SEMANA:
- TSS Total: {weekly_data.get('total_tss', 0)}
- TSS Target: {weekly_data.get('target_tss', 0)}
- Compliance: {weekly_data.get('compliance', 0):.0f}%
- Sessões completadas: {weekly_data.get('completed', 0)}/{weekly_data.get('planned', 0)}
- CTL atual: {weekly_data.get('ctl', 0):.1f}
- TSB atual: {weekly_data.get('tsb', 0):.1f}

SESSÕES:
{self._format_weekly_sessions(weekly_data.get('sessions', []))}

Responda em formato JSON com as chaves: summary, positives, concerns, recommendations
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um analista de performance esportiva. Responda sempre em JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e)}
    
    def _format_weekly_sessions(self, sessions: list) -> str:
        if not sessions:
            return "Nenhuma sessão registrada"
        
        lines = []
        for s in sessions:
            status = "✓" if s.get('completed') else "✗"
            lines.append(
                f"{status} {s.get('day', 'N/A')}: {s.get('sport_type', 'N/A')} - {s.get('name', 'N/A')} | "
                f"Planned: {s.get('planned_tss', 'N/A')} | Actual: {s.get('actual_tss', 'N/A')}"
            )
        return "\n".join(lines)
    
    async def suggest_nutrition_scenario(
        self, 
        today_plan: dict, 
        current_weight: float,
        target_weight: float
    ) -> str:
        """
        Sugere cenário nutricional baseado no treino do dia.
        """
        if not self.client:
            return "AI Coach não configurado"
        
        prompt = f"""
Baseado no treino de hoje, qual cenário nutricional recomendar?

TREINO DE HOJE:
- Tipo: {today_plan.get('sport_type', 'Descanso')}
- Sessão: {today_plan.get('session_name', 'N/A')}
- Duração: {today_plan.get('duration_min', 0)} min
- TSS esperado: {today_plan.get('target_tss', 0)}
- Horário: {today_plan.get('time', 'N/A')}

CONTEXTO:
- Peso atual: {current_weight}kg
- Meta: {target_weight}kg
- Diferença: {current_weight - target_weight:.1f}kg

CENÁRIOS DISPONÍVEIS:
A: Treino jejum manhã (5:30) → café completo pós-treino (~2.190 kcal)
B: Natação meio-dia → lanche leve pré, almoço pós (~2.130 kcal)
C: Treino tarde (16-17h) → pré-treino leve, jantar completo (~2.050 kcal)
D: Descanso → deficit maior (~1.787 kcal)

Responda com:
1. Cenário recomendado (A, B, C ou D)
2. Justificativa breve
3. Dica do dia
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Você é um nutricionista esportivo. Seja direto e prático."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro: {str(e)}"


# Singleton instance
ai_coach = AICoach()
