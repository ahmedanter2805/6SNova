"""
TrendLens Forecast Engine
=========================
Uses Theil-Sen slope (already computed by Mann-Kendall analysis) to project
future climate values up to 2050, with 95% confidence interval bands.

Methodology:
  - Projection method: Sen's Slope extrapolation (non-parametric, robust)
  - Confidence interval: Propagated from Sen's slope lower/upper bounds
  - Baseline: Last observed value + slope × years_ahead
  - Cited per: "Statistical test methods to detect trends in time series data"
    (Space Apps Challenge official resource)

NOT a GCM model — explicitly declared as linear trend extrapolation.
"""

import numpy as np
from typing import Dict, Any, List, Optional


def generate_forecast(
    raw_values: List[float],
    labels: List[str],
    sen_slope_per_year: float,
    sen_slope_low_per_year: float,
    sen_slope_high_per_year: float,
    intercept: float,
    forecast_years: int = 26,          # 2024 → 2050
    last_data_year: int = 2023,
) -> Dict[str, Any]:
    """
    Generates an annual forecast from last_data_year+1 to last_data_year+forecast_years.

    Returns:
        {
          forecast_years:   [2024, 2025, ..., 2050]
          forecast_values:  [projected mean values]
          ci_upper:         [upper 95% CI]
          ci_lower:         [lower 95% CI]
          baseline_value:   last observed annual mean
          slope_per_year:   Sen's slope used
          slope_per_decade: ...
          narrative_en:     plain-language projection statement
          narrative_ar:     Arabic version
        }
    """
    n = len(raw_values)
    if n == 0:
        return {}

    # Baseline: mean of last 12 observations (last ~1 year)
    baseline = float(np.mean(raw_values[-12:]) if n >= 12 else np.mean(raw_values))

    years_out   = list(range(1, forecast_years + 1))
    proj_years  = [last_data_year + y for y in years_out]

    forecast    = [round(baseline + sen_slope_per_year * y, 4) for y in years_out]
    ci_upper    = [round(baseline + sen_slope_high_per_year * y, 4) for y in years_out]
    ci_lower    = [round(baseline + sen_slope_low_per_year * y, 4) for y in years_out]

    total_proj  = forecast[-1] - baseline
    slope_dec   = sen_slope_per_year * 10.0
    sign        = "+" if total_proj >= 0 else ""
    direction_en = "rise" if total_proj > 0 else "fall"
    direction_ar = "الارتفاع" if total_proj > 0 else "الانخفاض"

    narrative_en = (
        f"If the current trend continues at {slope_dec:+.3f} units/decade "
        f"(Theil-Sen slope, 95% CI: [{sen_slope_low_per_year*10:.3f}, {sen_slope_high_per_year*10:.3f}] /decade), "
        f"values are projected to {direction_en} by {sign}{total_proj:.2f} units "
        f"by {proj_years[-1]}. "
        f"This is a linear extrapolation — not a climate model simulation."
    )
    narrative_ar = (
        f"إذا استمر الاتجاه الحالي بمعدل {slope_dec:+.3f} وحدة/عقد "
        f"(ميل ثايل-سن، فترة ثقة 95%: [{sen_slope_low_per_year*10:.3f}، {sen_slope_high_per_year*10:.3f}] /عقد)، "
        f"يُتوقع {direction_ar} بمقدار {sign}{total_proj:.2f} وحدة "
        f"بحلول عام {proj_years[-1]}. "
        f"هذا توقع خطي استقرائي — وليس نموذج مناخياً."
    )

    return {
        "forecast_years":        [int(y) for y in proj_years],
        "forecast_values":       forecast,
        "ci_upper":              ci_upper,
        "ci_lower":              ci_lower,
        "baseline_value":        round(baseline, 4),
        "slope_per_year":        round(sen_slope_per_year, 5),
        "slope_per_decade":      round(slope_dec, 4),
        "total_projected_change": round(total_proj, 3),
        "narrative_en":          narrative_en,
        "narrative_ar":          narrative_ar,
    }


def build_full_timeline(
    historical_labels: List[str],
    historical_annual_years: List[int],
    historical_annual_values: List[float],
    forecast_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merges historical annual data with forecast for a combined chart.
    """
    return {
        "historical_years":  historical_annual_years,
        "historical_values": historical_annual_values,
        "forecast_years":    forecast_result.get("forecast_years", []),
        "forecast_values":   forecast_result.get("forecast_values", []),
        "ci_upper":          forecast_result.get("ci_upper", []),
        "ci_lower":          forecast_result.get("ci_lower", []),
        "baseline_value":    forecast_result.get("baseline_value"),
    }

