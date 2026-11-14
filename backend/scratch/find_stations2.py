"""
Fetch NOAA GHCND daily TMAX+TMIN for available stations and build monthly means.
Then cache and compare with NASA POWER.
"""
import requests, json, sys
from pathlib import Path
from collections import defaultdict

TOKEN = "XigWcoqjXcvOqJKyXtceWIlYmEsQWlFd"
BASE  = "https://www.ncei.noaa.gov/cdo-web/api/v2"
H     = {"token": TOKEN}

# Best available GHCND stations with good coverage
BEST_STATIONS = {
    "california": {"id": "GHCND:USC00040343", "name": "Ash Mountain, CA"},
    "india":      {"id": "GHCND:IN012030700", "name": "Amraoti, India"},
    "patagonia":  {"id": "GHCND:AR000087860", "name": "Comodoro Rivadavia, Argentina"},
}

# Wider extent search for Cairo + Baghdad + others
WIDER_EXTENTS = {
    "cairo":   {"extent": "29.0,30.0,31.5,32.5", "country": "EG"},
    "baghdad": {"extent": "32.0,43.0,34.5,46.0", "country": "IQ"},
    "sahel":   {"extent": "12.0,10.0,17.0,20.0", "country": "NE"},  # Niger
    "greenland":{"extent": "64.0,-52.0,76.0,-35.0","country": "GL"},
    "siberia": {"extent": "58.0,100.0,65.0,110.0","country": "RS"},
    "arabia":  {"extent": "21.0,43.0,26.0,47.0",  "country": "SA"},
    "amazon":  {"extent": "-5.0,-63.5,0.0,-55.0",  "country": "BR"},
}

print("=== Searching wider extents ===")
for key, info in WIDER_EXTENTS.items():
    print(f"\n{key}:")
    r = requests.get(f"{BASE}/stations", headers=H, params={
        "datasetid": "GHCND",
        "datatypeid": "TMAX",
        "countrycode": info["country"],
        "extent": info["extent"],
        "startdate": "2000-01-01",
        "enddate": "2023-12-31",
        "sortfield": "datacoverage",
        "sortorder": "desc",
        "limit": 5
    }, timeout=20)
    if r.status_code == 200:
        results = r.json().get("results", [])
        for s in results[:3]:
            print(f"  {s['id']} | {s['name']} | cov={s.get('datacoverage','?')}")
        if results:
            best = results[0]
            BEST_STATIONS[key] = {"id": best["id"], "name": best["name"]}
    else:
        print(f"  Error {r.status_code}")

print("\n\n=== Final Best Station Map ===")
print(json.dumps(BEST_STATIONS, indent=2))

# Save to file for use in noaa_fetcher.py
out = Path(__file__).parent / "noaa_stations.json"
out.write_text(json.dumps(BEST_STATIONS, indent=2))
print(f"\nSaved to {out}")

