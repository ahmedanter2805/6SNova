/**
 * TrendLens / 6snova 3D Real Earth Globe (WebGL / Three.js)
 * =========================================================
 * - Real 3D interactive Earth model with orbital rotation, drag/zoom controls
 * - Atmospheric Fresnel limb glow (cyan/purple 6snova palette)
 * - Dynamic cloud layer with atmospheric motion
 * - 10 3D Hotspot beacons (pins, pulsing radar rings, labels)
 * - Real-time orbital satellite constellation tracks (SWOT, Sentinel-6, MODIS, PACE)
 * - Camera auto-rotate and smooth fly-to targeting when selecting any region
 * - Raycaster click-detection to select regions directly on the 3D sphere
 */

(function() {
  'use strict';

  // Constants & Config
  const EARTH_RADIUS = 100;
  const TEXTURE_URLS = {
    day:    'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg',
    spec:   'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_specular_2048.jpg',
    clouds: 'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_1024.png',
    night:  'https://cdn.jsdelivr.net/npm/three-globe/example/img/earth-night.jpg'
  };

  let scene, camera, renderer, controls;
  let earthMesh, cloudsMesh, atmosphereMesh, heatMesh, heatColumn, rimLight;
  let windGroup, rainGroup;
  let activePlanetLayer = 'all';
  let globeGroup, markersGroup, orbitsGroup, starsGroup;
  let targetRotation = { x: 0, y: 0 };
  let isFlying = false;
  let autoRotate = true;
  let introProgress = 0;
  let isZooming = false;
  let zoomStartDistance = 290;
  let zoomTargetDistance = 175;
  let zoomProgress = 1;
  let animationId = null;
  const markerMeshes = [];
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  const climateState = { year: 2050, heat: 1, anomaly: 0 };

  // Convert Latitude / Longitude to 3D Cartesian coordinates on sphere
  function latLonToVector3(lat, lon, radius = EARTH_RADIUS) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    return new THREE.Vector3(
      -(radius * Math.sin(phi) * Math.cos(theta)),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  }

  // Procedural fallback texture generator (guarantees instant display)
  function createProceduralEarthTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 2048;
    canvas.height = 1024;
    const ctx = canvas.getContext('2d');

    // Deep space navy ocean
    ctx.fillStyle = '#0a1020';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Graticule grid lines (Latitude & Longitude)
    ctx.strokeStyle = 'rgba(76, 214, 251, 0.12)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += canvas.width / 24) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += canvas.height / 12) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Glowing equator & tropics
    ctx.strokeStyle = 'rgba(138, 63, 252, 0.25)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    // Stylized procedural landmass dots / telemetry points
    ctx.fillStyle = 'rgba(76, 214, 251, 0.45)';
    for (let i = 0; i < 4000; i++) {
      const rx = Math.random() * canvas.width;
      const ry = Math.random() * canvas.height;
      // Rough land distribution bias
      const inAfricaEurope = (rx > 900 && rx < 1350 && ry > 250 && ry < 750);
      const inAmericas = (rx > 250 && rx < 700 && ry > 200 && ry < 850);
      const inAsia = (rx > 1300 && rx < 1850 && ry > 200 && ry < 650);
      if (inAfricaEurope || inAmericas || inAsia || Math.random() < 0.15) {
        ctx.beginPath();
        ctx.arc(rx, ry, Math.random() * 2 + 0.8, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    return new THREE.CanvasTexture(canvas);
  }

  // Create Atmospheric Glow Shader Material
  function createAtmosphereMaterial() {
    const vertexShader = `
      varying vec3 vNormal;
      varying vec3 vPosition;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;

    const fragmentShader = `
      uniform float uHeat;
      varying vec3 vNormal;
      varying vec3 vPosition;
      void main() {
        vec3 viewDir = normalize(-vPosition);
        float intensity = pow(0.62 - dot(vNormal, viewDir), 2.15);
        vec3 cyan = vec3(0.25, 0.82, 0.98);
        vec3 sapphire = vec3(0.08, 0.45, 0.92);
        vec3 col = mix(cyan, sapphire, vNormal.y * 0.5 + 0.5);
        gl_FragColor = vec4(col, intensity * 0.85);
      }
    `;

    return new THREE.ShaderMaterial({
      uniforms: { uHeat: { value: 1.0 } },
      vertexShader,
      fragmentShader,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      transparent: true,
      depthWrite: false
    });
  }

  function createHeatOverlayMaterial() {
    const vertexShader = `
      varying vec3 vWorldNormal;
      void main() {
        vWorldNormal = normalize((modelMatrix * vec4(normal, 0.0)).xyz);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `;
    const fragmentShader = `
      uniform float uHeat;
      varying vec3 vWorldNormal;
      void main() {
        vec3 n = normalize(vWorldNormal);
        float lat = degrees(asin(clamp(n.y, -1.0, 1.0)));
        float lon = degrees(atan(n.z, -n.x)) - 180.0;
        if (lon < -180.0) lon += 360.0;
        
        // 1. Egypt & Eastern Mediterranean High-Heat Dome
        float egyptDist = length(vec2(lat - 27.5, lon - 31.0));
        float egyptDome = 1.0 - smoothstep(3.0, 24.0, egyptDist);

        // 2. Global Arid / Subtropical Heat Belt (Lat 10° to 40° N and S)
        float latDist = abs(lat - 24.0);
        float heatBelt = (1.0 - smoothstep(4.0, 36.0, latDist)) * 0.72;
        
        float combinedThermalMask = max(egyptDome, heatBelt);
        float rim = pow(1.0 - abs(n.z), 1.2);

        // Responsive opacity scaling with uHeat:
        // In 2000 (uHeat = 0): cool subtle baseline
        // In 2024 (uHeat ~0.48): distinct warm golden glow
        // In 2050 (uHeat = 1.0): radiant amber/infrared heatwaves!
        float alpha = combinedThermalMask * (0.22 + uHeat * 0.65) * (0.45 + rim * 0.55);

        // Thermal color ramp:
        // Cool baseline: cyan-emerald -> Present: bright gold -> 2050: radiant amber/coral
        vec3 coolBaseline = vec3(0.20, 0.88, 0.72); // 2000 cool emerald
        vec3 warmGold     = vec3(1.00, 0.82, 0.15); // present warming
        vec3 radiantAmber = vec3(1.00, 0.42, 0.08); // mid-century heat surge
        vec3 hotCoral     = vec3(1.00, 0.18, 0.04); // extreme 2050 peak

        vec3 thermalColor;
        if (uHeat < 0.5) {
          thermalColor = mix(coolBaseline, warmGold, uHeat * 2.0);
        } else {
          thermalColor = mix(warmGold, mix(radiantAmber, hotCoral, egyptDome), (uHeat - 0.5) * 2.0);
        }

        gl_FragColor = vec4(thermalColor, alpha);
      }
    `;
    return new THREE.ShaderMaterial({
      uniforms: { uHeat: { value: 1.0 } },
      vertexShader,
      fragmentShader,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.FrontSide
    });
  }

  function createHeatColumn() {
    const group = new THREE.Group();
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0x06B6D4,
      transparent: true,
      opacity: 0.25,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide
    });
    const cone = new THREE.Mesh(new THREE.ConeGeometry(9, 44, 20, 1, true), glowMat);
    cone.position.y = 22;
    group.add(cone);
    const core = new THREE.Mesh(
      new THREE.CylinderGeometry(0.5, 0.5, 36, 8),
      new THREE.MeshBasicMaterial({ color: 0x38BDF8, transparent: true, opacity: 0.65, blending: THREE.AdditiveBlending, depthWrite: false })
    );
    core.position.y = 21;
    group.add(core);
    group.userData.cone = cone;
    group.userData.core = core;
    return group;
  }

  // 1. DYNAMIC WIND STREAMLINES (CIRCULATION VECTORS & JET STREAMS)
  function createWindStreamlines() {
    const group = new THREE.Group();
    const count = 1200;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const particlesData = [];
    const radius = EARTH_RADIUS + 1.8;

    for (let i = 0; i < count; i++) {
      const z = Math.random();
      let lat;
      if (z < 0.45) {
        lat = (Math.random() - 0.5) * 45; // Tropical trade winds
      } else if (z < 0.8) {
        const s = Math.random() > 0.5 ? 1 : -1;
        lat = s * (30 + Math.random() * 28); // Mid-latitude westerlies
      } else {
        const s = Math.random() > 0.5 ? 1 : -1;
        lat = s * (58 + Math.random() * 15); // Jet streams
      }

      const lon = Math.random() * 360 - 180;
      const isWesterly = Math.abs(lat) >= 28 && Math.abs(lat) <= 60;
      const speed = isWesterly ? (0.010 + Math.random() * 0.008) : (-0.007 - Math.random() * 0.006);

      const pos = latLonToVector3(lat, lon, radius);
      positions[i * 3]     = pos.x;
      positions[i * 3 + 1] = pos.y;
      positions[i * 3 + 2] = pos.z;

      const isJet = Math.abs(lat) >= 38 && Math.abs(lat) <= 60;
      colors[i * 3]     = isJet ? 0.30 : 0.08;
      colors[i * 3 + 1] = isJet ? 0.95 : 0.82;
      colors[i * 3 + 2] = 0.98;

      particlesData.push({
        lat,
        lon,
        speed,
        radius: radius + (Math.random() - 0.5) * 0.5
      });
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.PointsMaterial({
      size: 2.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.70,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const pts = new THREE.Points(geo, mat);
    group.add(pts);
    group.userData = { points: pts, particlesData, geo, speedFactor: 1.0 };
    return group;
  }

  // 2. DYNAMIC FALLING RAIN STREAKS & PRECIPITATION SYSTEM
  function createPrecipitationMoistureLayer() {
    const group = new THREE.Group();
    const rainCount = 1200;
    const streakLength = 3.6;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(rainCount * 2 * 3); // 2 vertices per line streak
    const colors = new Float32Array(rainCount * 2 * 3);
    const rainData = [];

    for (let i = 0; i < rainCount; i++) {
      let lat, lon;
      const r = Math.random();
      if (r < 0.45) {
        // Mediterranean storm track & North Africa coastal belt (Alexandria, Delta, Levant)
        lat = 27 + Math.random() * 18;
        lon = 20 + Math.random() * 25;
      } else if (r < 0.75) {
        // Equatorial rain belt (ITCZ)
        lat = (Math.random() - 0.3) * 16;
        lon = Math.random() * 360 - 180;
      } else {
        // Global rain corridors
        lat = (Math.random() - 0.5) * 80;
        lon = Math.random() * 360 - 180;
      }

      const baseRadius = EARTH_RADIUS + 0.8 + Math.random() * 10.0;
      const fallSpeed = 0.22 + Math.random() * 0.18;

      rainData.push({
        lat,
        lon,
        currentRadius: baseRadius,
        minRadius: EARTH_RADIUS + 0.6,
        maxRadius: EARTH_RADIUS + 12.0,
        speed: fallSpeed,
        streakLength: streakLength * (0.8 + Math.random() * 0.5)
      });

      const topPos = latLonToVector3(lat, lon, baseRadius + streakLength);
      const btmPos = latLonToVector3(lat, lon, baseRadius);

      const idx = i * 6;
      positions[idx]     = topPos.x;
      positions[idx + 1] = topPos.y;
      positions[idx + 2] = topPos.z;
      positions[idx + 3] = btmPos.x;
      positions[idx + 4] = btmPos.y;
      positions[idx + 5] = btmPos.z;

      // Cyan-blue rain line gradient (top is faint, bottom is bright cyan/blue)
      colors[idx]     = 0.10;
      colors[idx + 1] = 0.55;
      colors[idx + 2] = 0.95;
      colors[idx + 3] = 0.35;
      colors[idx + 4] = 0.95;
      colors[idx + 5] = 1.00;
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const lineMat = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.88,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const lines = new THREE.LineSegments(geo, lineMat);
    group.add(lines);

    // Surface Rain Splash Ripples
    const rippleCount = 35;
    const rippleGeo = new THREE.RingGeometry(0.8, 1.4, 16);
    const rippleMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.65,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const ripples = [];
    for (let r = 0; r < rippleCount; r++) {
      const mesh = new THREE.Mesh(rippleGeo, rippleMat.clone());
      const rLat = 28 + Math.random() * 6;
      const rLon = 28 + Math.random() * 6;
      const rPos = latLonToVector3(rLat, rLon, EARTH_RADIUS + 0.3);
      mesh.position.copy(rPos);
      mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), rPos.clone().normalize());
      mesh.userData = { scale: 0.5 + Math.random() * 1.5, speed: 0.04 + Math.random() * 0.03 };
      group.add(mesh);
      ripples.push(mesh);
    }

    group.userData = { lines, geo, rainData, ripples, intensity: 1.0 };
    return group;
  }

  function placeHeatColumn(lat, lon) {
    if (!heatColumn) return;
    const pos = latLonToVector3(lat, lon, EARTH_RADIUS);
    const normal = pos.clone().normalize();
    heatColumn.position.copy(pos);
    heatColumn.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
  }

  // Create Starfield Background
  function createStarfield() {
    const starGeo = new THREE.BufferGeometry();
    const starCount = 1800;
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount * 3; i += 3) {
      const dist = 500 + Math.random() * 700;
      const u = Math.random();
      const v = Math.random();
      const theta = 2 * Math.PI * u;
      const phi = Math.acos(2 * v - 1);
      positions[i]     = dist * Math.sin(phi) * Math.cos(theta);
      positions[i + 1] = dist * Math.sin(phi) * Math.sin(theta);
      positions[i + 2] = dist * Math.cos(phi);

      const isCyan = Math.random() > 0.7;
      colors[i]     = isCyan ? 0.3 : 0.85;
      colors[i + 1] = isCyan ? 0.85 : 0.88;
      colors[i + 2] = 1.0;
    }

    starGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    starGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const starMat = new THREE.PointsMaterial({
      size: 1.5,
      vertexColors: true,
      transparent: true,
      opacity: 0.85
    });

    return new THREE.Points(starGeo, starMat);
  }

  // Create Orbital Tracks & Satellites
  function createOrbitalTracks() {
    const group = new THREE.Group();
    const orbits = [
      { name: 'Sentinel-6 (Polar)', r: 125, tiltX: 1.1, tiltZ: 0.4, color: 0x4cd6fb, speed: 0.008 },
      { name: 'SWOT (Wide-Swath)',  r: 135, tiltX: 0.5, tiltZ: 1.2, color: 0x8a3ffc, speed: 0.006 },
      { name: 'MODIS Terra',        r: 118, tiltX: 1.4, tiltZ: -0.3, color: 0xffafd1, speed: 0.010 },
      { name: 'PACE (Atmospheric)', r: 142, tiltX: 0.2, tiltZ: 0.8, color: 0x00b2d6, speed: 0.005 }
    ];

    group.userData.satellites = [];

    orbits.forEach(orb => {
      // Orbit Ring Geometry
      const curve = new THREE.EllipseCurve(0, 0, orb.r, orb.r, 0, 2 * Math.PI, false, 0);
      const points = curve.getPoints(120);
      const geom = new THREE.BufferGeometry().setFromPoints(points);

      const mat = new THREE.LineBasicMaterial({
        color: orb.color,
        transparent: true,
        opacity: 0.35,
        linewidth: 1
      });

      const line = new THREE.Line(geom, mat);
      line.rotation.x = orb.tiltX;
      line.rotation.z = orb.tiltZ;
      group.add(line);

      // Satellite mesh
      const satGeom = new THREE.SphereGeometry(1.4, 8, 8);
      const satMat = new THREE.MeshBasicMaterial({ color: orb.color });
      const satMesh = new THREE.Mesh(satGeom, satMat);

      // Satellite glow beacon
      const satGlowGeom = new THREE.SphereGeometry(2.5, 8, 8);
      const satGlowMat = new THREE.MeshBasicMaterial({ color: orb.color, transparent: true, opacity: 0.45 });
      const satGlow = new THREE.Mesh(satGlowGeom, satGlowMat);
      satMesh.add(satGlow);

      group.add(satMesh);
      group.userData.satellites.push({
        mesh: satMesh,
        r: orb.r,
        tiltX: orb.tiltX,
        tiltZ: orb.tiltZ,
        speed: orb.speed,
        angle: Math.random() * Math.PI * 2
      });
    });

    return group;
  }

  // Create Marker Pin & Radar Ring for a Region
  function createRegionMarker(region, idx) {
    const pos = latLonToVector3(region.lat, region.lon, EARTH_RADIUS);
    const normal = pos.clone().normalize();
    const markerGroup = new THREE.Group();
    markerGroup.position.copy(pos);
    markerGroup.userData = { region, idx };

    // 1. Vertical Pin / Stem projecting outwards
    const pinHeight = 12;
    const pinGeo = new THREE.CylinderGeometry(0.4, 0.4, pinHeight, 8);
    const pinMat = new THREE.MeshBasicMaterial({
      color: 0x4cd6fb,
      transparent: true,
      opacity: 0.85
    });
    const pinMesh = new THREE.Mesh(pinGeo, pinMat);
    pinMesh.position.copy(normal.clone().multiplyScalar(pinHeight / 2));
    pinMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
    markerGroup.add(pinMesh);

    // 2. Glowing Beacon Head
    const headGeo = new THREE.SphereGeometry(1.6, 12, 12);
    const headMat = new THREE.MeshBasicMaterial({ color: 0xffafd1 });
    const headMesh = new THREE.Mesh(headGeo, headMat);
    headMesh.position.copy(normal.clone().multiplyScalar(pinHeight));
    headMesh.userData = { region, idx, isClickable: true };
    markerGroup.add(headMesh);

    // 3. Radar Wave Ring on Surface
    const ringGeo = new THREE.RingGeometry(1.5, 2.2, 24);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x4cd6fb,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.7
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
    markerGroup.add(ringMesh);
    markerGroup.userData.ring = ringMesh;

    // 4. Text Sprite Label
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'rgba(16, 19, 28, 0.85)';
    ctx.roundRect ? ctx.roundRect(4, 8, 248, 48, 8) : ctx.fillRect(4, 8, 248, 48);
    ctx.fill();
    ctx.strokeStyle = '#8B5CF6';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 18px "JetBrains Mono", monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const label = region.name_en ? region.name_en.split(' ')[0] : 'Sector';
    ctx.fillText(label, 128, 32);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: 0.9 });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(16, 4, 1);
    sprite.position.copy(normal.clone().multiplyScalar(pinHeight + 4));
    markerGroup.add(sprite);

    return markerGroup;
  }

  // Initialize Three.js 3D Earth
  function initEarth3D() {
    const container = document.getElementById('earth-3d-canvas');
    if (!container) return;

    // Clear any previous canvas
    container.innerHTML = '';
    const width = container.clientWidth || 800;
    const height = container.clientHeight || 500;

    // Scene & Camera
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, width / height, 1, 3000);
    camera.position.set(0, 40, 720);
    introProgress = 0;

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(200, 100, 150);
    scene.add(dirLight);

    rimLight = new THREE.DirectionalLight(0x4cd6fb, 0.8);
    rimLight.position.set(-200, -50, -100);
    scene.add(rimLight);

    // Groups
    globeGroup = new THREE.Group();
    markersGroup = new THREE.Group();
    orbitsGroup = createOrbitalTracks();
    starsGroup = createStarfield();

    scene.add(starsGroup);
    scene.add(globeGroup);
    globeGroup.add(markersGroup);
    scene.add(orbitsGroup);

    // Base Sphere
    const earthGeo = new THREE.SphereGeometry(EARTH_RADIUS, 64, 64);
    const textureLoader = new THREE.TextureLoader();

    // Default procedural fallback texture
    const earthMat = new THREE.MeshStandardMaterial({
      map: createProceduralEarthTexture(),
      roughness: 0.65,
      metalness: 0.15
    });

    earthMesh = new THREE.Mesh(earthGeo, earthMat);
    globeGroup.add(earthMesh);

    // Load High-Res NASA Texture Asynchronously
    textureLoader.load(
      TEXTURE_URLS.day,
      tex => {
        tex.wrapS = THREE.RepeatWrapping;
        tex.wrapT = THREE.ClampToEdgeWrapping;
        earthMat.map = tex;
        earthMat.needsUpdate = true;
      },
      undefined,
      err => console.log('Using procedural NASA earth texture fallback')
    );

    // Cloud Layer
    const cloudsGeo = new THREE.SphereGeometry(EARTH_RADIUS + 1.2, 48, 48);
    const cloudsMat = new THREE.MeshStandardMaterial({
      transparent: true,
      opacity: 0.28,
      blending: THREE.AdditiveBlending
    });
    cloudsMesh = new THREE.Mesh(cloudsGeo, cloudsMat);
    globeGroup.add(cloudsMesh);

    textureLoader.load(TEXTURE_URLS.clouds, tex => {
      cloudsMat.map = tex;
      cloudsMat.needsUpdate = true;
    });

    // Atmospheric Glow Halo
    const atmosGeo = new THREE.SphereGeometry(EARTH_RADIUS + 4.5, 48, 48);
    atmosphereMesh = new THREE.Mesh(atmosGeo, createAtmosphereMaterial());
    globeGroup.add(atmosphereMesh);

    // Thermal overlay + heat column over Egypt
    const heatGeo = new THREE.SphereGeometry(EARTH_RADIUS + 1.6, 64, 64);
    heatMesh = new THREE.Mesh(heatGeo, createHeatOverlayMaterial());
    globeGroup.add(heatMesh);
    heatColumn = createHeatColumn();
    globeGroup.add(heatColumn);
    placeHeatColumn(30.0444, 31.2357);

    // Dynamic Wind & Atmospheric Circulation Layer
    windGroup = createWindStreamlines();
    globeGroup.add(windGroup);

    // Dynamic Precipitation & Moisture Convective Cells Layer
    rainGroup = createPrecipitationMoistureLayer();
    globeGroup.add(rainGroup);

    // Add 10 Regional Hotspot Markers
    if (window.REGIONS) {
      window.REGIONS.forEach((reg, i) => {
        const marker = createRegionMarker(reg, i);
        markersGroup.add(marker);
        markerMeshes.push(marker);
      });
    }

    // Orbit Controls
    if (window.THREE.OrbitControls) {
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.enablePan = false;
      controls.minDistance = 140;
      controls.maxDistance = 550;
      controls.rotateSpeed = 0.6;
      controls.zoomSpeed = 0.8;

      controls.addEventListener('start', () => { autoRotate = false; });
    }

    // Raycast Click Handler
    renderer.domElement.addEventListener('click', onGlobeClick);
    window.addEventListener('resize', onWindowResize);

    // Initial orientation: focus on Cairo (first region)
    if (window.activeRegion) {
      flyToRegion(26.8, 30.8, true);
      placeHeatColumn(window.activeRegion.lat, window.activeRegion.lon);
    }
    setClimateYear(window.__climateYear || 2024, 0);
    if (typeof window.onScrubberChange === 'function') {
      setTimeout(() => window.onScrubberChange(2024), 200);
    }

    // Start Render Loop
    animate();
  }

  // Smooth Fly-To / Slerp Camera & Dramatic Zoom-In to Target Region
  function flyToRegion(lat, lon, instant = false, targetDistance = 175) {
    if (!globeGroup) return;

    // Calculate rotation required to center lat/lon facing the camera (z-axis)
    const targetY = -(lon + 90) * (Math.PI / 180);
    const targetX = lat * (Math.PI / 180) * 0.42;

    targetRotation.y = targetY;
    targetRotation.x = targetX;

    placeHeatColumn(lat, lon);
    placeSearchTargetBeacon(lat, lon);

    if (instant) {
      globeGroup.rotation.y = targetY;
      globeGroup.rotation.x = targetX;
      if (camera) {
        const dir = camera.position.clone().normalize();
        camera.position.copy(dir.multiplyScalar(targetDistance));
        if (controls) controls.update();
      }
    } else {
      isFlying = true;
      autoRotate = false;
      if (camera) {
        isZooming = true;
        zoomProgress = 0;
        zoomStartDistance = camera.position.length();
        zoomTargetDistance = targetDistance || 175;
      }
      setTimeout(() => { isFlying = false; }, 1600);
    }
  }

  function placeSearchTargetBeacon(lat, lon) {
    if (!globeGroup) return;
    let beacon = globeGroup.getObjectByName('searchTargetBeacon');
    if (!beacon) {
      beacon = new THREE.Group();
      beacon.name = 'searchTargetBeacon';

      // Outer radar ring
      const ringGeo = new THREE.RingGeometry(2.5, 4.2, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x06b6d4,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.95
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      beacon.add(ringMesh);
      beacon.userData.ring = ringMesh;

      // Inner glowing core
      const coreGeo = new THREE.SphereGeometry(2.2, 16, 16);
      const coreMat = new THREE.MeshBasicMaterial({ color: 0xffafd1 });
      const coreMesh = new THREE.Mesh(coreGeo, coreMat);
      beacon.add(coreMesh);

      globeGroup.add(beacon);
    }

    const pos = latLonToVector3(lat, lon, EARTH_RADIUS + 0.8);
    const normal = pos.clone().normalize();
    beacon.position.copy(pos);
    beacon.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
    beacon.visible = true;
  }

  // Click on globe markers
  function onGlobeClick(e) {
    if (!renderer || !camera) return;
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(markersGroup.children, true);

    if (intersects.length > 0) {
      let target = intersects[0].object;
      while (target && (!target.userData || target.userData.idx === undefined)) {
        target = target.parent;
      }
      if (target && target.userData && target.userData.region) {
        const { region, idx } = target.userData;
        if (window.switchRegion) {
          window.switchRegion(region, idx);
        }
      }
    }
  }

  // Window Resize
  function onWindowResize() {
    const container = document.getElementById('earth-3d-canvas');
    if (!container || !renderer || !camera) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  // Animation Loop
  let clock = new THREE.Clock ? new THREE.Clock() : { getElapsedTime: () => Date.now() * 0.001 };
  let ringScale = 1;

  function animate() {
    animationId = requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime ? clock.getElapsedTime() : Date.now() * 0.001;

    // Controls update
    if (controls) controls.update();

    // Slerp rotation during fly-to
    if (isFlying && globeGroup) {
      globeGroup.rotation.y += (targetRotation.y - globeGroup.rotation.y) * 0.08;
      globeGroup.rotation.x += (targetRotation.x - globeGroup.rotation.x) * 0.08;
    } else if (autoRotate && globeGroup) {
      globeGroup.rotation.y += 0.0012;
    }

    // Dynamic cloud rotation
    if (cloudsMesh) {
      cloudsMesh.rotation.y += 0.0018;
    }

    // Animate Satellite Constellations along their orbits
    if (orbitsGroup && orbitsGroup.userData.satellites) {
      orbitsGroup.userData.satellites.forEach(sat => {
        sat.angle += sat.speed;
        const x = sat.r * Math.cos(sat.angle);
        const y = sat.r * Math.sin(sat.angle);
        // Apply orbit tilt rotation
        const pos = new THREE.Vector3(x, y, 0);
        pos.applyAxisAngle(new THREE.Vector3(1, 0, 0), sat.tiltX);
        pos.applyAxisAngle(new THREE.Vector3(0, 0, 1), sat.tiltZ);
        sat.mesh.position.copy(pos);
      });
    }

    // Cinematic intro: drop in from high orbit
    if (introProgress < 1 && camera) {
      introProgress = Math.min(1, introProgress + 0.012);
      const ease = 1 - Math.pow(1 - introProgress, 3);
      camera.position.z = 720 + (290 - 720) * ease;
      camera.position.y = 40 + (20 - 40) * ease;
    }

    // Smooth camera zoom interpolation during fly-to & location search
    if (isZooming && camera) {
      zoomProgress = Math.min(1, zoomProgress + 0.026);
      const ease = 0.5 - Math.cos(zoomProgress * Math.PI) / 2;
      const currentDist = zoomStartDistance + (zoomTargetDistance - zoomStartDistance) * ease;
      const dir = camera.position.clone().normalize();
      camera.position.copy(dir.multiplyScalar(currentDist));
      if (controls) controls.update();
      if (zoomProgress >= 1) {
        isZooming = false;
      }
    }

    // Dynamic search target beacon radar pulsing
    const searchBeacon = globeGroup && globeGroup.getObjectByName('searchTargetBeacon');
    if (searchBeacon && searchBeacon.userData.ring) {
      const bScale = 1 + (Math.sin(elapsed * 6) * 0.5 + 0.5) * 1.8;
      searchBeacon.userData.ring.scale.set(bScale, bScale, 1);
      searchBeacon.userData.ring.material.opacity = Math.max(0.15, 1.0 - (bScale - 1) * 0.55);
    }

    // Animate radar wave rings expanding at active marker
    ringScale = 1 + (Math.sin(elapsed * 4) * 0.5 + 0.5) * 1.4;
    markersGroup.children.forEach(m => {
      if (m.userData.ring) {
        m.userData.ring.scale.set(ringScale, ringScale, 1);
        m.userData.ring.material.opacity = Math.max(0.1, 0.9 - (ringScale - 1) * 0.6);
      }
    });

    // Animate Wind Streamline Particles
    if (windGroup && windGroup.userData && windGroup.userData.particlesData) {
      const pData = windGroup.userData.particlesData;
      const factor = windGroup.userData.speedFactor || 1.0;
      const posAttr = windGroup.userData.geo.attributes.position;
      const posArray = posAttr.array;

      for (let i = 0; i < pData.length; i++) {
        const p = pData[i];
        p.lon += p.speed * factor * 40;
        if (p.lon > 180) p.lon -= 360;
        if (p.lon < -180) p.lon += 360;

        const newPos = latLonToVector3(p.lat, p.lon, p.radius);
        posArray[i * 3]     = newPos.x;
        posArray[i * 3 + 1] = newPos.y;
        posArray[i * 3 + 2] = newPos.z;
      }
      posAttr.needsUpdate = true;
    }

    // Animate Falling Rain Streaks & Impact Ripples
    if (rainGroup && rainGroup.userData && rainGroup.userData.rainData) {
      const rData = rainGroup.userData.rainData;
      const intensity = rainGroup.userData.intensity || 1.0;
      const posAttr = rainGroup.userData.geo.attributes.position;
      const posArray = posAttr.array;

      for (let i = 0; i < rData.length; i++) {
        const drop = rData[i];
        drop.currentRadius -= drop.speed * intensity;
        if (drop.currentRadius <= drop.minRadius) {
          drop.currentRadius = drop.maxRadius;
        }

        const topPos = latLonToVector3(drop.lat, drop.lon, drop.currentRadius + drop.streakLength);
        const btmPos = latLonToVector3(drop.lat, drop.lon, drop.currentRadius);

        const idx = i * 6;
        posArray[idx]     = topPos.x;
        posArray[idx + 1] = topPos.y;
        posArray[idx + 2] = topPos.z;
        posArray[idx + 3] = btmPos.x;
        posArray[idx + 4] = btmPos.y;
        posArray[idx + 5] = btmPos.z;
      }
      posAttr.needsUpdate = true;

      // Animate Surface Rain Splash Ripples
      if (rainGroup.userData.ripples) {
        rainGroup.userData.ripples.forEach(rp => {
          rp.userData.scale += rp.userData.speed * intensity;
          if (rp.userData.scale > 2.8) {
            rp.userData.scale = 0.4;
          }
          rp.scale.set(rp.userData.scale, rp.userData.scale, 1);
          rp.material.opacity = Math.max(0, 0.70 - (rp.userData.scale / 2.8));
        });
      }
    }

    if (heatColumn) {
      const pulse = 0.88 + Math.sin(elapsed * 2.8) * 0.12;
      heatColumn.scale.set(0.85 * pulse, 0.95, 0.85 * pulse);
    }

    renderer.render(scene, camera);
  }

  function setClimateYear(year, anomaly) {
    const y = Number(year);
    const t = Math.max(0, Math.min(1, (y - 2000) / 50));
    climateState.year = y;
    climateState.heat = t;
    climateState.anomaly = Number(anomaly) || 0;

    // 1. Atmosphere halo remains cool aerospace cyan (NEVER turns red!)
    if (atmosphereMesh && atmosphereMesh.material && atmosphereMesh.material.uniforms && atmosphereMesh.material.uniforms.uHeat) {
      atmosphereMesh.material.uniforms.uHeat.value = 0.2 + t * 0.3;
    }

    // 2. Regional thermal heat overlay over Egypt and North Africa (soft amber/gold isotherms, never all-red)
    if (heatMesh && heatMesh.material && heatMesh.material.uniforms && heatMesh.material.uniforms.uHeat) {
      heatMesh.material.uniforms.uHeat.value = t;
      heatMesh.visible = (activePlanetLayer === 'temp' || activePlanetLayer === 'all');
    }

    // 3. Orbital rim light remains crisp celestial light (NEVER red!)
    if (rimLight) {
      rimLight.color.setRGB(0.70, 0.88, 1.0);
      rimLight.intensity = 0.95;
    }

    // 4. Earth surface color stays completely natural (NEVER turns red!)
    if (earthMesh && earthMesh.material) {
      earthMesh.material.color.setRGB(1.0, 1.0, 1.0);
      if (earthMesh.material.emissive) {
        earthMesh.material.emissive.setRGB(0, 0, 0); // No red emissive!
        earthMesh.material.emissiveIntensity = 0.0;
      }
      earthMesh.material.needsUpdate = true;
    }

    // 5. Dynamic Wind Circulation responds to timeline
    const windFactor = 1.0 + t * 0.75 + Math.cos(t * Math.PI * 3) * 0.25;
    if (windGroup && windGroup.userData) {
      windGroup.userData.speedFactor = windFactor;
      windGroup.visible = (activePlanetLayer === 'wind' || activePlanetLayer === 'all');
    }

    // 6. Dynamic Precipitation & Cloud Moisture responds to timeline
    const rainFactor = 1.0 + Math.sin(t * Math.PI * 4) * 0.35 + (t * 0.15);
    if (rainGroup && rainGroup.userData) {
      rainGroup.userData.intensity = rainFactor;
      rainGroup.visible = (activePlanetLayer === 'rain' || activePlanetLayer === 'all');
    }
    if (cloudsMesh && cloudsMesh.material) {
      cloudsMesh.material.opacity = 0.24 + rainFactor * 0.10;
      cloudsMesh.visible = (activePlanetLayer === 'rain' || activePlanetLayer === 'all');
    }

    // 7. Sensor Beacon pulsation & Thermal Column above active sector
    if (heatColumn) {
      const pulse = 0.85 + Math.sin(t * 8.0) * 0.15;
      heatColumn.scale.set(0.8 + t * 0.9 * pulse, 0.75 + t * 1.3, 0.8 + t * 0.9 * pulse);
      if (heatColumn.userData.cone && heatColumn.userData.core) {
        heatColumn.userData.cone.material.opacity = 0.20 + t * 0.45;
        // Thermal beacon shifts color dynamically with temperature:
        // 2000 cool cyan -> 2024 warming gold -> 2050 radiant solar amber
        heatColumn.userData.cone.material.color.setHSL(0.52 - t * 0.42, 1.0, 0.55);
        heatColumn.userData.core.material.color.setHSL(0.52 - t * 0.42, 1.0, 0.65);
      }
    }
  }

  function setPlanetLayer(layer) {
    activePlanetLayer = layer || 'all';
    if (heatMesh) {
      heatMesh.visible = (activePlanetLayer === 'temp' || activePlanetLayer === 'all');
      if (heatMesh.material && heatMesh.material.uniforms && activePlanetLayer === 'temp') {
        heatMesh.material.uniforms.uHeat.value = Math.max(0.65, climateState.heat);
      }
    }
    if (windGroup) {
      windGroup.visible = (activePlanetLayer === 'wind' || activePlanetLayer === 'all');
      if (windGroup.userData && activePlanetLayer === 'wind') {
        windGroup.userData.speedFactor = 2.2;
      }
    }
    if (rainGroup) {
      rainGroup.visible = (activePlanetLayer === 'rain' || activePlanetLayer === 'all');
      if (rainGroup.userData && activePlanetLayer === 'rain') {
        rainGroup.userData.intensity = 2.2;
      }
    }
    if (cloudsMesh) cloudsMesh.visible = true;

    // Update layer selector pill classes
    document.querySelectorAll('.globe-layer-pill').forEach(btn => {
      const l = btn.getAttribute('data-layer');
      if (l === activePlanetLayer) {
        btn.classList.add('bg-cyan-500/25', 'text-cyan-300', 'border-cyan-400');
        btn.classList.remove('bg-black/60', 'text-slate-400', 'border-white/10');
      } else {
        btn.classList.remove('bg-cyan-500/25', 'text-cyan-300', 'border-cyan-400');
        btn.classList.add('bg-black/60', 'text-slate-400', 'border-white/10');
      }
    });
  }

  function setActiveRegion(lat, lon) {
    placeHeatColumn(lat, lon);
  }

  // Public Interface
  window.Earth3D = {
    init: initEarth3D,
    flyTo: flyToRegion,
    setClimateYear,
    setPlanetLayer,
    setActiveRegion,
    toggleAutoRotate: (val) => { autoRotate = val !== undefined ? val : !autoRotate; },
    getRenderer: () => renderer
  };

  // Auto-init when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(initEarth3D, 150));
  } else {
    setTimeout(initEarth3D, 150);
  }

})();

