import sys
sys.path.insert(0, '.')
from data_fetcher import fetch_nasa_data, PRESET_REGIONS
from analysis import analyze_time_series
from noaa_fetcher import fetch_region_noaa, compare_nasa_noaa

# Test Cairo analysis
data = fetch_nasa_data(30.0444, 31.2357, 2000, 2023)
result = analyze_time_series(data['records'], 'T2M', 'Cairo', 'القاهرة')
stats = result['statistics']
mk = stats['mann_kendall']
raw = result['chart_data']['raw_values']
print("=== Cairo T2M Analysis ===")
print(f"Records: {len(data['records'])} months")
print(f"Mean temp: {sum(raw)/len(raw):.2f} C")
print(f"Sen slope: {stats['sen_slope_per_decade']:.4f} C/decade")
print(f"Mann-Kendall p: {mk['p_value']:.4f}")
print(f"Significant: {mk['significant']}")
print(f"Detective: {result['detective_report']['what_changed']['en']}")

# Test Arabia NOAA
print()
print("=== Arabia NOAA ===")
noaa = fetch_region_noaa('arabia')
if noaa:
    print(f"Years: {noaa['years'][:3]}...{noaa['years'][-3:]}")
    print(f"Values: {[round(v,1) for v in noaa['values'][:3]]}...")
    print(f"Mean: {sum(noaa['values'])/len(noaa['values']):.2f} C")
else:
    print("No data")

# Test NOAA compare for Arabia
print()
print("=== NASA x NOAA Compare for Arabia ===")
nasa_data = fetch_nasa_data(23.69, 45.07, 2000, 2023)
nasa_res = analyze_time_series(nasa_data['records'], 'T2M', 'Arabia', 'الجزيرة')
annual = nasa_res['annual_chart']
if noaa:
    comparison = compare_nasa_noaa(annual['years'], annual['values'], noaa)
    print(f"Bias: {comparison['bias_celsius']:.3f} C")
    print(f"RMSE: {comparison['rmse_celsius']:.3f} C")
    print(f"Corr r: {comparison['correlation_r']:.3f}")
    print(f"Agreement: {comparison['agreement']}")
    print(f"Overlapping years: {comparison['overlapping_years']}")

