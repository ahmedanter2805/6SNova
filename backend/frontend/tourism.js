/**
 * AURA // Planetary Climate Intelligence & Telemetry SaaS
 * Tourism & Heritage Climate Sentinel Controller
 * NASA Space Apps Challenge 2026
 */
(function() {
  'use strict';

  let allSites = [];
  let currentActiveSiteId = 'giza_pyramids';
  let activeFilterCategory = 'all';
  let forecastChart = null;
  let benchmarkChart = null;

  // ── 1. Fetch & Initialize All 14 Sites ──────────────────────────────────────
  async function initTourismSentinel() {
    try {
      const res = await fetch('/api/tourism-sites');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      allSites = data.sites || [];

      renderSiteCards(allSites);
      loadSiteIntelligence(currentActiveSiteId);
    } catch (err) {
      console.warn('Failed to fetch tourism sites:', err);
    }
  }

  // ── 2. Render 14 Tourist Site Selector Strip ────────────────────────────────
  function renderSiteCards(sites) {
    const container = document.getElementById('tourism-sites-carousel');
    if (!container) return;

    const filtered = activeFilterCategory === 'all'
      ? sites
      : sites.filter(s => {
          if (activeFilterCategory === 'monuments') return s.category_key === 'monuments' || s.category_key === 'necropolis';
          if (activeFilterCategory === 'museums') return s.category_key === 'museum' || s.category_key === 'historic_islamic' || s.category_key === 'fortress';
          if (activeFilterCategory === 'marine') return s.category_key === 'marine_park' || s.category_key === 'coastal_heritage';
          if (activeFilterCategory === 'desert') return s.category_key === 'oasis_nature' || s.category_key === 'desert_wilderness' || s.category_key === 'high_altitude';
          return true;
        });

    container.innerHTML = filtered.map(s => {
      const isActive = s.id === currentActiveSiteId;
      const scoreColor = s.tsi_score >= 85 ? 'text-emerald-400 bg-emerald-500/15 border-emerald-500/30'
        : (s.tsi_score >= 72 ? 'text-cyan-400 bg-cyan-500/15 border-cyan-500/30' : 'text-amber-400 bg-amber-500/15 border-amber-500/30');

      return `
        <div onclick="window.selectTourismSite('${s.id}')"
             class="group cursor-pointer shrink-0 w-64 p-4 rounded-2xl transition-all duration-200 border ${
               isActive
                 ? 'bg-aura-purple/15 border-aura-purple ring-2 ring-aura-purple/40 shadow-lg shadow-aura-purple/20'
                 : 'bg-[#0f172a]/70 hover:bg-[#1e293b]/80 border-white/10 hover:border-aura-cyan/40'
             }">
          <div class="flex items-center justify-between mb-2.5">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center ${isActive ? 'bg-aura-purple text-white' : 'bg-white/5 text-amber-400 group-hover:bg-aura-cyan/20 group-hover:text-aura-cyan'} transition-all">
              <span class="material-symbols-outlined text-lg">${s.icon || 'temple_hindu'}</span>
            </div>
            <div class="flex items-center gap-1.5">
              ${s.unesco ? '<span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-amber-400/20 text-amber-300 border border-amber-400/30" title="UNESCO World Heritage Site">UNESCO</span>' : ''}
              <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${scoreColor}">
                ${s.tsi_score}/100
              </span>
            </div>
          </div>

          <h4 class="text-xs font-bold text-white group-hover:text-aura-cyan transition-colors line-clamp-1 font-headline">
            ${s.name_en}
          </h4>
          <p class="text-[10px] text-slate-400 font-mono line-clamp-1 mb-2">
            ${s.governorate_en} Governorate · Heritage Sentinel
          </p>

          <div class="flex items-center justify-between pt-2 border-t border-white/5 text-[10px] font-mono text-slate-400">
            <span class="flex items-center gap-1">
              <span class="material-symbols-outlined text-[12px] text-aura-purple">location_on</span>
              <span>${s.governorate_en}</span>
            </span>
            <span class="text-white font-bold">${s.current_temp}°C</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // ── 3. Category Filter Handler ──────────────────────────────────────────────
  window.filterTourismCategory = function(catKey) {
    activeFilterCategory = catKey;
    document.querySelectorAll('.tourism-cat-btn').forEach(btn => {
      const matches = btn.getAttribute('data-cat') === catKey;
      btn.className = matches
        ? 'tourism-cat-btn px-3 py-1.5 rounded-xl text-xs font-bold bg-aura-purple text-white shadow-md transition-all'
        : 'tourism-cat-btn px-3 py-1.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white bg-aura-void/60 hover:bg-white/5 transition-all';
    });
    renderSiteCards(allSites);
  };

  // ── 4. Select Tourist Destination ───────────────────────────────────────────
  window.selectTourismSite = function(siteId) {
    currentActiveSiteId = siteId;
    renderSiteCards(allSites);
    loadSiteIntelligence(siteId);
  };

  // ── 5. Load Deep Site Intelligence & Forecasts ──────────────────────────────
  async function loadSiteIntelligence(siteId) {
    const loadingBadge = document.getElementById('tourism-loading-badge');
    if (loadingBadge) loadingBadge.classList.remove('hidden');

    try {
      const res = await fetch(`/api/tourism-forecast?site_id=${siteId}`);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      renderSiteConsole(data);
    } catch (err) {
      console.warn('loadSiteIntelligence:', err);
    } finally {
      if (loadingBadge) loadingBadge.classList.add('hidden');
    }
  }

  // ── 6. Render Full Intelligence Console ─────────────────────────────────────
  function renderSiteConsole(data) {
    const s = data.site;
    const cw = data.current_weather;
    const comp = data.comparison_metrics;
    const adv = data.tourist_advisory;
    const her = data.heritage_conservation;

    // Header updates
    const titleEl = document.getElementById('tour-site-title');
    const arTitleEl = document.getElementById('tour-site-ar-title');
    const govBadge = document.getElementById('tour-gov-badge');
    const unescoBadge = document.getElementById('tour-unesco-badge');
    const elevBadge = document.getElementById('tour-elev-badge');
    const tsiScoreEl = document.getElementById('tour-tsi-score');
    const tsiRatingEl = document.getElementById('tour-tsi-rating');
    const bestHoursEl = document.getElementById('tour-best-hours');

    if (titleEl) titleEl.textContent = s.name_en;
    if (arTitleEl) arTitleEl.textContent = `${s.governorate_en} Region · Antiquity & Tourism Sentinel`;
    if (govBadge) govBadge.textContent = `${s.governorate_en} Governorate`;
    if (unescoBadge) unescoBadge.style.display = s.unesco_heritage ? 'inline-flex' : 'none';
    if (elevBadge) elevBadge.textContent = her.elevation;

    if (tsiScoreEl) tsiScoreEl.textContent = `${cw.tsi_score}/100`;
    if (tsiRatingEl) {
      tsiRatingEl.textContent = `${cw.rating_en} · Optimal Travel Window`;
      tsiRatingEl.style.color = cw.rating_color;
    }
    if (bestHoursEl) bestHoursEl.textContent = adv.best_visiting_hours_en;

    // KPI Cards
    const kpiUpcoming = document.getElementById('tour-kpi-upcoming');
    const kpiUpcomingSub = document.getElementById('tour-kpi-upcoming-sub');
    const kpiDelta = document.getElementById('tour-kpi-delta');
    const kpiDeltaSub = document.getElementById('tour-kpi-delta-sub');
    const kpiHist = document.getElementById('tour-kpi-hist');
    const kpiHistSub = document.getElementById('tour-kpi-hist-sub');
    const kpiFuture = document.getElementById('tour-kpi-future');
    const kpiFutureSub = document.getElementById('tour-kpi-future-sub');

    const firstFc = data.forecast_7days[0] || {};
    if (kpiUpcoming) kpiUpcoming.textContent = `${firstFc.high_c}°C / ${firstFc.low_c}°C`;
    if (kpiUpcomingSub) kpiUpcomingSub.textContent = `RealFeel ${firstFc.real_feel_c}°C · UV Index ${firstFc.uv_index} (High)`;

    const deltaSign = comp.delta_vs_last_week_c >= 0 ? '+' : '';
    if (kpiDelta) {
      kpiDelta.textContent = `${deltaSign}${comp.delta_vs_last_week_c}°C`;
      kpiDelta.className = comp.delta_vs_last_week_c > 1.0 ? 'text-2xl font-extrabold text-aura-rose font-mono' : 'text-2xl font-extrabold text-aura-cyan font-mono';
    }
    if (kpiDeltaSub) kpiDeltaSub.textContent = comp.delta_vs_last_week_text_en;

    if (kpiHist) kpiHist.textContent = `${comp.historical_24y_mean_c}°C Baseline`;
    if (kpiHistSub) kpiHistSub.textContent = `Record High ${comp.historical_max_c}°C · ${comp.delta_vs_2000s_text_en}`;

    const proj2050 = (data.projections_2050 && data.projections_2050.length) ? data.projections_2050[data.projections_2050.length - 1] : {};
    if (kpiFuture) kpiFuture.textContent = `+${proj2050.warming_delta_c || 1.8}°C By 2050`;
    if (kpiFutureSub) kpiFutureSub.textContent = `Theil-Sen Trend: ${her.decadal_warming_rate}`;

    // Advisories
    const clothingEl = document.getElementById('tour-clothing-guide');
    const hydrationEl = document.getElementById('tour-hydration-guide');
    const threatEl = document.getElementById('tour-threat-analysis');
    const threatArEl = document.getElementById('tour-threat-ar-analysis');

    if (clothingEl) clothingEl.textContent = adv.clothing_guide;
    if (hydrationEl) hydrationEl.textContent = adv.hydration_guide;
    if (threatEl) threatEl.textContent = her.threat_analysis_en;
    if (threatArEl) threatArEl.textContent = 'Structural micro-fracturing under diurnal temperature fluctuations amplified by airborne particulate erosion.';

    // Charts
    renderUpcomingForecastChart(data.forecast_7days);
    renderMultiHorizonChart(data);
  }

  // ── 7. Render Chart 1: 7-Day Tourist Trip Forecast ──────────────────────────
  function renderUpcomingForecastChart(forecastList) {
    const canvas = document.getElementById('tour-forecast-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (forecastChart) forecastChart.destroy();

    const labels = forecastList.map(d => `${d.day_name} (${d.date.slice(5)})`);
    const highs = forecastList.map(d => d.high_c);
    const lows = forecastList.map(d => d.low_c);
    const feels = forecastList.map(d => d.real_feel_c);
    const uvs = forecastList.map(d => d.uv_index);

    const gradHigh = ctx.createLinearGradient(0, 0, 0, 260);
    gradHigh.addColorStop(0, 'rgba(244, 63, 94, 0.35)');
    gradHigh.addColorStop(1, 'rgba(244, 63, 94, 0.0)');

    const gradLow = ctx.createLinearGradient(0, 0, 0, 260);
    gradLow.addColorStop(0, 'rgba(6, 182, 212, 0.25)');
    gradLow.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

    forecastChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Daily High (°C)',
            data: highs,
            borderColor: '#F43F5E',
            backgroundColor: gradHigh,
            borderWidth: 2.5,
            tension: 0.35,
            fill: true,
            pointBackgroundColor: '#F43F5E',
            pointRadius: 4.5
          },
          {
            label: 'RealFeel (°C)',
            data: feels,
            borderColor: '#F59E0B',
            borderWidth: 2,
            borderDash: [5, 4],
            tension: 0.35,
            pointRadius: 3.5,
            pointBackgroundColor: '#F59E0B'
          },
          {
            label: 'Night Low (°C)',
            data: lows,
            borderColor: '#06B6D4',
            backgroundColor: gradLow,
            borderWidth: 2,
            tension: 0.35,
            fill: true,
            pointBackgroundColor: '#06B6D4',
            pointRadius: 3.5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            labels: { color: '#94A3B8', font: { family: 'JetBrains Mono', size: 10 } }
          },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            borderColor: 'rgba(139, 92, 246, 0.4)',
            borderWidth: 1,
            titleFont: { family: 'Space Grotesk', weight: 'bold' },
            bodyFont: { family: 'JetBrains Mono' }
          }
        },
        scales: {
          x: {
            ticks: { color: '#64748B', font: { family: 'JetBrains Mono', size: 9 } },
            grid: { color: 'rgba(255, 255, 255, 0.04)' }
          },
          y: {
            ticks: {
              color: '#64748B',
              font: { family: 'JetBrains Mono', size: 9 },
              callback: v => `${v}°C`
            },
            grid: { color: 'rgba(255, 255, 255, 0.04)' }
          }
        }
      }
    });
  }

  // ── 8. Render Chart 2: Multi-Horizon Benchmarking (Past, Present, Climatology, Future)
  function renderMultiHorizonChart(data) {
    const canvas = document.getElementById('tour-multihorizon-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (benchmarkChart) benchmarkChart.destroy();

    const comp = data.comparison_metrics;
    const currMean = data.current_weather.mean_temp_c;
    const prevMean = currMean - comp.delta_vs_last_week_c;
    const hist24Y = comp.historical_24y_mean_c;
    
    // Future points
    const p35 = (data.projections_2050 && data.projections_2050[2]) ? data.projections_2050[2].projected_temp_c : (currMean + 0.8);
    const p50 = (data.projections_2050 && data.projections_2050[5]) ? data.projections_2050[5].projected_temp_c : (currMean + 1.7);

    const horizonLabels = [
      'Prior 7 Days',
      'This Week (Current)',
      '2000–2023 Climatology',
      '2035 Projection',
      '2050 Projection'
    ];

    const values = [
      Number(prevMean.toFixed(1)),
      Number(currMean.toFixed(1)),
      Number(hist24Y.toFixed(1)),
      Number(p35.toFixed(1)),
      Number(p50.toFixed(1))
    ];

    const barColors = [
      'rgba(148, 163, 184, 0.65)',  // Slate (Past)
      'rgba(6, 182, 212, 0.85)',    // Cyan (Current)
      'rgba(139, 92, 246, 0.85)',   // Purple (24Y Baseline)
      'rgba(245, 158, 11, 0.85)',   // Amber (2035)
      'rgba(244, 63, 94, 0.85)'     // Rose (2050)
    ];

    benchmarkChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: horizonLabels,
        datasets: [{
          label: 'Mean Temperature (°C)',
          data: values,
          backgroundColor: barColors,
          borderColor: barColors.map(c => c.replace('0.85', '1.0')),
          borderWidth: 1.5,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            borderColor: 'rgba(139, 92, 246, 0.4)',
            borderWidth: 1,
            callbacks: {
              label: ctx => ` ${ctx.parsed.y}°C`
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#94A3B8',
              font: { family: 'Space Grotesk', size: 9 },
              maxRotation: 25
            },
            grid: { display: false }
          },
          y: {
            ticks: {
              color: '#64748B',
              font: { family: 'JetBrains Mono', size: 9 },
              callback: v => `${v}°C`
            },
            grid: { color: 'rgba(255, 255, 255, 0.04)' }
          }
        }
      }
    });
  }

  // ── 9. Export Tourist Travel Brief (CSV) ────────────────────────────────────
  window.exportTourismBrief = async function() {
    try {
      const res = await fetch(`/api/tourism-forecast?site_id=${currentActiveSiteId}`);
      if (!res.ok) return;
      const d = await res.json();
      const s = d.site;

      let csv = `AURA Tourism & Cultural Heritage Climate Sentinel - Official Travel Brief\n`;
      csv += `Site:,"${s.name_en}"\n`;
      csv += `Governorate:,"${s.governorate_en}"\n`;
      csv += `Coordinates:,"${s.lat} N, ${s.lon} E"\n`;
      csv += `Tourism Suitability Score:,${d.current_weather.tsi_score}/100 - ${d.current_weather.rating_en}\n`;
      csv += `Optimal Visiting Hours:,"${d.tourist_advisory.best_visiting_hours_en}"\n\n`;

      csv += `Upcoming 7 Days Forecast\n`;
      csv += `Date,Day,High_C,Low_C,RealFeel_C,UV_Index,Wind_Speed_ms,Humidity_pct,Condition\n`;
      d.forecast_7days.forEach(f => {
        csv += `${f.date},${f.day_name},${f.high_c},${f.low_c},${f.real_feel_c},${f.uv_index},${f.wind_speed_ms},${f.humidity_pct},"${f.condition_en}"\n`;
      });

      csv += `\nMulti-Horizon Projections\n`;
      csv += `Horizon,Temperature_C,Description\n`;
      csv += `Prior_7_Days,${(d.current_weather.mean_temp_c - d.comparison_metrics.delta_vs_last_week_c).toFixed(1)},Observed Preceding Week\n`;
      csv += `Current_Week,${d.current_weather.mean_temp_c},Upcoming 7-Day Forecast Mean\n`;
      csv += `Historical_2000_2023,${d.comparison_metrics.historical_24y_mean_c},24-Year NASA MERRA-2 Baseline on same dates\n`;
      d.projections_2050.forEach(p => {
        csv += `Year_${p.year},${p.projected_temp_c},Theil-Sen Extrapolation (+${p.warming_delta_c}C)\n`;
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AURA_Tourism_${s.id}_Climate_Brief.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch(e) {
      console.warn('exportTourismBrief error:', e);
    }
  };

  // ── Auto-Boot on DOM Ready ──────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initTourismSentinel, 150);
  });
})();
