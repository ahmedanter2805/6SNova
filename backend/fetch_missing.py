"""
Fetch missing NASA POWER cache files for Siberia and Sahel.
"""
import sys, os, json, requests

sys.path.insert(0, '.')
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

MISSING = [
    {"id": "siberia",  "lat": 61.52,  "lon": 105.19},
    {"id": "sahel",    "lat": 15.5,   "lon": 17.5},
]

VARIABLES = "T2M,PRECTOTCORR,GWETTOP,RH2M,WS2M,ALLSKY_SFC_SW_DWN"

def fetch_and_cache(lat, lon, name):
    lat_r = round(lat, 2)
    lon_r = round(lon, 2)
    cache_file = os.path.join(CACHE_DIR, f"nasa_power_{lat_r}_{lon_r}_2000_2023.json")
    
    if os.path.exists(cache_file):
        print(f"  [{name}] Already cached: {cache_file}")
        return True

    url = (
        f"https://power.larc.nasa.gov/api/temporal/monthly/point?"
        f"parameters={VARIABLES}&community=AG"
        f"&longitude={lon_r}&latitude={lat_r}"
        f"&start=2000&end=2023&format=JSON"
    )
    headers = {"User-Agent": "Mozilla/5.0 TrendLens/1.0"}
    print(f"  [{name}] Fetching from NASA POWER API...")
    try:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        raw = r.json()
        
        params = raw.get("properties", {}).get("parameter", {})
        first_param = list(params.keys())[0]
        all_keys = sorted(params[first_param].keys())
        
        records = []
        for key in all_keys:
            if len(key) == 6 and not key.endswith("13"):
                year = int(key[:4])
                month = int(key[4:6])
                entry = {"date": f"{year}-{month:02d}-01", "year": year, "month": month, "period": key}
                for p, values in params.items():
                    val = values.get(key, None)
                    entry[p] = val if val is not None and val != -999 else None
                records.append(entry)
        
        payload = {
            "metadata": {"latitude": lat, "longitude": lon, "start_year": 2000, "end_year": 2023,
                         "data_source": "NASA POWER / MERRA-2"},
            "records": records
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"  [{name}] Cached {len(records)} months -> {cache_file}")
        return True
    except Exception as e:
        print(f"  [{name}] ERROR: {e}")
        return False

print("Fetching missing NASA POWER cache files...")
for m in MISSING:
    fetch_and_cache(m['lat'], m['lon'], m['id'])
print("Done.")

