import os

filepath = os.path.join('frontend', 'index.html')
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The old globe section (lines 888-915)
old_globe = '''        <!-- 3D Earth Globe (5 cols) + Theil-Sen Forecast Chart (7 cols) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <!-- Left: 3D WebGL Earth Globe (5 cols) -->
          <div
            class="lg:col-span-5 aura-glass rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden h-[490px]">
            <div class="flex items-center justify-between z-10">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-aura-cyan text-base">travel_explore</span>
                <span class="text-xs font-bold text-white uppercase tracking-wider font-headline">Interactive 3D Earth
                  Globe</span>
              </div>
              <button onclick="window.Earth3D &amp;&amp; window.Earth3D.flyTo(activeRegion.lat, activeRegion.lon)"
                class="px-2.5 py-1 rounded-lg bg-aura-dark hover:bg-white/10 text-slate-300 text-[11px] font-medium border border-white/10 transition-all flex items-center gap-1 font-mono">
                <span class="material-symbols-outlined text-xs">my_location</span>
                <span>Center Sector</span>
              </button>
            </div>

            <!-- WebGL Three.js Container -->
            <div id="earth-3d-canvas" class="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing"></div>

            <div
              class="z-10 bg-aura-void/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-[11px] text-slate-400 flex items-center justify-between font-mono">
              <span>\\U0001f4a1 Drag to rotate, click beacons to switch sector</span>
              <span class="text-aura-cyan font-bold">10 Sensors Active</span>
            </div>
          </div>'''

new_globe = '''        <!-- ═══ INTEGRATED TIMELINE CONTROLLER (connected to globe) ═══ -->
        <div class="aura-glass rounded-2xl p-4 space-y-2" style="border-bottom:2px solid rgba(157,78,221,0.35); box-shadow: 0 4px 30px rgba(157,78,221,0.08); border-radius: 1rem 1rem 0 0; margin-bottom: -6px;">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-aura-purple to-aura-cyan flex items-center justify-center shadow-lg shadow-aura-purple/25 shrink-0">
                <span class="material-symbols-outlined text-white text-lg">history_toggle_off</span>
              </div>
              <div>
                <h3 class="text-xs font-bold text-white uppercase tracking-wider font-headline flex items-center gap-2">
                  Planetary Time Machine
                  <span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-aura-purple/20 text-aura-purple border border-aura-purple/30">2000 \\u2192 2050</span>
                </h3>
                <p class="text-[11px] text-slate-400">Slide to travel through time \\u2014 globe markers, projections &amp; anomaly shift update in real-time</p>
              </div>
            </div>
            <div class="flex items-center gap-2 font-mono text-xs flex-wrap">
              <div class="bg-aura-dark px-3 py-2 rounded-xl border border-aura-cyan/20 flex items-center gap-2" style="box-shadow:0 0 12px rgba(0,210,255,0.08);">
                <span class="material-symbols-outlined text-aura-cyan text-sm">calendar_month</span>
                <div>
                  <div class="text-[9px] text-slate-500 uppercase tracking-widest">Year</div>
                  <span id="scrubber-year-val" class="font-extrabold text-aura-cyan text-base">2050</span>
                </div>
              </div>
              <div class="bg-aura-dark px-3 py-2 rounded-xl border border-aura-rose/20 flex items-center gap-2" style="box-shadow:0 0 12px rgba(244,63,94,0.08);">
                <span class="material-symbols-outlined text-aura-rose text-sm">thermostat</span>
                <div>
                  <div class="text-[9px] text-slate-500 uppercase tracking-widest">Projected</div>
                  <span id="scrubber-temp-val" class="font-extrabold text-aura-rose text-base">23.34\\u00b0C</span>
                </div>
              </div>
              <div class="bg-aura-dark px-3 py-2 rounded-xl border border-aura-purple/20 flex items-center gap-2" style="box-shadow:0 0 12px rgba(157,78,221,0.08);">
                <span class="material-symbols-outlined text-aura-purple text-sm">swap_vert</span>
                <div>
                  <div class="text-[9px] text-slate-500 uppercase tracking-widest">Delta \\u0394T</div>
                  <span id="scrubber-anomaly-val" class="font-extrabold text-aura-purple text-base">+2.21\\u00b0C</span>
                </div>
              </div>
            </div>
          </div>
          <div class="pt-1">
            <input id="timeline-slider" type="range" min="2000" max="2050" value="2050" step="1"
              oninput="onScrubberChange(this.value)"
              class="w-full h-2.5 rounded-lg appearance-none cursor-pointer"
              style="background: linear-gradient(90deg, rgba(0,210,255,0.4) 0%, rgba(157,78,221,0.5) 48%, rgba(244,63,94,0.5) 100%); accent-color: #9d4edd;">
            <div class="flex justify-between text-[10px] text-slate-500 font-mono mt-1 px-0.5">
              <span class="text-aura-cyan">2000</span>
              <span>2012</span>
              <span class="text-slate-400">2024 (Present)</span>
              <span>2037</span>
              <span class="text-aura-purple font-bold">2050</span>
            </div>
          </div>
        </div>

        <!-- 3D Earth Globe (5 cols) + Theil-Sen Forecast Chart (7 cols) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6" style="margin-top: 0;">

          <!-- Left: 3D WebGL Earth Globe (5 cols) \\u2014 controlled by Timeline above -->
          <div
            class="lg:col-span-5 aura-glass rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden h-[490px]" style="border-top: 2px solid rgba(0,210,255,0.2); border-radius: 0 0 1rem 1rem;">
            <div class="flex items-center justify-between z-10">
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-aura-cyan text-base">travel_explore</span>
                <span class="text-xs font-bold text-white uppercase tracking-wider font-headline">Interactive 3D Earth
                  Globe</span>
              </div>
              <div class="flex items-center gap-1.5">
                <button onclick="animateTimeTravel()"
                  class="px-2 py-1 rounded-lg bg-aura-purple/20 hover:bg-aura-purple/40 text-aura-purple text-[10px] font-bold border border-aura-purple/30 transition-all flex items-center gap-1 font-mono" title="Auto-play timelapse 2000\\u21922050">
                  <span class="material-symbols-outlined text-xs">play_arrow</span>
                  <span>Timelapse</span>
                </button>
                <button onclick="window.Earth3D &amp;&amp; window.Earth3D.flyTo(activeRegion.lat, activeRegion.lon)"
                  class="px-2 py-1 rounded-lg bg-aura-dark hover:bg-white/10 text-slate-300 text-[10px] font-medium border border-white/10 transition-all flex items-center gap-1 font-mono">
                  <span class="material-symbols-outlined text-xs">my_location</span>
                  <span>Center</span>
                </button>
              </div>
            </div>

            <!-- WebGL Three.js Container -->
            <div id="earth-3d-canvas" class="absolute inset-0 w-full h-full cursor-grab active:cursor-grabbing"></div>

            <!-- Year watermark overlay on globe -->
            <div id="globe-year-overlay" class="absolute top-16 left-1/2 -translate-x-1/2 z-10 pointer-events-none">
              <span class="font-headline text-5xl font-extrabold" style="color: rgba(255,255,255,0.06); text-shadow: 0 0 40px rgba(157,78,221,0.3);" id="globe-year-watermark">2050</span>
            </div>

            <div
              class="z-10 bg-aura-void/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-[11px] text-slate-400 flex items-center justify-between font-mono">
              <span>\\U0001f4a1 Drag to rotate \\u00b7 Click beacons \\u00b7 Scrub timeline above</span>
              <span class="text-aura-cyan font-bold">10 Sensors</span>
            </div>
          </div>'''

# Check the old text exists
if old_globe in content:
    content = content.replace(old_globe, new_globe, 1)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Globe section replaced with integrated timeline + globe!")
else:
    # Debug: find approximate match
    idx = content.find('<!-- 3D Earth Globe (5 cols)')
    print(f"OLD TEXT NOT FOUND. Nearest '3D Earth Globe' at index: {idx}")
    if idx >= 0:
        print("CONTEXT:", repr(content[idx:idx+200]))

