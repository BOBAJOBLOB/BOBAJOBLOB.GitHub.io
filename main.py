<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V8 Engine Simulator</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0a0a0c;
    --surface: #111116;
    --panel: #16161d;
    --border: #2a2a38;
    --fire: #ff4500;
    --fire2: #ff8c00;
    --fire3: #ffd700;
    --exhaust: #1a3a5c;
    --intake: #1a4a2a;
    --piston: #3a3a4a;
    --piston-active: #cc3300;
    --text: #e0e0f0;
    --dim: #666680;
    --accent: #ff4500;
    --green: #00ff88;
    --teal: #00ccdd;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow-x: hidden;
  }

  /* Scanline overlay */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.08) 2px,
      rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 1000;
  }

  header {
    width: 100%;
    padding: 20px 24px 12px;
    text-align: center;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, #0d0d12 0%, transparent 100%);
  }

  header h1 {
    font-family: 'Orbitron', monospace;
    font-weight: 900;
    font-size: clamp(1.4rem, 5vw, 2.4rem);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    background: linear-gradient(135deg, var(--fire) 0%, var(--fire2) 50%, var(--fire3) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    filter: drop-shadow(0 0 20px rgba(255,69,0,0.5));
  }

  header p {
    color: var(--dim);
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    margin-top: 4px;
  }

  .main {
    width: 100%;
    max-width: 900px;
    padding: 20px 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  /* Engine canvas area */
  .engine-wrap {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px;
    position: relative;
    overflow: hidden;
  }

  .engine-wrap::before {
    content: 'ENGINE BLOCK';
    position: absolute;
    top: 8px; left: 12px;
    font-size: 0.6rem;
    letter-spacing: 0.25em;
    color: var(--dim);
  }

  canvas {
    display: block;
    width: 100%;
    height: auto;
    image-rendering: crisp-edges;
  }

  /* Controls */
  .controls {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .control-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px;
  }

  .control-label {
    font-size: 0.6rem;
    letter-spacing: 0.25em;
    color: var(--dim);
    margin-bottom: 10px;
    text-transform: uppercase;
  }

  /* RPM display */
  .rpm-display {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2rem, 6vw, 3.5rem);
    font-weight: 700;
    color: var(--green);
    text-shadow: 0 0 20px rgba(0,255,136,0.5);
    line-height: 1;
    letter-spacing: 0.05em;
  }

  .rpm-unit {
    font-size: 0.65rem;
    color: var(--dim);
    letter-spacing: 0.2em;
    margin-top: 4px;
  }

  /* Slider */
  input[type=range] {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    outline: none;
    margin: 14px 0 8px;
    cursor: pointer;
  }

  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    background: var(--fire);
    border-radius: 50%;
    border: 2px solid var(--fire3);
    box-shadow: 0 0 12px rgba(255,69,0,0.7);
    cursor: pointer;
    transition: box-shadow 0.2s;
  }

  input[type=range]::-webkit-slider-thumb:hover {
    box-shadow: 0 0 20px rgba(255,69,0,1);
  }

  input[type=range]::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--fire);
    border-radius: 50%;
    border: 2px solid var(--fire3);
    box-shadow: 0 0 12px rgba(255,69,0,0.7);
    cursor: pointer;
  }

  .slider-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.6rem;
    color: var(--dim);
    letter-spacing: 0.1em;
  }

  /* Firing order display */
  .firing-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 4px;
    margin-top: 8px;
  }

  .cyl-badge {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    border: 1px solid var(--border);
    border-radius: 3px;
    background: var(--surface);
    color: var(--dim);
    transition: all 0.08s ease;
  }

  .cyl-badge.active {
    background: var(--fire);
    color: #fff;
    border-color: var(--fire3);
    box-shadow: 0 0 16px rgba(255,69,0,0.8);
    color: #fff;
    text-shadow: 0 0 8px rgba(255,255,255,0.8);
    transform: scale(1.08);
  }

  /* Stats row */
  .stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }

  .stat-box {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px 14px;
    text-align: center;
  }

  .stat-val {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--teal);
    text-shadow: 0 0 12px rgba(0,200,220,0.5);
  }

  .stat-lbl {
    font-size: 0.55rem;
    letter-spacing: 0.2em;
    color: var(--dim);
    margin-top: 4px;
    text-transform: uppercase;
  }

  /* Buttons */
  .btn-row {
    display: flex;
    gap: 10px;
  }

  button {
    flex: 1;
    padding: 12px;
    border: 1px solid var(--border);
    border-radius: 3px;
    background: var(--surface);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    cursor: pointer;
    text-transform: uppercase;
    transition: all 0.15s;
  }

  button:hover { border-color: var(--accent); color: var(--accent); }

  button.primary {
    background: var(--fire);
    border-color: var(--fire3);
    color: #fff;
    font-weight: bold;
    box-shadow: 0 0 16px rgba(255,69,0,0.4);
  }

  button.primary:hover {
    background: var(--fire2);
    box-shadow: 0 0 24px rgba(255,140,0,0.6);
    color: #fff;
  }

  /* Stroke indicator */
  .stroke-indicator {
    display: flex;
    gap: 6px;
    margin-top: 8px;
    flex-wrap: wrap;
  }

  .stroke-pill {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    border: 1px solid var(--border);
    color: var(--dim);
    background: var(--surface);
    transition: all 0.1s;
  }

  .stroke-pill.active-intake   { background: #0a2a14; border-color: #00aa44; color: #00ff88; }
  .stroke-pill.active-compress { background: #0a1a2a; border-color: #0044aa; color: #4488ff; }
  .stroke-pill.active-power    { background: #2a0a00; border-color: #aa2200; color: #ff4400; }
  .stroke-pill.active-exhaust  { background: #1a1a0a; border-color: #aaaa00; color: #dddd00; }

  @media (max-width: 540px) {
    .controls { grid-template-columns: 1fr; }
    .stats { grid-template-columns: repeat(3,1fr); }
  }
</style>
</head>
<body>

<header>
  <h1>V8 Engine Simulator</h1>
  <p>FIRING ORDER: 1 · 5 · 4 · 8 · 6 · 3 · 7 · 2</p>
</header>

<div class="main">

  <div class="engine-wrap">
    <canvas id="engineCanvas" width="860" height="320"></canvas>
  </div>

  <div class="controls">
    <div class="control-panel">
      <div class="control-label">Engine Speed</div>
      <div class="rpm-display" id="rpmDisplay">800</div>
      <div class="rpm-unit">RPM</div>
      <input type="range" id="rpmSlider" min="100" max="8000" value="800" step="50">
      <div class="slider-labels"><span>IDLE</span><span>REDLINE</span></div>
      <div class="btn-row" style="margin-top:14px">
        <button onclick="setRPM(800)">IDLE</button>
        <button onclick="setRPM(3000)">CRUISE</button>
        <button class="primary" onclick="setRPM(6500)">REDLINE</button>
      </div>
    </div>

    <div class="control-panel">
      <div class="control-label">Firing Sequence</div>
      <div class="firing-grid" id="firingGrid"></div>
      <div class="control-label" style="margin-top:14px">Stroke Phases</div>
      <div class="stroke-indicator" id="strokeIndicator">
        <span class="stroke-pill" id="sp-intake">INTAKE</span>
        <span class="stroke-pill" id="sp-compress">COMPRESS</span>
        <span class="stroke-pill" id="sp-power">POWER</span>
        <span class="stroke-pill" id="sp-exhaust">EXHAUST</span>
      </div>
    </div>
  </div>

  <div class="stats">
    <div class="stat-box">
      <div class="stat-val" id="statFires">0</div>
      <div class="stat-lbl">Total Fires</div>
    </div>
    <div class="stat-box">
      <div class="stat-val" id="statHz">--</div>
      <div class="stat-lbl">Fire Hz</div>
    </div>
    <div class="stat-box">
      <div class="stat-val" id="statCyl">--</div>
      <div class="stat-lbl">Active Cyl</div>
    </div>
  </div>

</div>

<script>
const FIRING_ORDER = [1, 5, 4, 8, 6, 3, 7, 2];
const NUM_CYLINDERS = 8;

// V8 layout: 4 left bank (1,2,3,4) + 4 right bank (5,6,7,8)
// Crank offset per cylinder (720° cycle, 90° between fires)
// Each cylinder: offset = its position in firing order * 90°
const firingIdx = {}; // cyl -> position in firing order
FIRING_ORDER.forEach((c, i) => firingIdx[c] = i);

let rpm = 800;
let crankAngle = 0; // degrees, 0–720
let totalFires = 0;
let lastFireCyl = 0;
let running = true;
let lastTime = null;

// Build firing grid
const grid = document.getElementById('firingGrid');
const badges = {};
FIRING_ORDER.forEach(c => {
  const b = document.createElement('div');
  b.className = 'cyl-badge';
  b.textContent = c;
  b.id = 'badge' + c;
  grid.appendChild(b);
  badges[c] = b;
});

// Slider
const slider = document.getElementById('rpmSlider');
slider.addEventListener('input', () => {
  rpm = parseInt(slider.value);
  document.getElementById('rpmDisplay').textContent = rpm;
});

function setRPM(val) {
  rpm = val;
  slider.value = val;
  document.getElementById('rpmDisplay').textContent = val;
}

// Canvas
const canvas = document.getElementById('engineCanvas');
const ctx = canvas.getContext('2d');
const W = 860, H = 320;

// Cylinder positions: 4 per bank
// Left bank: cylinders 1,2,3,4 (left side)
// Right bank: cylinders 5,6,7,8 (right side)
// We'll lay them horizontally: 8 cylinders in a V layout

// Layout: two banks of 4, displayed as two rows
// Top row = bank A (cylinders 1,3,5,7 in traditional V8, but let's just do top=1,2,3,4 bottom=5,6,7,8)
// Actually let's do: left bank top, right bank bottom, V style

const CYL_CONFIGS = [];
// Bank A (top): cylinders 1,3,5,7 visually left to right
// Bank B (bottom): cylinders 2,4,6,8
// Let's do: 8 cylinders laid out side by side in 2 rows of 4
// Row 1 (top-bank): cyl 1,3,5,7 → positions in firing order
// Row 2 (bottom-bank): cyl 2,4,6,8

function buildLayout() {
  const margin = 40;
  const bankCyls = [[1,3,5,7],[2,4,6,8]]; // just grouping visually
  const spacing = (W - margin*2) / 4;
  bankCyls.forEach((bank, bankIdx) => {
    bank.forEach((cyl, ci) => {
      CYL_CONFIGS.push({
        cyl,
        bank: bankIdx,
        x: margin + ci * spacing + spacing/2,
        yBase: bankIdx === 0 ? H*0.38 : H*0.88,
        dir: bankIdx === 0 ? -1 : 1  // piston moves up or down
      });
    });
  });
}
buildLayout();

// Crankshaft angle offset per cylinder (each fires 90° apart)
function getCylCrankOffset(cyl) {
  return firingIdx[cyl] * 90; // 0–630°
}

// Piston position: 0=TDC, 1=BDC, based on crank angle in cylinder's 720° cycle
function pistonPos(cyl, crankAngle) {
  const offset = getCylCrankOffset(cyl);
  const localAngle = ((crankAngle - offset) % 720 + 720) % 720;
  // Simple sinusoidal approximation
  return (1 - Math.cos(localAngle * Math.PI / 360)) / 2; // 0 at TDC, 1 at BDC
}

// Stroke phase for cylinder
function strokePhase(cyl, crankAngle) {
  const offset = getCylCrankOffset(cyl);
  const a = ((crankAngle - offset) % 720 + 720) % 720;
  if (a < 180) return 'intake';
  if (a < 360) return 'compress';
  if (a < 540) return 'power';
  return 'exhaust';
}

// Which cylinder is currently firing (power stroke near TDC = ~360°)
function activeFiringCyl(crankAngle) {
  let best = null, bestDist = Infinity;
  for (const cyl of FIRING_ORDER) {
    const offset = getCylCrankOffset(cyl);
    const a = ((crankAngle - offset) % 720 + 720) % 720;
    // Firing happens at ~360° (start of power stroke, top dead center after compression)
    const dist = Math.min(Math.abs(a - 360), 720 - Math.abs(a - 360));
    if (dist < bestDist) { bestDist = dist; best = cyl; }
  }
  return bestDist < 45 ? best : null;
}

let fireFlash = {}; // cyl -> intensity 0-1
FIRING_ORDER.forEach(c => fireFlash[c] = 0);

function draw(crankAngle, activeCyl) {
  ctx.clearRect(0, 0, W, H);

  // Background
  ctx.fillStyle = '#0d0d12';
  ctx.fillRect(0, 0, W, H);

  // Engine block silhouette
  ctx.fillStyle = '#141420';
  ctx.fillRect(20, H*0.12, W-40, H*0.76);
  ctx.strokeStyle = '#252535';
  ctx.lineWidth = 1;
  ctx.strokeRect(20, H*0.12, W-40, H*0.76);

  // Crankshaft line
  ctx.beginPath();
  ctx.moveTo(30, H*0.5);
  ctx.lineTo(W-30, H*0.5);
  ctx.strokeStyle = '#333345';
  ctx.lineWidth = 4;
  ctx.stroke();

  // Draw crankshaft throws
  FIRING_ORDER.forEach((cyl, fi) => {
    const offset = getCylCrankOffset(cyl);
    const localA = ((crankAngle - offset) % 720 + 720) % 720;
    const throwAngle = (localA / 360) * Math.PI * 2;
    const config = CYL_CONFIGS.find(c => c.cyl === cyl);
    const cx = config.x;
    const throwR = 8;
    const jx = cx + Math.sin(throwAngle) * throwR;
    const jy = H*0.5 + Math.cos(throwAngle) * throwR;

    ctx.beginPath();
    ctx.arc(cx, H*0.5, 3, 0, Math.PI*2);
    ctx.fillStyle = '#445';
    ctx.fill();

    ctx.beginPath();
    ctx.arc(jx, jy, 4, 0, Math.PI*2);
    ctx.fillStyle = '#778';
    ctx.fill();
  });

  // Draw cylinders
  CYL_CONFIGS.forEach(({ cyl, bank, x, yBase, dir }) => {
    const pp = pistonPos(cyl, crankAngle);
    const phase = strokePhase(cyl, crankAngle);
    const flash = fireFlash[cyl];
    const isActive = cyl === activeCyl;

    const cylW = 60;
    const cylH = 110;
    const wallT = 6;

    // Cylinder bore position
    const boreTop = bank === 0 ? yBase - cylH : yBase - cylH;
    const boreX = x - cylW/2;

    // Phase colors
    const phaseColors = {
      intake: '#0a2a14', compress: '#0a1a2a',
      power: '#2a0800', exhaust: '#1a1a08'
    };
    const phaseBorder = {
      intake: '#004422', compress: '#002244',
      power: '#881100', exhaust: '#444400'
    };

    // Cylinder wall
    ctx.fillStyle = '#1a1a24';
    ctx.strokeStyle = phaseBorder[phase];
    ctx.lineWidth = isActive ? 2 : 1;
    ctx.beginPath();
    ctx.rect(boreX, boreTop, cylW, cylH);
    ctx.fill();
    ctx.stroke();

    // Inner bore fill (gas color)
    ctx.fillStyle = phaseColors[phase];
    ctx.fillRect(boreX + wallT, boreTop, cylW - wallT*2, cylH);

    // Fire flash
    if (flash > 0.01) {
      const grad = ctx.createRadialGradient(x, boreTop + 20, 2, x, boreTop + 20, cylW*0.8);
      grad.addColorStop(0, `rgba(255,200,50,${flash * 0.9})`);
      grad.addColorStop(0.4, `rgba(255,80,0,${flash * 0.6})`);
      grad.addColorStop(1, `rgba(255,0,0,0)`);
      ctx.fillStyle = grad;
      ctx.fillRect(boreX + wallT, boreTop, cylW - wallT*2, cylH * 0.6);
    }

    // Piston
    const pistonTravel = cylH * 0.55;
    const pistonY = bank === 0
      ? boreTop + cylH - wallT - 22 - (pistonTravel * (1 - pp))
      : boreTop + wallT + (pistonTravel * pp);
    const pistonH = 22;

    // Piston body
    const pistonGrad = ctx.createLinearGradient(boreX + wallT, 0, boreX + cylW - wallT, 0);
    if (isActive || flash > 0.1) {
      pistonGrad.addColorStop(0, '#883300');
      pistonGrad.addColorStop(0.5, '#ff5500');
      pistonGrad.addColorStop(1, '#883300');
    } else {
      pistonGrad.addColorStop(0, '#2a2a38');
      pistonGrad.addColorStop(0.5, '#4a4a60');
      pistonGrad.addColorStop(1, '#2a2a38');
    }
    ctx.fillStyle = pistonGrad;
    ctx.fillRect(boreX + wallT + 2, pistonY, cylW - wallT*2 - 4, pistonH);

    // Piston ring lines
    ctx.strokeStyle = isActive ? '#ff8844' : '#555568';
    ctx.lineWidth = 1;
    [5, 10, 15].forEach(ry => {
      ctx.beginPath();
      ctx.moveTo(boreX + wallT + 2, pistonY + ry);
      ctx.lineTo(boreX + cylW - wallT - 2, pistonY + ry);
      ctx.stroke();
    });

    // Connecting rod
    const crankY = H*0.5;
    const rodTopY = bank === 0 ? pistonY + pistonH : pistonY;
    ctx.beginPath();
    ctx.moveTo(x, rodTopY);
    ctx.lineTo(x, crankY);
    ctx.strokeStyle = isActive ? '#884422' : '#333344';
    ctx.lineWidth = 4;
    ctx.stroke();

    // Valve hint (top)
    if (bank === 0) {
      ctx.fillStyle = phase === 'intake' ? '#004422' : '#330000';
      ctx.fillRect(boreX + 10, boreTop - 4, 12, 6);
      ctx.fillStyle = phase === 'exhaust' ? '#445500' : '#330000';
      ctx.fillRect(boreX + cylW - 22, boreTop - 4, 12, 6);
    } else {
      ctx.fillStyle = phase === 'intake' ? '#004422' : '#330000';
      ctx.fillRect(boreX + 10, boreTop + cylH - 2, 12, 6);
      ctx.fillStyle = phase === 'exhaust' ? '#445500' : '#330000';
      ctx.fillRect(boreX + cylW - 22, boreTop + cylH - 2, 12, 6);
    }

    // Cylinder number label
    ctx.fillStyle = isActive ? '#ff8800' : '#444460';
    ctx.font = `bold 11px "Orbitron", monospace`;
    ctx.textAlign = 'center';
    ctx.fillText(cyl, x, bank === 0 ? boreTop - 10 : boreTop + cylH + 18);
  });

  // Bank labels
  ctx.font = '9px "Share Tech Mono", monospace';
  ctx.fillStyle = '#333355';
  ctx.textAlign = 'left';
  ctx.fillText('BANK A', 22, H*0.38 - 26);
  ctx.fillText('BANK B', 22, H*0.88 + 26);
}

// Update badges
function updateBadges(activeCyl) {
  FIRING_ORDER.forEach(c => {
    badges[c].className = 'cyl-badge' + (c === activeCyl ? ' active' : '');
  });
}

// Update stroke indicator
function updateStrokes(crankAngle) {
  const phases = {};
  CYL_CONFIGS.forEach(({cyl}) => {
    phases[strokePhase(cyl, crankAngle)] = true;
  });
  ['intake','compress','power','exhaust'].forEach(p => {
    const el = document.getElementById('sp-' + p);
    el.className = 'stroke-pill' + (phases[p] ? ` active-${p}` : '');
  });
}

// Animation loop
let prevActiveCyl = null;
function loop(timestamp) {
  if (!running) { lastTime = null; return; }
  if (!lastTime) lastTime = timestamp;
  const dt = Math.min((timestamp - lastTime) / 1000, 0.1);
  lastTime = timestamp;

  // Advance crank: rpm * 360°/min / 60s = rpm * 6 °/s, but 720° per cycle
  const degsPerSec = rpm * 6; // degrees per second (one revolution = 360°)
  crankAngle = (crankAngle + degsPerSec * dt) % 720;

  const activeCyl = activeFiringCyl(crankAngle);

  // Fire flash
  if (activeCyl && activeCyl !== prevActiveCyl) {
    fireFlash[activeCyl] = 1.0;
    totalFires++;
    lastFireCyl = activeCyl;
    prevActiveCyl = activeCyl;
  }

  // Decay flashes
  FIRING_ORDER.forEach(c => {
    fireFlash[c] = Math.max(0, fireFlash[c] - dt * 8);
  });

  draw(crankAngle, activeCyl);
  updateBadges(activeCyl);
  updateStrokes(crankAngle);

  // Stats
  document.getElementById('statFires').textContent = totalFires;
  const hz = ((rpm / 60) * 8 / 2).toFixed(1); // 8 cylinders, 4-stroke = fire every 2 revs
  document.getElementById('statHz').textContent = hz;
  document.getElementById('statCyl').textContent = activeCyl || '--';

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
</script>
</body>
</html>
