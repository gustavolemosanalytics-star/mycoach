"""
Strava Client - OAuth and API integration per specification.
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional, List
import os

from app.config import get_settings

settings = get_settings()


class StravaClient:
    """
    Cliente para Strava API v3
    """
    
    BASE_URL = "https://www.strava.com/api/v3"
    AUTH_URL = "https://www.strava.com/oauth/token"
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or settings.strava_client_id
        self.client_secret = client_secret or settings.strava_client_secret
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
    
    # ==================== OAuth ====================
    def get_auth_url(self, redirect_uri: str = None) -> str:
        """Gera URL para autorização OAuth"""
        redirect = redirect_uri or settings.strava_redirect_uri
        return (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect}"
            f"&scope=read,activity:read_all"
        )
    
    def exchange_token(self, code: str) -> dict:
        """Troca authorization code por tokens"""
        with httpx.Client() as client:
            response = client.post(self.AUTH_URL, data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            })
            response.raise_for_status()
            data = response.json()
        
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expires_at = data['expires_at']
        
        return data
    
    def refresh_access_token(self) -> dict:
        """Renova access token usando refresh token"""
        with httpx.Client() as client:
            response = client.post(self.AUTH_URL, data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            })
            response.raise_for_status()
            data = response.json()
        
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expires_at = data['expires_at']
        
        return data
    
    def set_tokens(self, access_token: str, refresh_token: str, expires_at: int):
        """Set tokens from stored values"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
    
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
    ) -> List[dict]:
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
        
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/athlete/activities",
                headers=self._headers(),
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
        
        return response.json()
    
    def get_activity_detail(self, activity_id: int) -> dict:
        """Busca detalhes de uma atividade específica"""
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/activities/{activity_id}",
                headers=self._headers(),
                timeout=30.0
            )
            response.raise_for_status()
        return response.json()
    
    def get_activity_streams(
        self, 
        activity_id: int,
        keys: List[str] = ['time', 'heartrate', 'watts', 'velocity_smooth']
    ) -> dict:
        """
        Busca streams (dados segundo a segundo) de uma atividade.
        Útil para cálculo preciso de Normalized Power.
        
        Keys disponíveis:
        - time, distance, latlng, altitude
        - velocity_smooth, heartrate, cadence, watts, temp
        """
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/activities/{activity_id}/streams",
                headers=self._headers(),
                params={
                    'keys': ','.join(keys),
                    'key_by_type': True
                },
                timeout=30.0
            )
            response.raise_for_status()
        return response.json()
    
    def get_athlete(self) -> dict:
        """Get authenticated athlete info"""
        with httpx.Client() as client:
            response = client.get(
                f"{self.BASE_URL}/athlete",
                headers=self._headers(),
                timeout=30.0
            )
            response.raise_for_status()
        return response.json()


# Singleton instance
strava_client = StravaClient()
