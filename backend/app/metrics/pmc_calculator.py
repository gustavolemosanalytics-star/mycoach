"""
PMC Calculator Module

Performance Management Chart calculations:
- CTL (Chronic Training Load) - 42-day exponential moving average (fitness)
- ATL (Acute Training Load) - 7-day exponential moving average (fatigue)
- TSB (Training Stress Balance) - CTL - ATL (form)
"""
from datetime import date, timedelta
from typing import List, Dict


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
    
    def calculate_history(self, daily_tss_list: List[Dict]) -> List[Dict]:
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
    
    def project_taper(
        self, 
        current_ctl: float, 
        current_atl: float, 
        days: int = 14,
        taper_intensity: float = 0.5
    ) -> List[Dict]:
        """
        Projeta CTL/ATL/TSB durante taper com TSS reduzido.
        Útil para planejar a forma no dia da prova.
        
        Args:
            current_ctl: Current CTL value
            current_atl: Current ATL value
            days: Number of days to project
            taper_intensity: How much to reduce TSS (0.5 = 50% of CTL)
        
        Returns:
            List of projected daily values
        """
        projections = []
        ctl = current_ctl
        atl = current_atl
        
        for day in range(1, days + 1):
            # TSS progressivamente menor durante taper
            if day <= 7:
                daily_tss = current_ctl * taper_intensity  # Semana 1: reduced
            else:
                daily_tss = current_ctl * (taper_intensity / 2)  # Semana 2: even more reduced
            
            ctl = ctl + (daily_tss - ctl) / self.CTL_DAYS
            atl = atl + (daily_tss - atl) / self.ATL_DAYS
            tsb = ctl - atl
            
            projections.append({
                'day': day,
                'date': (date.today() + timedelta(days=day)).isoformat(),
                'projected_tss': round(daily_tss, 0),
                'ctl': round(ctl, 1),
                'atl': round(atl, 1),
                'tsb': round(tsb, 1)
            })
        
        return projections
    
    def get_form_status(self, tsb: float) -> Dict:
        """
        Get human-readable form status based on TSB.
        
        Returns:
            Dict with status text and color
        """
        if tsb > 25:
            return {'text': 'Muito descansado', 'color': '#22c55e', 'status': 'very_fresh'}
        if tsb > 10:
            return {'text': 'Fresh - Boa forma', 'color': '#10b981', 'status': 'fresh'}
        if tsb > -10:
            return {'text': 'Neutro', 'color': '#f59e0b', 'status': 'neutral'}
        if tsb > -20:
            return {'text': 'Cansado', 'color': '#f97316', 'status': 'tired'}
        return {'text': 'Overreaching', 'color': '#ef4444', 'status': 'overreaching'}
    
    @staticmethod
    def fill_missing_days(daily_data: List[Dict], start_date: date, end_date: date) -> List[Dict]:
        """
        Fill in missing days with 0 TSS for continuous calculation.
        
        Args:
            daily_data: List of {'date': date, 'tss': float}
            start_date: Start of period
            end_date: End of period
        
        Returns:
            Complete list with all days in range
        """
        # Create dict for quick lookup
        data_by_date = {d['date']: d['tss'] for d in daily_data}
        
        result = []
        current = start_date
        while current <= end_date:
            result.append({
                'date': current,
                'tss': data_by_date.get(current, 0)
            })
            current += timedelta(days=1)
        
        return result
