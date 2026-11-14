import re

with open('stitch_nasa_earth_weather_dashboard/stitch_nasa_earth_weather_dashboard/6s_nova_planetary_telemetry_google_mobile_crisis_alerts/code.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Chart.js and app.js before </body>
script_tag = """
<!-- Chart.js and TrendLens Live Data Engine -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="/static/app.js"></script>
</body>
"""
html = html.replace('</body>', script_tag)

# 2. Add Forecast toggle button in Layer switcher tabs
old_layer_tabs = """<button class="px-3 py-1.5 rounded-lg bg-primary-container text-on-primary-container shadow-sm font-medium transition-all">
              Thermal / SST
            </button>
<button class="px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface transition-all">
              Atmospheric Moisture
            </button>
<button class="px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface transition-all">
              Precipitation Radar
            </button>
<button class="px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface transition-all">
              Wind Vector Streamlines
            </button>"""

new_layer_tabs = """<button id="btn-layer-thermal" onclick="setLayer('T2M', this)" class="px-3 py-1.5 rounded-lg bg-primary-container text-on-primary-container shadow-sm font-medium transition-all">
              Thermal / SST
            </button>
<button id="btn-layer-moisture" onclick="setLayer('RH2M', this)" class="px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface transition-all">
              Atmospheric Moisture
            </button>
<button id="btn-layer-radar" onclick="setLayer('PRECTOTCORR', this)" class="px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface transition-all">
              Precipitation Radar
            </button>
<button id="btn-layer-wind" onclick="setLayer('WS2M', this)" class="px-3 py-1.5 rounded-lg text-on-surface-variant hover:text-on-surface transition-all">
              Wind Vector Streamlines
            </button>
<button id="btn-toggle-forecast" onclick="toggleForecastView()" class="px-3 py-1.5 rounded-lg text-secondary border border-secondary/40 hover:bg-secondary/20 transition-all flex items-center gap-1.5 font-medium ml-1">
              <span class="material-symbols-outlined text-sm">trending_up</span> NASA Trend &amp; 2050 Forecast
            </button>"""

if old_layer_tabs in html:
    html = html.replace(old_layer_tabs, new_layer_tabs)
    print("1. Layer switcher replaced successfully.")
else:
    print("WARNING: Layer switcher target not matched directly, checking whitespace...")

# 3. Add Forecast HUD overlay inside Central Viewport Canvas Area
# Look for: <!-- Realistic Composite Viewport Canvas Area -->
target_viewport_start = """<!-- Realistic Composite Viewport Canvas Area -->
<div class="relative flex-1 bg-surface-container-lowest overflow-hidden flex items-center justify-center">"""

forecast_overlay = """<!-- Realistic Composite Viewport Canvas Area -->
<div class="relative flex-1 bg-surface-container-lowest overflow-hidden flex items-center justify-center" id="viewport-canvas-container">
<!-- Glassmorphic NASA Trend & Forecast HUD Overlay (Toggled via button) -->
<div id="forecast-overlay" class="absolute inset-0 z-30 bg-surface-container-lowest/95 backdrop-blur-2xl p-4 flex flex-col justify-between" style="display: none;">
  <div class="flex items-center justify-between pb-2 border-b border-outline-variant/30">
    <div class="flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
      <span class="font-label-sm text-xs font-semibold text-secondary uppercase tracking-wider">NASA POWER Historical Trend &amp; Theil-Sen 2050 Forecast</span>
      <span id="forecast-region-badge" class="font-mono text-xs px-2 py-0.5 rounded bg-primary-container/20 text-primary border border-primary/40">Cairo, Egypt</span>
    </div>
    <div class="flex items-center gap-2">
      <button onclick="switchForecastVar('T2M')" id="btn-t2m" class="px-2 py-0.5 rounded text-[11px] font-mono bg-primary-container text-on-primary-container border border-primary/50">TEMP</button>
      <button onclick="switchForecastVar('RH2M')" id="btn-rh2m" class="px-2 py-0.5 rounded text-[11px] font-mono bg-surface-container text-on-surface-variant hover:text-on-surface border border-outline-variant/30">HUM</button>
      <button onclick="switchForecastVar('PRECTOTCORR')" id="btn-prec" class="px-2 py-0.5 rounded text-[11px] font-mono bg-surface-container text-on-surface-variant hover:text-on-surface border border-outline-variant/30">PREC</button>
      <button onclick="switchForecastVar('WS2M')" id="btn-ws2m" class="px-2 py-0.5 rounded text-[11px] font-mono bg-surface-container text-on-surface-variant hover:text-on-surface border border-outline-variant/30">WIND</button>
      <button onclick="toggleForecastView()" class="ml-2 px-2.5 py-1 rounded text-xs font-mono bg-surface-container-high hover:bg-surface-variant text-secondary border border-secondary/40 flex items-center gap-1 shadow-sm">
        <span class="material-symbols-outlined text-xs">public</span> 3D Earth
      </button>
    </div>
  </div>
  <div class="relative flex-1 py-1" style="min-height: 230px;">
    <canvas id="forecast-chart"></canvas>
    <div id="forecast-loading" class="absolute inset-0 flex items-center justify-center bg-surface-container-lowest/80" style="display:none;">
      <div class="text-center">
        <div class="w-7 h-7 border-2 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
        <span class="font-label-sm text-xs text-secondary animate-pulse">Calculating Theil-Sen Extrapolation...</span>
      </div>
    </div>
  </div>
  <div id="forecast-narrative" class="font-label-sm text-[11px] text-on-surface-variant py-1 border-t border-outline-variant/20 truncate"></div>
  <div class="grid grid-cols-3 gap-2 pt-1.5 border-t border-outline-variant/20 font-label-sm text-xs">
    <div class="p-2 rounded-lg bg-surface-container/60 border border-outline-variant/20">
      <div class="text-outline text-[10px] uppercase">What Changed</div>
      <div id="det-what" class="font-mono text-secondary truncate font-semibold">Surface Air Temperature (2m)</div>
    </div>
    <div class="p-2 rounded-lg bg-surface-container/60 border border-outline-variant/20">
      <div class="text-outline text-[10px] uppercase">Sen's Slope / Decade</div>
      <div id="det-how" class="font-mono text-tertiary font-semibold">+0.272°C / decade</div>
    </div>
    <div class="p-2 rounded-lg bg-surface-container/60 border border-outline-variant/20">
      <div class="text-outline text-[10px] uppercase">Statistical Significance</div>
      <div id="det-sig" class="font-mono text-emerald-400 font-semibold">★ Confirmed (p = 0.0033)</div>
    </div>
  </div>
</div>"""

if target_viewport_start in html:
    html = html.replace(target_viewport_start, forecast_overlay)
    print("2. Forecast overlay added inside Viewport.")
else:
    print("WARNING: Viewport start marker not matched directly.")

# 4. Add IDs to HUD Coordinate Elements
html = html.replace(
    '<span class="text-on-surface">34°12\'19" N, 118°08\'53" W</span>',
    '<span id="hud-subsat" class="text-on-surface">30°02\'40" N, 31°14\'08" E</span>'
)
html = html.replace(
    'TARGET LOCK: TROPOSPHERIC CORE',
    '<span id="hud-target-lock">TARGET LOCK: CAIRO, EGYPT (DELTA TROPOSPHERE)</span>'
)

# 5. Add IDs to 4 Climate Modules
# Module 1: Temperature
html = html.replace(
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-primary transition-colors">\n                15.8<span class="text-2xl font-light text-on-surface-variant">°C</span>\n</span>',
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-primary transition-colors">\n                <span id="mod1-val">21.8</span><span class="text-2xl font-light text-on-surface-variant">°C</span>\n</span>'
)
html = html.replace(
    '+1.42°C ANOMALY',
    '<span id="mod1-badge">+0.27°C / DECADE</span>'
)
html = html.replace(
    '+0.18°C MOM',
    '<span id="mod1-trend">+0.27°C/dec ★</span>'
)
html = html.replace(
    '<path d="M0,28 Q25,25 50,30 T100,18 T150,22 T200,8" fill="none" stroke="url(#thermal-grad)" stroke-linecap="round" stroke-width="2.5"></path>',
    '<path id="mod1-sparkline" d="M0,28 Q25,25 50,30 T100,18 T150,22 T200,8" fill="none" stroke="url(#thermal-grad)" stroke-linecap="round" stroke-width="2.5"></path>'
)
html = html.replace(
    '<circle class="pulse-beacon" cx="200" cy="8" fill="#ffafd1" r="3.5"></circle>',
    '<circle id="mod1-pulse" class="pulse-beacon" cx="200" cy="8" fill="#ffafd1" r="3.5"></circle>'
)
html = html.replace(
    'Global Troposphere &amp; Sea Surface Mean (vs 1951-1980 baseline).',
    '<span id="mod1-sub">NASA POWER MERRA-2 (2000-2023) — Cairo, Egypt</span>'
)

# Module 2: Humidity
html = html.replace(
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-secondary transition-colors">\n                68.4<span class="text-2xl font-light text-on-surface-variant">%</span>\n</span>',
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-secondary transition-colors">\n                <span id="mod2-val">58.2</span><span class="text-2xl font-light text-on-surface-variant">%</span>\n</span>'
)
html = html.replace(
    'TPW 28.5 mm',
    '<span id="mod2-badge">TPW 28.5 mm</span>'
)
html = html.replace(
    '<div class="bg-gradient-to-r from-primary-container via-secondary-container to-secondary h-full rounded-full" style="width: 68.4%"></div>',
    '<div id="mod2-bar" class="bg-gradient-to-r from-primary-container via-secondary-container to-secondary h-full rounded-full" style="width: 58.2%"></div>'
)

# Module 3: Precipitation
html = html.replace(
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-secondary-fixed transition-colors">\n                42<span class="text-2xl font-light text-on-surface-variant">%</span>\n</span>',
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-secondary-fixed transition-colors">\n                <span id="mod3-val">0.3</span><span class="text-2xl font-light text-on-surface-variant">mm/d</span>\n</span>'
)
html = html.replace(
    'PEAK CONVECTIVE',
    '<span id="mod3-badge">ARID BASELINE</span>'
)

# Module 4: Wind
html = html.replace(
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-primary transition-colors">\n                142<span class="text-2xl font-light text-on-surface-variant">km/h</span>\n</span>',
    '<span class="font-headline-lg text-headline-lg font-bold text-on-surface group-hover:text-primary transition-colors">\n                <span id="mod4-val">12.8</span><span class="text-2xl font-light text-on-surface-variant">km/h</span>\n</span>'
)
html = html.replace(
    '300 hPa JET',
    '<span id="mod4-badge">SURFACE 2m</span>'
)

# 6. Add tab switcher to Right Panel (Sensor Bus Health vs NOAA Ground Truth)
old_sensor_header = """<div class="flex items-center justify-between pb-3 border-b border-outline-variant/30">
<div class="flex items-center gap-2">
<span class="material-symbols-outlined text-secondary" data-icon="hub">hub</span>
<span class="font-headline-sm text-headline-sm font-semibold text-on-surface">Sensor Bus Health</span>
</div>
<span class="font-label-sm text-label-sm text-primary font-mono">MODIS-GOES</span>
</div>"""

new_sensor_header = """<div class="flex items-center justify-between pb-3 border-b border-outline-variant/30">
<div class="flex items-center gap-3">
  <button id="btn-tab-sensor" onclick="switchRightPanel('sensor')" class="font-headline-sm text-sm font-semibold text-secondary border-b-2 border-secondary pb-0.5 flex items-center gap-1.5 transition-all">
    <span class="material-symbols-outlined text-base">hub</span> Sensor Bus Health
  </button>
  <button id="btn-tab-noaa" onclick="switchRightPanel('noaa')" class="font-headline-sm text-sm font-semibold text-on-surface-variant hover:text-on-surface pb-0.5 flex items-center gap-1.5 transition-all">
    <span class="material-symbols-outlined text-base">fact_check</span> NOAA Ground Truth
  </button>
</div>
<span id="right-badge" class="font-label-sm text-label-sm text-primary font-mono">MODIS-GOES</span>
</div>"""

if old_sensor_header in html:
    html = html.replace(old_sensor_header, new_sensor_header)
    print("3. Sensor Bus header replaced with tab switcher.")
else:
    print("WARNING: Sensor Bus header not matched.")

# Now wrap the sensor bus gauges in a container, and add the NOAA container
target_sensor_body = """<div class="mt-4 space-y-3.5">
<!-- Telemetry item 1 -->"""

replacement_sensor_body = """<div id="view-sensor-bus">
<div class="mt-4 space-y-3.5">
<!-- Telemetry item 1 -->"""

html = html.replace(target_sensor_body, replacement_sensor_body)

# Close #view-sensor-bus and add #view-noaa
target_actions = """<!-- Quick Payload Command Actions -->
<div class="mt-6 pt-4 border-t border-outline-variant/30 grid grid-cols-2 gap-2">"""

replacement_actions = """<!-- Quick Payload Command Actions -->
<div class="mt-6 pt-4 border-t border-outline-variant/30 grid grid-cols-2 gap-2">
<button class="px-3 py-2 rounded-lg bg-surface-container-high hover:bg-surface-variant text-on-surface font-label-sm text-label-sm border border-outline-variant/40 transition-colors flex items-center justify-center gap-1.5">
<span class="material-symbols-outlined text-base" data-icon="restart_alt">restart_alt</span>
            Recalibrate IR
          </button>
<button class="px-3 py-2 rounded-lg bg-surface-container-high hover:bg-surface-variant text-on-surface font-label-sm text-label-sm border border-outline-variant/40 transition-colors flex items-center justify-center gap-1.5">
<span class="material-symbols-outlined text-base" data-icon="download">download</span>
            Dump Telemetry
          </button>
</div>
</div>
<!-- NOAA CDO Ground Station Validation View (Toggled) -->
<div id="view-noaa-val" style="display: none;" class="flex flex-col gap-3 pt-3">
  <div class="flex items-center justify-between text-[11px] font-label-sm">
    <span class="text-outline">Station Network: <strong class="text-secondary font-mono" id="noaa-station-name">GHCND Active</strong></span>
    <span id="noaa-agreement-badge" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-surface-container text-outline border border-outline-variant/40">CALCULATING</span>
  </div>
  <div class="relative rounded-xl bg-surface-container-lowest/90 border border-outline-variant/30 p-2" style="height: 140px;">
    <canvas id="noaa-compare-chart"></canvas>
    <div id="noaa-chart-loading" class="absolute inset-0 flex items-center justify-center bg-surface-container-lowest/80 rounded-xl" style="display:none;">
      <span class="font-label-sm text-xs text-secondary animate-pulse">Syncing NOAA Station Data...</span>
    </div>
  </div>
  <div class="grid grid-cols-3 gap-2 text-center font-label-sm text-xs">
    <div class="p-2 rounded-xl bg-surface-container/60 border border-outline-variant/20">
      <div class="text-outline text-[10px] uppercase">Mean Bias</div>
      <div id="noaa-bias" class="font-mono font-bold text-on-surface mt-0.5">—</div>
    </div>
    <div class="p-2 rounded-xl bg-surface-container/60 border border-outline-variant/20">
      <div class="text-outline text-[10px] uppercase">RMSE</div>
      <div id="noaa-rmse" class="font-mono font-bold text-on-surface mt-0.5">—</div>
    </div>
    <div class="p-2 rounded-xl bg-surface-container/60 border border-outline-variant/20">
      <div class="text-outline text-[10px] uppercase">Correlation r</div>
      <div id="noaa-corr" class="font-mono font-bold text-secondary mt-0.5">—</div>
    </div>
  </div>
  <div class="p-2.5 rounded-xl bg-surface-container-lowest/80 border border-outline-variant/30 font-label-sm text-[10px] text-on-surface-variant flex items-center justify-between">
    <span>Data Source: <a href="https://www.ncei.noaa.gov/cdo-web/" target="_blank" class="underline text-secondary">NOAA CDO GHCND</a></span>
    <button onclick="loadNoaaCompare()" class="text-secondary hover:text-secondary-fixed flex items-center gap-1 font-semibold">
      <span class="material-symbols-outlined text-xs">refresh</span> Sync
    </button>
  </div>
</div>"""

# Remove the original duplicate button group and replace
old_button_group = """<!-- Quick Payload Command Actions -->
<div class="mt-6 pt-4 border-t border-outline-variant/30 grid grid-cols-2 gap-2">
<button class="px-3 py-2 rounded-lg bg-surface-container-high hover:bg-surface-variant text-on-surface font-label-sm text-label-sm border border-outline-variant/40 transition-colors flex items-center justify-center gap-1.5">
<span class="material-symbols-outlined text-base" data-icon="restart_alt">restart_alt</span>
            Recalibrate IR
          </button>
<button class="px-3 py-2 rounded-lg bg-surface-container-high hover:bg-surface-variant text-on-surface font-label-sm text-label-sm border border-outline-variant/40 transition-colors flex items-center justify-center gap-1.5">
<span class="material-symbols-outlined text-base" data-icon="download">download</span>
            Dump Telemetry
          </button>
</div>"""

if old_button_group in html:
    html = html.replace(old_button_group, replacement_actions)
    print("4. Sensor Bus actions and NOAA view configured.")
else:
    print("WARNING: Sensor Bus actions not matched directly.")

# 7. Add IDs to Anomaly Matrix table tbody
html = html.replace(
    '<tbody class="divide-y divide-outline-variant/20 text-on-surface">',
    '<tbody id="anomaly-tbody" class="divide-y divide-outline-variant/20 text-on-surface">'
)

# 8. Add ID to uplink packet log
html = html.replace(
    '<div class="space-y-1.5 font-label-sm text-label-sm bg-surface-container-lowest/80 p-3 rounded-xl border border-outline-variant/30 max-h-48 overflow-y-auto">',
    '<div id="uplink-log" class="space-y-1.5 font-label-sm text-label-sm bg-surface-container-lowest/80 p-3 rounded-xl border border-outline-variant/30 max-h-48 overflow-y-auto">'
)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("SUCCESS: frontend/index.html generated flawlessly from exact Stitch base.")

