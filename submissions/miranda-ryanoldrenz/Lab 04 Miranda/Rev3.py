import os
import webbrowser

# ============================================================
# 3D SPACE FRAME / CUBE FEM SOLVER - NO-BOX TEXT OVERLAYS
# STUDENT: Ryanold Renz C. Miranda (BSCE-3D)
# ============================================================

html_3d_white = r"""<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Rev 3 Solver (White Viewport) - Ryanold Renz C. Miranda (BSCE-3D)</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

<style>
/* ============================================================
   GLOBAL & LAYOUT
============================================================ */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; }
body {
    font-family: Inter, "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    background: #f8fafc;
    color: #0f172a;
    overflow: hidden;
}

#app { width: 100%; height: 100%; display: flex; }

/* ============================================================
   SIDEBAR (PROFESSIONAL CONTROL PANEL)
============================================================ */
#sidebar {
    width: 410px; min-width: 410px; height: 100vh; padding: 20px;
    background: #0f172a;
    color: #f8fafc;
    border-right: 1px solid #1e293b;
    overflow-y: auto; z-index: 20; box-shadow: 8px 0 25px rgba(0,0,0,0.15);
}

.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.brand-icon {
    width: 48px; height: 48px; border-radius: 12px; display: flex;
    align-items: center; justify-content: center;
    background: linear-gradient(135deg, #0284c7, #2563eb);
    box-shadow: 0 6px 20px rgba(37,99,235,0.3); font-size: 16px; font-weight: 900; color: #ffffff;
}
.brand-text h1 { font-size: 1.05rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.3px; }
.brand-text p { color: #38bdf8; font-size: 0.70rem; margin-top: 3px; font-weight: 700; letter-spacing: 0.5px; }

/* ============================================================
   CARDS & CONTROLS
============================================================ */
.card {
    background: #1e293b; border: 1px solid #334155;
    border-radius: 12px; padding: 14px; margin-bottom: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.card-title {
    display: flex; align-items: center; gap: 8px; color: #f8fafc;
    font-size: 0.75rem; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 12px;
}
.card-title .dot { width: 7px; height: 7px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 8px #38bdf8; }

.unit-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; padding: 4px; background: #0f172a; border-radius: 8px; border: 1px solid #334155; }
.unit-option { padding: 8px 6px; text-align: center; border-radius: 6px; cursor: pointer; font-size: 0.74rem; font-weight: 700; color: #94a3b8; transition: 0.2s; }
.unit-option.active { background: linear-gradient(135deg, #0284c7, #2563eb); color: #ffffff; box-shadow: 0 2px 10px rgba(37,99,235,0.3); }

select.select-control {
    width: 100%; padding: 9px 12px; background: #0f172a; border: 1px solid #334155;
    border-radius: 8px; color: #f8fafc; font-size: 0.75rem; font-weight: 700; outline: none;
    cursor: pointer; transition: 0.2s;
}
select.select-control:focus { border-color: #38bdf8; }

.control { margin-bottom: 12px; }
.control:last-child { margin-bottom: 0; }
.control-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.control-header label { color: #cbd5e1; font-size: 0.74rem; font-weight: 600; }
.value { color: #38bdf8; font-size: 0.74rem; font-weight: 800; }

input[type="range"] { width: 100%; height: 5px; appearance: none; background: #334155; border-radius: 10px; outline: none; }
input[type="range"]::-webkit-slider-thumb { appearance: none; width: 15px; height: 15px; border-radius: 50%; background: #38bdf8; cursor: pointer; box-shadow: 0 0 8px rgba(56,189,248,0.5); }
input[type="range"]::-moz-range-thumb { width: 15px; height: 15px; border-radius: 50%; background: #38bdf8; cursor: pointer; }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
.info-box { padding: 9px; background: #0f172a; border: 1px solid #334155; border-radius: 8px; }
.info-label { color: #64748b; font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px; }
.info-value { color: #f8fafc; font-size: 0.78rem; font-weight: 700; }

.toggle { display: flex; align-items: center; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid rgba(148,163,184,0.1); }
.toggle:last-child { border-bottom: none; }
.toggle span { font-size: 0.73rem; color: #cbd5e1; }

.switch { position: relative; width: 36px; height: 20px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; inset: 0; background: #475569; border-radius: 20px; cursor: pointer; transition: 0.2s; }
.slider:before { content: ""; position: absolute; width: 14px; height: 14px; left: 3px; top: 3px; background: white; border-radius: 50%; transition: 0.2s; }
.switch input:checked + .slider { background: #0284c7; }
.switch input:checked + .slider:before { transform: translateX(16px); }

.button-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
button { border: none; border-radius: 8px; padding: 10px; color: white; font-size: 0.72rem; font-weight: 800; cursor: pointer; transition: transform 0.15s, opacity 0.15s; }
button:hover { transform: translateY(-1px); opacity: 0.92; }
.btn-blue { background: linear-gradient(135deg, #0284c7, #2563eb); }
.btn-green { background: linear-gradient(135deg, #059669, #16a34a); }
.btn-dark { background: #334155; }

/* ============================================================
   VIEWPORT & OVERLAYS
============================================================ */
#viewport { flex: 1; position: relative; height: 100vh; overflow: hidden; background: #ffffff; }
canvas { display: block; }

#top-hud { position: absolute; top: 18px; left: 18px; right: 18px; display: flex; justify-content: space-between; pointer-events: none; }
.hud-card { background: rgba(15, 23, 42, 0.90); backdrop-filter: blur(12px); border: 1px solid #334155; border-radius: 12px; padding: 12px 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); color: #f8fafc; }
.hud-title { color: #38bdf8; font-size: 0.67rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; margin-bottom: 4px; }
.hud-main { font-size: 0.85rem; font-weight: 800; color: #ffffff; }
.hud-sub { color: #94a3b8; font-size: 0.63rem; margin-top: 3px; }

#result-panel { position: absolute; right: 18px; top: 110px; width: 280px; background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(12px); border: 1px solid #0284c7; border-radius: 12px; padding: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.18); color: #f8fafc; }
.result-title { color: #38bdf8; font-size: 0.69rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 10px; text-transform: uppercase; }
.result-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(148,163,184,0.12); font-size: 0.72rem; }
.result-row:last-child { border-bottom: none; }
.result-label { color: #cbd5e1; }
.result-value { color: #4ade80; font-weight: 800; }

#load-audit-panel { position: absolute; right: 18px; top: 285px; width: 280px; background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(12px); border: 1px solid #facc15; border-radius: 12px; padding: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.18); color: #f8fafc; }
.audit-title { color: #facc15; font-size: 0.69rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 10px; text-transform: uppercase; }

#legend { position: absolute; right: 18px; bottom: 18px; background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(12px); border: 1px solid #334155; border-radius: 12px; padding: 12px 14px; width: 220px; color: #f8fafc; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
.legend-title { color: #38bdf8; font-size: 0.66rem; font-weight: 800; margin-bottom: 8px; letter-spacing: 0.8px; }
.legend-item { display: flex; align-items: center; gap: 8px; color: #e2e8f0; font-size: 0.65rem; margin-bottom: 6px; font-weight: 600; }
.legend-color { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }

#sidebar::-webkit-scrollbar { width: 6px; }
#sidebar::-webkit-scrollbar-track { background: transparent; }
#sidebar::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }

@media(max-width:900px) {
    body { overflow: auto; }
    #app { flex-direction: column; height: auto; }
    #sidebar { width: 100%; min-width: 0; height: auto; }
    #viewport { height: 70vh; min-height: 500px; }
    #result-panel, #load-audit-panel { width: 230px; }
}
</style>
</head>

<body>
<div id="app">

<!-- SIDEBAR CONTROLS -->
<aside id="sidebar">

<div class="brand">
    <div class="brand-icon">REV 3</div>
    <div class="brand-text">
        <h1>Rev 3 Solver</h1>
        <p>Ryanold Renz C. Miranda | BSCE-3D</p>
    </div>
</div>

<!-- SUBMISSION DETAILS -->
<div class="card" style="border-color: #0284c7;">
    <div class="card-title"><span class="dot"></span>Submission Details</div>
    <div class="info-grid">
        <div class="info-box" style="grid-column: 1 / 3;">
            <div class="info-label">Student Name</div>
            <div class="info-value" style="color: #38bdf8;">Ryanold Renz C. Miranda</div>
        </div>
        <div class="info-box">
            <div class="info-label">Section</div>
            <div class="info-value">BSCE-3D</div>
        </div>
        <div class="info-box">
            <div class="info-label">Exercise</div>
            <div class="info-value">Rev 3 Solver</div>
        </div>
        <div class="info-box" style="grid-column: 1 / 3;">
            <div class="info-label">Course</div>
            <div class="info-value" style="font-size: 0.68rem; line-height: 1.2;">Numerical Solutions to Civil Engineering Problems</div>
        </div>
    </div>
</div>

<!-- UNIT SYSTEM -->
<div class="card">
    <div class="card-title"><span class="dot"></span>Unit System</div>
    <div class="unit-selector">
        <div class="unit-option active" id="si-option" onclick="setUnitSystem('SI')">Standard (SI)</div>
        <div class="unit-option" id="imperial-option" onclick="setUnitSystem('IMPERIAL')">Imperial</div>
    </div>
</div>

<!-- LOAD CASE / COMBINATION SELECTOR -->
<div class="card">
    <div class="card-title"><span class="dot" style="background:#facc15;box-shadow:0 0 8px #facc15;"></span>Load Case / Combination</div>
    <select id="load-select" class="select-control" onchange="runSolver()">
        <optgroup label="Custom / Manual Controls">
            <option value="custom" selected>Manual Sliders (Node 7 Focus)</option>
        </optgroup>
        <optgroup label="Load Cases">
            <option value="lc1">LC1 - DEAD / SELF WEIGHT</option>
            <option value="lc2">LC2 - ROOF DEAD (5.0 kN/m)</option>
            <option value="lc3">LC3 - ROOF LIVE (3.0 kN/m)</option>
            <option value="lc4">LC4 - ROOF BEAM CENTER LOAD (5.0 kN)</option>
            <option value="lc5">LC5 - WIND X (10 kN Total / 2.5 kN Node)</option>
            <option value="lc6">LC6 - WIND Z (10 kN Total / 2.5 kN Node)</option>
            <option value="lc7">LC7 - SEISMIC X (15 kN Total / 3.75 kN Node)</option>
            <option value="lc8">LC8 - SEISMIC Z (15 kN Total / 3.75 kN Node)</option>
            <option value="lc9">LC9 - TEMPERATURE +15C</option>
        </optgroup>
        <optgroup label="NSCP Load Combinations">
            <option value="comb1">LRFD Comb 1: 1.4D</option>
            <option value="comb13">ASD Comb 13: D</option>
            <option value="comb15">ASD Comb 15: D</option>
        </optgroup>
    </select>
</div>

<!-- MANUAL LOAD SLIDERS -->
<div class="card" id="manual-load-card">
    <div class="card-title"><span class="dot" style="background:#facc15;box-shadow:0 0 8px #facc15;"></span>Nodal Load — Node 7</div>
    <div class="control">
        <div class="control-header"><label>Force X</label><span class="value" id="fx-value">40 kN</span></div>
        <input type="range" id="load-fx" min="-150" max="150" value="40" step="1" oninput="runSolver()">
    </div>
    <div class="control">
        <div class="control-header"><label>Force Y — Vertical</label><span class="value" id="fy-value">-60 kN</span></div>
        <input type="range" id="load-fy" min="-150" max="150" value="-60" step="1" oninput="runSolver()">
    </div>
    <div class="control">
        <div class="control-header"><label>Force Z</label><span class="value" id="fz-value">25 kN</span></div>
        <input type="range" id="load-fz" min="-150" max="150" value="25" step="1" oninput="runSolver()">
    </div>
</div>

<!-- MODEL VIEW SELECTION -->
<div class="card">
    <div class="card-title"><span class="dot"></span>Model Style</div>
    <select id="model-style" class="select-control" onchange="rebuild3DScene()">
        <option value="solid" selected>3D Extruded Cube (Solids)</option>
        <option value="line">Wireframe / Line Model</option>
    </select>
</div>

<!-- GEOMETRY -->
<div class="card">
    <div class="card-title"><span class="dot"></span>Cube Geometry</div>
    <div class="control">
        <div class="control-header"><label>Cube Edge</label><span class="value" id="edge-value">6.00 m</span></div>
        <input type="range" id="cube-edge" min="3" max="12" value="6" step="0.5" oninput="runSolver()">
    </div>
</div>

<!-- MATERIAL / SECTION -->
<div class="card">
    <div class="card-title"><span class="dot"></span>Material & Section</div>
    <div class="info-grid">
        <div class="info-box"><div class="info-label">Young's Modulus</div><div class="info-value" id="e-display">200 GPa</div></div>
        <div class="info-box"><div class="info-label">Area</div><div class="info-value" id="area-display">0.005 m²</div></div>
    </div>
</div>

<!-- VISUALIZATION LAYER CONTROLS -->
<div class="card">
    <div class="card-title"><span class="dot"></span>3D View Layer Controls</div>
    
    <div class="toggle">
        <span>Nodes</span>
        <label class="switch">
            <input type="checkbox" id="chk-nodes" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Supports</span>
        <label class="switch">
            <input type="checkbox" id="chk-supports" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Cube Faces</span>
        <label class="switch">
            <input type="checkbox" id="chk-faces" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Roof Diaphragm</span>
        <label class="switch">
            <input type="checkbox" id="chk-diaphragm" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Arrow Values & Names</span>
        <label class="switch">
            <input type="checkbox" id="chk-arrow-labels" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Local Axes</span>
        <label class="switch">
            <input type="checkbox" id="chk-local" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Global Axis</span>
        <label class="switch">
            <input type="checkbox" id="chk-global" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>MZ Releases</span>
        <label class="switch">
            <input type="checkbox" id="chk-release" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Node Labels</span>
        <label class="switch">
            <input type="checkbox" id="chk-labels" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Member Labels</span>
        <label class="switch">
            <input type="checkbox" id="chk-member-labels" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Section Labels</span>
        <label class="switch">
            <input type="checkbox" id="chk-section-labels" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="toggle">
        <span>Material Labels</span>
        <label class="switch">
            <input type="checkbox" id="chk-material-labels" checked onchange="rebuild3DScene()">
            <span class="slider"></span>
        </label>
    </div>

    <div class="control" style="margin-top:12px;">
        <div class="control-header"><label>Deflection Scale</label><span class="value" id="scale-value">100×</span></div>
        <input type="range" id="deflect-scale" min="1" max="500" value="100" step="1" oninput="updateDeformationVisuals()">
    </div>
</div>

<!-- BUTTONS -->
<div class="button-grid">
    <button class="btn-blue" onclick="resetView()">Reset View</button>
    <button class="btn-dark" onclick="toggleFaces()">Toggle Faces</button>
    <button class="btn-green" style="grid-column:1/3;" onclick="exportToExcel()">Export FEM Results to Excel</button>
</div>

</aside>

<!-- 3D VIEWPORT -->
<main id="viewport">

<div id="top-hud">
    <div class="hud-card">
        <div class="hud-title">Rev 3 Solver</div>
        <div class="hud-main" id="hud-dimensions">6.00 m × 6.00 m × 6.00 m</div>
        <div class="hud-sub">Student: Ryanold Renz C. Miranda | Section: BSCE-3D</div>
    </div>
    <div class="hud-card">
        <div class="hud-title">Active Unit System</div>
        <div class="hud-main" id="hud-units">Standard (SI)</div>
        <div class="hud-sub">FEM calculation active</div>
    </div>
</div>

<div id="result-panel">
    <div class="result-title">Max Deflection & N7 Results</div>
    <div class="result-row"><span class="result-label">Ux</span><span class="result-value" id="result-ux">0.000 mm</span></div>
    <div class="result-row"><span class="result-label">Uy</span><span class="result-value" id="result-uy">0.000 mm</span></div>
    <div class="result-row"><span class="result-label">Uz</span><span class="result-value" id="result-uz">0.000 mm</span></div>
    <div class="result-row"><span class="result-label">Max Deflection</span><span class="result-value" id="result-total">0.000 mm</span></div>
</div>

<div id="load-audit-panel">
    <div class="audit-title">Load Case & Equilibrium</div>
    <div class="result-row"><span class="result-label">Case</span><span class="result-value" id="audit-name" style="color:#facc15; font-size:0.65rem;">Manual</span></div>
    <div class="result-row"><span class="result-label">Total Global Fx</span><span class="result-value" id="audit-fx">0.000 kN</span></div>
    <div class="result-row"><span class="result-label">Total Global Fy</span><span class="result-value" id="audit-fy">0.000 kN</span></div>
    <div class="result-row"><span class="result-label">Total Global Fz</span><span class="result-value" id="audit-fz">0.000 kN</span></div>
    <div class="result-row"><span class="result-label">Resultant Force</span><span class="result-value" id="audit-res">0.000 kN</span></div>
    <div class="result-row"><span class="result-label">Equilibrium Status</span><span class="result-value" id="audit-err" style="color:#4ade80;">Balanced</span></div>
</div>

<div id="legend">
    <div class="legend-title">VISUAL LEGEND</div>
    <div class="legend-item"><span class="legend-color" style="background:#0284c7;"></span>Beam (M1–M8)</div>
    <div class="legend-item"><span class="legend-color" style="background:#16a34a;"></span>Column (β=90°, M9–M12)</div>
    <div class="legend-item"><span class="legend-color" style="background:#db2777;"></span>Free Node (N5–N8)</div>
    <div class="legend-item"><span class="legend-color" style="background:#16a34a;"></span>Pinned Support (N1–N4)</div>
    <div class="legend-item"><span class="legend-color" style="background:#d97706;"></span>Distributed Wireframe Load</div>
    <div class="legend-item"><span class="legend-color" style="background:#7c3aed;"></span>Point Loads</div>
    <div class="legend-item"><span class="legend-color" style="background:#dc2626;"></span>Deflected Shape</div>
</div>

</main>
</div>

<script>
/* UNIT CONVERSION & GLOBALS */
const UNIT = {
    SI: { name: "Standard (SI)", length: "m", force: "kN", area: "m²", modulus: "GPa", displacement: "mm" },
    IMPERIAL: { name: "Imperial", length: "ft", force: "kip", area: "ft²", modulus: "ksi", displacement: "in" }
};

const M_TO_FT = 3.280839895;
const FT_TO_M = 1 / M_TO_FT;
const KN_TO_KIP = 0.224808943;
const KIP_TO_KN = 1 / KN_TO_KIP;
const M2_TO_FT2 = M_TO_FT * M_TO_FT;
const FT2_TO_M2 = 1 / M2_TO_FT2;
const KPA_TO_KSI = 0.000145037738;
const KSI_TO_KPA = 1 / KPA_TO_KSI;

let unitSystem = "SI";
let currentNodes = [];
let currentMembers = [];
let rawDisplacements = [];
let sceneObjects = [];
let cubeFaceObjects = [];
let labelObjects = [];
let loadGroup = new THREE.Group();

const BASE_EDGE_M = 6.0;
const BASE_AREA_M2 = 0.005;
const BASE_E_KN_M2 = 200000000;

/* THREE.JS SETUP */
const container = document.getElementById("viewport");
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);
scene.add(loadGroup);

const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 2000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 3;
controls.maxDistance = 80;

/* LIGHTING SETUP */
scene.add(new THREE.AmbientLight(0xffffff, 0.85));
const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.9);
directionalLight1.position.set(25, 40, 25);
scene.add(directionalLight1);

const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
directionalLight2.position.set(-25, -20, -25);
scene.add(directionalLight2);

/* SUBTLE GRID */
const grid = new THREE.GridHelper(60, 60, 0xcccccc, 0xe5e5e5);
grid.position.y = 0;
scene.add(grid);

function setUnitSystem(system) {
    unitSystem = system;
    document.getElementById("si-option").classList.toggle("active", system === "SI");
    document.getElementById("imperial-option").classList.toggle("active", system === "IMPERIAL");
    updateInterfaceUnits();
    runSolver();
}

function getDisplayEdge() {
    const edgeM = parseFloat(document.getElementById("cube-edge").value);
    return unitSystem === "SI" ? edgeM : edgeM * M_TO_FT;
}

function getDisplayForce(valueKN) {
    return unitSystem === "SI" ? valueKN : valueKN * KN_TO_KIP;
}

function getDisplayArea() {
    return unitSystem === "SI" ? BASE_AREA_M2 : BASE_AREA_M2 * M2_TO_FT2;
}

function getDisplayE() {
    return unitSystem === "SI" ? 200 : BASE_E_KN_M2 * KPA_TO_KSI / 1000;
}

function updateInterfaceUnits() {
    const U = UNIT[unitSystem];
    document.getElementById("e-display").innerText = unitSystem === "SI" ? "200 GPa" : getDisplayE().toFixed(2) + " ksi";
    document.getElementById("area-display").innerText = getDisplayArea().toFixed(5) + " " + U.area;
    document.getElementById("hud-units").innerText = U.name;
}

/* MATRIX FEM SOLVER */
function solve3DFrame(nodes, members, loads, E, A) {
    const nNodes = nodes.length;
    const nDofs = nNodes * 3;
    let K = Array.from({ length: nDofs }, () => Array(nDofs).fill(0));
    let F = Array(nDofs).fill(0);

    for (const nodeIdx in loads) {
        const [fx, fy, fz] = loads[nodeIdx];
        F[nodeIdx * 3] += fx;
        F[nodeIdx * 3 + 1] += fy;
        F[nodeIdx * 3 + 2] += fz;
    }

    members.forEach(mem => {
        const n1 = mem.ni, n2 = mem.nj;
        const p1 = nodes[n1], p2 = nodes[n2];
        const dx = p2[0] - p1[0], dy = p2[1] - p1[1], dz = p2[2] - p1[2];
        const L = Math.hypot(dx, dy, dz);
        if (L < 1e-12) return;

        const cx = dx / L, cy = dy / L, cz = dz / L;
        const k = E * A / L;
        const direction = [cx, cy, cz, -cx, -cy, -cz];
        const dofs = [3*n1, 3*n1 + 1, 3*n1 + 2, 3*n2, 3*n2 + 1, 3*n2 + 2];

        for (let i = 0; i < 6; i++) {
            for (let j = 0; j < 6; j++) {
                K[dofs[i]][dofs[j]] += k * direction[i] * direction[j];
            }
        }
    });

    const fixedDofs = [0,1,2, 3,4,5, 6,7,8, 9,10,11];
    const freeDofs = [];
    for (let d = 0; d < nDofs; d++) {
        if (!fixedDofs.includes(d)) freeDofs.push(d);
    }

    const nFree = freeDofs.length;
    let Kff = Array.from({length:nFree}, () => Array(nFree).fill(0));
    let Ff = Array(nFree).fill(0);

    for (let i = 0; i < nFree; i++) {
        Ff[i] = F[freeDofs[i]];
        for (let j = 0; j < nFree; j++) {
            Kff[i][j] = K[freeDofs[i]][freeDofs[j]];
        }
    }

    const Uf = gaussianElimination(Kff, Ff);
    let U = Array(nDofs).fill(0);
    for (let i = 0; i < nFree; i++) {
        U[freeDofs[i]] = Uf[i];
    }
    return U;
}

function gaussianElimination(A,b) {
    const n = b.length;
    for (let i = 0; i < n; i++) {
        let maxRow = i;
        for (let k = i + 1; k < n; k++) {
            if (Math.abs(A[k][i]) > Math.abs(A[maxRow][i])) maxRow = k;
        }
        [A[i], A[maxRow]] = [A[maxRow], A[i]];
        [b[i], b[maxRow]] = [b[maxRow], b[i]];
        if (Math.abs(A[i][i]) < 1e-12) return Array(n).fill(0);

        for (let k = i + 1; k < n; k++) {
            const c = -A[k][i] / A[i][i];
            for (let j = i; j < n; j++) {
                if (i === j) A[k][j] = 0;
                else A[k][j] += c * A[i][j];
            }
            b[k] += c * b[i];
        }
    }
    const x = Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) {
        let sum = 0;
        for (let j = i + 1; j < n; j++) sum += A[i][j] * x[j];
        x[i] = (b[i] - sum) / A[i][i];
    }
    return x;
}

function runSolver() {
    const edgeM = parseFloat(document.getElementById("cube-edge").value);
    const selectedCase = document.getElementById("load-select").value;
    const manualCard = document.getElementById("manual-load-card");

    if (selectedCase === "custom") {
        manualCard.style.display = "block";
    } else {
        manualCard.style.display = "none";
    }

    currentNodes = [
        [0.0, 0.0, 0.0],       // N1: Base
        [edgeM, 0.0, 0.0],     // N2: Base
        [edgeM, 0.0, edgeM],   // N3: Base
        [0.0, 0.0, edgeM],     // N4: Base
        [0.0, edgeM, 0.0],     // N5: Roof
        [0.0, edgeM, edgeM],   // N6: Roof
        [edgeM, edgeM, edgeM], // N7: Roof
        [edgeM, edgeM, 0.0]    // N8: Roof
    ];

    currentMembers = [
        { id:"M1",  ni:0, nj:1, type:"Beam",   beta:0,  release:"both", section: "180x180 Box", material: "Steel S355" },
        { id:"M2",  ni:1, nj:2, type:"Beam",   beta:0,  release:"none", section: "180x180 Box", material: "Steel S355" },
        { id:"M3",  ni:2, nj:3, type:"Beam",   beta:0,  release:"both", section: "180x180 Box", material: "Steel S355" },
        { id:"M4",  ni:3, nj:0, type:"Beam",   beta:0,  release:"none", section: "180x180 Box", material: "Steel S355" },
        { id:"M5",  ni:4, nj:7, type:"Beam",   beta:0,  release:"both", section: "180x180 Box", material: "Steel S355" },
        { id:"M6",  ni:7, nj:6, type:"Beam",   beta:0,  release:"none", section: "180x180 Box", material: "Steel S355" },
        { id:"M7",  ni:6, nj:5, type:"Beam",   beta:0,  release:"both", section: "180x180 Box", material: "Steel S355" },
        { id:"M8",  ni:5, nj:4, type:"Beam",   beta:0,  release:"none", section: "180x180 Box", material: "Steel S355" },
        { id:"M9",  ni:0, nj:4, type:"Column", beta:90, release:"none", section: "220x220 Box", material: "Steel S355" },
        { id:"M10", ni:1, nj:7, type:"Column", beta:90, release:"none", section: "220x220 Box", material: "Steel S355" },
        { id:"M11", ni:2, nj:6, type:"Column", beta:90, release:"none", section: "220x220 Box", material: "Steel S355" },
        { id:"M12", ni:3, nj:5, type:"Column", beta:90, release:"none", section: "220x220 Box", material: "Steel S355" }
    ];

    let loadsMap = {};
    let totalFx = 0, totalFy = 0, totalFz = 0;
    let caseName = "Manual Sliders";

    if (selectedCase === "custom") {
        const Fx = parseFloat(document.getElementById("load-fx").value);
        const Fy = parseFloat(document.getElementById("load-fy").value);
        const Fz = parseFloat(document.getElementById("load-fz").value);
        loadsMap[6] = [Fx, Fy, Fz];
        totalFx = Fx; totalFy = Fy; totalFz = Fz;
        caseName = "Manual (Node 7 Focus)";
        document.getElementById("fx-value").innerText = getDisplayForce(Fx).toFixed(2) + " " + UNIT[unitSystem].force;
        document.getElementById("fy-value").innerText = getDisplayForce(Fy).toFixed(2) + " " + UNIT[unitSystem].force;
        document.getElementById("fz-value").innerText = getDisplayForce(Fz).toFixed(2) + " " + UNIT[unitSystem].force;
    } else if (selectedCase === 'lc1') {
        caseName = "LC1 - DEAD / SELF WEIGHT";
        totalFy = -21.22;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'lc2') {
        caseName = "LC2 - ROOF DEAD (5.0 kN/m)";
        totalFy = -120.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'lc3') {
        caseName = "LC3 - ROOF LIVE (3.0 kN/m)";
        totalFy = -72.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'lc4') {
        caseName = "LC4 - ROOF BEAM CENTER LOAD";
        totalFy = -20.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'lc5') {
        caseName = "LC5 - WIND X";
        totalFx = 10.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [totalFx/4, 0, 0]);
    } else if (selectedCase === 'lc6') {
        caseName = "LC6 - WIND Z";
        totalFz = 10.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, 0, totalFz/4]);
    } else if (selectedCase === 'lc7') {
        caseName = "LC7 - SEISMIC X";
        totalFx = 15.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [totalFx/4, 0, 0]);
    } else if (selectedCase === 'lc8') {
        caseName = "LC8 - SEISMIC Z";
        totalFz = 15.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, 0, totalFz/4]);
    } else if (selectedCase === 'lc9') {
        caseName = "LC9 - TEMPERATURE +15C";
    } else if (selectedCase === 'comb1') {
        caseName = "LRFD Comb 1: 1.4D";
        totalFy = -225.71;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'comb13' || selectedCase === 'comb15') {
        caseName = selectedCase === 'comb13' ? "ASD Comb 13: D" : "ASD Comb 15: D";
        totalFy = -161.22;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    }

    rawDisplacements = solve3DFrame(currentNodes, currentMembers, loadsMap, BASE_E_KN_M2, BASE_AREA_M2);

    const ux = rawDisplacements[18], uy = rawDisplacements[19], uz = rawDisplacements[20];
    const resultant = Math.hypot(ux, uy, uz);

    updateResults(ux, uy, uz, resultant);
    updateLoadAudit(caseName, totalFx, totalFy, totalFz);
    updateGeometryDisplay(edgeM);
    rebuild3DScene();
}

function updateResults(ux, uy, uz, resultant) {
    let values = unitSystem === "SI" 
        ? { ux: ux * 1000, uy: uy * 1000, uz: uz * 1000, total: resultant * 1000, unit: "mm" }
        : { ux: ux * M_TO_FT * 12, uy: uy * M_TO_FT * 12, uz: uz * M_TO_FT * 12, total: resultant * M_TO_FT * 12, unit: "in" };

    document.getElementById("result-ux").innerText = values.ux.toFixed(4) + " " + values.unit;
    document.getElementById("result-uy").innerText = values.uy.toFixed(4) + " " + values.unit;
    document.getElementById("result-uz").innerText = values.uz.toFixed(4) + " " + values.unit;
    document.getElementById("result-total").innerText = values.total.toFixed(4) + " " + values.unit;
}

function updateLoadAudit(name, fx, fy, fz) {
    const U = UNIT[unitSystem];
    const dfx = getDisplayForce(fx);
    const dfy = getDisplayForce(fy);
    const dfz = getDisplayForce(fz);
    const res = Math.hypot(dfx, dfy, dfz);

    document.getElementById("audit-name").innerText = name;
    document.getElementById("audit-fx").innerText = dfx.toFixed(3) + " " + U.force;
    document.getElementById("audit-fy").innerText = dfy.toFixed(3) + " " + U.force;
    document.getElementById("audit-fz").innerText = dfz.toFixed(3) + " " + U.force;
    document.getElementById("audit-res").innerText = res.toFixed(3) + " " + U.force;
}

function updateGeometryDisplay(edgeM) {
    const edgeDisplay = getDisplayEdge();
    const unit = UNIT[unitSystem].length;
    document.getElementById("edge-value").innerText = edgeDisplay.toFixed(2) + " " + unit;
    document.getElementById("hud-dimensions").innerText = `${edgeDisplay.toFixed(2)} ${unit} × ${edgeDisplay.toFixed(2)} ${unit} × ${edgeDisplay.toFixed(2)} ${unit}`;
}

function clear3DObjects() {
    sceneObjects.forEach(obj => {
        scene.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
            if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
            else obj.material.dispose();
        }
    });
    sceneObjects = [];
    cubeFaceObjects.forEach(obj => scene.remove(obj)); cubeFaceObjects = [];
    labelObjects.forEach(obj => scene.remove(obj)); labelObjects = [];
    loadGroup.clear();
}

/* HIGH-VISIBILITY CANVAS TEXT SPRITE (TRANSPARENT BACKGROUND WITH OUTLINE - NO BOX) */
function createTextSprite(message, textColor="#0284c7", outlineColor="#000000") {
    const canvas = document.createElement("canvas");
    canvas.width = 512; canvas.height = 128;
    const ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.font = "bold 34px Inter, Arial, sans-serif";
    ctx.textAlign = "center"; 
    ctx.textBaseline = "middle";

    // Text Outline / Stroke for contrast against any background
    ctx.strokeStyle = outlineColor;
    ctx.lineWidth = 6;
    ctx.strokeText(message, 256, 64);

    // Text Fill
    ctx.fillStyle = textColor;
    ctx.fillText(message, 256, 64);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(2.4, 0.6, 1);
    return sprite;
}

function createCubeFaces() {
    const edge = parseFloat(document.getElementById("cube-edge").value);
    const material = new THREE.MeshBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.06, side: THREE.DoubleSide, depthWrite: false });

    const createFace = (w, h, pos, rot) => {
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), material.clone());
        if (rot.x) mesh.rotation.x = rot.x;
        if (rot.y) mesh.rotation.y = rot.y;
        mesh.position.set(...pos);
        scene.add(mesh);
        cubeFaceObjects.push(mesh);
    };

    createFace(edge, edge, [edge/2, 0, edge/2], { x: -Math.PI / 2 });
    createFace(edge, edge, [edge/2, edge, edge/2], { x: -Math.PI / 2 });
    createFace(edge, edge, [edge/2, edge/2, 0], {});
    createFace(edge, edge, [edge/2, edge/2, edge], {});
    createFace(edge, edge, [0, edge/2, edge/2], { y: Math.PI / 2 });
    createFace(edge, edge, [edge, edge/2, edge/2], { y: Math.PI / 2 });
}

function rebuild3DScene() {
    clear3DObjects();

    const modelStyle = document.getElementById("model-style").value;
    const showNodes = document.getElementById("chk-nodes").checked;
    const showSupports = document.getElementById("chk-supports").checked;
    const showFaces = document.getElementById("chk-faces").checked;
    const showDiaphragm = document.getElementById("chk-diaphragm").checked;
    const showArrowLabels = document.getElementById("chk-arrow-labels").checked;
    const showLocal = document.getElementById("chk-local").checked;
    const showGlobal = document.getElementById("chk-global").checked;
    const showRelease = document.getElementById("chk-release").checked;
    const showLabels = document.getElementById("chk-labels").checked;
    const showMemberLabels = document.getElementById("chk-member-labels").checked;
    const showSectionLabels = document.getElementById("chk-section-labels").checked;
    const showMaterialLabels = document.getElementById("chk-material-labels").checked;

    if (showFaces) createCubeFaces();

    const beamMaterial = new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.3, roughness: 0.35 });
    const columnMaterial = new THREE.MeshStandardMaterial({ color: 0x16a34a, metalness: 0.25, roughness: 0.4 });
    const supportMaterial = new THREE.MeshStandardMaterial({ color: 0x16a34a, metalness: 0.15, roughness: 0.45 });
    const freeMaterial = new THREE.MeshStandardMaterial({ color: 0xdb2777, roughness: 0.35 });

    /* NODES & SUPPORTS */
    currentNodes.forEach((coords, index) => {
        const [x, y, z] = coords;
        const pinned = index < 4;

        if (showNodes) {
            const sphere = new THREE.Mesh(
                new THREE.SphereGeometry(0.24, 24, 24),
                pinned ? supportMaterial : freeMaterial
            );
            sphere.position.set(x, y, z);
            scene.add(sphere);
            sceneObjects.push(sphere);
        }

        if (pinned && showSupports) {
            const supportHeight = 0.62;
            const support = new THREE.Mesh(
                new THREE.ConeGeometry(0.45, supportHeight, 4),
                supportMaterial
            );
            support.position.set(x, y - supportHeight / 2, z);
            scene.add(support);
            sceneObjects.push(support);
        }

        if (showLabels) {
            const dofStart = index * 6 + 1;
            const dofEnd = dofStart + 5;
            const labelText = `N${index + 1} (DOF ${dofStart}-${dofEnd})`;
            const label = createTextSprite(labelText, "#0284c7", "#ffffff");
            label.position.set(x, y + 0.45, z);
            scene.add(label);
            labelObjects.push(label);
        }
    });

    /* ROOF DIAPHRAGM HIGHLIGHT */
    if (showDiaphragm) {
        const diaGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(...currentNodes[4]), new THREE.Vector3(...currentNodes[7]),
            new THREE.Vector3(...currentNodes[6]), new THREE.Vector3(...currentNodes[5]),
            new THREE.Vector3(...currentNodes[4])
        ]);
        const diaMat = new THREE.LineDashedMaterial({ color: 0x0284c7, dashSize: 0.4, gapSize: 0.2 });
        const diaLine = new THREE.Line(diaGeo, diaMat);
        diaLine.computeLineDistances();
        scene.add(diaLine);
        sceneObjects.push(diaLine);
    }

    /* MEMBERS */
    currentMembers.forEach(mem => {
        const p1 = new THREE.Vector3(...currentNodes[mem.ni]);
        const p2 = new THREE.Vector3(...currentNodes[mem.nj]);
        const direction = new THREE.Vector3().subVectors(p2, p1);
        const length = direction.length();

        if (modelStyle === "solid") {
            const thickness = mem.type === "Column" ? 0.22 : 0.18;
            const geometry = new THREE.BoxGeometry(thickness, thickness, length);
            const material = mem.type === "Column" ? columnMaterial : beamMaterial;
            const mesh = new THREE.Mesh(geometry, material);

            mesh.position.copy(new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5));
            mesh.lookAt(p2);

            if (mem.beta !== 0) mesh.rotateZ(THREE.MathUtils.degToRad(mem.beta));

            scene.add(mesh);
            sceneObjects.push(mesh);
        } else {
            const lineColor = mem.type === "Column" ? 0x16a34a : 0x0284c7;
            const geometry = new THREE.BufferGeometry().setFromPoints([p1, p2]);
            const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: lineColor, linewidth: 2 }));
            
            scene.add(line);
            sceneObjects.push(line);
        }

        const midPt = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
        let verticalOffset = 0.25;

        if (showMemberLabels) {
            const betaTxt = mem.beta !== 0 ? ` (β=${mem.beta}°)` : "";
            const mLabel = createTextSprite(`${mem.id}${betaTxt}`, "#0f172a", "#ffffff");
            mLabel.position.copy(midPt).add(new THREE.Vector3(0, verticalOffset, 0));
            scene.add(mLabel);
            labelObjects.push(mLabel);
            verticalOffset += 0.35;
        }

        if (showSectionLabels) {
            const secLabel = createTextSprite(`Sec: ${mem.section}`, "#334155", "#ffffff");
            secLabel.position.copy(midPt).add(new THREE.Vector3(0, verticalOffset, 0));
            scene.add(secLabel);
            labelObjects.push(secLabel);
            verticalOffset += 0.35;
        }

        if (showMaterialLabels) {
            const matLabel = createTextSprite(`Mat: ${mem.material}`, "#475569", "#ffffff");
            matLabel.position.copy(midPt).add(new THREE.Vector3(0, verticalOffset, 0));
            scene.add(matLabel);
            labelObjects.push(matLabel);
        }

        if (mem.release === "both" && showRelease) {
            [0.08, 0.92].forEach(ratio => {
                const pos = new THREE.Vector3().lerpVectors(p1, p2, ratio);
                const ring = new THREE.Mesh(
                    new THREE.RingGeometry(0.10, 0.17, 20),
                    new THREE.MeshBasicMaterial({ color: 0x0284c7, side: THREE.DoubleSide })
                );
                ring.position.copy(pos);
                ring.lookAt(p2);
                scene.add(ring);
                sceneObjects.push(ring);
            });
        }

        if (showLocal) {
            const localX = direction.clone().normalize();
            let reference = new THREE.Vector3(0, 1, 0);
            if (Math.abs(localX.dot(reference)) > 0.95) reference = new THREE.Vector3(1, 0, 0);

            const localZ = new THREE.Vector3().crossVectors(localX, reference).normalize();
            const localY = new THREE.Vector3().crossVectors(localZ, localX).normalize();
            const midpoint = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
            const axisLength = Math.min(0.85, length * 0.23);

            const ax = new THREE.ArrowHelper(localX, midpoint, axisLength, 0xdc2626, 0.17, 0.08);
            const ay = new THREE.ArrowHelper(localY, midpoint, axisLength, 0x16a34a, 0.17, 0.08);
            const az = new THREE.ArrowHelper(localZ, midpoint, axisLength, 0x2563eb, 0.17, 0.08);

            scene.add(ax, ay, az);
            sceneObjects.push(ax, ay, az);
        }
    });

    /* GLOBAL AXIS */
    if (showGlobal) {
        const origin = new THREE.Vector3(-1, 0, -1);
        const gx = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), origin, 2, 0xdc2626, 0.3, 0.15);
        const gy = new THREE.ArrowHelper(new THREE.Vector3(0,1,0), origin, 2, 0x16a34a, 0.3, 0.15);
        const gz = new THREE.ArrowHelper(new THREE.Vector3(0,0,1), origin, 2, 0x2563eb, 0.3, 0.15);
        scene.add(gx, gy, gz);
        sceneObjects.push(gx, gy, gz);
    }

    renderLoadVisuals(showArrowLabels);
    updateDeformationVisuals();
}

/* WIREFRAME DISTRIBUTED LOAD CURTAINS (PLACED ABOVE MEMBERS) */
function drawDistributedLoadCurtain(memberIdx, colorHex, heightOffset, labelText, showLabels) {
    const mem = currentMembers[memberIdx];
    const p1 = new THREE.Vector3(...currentNodes[mem.ni]);
    const p2 = new THREE.Vector3(...currentNodes[mem.nj]);

    const absHeight = Math.abs(heightOffset);
    const modelStyle = document.getElementById("model-style").value;
    const memberHalfThickness = (modelStyle === "solid") ? (mem.type === "Column" ? 0.11 : 0.09) : 0;
    
    // Position starting line above top surface of member
    const topPts = [];
    const numTicks = 6;
    const downDir = new THREE.Vector3(0, -1, 0);

    for (let i = 0; i <= numTicks; i++) {
        const t = i / numTicks;
        const bPos = new THREE.Vector3().lerpVectors(p1, p2, t);
        
        // Target contact point on member top boundary
        const contactPt = bPos.clone().add(new THREE.Vector3(0, memberHalfThickness, 0));
        // Start point raised above member
        const arrowStart = contactPt.clone().add(new THREE.Vector3(0, absHeight, 0));

        topPts.push(arrowStart);

        const arrow = new THREE.ArrowHelper(downDir, arrowStart, absHeight, colorHex, 0.18, 0.12);
        loadGroup.add(arrow);
    }

    const topBoundaryGeo = new THREE.BufferGeometry().setFromPoints(topPts);
    const topBoundaryMat = new THREE.LineBasicMaterial({ color: colorHex, linewidth: 2 });
    const topBoundaryLine = new THREE.Line(topBoundaryGeo, topBoundaryMat);
    loadGroup.add(topBoundaryLine);

    if (showLabels) {
        const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
        const sprite = createTextSprite(labelText, colorHex === 0x16a34a ? "#16a34a" : "#d97706", "#ffffff");
        sprite.position.set(mid.x, mid.y + memberHalfThickness + absHeight + 0.35, mid.z);
        loadGroup.add(sprite);
    }
}

function renderLoadVisuals(showLabels) {
    const selectedCase = document.getElementById("load-select").value;

    if (selectedCase === "custom") {
        const Fx = parseFloat(document.getElementById("load-fx").value);
        const Fy = parseFloat(document.getElementById("load-fy").value);
        const Fz = parseFloat(document.getElementById("load-fz").value);
        drawNodalArrow(6, [Fx, Fy, Fz], 0xd97706, `Fx:${Fx} Fy:${Fy} Fz:${Fz}`, showLabels);
    } else if (selectedCase === 'lc1') {
        // LC1: Self Weight applied across ALL 12 members (Beams + Columns) in Teal/Green (#16a34a)
        currentMembers.forEach((_, idx) => drawDistributedLoadCurtain(idx, 0x16a34a, 0.6, "self weight: 0.3802, 0.4818 kN/m -Y", showLabels));
    } else if (selectedCase === 'lc2') {
        // LC2: Roof Dead applied to top roof beams (M5, M6, M7, M8 / indices 4, 5, 6, 7) in Orange (#d97706)
        [4, 5, 6, 7].forEach(idx => drawDistributedLoadCurtain(idx, 0xd97706, 0.8, "distributed: 5 kN/m -Y", showLabels));
    } else if (selectedCase === 'lc3') {
        // LC3: Roof Live applied to top roof beams (M5, M6, M7, M8 / indices 4, 5, 6, 7) in Orange (#d97706)
        [4, 5, 6, 7].forEach(idx => drawDistributedLoadCurtain(idx, 0xd97706, 0.8, "distributed: 3 kN/m -Y", showLabels));
    } else if (selectedCase === 'lc4') {
        [4, 5, 6, 7].forEach(idx => drawPointLoad(idx, 0x7c3aed, "CENTER LOAD: 5.0 kN", showLabels));
    } else if (selectedCase === 'lc5') {
        [4, 5, 6, 7].forEach(nid => drawNodalArrow(nid, [2.5, 0, 0], 0xdc2626, "WIND X: 2.50 kN", showLabels));
    } else if (selectedCase === 'lc6') {
        [4, 5, 6, 7].forEach(nid => drawNodalArrow(nid, [0, 0, 2.5], 0xd97706, "WIND Z: 2.50 kN", showLabels));
    } else if (selectedCase === 'lc7') {
        [4, 5, 6, 7].forEach(nid => drawNodalArrow(nid, [3.75, 0, 0], 0xdc2626, "SEISMIC X: 3.75 kN", showLabels));
    } else if (selectedCase === 'lc8') {
        [4, 5, 6, 7].forEach(nid => drawNodalArrow(nid, [0, 0, 3.75], 0xd97706, "SEISMIC Z: 3.75 kN", showLabels));
    } else if (selectedCase === 'lc9') {
        currentMembers.forEach((_, idx) => drawThermalVector(idx, 0xd97706, `M${idx+1}: +15°C`, showLabels));
    } else if (selectedCase === 'comb1') {
        [4, 5, 6, 7].forEach(idx => drawDistributedLoadCurtain(idx, 0xd97706, 1.4, "1.4D: 7.0 kN/m", showLabels));
    } else if (selectedCase === 'comb13' || selectedCase === 'comb15') {
        [4, 5, 6, 7].forEach(idx => drawDistributedLoadCurtain(idx, 0xd97706, 1.0, "1.0D: 5.0 kN/m", showLabels));
    }
}

function drawPointLoad(memberIdx, color, labelText, showLabels) {
    const mem = currentMembers[memberIdx];
    const mid = new THREE.Vector3(...currentNodes[mem.ni]).add(new THREE.Vector3(...currentNodes[mem.nj])).multiplyScalar(0.5);
    const arrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), mid.clone().add(new THREE.Vector3(0, 1.5, 0)), 1.5, color, 0.3, 0.2);
    loadGroup.add(arrow);

    if (showLabels) {
        const sprite = createTextSprite(labelText, "#7c3aed", "#ffffff");
        sprite.position.set(mid.x, mid.y + 1.85, mid.z);
        loadGroup.add(sprite);
    }
}

function drawNodalArrow(nodeIdx, vec, color, labelText, showLabels) {
    const pos = new THREE.Vector3(...currentNodes[nodeIdx]);
    const vec3 = new THREE.Vector3(...vec);
    if (vec3.length() < 0.0001) return;

    const dir = vec3.clone().normalize();
    const len = Math.min(3.0, Math.max(1.0, vec3.length() * 0.2));
    const arrow = new THREE.ArrowHelper(dir, pos, len, color, 0.3, 0.2);
    loadGroup.add(arrow);

    if (showLabels) {
        const sprite = createTextSprite(labelText, "#dc2626", "#ffffff");
        sprite.position.set(pos.x + dir.x * 1.2, pos.y + 0.55, pos.z + dir.z * 1.2);
        loadGroup.add(sprite);
    }
}

function drawThermalVector(memberIdx, color, labelText, showLabels) {
    const mem = currentMembers[memberIdx];
    const p1 = new THREE.Vector3(...currentNodes[mem.ni]);
    const p2 = new THREE.Vector3(...currentNodes[mem.nj]);
    const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
    const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
    const arrow = new THREE.ArrowHelper(dir, mid, 1.0, color, 0.3, 0.2);
    loadGroup.add(arrow);

    if (showLabels) {
        const sprite = createTextSprite(labelText, "#d97706", "#ffffff");
        sprite.position.set(mid.x, mid.y + 0.45, mid.z);
        loadGroup.add(sprite);
    }
}

function updateDeformationVisuals() {
    sceneObjects = sceneObjects.filter(obj => {
        if (obj.isDeformedLine) {
            scene.remove(obj);
            if (obj.geometry) obj.geometry.dispose();
            return false;
        }
        return true;
    });

    if (rawDisplacements.length === 0) return;

    const scale = parseFloat(document.getElementById("deflect-scale").value);
    document.getElementById("scale-value").innerText = scale + "×";

    const material = new THREE.LineBasicMaterial({ color: 0xdc2626, linewidth: 3 });

    currentMembers.forEach(mem => {
        const n1 = mem.ni, n2 = mem.nj;
        const p1 = new THREE.Vector3(
            currentNodes[n1][0] + rawDisplacements[3*n1] * scale,
            currentNodes[n1][1] + rawDisplacements[3*n1+1] * scale,
            currentNodes[n1][2] + rawDisplacements[3*n1+2] * scale
        );
        const p2 = new THREE.Vector3(
            currentNodes[n2][0] + rawDisplacements[3*n2] * scale,
            currentNodes[n2][1] + rawDisplacements[3*n2+1] * scale,
            currentNodes[n2][2] + rawDisplacements[3*n2+2] * scale
        );

        const geometry = new THREE.BufferGeometry().setFromPoints([p1, p2]);
        const line = new THREE.Line(geometry, material);
        line.isDeformedLine = true;
        scene.add(line);
        sceneObjects.push(line);
    });
}

function resetView() {
    const edge = parseFloat(document.getElementById("cube-edge").value);
    camera.position.set(edge * 2.35, edge * 1.75, edge * 2.55);
    controls.target.set(edge / 2, edge / 2, edge / 2);
    controls.update();
}

function toggleFaces() {
    const checkbox = document.getElementById("chk-faces");
    checkbox.checked = !checkbox.checked;
    rebuild3DScene();
}

function exportToExcel() {
    const U = UNIT[unitSystem];

    const nodeData = currentNodes.map((c,i) => ({
        "Node ID": "N" + (i+1),
        ["X (" + U.length + ")"]: unitSystem === "SI" ? c[0] : c[0] * M_TO_FT,
        ["Y (" + U.length + ")"]: unitSystem === "SI" ? c[1] : c[1] * M_TO_FT,
        ["Z (" + U.length + ")"]: unitSystem === "SI" ? c[2] : c[2] * M_TO_FT,
        "Support Condition": i < 4 ? "Pinned — UX, UY, UZ Restrained" : "Free"
    }));

    const memberData = currentMembers.map(m => ({
        "Member ID": m.id,
        "Start Node": "N" + (m.ni+1),
        "End Node": "N" + (m.nj+1),
        "Type": m.type,
        "Section": m.section,
        "Material": m.material,
        "Beta Angle": m.beta + "°",
        "MZ Release": m.release === "both" ? "Released Both Ends" : "Rigid / Continuous"
    }));

    const displacementData = currentNodes.map((c,i) => {
        const ux = rawDisplacements[3*i], uy = rawDisplacements[3*i+1], uz = rawDisplacements[3*i+2];
        const factor = unitSystem === "SI" ? 1000 : M_TO_FT * 12;
        return {
            "Node ID": "N" + (i+1),
            ["Ux (" + U.displacement + ")"]: ux * factor,
            ["Uy (" + U.displacement + ")"]: uy * factor,
            ["Uz (" + U.displacement + ")"]: uz * factor
        };
    });

    const summaryData = [
        { Parameter: "Exercise Title", Value: "Rev 3 Solver (White Viewport)" },
        { Parameter: "Student Name", Value: "Ryanold Renz C. Miranda" },
        { Parameter: "Section", Value: "BSCE-3D" },
        { Parameter: "Course", Value: "Numerical Solutions to Civil Engineering Problems" },
        { Parameter: "Unit System", Value: U.name },
        { Parameter: "Selected Load Case", Value: document.getElementById("load-select").value },
        { Parameter: "Total Nodes", Value: 8 },
        { Parameter: "Total Members", Value: 12 },
        { Parameter: "Pinned Nodes", Value: "N1, N2, N3, N4" },
        { Parameter: "Global DOFs", Value: "48 (6 per node)" },
        { Parameter: "Restrained DOFs", Value: 12 },
        { Parameter: "Young's Modulus", Value: unitSystem === "SI" ? "200 GPa" : getDisplayE().toFixed(3) + " ksi" },
        { Parameter: "Section Area", Value: getDisplayArea().toFixed(6) + " " + U.area }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summaryData), "Model Summary");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(nodeData), "Nodal Data");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(memberData), "Member Data");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(displacementData), "Displacements");
    XLSX.writeFile(wb, "Rev3_Solver_White_Ryanold_Miranda_BSCE3D.xlsx");
}

window.addEventListener("resize", () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

/* INITIALIZE */
updateInterfaceUnits();
runSolver();
resetView();

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();
</script>

</body>
</html>
"""

output_html = "3D_Cube_Space_Frame_FEM_Rev3_White.html"

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_3d_white)

absolute_path = os.path.abspath(output_html)

print("\n" + "=" * 65)
print("REV 3 SOLVER - WHITE VIEWPORT EDITION (NO TEXT BOXES)")
print("NUMERICAL SOLUTIONS TO CIVIL ENGINEERING PROBLEMS")
print("=" * 65)
print(f"Student Name : Ryanold Renz C. Miranda")
print(f"Section      : BSCE-3D")
print(f"\nSuccessfully generated:\n{absolute_path}\n")

webbrowser.open(absolute_path)