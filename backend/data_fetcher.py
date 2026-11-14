import os
import json
import requests
import pandas as pd
from typing import Dict, Any, List

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

VARIABLE_METADATA = {
    "T2M": {
        "name_en": "Surface Air Temperature (2m)",
        "name_ar": "درجة حرارة الهواء السطحي (2 متر)",
        "unit": "°C",
        "description_en": "Air temperature measured 2 meters above ground level from NASA MERRA-2.",
        "description_ar": "درجة حرارة الهواء المقاسة على ارتفاع مترين من سطح الأرض مستمدة من نموذج ناسا MERRA-2.",
        "source": "NASA MERRA-2 Reanalysis"
    },
    "PRECTOTCORR": {
        "name_en": "Precipitation Rate",
        "name_ar": "معدل هطول الأمطار",
        "unit": "mm/day",
        "description_en": "Total bias-corrected precipitation rate from MERRA-2 / GPM sensors.",
        "description_ar": "المعدل اليومي لهطول الأمطار المصحح بناءً على أقمار GPM ونموذج MERRA-2.",
        "source": "NASA MERRA-2 / GPM"
    },
    "GWETTOP": {
        "name_en": "Surface Soil Moisture",
        "name_ar": "رطوبة التربة السطحية",
        "unit": "fraction (0-1)",
        "description_en": "Surface soil wetness / moisture content in the top layer of soil.",
        "description_ar": "محتوى رطوبة الطبقة السطحية من التربة (نسبة بين 0 و 1) من نموذج GLDAS/MERRA-2.",
        "source": "NASA GLDAS / MERRA-2 Land"
    },
    "RH2M": {
        "name_en": "Relative Humidity (2m)",
        "name_ar": "الرطوبة النسبية (2 متر)",
        "unit": "%",
        "description_en": "Relative humidity measured at 2 meters above ground level.",
        "description_ar": "نسبة الرطوبة النسبية للهواء على ارتفاع مترين من الأرض.",
        "source": "NASA MERRA-2 Reanalysis"
    },
    "WS2M": {
        "name_en": "Wind Speed (2m)",
        "name_ar": "سرعة الرياح (2 متر)",
        "unit": "m/s",
        "description_en": "Wind speed measured 2 meters above surface level.",
        "description_ar": "سرعة الرياح المقاسة على ارتفاع مترين من سطح الأرض.",
        "source": "NASA MERRA-2 Reanalysis"
    },
    "ALLSKY_SFC_SW_DWN": {
        "name_en": "Solar Radiation (All Sky Surface Shortwave)",
        "name_ar": "الإشعاع الشمسي السطحي",
        "unit": "kW-hr/m²/day",
        "description_en": "Total downward solar energy hitting the Earth surface per day.",
        "description_ar": "إجمالي الطاقة الإشعاعية الشمسية الساقطة على سطح الأرض يومياً.",
        "source": "NASA CERES / MERRA-2"
    }
}

PRESET_REGIONS = [
    {"id": "cairo",      "name_en": "Greater Cairo",               "name_ar": "القاهرة الكبرى والجيزة",          "lat": 30.0444, "lon": 31.2357},
    {"id": "alexandria", "name_en": "Alexandria & North Coast",    "name_ar": "الإسكندرية والساحل الشمالي",       "lat": 31.2001, "lon": 29.9187},
    {"id": "delta",      "name_en": "Nile Delta Agricultural Belt", "name_ar": "إقليم الدلتا والبحيرة",          "lat": 30.8500, "lon": 31.0500},
    {"id": "sinai",      "name_en": "South Sinai & St. Catherine",  "name_ar": "جنوب سيناء وشرم الشيخ",          "lat": 28.5560, "lon": 33.9750},
    {"id": "aswan",      "name_en": "Aswan & Lake Nasser",         "name_ar": "أسوان وبحيرة ناصر",               "lat": 24.0889, "lon": 32.8998},
    {"id": "luxor",      "name_en": "Luxor & Qena Valley",         "name_ar": "الأقصر وقنا (صعيد مصر)",          "lat": 25.6872, "lon": 32.6396},
    {"id": "redsea",     "name_en": "Red Sea Coast & Hurghada",    "name_ar": "ساحل البحر الأحمر والغردقة",       "lat": 27.2579, "lon": 33.8116},
    {"id": "siwa",       "name_en": "Siwa Oasis & Matrouh",        "name_ar": "واحة سيوة ومطروح",                "lat": 29.2032, "lon": 25.5195},
    {"id": "newvalley",  "name_en": "New Valley & Toshka",         "name_ar": "الوادي الجديد وتوشكى",            "lat": 24.5000, "lon": 30.0000},
    {"id": "suez",       "name_en": "Suez Canal & Port Said",      "name_ar": "إقليم قناة السويس والإسماعيلية",   "lat": 30.5965, "lon": 32.2715},
]

def get_cache_filename(lat: float, lon: float, start_year: int, end_year: int) -> str:
    # Round coordinates to 2 decimal places for consistent caching
    lat_r = round(lat, 2)
    lon_r = round(lon, 2)
    return os.path.join(CACHE_DIR, f"nasa_power_{lat_r}_{lon_r}_{start_year}_{end_year}.json")

def fetch_nasa_data(lat: float, lon: float, start_year: int = 2000, end_year: int = 2023) -> Dict[str, Any]:
    """
    Fetches monthly climate variables from NASA POWER API.
    Caches results locally to guarantee blazing fast demo response and offline capability.
    """
    cache_file = get_cache_filename(lat, lon, start_year, end_year)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                c = json.load(f)
                if "records" not in c and "data" in c:
                    c["records"] = c["data"]
                return c
        except Exception:
            pass

    # Fetch live from NASA POWER API
    parameters = ",".join(VARIABLE_METADATA.keys())
    url = (
        f"https://power.larc.nasa.gov/api/temporal/monthly/point?"
        f"parameters={parameters}&community=AG&longitude={round(lon, 4)}&latitude={round(lat, 4)}&"
        f"start={start_year}&end={end_year}&format=JSON"
    )
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TrendLens/1.0"}
    
    response = requests.get(url, headers=headers, timeout=45)
    response.raise_for_status()
    raw_data = response.json()

    # Process and sanitize data into structured time series
    # NASA POWER returns monthly keys formatted as 'YYYYMM', plus 'YYYY13' for annual average.
    # We filter out the 13th month to keep standard monthly time-series.
    params = raw_data.get("properties", {}).get("parameter", {})
    records = []
    
    # Get all sorted month keys from the first available parameter
    first_param = list(params.keys())[0]
    all_keys = sorted(params[first_param].keys())
    
    for key in all_keys:
        if len(key) == 6 and not key.endswith("13"):
            year = int(key[:4])
            month = int(key[4:6])
            date_str = f"{year}-{month:02d}-01"
            
            entry = {
                "date": date_str,
                "year": year,
                "month": month,
                "period": key
            }
            for p, values in params.items():
                val = values.get(key, None)
                # NASA uses -999 for missing values
                if val is not None and val != -999:
                    entry[p] = val
                else:
                    entry[p] = None
            records.append(entry)

    processed_payload = {
        "metadata": {
            "latitude": lat,
            "longitude": lon,
            "start_year": start_year,
            "end_year": end_year,
            "data_source": "NASA POWER / MERRA-2 / GLDAS / GPM",
            "variables": VARIABLE_METADATA
        },
        "records": records
    }

    # Save to local cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(processed_payload, f, ensure_ascii=False, indent=2)

    return processed_payload

