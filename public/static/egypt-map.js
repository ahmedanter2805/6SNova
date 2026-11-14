/**
 * TrendLens Egypt - Interactive SVG Heatmap of Egypt
 * ===================================================
 * Beautiful vector map of Egyptian governorates colored by warming intensity.
 * Clicking a governorate selects that region instantly.
 * Features: Gradient heatmap coloring, hover tooltips, pulse animations.
 */

(function() {
  'use strict';

  // Map each region key to simplified SVG path data (approximate governorate outlines)
  // Egypt simplified boundaries for 10 monitoring regions
  const REGION_PATHS = {
    cairo: {
      // Greater Cairo & Giza area
      d: 'M 195 175 L 210 168 L 222 172 L 225 185 L 218 195 L 205 198 L 195 192 Z',
      cx: 210, cy: 183, label: 'Cairo'
    },
    alexandria: {
      // Alexandria & North Coast
      d: 'M 140 140 L 175 132 L 195 138 L 200 150 L 185 160 L 155 158 L 140 150 Z',
      cx: 170, cy: 146, label: 'Alexandria'
    },
    delta: {
      // Nile Delta
      d: 'M 185 150 L 215 145 L 230 155 L 225 170 L 205 175 L 190 168 Z',
      cx: 208, cy: 161, label: 'Delta'
    },
    sinai: {
      // South Sinai
      d: 'M 260 185 L 290 165 L 310 180 L 305 215 L 285 235 L 265 220 L 258 200 Z',
      cx: 282, cy: 200, label: 'Sinai'
    },
    aswan: {
      // Aswan & Lake Nasser
      d: 'M 185 340 L 210 330 L 230 340 L 235 365 L 220 385 L 195 380 L 182 360 Z',
      cx: 210, cy: 358, label: 'Aswan'
    },
    luxor: {
      // Luxor & Qena Valley
      d: 'M 178 280 L 205 270 L 225 280 L 228 310 L 215 325 L 190 320 L 175 300 Z',
      cx: 202, cy: 298, label: 'Luxor'
    },
    redsea: {
      // Red Sea Coast
      d: 'M 240 210 L 270 200 L 295 220 L 290 265 L 275 290 L 250 280 L 235 250 Z',
      cx: 265, cy: 248, label: 'Red Sea'
    },
    siwa: {
      // Siwa Oasis & Matrouh
      d: 'M 60 160 L 105 150 L 130 162 L 135 185 L 115 200 L 75 195 L 55 178 Z',
      cx: 95, cy: 177, label: 'Siwa'
    },
    newvalley: {
      // New Valley & Toshka
      d: 'M 105 250 L 155 235 L 180 250 L 185 300 L 170 330 L 130 325 L 100 295 Z',
      cx: 145, cy: 285, label: 'New Valley'
    },
    suez: {
      // Suez Canal & Port Said
      d: 'M 232 158 L 258 150 L 268 162 L 265 182 L 252 190 L 238 185 L 230 172 Z',
      cx: 250, cy: 170, label: 'Suez'
    }
  };

  // Color scale: blue (cool/low warming) → yellow → orange → red (high warming)
  function warmingColor(slope) {
    // slope is °C per decade. Range typically 0.15 to 0.45
    const t = Math.min(1, Math.max(0, (slope - 0.15) / 0.30)); // normalize 0.15-0.45 → 0-1
    
    if (t < 0.33) {
      // Blue-ish to Cyan
      const p = t / 0.33;
      return `hsl(${200 - p * 30}, 75%, ${55 + p * 10}%)`;
    } else if (t < 0.66) {
      // Cyan to Orange
      const p = (t - 0.33) / 0.33;
      return `hsl(${170 - p * 140}, 80%, ${60 - p * 10}%)`;
    } else {
      // Orange to Red/Crimson
      const p = (t - 0.66) / 0.34;
      return `hsl(${30 - p * 30}, 85%, ${50 - p * 10}%)`;
    }
  }

  // Grade to color mapping
  function gradeColor(grade) {
    const map = { A: '#10b981', B: '#84cc16', C: '#f59e0b', D: '#f97316', F: '#ef4444' };
    return map[grade] || '#64748b';
  }

  function gradeBg(grade) {
    const map = { A: 'rgba(16,185,129,0.15)', B: 'rgba(132,204,22,0.15)', C: 'rgba(245,158,11,0.15)', D: 'rgba(249,115,22,0.15)', F: 'rgba(239,68,68,0.15)' };
    return map[grade] || 'rgba(100,116,139,0.15)';
  }

  // Build the SVG map
  function buildEgyptMap(container, reportCardData) {
    if (!container) return;

    // Create a lookup from key to report card data
    const dataMap = {};
    if (reportCardData && Array.isArray(reportCardData)) {
      reportCardData.forEach(d => { dataMap[d.key] = d; });
    }

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '30 120 310 290');
    svg.setAttribute('class', 'w-full h-full');
    svg.style.filter = 'drop-shadow(0 0 20px rgba(0, 210, 255, 0.15))';

    // Background — subtle Nile river line
    const nile = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    nile.setAttribute('d', 'M 210 145 Q 205 180, 208 200 Q 210 230, 205 260 Q 200 290, 207 320 Q 212 350, 215 380');
    nile.setAttribute('stroke', 'rgba(0, 210, 255, 0.25)');
    nile.setAttribute('stroke-width', '3');
    nile.setAttribute('fill', 'none');
    nile.setAttribute('stroke-dasharray', '6,4');
    svg.appendChild(nile);

    // Nile label
    const nileLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    nileLabel.setAttribute('x', '220');
    nileLabel.setAttribute('y', '240');
    nileLabel.setAttribute('fill', 'rgba(0, 210, 255, 0.35)');
    nileLabel.setAttribute('font-size', '8');
    nileLabel.setAttribute('font-family', 'Cairo, sans-serif');
    nileLabel.setAttribute('transform', 'rotate(-75 220 240)');
    nileLabel.textContent = 'River Nile';
    svg.appendChild(nileLabel);

    // Draw each region
    Object.entries(REGION_PATHS).forEach(([key, region]) => {
      const data = dataMap[key] || {};
      const slope = data.slope_decade || 0.25;
      const grade = data.grade || 'C';
      const fillColor = warmingColor(slope);

      const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      group.style.cursor = 'pointer';
      group.setAttribute('data-region', key);

      // Region shape
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', region.d);
      path.setAttribute('fill', fillColor);
      path.setAttribute('fill-opacity', '0.65');
      path.setAttribute('stroke', 'rgba(255,255,255,0.3)');
      path.setAttribute('stroke-width', '1.2');
      path.classList.add('egypt-region-path');
      path.style.transition = 'all 0.3s ease';

      // Hover effects
      group.addEventListener('mouseenter', () => {
        path.setAttribute('fill-opacity', '0.9');
        path.setAttribute('stroke', '#00d2ff');
        path.setAttribute('stroke-width', '2');
        tooltip.style.display = 'block';
        tooltip.innerHTML = `
          <div style="font-weight:700;color:#fff;margin-bottom:2px;">${data.name_en || region.label}</div>
          <div style="color:#94a3b8;font-size:10px;">${region.label} Sector</div>
          <div style="margin-top:4px;display:flex;gap:8px;align-items:center;">
            <span style="background:${gradeBg(grade)};color:${gradeColor(grade)};padding:1px 6px;border-radius:4px;font-weight:700;font-size:13px;border:1px solid ${gradeColor(grade)}40">${grade}</span>
            <span style="color:${slope >= 0.3 ? '#f43f5e' : '#f59e0b'};font-weight:600;">+${slope.toFixed(3)}°C/dec</span>
          </div>
        `;
        const rect = group.getBoundingClientRect();
        const svgRect = svg.getBoundingClientRect();
        tooltip.style.left = (rect.left - svgRect.left + rect.width/2 - 60) + 'px';
        tooltip.style.top = (rect.top - svgRect.top - 70) + 'px';
      });

      group.addEventListener('mouseleave', () => {
        path.setAttribute('fill-opacity', '0.65');
        path.setAttribute('stroke', 'rgba(255,255,255,0.3)');
        path.setAttribute('stroke-width', '1.2');
        tooltip.style.display = 'none';
      });

      // Click to select region
      group.addEventListener('click', () => {
        if (window.REGIONS && window.switchRegion) {
          const idx = window.REGIONS.findIndex(r => r.key === key);
          if (idx !== -1) {
            window.switchRegion(window.REGIONS[idx], idx);
          }
        }
      });

      group.appendChild(path);

      // Grade badge on map
      const badge = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      
      const badgeCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      badgeCircle.setAttribute('cx', region.cx);
      badgeCircle.setAttribute('cy', region.cy);
      badgeCircle.setAttribute('r', '11');
      badgeCircle.setAttribute('fill', gradeColor(grade));
      badgeCircle.setAttribute('fill-opacity', '0.9');
      badgeCircle.setAttribute('stroke', '#fff');
      badgeCircle.setAttribute('stroke-width', '1.5');
      badge.appendChild(badgeCircle);

      const badgeText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      badgeText.setAttribute('x', region.cx);
      badgeText.setAttribute('y', region.cy + 4);
      badgeText.setAttribute('text-anchor', 'middle');
      badgeText.setAttribute('fill', '#fff');
      badgeText.setAttribute('font-size', '11');
      badgeText.setAttribute('font-weight', '700');
      badgeText.setAttribute('font-family', 'JetBrains Mono, monospace');
      badgeText.textContent = grade;
      badge.appendChild(badgeText);

      group.appendChild(badge);

      // Region label
      const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', region.cx);
      label.setAttribute('y', region.cy + 20);
      label.setAttribute('text-anchor', 'middle');
      label.setAttribute('fill', 'rgba(255,255,255,0.7)');
      label.setAttribute('font-size', '7');
      label.setAttribute('font-family', 'Cairo, sans-serif');
      label.setAttribute('font-weight', '600');
      label.textContent = region.label;
      group.appendChild(label);

      svg.appendChild(group);
    });

    // Tooltip div (positioned absolutely within the container)
    const tooltip = document.createElement('div');
    tooltip.style.cssText = 'display:none;position:absolute;z-index:50;background:rgba(20,24,36,0.95);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.15);border-radius:10px;padding:8px 12px;font-size:11px;pointer-events:none;min-width:120px;';
    
    container.style.position = 'relative';
    container.innerHTML = '';
    container.appendChild(svg);
    container.appendChild(tooltip);
  }

  // Build the Report Card Grid
  function buildReportCardGrid(container, reportCardData) {
    if (!container || !reportCardData) return;

    container.innerHTML = '';
    
    // Sort by score (worst first for dramatic impact)
    const sorted = [...reportCardData].sort((a, b) => a.score - b.score);

    sorted.forEach(region => {
      const card = document.createElement('div');
      card.className = 'p-3 rounded-xl bg-brand-dark/70 border border-white/5 hover:border-white/20 transition-all cursor-pointer flex items-center gap-3';
      card.onclick = () => {
        if (window.REGIONS && window.switchRegion) {
          const idx = window.REGIONS.findIndex(r => r.key === region.key);
          if (idx !== -1) window.switchRegion(window.REGIONS[idx], idx);
        }
      };

      const gColor = gradeColor(region.grade);
      const slopeSign = region.slope_decade >= 0 ? '+' : '';

      card.innerHTML = `
        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-xl font-extrabold shrink-0" style="background:${gradeBg(region.grade)};color:${gColor};border:1.5px solid ${gColor}40">
          ${region.grade}
        </div>
        <div class="flex-1 min-w-0">
          <div class="font-bold text-white text-xs truncate">${region.name_en}</div>
          <div class="text-[10px] text-slate-400 font-mono">${region.name_en}</div>
          <div class="flex items-center gap-3 mt-1 text-[10px]">
            <span class="font-mono font-bold" style="color:${region.slope_decade >= 0.3 ? '#f43f5e' : '#f59e0b'}">${slopeSign}${region.slope_decade.toFixed(3)}°C/dec</span>
            <span class="text-slate-400">Score: <span class="font-bold text-white">${region.score}/100</span></span>
          </div>
        </div>
        <div class="shrink-0">
          <div class="text-[10px] font-bold px-2 py-0.5 rounded" style="background:${gradeBg(region.grade)};color:${gColor};border:1px solid ${gColor}30">${region.grade_ar || 'Rank'}</div>
        </div>
      `;

      container.appendChild(card);
    });
  }

  // Fetch report card data from API
  async function loadReportCard() {
    try {
      const res = await fetch('/api/report-card');
      if (!res.ok) throw new Error(res.status);
      const json = await res.json();
      if (json.status === 'success' && json.report_card) {
        return json.report_card;
      }
    } catch(e) {
      console.warn('Report card API not available, generating client-side grades...');
    }
    return null;
  }

  // Initialize the map and report card
  async function initEgyptMap() {
    const mapContainer = document.getElementById('egypt-svg-map');
    const gridContainer = document.getElementById('report-card-grid');
    
    if (!mapContainer && !gridContainer) return;

    // Try API first
    let data = await loadReportCard();

    // Fallback: generate grades from already-loaded table data
    if (!data && window.REGIONS) {
      data = [];
      for (const reg of window.REGIONS) {
        try {
          const res = await fetch(`/api/analyze?lat=${reg.lat}&lon=${reg.lon}&variable=T2M&region_name_en=${encodeURIComponent(reg.name_en)}&region_name_ar=${encodeURIComponent(reg.name_ar)}`);
          const json = await res.json();
          if (json.status === 'success' && json.data) {
            const stats = json.data.statistics || {};
            const slope = stats.sen_slope_per_decade || 0;
            const pVal = (stats.mann_kendall || {}).p_value || 1;
            const sig = (stats.mann_kendall || {}).significant || false;
            const raw = (json.data.chart_data || {}).raw_values || [];
            const meanT = raw.length ? raw.reduce((a,b) => a+b, 0) / raw.length : 0;

            let score = Math.max(0, Math.round(100 - Math.abs(slope) * 200));
            if (sig) score = Math.max(0, score - 15);

            let grade, gradeAr;
            if (score >= 80) { grade = 'A'; gradeAr = 'Optimal'; }
            else if (score >= 65) { grade = 'B'; gradeAr = 'Good'; }
            else if (score >= 50) { grade = 'C'; gradeAr = 'Moderate'; }
            else if (score >= 35) { grade = 'D'; gradeAr = 'Vulnerable'; }
            else { grade = 'F'; gradeAr = 'Critical'; }

            data.push({
              key: reg.key,
              name_ar: reg.name_ar,
              name_en: reg.name_en,
              grade, grade_ar: gradeAr, score,
              slope_decade: slope,
              mean_temp: meanT,
              p_value: pVal,
              color: gradeColor(grade)
            });
          }
        } catch(e) {
          console.warn(`Failed to load report card for ${reg.key}:`, e);
        }
      }
    }

    if (data && data.length > 0) {
      if (mapContainer) buildEgyptMap(mapContainer, data);
      if (gridContainer) buildReportCardGrid(gridContainer, data);
    }
  }

  // Public API
  window.EgyptMap = {
    init: initEgyptMap,
    build: buildEgyptMap,
    buildGrid: buildReportCardGrid
  };

  // Auto-init after short delay to let app.js load first
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(initEgyptMap, 2000));
  } else {
    setTimeout(initEgyptMap, 2000);
  }

})();
