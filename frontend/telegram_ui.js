/**
 * AURA // Planetary Climate Intelligence & Telemetry SaaS
 * Telegram Alert Center UI Controller (@sixsnova_bot)
 * NASA Space Apps Challenge 2026: Be An Earth System Trend Detective!
 */

(function () {
  'use strict';

  let tgStatus = {
    bot_username: "@sixsnova_bot",
    has_token: true,
    has_chat_id: true,
    chat_id: "1142168838"
  };

  let registeredSubscribers = [];

  async function fetchStatus() {
    try {
      const res = await fetch('/api/telegram/status');
      if (res.ok) {
        tgStatus = await res.json();
        updateStatusBadge();
      }
    } catch (e) {
      console.warn('Could not fetch Telegram status:', e);
    }
    loadSubscribers();
  }

  async function loadSubscribers() {
    try {
      const res = await fetch('/api/telegram/subscribers');
      if (res.ok) {
        const data = await res.json();
        const subs = data.subscribers || {};
        registeredSubscribers = Object.values(subs);

        // Update subscriber select dropdowns
        const selects = ['tg-test-subscriber-select', 'modal-tg-subscriber-select'];
        selects.forEach(id => {
          const sel = document.getElementById(id);
          if (sel) {
            sel.innerHTML = '<option value="all">📢 Broadcast to All 6 Telegram Users (إذاعة للكل)</option>';
            registeredSubscribers.forEach(s => {
              const opt = document.createElement('option');
              opt.value = s.chat_id;
              opt.textContent = `👤 ${s.name || s.username || s.chat_id} (${s.city || 'Cairo'}) · ${s.chat_id}`;
              sel.appendChild(opt);
            });
          }
        });

        // Update subscriber count badges
        const countBadges = document.querySelectorAll('.tg-subscriber-count');
        countBadges.forEach(b => {
          b.textContent = `${registeredSubscribers.length} Active Users`;
        });
      }
    } catch (e) {
      console.warn('Could not load subscribers:', e);
    }
  }

  function updateStatusBadge() {
    const badges = document.querySelectorAll('.tg-live-status-badge');
    badges.forEach(badge => {
      badge.className = 'tg-live-status-badge px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-aura-emerald/20 text-aura-emerald border border-aura-emerald/40 flex items-center gap-1.5';
      badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-aura-emerald animate-pulse"></span> BOT LIVE (@sixsnova_bot)';
    });
  }

  window.openTelegramModal = function () {
    const modal = document.getElementById('telegram-connect-modal');
    if (modal) {
      modal.classList.remove('hidden');
      loadSubscribers();
    }
  };

  window.closeTelegramModal = function () {
    const modal = document.getElementById('telegram-connect-modal');
    if (modal) modal.classList.add('hidden');
  };

  window.saveTelegramConfig = async function () {
    const tokenInput = document.getElementById('tg-bot-token-input');
    const chatIdInput = document.getElementById('tg-chat-id-input');
    const statusDiv = document.getElementById('tg-action-feedback');

    const bot_token = tokenInput ? tokenInput.value.trim() : '';
    const chat_id = chatIdInput ? chatIdInput.value.trim() : '';

    if (statusDiv) {
      statusDiv.innerHTML = '<span class="text-aura-cyan">Saving settings...</span>';
    }

    try {
      const res = await fetch('/api/telegram/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot_token, chat_id })
      });
      const data = await res.json();
      if (data.status === 'success') {
        if (statusDiv) {
          statusDiv.innerHTML = '<span class="text-aura-emerald font-bold">✅ Settings saved successfully!</span>';
        }
        await fetchStatus();
      } else {
        if (statusDiv) {
          statusDiv.innerHTML = `<span class="text-aura-rose">❌ Error: ${data.message}</span>`;
        }
      }
    } catch (e) {
      if (statusDiv) {
        statusDiv.innerHTML = `<span class="text-aura-rose">❌ Failed to save: ${e.message}</span>`;
      }
    }
  };

  window.autoDetectTelegramChat = async function () {
    const statusDiv = document.getElementById('tg-action-feedback');
    const tokenInput = document.getElementById('tg-bot-token-input');
    const bot_token = tokenInput ? tokenInput.value.trim() : '';

    if (statusDiv) {
      statusDiv.innerHTML = '<span class="text-aura-cyan animate-pulse">Scanning Telegram updates for messages to @sixsnova_bot...</span>';
    }

    try {
      const res = await fetch('/api/telegram/auto-detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bot_token })
      });
      const data = await res.json();

      if (data.status === 'success') {
        const chatIdInput = document.getElementById('tg-chat-id-input');
        if (chatIdInput) chatIdInput.value = data.chat_id;
        if (statusDiv) {
          statusDiv.innerHTML = `<span class="text-aura-emerald font-bold">✅ Found user '${data.user}' (Chat ID: ${data.chat_id})! Linked to @sixsnova_bot.</span>`;
        }
        await fetchStatus();
      } else if (data.status === 'pending') {
        if (statusDiv) {
          statusDiv.innerHTML = `<span class="text-aura-amber font-mono text-[11px]">⏳ ${data.message}</span>`;
        }
      } else {
        if (statusDiv) {
          statusDiv.innerHTML = `<span class="text-aura-rose font-mono text-[11px]">❌ ${data.message}</span>`;
        }
      }
    } catch (e) {
      if (statusDiv) {
        statusDiv.innerHTML = `<span class="text-aura-rose">❌ Detection failed: ${e.message}</span>`;
      }
    }
  };

  // ── CORE TEST BUTTON DISPATCHER ─────────────────────────────────────────────
  window.sendTelegramTestAlert = async function (alertType, customChatId = null) {
    const feedback = document.getElementById('tg-action-feedback');
    const modalFeedback = document.getElementById('modal-tg-feedback');
    const previewBox = document.getElementById('tg-preview-box');

    // Determine target chat ID
    let targetId = customChatId;
    if (!targetId) {
      const sel = document.getElementById('tg-test-subscriber-select') || document.getElementById('modal-tg-subscriber-select');
      if (sel && sel.value !== 'all') {
        targetId = sel.value;
      }
    }
    if (targetId === 'all') targetId = null;

    const at = alertType || 'green_space';
    const city = (window.activeRegion && window.activeRegion.name_en) ? window.activeRegion.name_en : 'Greater Cairo';
    const district = (window.activeRegion && window.activeRegion.name_ar) ? `${window.activeRegion.name_ar} Sector` : 'Urban Core';

    const payloads = {
      'heat': {
        alert_type: 'heat',
        city: city,
        district: `${district} · High Density District`,
        severity: 'LEVEL 3 CRITICAL',
        metric_val: '+4.8°C Anomaly (41.5°C Surface Temp)',
        chat_id: targetId
      },
      'wind': {
        alert_type: 'wind',
        city: city,
        district: `${district} · Open Highway Corridor`,
        severity: 'LEVEL 2 HIGH',
        metric_val: '68 km/h Gale Wind Gusts · Sandstorm Warning',
        chat_id: targetId
      },
      'rainfall': {
        alert_type: 'rainfall',
        city: city,
        district: `${district} · Low-Lying Wadi Basin`,
        severity: 'LEVEL 2 HIGH',
        metric_val: '22.5 mm/day Intense Rainfall · Drainage Surcharge',
        chat_id: targetId
      },
      'humidity': {
        alert_type: 'humidity',
        city: city,
        district: `${district} · Coastal/Metropolitan Basin`,
        severity: 'LEVEL 2 HIGH',
        metric_val: '89% Surface Humidity · Heat Index 44°C',
        chat_id: targetId
      },
      'green_space': {
        alert_type: 'green_space',
        city: city,
        district: `${district} · Critical UHI Zone`,
        severity: 'LEVEL 3 CRITICAL',
        metric_val: 'Vegetation Deficit NDVI < 0.08 · UHI +4.2°C',
        chat_id: targetId
      }
    };

    const payload = payloads[at] || payloads['green_space'];

    const notify = (html) => {
      if (feedback) feedback.innerHTML = html;
      if (modalFeedback) modalFeedback.innerHTML = html;
    };

    notify(`
      <div class="p-3 rounded-xl bg-sky-500/10 border border-sky-500/30 text-sky-300 text-xs font-mono flex items-center gap-2">
        <div class="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></div>
        <span>📡 Dispatching live ${payload.alert_type.toUpperCase()} test alert to Telegram (@sixsnova_bot)...</span>
      </div>
    `);

    try {
      const res = await fetch('/api/telegram/test-alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.successful_deliveries > 0) {
        notify(`
          <div class="p-3.5 rounded-xl bg-aura-emerald/15 border border-aura-emerald/40 text-aura-emerald text-xs font-mono space-y-1.5 shadow-lg">
            <div class="font-bold flex items-center gap-2 text-sm">
              <span class="material-symbols-outlined text-base">check_circle</span>
              <span>TEST ALERT DELIVERED SUCCESSFULLY!</span>
            </div>
            <div class="text-[11px] text-slate-200">
              Delivered to <b>${data.successful_deliveries} of ${data.total_dispatched}</b> Telegram users via <b>@sixsnova_bot</b>
            </div>
            <div class="text-[10px] text-emerald-300 font-mono">
              Alert: ${payload.alert_type.toUpperCase()} // Sector: ${payload.city} // JEEBS Bilingual Format
            </div>
          </div>
        `);
      } else {
        notify(`
          <div class="p-3.5 rounded-xl bg-aura-rose/15 border border-aura-rose/40 text-aura-rose text-xs font-mono">
            ⚠️ Delivery failed: ${data.message || 'Check bot connection.'}
          </div>
        `);
      }

      if (previewBox && data.preview_text) {
        previewBox.textContent = data.preview_text.replace(/<[^>]*>/g, '');
      }
    } catch (e) {
      notify(`<div class="p-3 rounded-xl bg-aura-rose/15 border border-aura-rose/40 text-aura-rose text-xs font-mono">Error: ${e.message}</div>`);
    }
  };

  // Compatibility function for legacy buttons
  window.dispatchTelegramAlert = function (preset) {
    const map = {
      'cairo': 'heat',
      'alex': 'wind',
      'pyramids': 'humidity',
      'aswan': 'heat',
      'green': 'green_space'
    };
    window.sendTelegramTestAlert(map[preset] || 'green_space');
  };

  document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    const alertsNavBtn = document.querySelector('button[data-tab="alerts"]');
    if (alertsNavBtn) {
      alertsNavBtn.addEventListener('click', () => {
        setTimeout(fetchStatus, 150);
      });
    }
  });

})();
