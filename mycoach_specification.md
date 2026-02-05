# MyCoach - Especificação Técnica Completa

## Visão Geral

App de acompanhamento de treinos e nutrição para triathlon, com integração Strava e módulo de IA (GPT) para análise e recomendações personalizadas.

**Stack:** FastAPI (backend) + React (frontend) + PostgreSQL/SQLite + Strava API + OpenAI API

---

## 1. Arquitetura de Dados

### 1.1 Entidades Principais

```sql
-- Atleta (configurações e thresholds)
CREATE TABLE athlete (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    weight_kg DECIMAL(5,2) DEFAULT 78.0,
    height_cm INT DEFAULT 171,
    
    -- Thresholds para cálculo de TSS
    ftp_watts INT DEFAULT 200,           -- Functional Threshold Power (bike)
    css_pace_sec INT DEFAULT 110,        -- Critical Swim Speed (1:50/100m = 110s)
    run_threshold_pace_sec INT DEFAULT 300, -- Pace limiar corrida (5:00/km = 300s)
    run_lthr INT DEFAULT 165,            -- Lactate Threshold Heart Rate
    fc_max INT DEFAULT 185,
    
    -- Metas
    target_weight_kg DECIMAL(5,2) DEFAULT 74.0,
    tdee_kcal INT DEFAULT 2582,
    target_deficit_pct DECIMAL(4,2) DEFAULT 0.175,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Atividades (sincronizadas do Strava)
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    strava_id BIGINT UNIQUE,
    sport_type VARCHAR(20), -- 'swim', 'bike', 'run'
    name VARCHAR(255),
    
    -- Métricas básicas
    duration_seconds INT,
    distance_meters DECIMAL(10,2),
    moving_time_seconds INT,
    
    -- Métricas de intensidade
    avg_hr INT,
    max_hr INT,
    avg_watts INT,                    -- bike
    weighted_avg_watts INT,           -- NP (Normalized Power)
    avg_pace_sec_per_100m INT,        -- natação
    avg_pace_sec_per_km INT,          -- corrida
    
    -- TSS calculado
    tss DECIMAL(6,2),
    intensity_factor DECIMAL(4,3),
    
    -- Dados brutos (opcional)
    streams_json JSONB,               -- dados segundo a segundo
    
    activity_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Métricas diárias (CTL, ATL, TSB)
CREATE TABLE daily_metrics (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    
    -- TSS do dia (soma de todas atividades)
    daily_tss DECIMAL(6,2) DEFAULT 0,
    
    -- Performance Management Chart
    ctl DECIMAL(6,2),  -- Chronic Training Load (fitness)
    atl DECIMAL(6,2),  -- Acute Training Load (fatigue)
    tsb DECIMAL(6,2),  -- Training Stress Balance (form)
    
    -- Nutrição do dia
    calories_consumed INT,
    protein_g DECIMAL(5,1),
    carbs_g DECIMAL(5,1),
    fat_g DECIMAL(5,1),
    
    -- Peso
    weight_kg DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Refeições
CREATE TABLE meals (
    id SERIAL PRIMARY KEY,
    date DATE,
    meal_type VARCHAR(20), -- 'breakfast', 'lunch', 'dinner', 'snack'
    time TIME,
    
    name VARCHAR(255),
    calories INT,
    protein_g DECIMAL(5,1),
    carbs_g DECIMAL(5,1),
    fat_g DECIMAL(5,1),
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Plano de treino (semanas/sessões)
CREATE TABLE training_plan (
    id SERIAL PRIMARY KEY,
    week_number INT,
    phase VARCHAR(20),  -- 'BASE', 'BUILD', 'PEAK', 'TAPER', 'RACE'
    
    target_tss INT,
    target_ctl INT,
    notes TEXT,
    
    start_date DATE,
    end_date DATE
);

CREATE TABLE planned_sessions (
    id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES training_plan(id),
    
    day_of_week INT,  -- 0=Monday, 6=Sunday
    sport_type VARCHAR(20),
    session_name VARCHAR(100),
    description TEXT,
    
    duration_minutes INT,
    target_tss INT,
    target_zone VARCHAR(10),  -- 'Z2', 'Z3', 'Z4', etc.
    
    completed BOOLEAN DEFAULT FALSE,
    actual_activity_id INT REFERENCES activities(id)
);

-- Cenários de nutrição
CREATE TABLE nutrition_scenarios (
    id SERIAL PRIMARY KEY,
    scenario_code VARCHAR(10),  -- 'A', 'B', 'C', 'D'
    name VARCHAR(100),
    description TEXT,
    
    total_calories INT,
    protein_g INT,
    carbs_g INT,
    fat_g INT,
    
    meals_json JSONB  -- estrutura detalhada das refeições
);

-- Tokens Strava
CREATE TABLE strava_tokens (
    id SERIAL PRIMARY KEY,
    access_token TEXT,
    refresh_token TEXT,
    expires_at BIGINT,
    athlete_id BIGINT,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. Cálculos de Métricas (TSS/CTL/ATL/TSB)

### 2.1 Módulo Python de Cálculos

```python
# metrics/tss_calculator.py

from datetime import date, timedelta
from typing import Optional
import math

class TSSCalculator:
    """
    Calcula TSS para diferentes modalidades e métricas de PMC
    """
    
    def __init__(self, athlete_config: dict):
        self.ftp = athlete_config.get('ftp_watts', 200)
        self.css_pace = athlete_config.get('css_pace_sec', 110)  # 1:50/100m
        self.run_threshold_pace = athlete_config.get('run_threshold_pace_sec', 300)  # 5:00/km
        self.run_lthr = athlete_config.get('run_lthr', 165)
        self.fc_max = athlete_config.get('fc_max', 185)
    
    # ==================== BIKE TSS ====================
    def calc_bike_tss(
        self, 
        duration_seconds: int,
        normalized_power: Optional[int] = None,
        avg_power: Optional[int] = None,
        avg_hr: Optional[int] = None
    ) -> float:
        """
        Calcula TSS para bike.
        Prioridade: NP > Avg Power > HR
        
        TSS = (duration_sec * NP * IF) / (FTP * 3600) * 100
        IF = NP / FTP
        """
        if normalized_power and self.ftp:
            np = normalized_power
        elif avg_power and self.ftp:
            np = avg_power * 1.05  # Estimativa de NP baseado em avg
        elif avg_hr:
            # hrTSS como fallback
            return self._calc_hr_tss(duration_seconds, avg_hr)
        else:
            return 0.0
        
        intensity_factor = np / self.ftp
        duration_hours = duration_seconds / 3600
        tss = (duration_hours * np * intensity_factor) / self.ftp * 100
        
        return round(tss, 1)
    
    # ==================== RUN TSS ====================
    def calc_run_tss(
        self,
        duration_seconds: int,
        distance_meters: float,
        avg_hr: Optional[int] = None
    ) -> float:
        """
        Calcula rTSS (running TSS) baseado em pace ou hrTSS baseado em FC.
        
        rTSS = (duration_sec * NGP * IF) / (threshold_pace * 3600) * 100
        Onde NGP = Normalized Graded Pace (sem elevação, usa pace médio)
        """
        if distance_meters and distance_meters > 0:
            # Pace em segundos por km
            pace_sec_per_km = (duration_seconds / distance_meters) * 1000
            
            # Intensity Factor = threshold_pace / atual_pace
            # (invertido porque pace menor = mais rápido)
            intensity_factor = self.run_threshold_pace / pace_sec_per_km
            intensity_factor = min(intensity_factor, 1.5)  # Cap em 150%
            
            duration_hours = duration_seconds / 3600
            
            # rTSS simplificado
            tss = duration_hours * (intensity_factor ** 2) * 100
            return round(tss, 1)
        
        elif avg_hr:
            return self._calc_hr_tss(duration_seconds, avg_hr)
        
        return 0.0
    
    # ==================== SWIM TSS ====================
    def calc_swim_tss(
        self,
        duration_seconds: int,
        distance_meters: float
    ) -> float:
        """
        Calcula sTSS (swim TSS) baseado em CSS.
        
        sTSS = duration_hours * IF² * 100
        IF = CSS / pace_atual (invertido)
        """
        if distance_meters and distance_meters > 0:
            # Pace em segundos por 100m
            pace_sec_per_100m = (duration_seconds / distance_meters) * 100
            
            # IF = CSS / pace (CSS menor = mais rápido = IF > 1)
            intensity_factor = self.css_pace / pace_sec_per_100m
            intensity_factor = min(intensity_factor, 1.5)  # Cap
            
            duration_hours = duration_seconds / 3600
            tss = duration_hours * (intensity_factor ** 2) * 100
            
            return round(tss, 1)
        
        return 0.0
    
    # ==================== HR TSS (fallback) ====================
    def _calc_hr_tss(self, duration_seconds: int, avg_hr: int) -> float:
        """
        hrTSS como fallback quando não há dados de potência/pace.
        Fórmula de Coggan simplificada.
        """
        # TRIMP modificado
        hr_reserve = (avg_hr - 60) / (self.fc_max - 60)  # Assume FC repouso = 60
        hr_reserve = max(0, min(hr_reserve, 1))
        
        duration_hours = duration_seconds / 3600
        
        # Aproximação: hrTSS ≈ TRIMP * fator
        trimp = duration_hours * hr_reserve * 100
        tss = trimp * 0.8  # Fator de ajuste
        
        return round(tss, 1)
    
    # ==================== Cálculo automático por tipo ====================
    def calc_tss(self, activity: dict) -> float:
        """
        Calcula TSS automaticamente baseado no tipo de atividade.
        """
        sport = activity.get('sport_type', '').lower()
        
        if sport in ['ride', 'bike', 'cycling', 'virtualride']:
            return self.calc_bike_tss(
                duration_seconds=activity.get('moving_time', 0),
                normalized_power=activity.get('weighted_average_watts'),
                avg_power=activity.get('average_watts'),
                avg_hr=activity.get('average_heartrate')
            )
        
        elif sport in ['run', 'running', 'virtualrun']:
            return self.calc_run_tss(
                duration_seconds=activity.get('moving_time', 0),
                distance_meters=activity.get('distance', 0),
                avg_hr=activity.get('average_heartrate')
            )
        
        elif sport in ['swim', 'swimming']:
            return self.calc_swim_tss(
                duration_seconds=activity.get('moving_time', 0),
                distance_meters=activity.get('distance', 0)
            )
        
        # Fallback para outros tipos (strength, etc.)
        elif activity.get('average_heartrate'):
            return self._calc_hr_tss(
                activity.get('moving_time', 0),
                activity.get('average_heartrate')
            )
        
        return 0.0


class PMCCalculator:
    """
    Performance Management Chart - calcula CTL, ATL, TSB
    """
    
    CTL_DAYS = 42  # Constante de tempo para fitness
    ATL_DAYS = 7   # Constante de tempo para fadiga
    
    def __init__(self, initial_ctl: float = 0, initial_atl: float = 0):
        self.ctl = initial_ctl
        self.atl = initial_atl
    
    def update(self, daily_tss: float) -> dict:
        """
        Atualiza CTL e ATL com o TSS do dia usando média móvel exponencial.
        
        CTL_hoje = CTL_ontem + (TSS_hoje - CTL_ontem) / 42
        ATL_hoje = ATL_ontem + (TSS_hoje - ATL_ontem) / 7
        TSB = CTL - ATL
        """
        self.ctl = self.ctl + (daily_tss - self.ctl) / self.CTL_DAYS
        self.atl = self.atl + (daily_tss - self.atl) / self.ATL_DAYS
        
        tsb = self.ctl - self.atl
        
        return {
            'ctl': round(self.ctl, 1),
            'atl': round(self.atl, 1),
            'tsb': round(tsb, 1)
        }
    
    def calculate_history(self, daily_tss_list: list[dict]) -> list[dict]:
        """
        Calcula histórico completo de CTL/ATL/TSB.
        
        Args:
            daily_tss_list: Lista de {'date': date, 'tss': float}
        
        Returns:
            Lista de {'date': date, 'tss': float, 'ctl': float, 'atl': float, 'tsb': float}
        """
        results = []
        
        for day in sorted(daily_tss_list, key=lambda x: x['date']):
            metrics = self.update(day['tss'])
            results.append({
                'date': day['date'],
                'tss': day['tss'],
                **metrics
            })
        
        return results
    
    def project_taper(self, current_ctl: float, current_atl: float, days: int = 14) -> list[dict]:
        """
        Projeta CTL/ATL/TSB durante taper com TSS reduzido.
        Útil para planejar a forma no dia da prova.
        """
        projections = []
        ctl = current_ctl
        atl = current_atl
        
        for day in range(1, days + 1):
            # TSS progressivamente menor durante taper
            if day <= 7:
                daily_tss = current_ctl * 0.5  # Semana 1: 50% do CTL
            else:
                daily_tss = current_ctl * 0.25  # Semana 2: 25% do CTL
            
            ctl = ctl + (daily_tss - ctl) / self.CTL_DAYS
            atl = atl + (daily_tss - atl) / self.ATL_DAYS
            tsb = ctl - atl
            
            projections.append({
                'day': day,
                'projected_tss': round(daily_tss, 0),
                'ctl': round(ctl, 1),
                'atl': round(atl, 1),
                'tsb': round(tsb, 1)
            })
        
        return projections
```

---

## 3. Integração Strava

### 3.1 Módulo de Sincronização

```python
# integrations/strava.py

import requests
from datetime import datetime, timedelta
from typing import Optional
import os

class StravaClient:
    """
    Cliente para Strava API v3
    """
    
    BASE_URL = "https://www.strava.com/api/v3"
    AUTH_URL = "https://www.strava.com/oauth/token"
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
    
    # ==================== OAuth ====================
    def get_auth_url(self, redirect_uri: str) -> str:
        """Gera URL para autorização OAuth"""
        return (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&scope=read,activity:read_all"
        )
    
    def exchange_token(self, code: str) -> dict:
        """Troca authorization code por tokens"""
        response = requests.post(self.AUTH_URL, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        })
        data = response.json()
        
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expires_at = data['expires_at']
        
        return data
    
    def refresh_access_token(self) -> dict:
        """Renova access token usando refresh token"""
        response = requests.post(self.AUTH_URL, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        })
        data = response.json()
        
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expires_at = data['expires_at']
        
        return data
    
    def _ensure_token(self):
        """Garante que o token está válido"""
        if self.expires_at and datetime.now().timestamp() >= self.expires_at - 300:
            self.refresh_access_token()
    
    def _headers(self) -> dict:
        self._ensure_token()
        return {"Authorization": f"Bearer {self.access_token}"}
    
    # ==================== Activities ====================
    def get_activities(
        self, 
        after: Optional[datetime] = None, 
        before: Optional[datetime] = None,
        per_page: int = 100
    ) -> list[dict]:
        """
        Busca atividades do atleta.
        
        Campos retornados relevantes:
        - id, name, sport_type
        - distance, moving_time, elapsed_time
        - average_speed, max_speed
        - average_heartrate, max_heartrate
        - average_watts, weighted_average_watts (se disponível)
        - start_date, start_date_local
        """
        params = {'per_page': per_page}
        
        if after:
            params['after'] = int(after.timestamp())
        if before:
            params['before'] = int(before.timestamp())
        
        response = requests.get(
            f"{self.BASE_URL}/athlete/activities",
            headers=self._headers(),
            params=params
        )
        
        return response.json()
    
    def get_activity_detail(self, activity_id: int) -> dict:
        """Busca detalhes de uma atividade específica"""
        response = requests.get(
            f"{self.BASE_URL}/activities/{activity_id}",
            headers=self._headers()
        )
        return response.json()
    
    def get_activity_streams(
        self, 
        activity_id: int,
        keys: list[str] = ['time', 'heartrate', 'watts', 'velocity_smooth']
    ) -> dict:
        """
        Busca streams (dados segundo a segundo) de uma atividade.
        Útil para cálculo preciso de Normalized Power.
        
        Keys disponíveis:
        - time, distance, latlng, altitude
        - velocity_smooth, heartrate, cadence, watts, temp
        """
        response = requests.get(
            f"{self.BASE_URL}/activities/{activity_id}/streams",
            headers=self._headers(),
            params={
                'keys': ','.join(keys),
                'key_by_type': True
            }
        )
        return response.json()
    
    def sync_activities(
        self, 
        db_session,
        tss_calculator,
        days_back: int = 7
    ) -> list[dict]:
        """
        Sincroniza atividades dos últimos N dias.
        Calcula TSS e salva no banco.
        """
        after = datetime.now() - timedelta(days=days_back)
        activities = self.get_activities(after=after)
        
        synced = []
        
        for act in activities:
            # Verifica se já existe
            existing = db_session.query(Activity).filter_by(
                strava_id=act['id']
            ).first()
            
            if existing:
                continue
            
            # Calcula TSS
            tss = tss_calculator.calc_tss(act)
            
            # Mapeia tipo de esporte
            sport_map = {
                'Ride': 'bike', 'VirtualRide': 'bike',
                'Run': 'run', 'VirtualRun': 'run',
                'Swim': 'swim'
            }
            sport_type = sport_map.get(act.get('sport_type'), 'other')
            
            # Calcula pace baseado no tipo
            avg_pace_100m = None
            avg_pace_km = None
            
            if sport_type == 'swim' and act.get('distance'):
                avg_pace_100m = int((act['moving_time'] / act['distance']) * 100)
            elif sport_type == 'run' and act.get('distance'):
                avg_pace_km = int((act['moving_time'] / act['distance']) * 1000)
            
            # Cria registro
            new_activity = Activity(
                strava_id=act['id'],
                sport_type=sport_type,
                name=act.get('name'),
                duration_seconds=act.get('elapsed_time'),
                moving_time_seconds=act.get('moving_time'),
                distance_meters=act.get('distance'),
                avg_hr=act.get('average_heartrate'),
                max_hr=act.get('max_heartrate'),
                avg_watts=act.get('average_watts'),
                weighted_avg_watts=act.get('weighted_average_watts'),
                avg_pace_sec_per_100m=avg_pace_100m,
                avg_pace_sec_per_km=avg_pace_km,
                tss=tss,
                intensity_factor=act.get('weighted_average_watts', 0) / tss_calculator.ftp if tss_calculator.ftp else None,
                activity_date=datetime.fromisoformat(act['start_date_local'].replace('Z', '')).date()
            )
            
            db_session.add(new_activity)
            synced.append(new_activity)
        
        db_session.commit()
        return synced
```

---

## 4. API Endpoints (FastAPI)

```python
# api/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from typing import Optional
import os

app = FastAPI(title="MyCoach API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Schemas ====================
class AthleteConfig(BaseModel):
    weight_kg: float = 78.0
    ftp_watts: int = 200
    css_pace_sec: int = 110
    run_threshold_pace_sec: int = 300
    fc_max: int = 185

class MealInput(BaseModel):
    date: date
    meal_type: str
    time: str
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    notes: Optional[str] = None

class DailyMetricsResponse(BaseModel):
    date: date
    daily_tss: float
    ctl: float
    atl: float
    tsb: float
    calories_consumed: Optional[int]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    weight_kg: Optional[float]

# ==================== Endpoints ====================

@app.get("/")
async def root():
    return {"app": "MyCoach", "version": "1.0.0"}

# ---------- Strava ----------
@app.get("/strava/auth")
async def strava_auth_url():
    """Retorna URL para autenticação Strava"""
    client = get_strava_client()
    redirect_uri = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:3000/strava/callback")
    return {"url": client.get_auth_url(redirect_uri)}

@app.get("/strava/callback")
async def strava_callback(code: str):
    """Callback do OAuth Strava"""
    client = get_strava_client()
    tokens = client.exchange_token(code)
    # Salvar tokens no banco
    save_strava_tokens(tokens)
    return {"status": "connected", "athlete_id": tokens.get('athlete', {}).get('id')}

@app.post("/strava/sync")
async def sync_strava(days_back: int = 7):
    """Sincroniza atividades do Strava"""
    client = get_strava_client()
    load_strava_tokens(client)
    
    calculator = TSSCalculator(get_athlete_config())
    synced = client.sync_activities(get_db(), calculator, days_back)
    
    # Recalcula métricas diárias
    recalculate_daily_metrics()
    
    return {"synced_activities": len(synced)}

# ---------- Atividades ----------
@app.get("/activities")
async def list_activities(
    sport_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = 50
):
    """Lista atividades com filtros"""
    query = Activity.query
    
    if sport_type:
        query = query.filter_by(sport_type=sport_type)
    if from_date:
        query = query.filter(Activity.activity_date >= from_date)
    if to_date:
        query = query.filter(Activity.activity_date <= to_date)
    
    activities = query.order_by(Activity.activity_date.desc()).limit(limit).all()
    return activities

@app.get("/activities/{activity_id}")
async def get_activity(activity_id: int):
    """Detalhes de uma atividade"""
    activity = Activity.query.get(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

# ---------- Métricas (PMC) ----------
@app.get("/metrics/daily")
async def get_daily_metrics(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """Retorna métricas diárias (TSS, CTL, ATL, TSB)"""
    if not from_date:
        from_date = date.today() - timedelta(days=90)
    if not to_date:
        to_date = date.today()
    
    metrics = DailyMetrics.query.filter(
        DailyMetrics.date >= from_date,
        DailyMetrics.date <= to_date
    ).order_by(DailyMetrics.date).all()
    
    return metrics

@app.get("/metrics/current")
async def get_current_form():
    """Retorna forma atual (CTL, ATL, TSB de hoje)"""
    today = DailyMetrics.query.filter_by(date=date.today()).first()
    
    if not today:
        # Calcula baseado no último registro
        last = DailyMetrics.query.order_by(DailyMetrics.date.desc()).first()
        if last:
            return {
                "date": date.today(),
                "ctl": last.ctl,
                "atl": last.atl,
                "tsb": last.ctl - last.atl,
                "status": "projected"
            }
        return {"date": date.today(), "ctl": 0, "atl": 0, "tsb": 0, "status": "no_data"}
    
    return {
        "date": today.date,
        "ctl": today.ctl,
        "atl": today.atl,
        "tsb": today.tsb,
        "status": "actual"
    }

@app.get("/metrics/projection")
async def project_taper(target_date: date):
    """Projeta forma até a data alvo (ex: dia da prova)"""
    current = get_current_form()
    days_to_target = (target_date - date.today()).days
    
    if days_to_target <= 0:
        raise HTTPException(status_code=400, detail="Target date must be in the future")
    
    pmc = PMCCalculator(current['ctl'], current['atl'])
    projection = pmc.project_taper(current['ctl'], current['atl'], days_to_target)
    
    return {
        "current": current,
        "target_date": target_date,
        "projection": projection,
        "race_day_tsb": projection[-1]['tsb'] if projection else None
    }

# ---------- Nutrição ----------
@app.post("/meals")
async def add_meal(meal: MealInput):
    """Adiciona refeição"""
    new_meal = Meal(**meal.dict())
    db.add(new_meal)
    db.commit()
    
    # Atualiza totais do dia
    update_daily_nutrition(meal.date)
    
    return new_meal

@app.get("/meals/{date_str}")
async def get_meals_for_date(date_str: str):
    """Retorna refeições de um dia específico"""
    target_date = date.fromisoformat(date_str)
    meals = Meal.query.filter_by(date=target_date).order_by(Meal.time).all()
    
    totals = {
        "calories": sum(m.calories for m in meals),
        "protein_g": sum(m.protein_g for m in meals),
        "carbs_g": sum(m.carbs_g for m in meals),
        "fat_g": sum(m.fat_g for m in meals)
    }
    
    return {"date": target_date, "meals": meals, "totals": totals}

@app.get("/nutrition/scenarios")
async def get_nutrition_scenarios():
    """Retorna cenários de nutrição configurados"""
    return NutritionScenario.query.all()

@app.get("/nutrition/scenario/{scenario_code}")
async def get_scenario_detail(scenario_code: str):
    """Detalhes de um cenário específico"""
    scenario = NutritionScenario.query.filter_by(scenario_code=scenario_code.upper()).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

# ---------- Plano de Treino ----------
@app.get("/plan/current-week")
async def get_current_week_plan():
    """Retorna plano da semana atual"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    plan = TrainingPlan.query.filter(
        TrainingPlan.start_date <= today,
        TrainingPlan.end_date >= today
    ).first()
    
    if not plan:
        return {"message": "No plan for current week"}
    
    sessions = PlannedSession.query.filter_by(plan_id=plan.id).order_by(PlannedSession.day_of_week).all()
    
    # Associa com atividades realizadas
    for session in sessions:
        session_date = week_start + timedelta(days=session.day_of_week)
        actual = Activity.query.filter(
            Activity.activity_date == session_date,
            Activity.sport_type == session.sport_type
        ).first()
        session.actual_activity = actual
    
    return {
        "week_number": plan.week_number,
        "phase": plan.phase,
        "target_tss": plan.target_tss,
        "sessions": sessions
    }

@app.get("/plan/compliance")
async def get_plan_compliance(weeks_back: int = 4):
    """Calcula aderência ao plano"""
    # Implementar lógica de compliance
    pass

# ---------- Athlete ----------
@app.get("/athlete/config")
async def get_athlete_config():
    """Retorna configurações do atleta"""
    athlete = Athlete.query.first()
    if not athlete:
        return AthleteConfig()
    return athlete

@app.put("/athlete/config")
async def update_athlete_config(config: AthleteConfig):
    """Atualiza configurações do atleta"""
    athlete = Athlete.query.first()
    if not athlete:
        athlete = Athlete()
        db.add(athlete)
    
    for key, value in config.dict().items():
        setattr(athlete, key, value)
    
    athlete.updated_at = datetime.now()
    db.commit()
    
    return athlete

@app.post("/athlete/weight")
async def log_weight(weight_kg: float, date_str: Optional[str] = None):
    """Registra peso"""
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    
    daily = DailyMetrics.query.filter_by(date=target_date).first()
    if not daily:
        daily = DailyMetrics(date=target_date)
        db.add(daily)
    
    daily.weight_kg = weight_kg
    db.commit()
    
    return {"date": target_date, "weight_kg": weight_kg}
```

---

## 5. Módulo de IA (OpenAI Integration)

```python
# ai/coach.py

import openai
from datetime import date, timedelta
from typing import Optional

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

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def _build_context(self, athlete_data: dict, metrics: dict) -> str:
        """Constrói contexto atual para o prompt"""
        return f"""
ESTADO ATUAL ({date.today()}):
- Peso: {metrics.get('weight', 'N/A')}kg
- CTL (Fitness): {metrics.get('ctl', 0):.1f}
- ATL (Fadiga): {metrics.get('atl', 0):.1f}
- TSB (Forma): {metrics.get('tsb', 0):.1f}
- TSS últimos 7 dias: {metrics.get('weekly_tss', 0):.0f}

ÚLTIMAS ATIVIDADES:
{self._format_recent_activities(metrics.get('recent_activities', []))}

NUTRIÇÃO HOJE:
{self._format_nutrition(metrics.get('today_nutrition', {}))}
"""
    
    def _format_recent_activities(self, activities: list) -> str:
        if not activities:
            return "Nenhuma atividade recente"
        
        lines = []
        for act in activities[:5]:
            lines.append(
                f"- {act['date']}: {act['sport_type'].upper()} | "
                f"{act['duration_min']}min | TSS: {act['tss']:.0f}"
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
        conversation_history: list = []
    ) -> str:
        """
        Processa mensagem do usuário e retorna resposta do coach.
        """
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
        
        # Adiciona histórico da conversa
        messages.extend(conversation_history[-10:])  # Últimas 10 mensagens
        
        # Adiciona mensagem atual
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _format_pace(self, seconds: int) -> str:
        """Formata pace em mm:ss"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    async def analyze_week(self, weekly_data: dict) -> dict:
        """
        Análise automática da semana com insights.
        """
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
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um analista de performance esportiva. Responda sempre em JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def _format_weekly_sessions(self, sessions: list) -> str:
        lines = []
        for s in sessions:
            status = "✓" if s.get('completed') else "✗"
            lines.append(
                f"{status} {s['day']}: {s['sport_type']} - {s['name']} | "
                f"Planned: {s['planned_tss']} | Actual: {s.get('actual_tss', 'N/A')}"
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
```

---

## 6. Frontend React (Estrutura de Componentes)

```
src/
├── components/
│   ├── Dashboard/
│   │   ├── PMCChart.jsx          # Gráfico CTL/ATL/TSB
│   │   ├── WeeklyOverview.jsx    # Resumo da semana
│   │   ├── TodayCard.jsx         # Card do dia atual
│   │   └── FormIndicator.jsx     # Indicador de forma
│   │
│   ├── Training/
│   │   ├── WeekPlan.jsx          # Plano semanal
│   │   ├── SessionCard.jsx       # Card de sessão
│   │   ├── ActivityList.jsx      # Lista de atividades
│   │   └── ActivityDetail.jsx    # Detalhes de atividade
│   │
│   ├── Nutrition/
│   │   ├── DayPlan.jsx           # Plano do dia
│   │   ├── MealCard.jsx          # Card de refeição
│   │   ├── MacroProgress.jsx     # Barra de macros
│   │   ├── ScenarioSelector.jsx  # Seletor de cenário
│   │   └── MealLogger.jsx        # Registro de refeição
│   │
│   ├── Metrics/
│   │   ├── WeightTracker.jsx     # Gráfico de peso
│   │   ├── TSSHistory.jsx        # Histórico de TSS
│   │   └── ZoneDistribution.jsx  # Distribuição por zona
│   │
│   ├── AI/
│   │   ├── ChatInterface.jsx     # Interface de chat
│   │   ├── WeeklyAnalysis.jsx    # Análise semanal
│   │   └── CoachTips.jsx         # Dicas do coach
│   │
│   └── Settings/
│       ├── AthleteConfig.jsx     # Config do atleta
│       ├── StravaConnect.jsx     # Conexão Strava
│       └── ThresholdSetup.jsx    # Config de thresholds
│
├── pages/
│   ├── Dashboard.jsx
│   ├── Training.jsx
│   ├── Nutrition.jsx
│   ├── Metrics.jsx
│   ├── Coach.jsx
│   └── Settings.jsx
│
├── hooks/
│   ├── useActivities.js
│   ├── useMetrics.js
│   ├── useNutrition.js
│   └── useAICoach.js
│
├── services/
│   ├── api.js                    # Cliente HTTP
│   ├── strava.js                 # Serviços Strava
│   └── openai.js                 # Serviços IA
│
└── utils/
    ├── formatters.js             # Formatação de dados
    ├── calculations.js           # Cálculos no frontend
    └── constants.js              # Constantes
```

### 6.1 Componente Principal: PMC Chart

```jsx
// components/Dashboard/PMCChart.jsx

import React, { useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';

const PMCChart = ({ data, targetDate }) => {
  const chartData = useMemo(() => {
    return data.map(d => ({
      ...d,
      date: new Date(d.date).toLocaleDateString('pt-BR', { 
        day: '2-digit', 
        month: '2-digit' 
      })
    }));
  }, [data]);

  const currentTSB = data[data.length - 1]?.tsb || 0;
  
  const getTSBStatus = (tsb) => {
    if (tsb > 25) return { text: 'Muito descansado', color: '#22c55e' };
    if (tsb > 10) return { text: 'Fresh - Boa forma', color: '#10b981' };
    if (tsb > -10) return { text: 'Neutro', color: '#f59e0b' };
    if (tsb > -20) return { text: 'Cansado', color: '#f97316' };
    return { text: 'Overreaching', color: '#ef4444' };
  };

  const status = getTSBStatus(currentTSB);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Performance Management Chart</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Forma atual:</span>
          <span 
            className="font-bold px-3 py-1 rounded-full text-white"
            style={{ backgroundColor: status.color }}
          >
            TSB: {currentTSB.toFixed(0)} - {status.text}
          </span>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip 
            formatter={(value, name) => [value.toFixed(1), name]}
            labelFormatter={(label) => `Data: ${label}`}
          />
          <Legend />
          
          {/* Linha de referência TSB = 0 */}
          <ReferenceLine y={0} stroke="#999" strokeDasharray="5 5" />
          
          {/* Zona ideal de TSB para prova (15-25) */}
          <ReferenceLine y={15} stroke="#22c55e" strokeDasharray="3 3" />
          <ReferenceLine y={25} stroke="#22c55e" strokeDasharray="3 3" />
          
          <Line 
            type="monotone" 
            dataKey="ctl" 
            stroke="#3b82f6" 
            name="CTL (Fitness)"
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="atl" 
            stroke="#ef4444" 
            name="ATL (Fadiga)"
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="tsb" 
            stroke="#10b981" 
            name="TSB (Forma)"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div className="p-3 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {data[data.length - 1]?.ctl?.toFixed(0) || 0}
          </div>
          <div className="text-sm text-gray-600">CTL (Fitness)</div>
        </div>
        <div className="p-3 bg-red-50 rounded-lg">
          <div className="text-2xl font-bold text-red-600">
            {data[data.length - 1]?.atl?.toFixed(0) || 0}
          </div>
          <div className="text-sm text-gray-600">ATL (Fadiga)</div>
        </div>
        <div className="p-3 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {currentTSB.toFixed(0)}
          </div>
          <div className="text-sm text-gray-600">TSB (Forma)</div>
        </div>
      </div>
    </div>
  );
};

export default PMCChart;
```

---

## 7. Dados Iniciais (Seeds)

### 7.1 Cenários de Nutrição

```python
# seeds/nutrition_scenarios.py

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
```

---

## 8. Variáveis de Ambiente

```env
# .env

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/mycoach
# ou para SQLite:
# DATABASE_URL=sqlite:///./mycoach.db

# Strava OAuth
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REDIRECT_URI=http://localhost:3000/strava/callback

# OpenAI
OPENAI_API_KEY=sk-your-api-key

# App
SECRET_KEY=your-secret-key-here
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# Atleta (defaults)
DEFAULT_FTP=200
DEFAULT_CSS_PACE=110
DEFAULT_RUN_THRESHOLD=300
DEFAULT_FC_MAX=185
```

---

## 9. Comandos de Deploy

```bash
# Backend (Railway)
railway init
railway add postgresql
railway up

# Frontend (Vercel)
vercel --prod

# Migrations
alembic upgrade head

# Seed data
python -m seeds.run_seeds
```

---

## 10. Checklist de Implementação

### MVP (Semana 1-2)
- [ ] Setup banco de dados e modelos
- [ ] Integração Strava OAuth
- [ ] Sync de atividades
- [ ] Cálculo de TSS por modalidade
- [ ] Cálculo de CTL/ATL/TSB
- [ ] API básica (activities, metrics)
- [ ] Dashboard com PMC Chart

### Fase 2 (Semana 3-4)
- [ ] Módulo de nutrição
- [ ] Cenários A/B/C/D
- [ ] Registro de refeições
- [ ] Tracking de peso
- [ ] Plano de treino semanal

### Fase 3 (Semana 5-6)
- [ ] Integração OpenAI
- [ ] Chat com coach
- [ ] Análise semanal automática
- [ ] Sugestão de cenário nutricional
- [ ] Alertas de overtraining

### Polimento
- [ ] PWA / Mobile responsive
- [ ] Notificações
- [ ] Exportação de dados
- [ ] Backup automático
