/**
 * AURA // Planetary Climate Intelligence & Telemetry SaaS
 * Deep Space Cosmic Engine: Starfield, Celestial Animated Planets, Meteors & 3D Parallax
 * NASA Space Apps Challenge 2026
 */
(function () {
  'use strict';

  function initSpaceBackground() {
    const canvas = document.getElementById('starfield-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let dpr = 1;
    let animationFrameId = null;

    // Star collection
    const STAR_COUNT = 240;
    const stars = [];

    // Shooting stars (meteors)
    const meteors = [];
    let lastMeteorTime = performance.now();
    let nextMeteorDelay = 3200 + Math.random() * 3000;

    // Mouse Parallax tracking
    let targetOffsetX = 0;
    let targetOffsetY = 0;
    let currentOffsetX = 0;
    let currentOffsetY = 0;

    const STAR_COLORS = [
      'rgba(255, 255, 255, ',    // Pure Starlight White
      'rgba(224, 231, 255, ',    // Ice Sapphire
      'rgba(165, 243, 252, ',    // Cyan Spectral
      'rgba(216, 180, 254, ',    // Amethyst Violet
      'rgba(254, 240, 138, '     // Warm Solar Gold
    ];

    // =========================================================================
    // CELESTIAL DRIFTING PLANETS (3D Lighting, Rings, Atmosphere & Cloud Bands)
    // =========================================================================
    const planets = [
      {
        id: 'kronos',
        name: 'Gas Giant Kronos',
        relX: 0.84,
        relY: 0.22,
        x: 0,
        y: 0,
        radius: 34,
        z: 1.5,
        driftVx: -0.016,
        driftVy: 0.008,
        type: 'ringed',
        tilt: -0.36, // in radians (~20 deg tilt)
        primaryColor: '#f59e0b',
        secondaryColor: '#b45309',
        shadowColor: '#050208',
        ringRadiusX: 68,
        ringRadiusY: 17,
        ringTilt: -0.36
      },
      {
        id: 'gliese',
        name: 'Azure Ice Exoplanet',
        relX: 0.14,
        relY: 0.62,
        x: 0,
        y: 0,
        radius: 22,
        z: 2.1,
        driftVx: 0.018,
        driftVy: -0.010,
        type: 'oceanic',
        primaryColor: '#38bdf8',
        secondaryColor: '#0284c7',
        shadowColor: '#020617'
      },
      {
        id: 'ares',
        name: 'Crimson Terrestrial Moon',
        relX: 0.48,
        relY: 0.86,
        x: 0,
        y: 0,
        radius: 14,
        z: 1.1,
        driftVx: -0.012,
        driftVy: -0.014,
        type: 'cratered',
        primaryColor: '#fb923c',
        secondaryColor: '#9a3412',
        shadowColor: '#1c0703'
      },
      {
        id: 'selene',
        name: 'Luminescent Ice Moon',
        relX: 0.26,
        relY: 0.16,
        x: 0,
        y: 0,
        radius: 10,
        z: 0.85,
        driftVx: 0.014,
        driftVy: 0.011,
        type: 'crystal',
        primaryColor: '#e0e7ff',
        secondaryColor: '#818cf8',
        shadowColor: '#0b0f2e'
      }
    ];

    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      // Position planets based on relative screen coordinates
      for (let i = 0; i < planets.length; i++) {
        const p = planets[i];
        if (!p.initialized) {
          p.x = width * p.relX;
          p.y = height * p.relY;
          p.initialized = true;
        }
      }
    }

    function initStars() {
      stars.length = 0;
      for (let i = 0; i < STAR_COUNT; i++) {
        stars.push({
          x: Math.random() * width,
          y: Math.random() * height,
          z: Math.random() * 3.2 + 0.6,
          radius: Math.random() * 1.4 + 0.4,
          baseAlpha: Math.random() * 0.65 + 0.25,
          twinkleSpeed: Math.random() * 0.035 + 0.012,
          twinkleOffset: Math.random() * Math.PI * 2,
          colorPrefix: STAR_COLORS[Math.floor(Math.random() * STAR_COLORS.length)],
          vx: (Math.random() - 0.5) * 0.06,
          vy: (Math.random() - 0.5) * 0.06
        });
      }
    }

    function spawnMeteor() {
      const startX = Math.random() * (width * 1.3);
      const startY = Math.random() * (height * 0.45);
      const angle = (Math.PI / 4.2) + (Math.random() * 0.2 - 0.1);
      const speed = Math.random() * 7 + 11;
      const length = Math.random() * 95 + 65;

      meteors.push({
        x: startX,
        y: startY,
        dx: -Math.cos(angle) * speed,
        dy: Math.sin(angle) * speed,
        length: length,
        alpha: 1.0,
        decay: Math.random() * 0.018 + 0.012
      });
    }

    window.addEventListener('mousemove', function (e) {
      targetOffsetX = (e.clientX - width / 2) * 0.022;
      targetOffsetY = (e.clientY - height / 2) * 0.022;
    }, { passive: true });

    // =========================================================================
    // PLANET DRAWING SUBROUTINES
    // =========================================================================

    function drawRingedPlanet(p, drawX, drawY) {
      const r = p.radius;
      const rx = p.ringRadiusX;
      const ry = p.ringRadiusY;

      ctx.save();
      ctx.translate(drawX, drawY);
      ctx.rotate(p.tilt);

      // 1. Back Arc of Planetary Rings (Behind Planet Sphere)
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(0, 0, rx, ry, 0, Math.PI, 2 * Math.PI);
      const ringGradBack = ctx.createLinearGradient(-rx, 0, rx, 0);
      ringGradBack.addColorStop(0, 'rgba(217, 119, 6, 0.15)');
      ringGradBack.addColorStop(0.3, 'rgba(253, 230, 138, 0.45)');
      ringGradBack.addColorStop(0.7, 'rgba(245, 158, 11, 0.35)');
      ringGradBack.addColorStop(1, 'rgba(217, 119, 6, 0.10)');
      ctx.strokeStyle = ringGradBack;
      ctx.lineWidth = 6;
      ctx.stroke();

      // Outer thin division
      ctx.beginPath();
      ctx.ellipse(0, 0, rx + 4, ry + 1.2, 0, Math.PI, 2 * Math.PI);
      ctx.strokeStyle = 'rgba(254, 243, 199, 0.25)';
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.restore();

      // 2. Planet Sphere with Atmospheric Bands
      ctx.save();
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.clip();

      // Base spherical 3D lighting (light from upper-left)
      const sphereGrad = ctx.createRadialGradient(-r * 0.38, -r * 0.38, r * 0.05, 0, 0, r);
      sphereGrad.addColorStop(0, '#fef3c7');    // Solar highlight
      sphereGrad.addColorStop(0.25, '#f59e0b'); // Warm amber
      sphereGrad.addColorStop(0.65, '#b45309'); // Rust band
      sphereGrad.addColorStop(0.95, '#451a03'); // Deep terminator
      sphereGrad.addColorStop(1, '#020104');    // Night side
      ctx.fillStyle = sphereGrad;
      ctx.fillRect(-r, -r, r * 2, r * 2);

      // Atmospheric cloud bands
      ctx.fillStyle = 'rgba(180, 83, 9, 0.35)';
      ctx.fillRect(-r, -r * 0.3, r * 2, 4);
      ctx.fillStyle = 'rgba(254, 243, 199, 0.25)';
      ctx.fillRect(-r, 0, r * 2, 5);
      ctx.fillStyle = 'rgba(120, 53, 15, 0.40)';
      ctx.fillRect(-r, r * 0.35, r * 2, 4);

      // Shadow overlay on sphere to enhance 3D curvature
      const shadowGrad = ctx.createRadialGradient(r * 0.4, r * 0.4, r * 0.2, 0, 0, r * 1.1);
      shadowGrad.addColorStop(0, 'rgba(0, 0, 0, 0.85)');
      shadowGrad.addColorStop(0.6, 'rgba(0, 0, 0, 0.3)');
      shadowGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = shadowGrad;
      ctx.fillRect(-r, -r, r * 2, r * 2);

      ctx.restore();

      // 3. Front Arc of Planetary Rings (In Front of Planet Sphere)
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI);
      const ringGradFront = ctx.createLinearGradient(-rx, 0, rx, 0);
      ringGradFront.addColorStop(0, 'rgba(217, 119, 6, 0.20)');
      ringGradFront.addColorStop(0.2, 'rgba(253, 230, 138, 0.65)');
      ringGradFront.addColorStop(0.5, 'rgba(245, 158, 11, 0.50)');
      ringGradFront.addColorStop(0.8, 'rgba(253, 230, 138, 0.55)');
      ringGradFront.addColorStop(1, 'rgba(217, 119, 6, 0.15)');
      ctx.strokeStyle = ringGradFront;
      ctx.lineWidth = 6;
      ctx.stroke();

      // Outer division line
      ctx.beginPath();
      ctx.ellipse(0, 0, rx + 4, ry + 1.2, 0, 0, Math.PI);
      ctx.strokeStyle = 'rgba(254, 243, 199, 0.35)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Planet Shadow cast onto rings
      ctx.fillStyle = 'rgba(3, 1, 8, 0.75)';
      ctx.beginPath();
      ctx.ellipse(r * 0.1, r * 0.1, r * 0.85, ry * 0.95, 0, 0, Math.PI);
      ctx.fill();
      ctx.restore();

      // 4. Subtle Outer Atmosphere Glow
      ctx.beginPath();
      ctx.arc(0, 0, r + 1, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(251, 191, 36, 0.25)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      ctx.restore();
    }

    function drawOceanicPlanet(p, drawX, drawY) {
      const r = p.radius;
      ctx.save();
      ctx.translate(drawX, drawY);

      // Atmospheric Rayleigh scattering halo
      const haloGrad = ctx.createRadialGradient(0, 0, r * 0.85, 0, 0, r * 1.35);
      haloGrad.addColorStop(0, 'rgba(56, 189, 248, 0.40)');
      haloGrad.addColorStop(0.5, 'rgba(6, 182, 212, 0.15)');
      haloGrad.addColorStop(1, 'rgba(6, 182, 212, 0)');
      ctx.fillStyle = haloGrad;
      ctx.beginPath();
      ctx.arc(0, 0, r * 1.35, 0, Math.PI * 2);
      ctx.fill();

      // Sphere with 3D oceanic lighting
      ctx.save();
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.clip();

      const oceanGrad = ctx.createRadialGradient(-r * 0.35, -r * 0.35, r * 0.05, 0, 0, r);
      oceanGrad.addColorStop(0, '#e0f2fe');    // White polar sunlight
      oceanGrad.addColorStop(0.2, '#38bdf8');   // Bright azure ocean
      oceanGrad.addColorStop(0.55, '#0284c7');  // Deep cobalt
      oceanGrad.addColorStop(0.85, '#0c4a6e');  // Ocean depths
      oceanGrad.addColorStop(1, '#020617');     // Night side shadow
      ctx.fillStyle = oceanGrad;
      ctx.fillRect(-r, -r, r * 2, r * 2);

      // Swirling cirrus cloud filaments
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.28)';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(-r * 0.2, -r * 0.1, r * 0.6, 0.2, Math.PI * 0.85);
      ctx.stroke();

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.22)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(r * 0.1, r * 0.2, r * 0.5, Math.PI * 0.3, Math.PI * 1.1);
      ctx.stroke();

      ctx.restore();

      // Sunlit crescent rim highlight
      ctx.beginPath();
      ctx.arc(0, 0, r, Math.PI * 0.75, Math.PI * 1.75);
      ctx.strokeStyle = 'rgba(186, 230, 253, 0.65)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.restore();
    }

    function drawCrateredPlanet(p, drawX, drawY) {
      const r = p.radius;
      ctx.save();
      ctx.translate(drawX, drawY);

      // Base spherical gradient
      ctx.save();
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.clip();

      const craterGrad = ctx.createRadialGradient(-r * 0.35, -r * 0.35, r * 0.05, 0, 0, r);
      craterGrad.addColorStop(0, '#ffedd5');    // Solar crest
      craterGrad.addColorStop(0.3, '#fb923c');   // Mars terracotta
      craterGrad.addColorStop(0.7, '#9a3412');   // Deep copper
      craterGrad.addColorStop(1, '#1c0703');     // Shadow side
      ctx.fillStyle = craterGrad;
      ctx.fillRect(-r, -r, r * 2, r * 2);

      // Distinct crater indentations
      ctx.fillStyle = 'rgba(67, 20, 7, 0.45)';
      ctx.beginPath();
      ctx.arc(-r * 0.25, -r * 0.15, r * 0.22, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = 'rgba(67, 20, 7, 0.40)';
      ctx.beginPath();
      ctx.arc(r * 0.15, r * 0.2, r * 0.28, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();

      // Delicate warm atmospheric rim
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(251, 146, 60, 0.35)';
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.restore();
    }

    function drawCrystalMoon(p, drawX, drawY) {
      const r = p.radius;
      ctx.save();
      ctx.translate(drawX, drawY);

      // Soft icy halo
      const halo = ctx.createRadialGradient(0, 0, r * 0.5, 0, 0, r * 1.6);
      halo.addColorStop(0, 'rgba(165, 180, 252, 0.35)');
      halo.addColorStop(1, 'rgba(165, 180, 252, 0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(0, 0, r * 1.6, 0, Math.PI * 2);
      ctx.fill();

      // Sphere with luminous icy pearl lighting
      const moonGrad = ctx.createRadialGradient(-r * 0.35, -r * 0.35, r * 0.05, 0, 0, r);
      moonGrad.addColorStop(0, '#ffffff');
      moonGrad.addColorStop(0.35, '#c7d2fe');
      moonGrad.addColorStop(0.75, '#6366f1');
      moonGrad.addColorStop(1, '#0e1138');
      ctx.fillStyle = moonGrad;
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.fill();

      // Crisp diamond highlight on crest
      ctx.beginPath();
      ctx.arc(0, 0, r, Math.PI * 0.8, Math.PI * 1.65);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      ctx.restore();
    }

    // =========================================================================
    // MAIN 60 FPS RENDER LOOP
    // =========================================================================
    function render(time) {
      ctx.clearRect(0, 0, width, height);

      // Smooth parallax interpolation
      currentOffsetX += (targetOffsetX - currentOffsetX) * 0.04;
      currentOffsetY += (targetOffsetY - currentOffsetY) * 0.04;

      // -----------------------------------------------------------------------
      // 1. Draw All Stars
      // -----------------------------------------------------------------------
      for (let i = 0; i < stars.length; i++) {
        const s = stars[i];

        // Cosmic slow drift
        s.x += s.vx;
        s.y += s.vy;
        if (s.x < 0) s.x = width;
        if (s.x > width) s.x = 0;
        if (s.y < 0) s.y = height;
        if (s.y > height) s.y = 0;

        // Apply depth parallax
        const drawX = s.x + currentOffsetX * s.z;
        const drawY = s.y + currentOffsetY * s.z;

        // Sine wave twinkle
        const alpha = s.baseAlpha + Math.sin(time * s.twinkleSpeed + s.twinkleOffset) * 0.3;
        const clampedAlpha = Math.max(0.08, Math.min(1.0, alpha));

        ctx.beginPath();
        ctx.arc(drawX, drawY, s.radius * (s.z > 2.5 ? 1.2 : 1), 0, Math.PI * 2);
        ctx.fillStyle = s.colorPrefix + clampedAlpha + ')';
        ctx.fill();

        // Soft celestial glow halo around close stars
        if (s.z > 2.6 && clampedAlpha > 0.55) {
          ctx.beginPath();
          ctx.arc(drawX, drawY, s.radius * 3.2, 0, Math.PI * 2);
          ctx.fillStyle = s.colorPrefix + (clampedAlpha * 0.16) + ')';
          ctx.fill();
        }
      }

      // -----------------------------------------------------------------------
      // 2. Telemetry Constellation Connections (Faint lines between close stars)
      // -----------------------------------------------------------------------
      ctx.lineWidth = 0.5;
      const subsetLen = Math.min(45, stars.length);
      for (let i = 0; i < subsetLen; i++) {
        const a = stars[i];
        for (let j = i + 1; j < subsetLen; j++) {
          const b = stars[j];
          const ax = a.x + currentOffsetX * a.z;
          const ay = a.y + currentOffsetY * a.z;
          const bx = b.x + currentOffsetX * b.z;
          const by = b.y + currentOffsetY * b.z;
          const dx = ax - bx;
          const dy = ay - by;
          const distSq = dx * dx + dy * dy;

          if (distSq < 72 * 72) {
            const dist = Math.sqrt(distSq);
            const lineAlpha = (1 - dist / 72) * 0.14;
            ctx.strokeStyle = 'rgba(139, 92, 246, ' + lineAlpha + ')';
            ctx.beginPath();
            ctx.moveTo(ax, ay);
            ctx.lineTo(bx, by);
            ctx.stroke();
          }
        }
      }

      // -----------------------------------------------------------------------
      // 3. Drifting Celestial Planets (With Slow Orbital Movement & 3D Shading)
      // -----------------------------------------------------------------------
      for (let i = 0; i < planets.length; i++) {
        const p = planets[i];

        // Orbital drift
        p.x += p.driftVx;
        p.y += p.driftVy;

        // Smooth wrap-around screen boundaries
        const margin = 120;
        if (p.x < -margin) p.x = width + margin;
        if (p.x > width + margin) p.x = -margin;
        if (p.y < -margin) p.y = height + margin;
        if (p.y > height + margin) p.y = -margin;

        // Compute parallax position based on planet's depth factor
        const drawX = p.x + currentOffsetX * p.z;
        const drawY = p.y + currentOffsetY * p.z;

        // Render according to planet type
        if (p.type === 'ringed') {
          drawRingedPlanet(p, drawX, drawY);
        } else if (p.type === 'oceanic') {
          drawOceanicPlanet(p, drawX, drawY);
        } else if (p.type === 'cratered') {
          drawCrateredPlanet(p, drawX, drawY);
        } else if (p.type === 'crystal') {
          drawCrystalMoon(p, drawX, drawY);
        }
      }

      // -----------------------------------------------------------------------
      // 4. Meteors (Shooting Stars)
      // -----------------------------------------------------------------------
      if (time - lastMeteorTime > nextMeteorDelay) {
        spawnMeteor();
        lastMeteorTime = time;
        nextMeteorDelay = 3500 + Math.random() * 4500;
      }

      for (let i = meteors.length - 1; i >= 0; i--) {
        const m = meteors[i];
        m.x += m.dx;
        m.y += m.dy;
        m.alpha -= m.decay;

        if (m.alpha <= 0 || m.x < -120 || m.y > height + 120) {
          meteors.splice(i, 1);
          continue;
        }

        const hyp = Math.hypot(m.dx, m.dy) || 1;
        const tailX = m.x - (m.dx / hyp) * m.length;
        const tailY = m.y - (m.dy / hyp) * m.length;

        const grad = ctx.createLinearGradient(tailX, tailY, m.x, m.y);
        grad.addColorStop(0, 'rgba(6, 182, 212, 0)');
        grad.addColorStop(0.6, 'rgba(139, 92, 246, ' + (m.alpha * 0.5) + ')');
        grad.addColorStop(1, 'rgba(255, 255, 255, ' + m.alpha + ')');

        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.7;
        ctx.beginPath();
        ctx.moveTo(tailX, tailY);
        ctx.lineTo(m.x, m.y);
        ctx.stroke();

        // Incandescent Meteor Head
        ctx.beginPath();
        ctx.arc(m.x, m.y, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, ' + m.alpha + ')';
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(render);
    }

    window.addEventListener('resize', function () {
      resize();
      initStars();
    }, { passive: true });

    resize();
    initStars();
    animationFrameId = requestAnimationFrame(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSpaceBackground);
  } else {
    initSpaceBackground();
  }
})();
