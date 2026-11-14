"""
Search NOAA CDO stations for all 10 preset regions and fetch GSOM TAVG data.
"""
import requests
import json
import sys

TOKEN = "XigWcoqjXcvOqJKyXtceWIlYmEsQWlFd"
BASE  = "https://www.ncei.noaa.gov/cdo-web/api/v2"
H     = {"token": TOKEN}

REGIONS = [
    {"key": "cairo",      "name": "Cairo, Egypt",         "lat": 30.0444, "lon": 31.2357, "extent": "29.5,30.9,31.8,32.0"},
    {"key": "amazon",     "name": "Amazon Rainforest",    "lat": -3.47,   "lon": -62.22,  "extent": "-5.0,-63.5,-2.0,-61.0"},
    {"key": "siberia",    "name": "Siberia",              "lat": 61.52,   "lon": 105.19,  "extent": "60.0,104.0,63.0,107.0"},
    {"key": "sahel",      "name": "Sahel, Africa",        "lat": 15.5,    "lon": 17.5,    "extent": "13.5,16.0,17.0,19.0"},
    {"key": "california", "name": "Central Valley, CA",   "lat": 36.78,   "lon": -119.42, "extent": "36.0,-120.5,37.5,-118.5"},
    {"key": "arabia",     "name": "Arabian Peninsula",    "lat": 23.69,   "lon": 45.07,   "extent": "22.5,44.0,25.0,46.0"},
    {"key": "greenland",  "name": "Greenland",            "lat": 72.0,    "lon": -40.0,   "extent": "70.0,-42.0,74.0,-38.0"},
    {"key": "india",      "name": "South Asian Monsoon",  "lat": 20.59,   "lon": 78.96,   "extent": "19.0,77.5,22.0,80.5"},
    {"key": "patagonia",  "name": "Patagonia",            "lat": -45.0,   "lon": -69.0,   "extent": "-46.5,-70.5,-43.5,-67.5"},
    {"key": "baghdad",    "name": "Baghdad",              "lat": 33.32,   "lon": 44.37,   "extent": "32.5,43.5,34.0,45.0"},
]

station_map = {}

for reg in REGIONS:
    print(f"\n--- {reg['name']} ---")
    # Search stations with GSOM TAVG data
    r = requests.get(f"{BASE}/stations", headers=H, params={
        "datasetid":   "GSOM",
        "datatypeid":  "TAVG",
        "extent":      reg["extent"],
        "startdate":   "2000-01-01",
        "enddate":     "2023-12-31",
        "limit":       5,
    }, timeout=15)

    if r.status_code != 200:
        print(f"  Search failed: {r.status_code}")
        # Try without datatypeid filter
        r2 = requests.get(f"{BASE}/stations", headers=H, params={
            "datasetid":  "GSOM",
            "extent":     reg["extent"],
            "startdate":  "2000-01-01",
            "enddate":    "2023-12-31",
            "limit":      5,
        }, timeout=15)
        if r2.status_code == 200:
            data2 = r2.json().get("results", [])
            for s in data2[:3]:
                print(f"  (no-filter) {s['id']} | {s['name']} | cov={s.get('datacoverage','?')}")
        continue

    results = r.json().get("results", [])
    if not results:
        print(f"  No GSOM TAVG stations found in extent {reg['extent']}")
        # Try GHCND monthly
        r3 = requests.get(f"{BASE}/stations", headers=H, params={
            "datasetid":  "GHCND",
            "datatypeid": "TAVG",
            "extent":     reg["extent"],
            "startdate":  "2000-01-01",
            "enddate":    "2023-12-31",
            "limit":      5,
        }, timeout=15)
        if r3.status_code == 200:
            res3 = r3.json().get("results", [])
            for s in res3[:3]:
                print(f"  (GHCND) {s['id']} | {s['name']} | cov={s.get('datacoverage','?')}")
        continue

    for s in results[:3]:
        print(f"  {s['id']} | {s['name']} | cov={s.get('datacoverage','?')}")
    station_map[reg["key"]] = results[0]["id"]

print("\n\n=== Station Map ===")
print(json.dumps(station_map, indent=2))

