"""
FIT File Parser — formato primário do Garmin.
Extrai TODAS as métricas: session, records (1Hz), laps, running dynamics, swim.
"""
import io
import math
from datetime import datetime, timezone
from typing import Any

from fitparse import FitFile


SEMICIRCLE_TO_DEGREES = 180.0 / (2**31)
MAX_STREAM_POINTS = 3600

# Mapping FIT sport enum to our sport types
FIT_SPORT_MAP = {
    "running": "run",
    "cycling": "bike",
    "swimming": "swim",
    "training": "strength",
    "multisport": "brick",
    "generic": "run",
    "transition": "run",
    "walking": "run",
    "trail_running": "run",
    "virtual_ride": "bike",
    "e_biking": "bike",
    "indoor_cycling": "bike",
    "open_water_swimming": "swim",
    "lap_swimming": "swim",
}


def _get_field(message, field_name, default=None):
    """Safely get a field value from a FIT message."""
    field = message.get(field_name)
    if field is not None:
        return field.value if hasattr(field, "value") else field
    return default


def _get_value(message, field_name, default=None):
    """Get raw value from FIT message fields dict."""
    for field in message.fields:
        if field.name == field_name:
            return field.value if field.value is not None else default
    return default


def parse_fit(file_bytes: bytes) -> dict[str, Any]:
    """
    Parse a .FIT file and return a standardized activity dict.

    Returns dict matching Activity model fields.
    """
    fitfile = FitFile(io.BytesIO(file_bytes))

    session_data = {}
    records = []
    laps_raw = []
    device_info = {}

    for message in fitfile.get_messages():
        msg_type = message.name

        if msg_type == "session":
            session_data = {f.name: f.value for f in message.fields if f.value is not None}

        elif msg_type == "record":
            record = {f.name: f.value for f in message.fields if f.value is not None}
            records.append(record)

        elif msg_type == "lap":
            lap = {f.name: f.value for f in message.fields if f.value is not None}
            laps_raw.append(lap)

        elif msg_type == "device_info":
            device_info = {f.name: f.value for f in message.fields if f.value is not None}

    # Determine sport
    raw_sport = str(session_data.get("sport", "generic")).lower()
    sport = FIT_SPORT_MAP.get(raw_sport, "run")

    # Extract start time
    start_time = session_data.get("start_time")
    if start_time and not isinstance(start_time, datetime):
        start_time = datetime.now(timezone.utc)

    # Basic metrics from session
    total_elapsed = int(session_data.get("total_elapsed_time", 0))
    total_timer = int(session_data.get("total_timer_time", 0))
    total_distance = float(session_data.get("total_distance", 0))

    # Speed / Pace
    avg_speed_ms = session_data.get("avg_speed")
    max_speed_ms = session_data.get("max_speed")
    avg_speed_kmh = round(avg_speed_ms * 3.6, 2) if avg_speed_ms else None
    max_speed_kmh = round(max_speed_ms * 3.6, 2) if max_speed_ms else None

    avg_pace_min_km = None
    if avg_speed_ms and avg_speed_ms > 0:
        avg_pace_min_km = round((1000 / avg_speed_ms) / 60, 2)

    max_pace_min_km = None
    if max_speed_ms and max_speed_ms > 0:
        max_pace_min_km = round((1000 / max_speed_ms) / 60, 2)

    # Heart Rate
    avg_hr = _safe_int(session_data.get("avg_heart_rate"))
    max_hr = _safe_int(session_data.get("max_heart_rate"))
    min_hr = _safe_int(session_data.get("min_heart_rate"))

    # Cadence
    avg_cadence = _safe_int(session_data.get("avg_cadence"))
    max_cadence = _safe_int(session_data.get("max_cadence"))
    # Running cadence is per-foot, multiply by 2 for steps per minute
    if sport == "run" and avg_cadence:
        avg_cadence *= 2
    if sport == "run" and max_cadence:
        max_cadence *= 2

    # Power (bike)
    avg_power = _safe_int(session_data.get("avg_power"))
    max_power = _safe_int(session_data.get("max_power"))

    # Elevation
    total_ascent = session_data.get("total_ascent")
    total_descent = session_data.get("total_descent")

    # Temperature
    avg_temp = session_data.get("avg_temperature")
    max_temp = session_data.get("max_temperature")

    # Calories
    calories = _safe_int(session_data.get("total_calories"))

    # Training Effect
    te_aerobic = session_data.get("total_training_effect")
    te_anaerobic = session_data.get("total_anaerobic_training_effect")

    # Running Dynamics
    avg_gct = _safe_int(session_data.get("avg_stance_time"))
    avg_stride = session_data.get("avg_step_length")
    avg_stride_m = round(avg_stride / 1000, 3) if avg_stride else None
    avg_vo = session_data.get("avg_vertical_oscillation")
    avg_vo_mm = round(avg_vo, 1) if avg_vo else None
    avg_vr = session_data.get("avg_vertical_ratio")
    avg_gcb = session_data.get("avg_stance_time_balance")

    # Swim Metrics
    avg_stroke_rate = session_data.get("avg_stroke_count")
    pool_length = _safe_int(session_data.get("pool_length"))
    if pool_length:
        pool_length = int(pool_length / 100) if pool_length > 100 else pool_length
    total_lengths = _safe_int(session_data.get("num_lengths"))
    swolf = session_data.get("avg_swolf")

    # Calculate NP from records if we have power data
    normalized_power = _safe_int(session_data.get("normalized_power"))
    power_values = [r.get("power") for r in records if r.get("power") is not None]
    if not normalized_power and power_values and len(power_values) > 30:
        normalized_power = _calc_normalized_power(power_values)

    # IF and VI
    ftp = None  # Will be set from user profile in the route
    intensity_factor_val = None
    variability_index_val = None
    if normalized_power and avg_power and avg_power > 0:
        variability_index_val = round(normalized_power / avg_power, 3)

    # Build streams (sampled to MAX_STREAM_POINTS)
    hr_stream, pace_stream, power_stream_data, cadence_stream = [], [], [], []
    altitude_stream, gps_stream = [], []

    if records:
        step = max(1, len(records) // MAX_STREAM_POINTS)
        first_ts = records[0].get("timestamp")

        for i in range(0, len(records), step):
            r = records[i]
            ts = r.get("timestamp")
            elapsed = int((ts - first_ts).total_seconds()) if ts and first_ts else i

            if r.get("heart_rate"):
                hr_stream.append({"t": elapsed, "hr": r["heart_rate"]})

            speed = r.get("speed") or r.get("enhanced_speed")
            if speed and speed > 0:
                pace = round((1000 / speed) / 60, 2)
                pace_stream.append({"t": elapsed, "pace": pace})

            if r.get("power"):
                power_stream_data.append({"t": elapsed, "power": r["power"]})

            cad = r.get("cadence")
            if cad:
                if sport == "run":
                    cad *= 2
                cadence_stream.append({"t": elapsed, "cadence": cad})

            alt = r.get("altitude") or r.get("enhanced_altitude")
            if alt is not None:
                altitude_stream.append({"t": elapsed, "alt": round(alt, 1)})

            lat = r.get("position_lat")
            lon = r.get("position_long")
            if lat is not None and lon is not None:
                gps_stream.append({
                    "t": elapsed,
                    "lat": round(lat * SEMICIRCLE_TO_DEGREES, 6),
                    "lon": round(lon * SEMICIRCLE_TO_DEGREES, 6),
                })

    # Build laps
    laps_data = []
    for i, lap in enumerate(laps_raw):
        laps_data.append({
            "lap": i + 1,
            "distance_m": round(lap.get("total_distance", 0), 1),
            "duration_s": round(lap.get("total_elapsed_time", 0), 1),
            "avg_hr": _safe_int(lap.get("avg_heart_rate")),
            "max_hr": _safe_int(lap.get("max_heart_rate")),
            "avg_speed_kmh": round(lap.get("avg_speed", 0) * 3.6, 2) if lap.get("avg_speed") else None,
            "avg_cadence": _safe_int(lap.get("avg_cadence")),
            "avg_power": _safe_int(lap.get("avg_power")),
            "total_ascent": lap.get("total_ascent"),
            "calories": _safe_int(lap.get("total_calories")),
        })

    # Generate title
    dist_km = total_distance / 1000
    if dist_km > 0:
        title = f"{sport.capitalize()} de {dist_km:.2f}km"
    else:
        duration_min = total_timer // 60
        title = f"{sport.capitalize()} de {duration_min}min"

    return {
        "sport": sport,
        "title": title,
        "start_time": start_time,
        "end_time": start_time,
        "source_format": "fit",
        "total_elapsed_seconds": total_elapsed,
        "total_timer_seconds": total_timer,
        "total_moving_seconds": total_timer,
        "total_distance_meters": total_distance,
        "avg_pace_min_km": avg_pace_min_km,
        "max_pace_min_km": max_pace_min_km,
        "avg_speed_kmh": avg_speed_kmh,
        "max_speed_kmh": max_speed_kmh,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "min_hr": min_hr,
        "avg_cadence": avg_cadence,
        "max_cadence": max_cadence,
        "avg_power": avg_power,
        "max_power": max_power,
        "normalized_power": normalized_power,
        "intensity_factor": intensity_factor_val,
        "variability_index": variability_index_val,
        "total_ascent_m": total_ascent,
        "total_descent_m": total_descent,
        "avg_temperature_c": avg_temp,
        "max_temperature_c": max_temp,
        "calories": calories,
        "training_effect_aerobic": te_aerobic,
        "training_effect_anaerobic": te_anaerobic,
        "avg_ground_contact_time_ms": avg_gct,
        "avg_stride_length_m": avg_stride_m,
        "avg_vertical_oscillation_mm": avg_vo_mm,
        "avg_vertical_ratio_pct": avg_vr,
        "avg_ground_contact_balance_pct": avg_gcb,
        "avg_stroke_rate": avg_stroke_rate,
        "pool_length_m": pool_length,
        "total_lengths": total_lengths,
        "swolf": swolf,
        "hr_stream": hr_stream or None,
        "pace_stream": pace_stream or None,
        "power_stream": power_stream_data or None,
        "cadence_stream": cadence_stream or None,
        "altitude_stream": altitude_stream or None,
        "gps_stream": gps_stream or None,
        "laps_data": laps_data or None,
    }


def _safe_int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _calc_normalized_power(power_values: list[int | float]) -> int | None:
    """Calculate Normalized Power from 30-second rolling average."""
    if len(power_values) < 30:
        return None

    # 30-second rolling average
    rolling = []
    for i in range(len(power_values) - 29):
        window = power_values[i : i + 30]
        rolling.append(sum(window) / 30)

    # Raise to 4th power, average, then 4th root
    fourth_power = [p**4 for p in rolling]
    avg_fourth = sum(fourth_power) / len(fourth_power)
    np_value = avg_fourth**0.25

    return int(round(np_value))
