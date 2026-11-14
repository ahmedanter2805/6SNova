import sys
sys.path.insert(0, '.')
from data_fetcher import PRESET_REGIONS, fetch_nasa_data

print("=== NASA Cache Check ===")
ok = 0
for r in PRESET_REGIONS:
    try:
        data = fetch_nasa_data(r['lat'], r['lon'], 2000, 2023)
        recs = data.get('records', [])
        t_vals = [d['T2M'] for d in recs if d.get('T2M') is not None]
        if t_vals:
            print("  [OK] {:12s} {:3d} months | T2M: {:.1f} to {:.1f}C".format(
                r['id'], len(recs), min(t_vals), max(t_vals)))
            ok += 1
        else:
            print("  [!!] {:12s} No T2M data!".format(r['id']))
    except Exception as e:
        print("  [ERR] {:12s} {}".format(r['id'], e))

print("Result: {}/{} regions OK".format(ok, len(PRESET_REGIONS)))

