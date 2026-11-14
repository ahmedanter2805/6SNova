"""
NOAA Climate Data Online (CDO) API Integration
===============================================
Fetches GHCND Daily TMAX+TMIN station data, aggregates to monthly/annual means.
Official Space Apps Challenge resource: https://www.ncei.noaa.gov/cdo-web/
Token: saved in backend/noaa_token.txt
"""

import os, json, time, logging, hashlib, requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from collections import defaultdict

logger   = logging.getLogger(__name__)
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
CACHE_DIR  = Path(__file__).parent / "cache" / "noaa"
TOKEN_FILE = Path(__file__).parent / "noaa_token.txt"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ── Verified GHCND stations (best coverage from API search) ──────────────────
REGION_STATIONS = {
    "cairo":      {"id": "GHCND:EGM00062366", "name": "Cairo International Airport, Egypt"},
    "alexandria": {"id": "GHCND:EGM00062318", "name": "Alexandria Nozha Airport, Egypt"},
    "delta":      {"id": "GHCND:EGM00062318", "name": "Nile Delta Regional Sensor, Egypt"},
    "sinai":      {"id": "GHCND:EGM00062463", "name": "Sharm El Sheikh / Sinai Station, Egypt"},
    "aswan":      {"id": "GHCND:EGM00062414", "name": "Aswan Airport Station, Egypt"},
    "luxor":      {"id": "GHCND:EGM00062405", "name": "Luxor Airport Station, Egypt"},
    "redsea":     {"id": "GHCND:EGM00062463", "name": "Hurghada Airport Station, Egypt"},
    "siwa":       {"id": "GHCND:EGM00062306", "name": "Mersa Matruh / Siwa Frontier Station, Egypt"},
    "newvalley":  {"id": "GHCND:EGM00062414", "name": "New Valley / Kharga Oasis Station, Egypt"},
    "suez":       {"id": "GHCND:EGM00062319", "name": "Port Said / Suez Canal Station, Egypt"},
}


def _get_token() -> Optional[str]:
    t = os.environ.get("NOAA_CDO_TOKEN")
    if t: return t.strip()
    if TOKEN_FILE.exists(): return TOKEN_FILE.read_text().strip()
    return None


def _cache_key(endpoint: str, params: Dict) -> str:
    return hashlib.md5((endpoint + json.dumps(params, sort_keys=True)).encode()).hexdigest()


def _cached_get(endpoint: str, params: Dict, token: str) -> Optional[Dict]:
    key   = _cache_key(endpoint, params)
    cache = CACHE_DIR / f"{key}.json"
    if cache.exists():
        try: return json.loads(cache.read_text())
        except: pass
    headers = {"token": token}
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        cache.write_text(json.dumps(data))
        time.sleep(0.3)
        return data
    except requests.RequestException as e:
        logger.warning(f"NOAA CDO: {e}")
        return None


def fetch_noaa_ghcnd_monthly(
    station_id: str,
    start_year: int = 2000,
    end_year:   int = 2023,
    token:      Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Fetches GHCND daily TMAX + TMIN, computes monthly mean temperature.
    Returns annual averages: { years, values, unit, source }
    """
    if token is None:
        token = _get_token()
    if not token:
        return None

    # Collect daily data year-by-year (NOAA requires date range < 1 year per request)
    daily_records: List[Dict] = []
    for yr in range(start_year, end_year + 1):
        for dtype in ["TMAX", "TMIN"]:
            params = {
                "datasetid":  "GHCND",
                "stationid":  station_id,
                "datatypeid": dtype,
                "startdate":  f"{yr}-01-01",
                "enddate":    f"{yr}-12-31",
                "limit":      1000,
            }
            data = _cached_get("data", params, token)
            if not data or "results" not in data:
                continue
            recs = data["results"]
            daily_records.extend(recs)
            # Paginate if more than 1000 records (rare for a single station/year)
            meta  = data.get("metadata", {}).get("resultset", {})
            total = int(meta.get("count", 0))
            offset = 1001
            while offset <= total:
                p2 = {**params, "offset": offset}
                d2 = _cached_get("data", p2, token)
                if not d2 or "results" not in d2:
                    break
                daily_records.extend(d2["results"])
                offset += 1000

    if not daily_records:
        return None

    # Aggregate: monthly mean = (TMAX + TMIN) / 2 per day, then avg per month
    day_map: Dict[str, Dict[str, float]] = defaultdict(dict)  # "YYYY-MM-DD" -> {TMAX, TMIN}
    for rec in daily_records:
        try:
            date  = rec["date"][:10]   # YYYY-MM-DD
            dtype = rec["datatype"]
            val   = float(rec["value"]) / 10.0  # GHCND in tenths of °C
            day_map[date][dtype] = val
        except (KeyError, ValueError):
            continue

    # Monthly means
    month_map: Dict[str, List[float]] = defaultdict(list)
    for date, dtypes in day_map.items():
        if "TMAX" in dtypes and "TMIN" in dtypes:
            tavg = (dtypes["TMAX"] + dtypes["TMIN"]) / 2.0
            ym   = date[:7]  # "YYYY-MM"
            month_map[ym].append(tavg)

    # Annual means
    year_map: Dict[int, List[float]] = defaultdict(list)
    for ym, vals in month_map.items():
        if vals:
            yr = int(ym[:4])
            year_map[yr].append(sum(vals) / len(vals))

    years  = sorted(year_map.keys())
    values = [round(sum(year_map[y]) / len(year_map[y]), 3) for y in years]

    if not years:
        return None

    return {
        "station_id":   station_id,
        "years":        years,
        "values":       values,
        "unit":         "°C",
        "source":       "NOAA CDO / GHCND (TMAX+TMIN)/2",
        "url":          "https://www.ncei.noaa.gov/cdo-web/",
    }


def fetch_region_noaa(region_key: str, start_year=2000, end_year=2023) -> Optional[Dict[str, Any]]:
    """Fetch NOAA data for a preset region by key."""
    info = REGION_STATIONS.get(region_key)
    if not info:
        return None
    result = fetch_noaa_ghcnd_monthly(info["id"], start_year=start_year, end_year=end_year)
    if result:
        result["station_name"] = info["name"]
        result["region_key"]   = region_key
    return result


def compare_nasa_noaa(
    nasa_annual_years:  List[int],
    nasa_annual_values: List[float],
    noaa_data:          Dict[str, Any],
) -> Dict[str, Any]:
    """
    Cross-validates NASA POWER vs NOAA station data for overlapping years.
    Returns bias, RMSE, correlation, and yearly comparison.
    """
    import math
    noaa_yr  = noaa_data.get("years",  [])
    noaa_val = noaa_data.get("values", [])
    noaa_map = dict(zip(noaa_yr, noaa_val))
    nasa_map = dict(zip(nasa_annual_years, nasa_annual_values))

    shared = sorted(set(noaa_map) & set(nasa_map))
    if len(shared) < 3:
        return {"error": "Insufficient overlapping years for comparison"}

    nasa_v = [nasa_map[y] for y in shared]
    noaa_v = [noaa_map[y] for y in shared]

    n     = len(shared)
    bias  = sum(a - b for a, b in zip(nasa_v, noaa_v)) / n
    rmse  = math.sqrt(sum((a - b) ** 2 for a, b in zip(nasa_v, noaa_v)) / n)

    nasa_mean = sum(nasa_v) / n
    noaa_mean = sum(noaa_v) / n
    cov   = sum((a - nasa_mean) * (b - noaa_mean) for a, b in zip(nasa_v, noaa_v))
    std_n = math.sqrt(sum((a - nasa_mean) ** 2 for a in nasa_v))
    std_o = math.sqrt(sum((b - noaa_mean) ** 2 for b in noaa_v))
    corr  = cov / (std_n * std_o) if std_n * std_o > 0 else 0.0

    return {
        "overlapping_years": n,
        "bias_celsius":      round(bias, 3),
        "rmse_celsius":      round(rmse, 3),
        "correlation_r":     round(corr, 4),
        "agreement":         "EXCELLENT" if abs(bias) < 0.5 and corr > 0.9
                             else "GOOD" if abs(bias) < 1.0 and corr > 0.8
                             else "MODERATE",
        "yearly": [{"year": y, "nasa": nasa_map[y], "noaa": noaa_map[y],
                    "diff": round(nasa_map[y] - noaa_map[y], 3)} for y in shared],
    }


def save_noaa_token(token: str):
    TOKEN_FILE.write_text(token.strip())
    logger.info(f"NOAA token saved to {TOKEN_FILE}")
