import os
import webbrowser

# ============================================================
# 3D SPACE FRAME / CUBE FEM SOLVER
# REVISION 3 - SOLVER DEVELOPMENT EXERCISE
# STUDENT: Ryanold Renz C. Miranda (BSCE-3D)
# ============================================================

html_3d_rev3 = r"""<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Rev 3 Solver Development Exercise - Ryanold Renz C. Miranda (BSCE-3D)</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

<style>
/* ============================================================
   GLOBAL
============================================================ */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; }
body {
    font-family: Inter, "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    background: radial-gradient(circle at 70% 20%, #172554 0%, #0f172a 40%, #020617 100%);
    color: #f8fafc;
    overflow: hidden;
}

/* ============================================================
   APP & SIDEBAR
============================================================ */
#app { width: 100%; height: 100%; display: flex; }
#sidebar {
    width: 410px; min-width: 410px; height: 100vh; padding: 20px;
    background: linear-gradient(180deg, rgba(15,23,42,0.98), rgba(2,6,23,0.98));
    border-right: 1px solid rgba(148,163,184,0.16);
    overflow-y: auto; z-index: 20; box-shadow: 10px 0 35px rgba(0,0,0,0.35);
}

.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.brand-icon {
    width: 48px; height: 48px; border-radius: 13px; display: flex;
    align-items: center; justify-content: center;
    background: linear-gradient(135deg, #06b6d4, #2563eb);
    box-shadow: 0 8px 25px rgba(37,99,235,0.35); font-size: 20px; font-weight: 900;
}
.brand-text h1 { font-size: 1.05rem; font-weight: 800; letter-spacing: -0.3px; color: #f8fafc; }
.brand-text p { color: #38bdf8; font-size: 0.70rem; margin-top: 3px; font-weight: 700; letter-spacing: 0.5px; }

/* ============================================================
   CARDS & CONTROLS
============================================================ */
.card {
    background: rgba(15,23,42,0.78); border: 1px solid rgba(148,163,184,0.13);
    border-radius: 13px; padding: 14px; margin-bottom: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.12);
}
.card-title {
    display: flex; align-items: center; gap: 8px; color: #e2e8f0;
    font-size: 0.76rem; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 12px;
}
.card-title .dot { width: 7px; height: 7px; border-radius: 50%; background: #38bdf8; box-shadow: 0 0 10px #38bdf8; }

.unit-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; padding: 5px; background: #020617; border-radius: 10px; border: 1px solid #1e293b; }
.unit-option { padding: 9px 7px; text-align: center; border-radius: 7px; cursor: pointer; font-size: 0.74rem; font-weight: 700; color: #64748b; transition: 0.2s; }
.unit-option.active { background: linear-gradient(135deg, #0284c7, #2563eb); color: white; box-shadow: 0 4px 15px rgba(37,99,235,0.3); }

select.select-control {
    width: 100%; padding: 9px 12px; background: #020617; border: 1px solid #1e293b;
    border-radius: 9px; color: #f8fafc; font-size: 0.75rem; font-weight: 700; outline: none;
    cursor: pointer; transition: 0.2s;
}
select.select-control:focus { border-color: #0284c7; box-shadow: 0 0 10px rgba(2,132,199,0.3); }

.control { margin-bottom: 12px; }
.control:last-child { margin-bottom: 0; }
.control-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.control-header label { color: #cbd5e1; font-size: 0.74rem; font-weight: 600; }
.value { color: #38bdf8; font-size: 0.74rem; font-weight: 800; }

input[type="range"] { width: 100%; height: 5px; appearance: none; background: #1e293b; border-radius: 10px; outline: none; }
input[type="range"]::-webkit-slider-thumb { appearance: none; width: 15px; height: 15px; border-radius: 50%; background: #38bdf8; cursor: pointer; box-shadow: 0 0 12px rgba(56,189,248,0.65); }
input[type="range"]::-moz-range-thumb { width: 15px; height: 15px; border-radius: 50%; background: #38bdf8; cursor: pointer; }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
.info-box { padding: 10px; background: rgba(2,6,23,0.65); border: 1px solid rgba(148,163,184,0.1); border-radius: 9px; }
.info-label { color: #64748b; font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px; }
.info-value { color: #e2e8f0; font-size: 0.78rem; font-weight: 700; }

.toggle { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(148,163,184,0.08); }
.toggle:last-child { border-bottom: none; }
.toggle span { font-size: 0.73rem; color: #cbd5e1; }

.switch { position: relative; width: 36px; height: 20px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; inset: 0; background: #334155; border-radius: 20px; cursor: pointer; transition: 0.2s; }
.slider:before { content: ""; position: absolute; width: 14px; height: 14px; left: 3px; top: 3px; background: white; border-radius: 50%; transition: 0.2s; }
.switch input:checked + .slider { background: #0284c7; }
.switch input:checked + .slider:before { transform: translateX(16px); }

.button-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
button { border: none; border-radius: 9px; padding: 10px; color: white; font-size: 0.72rem; font-weight: 800; cursor: pointer; transition: transform 0.15s, opacity 0.15s; }
button:hover { transform: translateY(-1px); opacity: 0.92; }
.btn-blue { background: linear-gradient(135deg, #0284c7, #2563eb); }
.btn-green { background: linear-gradient(135deg, #059669, #16a34a); }
.btn-dark { background: linear-gradient(135deg, #334155, #1e293b); }

/* ============================================================
   VIEWPORT & OVERLAYS
============================================================ */
#viewport { flex: 1; position: relative; height: 100vh; overflow: hidden; }
canvas { display: block; }

#top-hud { position: absolute; top: 18px; left: 18px; right: 18px; display: flex; justify-content: space-between; pointer-events: none; }
.hud-card { background: rgba(2,6,23,0.78); backdrop-filter: blur(14px); border: 1px solid rgba(148,163,184,0.15); border-radius: 12px; padding: 12px 15px; box-shadow: 0 12px 30px rgba(0,0,0,0.25); }
.hud-title { color: #38bdf8; font-size: 0.67rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 800; margin-bottom: 4px; }
.hud-main { font-size: 0.84rem; font-weight: 800; }
.hud-sub { color: #94a3b8; font-size: 0.63rem; margin-top: 3px; }

#result-panel { position: absolute; right: 18px; top: 115px; width: 275px; background: rgba(2,6,23,0.84); backdrop-filter: blur(15px); border: 1px solid rgba(56,189,248,0.18); border-radius: 14px; padding: 15px; box-shadow: 0 15px 40px rgba(0,0,0,0.3); }
.result-title { color: #38bdf8; font-size: 0.69rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 12px; text-transform: uppercase; }
.result-row { display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid rgba(148,163,184,0.08); font-size: 0.71rem; }
.result-row:last-child { border-bottom: none; }
.result-label { color: #94a3b8; }
.result-value { color: #4ade80; font-weight: 800; }

#load-badge { position: absolute; left: 18px; bottom: 18px; padding: 12px 15px; background: rgba(2,6,23,0.82); backdrop-filter: blur(12px); border: 1px solid rgba(250,204,21,0.22); border-radius: 11px; font-size: 0.69rem; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
.load-title { color: #facc15; font-weight: 800; margin-bottom: 6px; font-size: 0.65rem; letter-spacing: 0.7px; }
.load-values { color: #e2e8f0; line-height: 1.7; }

#legend { position: absolute; right: 18px; bottom: 18px; background: rgba(2,6,23,0.82); backdrop-filter: blur(12px); border: 1px solid rgba(148,163,184,0.14); border-radius: 11px; padding: 12px; width: 190px; }
.legend-title { color: #38bdf8; font-size: 0.65rem; font-weight: 800; margin-bottom: 8px; letter-spacing: 0.7px; }
.legend-item { display: flex; align-items: center; gap: 7px; color: #cbd5e1; font-size: 0.64rem; margin-bottom: 6px; }
.legend-color { width: 10px; height: 10px; border-radius: 3px; }

#sidebar::-webkit-scrollbar { width: 6px; }
#sidebar::-webkit-scrollbar-track { background: transparent; }
#sidebar::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }

@media(max-width:900px) {
    body { overflow: auto; }
    #app { flex-direction: column; height: auto; }
    #sidebar { width: 100%; min-width: 0; height: auto; max-height: none; }
    #viewport { height: 70vh; min-height: 500px; }
    #result-panel { width: 220px; }
}
</style>
</head>

<body>
<div id="app">

<!-- SIDEBAR -->
<aside id="sidebar">

<div class="brand">
    <div class="brand-icon">R3</div>
    <div class="brand-text">
        <h1>Rev 3 Solver Exercise</h1>
        <p>Ryanold Renz C. Miranda | BSCE-3D</p>
    </div>
</div>

<!-- STUDENT & COURSE DETAILS CARD -->
<div class="card" style="border-color: rgba(56,189,248,0.3);">
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

<!-- MODEL VIEW SELECTION -->
<div class="card">
    <div class="card-title"><span class="dot"></span>Model Style</div>
    <select id="model-style" class="select-control" onchange="rebuild3DScene()">
        <option value="solid" selected>3D Extruded Cube (Solids)</option>
        <option value="line">Wireframe / Line Model</option>
    </select>
</div>

<!-- LOADS -->
<div class="card">
    <div class="card-title"><span class="dot" style="background:#facc15;box-shadow:0 0 10px #facc15;"></span>Nodal Load — Node 7</div>
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

<!-- MODEL INFO -->
<div class="card">
    <div class="card-title"><span class="dot"></span>Model Information</div>
    <div class="info-grid">
        <div class="info-box"><div class="info-label">Nodes</div><div class="info-value">8 (48 DOF)</div></div>
        <div class="info-box"><div class="info-label">Members</div><div class="info-value">12 (M1-M12)</div></div>
        <div class="info-box"><div class="info-label">Supports</div><div class="info-value">N1–N4 (Pinned)</div></div>
        <div class="info-box"><div class="info-label">Loaded Node</div><div class="info-value">N7</div></div>
    </div>
</div>

<!-- VISUALIZATION -->
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
        <div class="hud-title">Rev 3 Solver Development Exercise</div>
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
    <div class="result-title">Node 7 — Displacement Results</div>
    <div class="result-row"><span class="result-label">Ux</span><span class="result-value" id="result-ux">0.000 mm</span></div>
    <div class="result-row"><span class="result-label">Uy</span><span class="result-value" id="result-uy">0.000 mm</span></div>
    <div class="result-row"><span class="result-label">Uz</span><span class="result-value" id="result-uz">0.000 mm</span></div>
    <div class="result-row"><span class="result-label">Resultant</span><span class="result-value" id="result-total">0.000 mm</span></div>
</div>

<div id="load-badge">
    <div class="load-title">APPLIED LOAD — NODE 7</div>
    <div class="load-values">
        Fx: <span id="load-x">40</span> &nbsp;
        Fy: <span id="load-y">-60</span> &nbsp;
        Fz: <span id="load-z">25</span>
        <span id="load-unit">kN</span>
    </div>
</div>

<div id="legend">
    <div class="legend-title">VISUAL LEGEND</div>
    <div class="legend-item"><span class="legend-color" style="background:#38bdf8;"></span>Beam (M1–M8)</div>
    <div class="legend-item"><span class="legend-color" style="background:#22c55e;"></span>Column (β=90°, M9–M12)</div>
    <div class="legend-item"><span class="legend-color" style="background:#f472b6;"></span>Free Node (N5–N8)</div>
    <div class="legend-item"><span class="legend-color" style="background:#22c55e;"></span>Pinned Support (N1–N4)</div>
    <div class="legend-item"><span class="legend-color" style="background:#ef4444;"></span>Deflected Shape</div>
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
let loadArrowObjects = [];

const BASE_EDGE_M = 6.0;
const BASE_FX_KN = 40;
const BASE_FY_KN = -60;
const BASE_FZ_KN = 25;
const BASE_AREA_M2 = 0.005;
const BASE_E_KN_M2 = 200000000;

/* THREE.JS SETUP */
const container = document.getElementById("viewport");
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x020617);

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

/* LIGHTING */
scene.add(new THREE.AmbientLight(0xffffff, 0.72));
const directionalLight = new THREE.DirectionalLight(0xffffff, 1.15);
directionalLight.position.set(25, 40, 25);
scene.add(directionalLight);

/* GRID */
const grid = new THREE.GridHelper(60, 60, 0x334155, 0x172033);
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
    document.getElementById("load-unit").innerText = U.force;
}

/* MATRIX SOLVER */
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
    const FxKN = parseFloat(document.getElementById("load-fx").value);
    const FyKN = parseFloat(document.getElementById("load-fy").value);
    const FzKN = parseFloat(document.getElementById("load-fz").value);

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

    rawDisplacements = solve3DFrame(
        currentNodes, currentMembers,
        { 6: [FxKN, FyKN, FzKN] },
        BASE_E_KN_M2, BASE_AREA_M2
    );

    const ux = rawDisplacements[18], uy = rawDisplacements[19], uz = rawDisplacements[20];
    const resultant = Math.hypot(ux, uy, uz);

    updateResults(ux, uy, uz, resultant);
    updateLoadDisplay(FxKN, FyKN, FzKN);
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

function updateLoadDisplay(Fx, Fy, Fz) {
    const U = UNIT[unitSystem];
    document.getElementById("fx-value").innerText = getDisplayForce(Fx).toFixed(2) + " " + U.force;
    document.getElementById("fy-value").innerText = getDisplayForce(Fy).toFixed(2) + " " + U.force;
    document.getElementById("fz-value").innerText = getDisplayForce(Fz).toFixed(2) + " " + U.force;
    document.getElementById("load-x").innerText = getDisplayForce(Fx).toFixed(2);
    document.getElementById("load-y").innerText = getDisplayForce(Fy).toFixed(2);
    document.getElementById("load-z").innerText = getDisplayForce(Fz).toFixed(2);
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
    loadArrowObjects.forEach(obj => scene.remove(obj)); loadArrowObjects = [];
}

function createTextSprite(message) {
    const canvas = document.createElement("canvas");
    canvas.width = 384; canvas.height = 128;
    const context = canvas.getContext("2d");
    context.font = "bold 36px Arial";
    context.textAlign = "center"; context.textBaseline = "middle";
    context.lineWidth = 8; context.strokeStyle = "#020617"; context.fillStyle = "#ffffff";
    context.strokeText(message, 192, 64);
    context.fillText(message, 192, 64);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(2.1, 0.7, 1);
    return sprite;
}

function createCubeFaces() {
    const edge = parseFloat(document.getElementById("cube-edge").value);
    const material = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.055, side: THREE.DoubleSide, depthWrite: false });

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
    const showLocal = document.getElementById("chk-local").checked;
    const showGlobal = document.getElementById("chk-global").checked;
    const showRelease = document.getElementById("chk-release").checked;
    const showLabels = document.getElementById("chk-labels").checked;
    const showMemberLabels = document.getElementById("chk-member-labels").checked;
    const showSectionLabels = document.getElementById("chk-section-labels").checked;
    const showMaterialLabels = document.getElementById("chk-material-labels").checked;

    if (showFaces) createCubeFaces();

    const beamMaterial = new THREE.MeshStandardMaterial({ color: 0x38bdf8, metalness: 0.3, roughness: 0.35 });
    const columnMaterial = new THREE.MeshStandardMaterial({ color: 0x22c55e, metalness: 0.25, roughness: 0.4 });
    const supportMaterial = new THREE.MeshStandardMaterial({ color: 0x22c55e, metalness: 0.15, roughness: 0.45 });
    const freeMaterial = new THREE.MeshStandardMaterial({ color: 0xf472b6, roughness: 0.35 });

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
            const label = createTextSprite(labelText);
            label.position.set(x, y + 0.5, z);
            scene.add(label);
            labelObjects.push(label);
        }
    });

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
            const lineColor = mem.type === "Column" ? 0x22c55e : 0x38bdf8;
            const geometry = new THREE.BufferGeometry().setFromPoints([p1, p2]);
            const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: lineColor, linewidth: 2 }));
            
            scene.add(line);
            sceneObjects.push(line);
        }

        const midPt = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
        let verticalOffset = 0.25;

        if (showMemberLabels) {
            const betaTxt = mem.beta !== 0 ? ` (β=${mem.beta}°)` : "";
            const mLabel = createTextSprite(`${mem.id}${betaTxt}`);
            mLabel.position.copy(midPt).add(new THREE.Vector3(0, verticalOffset, 0));
            scene.add(mLabel);
            labelObjects.push(mLabel);
            verticalOffset += 0.45;
        }

        if (showSectionLabels) {
            const secLabel = createTextSprite(`Sec: ${mem.section}`);
            secLabel.position.copy(midPt).add(new THREE.Vector3(0, verticalOffset, 0));
            scene.add(secLabel);
            labelObjects.push(secLabel);
            verticalOffset += 0.45;
        }

        if (showMaterialLabels) {
            const matLabel = createTextSprite(`Mat: ${mem.material}`);
            matLabel.position.copy(midPt).add(new THREE.Vector3(0, verticalOffset, 0));
            scene.add(matLabel);
            labelObjects.push(matLabel);
        }

        if (mem.release === "both" && showRelease) {
            [0.08, 0.92].forEach(ratio => {
                const pos = new THREE.Vector3().lerpVectors(p1, p2, ratio);
                const ring = new THREE.Mesh(
                    new THREE.RingGeometry(0.10, 0.17, 20),
                    new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide })
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

            const ax = new THREE.ArrowHelper(localX, midpoint, axisLength, 0xef4444, 0.17, 0.08);
            const ay = new THREE.ArrowHelper(localY, midpoint, axisLength, 0x22c55e, 0.17, 0.08);
            const az = new THREE.ArrowHelper(localZ, midpoint, axisLength, 0x3b82f6, 0.17, 0.08);

            scene.add(ax, ay, az);
            sceneObjects.push(ax, ay, az);
        }
    });

    /* GLOBAL AXIS */
    if (showGlobal) {
        const origin = new THREE.Vector3(-1, 0, -1);
        const gx = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), origin, 2, 0xef4444, 0.3, 0.15);
        const gy = new THREE.ArrowHelper(new THREE.Vector3(0,1,0), origin, 2, 0x22c55e, 0.3, 0.15);
        const gz = new THREE.ArrowHelper(new THREE.Vector3(0,0,1), origin, 2, 0x3b82f6, 0.3, 0.15);
        scene.add(gx, gy, gz);
        sceneObjects.push(gx, gy, gz);
    }

    createLoadArrow();
    updateDeformationVisuals();
}

function createLoadArrow() {
    const Fx = parseFloat(document.getElementById("load-fx").value);
    const Fy = parseFloat(document.getElementById("load-fy").value);
    const Fz = parseFloat(document.getElementById("load-fz").value);
    const node = new THREE.Vector3(...currentNodes[6]);
    const load = new THREE.Vector3(Fx, Fy, Fz);

    if (load.length() < 0.0001) return;

    const direction = load.clone().normalize();
    const arrow = new THREE.ArrowHelper(direction, node, 1.8, 0xfacc15, 0.36, 0.18);
    scene.add(arrow);
    loadArrowObjects.push(arrow);
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

    const material = new THREE.LineBasicMaterial({ color: 0xef4444, linewidth: 3 });

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
    const edgeM = parseFloat(document.getElementById("cube-edge").value);

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

    const edgeDisplay = getDisplayEdge();
    const fx = getDisplayForce(parseFloat(document.getElementById("load-fx").value));
    const fy = getDisplayForce(parseFloat(document.getElementById("load-fy").value));
    const fz = getDisplayForce(parseFloat(document.getElementById("load-fz").value));

    const summaryData = [
        { Parameter: "Exercise Title", Value: "Rev 3 Solver Development Exercise" },
        { Parameter: "Student Name", Value: "Ryanold Renz C. Miranda" },
        { Parameter: "Section", Value: "BSCE-3D" },
        { Parameter: "Course", Value: "Numerical Solutions to Civil Engineering Problems" },
        { Parameter: "Unit System", Value: U.name },
        { Parameter: "Cube Edge Dimension", Value: edgeDisplay.toFixed(4) + " " + U.length },
        { Parameter: "Total Nodes", Value: 8 },
        { Parameter: "Total Members", Value: 12 },
        { Parameter: "Pinned Nodes", Value: "N1, N2, N3, N4" },
        { Parameter: "Loaded Node", Value: "N7" },
        { Parameter: "Global DOFs", Value: "48 (6 per node)" },
        { Parameter: "Restrained DOFs", Value: 12 },
        { Parameter: "Young's Modulus", Value: unitSystem === "SI" ? "200 GPa" : getDisplayE().toFixed(3) + " ksi" },
        { Parameter: "Section Area", Value: getDisplayArea().toFixed(6) + " " + U.area },
        { Parameter: "Applied Load Fx", Value: fx.toFixed(4) + " " + U.force },
        { Parameter: "Applied Load Fy", Value: fy.toFixed(4) + " " + U.force },
        { Parameter: "Applied Load Fz", Value: fz.toFixed(4) + " " + U.force }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summaryData), "Model Summary");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(nodeData), "Nodal Data");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(memberData), "Member Data");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(displacementData), "Displacements");
    XLSX.writeFile(wb, "Rev3_Solver_Exercise_Ryanold_Miranda_BSCE3D.xlsx");
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

output_html = "3D_Cube_Space_Frame_FEM_Rev3.html"

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_3d_rev3)

absolute_path = os.path.abspath(output_html)

print("\n" + "=" * 65)
print("REV 3 SOLVER DEVELOPMENT EXERCISE")
print("NUMERICAL SOLUTIONS TO CIVIL ENGINEERING PROBLEMS")
print("=" * 65)
print(f"Student Name : Ryanold Renz C. Miranda")
print(f"Section      : BSCE-3D")
print(f"\nSuccessfully generated:\n{absolute_path}\n")
print("Updated Interface Elements:")
print("  ✓ Web Page Title & Header HUD")
print("  ✓ Sidebar Submission Details Card")
print("  ✓ Excel Data Export Metadata")
print("  ✓ Added Member, Section, and Material Labels to 3D View Layer Controls")
print("\n" + "=" * 65)

webbrowser.open(absolute_path)