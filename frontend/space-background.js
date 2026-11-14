/**
 * 6S Nova // Deep Space Background Engine
 * Exact 3D Rotating Starfield Sphere matching https://www.ahmed3nter.online/
 * Developed with Three.js (Sphere radius 15, 5,000 star points, AdditiveBlending, Cyber-Black)
 */
(function () {
  'use strict';

  function initAhmedAntarSpaceBackground() {
    const canvas = document.getElementById('starfield-canvas');
    if (!canvas) return;

    // Check Three.js availability
    if (typeof THREE === 'undefined') {
      setTimeout(initAhmedAntarSpaceBackground, 100);
      return;
    }

    let width = window.innerWidth;
    let height = window.innerHeight;

    const renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 0, 10);

    // ── 1. Primary 3D Star Sphere (5,000 Stars / 15,000 Points inside Sphere R=15) ──
    const starCount = 5000;
    const starPositions = new Float32Array(starCount * 3);
    const starColors = new Float32Array(starCount * 3);

    const radius = 15;
    for (let i = 0; i < starCount; i++) {
      // Uniform random distribution in sphere
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = Math.cbrt(Math.random()) * radius;

      const sinPhi = Math.sin(phi);
      const x = r * sinPhi * Math.cos(theta);
      const y = r * sinPhi * Math.sin(theta);
      const z = r * Math.cos(phi);

      const i3 = i * 3;
      starPositions[i3] = x;
      starPositions[i3 + 1] = y;
      starPositions[i3 + 2] = z;

      // Color variation: 70% Cyan (#00f0ff), 20% Starlight White, 10% Cyber Purple (#7a00ff)
      const randColor = Math.random();
      if (randColor < 0.70) {
        starColors[i3] = 0.0;     // R
        starColors[i3 + 1] = 0.94; // G
        starColors[i3 + 2] = 1.0;  // B (#00f0ff)
      } else if (randColor < 0.90) {
        starColors[i3] = 1.0;
        starColors[i3 + 1] = 1.0;
        starColors[i3 + 2] = 1.0;  // White
      } else {
        starColors[i3] = 0.48;
        starColors[i3 + 1] = 0.0;
        starColors[i3 + 2] = 1.0;  // Cyber Purple
      }
    }

    const starGeo = new THREE.BufferGeometry();
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));

    // Particle Material matching ahmed3nter.online
    const starMat = new THREE.PointsMaterial({
      size: 0.038,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.88,
      vertexColors: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const starGroup = new THREE.Group();
    starGroup.rotation.set(0, 0, Math.PI / 4);

    const starPoints = new THREE.Points(starGeo, starMat);
    starGroup.add(starPoints);

    // ── 2. Subtle Signature Orbital Tech Ring (Right Horizon as in ahmed3nter.online) ──
    const orbitRadius = 4.2;
    const ringSegments = 128;
    const ringGeo = new THREE.BufferGeometry();
    const ringPositions = new Float32Array((ringSegments + 1) * 3);
    for (let i = 0; i <= ringSegments; i++) {
      const theta = (i / ringSegments) * Math.PI * 2;
      ringPositions[i * 3] = Math.cos(theta) * orbitRadius;
      ringPositions[i * 3 + 1] = Math.sin(theta) * orbitRadius;
      ringPositions[i * 3 + 2] = 0;
    }
    ringGeo.setAttribute('position', new THREE.BufferAttribute(ringPositions, 3));
    const ringMat = new THREE.LineBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.16,
      blending: THREE.AdditiveBlending
    });
    const ring = new THREE.Line(ringGeo, ringMat);
    ring.position.set(3.8, -0.6, -1.0);
    ring.rotation.set(0.9, 0.4, 0.2);
    starGroup.add(ring);

    // Orbital Satellite Node on the Ring
    const nodeGeo = new THREE.SphereGeometry(0.09, 16, 16);
    const nodeMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.95
    });
    const node = new THREE.Mesh(nodeGeo, nodeMat);
    starGroup.add(node);

    scene.add(starGroup);

    // ── 3. Smooth Mouse Parallax Tracking ──
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    window.addEventListener('mousemove', (e) => {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 0.4;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 0.4;
    });

    // ── 4. Continuous Animation Loop ──
    let lastTime = performance.now();
    let ringAngle = 0;

    function animate(currentTime) {
      requestAnimationFrame(animate);

      const delta = Math.min((currentTime - lastTime) / 1000, 0.1);
      lastTime = currentTime;

      // Exact rotation speed from ahmed3nter.online:
      // t.current.rotation.x -= r / 30; t.current.rotation.y -= r / 35;
      starPoints.rotation.x -= delta / 30;
      starPoints.rotation.y -= delta / 35;

      // Animate node orbiting along the tech ring
      ringAngle += delta * 0.4;
      const nx = Math.cos(ringAngle) * orbitRadius;
      const ny = Math.sin(ringAngle) * orbitRadius;
      const p = new THREE.Vector3(nx, ny, 0).applyEuler(ring.rotation).add(ring.position);
      node.position.copy(p);

      // Smooth mouse parallax easing
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;
      camera.position.x = targetX * 1.5;
      camera.position.y = -targetY * 1.5;
      camera.lookAt(0, 0, 0);

      renderer.render(scene, camera);
    }
    requestAnimationFrame(animate);

    // ── 5. Responsive Resize Handling ──
    window.addEventListener('resize', () => {
      width = window.innerWidth;
      height = window.innerHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAhmedAntarSpaceBackground);
  } else {
    initAhmedAntarSpaceBackground();
  }
})();
