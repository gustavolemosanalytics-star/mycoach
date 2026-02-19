"""
TCX File Parser — fallback para quando .FIT não está disponível.
Extrai: HR, cadência, laps, calorias, GPS, elevação.
Não tem: running dynamics, swim metrics detalhados, training effect.
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

NS = {"ns": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}
MAX_STREAM_POINTS = 3600

TCX_SPORT_MAP = {
    "running": "run",
    "biking": "bike",
    "swimming": "swim",
    "other": "run",
}


def parse_tcx(file_bytes: bytes) -> dict[str, Any]:
    """Parse a .TCX file and return a standardized activity dict."""
    root = ET.fromstring(file_bytes)

    activity = root.find(".//ns:Activity", NS)
    if activity is None:
        raise ValueError("Nenhuma atividade encontrada no arquivo TCX")

    raw_sport = (activity.get("Sport") or "Other").lower()
    sport = TCX_SPORT_MAP.get(raw_sport, "run")

    id_tag = activity.find("ns:Id", NS)
    start_time_str = id_tag.text if id_tag is not None else None
    start_time = _parse_time(start_time_str) if start_time_str else datetime.utcnow()

    total_time = 0.0
    total_distance = 0.0
    total_calories = 0
    hr_values = []
    all_trackpoints = []
    laps_data = []

    laps = activity.findall("ns:Lap", NS)

    for i, lap in enumerate(laps):
        lap_time = _float(lap, "ns:TotalTimeSeconds")
        lap_dist = _float(lap, "ns:DistanceMeters")
        lap_cal = _int(lap, "ns:Calories")

        total_time += lap_time
        total_distance += lap_dist
        total_calories += lap_cal

        lap_hr_values = []
        track = lap.find("ns:Track", NS)
        if track is not None:
            for pt in track.findall("ns:Trackpoint", NS):
                tp = _parse_trackpoint(pt)
                if tp:
                    all_trackpoints.append(tp)
                    if tp.get("hr"):
                        hr_values.append(tp["hr"])
                        lap_hr_values.append(tp["hr"])

        laps_data.append({
            "lap": i + 1,
            "distance_m": round(lap_dist, 1),
            "duration_s": round(lap_time, 1),
            "avg_hr": int(sum(lap_hr_values) / len(lap_hr_values)) if lap_hr_values else None,
            "max_hr": max(lap_hr_values) if lap_hr_values else None,
            "calories": lap_cal,
        })

    avg_hr = int(sum(hr_values) / len(hr_values)) if hr_values else None
    max_hr = max(hr_values) if hr_values else None
    min_hr = min(hr_values) if hr_values else None

    # Speed / Pace
    avg_speed_kmh = None
    avg_pace_min_km = None
    if total_time > 0 and total_distance > 0:
        avg_speed_ms = total_distance / total_time
        avg_speed_kmh = round(avg_speed_ms * 3.6, 2)
        avg_pace_min_km = round((1000 / avg_speed_ms) / 60, 2)

    # Build streams
    hr_stream = []
    altitude_stream = []
    gps_stream = []
    pace_stream = []

    if all_trackpoints:
        step = max(1, len(all_trackpoints) // MAX_STREAM_POINTS)
        first_ts = all_trackpoints[0].get("time_dt")

        prev_dist = 0
        prev_time = 0

        for i in range(0, len(all_trackpoints), step):
            tp = all_trackpoints[i]
            ts = tp.get("time_dt")
            elapsed = int((ts - first_ts).total_seconds()) if ts and first_ts else i

            if tp.get("hr"):
                hr_stream.append({"t": elapsed, "hr": tp["hr"]})

            if tp.get("alt") is not None:
                altitude_stream.append({"t": elapsed, "alt": round(tp["alt"], 1)})

            if tp.get("lat") is not None and tp.get("lng") is not None:
                gps_stream.append({
                    "t": elapsed,
                    "lat": tp["lat"],
                    "lon": tp["lng"],
                })

            # Estimate pace from distance deltas
            curr_dist = tp.get("distance") or 0
            if curr_dist > prev_dist and elapsed > prev_time:
                delta_dist = curr_dist - prev_dist
                delta_time = elapsed - prev_time
                if delta_dist > 0:
                    speed = delta_dist / delta_time
                    pace = round((1000 / speed) / 60, 2) if speed > 0 else None
                    if pace and pace < 20:  # Sanity check
                        pace_stream.append({"t": elapsed, "pace": pace})
                prev_dist = curr_dist
                prev_time = elapsed

    # Calculate elevation from altitude stream
    total_ascent = 0.0
    total_descent = 0.0
    if altitude_stream:
        for i in range(1, len(altitude_stream)):
            diff = altitude_stream[i]["alt"] - altitude_stream[i - 1]["alt"]
            if diff > 0:
                total_ascent += diff
            else:
                total_descent += abs(diff)

    # Title
    dist_km = total_distance / 1000
    if dist_km > 0:
        title = f"{sport.capitalize()} de {dist_km:.2f}km"
    else:
        title = f"{sport.capitalize()} de {int(total_time // 60)}min"

    return {
        "sport": sport,
        "title": title,
        "start_time": start_time,
        "end_time": start_time,
        "source_format": "tcx",
        "total_elapsed_seconds": int(total_time),
        "total_timer_seconds": int(total_time),
        "total_moving_seconds": int(total_time),
        "total_distance_meters": total_distance,
        "avg_pace_min_km": avg_pace_min_km,
        "max_pace_min_km": None,
        "avg_speed_kmh": avg_speed_kmh,
        "max_speed_kmh": None,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "min_hr": min_hr,
        "avg_cadence": None,
        "max_cadence": None,
        "avg_power": None,
        "max_power": None,
        "normalized_power": None,
        "intensity_factor": None,
        "variability_index": None,
        "total_ascent_m": round(total_ascent, 1) if total_ascent > 0 else None,
        "total_descent_m": round(total_descent, 1) if total_descent > 0 else None,
        "avg_temperature_c": None,
        "max_temperature_c": None,
        "calories": total_calories or None,
        "training_effect_aerobic": None,
        "training_effect_anaerobic": None,
        "avg_ground_contact_time_ms": None,
        "avg_stride_length_m": None,
        "avg_vertical_oscillation_mm": None,
        "avg_vertical_ratio_pct": None,
        "avg_ground_contact_balance_pct": None,
        "avg_stroke_rate": None,
        "pool_length_m": None,
        "total_lengths": None,
        "swolf": None,
        "hr_stream": hr_stream or None,
        "pace_stream": pace_stream or None,
        "power_stream": None,
        "cadence_stream": None,
        "altitude_stream": altitude_stream or None,
        "gps_stream": gps_stream or None,
        "laps_data": laps_data or None,
    }


def _parse_trackpoint(pt: ET.Element) -> dict | None:
    try:
        time_el = pt.find("ns:Time", NS)
        time_str = time_el.text if time_el is not None else None
        time_dt = _parse_time(time_str) if time_str else None

        pos = pt.find("ns:Position", NS)
        lat = float(pos.find("ns:LatitudeDegrees", NS).text) if pos is not None else None
        lng = float(pos.find("ns:LongitudeDegrees", NS).text) if pos is not None else None

        alt_el = pt.find("ns:AltitudeMeters", NS)
        alt = float(alt_el.text) if alt_el is not None else None

        dist_el = pt.find("ns:DistanceMeters", NS)
        dist = float(dist_el.text) if dist_el is not None else None

        hr_el = pt.find(".//ns:HeartRateBpm/ns:Value", NS)
        hr = int(hr_el.text) if hr_el is not None else None

        cad_el = pt.find("ns:Cadence", NS)
        cad = int(cad_el.text) if cad_el is not None else None

        return {
            "time_dt": time_dt,
            "lat": lat,
            "lng": lng,
            "alt": alt,
            "distance": dist,
            "hr": hr,
            "cadence": cad,
        }
    except Exception:
        return None


def _parse_time(s: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return datetime.utcnow()


def _float(el: ET.Element, path: str) -> float:
    child = el.find(path, NS)
    return float(child.text) if child is not None and child.text else 0.0


def _int(el: ET.Element, path: str) -> int:
    child = el.find(path, NS)
    return int(child.text) if child is not None and child.text else 0
