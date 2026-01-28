import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.user import User
from app.models.workout import Workout

settings = get_settings()

STRAVA_API_URL = "https://www.strava.com/api/v3"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"


async def refresh_strava_token(user: User, db: Session) -> str:
    """Refresh Strava access token if expired."""
    if user.strava_token_expires_at and user.strava_token_expires_at > datetime.utcnow():
        return user.strava_access_token
    
    async with httpx.AsyncClient() as client:
        response = await client.post(STRAVA_TOKEN_URL, data={
            "client_id": settings.strava_client_id,
            "client_secret": settings.strava_client_secret,
            "refresh_token": user.strava_refresh_token,
            "grant_type": "refresh_token"
        })
    
    if response.status_code != 200:
        raise Exception("Failed to refresh Strava token")
    
    token_data = response.json()
    user.strava_access_token = token_data["access_token"]
    user.strava_refresh_token = token_data["refresh_token"]
    user.strava_token_expires_at = datetime.fromtimestamp(token_data["expires_at"])
    db.commit()
    
    return user.strava_access_token


async def sync_strava_activities(user: User, db: Session, days: int = 30) -> int:
    """Sync activities from Strava."""
    access_token = await refresh_strava_token(user, db)
    
    # Get activities from the last N days
    after_timestamp = int((datetime.utcnow() - timedelta(days=days)).timestamp())
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{STRAVA_API_URL}/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"after": after_timestamp, "per_page": 100}
        )
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Strava activities: {response.text}")
    
    activities = response.json()
    synced_count = 0
    
    for activity in activities:
        # Check if already synced
        existing = db.query(Workout).filter(
            Workout.external_id == str(activity["id"]),
            Workout.source == "strava"
        ).first()
        
        if existing:
            continue
        
        # Map Strava activity to our workout model
        workout = Workout(
            user_id=user.id,
            source="strava",
            external_id=str(activity["id"]),
            name=activity.get("name", "Strava Activity"),
            sport_type=map_strava_sport(activity.get("sport_type", activity.get("type", "Run"))),
            start_date=datetime.fromisoformat(activity["start_date"].replace("Z", "+00:00")),
            elapsed_time=activity.get("elapsed_time", 0),
            moving_time=activity.get("moving_time"),
            distance=activity.get("distance"),
            avg_heart_rate=activity.get("average_heartrate"),
            max_heart_rate=activity.get("max_heartrate"),
            elevation_gain=activity.get("total_elevation_gain"),
            calories=activity.get("calories") or estimate_calories(activity),
            avg_cadence=activity.get("average_cadence"),
            avg_power=activity.get("average_watts"),
            max_power=activity.get("max_watts"),
            polyline=activity.get("map", {}).get("summary_polyline"),
            start_lat=activity.get("start_latlng", [None, None])[0],
            start_lng=activity.get("start_latlng", [None, None])[1],
            raw_data=activity
        )
        
        # Calculate pace
        if workout.distance and workout.moving_time:
            workout.avg_pace = workout.moving_time / (workout.distance / 1000)
        
        # Generate highlights
        workout.highlights = generate_highlights(workout, activity)
        
        db.add(workout)
        synced_count += 1
    
    db.commit()
    
    # Check for achievements after sync
    from app.services.gamification import check_achievements
    for workout in db.query(Workout).filter(
        Workout.user_id == user.id
    ).order_by(Workout.start_date.desc()).limit(synced_count).all():
        check_achievements(user.id, db, workout)
    
    return synced_count


def map_strava_sport(strava_type: str) -> str:
    """Map Strava sport type to our enum."""
    type_map = {
        "Run": "run",
        "Ride": "ride",
        "Swim": "swim",
        "Walk": "walk",
        "Hike": "walk",
        "WeightTraining": "strength",
        "Yoga": "yoga",
        "VirtualRun": "run",
        "VirtualRide": "ride",
        "TrailRun": "run",
        "GravelRide": "ride",
        "MountainBikeRide": "ride"
    }
    return type_map.get(strava_type, "other")


def estimate_calories(activity: dict) -> int:
    """Estimate calories if not provided by Strava."""
    distance = activity.get("distance", 0) / 1000  # km
    elapsed_time = activity.get("elapsed_time", 0) / 60  # minutes
    sport = activity.get("type", "Run")
    
    # MET values (rough estimates)
    met_values = {
        "Run": 10,
        "Ride": 8,
        "Swim": 8,
        "Walk": 3.5,
        "WeightTraining": 6
    }
    
    met = met_values.get(sport, 5)
    # Assume 70kg weight, calories = MET * weight * time(hours)
    calories = met * 70 * (elapsed_time / 60)
    
    return int(calories)


def generate_highlights(workout: Workout, raw_data: dict) -> list:
    """Generate automatic highlights for a workout."""
    highlights = []
    
    # Distance highlight
    if workout.distance:
        km = workout.distance / 1000
        if km >= 42.195:
            highlights.append({"type": "milestone", "message": "🏅 Marathon distance completed!", "icon": "🏅"})
        elif km >= 21.1:
            highlights.append({"type": "milestone", "message": "🎖️ Half marathon distance!", "icon": "🎖️"})
        elif km >= 10:
            highlights.append({"type": "distance", "message": f"🏃 Great {km:.1f}km workout!", "icon": "🏃"})
    
    # Pace highlight (for runs)
    if workout.sport_type == "run" and workout.avg_pace:
        pace_min = workout.avg_pace / 60
        if pace_min < 4:
            highlights.append({"type": "pace", "message": f"⚡ Elite pace: {int(workout.avg_pace//60)}:{int(workout.avg_pace%60):02d}/km", "icon": "⚡"})
        elif pace_min < 5:
            highlights.append({"type": "pace", "message": f"🔥 Fast pace: {int(workout.avg_pace//60)}:{int(workout.avg_pace%60):02d}/km", "icon": "🔥"})
    
    # Heart rate zone (if available)
    if workout.avg_heart_rate and workout.max_heart_rate:
        hr_percentage = (workout.avg_heart_rate / workout.max_heart_rate) * 100
        if hr_percentage >= 85:
            highlights.append({"type": "intensity", "message": "💪 High intensity training!", "icon": "💪"})
        elif hr_percentage <= 70:
            highlights.append({"type": "intensity", "message": "🧘 Nice recovery/zone 2 session", "icon": "🧘"})
    
    # Elevation
    if workout.elevation_gain and workout.elevation_gain >= 500:
        highlights.append({"type": "elevation", "message": f"⛰️ Climbed {int(workout.elevation_gain)}m!", "icon": "⛰️"})
    
    # Kudos from Strava
    kudos = raw_data.get("kudos_count", 0)
    if kudos >= 10:
        highlights.append({"type": "social", "message": f"👏 {kudos} kudos received!", "icon": "👏"})
    
    return highlights
