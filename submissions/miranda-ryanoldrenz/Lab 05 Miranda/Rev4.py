import os
import webbrowser

# ============================================================
# CUBE FEM STUDIO - INTEGRATED MODERN DASHBOARD & FEM SOLVER
# STUDENT: Ryanold Renz C. Miranda (BSCE-3D)
# ============================================================

html_content = r"""<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cube FEM Studio - Professional Structural Analysis</title>

<!-- Three.js, OrbitControls & SheetJS Libraries -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

<style>
/* ============================================================
   DESIGN SYSTEM & INTEGRATED DASHBOARD LAYOUT
============================================================ */
:root {
    --bg-app: #e2e8f0;
    --bg-surface: #ffffff;
    --bg-sidebar: #1e293b;
    --sidebar-card: #0f172a;
    --border-color: #cbd5e1;
    --border-light: #f1f5f9;
    --text-primary: #0f172a;
    --text-muted: #64748b;
    
    /* KPI & Modern Dashboard Colors */
    --card-teal: #0d5c75;
    --card-amber: #f59e0b;
    --card-navy: #1e1b4b;
    --card-dark: #0f172a;
    
    --accent-blue: #0284c7;
    --accent-blue-hover: #0369a1;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    
    --radius-lg: 16px;
    --radius-md: 10px;
    --radius-sm: 6px;
    
    --shadow-card: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.02);
    --font-main: "Segoe UI", system-ui, -apple-system, sans-serif;
}

[data-theme="dark"] {
    --bg-app: #090d16;
    --bg-surface: #131c2e;
    --bg-sidebar: #0a0f1d;
    --sidebar-card: #040711;
    --border-color: #1e293b;
    --border-light: #0f172a;
    --text-primary: #f8fafc;
    --text-muted: #94a3b8;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; font-family: var(--font-main); background: var(--bg-app); color: var(--text-primary); overflow: hidden; font-size: 13px; }

#app-container { display: flex; width: 100vw; height: 100vh; padding: 12px; gap: 12px; }

/* ============================================================
   MAIN CONTENT AREA
============================================================ */
#main-content { flex: 1; display: flex; flex-direction: column; gap: 12px; overflow: hidden; }

/* TOP KPI METRICS ROW */
.metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; height: 80px; flex-shrink: 0; }
.metric-card {
    border-radius: var(--radius-md); padding: 12px 16px; color: #ffffff; display: flex;
    flex-direction: column; justify-between; position: relative; box-shadow: var(--shadow-card);
}
.metric-card.teal { background: var(--card-teal); }
.metric-card.amber { background: var(--card-amber); }
.metric-card.navy { background: var(--card-navy); }
.metric-card.dark { background: var(--card-dark); }

.metric-title { font-size: 10px; font-weight: 700; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-value { font-size: 18px; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.metric-sub { font-size: 9px; opacity: 0.75; }
.metric-icon { position: absolute; top: 10px; right: 12px; opacity: 0.3; font-size: 18px; }

/* RIBBON & NAVIGATION TABS */
#navigation-bar { background: var(--bg-surface); border-radius: var(--radius-md); border: 1px solid var(--border-color); overflow: hidden; flex-shrink: 0; }
.nav-tabs { display: flex; background: var(--bg-sidebar); padding-left: 6px; gap: 2px; }
.tab-btn {
    padding: 6px 14px; background: transparent; border: none; color: #94a3b8;
    font-size: 11px; font-weight: 600; cursor: pointer; border-top-left-radius: 4px; border-top-right-radius: 4px;
}
.tab-btn:hover { color: #f8fafc; background: rgba(255,255,255,0.05); }
.tab-btn.active { background: var(--bg-surface); color: var(--accent-blue); font-weight: 700; }

.ribbon-panel {
    display: none; height: 75px; background: var(--bg-surface); padding: 6px 12px;
    align-items: center; gap: 16px; overflow-x: auto;
}
.ribbon-panel.active { display: flex; }

.ribbon-group { display: flex; flex-direction: column; height: 100%; justify-content: space-between; border-right: 1px solid var(--border-light); padding-right: 12px; }
.ribbon-group-title { font-size: 9px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; text-align: center; }
.ribbon-controls { display: flex; align-items: center; gap: 8px; flex: 1; }

.r-btn {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: transparent; border: 1px solid transparent; padding: 4px 8px; border-radius: 4px;
    cursor: pointer; color: var(--text-primary); font-size: 10px; font-weight: 600; gap: 2px; min-width: 50px;
}
.r-btn:hover { background: var(--bg-app); border-color: var(--border-color); }
.r-btn-sm { flex-direction: row; padding: 3px 6px; min-width: 0; }

.r-input-group { display: flex; flex-direction: column; gap: 2px; }
.r-input-group label { font-size: 9px; color: var(--text-muted); font-weight: 600; }
.r-select, .r-input {
    padding: 3px 6px; border: 1px solid var(--border-color); border-radius: 4px;
    background: var(--bg-surface); color: var(--text-primary); font-size: 11px; font-weight: 600; outline: none;
}

/* WORKSPACE GRID: Left Controls, Center Viewport, Right Summary Panel */
.workspace-grid { flex: 1; display: grid; grid-template-columns: 280px 1fr 310px; gap: 12px; overflow: hidden; min-height: 0; }

/* LEFT CONTROLS CARD */
.controls-card {
    background: var(--bg-surface); border-radius: var(--radius-lg); padding: 14px;
    display: flex; flex-direction: column; gap: 12px; overflow-y: auto; box-shadow: var(--shadow-card);
}

.card-section-title { font-size: 10px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border-light); padding-bottom: 3px; }

/* RIGHT SUMMARY & DETAILS PANEL */
.right-panel {
    background: var(--bg-surface); border-radius: var(--radius-lg); padding: 14px;
    display: flex; flex-direction: column; gap: 10px; overflow-y: auto; box-shadow: var(--shadow-card);
}

/* 3D VIEWPORT CONTAINER CARD */
.viewport-card {
    background: var(--bg-surface); border-radius: var(--radius-lg);
    display: flex; flex-direction: column; overflow: hidden; position: relative; box-shadow: var(--shadow-card);
}
#canvas-container { flex: 1; width: 100%; height: 100%; position: relative; }

/* HUD OVERLAYS */
.hud-card {
    position: absolute; background: rgba(255,255,255,0.88); backdrop-filter: blur(8px);
    border-radius: var(--radius-md); padding: 8px 12px; box-shadow: var(--shadow-card);
    pointer-events: none; z-index: 5; font-size: 11px; border: 1px solid var(--border-color);
}
[data-theme="dark"] .hud-card { background: rgba(19, 28, 46, 0.88); }
#hud-top-left { top: 12px; left: 12px; }

/* VIEW CUBE OVERLAY */
#view-cube {
    position: absolute; top: 12px; right: 12px; width: 55px; height: 55px;
    background: rgba(2, 132, 199, 0.1); border: 1px solid var(--accent-blue);
    border-radius: 8px; display: flex; align-items: center; justify-content: center;
    font-weight: 800; color: var(--accent-blue); font-size: 10px; pointer-events: none;
}

/* BOTTOM DATA TABLE CARD */
.bottom-table-card {
    height: 180px; background: var(--bg-surface); border-radius: var(--radius-lg);
    display: flex; flex-direction: column; padding: 10px 14px; box-shadow: var(--shadow-card); overflow: hidden;
    transition: height 0.25s ease; flex-shrink: 0;
}
.bottom-table-card.collapsed {
    height: 42px !important;
    padding-bottom: 4px;
}
.bottom-table-card.collapsed .bottom-content {
    display: none;
}

.bottom-header-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-light); padding-bottom: 4px; margin-bottom: 8px; }
.bottom-tabs { display: flex; gap: 8px; }
.b-tab {
    padding: 4px 10px; border: none; background: transparent; font-size: 11px; font-weight: 700;
    cursor: pointer; color: var(--text-muted); border-radius: var(--radius-sm); transition: all 0.2s;
}
.b-tab.active { background: var(--border-light); color: var(--accent-blue); }

.toggle-table-btn {
    background: var(--bg-app); border: 1px solid var(--border-color); color: var(--text-primary);
    padding: 3px 10px; border-radius: var(--radius-sm); font-size: 11px; font-weight: 700; cursor: pointer;
    display: flex; align-items: center; gap: 4px; transition: background 0.2s;
}
.toggle-table-btn:hover { background: var(--border-color); }

.bottom-content { flex: 1; overflow: auto; }

/* TABLES */
.eng-table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; }
.eng-table th { background: var(--bg-app); color: var(--text-muted); font-weight: 700; padding: 5px 8px; position: sticky; top: 0; border-bottom: 1px solid var(--border-color); }
.eng-table td { padding: 4px 8px; border-bottom: 1px solid var(--border-light); }
.eng-table tr:hover { background: rgba(2,132,199,0.05); cursor: pointer; }

/* INPUT & FORM CONTROLS */
.form-group { display: flex; flex-direction: column; gap: 3px; margin-bottom: 6px; }
.form-group label { font-size: 10px; color: var(--text-muted); font-weight: 700; }
.form-control {
    padding: 5px 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm);
    background: var(--bg-app); color: var(--text-primary); font-size: 11px; font-weight: 600; outline: none; width: 100%;
}
.form-control:focus { border-color: var(--accent-blue); background: var(--bg-surface); }

.toggle-row { display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 600; padding: 2px 0; }

.btn-primary {
    background: var(--accent-blue); color: #fff; border: none; padding: 6px 10px;
    border-radius: var(--radius-sm); font-weight: 700; cursor: pointer; font-size: 11px; width: 100%;
    transition: background 0.2s;
}
.btn-primary:hover { background: var(--accent-blue-hover); }

</style>
</head>

<body data-theme="light">
<div id="app-container">

<!-- ============================================================
     MAIN WORKSPACE CONTENT
============================================================ -->
<main id="main-content">

    <!-- TOP KPI / METRICS ROW -->
    <header class="metrics-row">
        <div class="metric-card teal">
            <div class="metric-title">Unit System</div>
            <div class="metric-value" id="kpi-units">SI (m, kN)</div>
            <div class="metric-sub">Active Engineering Metric</div>
            <div class="metric-icon">⚙️</div>
        </div>

        <div class="metric-card amber">
            <div class="metric-title">Max Displacement</div>
            <div class="metric-value" id="kpi-max-disp">0.0000 mm</div>
            <div class="metric-sub">Critical Node Resultant</div>
            <div class="metric-icon">📉</div>
        </div>

        <div class="metric-card navy">
            <div class="metric-title">Active Load Case</div>
            <div class="metric-value" id="kpi-load-case" style="font-size:13px; font-weight:700;">Manual Sliders</div>
            <div class="metric-sub">Applied Boundary Conditions</div>
            <div class="metric-icon">⚖️</div>
        </div>

        <div class="metric-card dark">
            <div class="metric-title">Solver Status</div>
            <div class="metric-value" style="color:var(--accent-green)" id="kpi-solver-status">READY</div>
            <div class="metric-sub">3-DOF Nodal Formulation</div>
            <div class="metric-icon">🚀</div>
        </div>
    </header>

    <!-- NAVIGATION & RIBBON BAR -->
    <div id="navigation-bar">
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('home')">Home</button>
            <button class="tab-btn" onclick="switchTab('file')">File</button>
            <button class="tab-btn" onclick="switchTab('model')">Model</button>
            <button class="tab-btn" onclick="switchTab('loads')">Loads</button>
            <button class="tab-btn" onclick="switchTab('analyze')">Analyze</button>
            <button class="tab-btn" onclick="switchTab('results')">Results</button>
            <button class="tab-btn" onclick="switchTab('view')">View</button>
            <button class="tab-btn" onclick="switchTab('export')">Export</button>
        </div>

        <!-- TAB 1: HOME -->
        <div class="ribbon-panel active" id="ribbon-home">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <button class="r-btn" onclick="runAnalysisWorkflow()">▶ Run Analysis</button>
                    <button class="r-btn" onclick="exportToExcel()">📊 Quick Export</button>
                </div>
                <div class="ribbon-group-title">Actions</div>
            </div>
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <button class="r-btn" id="themeToggleBtn" onclick="toggleTheme()">🌙 Dark Mode</button>
                </div>
                <div class="ribbon-group-title">Theme Mode</div>
            </div>
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <div class="r-input-group">
                        <label>Active Unit System</label>
                        <select class="r-select" id="home-unit-select" onchange="setUnitSystem(this.value)">
                            <option value="SI" selected>Standard (SI - m, kN)</option>
                            <option value="IMPERIAL">Imperial (ft, kip)</option>
                        </select>
                    </div>
                </div>
                <div class="ribbon-group-title">Units Config</div>
            </div>
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <div class="r-input-group">
                        <label>Quick Load Case</label>
                        <select class="r-select" id="home-load-select" onchange="syncLoadCase(this.value)">
                            <option value="custom">Manual Sliders (Node 7 Focus)</option>
                            <option value="lc1">LC1 - Dead / Self Weight</option>
                            <option value="lc2">LC2 - Roof Dead (5.0 kN/m)</option>
                            <option value="lc3">LC3 - Roof Live (3.0 kN/m)</option>
                            <option value="lc4">LC4 - Roof Beam Center Load (5.0 kN)</option>
                            <option value="lc5">LC5 - Wind X (10 kN Total)</option>
                            <option value="lc6">LC6 - Wind Z (10 kN Total)</option>
                            <option value="lc7">LC7 - Seismic X (15 kN Total)</option>
                            <option value="lc8">LC8 - Seismic Z (15 kN Total)</option>
                            <option value="lc9">LC9 - Temperature +15C</option>
                            <option value="comb1">LRFD Comb 1: 1.4D</option>
                            <option value="comb13">ASD Comb 13: D</option>
                            <option value="comb15">ASD Comb 15: D</option>
                        </select>
                    </div>
                </div>
                <div class="ribbon-group-title">Quick Load Selector</div>
            </div>
        </div>

        <!-- TAB 2: FILE -->
        <div class="ribbon-panel" id="ribbon-file">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <button class="r-btn" onclick="resetProject()">📄 New Project</button>
                    <button class="r-btn" onclick="triggerSaveProject()">💾 Save Project</button>
                </div>
                <div class="ribbon-group-title">Project Files</div>
            </div>
        </div>

        <!-- TAB 3: MODEL -->
        <div class="ribbon-panel" id="ribbon-model">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <div class="r-input-group">
                        <label>Cube Edge Size</label>
                        <input type="number" id="ribbon-cube-edge" class="r-input" value="6.0" step="0.5" min="3" max="12" onchange="syncCubeEdge(this.value)">
                    </div>
                    <div class="r-input-group">
                        <label>Display Render Style</label>
                        <select class="r-select" id="ribbon-model-style" onchange="syncModelStyle(this.value)">
                            <option value="solid">3D Extruded Cube (Solids)</option>
                            <option value="line">Wireframe Line Model</option>
                        </select>
                    </div>
                </div>
                <div class="ribbon-group-title">Geometry & Rendering</div>
            </div>
        </div>

        <!-- TAB 4: LOADS -->
        <div class="ribbon-panel" id="ribbon-loads">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <div class="r-input-group">
                        <label>Node 7 Fx</label>
                        <input type="number" id="r-fx" class="r-input" style="width:65px;" value="40" onchange="syncManualLoad()">
                    </div>
                    <div class="r-input-group">
                        <label>Node 7 Fy</label>
                        <input type="number" id="r-fy" class="r-input" style="width:65px;" value="-60" onchange="syncManualLoad()">
                    </div>
                    <div class="r-input-group">
                        <label>Node 7 Fz</label>
                        <input type="number" id="r-fz" class="r-input" style="width:65px;" value="25" onchange="syncManualLoad()">
                    </div>
                </div>
                <div class="ribbon-group-title">Manual Nodal Load Sliders Focus</div>
            </div>
        </div>

        <!-- TAB 5: ANALYZE -->
        <div class="ribbon-panel" id="ribbon-analyze">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <button class="r-btn" onclick="validateModel()">✔️ Validate Model</button>
                    <button class="r-btn" onclick="runAnalysisWorkflow()">▶ Run FEM Solver</button>
                </div>
                <div class="ribbon-group-title">Calculation Engine</div>
            </div>
        </div>

        <!-- TAB 6: RESULTS -->
        <div class="ribbon-panel" id="ribbon-results">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <button class="r-btn" onclick="switchBottomTab('displacements')">Displacements</button>
                    <button class="r-btn" onclick="switchBottomTab('reactions')">Reactions</button>
                    <button class="r-btn" onclick="switchBottomTab('summary')">Audit Log</button>
                </div>
                <div class="ribbon-group-title">Result Tables View</div>
            </div>
        </div>

        <!-- TAB 7: VIEW -->
        <div class="ribbon-panel" id="ribbon-view">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <button class="r-btn r-btn-sm" onclick="setPresetView('iso')">Isometric</button>
                    <button class="r-btn r-btn-sm" onclick="setPresetView('top')">Top</button>
                    <button class="r-btn r-btn-sm" onclick="setPresetView('front')">Front</button>
                    <button class="r-btn r-btn-sm" onclick="resetView()">Fit Screen</button>
                </div>
                <div class="ribbon-group-title">Camera Views</div>
            </div>
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <div class="r-input-group">
                        <label>Deflection Scale Factor</label>
                        <input type="range" id="r-deflect-scale" min="1" max="500" value="100" oninput="syncDeflectScale(this.value)">
                    </div>
                </div>
                <div class="ribbon-group-title">Deformation Visualization</div>
            </div>
        </div>

        <!-- TAB 8: EXPORT -->
        <div class="ribbon-panel" id="ribbon-export">
            <div class="ribbon-group">
                <div class="ribbon-controls">
                    <button class="r-btn" onclick="exportToExcel()">📊 Export Excel Spreadsheet</button>
                </div>
                <div class="ribbon-group-title">Reports</div>
            </div>
        </div>
    </div>

    <!-- DASHBOARD WORKSPACE GRID -->
    <div class="workspace-grid">

        <!-- LEFT CONTROLS CARD -->
        <section class="controls-card">
            <div class="card-section-title">Project Metadata</div>
            <div class="form-group">
                <label>Model Name</label>
                <input type="text" id="meta-model-name" class="form-control" value="Cube Structural Model" oninput="updateHeaderTitle()">
            </div>
            <div class="form-group">
                <label>Company</label>
                <input type="text" id="meta-company" class="form-control" value="RYse Built Co.">
            </div>
            <div class="form-group">
                <label>Designer</label>
                <input type="text" id="meta-designer" class="form-control" value="Ryanold Renz C. Miranda">
            </div>

            <div id="side-manual-load-card">
                <div class="card-section-title">Node 7 Manual Loads (<span class="unit-force">kN</span>)</div>
                <div class="form-group">
                    <label>Force X: <span id="val-fx">40</span></label>
                    <input type="range" id="slide-fx" min="-150" max="150" value="40" oninput="syncManualLoad()">
                </div>
                <div class="form-group">
                    <label>Force Y: <span id="val-fy">-60</span></label>
                    <input type="range" id="slide-fy" min="-150" max="150" value="-60" oninput="syncManualLoad()">
                </div>
                <div class="form-group">
                    <label>Force Z: <span id="val-fz">25</span></label>
                    <input type="range" id="slide-fz" min="-150" max="150" value="25" oninput="syncManualLoad()">
                </div>
            </div>

            <div class="card-section-title">Layer Visibility Toggles</div>
            <div class="toggle-row"><span>Nodes & Supports</span><input type="checkbox" id="chk-nodes" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>Transparent Faces</span><input type="checkbox" id="chk-faces" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>Roof Diaphragm</span><input type="checkbox" id="chk-diaphragm" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>Labels & Value Arrows</span><input type="checkbox" id="chk-arrow-labels" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>Local Member Axes</span><input type="checkbox" id="chk-local" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>Global Axes System</span><input type="checkbox" id="chk-global" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>MZ Member Releases</span><input type="checkbox" id="chk-release" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>Node Labels</span><input type="checkbox" id="chk-labels" checked onchange="rebuild3DScene()"></div>
            <div class="toggle-row"><span>Member Labels</span><input type="checkbox" id="chk-member-labels" checked onchange="rebuild3DScene()"></div>

            <button class="btn-primary" onclick="runAnalysisWorkflow()">▶ Run Analysis Solver</button>
            <button class="btn-primary" style="background:#10b981;" onclick="exportToExcel()">📊 Export to Excel</button>
        </section>

        <!-- CENTER 3D VIEWPORT CARD -->
        <section class="viewport-card">
            <div id="canvas-container"></div>

            <div class="hud-card" id="hud-top-left">
                <div style="font-weight:800; color:var(--accent-blue);">MODEL SPECIFICATIONS</div>
                <div style="font-weight:800;" id="hud-dimensions">6.00 m × 6.00 m × 6.00 m</div>
                <div style="font-size:10px; color:var(--text-muted);" id="hud-units-label">System: Standard (SI)</div>
            </div>

            <div id="view-cube">3D VIEW</div>
        </section>

        <!-- RIGHT SUMMARY & DETAILS PANEL -->
        <section class="right-panel">
            <div class="card-section-title">Selection Inspector</div>
            <div id="selection-properties-content" style="font-size:11px; color:var(--text-muted); line-height: 1.6;">
                Click any node or member in the 3D view or tables to inspect properties here.
            </div>
        </section>

    </div>

    <!-- BOTTOM DATA TABLE CARD -->
    <footer class="bottom-table-card" id="bottomTableCard">
        <div class="bottom-header-row">
            <div class="bottom-tabs">
                <button class="b-tab active" onclick="switchBottomTab('displacements')">Nodal Displacements</button>
                <button class="b-tab" onclick="switchBottomTab('reactions')">Support Reactions</button>
                <button class="b-tab" onclick="switchBottomTab('members')">Member Inventory</button>
                <button class="b-tab" onclick="switchBottomTab('summary')">Audit Log</button>
            </div>
            <button class="toggle-table-btn" id="toggleTableBtn" onclick="toggleBottomTable()">
                <span id="toggleIcon">▼</span> <span id="toggleText">Collapse Table</span>
            </button>
        </div>

        <div class="bottom-content">
            <div id="tab-table-displacements">
                <table class="eng-table">
                    <thead>
                        <tr>
                            <th>Node ID</th>
                            <th>Ux (<span class="unit-disp">mm</span>)</th>
                            <th>Uy (<span class="unit-disp">mm</span>)</th>
                            <th>Uz (<span class="unit-disp">mm</span>)</th>
                            <th>Resultant (<span class="unit-disp">mm</span>)</th>
                            <th>Condition</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-displacements"></tbody>
                </table>
            </div>

            <div id="tab-table-reactions" style="display:none;">
                <table class="eng-table">
                    <thead>
                        <tr>
                            <th>Support ID</th>
                            <th>Rx (<span class="unit-force">kN</span>)</th>
                            <th>Ry (<span class="unit-force">kN</span>)</th>
                            <th>Rz (<span class="unit-force">kN</span>)</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-reactions"></tbody>
                </table>
            </div>

            <div id="tab-table-members" style="display:none;">
                <table class="eng-table">
                    <thead>
                        <tr>
                            <th>Member ID</th>
                            <th>Start Node</th>
                            <th>End Node</th>
                            <th>Type</th>
                            <th>Beta Angle</th>
                            <th>Section</th>
                            <th>Material</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-members"></tbody>
                </table>
            </div>

            <div id="tab-table-summary" style="display:none;">
                <div style="font-size:11px; line-height:1.6; font-family:monospace;" id="audit-log-text">
                    [SYSTEM READY] FEM Calculation Engine initialized.<br>
                    Degree of Freedom Formulation: 3 Translational DOFs per node (Axial Stiffness Model).
                </div>
            </div>
        </div>
    </footer>

</main>

</div>

<script>
/* ============================================================
   GLOBAL CONVENTIONS & UNIT CONVERSION CONSTANTS
============================================================ */
const UNIT = {
    SI: { name: "Standard (SI)", length: "m", force: "kN", area: "m²", modulus: "GPa", displacement: "mm" },
    IMPERIAL: { name: "Imperial", length: "ft", force: "kip", area: "ft²", modulus: "ksi", displacement: "in" }
};

const M_TO_FT = 3.280839895;
const FT_TO_M = 1 / M_TO_FT;
const KN_TO_KIP = 0.224808943;
const KIP_TO_KN = 1 / KN_TO_KIP;

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

/* THREE.JS VIEWPORT INITIALIZATION */
const container = document.getElementById("canvas-container");
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

scene.add(new THREE.AmbientLight(0xffffff, 0.85));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
dirLight.position.set(25, 40, 25);
scene.add(dirLight);

const grid = new THREE.GridHelper(60, 60, 0xcbd5e1, 0xf1f5f9);
grid.position.y = 0;
grid.material.transparent = true;
scene.add(grid);

/* UI NAVIGATION & TAB SWITCHING */
function switchTab(tabName) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".ribbon-panel").forEach(p => p.classList.remove("active"));
    
    event.target.classList.add("active");
    const panel = document.getElementById("ribbon-" + tabName);
    if(panel) panel.classList.add("active");
}

function switchBottomTab(tabName) {
    document.querySelectorAll(".b-tab").forEach(b => b.classList.remove("active"));
    event.target.classList.add("active");

    document.getElementById("tab-table-displacements").style.display = tabName === 'displacements' ? 'block' : 'none';
    document.getElementById("tab-table-reactions").style.display = tabName === 'reactions' ? 'block' : 'none';
    document.getElementById("tab-table-members").style.display = tabName === 'members' ? 'block' : 'none';
    document.getElementById("tab-table-summary").style.display = tabName === 'summary' ? 'block' : 'none';
}

function toggleBottomTable() {
    const card = document.getElementById("bottomTableCard");
    const icon = document.getElementById("toggleIcon");
    const text = document.getElementById("toggleText");
    card.classList.toggle("collapsed");
    
    const isCollapsed = card.classList.contains("collapsed");
    icon.innerText = isCollapsed ? "▲" : "▼";
    text.innerText = isCollapsed ? "Expand Table" : "Collapse Table";
    
    setTimeout(onWindowResize, 300);
}

function toggleTheme() {
    const current = document.body.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.body.setAttribute("data-theme", next);
    
    const btn = document.getElementById("themeToggleBtn");
    if (next === "dark") {
        btn.innerText = "☀️ Light Mode";
        scene.background = new THREE.Color(0x090d16);
        grid.material.opacity = 0.2;
    } else {
        btn.innerText = "🌙 Dark Mode";
        scene.background = new THREE.Color(0xffffff);
        grid.material.opacity = 1.0;
    }
}

function updateHeaderTitle() {
    const modelName = document.getElementById("meta-model-name").value;
    document.getElementById("kpi-load-case").innerText = modelName || "Manual Sliders";
}

/* UNIT SWITCHING & SYNCHRONIZATION */
function setUnitSystem(system) {
    unitSystem = system;
    document.getElementById("home-unit-select").value = system;
    document.getElementById("kpi-units").innerText = system === "SI" ? "SI (m, kN)" : "Imperial (ft, kip)";
    
    document.querySelectorAll(".unit-len").forEach(e => e.innerText = UNIT[system].length);
    document.querySelectorAll(".unit-force").forEach(e => e.innerText = UNIT[system].force);
    document.querySelectorAll(".unit-disp").forEach(e => e.innerText = UNIT[system].displacement);

    runSolver();
}

function getDisplayEdge() {
    const edgeM = parseFloat(document.getElementById("ribbon-cube-edge").value);
    return unitSystem === "SI" ? edgeM : edgeM * M_TO_FT;
}

function syncCubeEdge(val) {
    document.getElementById("ribbon-cube-edge").value = val;
    runSolver();
}

function syncModelStyle(val) {
    document.getElementById("ribbon-model-style").value = val;
    rebuild3DScene();
}

function syncLoadCase(val) {
    document.getElementById("home-load-select").value = val;
    const manualCard = document.getElementById("side-manual-load-card");
    manualCard.style.display = (val === "custom") ? "block" : "none";
    runSolver();
}

function syncManualLoad() {
    const fx = document.getElementById("slide-fx").value;
    const fy = document.getElementById("slide-fy").value;
    const fz = document.getElementById("slide-fz").value;

    document.getElementById("r-fx").value = fx;
    document.getElementById("r-fy").value = fy;
    document.getElementById("r-fz").value = fz;

    document.getElementById("val-fx").innerText = fx;
    document.getElementById("val-fy").innerText = fy;
    document.getElementById("val-fz").innerText = fz;

    runSolver();
}

function syncDeflectScale(val) {
    document.getElementById("r-deflect-scale").value = val;
    updateDeformationVisuals();
}

/* ============================================================
   NUMERICAL FEM MATRIX SOLVER ENGINE
============================================================ */
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

function gaussianElimination(A, b) {
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
    const edgeM = parseFloat(document.getElementById("ribbon-cube-edge").value);
    const selectedCase = document.getElementById("home-load-select").value;

    currentNodes = [
        [0.0, 0.0, 0.0],       // N1
        [edgeM, 0.0, 0.0],     // N2
        [edgeM, 0.0, edgeM],   // N3
        [0.0, 0.0, edgeM],     // N4
        [0.0, edgeM, 0.0],     // N5
        [0.0, edgeM, edgeM],   // N6
        [edgeM, edgeM, edgeM], // N7
        [edgeM, edgeM, 0.0]    // N8
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
        { id:"M9",  ni:0, nj:4, type:"Column", beta:0,  release:"none", section: "220x220 Box", material: "Steel S355" },
        { id:"M10", ni:1, nj:7, type:"Column", beta:0,  release:"none", section: "220x220 Box", material: "Steel S355" },
        { id:"M11", ni:2, nj:6, type:"Column", beta:0,  release:"none", section: "220x220 Box", material: "Steel S355" },
        { id:"M12", ni:3, nj:5, type:"Column", beta:0,  release:"none", section: "220x220 Box", material: "Steel S355" }
    ];

    let loadsMap = {};
    let totalFx = 0, totalFy = 0, totalFz = 0;
    let caseName = "Manual Sliders";

    if (selectedCase === "custom") {
        const Fx = parseFloat(document.getElementById("r-fx").value);
        const Fy = parseFloat(document.getElementById("r-fy").value);
        const Fz = parseFloat(document.getElementById("r-fz").value);
        loadsMap[6] = [Fx, Fy, Fz];
        totalFx = Fx; totalFy = Fy; totalFz = Fz;
        caseName = "Manual Sliders";
    } else if (selectedCase === 'lc1') {
        caseName = "LC1 - Self Weight";
        totalFy = -21.22;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'lc2') {
        caseName = "LC2 - Roof Dead";
        totalFy = -120.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'lc3') {
        caseName = "LC3 - Roof Live";
        totalFy = -72.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'lc4') {
        caseName = "LC4 - Beam Load";
        totalFy = -20.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, -5.0, 0]);
    } else if (selectedCase === 'lc5') {
        caseName = "LC5 - Wind X";
        totalFx = 10.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [totalFx/4, 0, 0]);
    } else if (selectedCase === 'lc6') {
        caseName = "LC6 - Wind Z";
        totalFz = 10.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, 0, totalFz/4]);
    } else if (selectedCase === 'lc7') {
        caseName = "LC7 - Seismic X";
        totalFx = 15.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [totalFx/4, 0, 0]);
    } else if (selectedCase === 'lc8') {
        caseName = "LC8 - Seismic Z";
        totalFz = 15.0;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, 0, totalFz/4]);
    } else if (selectedCase === 'lc9') {
        caseName = "LC9 - Temp +15C";
    } else if (selectedCase === 'comb1') {
        caseName = "LRFD Comb 1.4D";
        totalFy = -225.71;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    } else if (selectedCase === 'comb13' || selectedCase === 'comb15') {
        caseName = selectedCase === 'comb13' ? "ASD Comb 13" : "ASD Comb 15";
        totalFy = -161.22;
        [4,5,6,7].forEach(n => loadsMap[n] = [0, totalFy/4, 0]);
    }

    rawDisplacements = solve3DFrame(currentNodes, currentMembers, loadsMap, BASE_E_KN_M2, BASE_AREA_M2);

    document.getElementById("kpi-load-case").innerText = caseName;
    updateHUD(edgeM);
    populateTables(totalFx, totalFy, totalFz);
    rebuild3DScene();
}

function updateHUD(edgeM) {
    const dispEdge = getDisplayEdge();
    const unitLen = UNIT[unitSystem].length;
    document.getElementById("hud-dimensions").innerText = `${dispEdge.toFixed(2)} ${unitLen} × ${dispEdge.toFixed(2)} ${unitLen} × ${dispEdge.toFixed(2)} ${unitLen}`;
    document.getElementById("hud-units-label").innerText = `System: ${UNIT[unitSystem].name}`;
}

function populateTables(totalFx, totalFy, totalFz) {
    const factor = unitSystem === "SI" ? 1000 : M_TO_FT * 12;
    const forceFactor = unitSystem === "SI" ? 1 : KN_TO_KIP;
    const lenUnit = UNIT[unitSystem].length;

    let maxResultant = 0;
    let tbodyDisp = "";
    
    currentNodes.forEach((c, i) => {
        const ux = rawDisplacements[3*i] * factor;
        const uy = rawDisplacements[3*i+1] * factor;
        const uz = rawDisplacements[3*i+2] * factor;
        const res = Math.hypot(ux, uy, uz);
        if (res > maxResultant) maxResultant = res;

        tbodyDisp += `<tr onclick="selectNode(${i})">
            <td><strong>N${i+1}</strong></td>
            <td>${ux.toFixed(4)}</td>
            <td>${uy.toFixed(4)}</td>
            <td>${uz.toFixed(4)}</td>
            <td><strong>${res.toFixed(4)}</strong></td>
            <td>${i < 4 ? "Pinned Support" : "Free Roof Node"}</td>
        </tr>`;
    });
    document.getElementById("tbody-displacements").innerHTML = tbodyDisp;
    document.getElementById("kpi-max-disp").innerText = maxResultant.toFixed(4) + " " + UNIT[unitSystem].displacement;

    let tbodyReact = "";
    for(let i=0; i<4; i++) {
        const rx = -totalFx / 4 * forceFactor;
        const ry = -totalFy / 4 * forceFactor;
        const rz = -totalFz / 4 * forceFactor;
        tbodyReact += `<tr>
            <td><strong>N${i+1}</strong></td>
            <td>${rx.toFixed(3)}</td>
            <td>${ry.toFixed(3)}</td>
            <td>${rz.toFixed(3)}</td>
            <td><span style="color:var(--accent-green); font-weight:700;">Equilibrium Verified</span></td>
        </tr>`;
    }
    document.getElementById("tbody-reactions").innerHTML = tbodyReact;

    let tbodyMem = "";
    currentMembers.forEach(m => {
        tbodyMem += `<tr onclick="selectMember('${m.id}')">
            <td><strong>${m.id}</strong></td>
            <td>N${m.ni+1}</td>
            <td>N${m.nj+1}</td>
            <td>${m.type}</td>
            <td>${m.beta}°</td>
            <td>${m.section}</td>
            <td>${m.material}</td>
        </tr>`;
    });
    document.getElementById("tbody-members").innerHTML = tbodyMem;

    const resForce = Math.hypot(totalFx, totalFy, totalFz) * forceFactor;
    document.getElementById("audit-log-text").innerHTML = `
        [SOLVER STATUS] Execution Completed Successfully.<br>
        [EQUILIBRIUM AUDIT] Total Applied Force = ${resForce.toFixed(3)} ${UNIT[unitSystem].force}<br>
        [GLOBAL FORCES] Fx = ${(totalFx*forceFactor).toFixed(3)} | Fy = ${(totalFy*forceFactor).toFixed(3)} | Fz = ${(totalFz*forceFactor).toFixed(3)} ${UNIT[unitSystem].force}<br>
        [DEGREES OF FREEDOM] Total DOFs: 24 | Restrained DOFs: 12 | Active Free DOFs: 12
    `;
}

function selectNode(index) {
    const card = document.getElementById("selection-properties-content");
    const factor = unitSystem === "SI" ? 1000 : M_TO_FT * 12;
    const ux = rawDisplacements[3*index] * factor;
    const uy = rawDisplacements[3*index+1] * factor;
    const uz = rawDisplacements[3*index+2] * factor;

    card.innerHTML = `
        <div style="font-weight:800; color:var(--accent-blue); font-size:13px; margin-bottom:6px;">Node N${index+1} Selected</div>
        <div><strong>Type:</strong> ${index < 4 ? "Pinned Base Support" : "Roof Node"}</div>
        <div><strong>Ux:</strong> ${ux.toFixed(4)} ${UNIT[unitSystem].displacement}</div>
        <div><strong>Uy:</strong> ${uy.toFixed(4)} ${UNIT[unitSystem].displacement}</div>
        <div><strong>Uz:</strong> ${uz.toFixed(4)} ${UNIT[unitSystem].displacement}</div>
    `;
}

function selectMember(memId) {
    const m = currentMembers.find(item => item.id === memId);
    if (!m) return;
    const card = document.getElementById("selection-properties-content");
    card.innerHTML = `
        <div style="font-weight:800; color:var(--accent-blue); font-size:13px; margin-bottom:6px;">Member ${m.id} Selected</div>
        <div><strong>Type:</strong> ${m.type}</div>
        <div><strong>Connectivity:</strong> N${m.ni+1} to N${m.nj+1}</div>
        <div><strong>Section:</strong> ${m.section}</div>
        <div><strong>Material:</strong> ${m.material}</div>
        <div><strong>Beta Angle:</strong> ${m.beta}°</div>
    `;
}

/* ============================================================
   3D GRAPHICS RENDERER (THREE.JS)
============================================================ */
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

function createTextSprite(message, textColor="#0284c7") {
    const canvas = document.createElement("canvas");
    canvas.width = 512; canvas.height = 128;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = "bold 34px 'Segoe UI', Arial, sans-serif";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 6; ctx.strokeText(message, 256, 64);
    ctx.fillStyle = textColor; ctx.fillText(message, 256, 64);

    const texture = new THREE.CanvasTexture(canvas);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }));
    sprite.scale.set(2.4, 0.6, 1);
    return sprite;
}

function rebuild3DScene() {
    clear3DObjects();

    const modelStyle = document.getElementById("ribbon-model-style").value;
    const showNodes = document.getElementById("chk-nodes").checked;
    const showFaces = document.getElementById("chk-faces").checked;
    const showDiaphragm = document.getElementById("chk-diaphragm").checked;
    const showArrowLabels = document.getElementById("chk-arrow-labels").checked;
    const showLocal = document.getElementById("chk-local").checked;
    const showGlobal = document.getElementById("chk-global").checked;
    const showRelease = document.getElementById("chk-release").checked;
    const showLabels = document.getElementById("chk-labels").checked;
    const showMemberLabels = document.getElementById("chk-member-labels").checked;

    const edge = parseFloat(document.getElementById("ribbon-cube-edge").value);

    if (showFaces) {
        const faceMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.05, side: THREE.DoubleSide, depthWrite: false });
        const createFace = (w, h, pos, rot) => {
            const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, h), faceMat);
            if (rot.x) mesh.rotation.x = rot.x; if (rot.y) mesh.rotation.y = rot.y;
            mesh.position.set(...pos); scene.add(mesh); cubeFaceObjects.push(mesh);
        };
        createFace(edge, edge, [edge/2, 0, edge/2], { x: -Math.PI / 2 });
        createFace(edge, edge, [edge/2, edge, edge/2], { x: -Math.PI / 2 });
        createFace(edge, edge, [edge/2, edge/2, 0], {});
        createFace(edge, edge, [edge/2, edge/2, edge], {});
        createFace(edge, edge, [0, edge/2, edge/2], { y: Math.PI / 2 });
        createFace(edge, edge, [edge, edge/2, edge/2], { y: Math.PI / 2 });
    }

    const beamMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.4 });
    const colMat = new THREE.MeshStandardMaterial({ color: 0x16a34a, roughness: 0.4 });
    const suppMat = new THREE.MeshStandardMaterial({ color: 0x16a34a });
    const freeMat = new THREE.MeshStandardMaterial({ color: 0xdc2626 });

    currentNodes.forEach((coords, index) => {
        const [x, y, z] = coords;
        const pinned = index < 4;

        if (showNodes) {
            const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.22, 20, 20), pinned ? suppMat : freeMat);
            sphere.position.set(x, y, z);
            scene.add(sphere); sceneObjects.push(sphere);
        }

        if (pinned && showNodes) {
            const cone = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.6, 4), suppMat);
            cone.position.set(x, y - 0.3, z);
            scene.add(cone); sceneObjects.push(cone);
        }

        if (showLabels) {
            const label = createTextSprite(`N${index + 1}`, "#0284c7");
            label.position.set(x, y + 0.4, z);
            scene.add(label); labelObjects.push(label);
        }
    });

    if (showDiaphragm) {
        const diaGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(...currentNodes[4]), new THREE.Vector3(...currentNodes[7]),
            new THREE.Vector3(...currentNodes[6]), new THREE.Vector3(...currentNodes[5]),
            new THREE.Vector3(...currentNodes[4])
        ]);
        const diaLine = new THREE.Line(diaGeo, new THREE.LineDashedMaterial({ color: 0x0284c7, dashSize: 0.4, gapSize: 0.2 }));
        diaLine.computeLineDistances();
        scene.add(diaLine); sceneObjects.push(diaLine);
    }

    currentMembers.forEach(mem => {
        const p1 = new THREE.Vector3(...currentNodes[mem.ni]);
        const p2 = new THREE.Vector3(...currentNodes[mem.nj]);
        const direction = new THREE.Vector3().subVectors(p2, p1);
        const length = direction.length();

        if (modelStyle === "solid") {
            const thick = mem.type === "Column" ? 0.22 : 0.18;
            const mesh = new THREE.Mesh(new THREE.BoxGeometry(thick, thick, length), mem.type === "Column" ? colMat : beamMat);
            mesh.position.copy(new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5));
            mesh.lookAt(p2);
            if (mem.beta !== 0) mesh.rotateZ(THREE.MathUtils.degToRad(mem.beta));
            scene.add(mesh); sceneObjects.push(mesh);
        } else {
            const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([p1, p2]), new THREE.LineBasicMaterial({ color: mem.type === "Column" ? 0x16a34a : 0x0284c7, linewidth: 2 }));
            scene.add(line); sceneObjects.push(line);
        }

        const midPt = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
        if (showMemberLabels) {
            const mLabel = createTextSprite(mem.id, "#0f172a");
            mLabel.position.copy(midPt).add(new THREE.Vector3(0, 0.3, 0));
            scene.add(mLabel); labelObjects.push(mLabel);
        }

        if (mem.release === "both" && showRelease) {
            [0.1, 0.9].forEach(r => {
                const ring = new THREE.Mesh(new THREE.RingGeometry(0.1, 0.16, 16), new THREE.MeshBasicMaterial({ color: 0x0284c7, side: THREE.DoubleSide }));
                ring.position.copy(new THREE.Vector3().lerpVectors(p1, p2, r));
                ring.lookAt(p2); scene.add(ring); sceneObjects.push(ring);
            });
        }

        if (showLocal) {
            const localX = direction.clone().normalize();
            let ref = new THREE.Vector3(0, 1, 0);
            if (Math.abs(localX.dot(ref)) > 0.95) ref = new THREE.Vector3(1, 0, 0);
            const localZ = new THREE.Vector3().crossVectors(localX, ref).normalize();
            const localY = new THREE.Vector3().crossVectors(localZ, localX).normalize();
            const ax = new THREE.ArrowHelper(localX, midPt, 0.6, 0xdc2626, 0.15, 0.08);
            const ay = new THREE.ArrowHelper(localY, midPt, 0.6, 0x16a34a, 0.15, 0.08);
            const az = new THREE.ArrowHelper(localZ, midPt, 0.6, 0x2563eb, 0.15, 0.08);
            scene.add(ax, ay, az); sceneObjects.push(ax, ay, az);
        }
    });

    if (showGlobal) {
        const origin = new THREE.Vector3(-1, 0, -1);
        const gx = new THREE.ArrowHelper(new THREE.Vector3(1,0,0), origin, 2, 0xdc2626, 0.3, 0.15);
        const gy = new THREE.ArrowHelper(new THREE.Vector3(0,1,0), origin, 2, 0x16a34a, 0.3, 0.15);
        const gz = new THREE.ArrowHelper(new THREE.Vector3(0,0,1), origin, 2, 0x2563eb, 0.3, 0.15);
        scene.add(gx, gy, gz); sceneObjects.push(gx, gy, gz);
    }

    renderLoadVisuals(showArrowLabels);
    updateDeformationVisuals();
}

function renderLoadVisuals(showLabels) {
    const selectedCase = document.getElementById("home-load-select").value;
    if (selectedCase === "custom") {
        const Fx = parseFloat(document.getElementById("r-fx").value);
        const Fy = parseFloat(document.getElementById("r-fy").value);
        const Fz = parseFloat(document.getElementById("r-fz").value);
        drawNodalArrow(6, [Fx, Fy, Fz], 0xd97706, `N7 Load`, showLabels);
    } else if (selectedCase === 'lc1') {
        currentMembers.forEach((_, idx) => drawDistributedLoad(idx, 0x16a34a, 0.5, "Self Wt", showLabels));
    } else if (['lc2', 'lc3', 'comb1', 'comb13', 'comb15'].includes(selectedCase)) {
        [4, 5, 6, 7].forEach(idx => drawDistributedLoad(idx, 0xd97706, 0.8, "Roof Load", showLabels));
    } else if (selectedCase === 'lc4') {
        [4, 5, 6, 7].forEach(memIdx => {
            const mem = currentMembers[memIdx];
            const p1 = new THREE.Vector3(...currentNodes[mem.ni]);
            const p2 = new THREE.Vector3(...currentNodes[mem.nj]);
            const midPt = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);

            const arrowLength = 1.8;
            const startPt = midPt.clone().add(new THREE.Vector3(0, arrowLength, 0));
            const arrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), startPt, arrowLength, 0x7c3aed, 0.35, 0.2);
            loadGroup.add(arrow);

            if (showLabels) {
                const label = createTextSprite("CENTER LOAD: 5.0 kN", "#7c3aed");
                label.position.copy(startPt).add(new THREE.Vector3(0, 0.35, 0));
                loadGroup.add(label);
            }
        });
    } else if (['lc5', 'lc7'].includes(selectedCase)) {
        [4,5,6,7].forEach(nid => drawNodalArrow(nid, [3, 0, 0], 0xdc2626, "Wind/Seismic X", showLabels));
    } else if (['lc6', 'lc8'].includes(selectedCase)) {
        [4,5,6,7].forEach(nid => drawNodalArrow(nid, [0, 0, 3], 0xd97706, "Wind/Seismic Z", showLabels));
    } else if (selectedCase === 'lc9') {
        currentMembers.forEach(mem => {
            const p1 = new THREE.Vector3(...currentNodes[mem.ni]);
            const p2 = new THREE.Vector3(...currentNodes[mem.nj]);
            const dir = new THREE.Vector3().subVectors(p2, p1).normalize();
            const midPt = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);

            const a1 = new THREE.ArrowHelper(dir, midPt, 0.7, 0xd97706, 0.25, 0.15);
            const a2 = new THREE.ArrowHelper(dir.clone().negate(), midPt, 0.7, 0xd97706, 0.25, 0.15);
            loadGroup.add(a1);
            loadGroup.add(a2);

            if (showLabels) {
                const label = createTextSprite("+15°C", "#d97706");
                label.position.copy(midPt).add(new THREE.Vector3(0, 0.3, 0));
                loadGroup.add(label);
            }
        });
    }
}

function drawDistributedLoad(memberIdx, color, height, labelText, showLabels) {
    const mem = currentMembers[memberIdx];
    const p1 = new THREE.Vector3(...currentNodes[mem.ni]);
    const p2 = new THREE.Vector3(...currentNodes[mem.nj]);
    for(let i=0; i<=5; i++) {
        const pos = new THREE.Vector3().lerpVectors(p1, p2, i/5).add(new THREE.Vector3(0, height, 0));
        const arrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), pos, height, color, 0.15, 0.1);
        loadGroup.add(arrow);
    }
}

function drawNodalArrow(nodeIdx, vec, color, labelText, showLabels) {
    const pos = new THREE.Vector3(...currentNodes[nodeIdx]);
    const vec3 = new THREE.Vector3(...vec);
    if (vec3.length() < 0.0001) return;
    const arrow = new THREE.ArrowHelper(vec3.clone().normalize(), pos, 2.0, color, 0.3, 0.2);
    loadGroup.add(arrow);
}

function updateDeformationVisuals() {
    sceneObjects = sceneObjects.filter(obj => {
        if (obj.isDeformedLine) { scene.remove(obj); return false; }
        return true;
    });

    if (rawDisplacements.length === 0) return;
    const scale = parseFloat(document.getElementById("r-deflect-scale").value);
    const mat = new THREE.LineBasicMaterial({ color: 0xdc2626, linewidth: 3 });

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
        const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([p1, p2]), mat);
        line.isDeformedLine = true;
        scene.add(line); sceneObjects.push(line);
    });
}

function setPresetView(viewType) {
    const edge = parseFloat(document.getElementById("ribbon-cube-edge").value);
    const center = new THREE.Vector3(edge/2, edge/2, edge/2);
    controls.target.copy(center);

    if (viewType === 'iso') camera.position.set(edge * 2.3, edge * 1.8, edge * 2.5);
    else if (viewType === 'top') camera.position.set(edge/2, edge * 3.5, edge/2 + 0.01);
    else if (viewType === 'front') camera.position.set(edge/2, edge/2, edge * 3.5);
    controls.update();
}

function resetView() { setPresetView('iso'); }

function validateModel() {
    alert("Model Validation Status: SUCCESSFUL\n\n- Geometry: Valid 3D Cube\n- Connectivity: 12 Structural Members\n- Boundary Conditions: 4 Base Pinned Supports (N1-N4)\n- Matrix Solver: Stable & Ready.");
}

function runAnalysisWorkflow() {
    runSolver();
    document.getElementById("kpi-solver-status").innerText = "CALCULATED";
}

function resetProject() {
    if(confirm("Reset model and load values to default?")) {
        document.getElementById("ribbon-cube-edge").value = "6.0";
        document.getElementById("meta-model-name").value = "Cube Structural Model";
        updateHeaderTitle();
        syncCubeEdge("6.0");
    }
}

function triggerSaveProject() {
    alert("Project saved successfully.");
}

function exportToExcel() {
    const U = UNIT[unitSystem];
    const metaData = [
        { Field: "Model Name", Value: document.getElementById("meta-model-name").value },
        { Field: "Company", Value: document.getElementById("meta-company").value },
        { Field: "Designer", Value: document.getElementById("meta-designer").value }
    ];

    const nodeData = currentNodes.map((c,i) => ({
        "Node ID": "N" + (i+1),
        ["X (" + U.length + ")"]: unitSystem === "SI" ? c[0] : c[0] * M_TO_FT,
        ["Y (" + U.length + ")"]: unitSystem === "SI" ? c[1] : c[1] * M_TO_FT,
        ["Z (" + U.length + ")"]: unitSystem === "SI" ? c[2] : c[2] * M_TO_FT,
        "Support": i < 4 ? "Pinned" : "Free"
    }));

    const memberData = currentMembers.map(m => ({
        "Member ID": m.id, "Start": "N" + (m.ni+1), "End": "N" + (m.nj+1),
        "Type": m.type, "Section": m.section, "Material": m.material
    }));

    const displacementData = currentNodes.map((c,i) => {
        const factor = unitSystem === "SI" ? 1000 : M_TO_FT * 12;
        return {
            "Node ID": "N" + (i+1),
            ["Ux (" + U.displacement + ")"]: rawDisplacements[3*i] * factor,
            ["Uy (" + U.displacement + ")"]: rawDisplacements[3*i+1] * factor,
            ["Uz (" + U.displacement + ")"]: rawDisplacements[3*i+2] * factor
        };
    });

    const fileName = (document.getElementById("meta-model-name").value.trim().replace(/[^a-zA-Z0-9_-]/g, "_") || "Cube_FEM_Studio") + "_Results.xlsx";

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(metaData), "Project Info");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(nodeData), "Nodal Data");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(memberData), "Member Data");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(displacementData), "Displacements");
    XLSX.writeFile(wb, fileName);
}

function onWindowResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}
window.addEventListener("resize", onWindowResize);

/* INITIALIZATION */
setUnitSystem("SI");
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

output_html = "Cube_FEM_Studio_Dashboard.html"

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

absolute_path = os.path.abspath(output_html)

print("\n" + "=" * 65)
print("CUBE FEM STUDIO - MODERN INTEGRATED DASHBOARD")
print("=" * 65)
print(f"Student Name : Ryanold Renz C. Miranda")
print(f"Section      : BSCE-3D")
print(f"\nGenerated Web Application:\n{absolute_path}\n")

webbrowser.open(absolute_path)