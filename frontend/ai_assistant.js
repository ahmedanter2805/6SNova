/**
 * AURA // Planetary Climate Intelligence & Telemetry SaaS
 * AI Climate & Weather Assistant Tool (English Edition)
 * NASA Space Apps Challenge 2026
 */

(function () {
  'use strict';

  // Comprehensive list of Egypt Governorates + 14 Tourist Sites for AI auto-selection
  const REGION_OPTIONS = [
    { name_en: "Greater Cairo & Giza Metropolis", name_ar: "القاهرة الكبرى والجيزة", lat: 30.0444, lon: 31.2357 },
    { name_en: "Giza Pyramids & Great Sphinx (Giza)", name_ar: "أهرامات الجيزة وأبو الهول", lat: 29.9792, lon: 31.1342 },
    { name_en: "Grand Egyptian Museum - GEM (Giza)", name_ar: "المتحف المصري الكبير", lat: 29.9950, lon: 31.1197 },
    { name_en: "Al-Muizz Street & Khan el-Khalili (Cairo)", name_ar: "شارع المعز وخان الخليلي", lat: 30.0538, lon: 31.2625 },
    { name_en: "Cairo Citadel of Saladin (Cairo)", name_ar: "قلعة صلاح الدين الأيوبي", lat: 30.0299, lon: 31.2612 },
    { name_en: "Alexandria Coastal Hub & Corniche", name_ar: "الإسكندرية والساحل الشمالي", lat: 31.2001, lon: 29.9187 },
    { name_en: "Qaitbay Citadel & Alexandria Library", name_ar: "قلعة قايتباي ومكتبة الإسكندرية", lat: 31.2140, lon: 29.8856 },
    { name_en: "Karnak & Luxor Temples (Luxor)", name_ar: "معبد الكرنك ومعبد الأقصر", lat: 25.7188, lon: 32.6573 },
    { name_en: "Valley of the Kings & Hatshepsut (Luxor)", name_ar: "وادي الملوك ومعبد حتشبسوت", lat: 25.7402, lon: 32.6014 },
    { name_en: "Abu Simbel Sun Temples (Aswan)", name_ar: "معبد أبو سمبل", lat: 22.3372, lon: 31.6258 },
    { name_en: "Philae Island & Nubian Villages (Aswan)", name_ar: "معبد فيلة وقرى النوبة", lat: 24.0253, lon: 32.8842 },
    { name_en: "Ras Mohammed & Naama Bay (Sharm El Sheikh)", name_ar: "محمية رأس محمد وخليج نعمة", lat: 27.7294, lon: 34.2500 },
    { name_en: "Blue Hole Subsea Marine Canyon (Dahab)", name_ar: "منطقة البلو هول", lat: 28.5724, lon: 34.5372 },
    { name_en: "Siwa Oasis & Hyper-Saline Lakes (Matrouh)", name_ar: "واحة سيوة وبحيرات الملح", lat: 29.2032, lon: 25.5195 },
    { name_en: "St. Catherine Monastery & Mount Sinai", name_ar: "دير سانت كاترين وجبل موسى", lat: 28.5559, lon: 33.9753 },
    { name_en: "White Desert Chalk Karsts (New Valley)", name_ar: "الصحراء البيضاء", lat: 27.0600, lon: 28.0000 },
    { name_en: "Marsa Matrouh & New Alamein Fairway", name_ar: "مطروح والعلمين الجديدة", lat: 31.3543, lon: 27.2373 },
    { name_en: "Luxor Governorate", name_ar: "محافظة الأقصر", lat: 25.6872, lon: 32.6396 },
    { name_en: "Aswan & Lake Nasser Basin", name_ar: "محافظة أسوان", lat: 24.0889, lon: 32.8998 },
    { name_en: "Port Said & Northern Suez Canal", name_ar: "محافظة بورسعيد", lat: 31.2653, lon: 32.3019 },
    { name_en: "Suez Governorate & Southern Canal", name_ar: "محافظة السويس", lat: 29.9668, lon: 32.5498 },
    { name_en: "Hurghada & Red Sea Coral Riviera", name_ar: "محافظة الغردقة والبحر الأحمر", lat: 27.2579, lon: 33.8116 },
    { name_en: "Fayoum Oasis & Lake Qarun", name_ar: "محافظة الفيوم", lat: 29.3084, lon: 30.8428 },
    { name_en: "Qena Upper Nile Agrarian Basin", name_ar: "محافظة قنا", lat: 26.1551, lon: 32.7160 },
    { name_en: "Sohag Governorate", name_ar: "محافظة سوهاج", lat: 26.5569, lon: 31.6948 },
    { name_en: "Minya Governorate", name_ar: "محافظة المنيا", lat: 28.1099, lon: 30.7503 },
    { name_en: "Asyut Governorate", name_ar: "محافظة أسيوط", lat: 27.1783, lon: 31.1859 }
  ];

  window.toggleAIChatModal = function (show) {
    const modal = document.getElementById('ai-assistant-modal');
    if (!modal) return;
    if (show === undefined) {
      modal.classList.toggle('hidden');
    } else if (show) {
      modal.classList.remove('hidden');
    } else {
      modal.classList.add('hidden');
    }

    if (!modal.classList.contains('hidden')) {
      const input = document.getElementById('ai-modal-input');
      if (input) setTimeout(() => input.focus(), 150);
      syncSelectedRegion();
    }
  };

  function syncSelectedRegion() {
    const select = document.getElementById('ai-region-select');
    if (!select) return;

    if (select.children.length === 0) {
      REGION_OPTIONS.forEach((reg, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        opt.textContent = `${reg.name_en} (${reg.name_ar})`;
        select.appendChild(opt);
      });
    }

    if (window.activeRegion) {
      const currentLat = window.activeRegion.lat;
      const currentLon = window.activeRegion.lon;
      let bestIdx = 0;
      let minD = 999;
      REGION_OPTIONS.forEach((reg, idx) => {
        const d = Math.hypot(reg.lat - currentLat, reg.lon - currentLon);
        if (d < minD) {
          minD = d;
          bestIdx = idx;
        }
      });
      select.value = bestIdx;
    }
  }

  window.askAIPreset = function (questionText) {
    const barInput = document.getElementById('top-ai-bar-input');
    const modalInput = document.getElementById('ai-modal-input');
    if (barInput) barInput.value = questionText;
    if (modalInput) modalInput.value = questionText;
    window.submitAIQuestion();
  };

  window.submitAIQuestion = async function () {
    const barInput = document.getElementById('top-ai-bar-input');
    const modalInput = document.getElementById('ai-modal-input');
    const select = document.getElementById('ai-region-select');

    let question = "";
    if (modalInput && modalInput.value.trim()) {
      question = modalInput.value.trim();
    } else if (barInput && barInput.value.trim()) {
      question = barInput.value.trim();
    }

    if (!question) {
      question = "What is the 7-day weather forecast, multi-decadal historical baseline comparison, and 2050 climate trend projection?";
    }

    // Ensure modal is open to display the full report
    window.toggleAIChatModal(true);

    const regIdx = select ? parseInt(select.value) || 0 : 0;
    const targetRegion = REGION_OPTIONS[regIdx] || REGION_OPTIONS[0];

    const resultBox = document.getElementById('ai-response-box');
    const metricsGrid = document.getElementById('ai-metrics-grid');
    const statusPill = document.getElementById('ai-loading-pill');

    if (statusPill) statusPill.classList.remove('hidden');
    if (resultBox) {
      resultBox.innerHTML = `
        <div class="flex flex-col items-center justify-center p-8 space-y-3">
          <div class="w-10 h-10 border-4 border-aura-purple border-t-aura-cyan rounded-full animate-spin"></div>
          <div class="text-xs font-mono text-cyan-300 animate-pulse">Contacting NASA MERRA-2 telemetry & AI climate models for ${targetRegion.name_en}...</div>
          <div class="text-[10px] text-slate-500 font-mono">Synthesizing 24-Year MERRA-2 Records · Theil-Sen 2050 Projections · Live Synoptic 7-Day Outlook</div>
        </div>
      `;
    }
    if (metricsGrid) metricsGrid.classList.add('hidden');

    try {
      const url = `/api/ask?question=${encodeURIComponent(question)}&lat=${targetRegion.lat}&lon=${targetRegion.lon}&variable=T2M&region_name_en=${encodeURIComponent(targetRegion.name_en)}&region_name_ar=${encodeURIComponent(targetRegion.name_ar)}`;
      const res = await fetch(url);
      const data = await res.json();

      if (statusPill) statusPill.classList.add('hidden');

      if (data.status === 'success') {
        renderAIResponse(data, targetRegion);
      } else {
        if (resultBox) {
          resultBox.innerHTML = `
            <div class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              ⚠️ An error occurred while synthesizing the response: ${data.message || 'Please try again.'}
            </div>
          `;
        }
      }
    } catch (e) {
      if (statusPill) statusPill.classList.add('hidden');
      if (resultBox) {
        resultBox.innerHTML = `
          <div class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            ⚠️ Gateway connection error: ${e.message}
          </div>
        `;
      }
    }
  };

  function renderAIResponse(data, region) {
    const resultBox = document.getElementById('ai-response-box');
    const metricsGrid = document.getElementById('ai-metrics-grid');
    const headerTitle = document.getElementById('ai-target-title');

    if (headerTitle) {
      headerTitle.textContent = `${region.name_en} (${region.name_ar})`;
    }

    if (metricsGrid && data.metrics) {
      const m = data.metrics;
      metricsGrid.classList.remove('hidden');
      metricsGrid.innerHTML = `
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-4 text-xs font-mono">
          <div class="bg-aura-dark/80 p-2.5 rounded-xl border border-white/10 text-center">
            <span class="text-slate-400 block text-[10px] uppercase">Current Temp</span>
            <span class="text-white font-extrabold text-base">${m.temperature_c.toFixed(1)}°C</span>
            <span class="text-aura-cyan text-[10px] block">RealFeel: ${m.real_feel_c.toFixed(1)}°C</span>
          </div>
          <div class="bg-aura-dark/80 p-2.5 rounded-xl border border-white/10 text-center">
            <span class="text-slate-400 block text-[10px] uppercase">Decadal Warming</span>
            <span class="text-aura-amber font-extrabold text-base">+${m.warming_slope_decade.toFixed(2)}°C</span>
            <span class="text-slate-400 text-[10px] block">per decade (Theil-Sen)</span>
          </div>
          <div class="bg-aura-dark/80 p-2.5 rounded-xl border border-white/10 text-center">
            <span class="text-slate-400 block text-[10px] uppercase">Projected 2050</span>
            <span class="text-aura-rose font-extrabold text-base">${m.temp_2050_c.toFixed(1)}°C</span>
            <span class="text-slate-400 text-[10px] block">IPCC Extrapolated</span>
          </div>
          <div class="bg-aura-dark/80 p-2.5 rounded-xl border border-white/10 text-center">
            <span class="text-slate-400 block text-[10px] uppercase">UV Index & Wind</span>
            <span class="text-sky-300 font-extrabold text-base">UV: ${m.uv_index}</span>
            <span class="text-slate-400 text-[10px] block">${m.wind_kmh.toFixed(1)} km/h</span>
          </div>
        </div>
      `;
    }

    let rawText = data.answer || "No response received.";
    let formattedHtml = rawText
      .replace(/### (.*?)\n/g, '<h3 class="text-base font-bold text-white font-headline my-2">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-cyan-300 font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="text-slate-200">$1</em>')
      .replace(/• (.*?)\n/g, '<li class="my-1 text-slate-200 leading-relaxed">$1</li>')
      .replace(/\n\n/g, '<br/>');

    if (resultBox) {
      resultBox.innerHTML = `
        <div class="p-4 rounded-2xl bg-aura-void/60 border border-white/10 text-xs text-slate-200 leading-relaxed font-sans space-y-2">
          ${formattedHtml}
        </div>
        <div class="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-2 border-t border-white/5">
          <span class="flex items-center gap-1.5 text-aura-emerald">
            <span class="w-2 h-2 rounded-full bg-aura-emerald animate-pulse"></span>
            Verified Climate AI · Model: ${data.model} (${data.source})
          </span>
          <button onclick="window.dispatchTelegramAlert('cairo')" class="text-sky-400 hover:text-sky-300 flex items-center gap-1 underline cursor-pointer">
            <span class="material-symbols-outlined text-xs">send</span> Dispatch Report to Telegram @sixsnova_bot
          </button>
        </div>
      `;
    }

    if (window.Earth3D && typeof window.Earth3D.flyTo === 'function') {
      window.Earth3D.flyTo(region.lat, region.lon, false, 175);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    syncSelectedRegion();

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'i') {
        e.preventDefault();
        window.toggleAIChatModal();
      }
    });
  });

})();
