with open('frontend/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

checks = [
    ('6snova Insignia Logo', '6snova Planetary Intelligence Insignia' in c),
    ('Earth Satellite Composite Image', 'AB6AXuA6LmmZ1hA9X' in c),
    ('Radar Conic Sweep', 'radar-sweep' in c),
    ('HUD Coordinates Overlay', 'SUBSAT POINT:' in c),
    ('Center Target Reticle', 'pulse-beacon' in c),
    ('Scrubbable Orbital Slider', 'NOAA Predictive Run' in c),
    ('Google Crisis Alert Relay', 'Google Public Safety &amp; Android Emergency Alert Relay' in c),
    ('Sensor Bus Health', 'Sensor Bus Health' in c),
    ('NOAA Ground Truth View', 'view-noaa-val' in c),
    ('Anomaly Table', 'anomaly-tbody' in c),
    ('Forecast Overlay', 'forecast-overlay' in c),
    ('Chart.js & app.js', 'app.js' in c and 'chart.umd.min.js' in c)
]

for name, passed in checks:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
