"""
Training Metrics Service — cálculos unificados de métricas de treino.

Inclui: TSS (HR + power), NP, IF, VI, TRIMP, HR drift,
pace consistency, zonas FC, zonas potência, CTL/ATL/TSB, monotonia, strain.
"""
import math
from datetime import date, timedelta
from typing import Optional


# ============================================================
# Zonas de FC (5 zonas baseadas em % da FC máxima)
# ============================================================
def get_hr_zones(hr_max: int) -> list[dict]:
    return [
        {"zone": 1, "name": "Recuperação", "min": int(hr_max * 0.50), "max": int(hr_max * 0.60)},
        {"zone": 2, "name": "Aeróbico", "min": int(hr_max * 0.60), "max": int(hr_max * 0.70)},
        {"zone": 3, "name": "Tempo", "min": int(hr_max * 0.70), "max": int(hr_max * 0.80)},
        {"zone": 4, "name": "Limiar", "min": int(hr_max * 0.80), "max": int(hr_max * 0.90)},
        {"zone": 5, "name": "VO2max", "min": int(hr_max * 0.90), "max": hr_max},
    ]


# ============================================================
# Zonas de Potência (7 zonas Coggan baseadas em % do FTP)
# ============================================================
def get_power_zones(ftp: int) -> list[dict]:
    return [
        {"zone": 1, "name": "Recuperação ativa", "min": 0, "max": int(ftp * 0.55)},
        {"zone": 2, "name": "Endurance", "min": int(ftp * 0.55), "max": int(ftp * 0.75)},
        {"zone": 3, "name": "Tempo", "min": int(ftp * 0.75), "max": int(ftp * 0.90)},
        {"zone": 4, "name": "Limiar", "min": int(ftp * 0.90), "max": int(ftp * 1.05)},
        {"zone": 5, "name": "VO2max", "min": int(ftp * 1.05), "max": int(ftp * 1.20)},
        {"zone": 6, "name": "Anaeróbico", "min": int(ftp * 1.20), "max": int(ftp * 1.50)},
        {"zone": 7, "name": "Neuromuscular", "min": int(ftp * 1.50), "max": 9999},
    ]


# ============================================================
# Tempo em Zonas — segundos em cada zona a partir do HR stream
# ============================================================
def calc_time_in_hr_zones(hr_stream: list[dict], hr_max: int) -> dict[str, int]:
    zones = get_hr_zones(hr_max)
    result = {f"z{z['zone']}": 0 for z in zones}

    for i in range(1, len(hr_stream)):
        hr = hr_stream[i].get("hr", 0)
        dt = hr_stream[i].get("t", 0) - hr_stream[i - 1].get("t", 0)
        dt = max(0, min(dt, 10))  # Sanity check: max 10s gap

        for z in zones:
            if z["min"] <= hr <= z["max"]:
                result[f"z{z['zone']}"] += dt
                break

    return result


# ============================================================
# TSS Calculations
# ============================================================
def calc_bike_tss(duration_s: int, np: int, ftp: int) -> float:
    if not np or not ftp or ftp == 0:
        return 0.0
    intensity_factor = np / ftp
    return round((duration_s * np * intensity_factor) / (ftp * 3600) * 100, 1)


def calc_run_tss(duration_s: int, distance_m: float, threshold_pace_s_km: float) -> float:
    if not distance_m or distance_m == 0 or not threshold_pace_s_km:
        return 0.0
    pace = (duration_s / distance_m) * 1000
    intensity_factor = min(threshold_pace_s_km / pace, 1.5)
    return round((duration_s / 3600) * (intensity_factor**2) * 100, 1)


def calc_swim_tss(duration_s: int, distance_m: float, css_s_100m: float) -> float:
    if not distance_m or distance_m == 0 or not css_s_100m:
        return 0.0
    pace = (duration_s / distance_m) * 100
    intensity_factor = min(css_s_100m / pace, 1.5)
    return round((duration_s / 3600) * (intensity_factor**2) * 100, 1)


def calc_hr_tss(duration_s: int, avg_hr: int, hr_max: int, hr_rest: int = 60) -> float:
    if not avg_hr or not hr_max or hr_max <= hr_rest:
        return 0.0
    hr_reserve = max(0, min((avg_hr - hr_rest) / (hr_max - hr_rest), 1))
    return round((duration_s / 3600) * hr_reserve * 100 * 0.8, 1)


def calc_tss(
    sport: str,
    duration_s: int,
    distance_m: float,
    avg_hr: Optional[int],
    np: Optional[int],
    ftp: Optional[int],
    threshold_pace: Optional[float],
    css: Optional[float],
    hr_max: Optional[int],
) -> float:
    """Auto-calculate TSS based on sport and available data."""
    if sport == "bike" and np and ftp:
        return calc_bike_tss(duration_s, np, ftp)
    elif sport == "run" and distance_m and threshold_pace:
        return calc_run_tss(duration_s, distance_m, threshold_pace)
    elif sport == "swim" and distance_m and css:
        return calc_swim_tss(duration_s, distance_m, css)
    elif avg_hr and hr_max:
        return calc_hr_tss(duration_s, avg_hr, hr_max)
    return 0.0


# ============================================================
# Normalized Power (NP)
# ============================================================
def calc_normalized_power(power_stream: list[dict]) -> Optional[int]:
    values = [p.get("power", 0) for p in power_stream if p.get("power")]
    if len(values) < 30:
        return None
    rolling = []
    for i in range(len(values) - 29):
        rolling.append(sum(values[i : i + 30]) / 30)
    avg_fourth = sum(p**4 for p in rolling) / len(rolling)
    return int(round(avg_fourth**0.25))


# ============================================================
# Intensity Factor (IF) = NP / FTP
# ============================================================
def calc_intensity_factor(np: int, ftp: int) -> Optional[float]:
    if not np or not ftp or ftp == 0:
        return None
    return round(np / ftp, 3)


# ============================================================
# Variability Index (VI) = NP / Avg Power
# ============================================================
def calc_variability_index(np: int, avg_power: int) -> Optional[float]:
    if not np or not avg_power or avg_power == 0:
        return None
    return round(np / avg_power, 3)


# ============================================================
# TRIMP (Training Impulse — Banister method)
# ============================================================
def calc_trimp(
    duration_s: int,
    avg_hr: int,
    hr_rest: int,
    hr_max: int,
    gender: str = "male",
) -> float:
    if not avg_hr or not hr_max or hr_max <= hr_rest:
        return 0.0
    hr_reserve = max(0, min((avg_hr - hr_rest) / (hr_max - hr_rest), 1))
    k = 1.92 if gender == "male" else 1.67
    trimp = (duration_s / 60) * hr_reserve * 0.64 * math.exp(k * hr_reserve)
    return round(trimp, 1)


# ============================================================
# HR Drift — comparação FC 1ª metade vs 2ª metade
# ============================================================
def calc_hr_drift(hr_stream: list[dict]) -> Optional[float]:
    if not hr_stream or len(hr_stream) < 10:
        return None
    mid = len(hr_stream) // 2
    first_half = [p["hr"] for p in hr_stream[:mid] if p.get("hr")]
    second_half = [p["hr"] for p in hr_stream[mid:] if p.get("hr")]
    if not first_half or not second_half:
        return None
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    if avg_first == 0:
        return None
    drift = ((avg_second - avg_first) / avg_first) * 100
    return round(drift, 1)


# ============================================================
# Pace Consistency — coeficiente de variação dos splits
# ============================================================
def calc_pace_consistency(pace_stream: list[dict]) -> Optional[float]:
    if not pace_stream or len(pace_stream) < 5:
        return None
    paces = [p["pace"] for p in pace_stream if p.get("pace") and 2 < p["pace"] < 15]
    if len(paces) < 5:
        return None
    avg = sum(paces) / len(paces)
    if avg == 0:
        return None
    variance = sum((p - avg) ** 2 for p in paces) / len(paces)
    cv = (variance**0.5) / avg * 100
    return round(cv, 1)


# ============================================================
# CTL / ATL / TSB (Performance Management Chart)
# ============================================================
CTL_DAYS = 42
ATL_DAYS = 7


def calc_pmc(
    daily_tss: list[dict],
    initial_ctl: float = 0,
    initial_atl: float = 0,
) -> list[dict]:
    """
    Calculate CTL/ATL/TSB from daily TSS values.

    Args:
        daily_tss: [{"date": date, "tss": float}, ...]
    """
    ctl = initial_ctl
    atl = initial_atl
    results = []

    for day in sorted(daily_tss, key=lambda x: x["date"]):
        tss = day["tss"]
        ctl = ctl + (tss - ctl) / CTL_DAYS
        atl = atl + (tss - atl) / ATL_DAYS
        tsb = ctl - atl
        results.append({
            "date": day["date"].isoformat() if isinstance(day["date"], date) else day["date"],
            "tss": tss,
            "ctl": round(ctl, 1),
            "atl": round(atl, 1),
            "tsb": round(tsb, 1),
        })

    return results


def get_form_status(tsb: float) -> dict:
    if tsb > 25:
        return {"text": "Muito descansado", "status": "very_fresh"}
    if tsb > 10:
        return {"text": "Boa forma", "status": "fresh"}
    if tsb > -10:
        return {"text": "Neutro", "status": "neutral"}
    if tsb > -20:
        return {"text": "Cansado", "status": "tired"}
    return {"text": "Overreaching", "status": "overreaching"}


# ============================================================
# Monotonia e Strain
# ============================================================
def calc_monotony_strain(weekly_tss: list[float]) -> dict:
    """
    Monotonia = média / desvio padrão (alto > 1.5 = risco)
    Strain = soma * monotonia (alto > overtraining)
    """
    if not weekly_tss or len(weekly_tss) < 3:
        return {"monotony": 0, "strain": 0}

    avg = sum(weekly_tss) / len(weekly_tss)
    if avg == 0:
        return {"monotony": 0, "strain": 0}

    variance = sum((t - avg) ** 2 for t in weekly_tss) / len(weekly_tss)
    stdev = variance**0.5

    monotony = round(avg / stdev, 2) if stdev > 0 else 0
    strain = round(sum(weekly_tss) * monotony, 1)

    return {"monotony": monotony, "strain": strain}


def fill_missing_days(daily_data: list[dict], start: date, end: date) -> list[dict]:
    """Fill gaps with 0 TSS for continuous PMC calculation."""
    by_date = {d["date"]: d["tss"] for d in daily_data}
    result = []
    current = start
    while current <= end:
        result.append({"date": current, "tss": by_date.get(current, 0)})
        current += timedelta(days=1)
    return result
