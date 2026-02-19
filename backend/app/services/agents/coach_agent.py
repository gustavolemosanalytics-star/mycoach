"""
Coach Agent — Agente IA Treinador com 4 funções.
Usa OpenAI API com respostas em JSON estruturado.
"""
import json
import uuid
from typing import Any, Optional

import openai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.services.agents.prompts import get_coach_prompt


def _get_client() -> openai.AsyncOpenAI | None:
    if not settings.OPENAI_API_KEY:
        return None
    return openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def _format_pace(seconds_per_km: float) -> str:
    if not seconds_per_km:
        return "N/A"
    minutes = int(seconds_per_km) // 60
    secs = int(seconds_per_km) % 60
    return f"{minutes}:{secs:02d}"


def _format_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h}h{m:02d}min"
    return f"{m}min"


async def analyze_activity(
    activity_data: dict,
    planned_session: Optional[dict],
    athlete_profile: dict,
    modality: str,
) -> dict:
    """
    Analisa uma atividade individual.
    Retorna JSON: score, summary, execution_analysis, planned_vs_actual,
    highlights, warnings, recommendations, fatigue_indicators.
    """
    client = _get_client()
    if not client:
        return {"error": "OpenAI não configurada", "score": 0}

    system_prompt = get_coach_prompt(modality)

    user_msg = f"""Analise esta atividade e forneça uma avaliação completa.

PERFIL DO ATLETA:
- Modalidade: {modality}
- FC Máx: {athlete_profile.get('hr_max', 'N/A')}bpm
- FC Limiar: {athlete_profile.get('hr_threshold', 'N/A')}bpm
- FTP: {athlete_profile.get('ftp', 'N/A')}W
- Pace Limiar: {_format_pace(athlete_profile.get('run_threshold_pace', 0))}/km

ATIVIDADE:
- Tipo: {activity_data.get('sport', 'N/A')}
- Duração: {_format_duration(activity_data.get('total_timer_seconds', 0))}
- Distância: {activity_data.get('total_distance_meters', 0) / 1000:.2f}km
- FC Média: {activity_data.get('avg_hr', 'N/A')}bpm | Máx: {activity_data.get('max_hr', 'N/A')}bpm
- Pace Médio: {_format_pace(activity_data.get('avg_pace_min_km', 0) * 60 if activity_data.get('avg_pace_min_km') else 0)}/km
- TSS: {activity_data.get('tss', 'N/A')}
- Cadência: {activity_data.get('avg_cadence', 'N/A')}spm
- Potência Média: {activity_data.get('avg_power', 'N/A')}W | NP: {activity_data.get('normalized_power', 'N/A')}W
- IF: {activity_data.get('intensity_factor', 'N/A')} | VI: {activity_data.get('variability_index', 'N/A')}
- Elevação: +{activity_data.get('total_ascent_m', 0)}m
- HR Drift: {activity_data.get('hr_drift', 'N/A')}%
- Sensação: {activity_data.get('feeling', 'N/A')} | RPE: {activity_data.get('perceived_effort', 'N/A')}
"""

    if planned_session:
        user_msg += f"""
SESSÃO PLANEJADA:
- Título: {planned_session.get('title', 'N/A')}
- Duração alvo: {planned_session.get('target_duration_minutes', 'N/A')}min
- TSS alvo: {planned_session.get('target_tss', 'N/A')}
- Zona alvo: {planned_session.get('target_hr_zone', 'N/A')}
- Descrição: {planned_session.get('description', 'N/A')}
"""

    user_msg += """
Responda em JSON com estas chaves:
{
  "score": 0-100,
  "summary": "resumo em 2-3 frases",
  "execution_analysis": {
    "pace": "análise do pace",
    "heart_rate": "análise da FC",
    "cadence": "análise da cadência",
    "power": "análise da potência (se aplicável)",
    "consistency": "consistência dos splits"
  },
  "planned_vs_actual": {
    "compliance_pct": 0-100,
    "notes": "comparação com o planejado"
  },
  "highlights": ["pontos positivos"],
  "warnings": ["alertas/atenções"],
  "recommendations": ["recomendações para próximos treinos"],
  "fatigue_indicators": {
    "hr_drift": "interpretação do HR drift",
    "estimated_fatigue": "baixa/moderada/alta"
  }
}"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "score": 0}


async def analyze_week(
    week_activities: list[dict],
    planned_week: Optional[dict],
    athlete_profile: dict,
    load_history: dict,
    modality: str,
) -> dict:
    """
    Análise semanal completa.
    Retorna JSON: overall_score, summary, coach_message, planned_vs_actual,
    load_analysis, next_week_recommendations, trends.
    """
    client = _get_client()
    if not client:
        return {"error": "OpenAI não configurada", "overall_score": 0}

    system_prompt = get_coach_prompt(modality)

    activities_text = ""
    for act in week_activities:
        activities_text += (
            f"- {act.get('sport', 'N/A')}: {_format_duration(act.get('total_timer_seconds', 0))} | "
            f"{act.get('total_distance_meters', 0) / 1000:.1f}km | "
            f"TSS: {act.get('tss', 0):.0f} | FC: {act.get('avg_hr', 'N/A')}bpm\n"
        )

    user_msg = f"""Analise a semana de treino completa.

PERFIL: {modality} | FC Máx: {athlete_profile.get('hr_max', 'N/A')} | FTP: {athlete_profile.get('ftp', 'N/A')}W

ATIVIDADES DA SEMANA:
{activities_text}

CARGA:
- CTL (fitness): {load_history.get('ctl', 0):.1f}
- ATL (fadiga): {load_history.get('atl', 0):.1f}
- TSB (forma): {load_history.get('tsb', 0):.1f}
- TSS total semana: {sum(a.get('tss', 0) for a in week_activities):.0f}
"""

    if planned_week:
        user_msg += f"""
PLANEJADO:
- Horas alvo: {planned_week.get('target_volume_hours', 'N/A')}h
- TSS alvo: {planned_week.get('target_tss', 'N/A')}
- Sessões planejadas: {planned_week.get('sessions_planned', 'N/A')}
- Sessões completadas: {planned_week.get('sessions_completed', 'N/A')}
- Fase: {planned_week.get('phase', 'N/A')}
"""

    user_msg += """
Responda em JSON:
{
  "overall_score": 0-100,
  "summary": "resumo da semana",
  "coach_message": "mensagem motivacional/técnica do treinador",
  "planned_vs_actual": {"compliance_pct": 0-100, "notes": "..."},
  "load_analysis": {"fatigue_level": "...", "injury_risk": "low/moderate/high", "readiness_score": 0-100},
  "highlights": ["positivos"],
  "warnings": ["alertas"],
  "improvements": ["areas de melhoria"],
  "next_week_recommendations": {"volume_adjustment": "...", "intensity_focus": "...", "key_sessions": ["..."], "recovery_notes": "..."},
  "trends": {"fitness_trend": "ascending/stable/descending", "fatigue_trend": "...", "form_trend": "..."}
}"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "overall_score": 0}


async def generate_weekly_plan(
    athlete_profile: dict,
    target_race: Optional[dict],
    current_phase: str,
    week_number: int,
    total_weeks: int,
    previous_week_analysis: Optional[dict],
    load_history: dict,
    modality: str,
) -> dict:
    """
    Gera sessões detalhadas para uma semana.
    Retorna JSON: sessions[] com workout_structure.
    """
    client = _get_client()
    if not client:
        return {"error": "OpenAI não configurada", "sessions": []}

    system_prompt = get_coach_prompt(modality)

    user_msg = f"""Gere o plano de treino detalhado para esta semana.

ATLETA:
- Modalidade: {modality}
- Nível: {athlete_profile.get('experience_level', 'intermediate')}
- Horas disponíveis/semana: {athlete_profile.get('weekly_hours_available', 10)}h
- Dias/semana: {athlete_profile.get('training_days_per_week', 6)}
- FC Máx: {athlete_profile.get('hr_max', 'N/A')} | FTP: {athlete_profile.get('ftp', 'N/A')}W
- Pace limiar: {_format_pace(athlete_profile.get('run_threshold_pace', 0))}/km

PERIODIZAÇÃO:
- Semana {week_number} de {total_weeks}
- Fase atual: {current_phase}
- CTL: {load_history.get('ctl', 0):.1f} | TSB: {load_history.get('tsb', 0):.1f}
"""

    if target_race:
        user_msg += f"""
PROVA ALVO:
- {target_race.get('name', 'N/A')} ({target_race.get('race_type', 'N/A')})
- Data: {target_race.get('race_date', 'N/A')}
- Meta: {target_race.get('goal_time_seconds', 'N/A')}s
"""

    if previous_week_analysis:
        user_msg += f"""
SEMANA ANTERIOR:
- Score: {previous_week_analysis.get('overall_score', 'N/A')}
- Compliance: {previous_week_analysis.get('compliance_pct', 'N/A')}%
- Recomendações: {previous_week_analysis.get('next_week_recommendations', 'N/A')}
"""

    sports_text = "swim, bike, run, strength, brick, rest" if modality == "triathlon" else "run, strength, rest"

    user_msg += f"""
REGRAS:
- Respeitar disponibilidade do atleta
- Progressão máxima 10% volume/semana
- Distribuição polarizada 80/20
- Sessões intensas com 48h de intervalo
- Pelo menos 1 dia de descanso
- Modalidades disponíveis: {sports_text}

Responda em JSON:
{{
  "week_number": {week_number},
  "phase": "{current_phase}",
  "target_volume_hours": X.X,
  "target_tss": X,
  "coach_notes": "notas do treinador",
  "focus_areas": {{"swim": "foco", "bike": "foco", "run": "foco"}},
  "sessions": [
    {{
      "day_of_week": 0-6,
      "sport": "run|bike|swim|strength|brick|rest",
      "title": "Nome da sessão",
      "description": "Descrição detalhada",
      "intensity": "recovery|easy|moderate|hard|race_pace",
      "target_duration_minutes": X,
      "target_distance_meters": X,
      "target_tss": X,
      "target_hr_zone": 1-5,
      "workout_structure": {{
        "warmup": "detalhes",
        "main_set": "detalhes",
        "cooldown": "detalhes"
      }}
    }}
  ]
}}"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e), "sessions": []}


async def generate_periodization(
    athlete_profile: dict,
    target_race: dict,
    start_date: str,
    modality: str,
) -> dict:
    """
    Gera periodização macro completa.
    Retorna JSON: phases[], weekly_overview[], race_week_plan, key_milestones[].
    """
    client = _get_client()
    if not client:
        return {"error": "OpenAI não configurada"}

    system_prompt = get_coach_prompt(modality)

    user_msg = f"""Gere uma periodização completa de treino.

ATLETA:
- Modalidade: {modality}
- Nível: {athlete_profile.get('experience_level', 'intermediate')}
- Horas/semana: {athlete_profile.get('weekly_hours_available', 10)}h
- Dias/semana: {athlete_profile.get('training_days_per_week', 6)}

PROVA ALVO:
- {target_race.get('name', 'N/A')} ({target_race.get('race_type', 'N/A')})
- Data: {target_race.get('race_date', 'N/A')}
- Meta tempo: {target_race.get('goal_time_seconds', 'N/A')}s

DATA INÍCIO: {start_date}

REGRAS:
- Ciclo 3 semanas carga + 1 descarga
- Base 30-40%, Build 30-40%, Peak 15-20%, Taper 10-15%
- Progressão +5-10% por semana de carga
- Descarga -30-40% do volume
- Especificidade aumenta progressivamente

Responda em JSON:
{{
  "total_weeks": X,
  "phases": [
    {{
      "phase": "base|build|peak|taper|recovery|transition",
      "duration_weeks": X,
      "objective": "objetivo da fase",
      "weekly_volume_range_hours": "X-Y",
      "intensity_distribution": "80/20 ou 75/25",
      "key_sessions": ["sessões características"]
    }}
  ],
  "weekly_overview": [
    {{
      "week": 1,
      "phase": "base",
      "target_hours": X.X,
      "target_tss": X,
      "focus": "foco da semana",
      "is_recovery_week": false
    }}
  ],
  "race_week_plan": "plano para a semana da prova",
  "key_milestones": ["marcos importantes"]
}}"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


async def analyze_activity_background(activity_id: uuid.UUID, db_url: str):
    """Background task to analyze an activity with AI."""
    engine = create_async_engine(db_url)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as db:
        from app.models.activity import Activity
        from app.models.user import User

        result = await db.execute(select(Activity).where(Activity.id == activity_id))
        activity = result.scalar_one_or_none()
        if not activity:
            return

        result = await db.execute(select(User).where(User.id == activity.user_id))
        user = result.scalar_one_or_none()
        if not user:
            return

        athlete_profile = {
            "hr_max": user.hr_max,
            "hr_threshold": user.hr_threshold,
            "ftp": user.ftp,
            "css": user.css,
            "run_threshold_pace": user.run_threshold_pace,
            "experience_level": user.experience_level.value if user.experience_level else "intermediate",
        }

        activity_data = {
            "sport": activity.sport.value if activity.sport else "run",
            "total_timer_seconds": activity.total_timer_seconds,
            "total_distance_meters": activity.total_distance_meters,
            "avg_hr": activity.avg_hr,
            "max_hr": activity.max_hr,
            "avg_pace_min_km": activity.avg_pace_min_km,
            "avg_power": activity.avg_power,
            "normalized_power": activity.normalized_power,
            "intensity_factor": activity.intensity_factor,
            "variability_index": activity.variability_index,
            "tss": activity.tss,
            "avg_cadence": activity.avg_cadence,
            "total_ascent_m": activity.total_ascent_m,
            "feeling": activity.feeling,
            "perceived_effort": activity.perceived_effort,
        }

        analysis = await analyze_activity(
            activity_data=activity_data,
            planned_session=None,
            athlete_profile=athlete_profile,
            modality=user.modality.value,
        )

        activity.ai_analysis = analysis
        activity.ai_score = analysis.get("score", 0)
        await db.commit()

    await engine.dispose()
