"""Quick test to debug NOAA 400 error."""
import requests

TOKEN = "XigWcoqjXcvOqJKyXtceWIlYmEsQWlFd"
H = {"token": TOKEN}
BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"

# Test Saudi Arabia station (high coverage)
station = "GHCND:SAM00040437"
params = {
    "datasetid": "GHCND",
    "stationid": station,
    "datatypeid": "TMAX",
    "startdate": "2000-01-01",
    "enddate": "2004-12-31",
    "limit": 1000,
    "units": "metric",
}
r = requests.get(f"{BASE}/data", headers=H, params=params, timeout=20)
print("Status:", r.status_code)
print("Response:", r.text[:500])

# Test without units
params2 = {k: v for k, v in params.items() if k != "units"}
r2 = requests.get(f"{BASE}/data", headers=H, params=params2, timeout=20)
print("\nWithout units - Status:", r2.status_code)
print("Response:", r2.text[:300])

