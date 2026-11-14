"""Test single year NOAA fetch to verify data format."""
import requests

TOKEN = "XigWcoqjXcvOqJKyXtceWIlYmEsQWlFd"
H = {"token": TOKEN}
BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"

# Saudi Arabia station - single year
r = requests.get(f"{BASE}/data", headers=H, params={
    "datasetid": "GHCND",
    "stationid": "GHCND:SAM00040437",
    "datatypeid": "TMAX",
    "startdate": "2020-01-01",
    "enddate": "2020-12-31",
    "limit": 10,
}, timeout=20)
print("Saudi TMAX 2020:", r.status_code)
if r.status_code == 200:
    data = r.json()
    results = data.get("results", [])
    for rec in results[:5]:
        print(f"  date={rec['date'][:10]}, value={rec['value']}, datatype={rec['datatype']}")
    # Check metadata
    meta = data.get("metadata", {}).get("resultset", {})
    print(f"  total_records: {meta.get('count')}")

# Greenland station
r2 = requests.get(f"{BASE}/data", headers=H, params={
    "datasetid": "GHCND",
    "stationid": "GHCND:GL000004250",
    "datatypeid": "TMAX",
    "startdate": "2020-01-01",
    "enddate": "2020-12-31",
    "limit": 5,
}, timeout=20)
print("\nGreenland TMAX 2020:", r2.status_code)
if r2.status_code == 200:
    for rec in r2.json().get("results", [])[:3]:
        print(f"  date={rec['date'][:10]}, value={rec['value']}")

