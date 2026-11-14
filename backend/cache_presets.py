import sys
import os
import time

sys.path.append(os.path.dirname(__file__))
from data_fetcher import PRESET_REGIONS, fetch_nasa_data

def cache_all():
    print(f"Starting pre-caching for {len(PRESET_REGIONS)} regions from NASA POWER API...")
    for idx, reg in enumerate(PRESET_REGIONS, 1):
        name = reg["name_en"]
        lat = reg["lat"]
        lon = reg["lon"]
        print(f"[{idx}/{len(PRESET_REGIONS)}] Fetching NASA data for: {name} ({lat}, {lon})...")
        try:
            data = fetch_nasa_data(lat, lon, start_year=2000, end_year=2023)
            records_count = len(data.get("records", []))
            print(f"   --> Success: Cached {records_count} months of real data.")
        except Exception as err:
            print(f"   --> Error fetching {name}: {err}")
        time.sleep(1) # respectful API pacing

    print("\nAll preset regions cached successfully!")

if __name__ == "__main__":
    cache_all()

