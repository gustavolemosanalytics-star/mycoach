"""
TSS Calculator Module

Calculates Training Stress Score (TSS) for different sports:
- Bike: Power-based TSS using Normalized Power and FTP
- Run: rTSS based on pace relative to threshold pace
- Swim: sTSS based on pace relative to CSS (Critical Swim Speed)
- HR: Fallback hrTSS when no power/pace data available
"""
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
    
    def get_intensity_factor(self, activity: dict) -> Optional[float]:
        """
        Calculate intensity factor for an activity.
        """
        sport = activity.get('sport_type', '').lower()
        
        if sport in ['ride', 'bike', 'cycling', 'virtualride']:
            np = activity.get('weighted_average_watts') or activity.get('average_watts')
            if np and self.ftp:
                return round(np / self.ftp, 3)
        
        elif sport in ['run', 'running', 'virtualrun']:
            distance = activity.get('distance', 0)
            moving_time = activity.get('moving_time', 0)
            if distance and moving_time:
                pace_sec_per_km = (moving_time / distance) * 1000
                return round(self.run_threshold_pace / pace_sec_per_km, 3)
        
        elif sport in ['swim', 'swimming']:
            distance = activity.get('distance', 0)
            moving_time = activity.get('moving_time', 0)
            if distance and moving_time:
                pace_sec_per_100m = (moving_time / distance) * 100
                return round(self.css_pace / pace_sec_per_100m, 3)
        
        return None
