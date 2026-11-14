import os
import sys
import math
from typing import Dict, Any, Optional
import numpy as np
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

sys.path.append(os.path.dirname(__file__))
from data_fetcher import (
    VARIABLE_METADATA, 
    PRESET_REGIONS, 
    fetch_nasa_data
)
from analysis import analyze_time_series, run_auto_scan
from forecast import generate_forecast, build_full_timeline
from ask import answer_question, GEMINI_MODEL
from noaa_fetcher import fetch_noaa_ghcnd_monthly, fetch_region_noaa, compare_nasa_noaa, save_noaa_token, REGION_STATIONS
from tourism import get_all_tourism_sites_summary, get_site_tourism_intelligence, TOURISM_SITES
from telegram_alerts import (
    load_config as load_tg_config,
    save_config as save_tg_config,
    auto_detect_chat_id,
    send_telegram_alert,
    get_all_subscribers,
    save_subscriber,
    broadcast_alert_to_subscribers,
    run_daily_climate_audit
)
from cairo_service import (
    CAIRO_DISTRICTS,
    load_cairo_historical_data,
    compute_prophet_additive_forecast,
    generate_cairo_climate_warnings,
    WHO_GREEN_SPACE_MIN_PER_CAPITA
)

app = FastAPI(
    title="TrendLens API - NASA Space Apps Challenge",
    description="Backend API for NASA Earth System Trend Detective",
    version="1.0.0"
)

def clean_nans(obj):
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        val = float(obj)
        return None if (math.isnan(val) or math.isinf(val)) else val
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return [clean_nans(v) for v in obj.tolist()]
    if isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_nans(v) for v in obj]
    return obj

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_frontend_dir():
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend")),
        os.path.abspath(os.path.join(os.getcwd(), "frontend")),
        os.path.abspath("frontend"),
        os.path.join("/var/task", "backend", "frontend"),
        os.path.join("/var/task", "frontend"),
    ]
    for c in candidates:
        if os.path.isdir(c) and os.path.exists(os.path.join(c, "index.html")):
            return c
    return None

FRONTEND_DIR = find_frontend_dir()

DETECTIVE_CASES = [
    {
        "id": "cairo_heat",
        "title_en": "Case #1: Greater Cairo Urban Heat Island & Delta Boundary",
        "title_ar": "القضية 1: تسارع الاحترار وظاهرة الجزيرة الحرارية بالقاهرة الكبرى",
        "subtitle_en": "Investigate 24 years of surface temperature changes over Cairo and Lower Egypt metropolis.",
        "subtitle_ar": "تحقيق في 24 عاماً من التغيرات الحرارية السطحية في القاهرة وشمال مصر.",
        "region_id": "cairo",
        "variable": "T2M",
        "lat": 30.0444,
        "lon": 31.2357,
        "region_name_en": "Greater Cairo, Egypt",
        "region_name_ar": "القاهرة الكبرى، مصر",
        "hypothesis_en": "Surface air temperatures show a statistically significant warming rate (>0.25°C/decade).",
        "hypothesis_ar": "تظهر درجات حرارة الهواء السطحي وتيرة احترار متسارعة ذات دلالة إحصائية مؤكدة."
    },
    {
        "id": "alexandria_coastal",
        "title_en": "Case #2: Alexandria & Nile Delta Coastal Vulnerability",
        "title_ar": "القضية 2: الإسكندرية والساحل الشمالي ومخاطر التغيرات الهيدرولوجية",
        "subtitle_en": "Analyze shifts in precipitation patterns and coastal humidity along the Mediterranean.",
        "subtitle_ar": "تحليل أنماط هطول الأمطار والرطوبة الساحلية للبحر المتوسط.",
        "region_id": "alexandria",
        "variable": "PRECTOTCORR",
        "lat": 31.2001,
        "lon": 29.9187,
        "region_name_en": "Alexandria & North Coast",
        "region_name_ar": "الإسكندرية والساحل الشمالي",
        "hypothesis_en": "Coastal rain events display higher flash-intensity and shorter duration variance.",
        "hypothesis_ar": "أحداث الأمطار الساحلية تظهر تركيزاً أعلى وتقلبات شتوية حادة."
    },
    {
        "id": "aswan_reservoir",
        "title_en": "Case #3: Lake Nasser & Upper Egypt Evaporative Stress",
        "title_ar": "القضية 3: بحيرة ناصر وصعيد مصر — الإجهاد الحراري والتبخري",
        "subtitle_en": "Detect extreme thermal and solar radiance trends impacting strategic Nile water reserves.",
        "subtitle_ar": "الكشف عن معدلات تسارع درجات الحرارة والإشعاع الشمسي المؤثر على مخزون المياه الاستراتيجي.",
        "region_id": "aswan",
        "variable": "T2M",
        "lat": 24.0889,
        "lon": 32.8998,
        "region_name_en": "Aswan & Lake Nasser",
        "region_name_ar": "أسوان وبحيرة ناصر",
        "hypothesis_en": "High-latitude tropical heat stress accelerates evaporative demand over surface reservoirs.",
        "hypothesis_ar": "الاحترار المستمر يرفع معدلات الفقد التبخري فوق المسطحات المائية الجنوبية."
    },
    {
        "id": "redsea_wind",
        "title_en": "Case #4: Red Sea & Gulf of Suez Wind Energy Trajectory",
        "title_ar": "القضية 4: ساحل البحر الأحمر وخليج السويس — استدامة طاقة الرياح",
        "subtitle_en": "Evaluate multi-decadal kinetic wind speed stability for national renewable corridors.",
        "subtitle_ar": "تقييم استقرار وسرعات الرياح الحركية لدعم مزارع الطاقة المتجددة (الزعفرانة وجبل الزيت).",
        "region_id": "redsea",
        "variable": "WS2M",
        "lat": 27.2579,
        "lon": 33.8116,
        "region_name_en": "Red Sea Coast & Hurghada",
        "region_name_ar": "ساحل البحر الأحمر والغردقة",
        "hypothesis_en": "Consistent coastal pressure gradients maintain high-density kinetic energy yield.",
        "hypothesis_ar": "فروق الضغط الساحلية المستقرة تضمن كثافة طاقة رياح عالية ومستدامة."
    }
]

@app.get("/api/variables")
def get_variables():
    return {
        "status": "success",
        "variables": VARIABLE_METADATA
    }

@app.get("/api/regions")
def get_regions():
    return {
        "status": "success",
        "regions": PRESET_REGIONS
    }

@app.get("/api/detective-cases")
def get_cases():
    return {
        "status": "success",
        "cases": DETECTIVE_CASES
    }

@app.get("/api/analyze")
def analyze(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    variable: str = Query("T2M", description="Climate variable code"),
    region_name_en: str = Query("Selected Location"),
    region_name_ar: str = Query("الموقع المحدد"),
    start_year: int = Query(2000),
    end_year: int = Query(2023)
):
    if variable not in VARIABLE_METADATA:
        raise HTTPException(status_code=400, detail=f"Invalid variable: {variable}")

    try:
        data = fetch_nasa_data(lat, lon, start_year, end_year)
        records = data.get("records") or data.get("data") or []
        if not records:
            raise HTTPException(status_code=404, detail="No data records returned from NASA.")
        
        result = analyze_time_series(records, variable, region_name_en, region_name_ar)
        return clean_nans({
            "status": "success",
            "region": {
                "name_en": region_name_en,
                "name_ar": region_name_ar,
                "lat": lat,
                "lon": lon
            },
            "data": result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast")
def forecast(
    lat: float = Query(...),
    lon: float = Query(...),
    variable: str = Query("T2M"),
    region_name_en: str = Query("Selected Location"),
    region_name_ar: str = Query("الموقع المحدد"),
    start_year: int = Query(2000),
    end_year: int = Query(2023),
    forecast_years: int = Query(26, ge=1, le=50),
):
    """
    Returns full analysis + future projection to end_year+forecast_years.
    Uses Theil-Sen slope extrapolation with 95% CI bands.
    Methodology: Mann-Kendall + Sen's slope (Space Apps official resources).
    """
    if variable not in VARIABLE_METADATA:
        raise HTTPException(status_code=400, detail=f"Invalid variable: {variable}")
    try:
        data = fetch_nasa_data(lat, lon, start_year, end_year)
        records = data.get("records") or data.get("data") or []
        if not records:
            raise HTTPException(status_code=404, detail="No data found.")

        analysis = analyze_time_series(records, variable, region_name_en, region_name_ar)
        stats    = analysis["statistics"]
        chart    = analysis["chart_data"]
        annual   = analysis["annual_chart"]

        # Theil-Sen slope values (per year) for forecasting
        slope_yr     = stats["sen_slope_per_year"]
        slope_low_yr = slope_yr * 0.6   # approximate from CI bounds
        slope_hi_yr  = slope_yr * 1.4

        # Try to extract actual CI from chart data
        tl  = chart["trend_line"]
        sll = chart["slope_low_line"]
        slh = chart["slope_high_line"]
        n_t = len(tl)
        if n_t > 1:
            dt_years = (end_year - start_year)
            if dt_years > 0:
                slope_low_yr = (sll[-1] - sll[0]) / dt_years
                slope_hi_yr  = (slh[-1] - slh[0]) / dt_years

        fc = generate_forecast(
            raw_values=chart["raw_values"],
            labels=chart["labels"],
            sen_slope_per_year=slope_yr,
            sen_slope_low_per_year=slope_low_yr,
            sen_slope_high_per_year=slope_hi_yr,
            intercept=0,
            forecast_years=forecast_years,
            last_data_year=end_year,
        )

        timeline = build_full_timeline(
            historical_labels=chart["labels"],
            historical_annual_years=annual["years"],
            historical_annual_values=annual["values"],
            forecast_result=fc,
        )

        return clean_nans({
            "status": "success",
            "region": {"name_en": region_name_en, "name_ar": region_name_ar, "lat": lat, "lon": lon},
            "variable": variable,
            "variable_meta": analysis["variable_meta"],
            "statistics": stats,
            "detective_report": analysis["detective_report"],
            "forecast": fc,
            "timeline": timeline,
            "change_point": analysis.get("change_point"),
            "seasonal_asymmetry": analysis.get("seasonal_asymmetry"),
            "heat_index": analysis.get("heat_index"),
            "policy_brief": analysis.get("policy_brief"),
            "data_source": "NASA POWER MERRA-2 (2000-2023) + Theil-Sen Extrapolation",
            "methodology_url": "https://medium.com/@snp.kriss/statistical-test-methods-to-detect-trends-in-time-series-data-b361a0ec530b",
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/noaa-token")
def set_noaa_token(token: str = Body(..., embed=True)):
    """Save a user-provided NOAA CDO API token for station data access."""
    try:
        save_noaa_token(token)
        return {"status": "success", "message": "NOAA token saved. Station validation enabled."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/noaa-validate")
def noaa_validate(
    region_key: str = Query(..., description="Region key: cairo, amazon, siberia, sahel, california, arabia, greenland, india, patagonia, baghdad"),
    start_year: int = Query(2000),
    end_year:   int = Query(2023),
):
    """
    Fetches NOAA GHCND daily station temperature data and cross-validates against NASA POWER.
    Source: https://www.ncei.noaa.gov/cdo-web/ (Space Apps official resource)
    """
    result = fetch_region_noaa(region_key, start_year=start_year, end_year=end_year)
    if result is None:
        token_missing = not (
            __import__('os').environ.get("NOAA_CDO_TOKEN") or
            (__import__('pathlib').Path(__file__).parent / "noaa_token.txt").exists()
        )
        if token_missing:
            return {
                "status": "no_token",
                "message": "NOAA CDO token not set. Get free token at https://www.ncdc.noaa.gov/cdo-web/token then POST to /api/noaa-token",
                "token_url": "https://www.ncdc.noaa.gov/cdo-web/token",
            }
        return {"status": "error", "message": f"No NOAA station data found for region '{region_key}'."}
    return {"status": "success", "data": result}


@app.get("/api/noaa-compare")
def noaa_compare(
    region_key:    str   = Query(...),
    start_year:    int   = Query(2000),
    end_year:      int   = Query(2023),
):
    """
    Full NASA POWER vs NOAA station cross-validation with bias/RMSE/correlation stats.
    Both data sources are official Space Apps Challenge resources.
    """
    # Look up region lat/lon
    reg_info = next((r for r in PRESET_REGIONS if r.get("id") == region_key), None)
    station  = REGION_STATIONS.get(region_key)

    if not station:
        raise HTTPException(status_code=404, detail=f"No NOAA station mapped for '{region_key}'")

    # 1. NASA POWER annual data
    try:
        lat = reg_info["lat"] if reg_info else 30.0
        lon = reg_info["lon"] if reg_info else 31.2
        nasa_data  = fetch_nasa_data(lat, lon, start_year, end_year)
        nasa_analysis = analyze_time_series(
            nasa_data["records"], "T2M",
            reg_info["name_en"] if reg_info else region_key,
            reg_info["name_ar"] if reg_info else region_key,
        )
        annual = nasa_analysis["annual_chart"]
        nasa_years  = annual["years"]
        nasa_values = annual["values"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NASA POWER error: {e}")

    # 2. NOAA GHCND station data
    noaa_data = fetch_region_noaa(region_key, start_year=start_year, end_year=end_year)
    if noaa_data is None:
        return {
            "status": "partial",
            "message": "NOAA data unavailable (token missing or no station data). NASA POWER data returned.",
            "nasa_annual": {"years": nasa_years, "values": nasa_values},
        }

    # 3. Cross-validation statistics
    comparison = compare_nasa_noaa(nasa_years, nasa_values, noaa_data)

    return {
        "status":        "success",
        "region_key":    region_key,
        "station":       {"id": station["id"], "name": station["name"]},
        "nasa_source":   "NASA POWER MERRA-2 — https://power.larc.nasa.gov/",
        "noaa_source":   "NOAA CDO GHCND — https://www.ncei.noaa.gov/cdo-web/",
        "nasa_annual":   {"years": nasa_years, "values": nasa_values},
        "noaa_annual":   {"years": noaa_data["years"], "values": noaa_data["values"]},
        "cross_validation": comparison,
    }

@app.get("/api/auto-scan")
def auto_scan(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    region_name_en: str = Query("Selected Location"),
    region_name_ar: str = Query("الموقع المحدد"),
    start_year: int = Query(2000),
    end_year: int = Query(2023)
):
    try:
        data = fetch_nasa_data(lat, lon, start_year, end_year)
        records = data.get("records") or data.get("data") or []
        if not records:
            raise HTTPException(status_code=404, detail="No data records returned from NASA.")

        scan_results = run_auto_scan(records, region_name_en, region_name_ar)
        return {
            "status": "success",
            "region": {
                "name_en": region_name_en,
                "name_ar": region_name_ar,
                "lat": lat,
                "lon": lon
            },
            "ranked_variables": scan_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


EGYPT_REGIONS = [
    {"key": "cairo",      "name_ar": "القاهرة الكبرى والجيزة",          "name_en": "Greater Cairo",               "lat": 30.0444, "lon": 31.2357},
    {"key": "alexandria", "name_ar": "الإسكندرية والساحل الشمالي",       "name_en": "Alexandria & North Coast",    "lat": 31.2001, "lon": 29.9187},
    {"key": "delta",      "name_ar": "إقليم الدلتا والبحيرة",          "name_en": "Nile Delta Agriculture",      "lat": 30.8500, "lon": 31.0500},
    {"key": "sinai",      "name_ar": "جنوب سيناء وشرم الشيخ",          "name_en": "South Sinai & St. Catherine", "lat": 28.5560, "lon": 33.9750},
    {"key": "aswan",      "name_ar": "أسوان وبحيرة ناصر",               "name_en": "Aswan & Lake Nasser",         "lat": 24.0889, "lon": 32.8998},
    {"key": "luxor",      "name_ar": "الأقصر وقنا (صعيد مصر)",          "name_en": "Luxor & Qena Valley",         "lat": 25.6872, "lon": 32.6396},
    {"key": "redsea",     "name_ar": "ساحل البحر الأحمر والغردقة",       "name_en": "Red Sea Coast & Hurghada",    "lat": 27.2579, "lon": 33.8116},
    {"key": "siwa",       "name_ar": "واحة سيوة ومطروح",                "name_en": "Siwa Oasis & Matrouh",        "lat": 29.2032, "lon": 25.5195},
    {"key": "newvalley",  "name_ar": "الوادي الجديد وتوشكى",            "name_en": "New Valley & Toshka",         "lat": 24.5000, "lon": 30.0000},
    {"key": "suez",       "name_ar": "إقليم قناة السويس وبورسعيد",       "name_en": "Suez Canal & Port Said",      "lat": 30.5965, "lon": 32.2715},
]


def _sanitize_dict(obj):
    if isinstance(obj, dict):
        return {k: _sanitize_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_dict(x) for x in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


@app.get("/api/report-card")
def get_report_card():
    """
    Computes climate health grades for all 10 Egyptian regions based on:
    - Warming rate (sen_slope_per_decade)
    - Mann-Kendall statistical significance
    - Seasonal asymmetry ratio
    """
    results = []
    for reg in EGYPT_REGIONS:
        try:
            data = fetch_nasa_data(reg["lat"], reg["lon"], 2000, 2023)
            records = data.get("records") or data.get("data") or []
            if not records:
                continue

            analysis = analyze_time_series(records, "T2M", reg["name_en"], reg["name_ar"])
            stats = analysis.get("statistics", {})
            mk = stats.get("mann_kendall", {})
            raw_vals = (analysis.get("chart_data") or {}).get("raw_values") or []
            mean_temp = float(np.mean(raw_vals)) if len(raw_vals) > 0 else float(stats.get("mean", 22.0))

            slope_decade = float(stats.get("sen_slope_per_decade", 0.0))
            p_val = float(mk.get("p_value", 1.0))
            significant = bool(p_val < 0.05)

            asym = analysis.get("seasonal_asymmetry") or {}
            asym_ratio = float(asym.get("asymmetry_ratio", 1.0)) if asym.get("asymmetry_ratio") is not None else 1.0

            # Composite score calculation (0 - 100) calibrated for MENA climate scale:
            # Baseline 100, penalized by warming rate, statistical certainty, and seasonal amplification
            score = 100.0 - (abs(slope_decade) * 110.0)
            if significant:
                score -= 12.0
            if asym_ratio > 2.8:
                score -= 10.0

            score = max(10.0, min(95.0, round(score, 1)))

            # Letter grade assignment
            if score >= 80:
                grade = "A"
                grade_ar = "ممتاز"
                color = "#10b981"  # green
            elif score >= 65:
                grade = "B"
                grade_ar = "جيد"
                color = "#eab308"  # yellow
            elif score >= 50:
                grade = "C"
                grade_ar = "متوسط"
                color = "#f97316"  # orange
            elif score >= 35:
                grade = "D"
                grade_ar = "ضعيف"
                color = "#ef4444"  # red
            else:
                grade = "F"
                grade_ar = "حرج"
                color = "#be123c"  # crimson

            results.append({
                "key": reg["key"],
                "name_ar": reg["name_ar"],
                "name_en": reg["name_en"],
                "lat": reg["lat"],
                "lon": reg["lon"],
                "grade": grade,
                "grade_ar": grade_ar,
                "score": score,
                "slope_decade": round(slope_decade, 3),
                "mean_temp": round(mean_temp, 2),
                "p_value": round(p_val, 4),
                "significant": significant,
                "asymmetry_ratio": round(asym_ratio, 2),
                "color": color
            })
        except Exception as e:
            continue

    return _sanitize_dict({
        "status": "success",
        "total_regions": len(results),
        "report_card": results,
        "regions": results
    })


@app.get("/api/compare")
def compare_regions(
    region1_key: str = Query(..., description="First region key (e.g. cairo)"),
    region2_key: str = Query(..., description="Second region key (e.g. alexandria)"),
    variable: str = Query("T2M", description="Climate variable code")
):
    """
    Side-by-side comparative analysis of two Egyptian regions.
    Returns synchronized historical timelines and 2050 Theil-Sen projections.
    """
    r1 = next((r for r in EGYPT_REGIONS if r["key"] == region1_key), None)
    r2 = next((r for r in EGYPT_REGIONS if r["key"] == region2_key), None)

    if not r1:
        raise HTTPException(status_code=404, detail=f"Region '{region1_key}' not found in Egyptian regions.")
    if not r2:
        raise HTTPException(status_code=404, detail=f"Region '{region2_key}' not found in Egyptian regions.")

    def _get_region_forecast(reg):
        data = fetch_nasa_data(reg["lat"], reg["lon"], 2000, 2023)
        records = data.get("records") or data.get("data") or []
        if not records:
            raise HTTPException(status_code=404, detail=f"No data records for {reg['name_en']}")

        analysis = analyze_time_series(records, variable, reg["name_en"], reg["name_ar"])
        stats = analysis["statistics"]
        chart = analysis["chart_data"]
        annual = analysis["annual_chart"]

        slope_yr = stats["sen_slope_per_year"]
        slope_low_yr = slope_yr * 0.6
        slope_hi_yr = slope_yr * 1.4

        fc = generate_forecast(
            raw_values=chart["raw_values"],
            labels=chart["labels"],
            sen_slope_per_year=slope_yr,
            sen_slope_low_per_year=slope_low_yr,
            sen_slope_high_per_year=slope_hi_yr,
            intercept=0,
            forecast_years=27,
            last_data_year=2023
        )

        timeline = build_full_timeline(
            historical_labels=chart["labels"],
            historical_annual_years=annual["years"],
            historical_annual_values=annual["values"],
            forecast_result=fc
        )

        return {
            "key": reg["key"],
            "name_ar": reg["name_ar"],
            "name_en": reg["name_en"],
            "lat": reg["lat"],
            "lon": reg["lon"],
            "statistics": stats,
            "timeline": timeline,
            "change_point": analysis.get("change_point"),
            "seasonal_asymmetry": analysis.get("seasonal_asymmetry"),
            "heat_index": analysis.get("heat_index")
        }

    try:
        data1 = _get_region_forecast(r1)
        data2 = _get_region_forecast(r2)

        slope1 = data1["statistics"].get("sen_slope_per_decade", 0.0)
        slope2 = data2["statistics"].get("sen_slope_per_decade", 0.0)
        slope_diff = round(slope1 - slope2, 3)

        fc_vals1 = data1["timeline"].get("forecast_values", [])
        fc_vals2 = data2["timeline"].get("forecast_values", [])
        val2050_1 = fc_vals1[-1] if len(fc_vals1) > 0 else None
        val2050_2 = fc_vals2[-1] if len(fc_vals2) > 0 else None
        temp_diff_2050 = round(val2050_1 - val2050_2, 2) if (val2050_1 is not None and val2050_2 is not None) else None

        warmer_region = r1["name_ar"] if slope1 > slope2 else r2["name_ar"]
        warmer_key = r1["key"] if slope1 > slope2 else r2["key"]

        comparison = {
            "slope_diff": slope_diff,
            "warmer_region": warmer_region,
            "warmer_key": warmer_key,
            "temp_diff_2050": temp_diff_2050,
            "slope1": slope1,
            "slope2": slope2,
            "val2050_1": val2050_1,
            "val2050_2": val2050_2,
            "summary_ar": f"يسجل {r1['name_ar']} معدل احترار {slope1:+.3f}°C/عقد مقارنة بـ {slope2:+.3f}°C/عقد في {r2['name_ar']} (فارق {abs(slope_diff):.3f}°C/عقد).",
            "summary_en": f"{r1['name_en']} records {slope1:+.3f}°C/dec vs {slope2:+.3f}°C/dec in {r2['name_en']} (difference of {abs(slope_diff):.3f}°C/dec)."
        }

        response_payload = {
            "status": "success",
            "variable": variable,
            "region1": data1,
            "region2": data2,
            "comparison": comparison
        }
        return _sanitize_dict(response_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/ask")
def ask_climate(
    question: str = Query(..., description="Arabic question about the open region"),
    lat: float = Query(...),
    lon: float = Query(...),
    variable: str = Query("T2M"),
    region_name_en: str = Query("Selected Location"),
    region_name_ar: str = Query("الموقع المحدد"),
):
    if variable not in VARIABLE_METADATA:
        raise HTTPException(status_code=400, detail=f"Invalid variable: {variable}")
    try:
        result = answer_question(question, lat, lon, variable, region_name_en, region_name_ar)
        result["configured_model"] = GEMINI_MODEL
        return clean_nans(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tourism-sites")
def api_tourism_sites():
    """
    Returns the registry of Egypt's top 14 tourist & cultural heritage destinations,
    including real-time season suitability, coordinates, governorate, and categories.
    """
    try:
        sites = get_all_tourism_sites_summary()
        return clean_nans({
            "status": "success",
            "total_sites": len(sites),
            "sites": sites
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tourism-forecast")
def api_tourism_forecast(site_id: str = Query("giza_pyramids")):
    """
    Returns deep tourism climate intelligence for a specific destination:
    - 7-Day Tourist Forecast (High/Low, RealFeel, UV, Wind, Best Visiting Hours)
    - Prior 7-Day Observed Delta
    - 24-Year Multi-Decadal Historical Climatology Baseline (2000-2023 on same calendar dates)
    - Future 2025-2050 Theil-Sen & IPCC Scenario Projections
    - Heritage Conservation & Visitor Advisory
    """
    try:
        intel = get_site_tourism_intelligence(site_id)
        return clean_nans(intel)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telegram/status")
def api_telegram_status():
    cfg = load_tg_config()
    return clean_nans({
        "status": "success",
        "bot_username": cfg.get("bot_username", "@sixsnova_bot"),
        "has_token": bool(cfg.get("bot_token")),
        "has_chat_id": bool(cfg.get("chat_id")),
        "chat_id": cfg.get("chat_id", "")
    })


@app.post("/api/telegram/config")
def api_telegram_config(payload: Dict[str, Any] = Body(...)):
    cfg = load_tg_config()
    if "bot_token" in payload:
        cfg["bot_token"] = payload["bot_token"].strip()
    if "chat_id" in payload:
        cfg["chat_id"] = str(payload["chat_id"]).strip()
    save_tg_config(cfg)
    return {"status": "success", "message": "Telegram alert settings updated successfully."}


@app.post("/api/telegram/auto-detect")
def api_telegram_auto_detect(bot_token: str = Body(None, embed=True)):
    result = auto_detect_chat_id(bot_token)
    return clean_nans(result)


@app.post("/api/telegram/send-alert")
def api_telegram_send_alert(
    region_name: str = Body("Greater Cairo & Giza Metropolis"),
    alert_type: str = Body("Thermal Surge Spike"),
    severity: str = Body("LEVEL 3 CRITICAL"),
    metric_val: str = Body("+4.8°C Anomaly (39.2°C Surface Temp)"),
    details: str = Body("MODIS Aqua and MERRA-2 sensors report extreme surface thermal radiance. Urban heat island index exceeds critical seasonal threshold."),
    lat: float = Body(30.0444),
    lon: float = Body(31.2357),
    chat_id: Optional[str] = Body(None)
):
    result = send_telegram_alert(
        region_name=region_name,
        alert_type=alert_type,
        severity=severity,
        metric_val=metric_val,
        details=details,
        lat=lat,
        lon=lon,
        chat_id=chat_id
    )
    return clean_nans(result)


@app.get("/api/telegram/subscribers")
def api_telegram_subscribers():
    subs = get_all_subscribers()
    return clean_nans({
        "status": "success",
        "total": len(subs),
        "subscribers": subs
    })


@app.post("/api/telegram/test-alert")
def api_telegram_test_alert(payload: Dict[str, Any] = Body(...)):
    """
    Triggered by the TEST button on the website.
    Sends a live bilingual alert (Heat, Wind, Rainfall, Humidity, or Green Space)
    to a specific chat_id or broadcasts to all registered subscribers.
    """
    alert_type = payload.get("alert_type", "green_space")
    city = payload.get("city", "Cairo")
    district = payload.get("district", "Heliopolis / مصر الجديدة")
    severity = payload.get("severity", "LEVEL 3 CRITICAL")
    metric_val = payload.get("metric_val", "")
    target_chat_id = payload.get("chat_id")  # If None, broadcasts to all!

    result = broadcast_alert_to_subscribers(
        alert_type=alert_type,
        city=city,
        district=district,
        severity=severity,
        metric_val=metric_val,
        target_chat_id=target_chat_id
    )
    return clean_nans(result)


@app.post("/api/telegram/subscriber")
def api_telegram_save_subscriber(payload: Dict[str, Any] = Body(...)):
    chat_id = payload.get("chat_id")
    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id is required")
    sub = save_subscriber(str(chat_id), payload)
    return clean_nans({"status": "success", "subscriber": sub})


@app.post("/api/telegram/trigger-daily-check")
def api_telegram_trigger_daily():
    res = run_daily_climate_audit()
    return clean_nans(res)


# =========================================================================
# CAIRO AI CLIMATE PREDICTOR & GREEN SPACE API (OFFICIAL SPECIFICATION)
# =========================================================================

@app.get("/api/cairo/districts")
def api_cairo_districts():
    """Returns Cairo districts green space telemetry, NDVI, and actionable solutions."""
    return clean_nans({
        "status": "success",
        "city": "Cairo",
        "who_guideline_per_capita": WHO_GREEN_SPACE_MIN_PER_CAPITA,
        "districts": CAIRO_DISTRICTS
    })


@app.get("/api/cairo/historical")
def api_cairo_historical():
    """Returns 24-year NASA POWER MERRA-2 historical records (T2M, WS10M, PRECTOTCORR) for Cairo."""
    data = load_cairo_historical_data()
    return clean_nans({"status": "success", "data": data})


@app.get("/api/cairo/prophet-forecast")
def api_cairo_prophet_forecast(variable: str = Query("T2M")):
    """
    Returns 10-year Prophet additive forecast (2024-2034) for Cairo
    for T2M, WS10M, or PRECTOTCORR with 95% confidence intervals.
    """
    if variable not in ["T2M", "WS10M", "WS2M", "PRECTOTCORR", "RH2M"]:
        variable = "T2M"
    hist = load_cairo_historical_data()
    fc = compute_prophet_additive_forecast(hist["monthly_records"], variable=variable, forecast_years=10)
    return clean_nans({
        "status": "success",
        "variable": variable,
        "forecast": fc
    })


@app.get("/api/cairo/warnings")
def api_cairo_warnings():
    """Returns algorithmic Climate Change & Green Space Warnings for Cairo."""
    warnings = generate_cairo_climate_warnings()
    return clean_nans({"status": "success", "warnings": warnings})


@app.get("/api/cairo/sources")
def api_cairo_sources():
    """Returns official data sources, sensors, and methodology credits."""
    return clean_nans({
        "status": "success",
        "sources": [
            {
                "name": "NASA POWER Project",
                "full_name": "Prediction Of Worldwide Energy Resources",
                "model": "MERRA-2 (Modern-Era Retrospective analysis for Research and Applications, Version 2)",
                "description": "Provides satellite and model-based daily and monthly climatology at 0.5° x 0.625° resolution across Egypt.",
                "url": "https://power.larc.nasa.gov/",
                "variables": ["T2M (Temperature 2m)", "WS10M / WS2M (Wind Speed)", "PRECTOTCORR (Precipitation)", "RH2M (Relative Humidity)", "ALLSKY_SFC_SW_DWN (Solar Irradiance)"]
            },
            {
                "name": "NASA GIBS",
                "full_name": "Global Imagery Browse Services",
                "sensors": "MODIS (Terra & Aqua), VIIRS (Suomi NPP & NOAA-20)",
                "description": "Supplies interactive daily full-resolution satellite imagery layers, aerosol optical depth (AOD), and thermal anomaly overlays.",
                "url": "https://www.earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs",
                "capabilities": ["Terra/MODIS Corrected Reflectance", "Aqua/MODIS Thermal Anomalies & Fires", "VIIRS Day/Night Band"]
            },
            {
                "name": "NASA Technical Report (NTRS #20090042747)",
                "authors": "James G. Acker, Erin McMahon, Suhung Shen, Thomas Hearty, Nancy Casey",
                "institution": "NASA Goddard Space Flight Center / GES DISC",
                "title": "Time-Series Analysis of Remotely-Sensed SeaWiFS Chlorophyll in River-Influenced Coastal Regions",
                "methodology": "Peer-reviewed multi-decadal satellite time-series trend detection, harmonic de-seasoning, and comparative divergence analysis applied in the Dual-Sector Comparative Intelligence engine.",
                "url": "https://ntrs.nasa.gov/citations/20090042747"
            },
            {
                "name": "World Health Organization (WHO) Urban Health Metrics",
                "guideline": "Minimum 9.0 m² of green space per urban resident, with ideal access of 50 m².",
                "benchmark": "Used to evaluate green space equity and deficit across Cairo districts."
            },
            {
                "name": "Cairo Urban Observatory & CAPMAS",
                "description": "District boundaries, population densities, and land cover classification records for the Greater Cairo Metropolis."
            }
        ]
    })



# Mount frontend directory for static assets
if FRONTEND_DIR and os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa_or_static(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/")
    def serve_fallback():
        return {"status": "online", "message": "6S Nova API running. Frontend folder not mounted.", "dir": str(FRONTEND_DIR)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

