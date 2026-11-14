import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Optional
from data_fetcher import VARIABLE_METADATA

def mann_kendall_test(y: np.ndarray) -> Dict[str, Any]:
    """
    Computes the Mann-Kendall non-parametric trend test.
    Returns:
        S: Kendall's score
        var_s: Variance of S (accounting for tied values)
        z: Standardized test statistic
        p_value: Two-tailed p-value
        significant: Boolean (p_value < 0.05)
    """
    n = len(y)
    if n < 3:
        return {"S": 0, "z": 0.0, "p_value": 1.0, "significant": False}

    # Calculate Kendall S
    s = 0
    for k in range(n - 1):
        s += np.sum(np.sign(y[k + 1:] - y[k]))

    # Calculate tie correction
    unique_vals, counts = np.unique(y, return_counts=True)
    tie_term = np.sum(counts * (counts - 1) * (2 * counts + 5))

    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0

    if var_s == 0:
        z = 0.0
    elif s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0

    # Two-sided p-value
    p_value = 2.0 * (1.0 - stats.norm.cdf(abs(z)))

    return {
        "S": int(s),
        "var_s": float(var_s),
        "z": float(z),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05)
    }

def theil_sen_slope(x: np.ndarray, y: np.ndarray, alpha: float = 0.05) -> Dict[str, Any]:
    """
    Calculates Theil-Sen's robust non-parametric slope estimator and confidence interval.
    """
    n = len(y)
    slopes = []
    for i in range(n - 1):
        dx = x[i + 1:] - x[i]
        dy = y[i + 1:] - y[i]
        valid = dx != 0
        if np.any(valid):
            slopes.extend((dy[valid] / dx[valid]).tolist())

    if not slopes:
        return {"slope": 0.0, "intercept": float(np.mean(y)), "slope_low": 0.0, "slope_high": 0.0}

    slopes = np.sort(np.array(slopes))
    median_slope = float(np.median(slopes))
    intercept = float(np.median(y - median_slope * x))

    # Confidence interval for Sen's slope
    N = len(slopes)
    z_crit = stats.norm.ppf(1.0 - alpha / 2.0)
    # Variance formula for number of pairs
    unique_vals, counts = np.unique(y, return_counts=True)
    tie_term = np.sum(counts * (counts - 1) * (2 * counts + 5))
    var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0
    c_alpha = z_crit * np.sqrt(var_s)

    m1 = int(np.floor((N - c_alpha) / 2.0))
    m2 = int(np.ceil((N + c_alpha) / 2.0))
    m1 = max(0, min(N - 1, m1))
    m2 = max(0, min(N - 1, m2))

    slope_low = float(slopes[m1])
    slope_high = float(slopes[m2])

    return {
        "slope": median_slope,
        "intercept": intercept,
        "slope_low": slope_low,
        "slope_high": slope_high
    }


def pettitt_test(data: np.ndarray, years: List[int]) -> Dict[str, Any]:
    """
    Pettitt's non-parametric test for abrupt change-point detection in climate time series.
    Identifies the exact year when the climate baseline shifted.
    """
    n = len(data)
    if n < 6:
        return {"change_year": None, "p_value": 1.0, "significant": False}

    u = np.zeros(n - 1)
    for t in range(1, n):
        s = 0
        for i in range(t):
            s += np.sum(np.sign(data[i] - data[t:]))
        u[t - 1] = s

    abs_u = np.abs(u)
    k = np.max(abs_u)
    idx = int(np.argmax(abs_u))
    change_year = years[idx] if idx < len(years) else years[-1]
    
    # Pettitt's p-value approximation
    p_val = 2.0 * np.exp(-6.0 * (k ** 2) / (n ** 3 + n ** 2))
    p_val = min(1.0, max(0.0, float(p_val)))

    pre_mean = float(np.mean(data[:idx])) if idx > 0 else float(data[0])
    post_mean = float(np.mean(data[idx:])) if idx < n else float(data[-1])

    return {
        "change_year": int(change_year),
        "k_statistic": float(k),
        "p_value": round(p_val, 4),
        "significant": bool(p_val < 0.10),
        "pre_shift_mean": round(pre_mean, 2),
        "post_shift_mean": round(post_mean, 2),
        "shift_delta": round(post_mean - pre_mean, 2)
    }

def compute_heat_index_celsius(t_c: float, rh: float) -> Dict[str, Any]:
    """
    Computes NOAA Steadman Heat Index (Apparent Perceived Temperature in Celsius).
    Categorizes thermal stress risk for human health and agricultural labor.
    """
    if t_c is None or rh is None or np.isnan(t_c) or np.isnan(rh):
        return {"heat_index_c": None, "category": "Normal", "category_ar": "طبيعي"}

    # Convert to Fahrenheit for NOAA polynomial
    t_f = t_c * 9.0 / 5.0 + 32.0
    r = min(100.0, max(0.0, rh))

    if t_f < 80.0:
        hi_f = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (r * 0.094))
    else:
        hi_f = (
            -42.379
            + 2.04901523 * t_f
            + 10.14333127 * r
            - 0.22475541 * t_f * r
            - 0.00683783 * (t_f ** 2)
            - 0.05481717 * (r ** 2)
            + 0.00122874 * (t_f ** 2) * r
            + 0.00085282 * t_f * (r ** 2)
            - 0.00000199 * (t_f ** 2) * (r ** 2)
        )

    hi_c = (hi_f - 32.0) * 5.0 / 9.0
    hi_c = round(hi_c, 1)

    if hi_c >= 54.0:
        cat = "Extreme Danger"
        cat_ar = "خطر شديد جداً (ضربة شمس وشيكة)"
        color = "#e11d48"
    elif hi_c >= 41.0:
        cat = "Danger"
        cat_ar = "خطر (إجهاد حراري حاد)"
        color = "#f43f5e"
    elif hi_c >= 32.0:
        cat = "Extreme Caution"
        cat_ar = "حذر شديد (احتمال إجهاد حراري)"
        color = "#f59e0b"
    elif hi_c >= 27.0:
        cat = "Caution"
        cat_ar = "حذر (تأثير حراري ملحوظ)"
        color = "#eab308"
    else:
        cat = "Comfortable"
        cat_ar = "مريح وطبيعي"
        color = "#10b981"

    return {
        "heat_index_c": hi_c,
        "category": cat,
        "category_ar": cat_ar,
        "color": color
    }

def analyze_seasonal_asymmetry(df: pd.DataFrame, variable_key: str) -> Dict[str, Any]:
    """
    Computes Summer (JJA) vs Winter (DJF) warming divergence.
    Detects if Egypt is suffering from summer amplification.
    """
    if "month" not in df.columns or variable_key not in df.columns:
        return {}

    summer_df = df[df["month"].isin([6, 7, 8])].groupby("year")[variable_key].mean()
    winter_df = df[df["month"].isin([12, 1, 2])].groupby("year")[variable_key].mean()

    res = {}
    if len(summer_df) >= 5:
        s_res = stats.linregress(range(len(summer_df)), summer_df)
        res["summer_slope_decade"] = round(float(s_res.slope * 10.0), 3)
        res["summer_p_value"] = round(float(s_res.pvalue), 4)
        res["summer_significant"] = bool(s_res.pvalue < 0.05)
    
    if len(winter_df) >= 5:
        w_res = stats.linregress(range(len(winter_df)), winter_df)
        res["winter_slope_decade"] = round(float(w_res.slope * 10.0), 3)
        res["winter_p_value"] = round(float(w_res.pvalue), 4)
        res["winter_significant"] = bool(w_res.pvalue < 0.05)

    s_slope = res.get("summer_slope_decade", 0)
    w_slope = res.get("winter_slope_decade", 0)
    res["asymmetry_ratio"] = round(s_slope / w_slope, 2) if w_slope > 0 else round(s_slope, 2)
    res["amplification_detected"] = s_slope > w_slope

    return res

def generate_policy_brief(region_name_en: str, region_name_ar: str, slope_decade: float, seasonal: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Senior Executive Briefing: Actionable policy adaptation points for Egyptian authorities.
    """
    s_slope = seasonal.get("summer_slope_decade", slope_decade)
    return [
        {
            "sector_ar": "الأمن المائي والري (وزارة الموارد المائية)",
            "sector_en": "Water Security & Irrigation",
            "action_ar": f"تطبيق الري الذكي وتغطية وتأهيل الترع لمواجهة التسارع التبخري الصيفي المرتفع ({s_slope:+.2f}°C/عقد).",
            "action_en": "Expand modern drip irrigation and canal lining to offset elevated summer evaporative losses."
        },
        {
            "sector_ar": "الزراعة والأمن الغذائي (وزارة الزراعة)",
            "sector_en": "Agriculture & Crop Resilience",
            "action_ar": "استنباط سلالات قمح وذرة تتحمل الإجهاد الحراري وتعديل المواعيد الزراعية لتفادي ذروة موجات الحر المبكرة.",
            "action_en": "Deploy heat-tolerant wheat and maize cultivars and shift planting calendars to avoid peak thermal anomalies."
        },
        {
            "sector_ar": "الطاقة والشبكة القومية (وزارة الكهرباء)",
            "sector_en": "Energy & Grid Reliability",
            "action_ar": "تعزيز قدرات شبكات التوزيع لمجابهة أحمال التبريد القياسية والاستفادة من الإشعاع الشمسي المرتفع في مشاريع الطاقة المتجددة.",
            "action_en": "Fortify grid resilience against peak summer cooling surges while scaling solar PV generation."
        },
        {
            "sector_ar": "الصحة العامة وإدارة الأزمات (إدارة الحماية المدنية)",
            "sector_en": "Public Health & Crisis Alerts",
            "action_ar": "تفعيل منظومة الإنذار المبكر عبر رسائل الجوال لتنبيه العمالة الميدانية وكبار السن عند تجاوز مؤشر الحرارة حاجز الخطر.",
            "action_en": "Activate mobile early warning broadcasts for outdoor workers when Heat Index crosses extreme caution thresholds."
        }
    ]


def analyze_time_series(
    records: List[Dict[str, Any]], 
    variable_key: str, 
    region_name_en: str = "Target Region", 
    region_name_ar: str = "المنطقة المستهدفة"
) -> Dict[str, Any]:
    """
    Complete scientific analysis:
    1. Deseasonalization (Monthly Anomaly + 12-month Rolling Mean)
    2. Theil-Sen Slope and 95% Confidence Bounds
    3. Mann-Kendall Trend Test
    4. OLS Linear Regression
    5. Plain-Language Detective Explanation (Arabic & English)
    """
    df = pd.DataFrame(records)
    if variable_key not in df.columns or df[variable_key].isna().all():
        raise ValueError(f"Variable '{variable_key}' not found or empty.")

    # Drop missing values
    clean_df = df.dropna(subset=[variable_key]).copy()
    clean_df["date"] = pd.to_datetime(clean_df["date"])
    clean_df = clean_df.sort_values("date").reset_index(drop=True)

    n_points = int(len(clean_df))
    n_years = int(clean_df["year"].max() - clean_df["year"].min() + 1)
    min_year = int(clean_df["year"].min())
    max_year = int(clean_df["year"].max())
    
    # 1. Seasonality removal: Compute monthly climatology
    monthly_means = clean_df.groupby("month")[variable_key].transform("mean")
    clean_df["monthly_mean"] = monthly_means
    clean_df["anomaly"] = clean_df[variable_key] - clean_df["monthly_mean"]
    
    # 12-month rolling mean
    clean_df["rolling_12m"] = clean_df[variable_key].rolling(window=12, center=True).mean()

    # Annual summary series
    annual_df = clean_df.groupby("year")[variable_key].mean().reset_index()

    # Time index in years for slope calculation
    start_date = clean_df["date"].iloc[0]
    time_years = (clean_df["date"] - start_date).dt.days.values / 365.25

    # 2. Mann-Kendall test on anomalies (seasonally adjusted)
    mk_result = mann_kendall_test(clean_df["anomaly"].values)

    # 3. Theil-Sen's Slope (per year)
    sen_result = theil_sen_slope(time_years, clean_df["anomaly"].values)
    sen_slope_per_year = sen_result["slope"]
    sen_slope_per_decade = sen_slope_per_year * 10.0

    # 4. Ordinary Least Squares (OLS) Regression
    ols_res = stats.linregress(time_years, clean_df["anomaly"].values)
    trend_line = (sen_result["slope"] * time_years + sen_result["intercept"]).tolist()

    # 95% Confidence Band for the trendline
    slope_low_line = (sen_result["slope_low"] * time_years + sen_result["intercept"]).tolist()
    slope_high_line = (sen_result["slope_high"] * time_years + sen_result["intercept"]).tolist()

    # Total observed change over the analyzed period
    total_change = sen_slope_per_year * (time_years[-1] - time_years[0])
    
    var_meta = VARIABLE_METADATA.get(variable_key, {
        "name_en": variable_key,
        "name_ar": variable_key,
        "unit": ""
    })

    # 5. Scientific Detective Plain Language Generator
    is_significant = mk_result["significant"]
    p_val = mk_result["p_value"]
    unit = var_meta["unit"]
    
    direction_en = "increasing" if sen_slope_per_year > 0 else "decreasing" if sen_slope_per_year < 0 else "stable"
    direction_ar = "تصاعدياً (ارتفاع)" if sen_slope_per_year > 0 else "تنازلياً (انخفاض)" if sen_slope_per_year < 0 else "مستقراً"

    # Detective narrative construction
    if is_significant:
        sig_text_en = f"Statistically Significant (p = {p_val:.4f} < 0.05). This confirms a genuine climatic trend rather than random variation."
        sig_text_ar = f"مؤكد وذو دلالة إحصائية (قيمة p = {p_val:.4f} أقل من 0.05). وهذا يثبت علمياً أن التغير حقيقي ومستمر وليس مجرد تقلبات طبيعية عشوائية."
        confidence_badge = "High Scientific Confidence"
        confidence_badge_ar = "موثوقية علمية عالية"
    else:
        sig_text_en = f"Not Statistically Significant (p = {p_val:.4f} >= 0.05). The observed variations may be natural short-term cycles."
        sig_text_ar = f"غير مؤكد إحصائياً (قيمة p = {p_val:.4f} أكبر من 0.05). التغيرات المرصودة قد تكون ناجمة عن تقلبات دورية طبيعية قصيرة المدى."
        confidence_badge = "Moderate / Natural Variability"
        confidence_badge_ar = "تقلب طبيعي معتدل"

    # Detective answers to the 5 core questions:
    detective_answers = {
        "what_changed": {
            "en": f"{var_meta['name_en']} ({unit})",
            "ar": f"{var_meta['name_ar']} ({unit})"
        },
        "where": {
            "en": region_name_en,
            "ar": region_name_ar
        },
        "when": {
            "en": f"{min_year} to {max_year} ({n_years} years, {n_points} monthly records)",
            "ar": f"من عام {min_year} إلى {max_year} ({n_years} سنة، {n_points} قراءة شهرية)"
        },
        "how_much": {
            "en": f"{abs(sen_slope_per_decade):.3f} {unit} per decade (Total: {total_change:+.2f} {unit} over {n_years} years)",
            "ar": f"{abs(sen_slope_per_decade):.3f} {unit} لكل عقد (إجمالي التغير: {total_change:+.2f} {unit} على مدار {n_years} سنة)"
        },
        "is_significant": {
            "en": sig_text_en,
            "ar": sig_text_ar,
            "p_value": float(p_val),
            "significant": bool(is_significant),
            "badge_en": confidence_badge,
            "badge_ar": confidence_badge_ar
        }
    }

    # Format chart time series
    chart_data = {
        "labels": [str(d) for d in clean_df["date"].dt.strftime("%Y-%m").tolist()],
        "raw_values": [float(v) if pd.notna(v) else None for v in clean_df[variable_key]],
        "anomalies": [float(round(v, 4)) if pd.notna(v) else None for v in clean_df["anomaly"]],
        "rolling_12m": [float(round(v, 4)) if pd.notna(v) else None for v in clean_df["rolling_12m"]],
        "trend_line": [float(round(v, 4)) for v in trend_line],
        "slope_low_line": [float(round(v, 4)) for v in slope_low_line],
        "slope_high_line": [float(round(v, 4)) for v in slope_high_line]
    }

    # Annual chart data
    annual_chart = {
        "years": [int(y) for y in annual_df["year"].tolist()],
        "values": [float(round(v, 3)) if pd.notna(v) else None for v in annual_df[variable_key]]
    }

    # Senior Analytics: Change Point, Seasonal Asymmetry, Heat Index & Policy Brief
    pettitt_res = pettitt_test(annual_df[variable_key].values, [int(y) for y in annual_df["year"].tolist()])
    seasonal_res = analyze_seasonal_asymmetry(clean_df, variable_key)
    
    # Calculate representative Heat Index (apparent temperature)
    mean_t = float(clean_df["T2M"].mean()) if "T2M" in clean_df.columns else float(clean_df[variable_key].mean())
    mean_rh = float(clean_df["RH2M"].mean()) if "RH2M" in clean_df.columns else 50.0
    heat_index_res = compute_heat_index_celsius(mean_t, mean_rh)
    
    policy_brief = generate_policy_brief(region_name_en, region_name_ar, sen_slope_per_decade, seasonal_res)

    return {
        "variable": variable_key,
        "variable_meta": var_meta,
        "statistics": {
            "sen_slope_per_year": round(sen_slope_per_year, 5),
            "sen_slope_per_decade": round(sen_slope_per_decade, 4),
            "total_change": round(total_change, 3),
            "mann_kendall": mk_result,
            "ols_r_squared": round(ols_res.rvalue ** 2, 4),
            "ols_p_value": float(ols_res.pvalue),
            "data_points_count": n_points,
            "years_span": n_years
        },
        "detective_report": detective_answers,
        "chart_data": chart_data,
        "annual_chart": annual_chart,
        "change_point": pettitt_res,
        "seasonal_asymmetry": seasonal_res,
        "heat_index": heat_index_res,
        "policy_brief": policy_brief
    }

def run_auto_scan(records: List[Dict[str, Any]], region_name_en: str, region_name_ar: str) -> List[Dict[str, Any]]:
    """
    Scans ALL available NASA variables for the region and ranks them by:
    1. Statistical Significance (p-value ascending)
    2. Magnitude of trend
    """
    scan_results = []
    for var_key in VARIABLE_METADATA.keys():
        try:
            analysis = analyze_time_series(records, var_key, region_name_en, region_name_ar)
            stats_data = analysis["statistics"]
            p_val = stats_data["mann_kendall"]["p_value"]
            slope_dec = stats_data["sen_slope_per_decade"]
            
            # Rank score: lower p-value gets higher score, weighted by normalized trend
            is_sig = stats_data["mann_kendall"]["significant"]
            
            scan_results.append({
                "variable": var_key,
                "name_en": analysis["variable_meta"]["name_en"],
                "name_ar": analysis["variable_meta"]["name_ar"],
                "unit": analysis["variable_meta"]["unit"],
                "p_value": p_val,
                "significant": is_sig,
                "slope_per_decade": slope_dec,
                "total_change": stats_data["total_change"],
                "direction": "up" if slope_dec > 0 else "down" if slope_dec < 0 else "flat",
                "detective_report": analysis["detective_report"]
            })
        except Exception as e:
            continue

    # Sort: significant first, then by lowest p-value
    scan_results.sort(key=lambda item: (not item["significant"], item["p_value"]))
    return scan_results
