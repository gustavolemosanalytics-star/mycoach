from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import httpx
from app.database import get_db
from app.config import get_settings
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter()
settings = get_settings()

# Strava OAuth URLs
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_URL = "https://www.strava.com/api/v3"


@router.get("/strava/connect")
async def strava_connect(current_user: User = Depends(get_current_user)):
    """Get Strava OAuth authorization URL."""
    if not settings.strava_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Strava integration not configured"
        )
    
    params = {
        "client_id": settings.strava_client_id,
        "redirect_uri": settings.strava_redirect_uri,
        "response_type": "code",
        "scope": "read,activity:read_all,profile:read_all",
        "state": str(current_user.id)  # Pass user ID in state
    }
    
    auth_url = f"{STRAVA_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    return {"authorization_url": auth_url}


@router.get("/strava/callback")
async def strava_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Strava OAuth callback."""
    user_id = int(state)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": settings.strava_client_id,
            "client_secret": settings.strava_client_secret,
            "code": code,
            "grant_type": "authorization_code"
        })
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for tokens"
        )
    
    token_data = response.json()
    
    # Save tokens to user
    user.strava_athlete_id = token_data.get("athlete", {}).get("id")
    user.strava_access_token = token_data.get("access_token")
    user.strava_refresh_token = token_data.get("refresh_token")
    user.strava_token_expires_at = datetime.fromtimestamp(token_data.get("expires_at", 0))
    
    db.commit()
    
    # Redirect to frontend
    return RedirectResponse(url=f"{settings.frontend_url}/settings?strava=connected")


@router.delete("/strava/disconnect")
async def strava_disconnect(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Strava account."""
    current_user.strava_athlete_id = None
    current_user.strava_access_token = None
    current_user.strava_refresh_token = None
    current_user.strava_token_expires_at = None
    
    db.commit()
    
    return {"message": "Strava disconnected successfully"}


@router.post("/strava/sync")
async def strava_sync(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync activities from Strava."""
    if not current_user.strava_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Strava not connected"
        )
    
    from app.services.strava_service import sync_strava_activities
    
    try:
        synced_count = await sync_strava_activities(current_user, db)
        current_user.last_sync_at = datetime.utcnow()
        db.commit()
        
        return {"message": f"Synced {synced_count} activities from Strava"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync: {str(e)}"
        )


# Garmin endpoints (placeholder - requires developer program approval)
@router.get("/garmin/connect")
async def garmin_connect(current_user: User = Depends(get_current_user)):
    """Get Garmin OAuth authorization URL."""
    if not settings.garmin_client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Garmin integration not configured. Apply at developer.garmin.com"
        )
    
    # Garmin uses OAuth 2.0 with PKCE
    # Implementation similar to Strava but with Garmin's endpoints
    return {"message": "Garmin integration requires developer program approval"}


@router.get("/status")
async def integration_status(
    current_user: User = Depends(get_current_user)
):
    """Get status of all integrations."""
    return {
        "strava": {
            "connected": current_user.strava_access_token is not None,
            "athlete_id": current_user.strava_athlete_id,
            "last_sync": current_user.last_sync_at
        },
        "garmin": {
            "connected": current_user.garmin_access_token is not None,
            "user_id": current_user.garmin_user_id
        }
    }
