"""
Pre-cache NOAA GHCND data for all available stations.
Run once: python backend/cache_noaa.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from noaa_fetcher import REGION_STATIONS, fetch_noaa_ghcnd_monthly

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "noaa_token.txt")
if not os.path.exists(TOKEN_FILE):
    print("ERROR: noaa_token.txt not found!")
    sys.exit(1)

with open(TOKEN_FILE) as f:
    token = f.read().strip()

print(f"Token loaded. Fetching NOAA GHCND data for {len(REGION_STATIONS)} regions...\n")

success, failed = [], []
for key, info in REGION_STATIONS.items():
    print(f"  [{key}] {info['name']} ({info['id']})...")
    try:
        result = fetch_noaa_ghcnd_monthly(info["id"], start_year=2000, end_year=2023, token=token)
        if result:
            n = len(result["years"])
            print(f"    ✓ {n} years | {result['years'][0]}-{result['years'][-1]} | mean={sum(result['values'])/n:.1f}°C")
            success.append(key)
        else:
            print(f"    ✗ No data returned")
            failed.append(key)
    except Exception as e:
        print(f"    ✗ Error: {e}")
        failed.append(key)

print(f"\n=== Done: {len(success)} cached, {len(failed)} failed ===")
if success: print("Success:", success)
if failed:  print("Failed:", failed)

