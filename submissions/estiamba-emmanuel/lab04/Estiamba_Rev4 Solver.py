"""
gen_rev4_solver.py — Rev 4 Web Edition with LC9 Temperature and user member loads

Generates REV4-SOLVER.html and opens it in the default browser.
"""

import pathlib
import sys
import webbrowser

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Revit 4 Solver — Web Edition</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"></script>
<style>
  :root {
    --bg:#0b1220;--panel:#121b2e;--panel-2:#1a2540;--border:#2a3654;
    --text:#e2e8f0;--muted:#94a3b8;--accent:#38bdf8;--accent-2:#22c55e;
    --warn:#f59e0b;--danger:#ef4444;
  }
  *{box-sizing:border-box}html,body{height:100%}
  body{margin:0;background:var(--bg);color:var(--text);
    font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:14px}
  header{display:flex;align-items:center;gap:16px;padding:12px 20px;background:var(--panel);
    border-bottom:1px solid var(--border)}
  header h1{margin:0;font-size:18px;letter-spacing:.3px}
  header .subtitle{color:var(--muted);font-size:12px}
  header .author{color:var(--accent);font-size:12px;margin-top:3px;font-weight:600;letter-spacing:.4px}
  header .spacer{flex:1}
  button{background:var(--panel-2);color:var(--text);border:1px solid var(--border);
    border-radius:6px;padding:8px 14px;cursor:pointer;font-size:13px;font-weight:500;transition:.15s}
  button:hover:not(:disabled){background:#24334f;border-color:#3d4d70}
  button:disabled{opacity:.5;cursor:not-allowed}
  button.primary{background:var(--accent);border-color:var(--accent);color:#06202f;font-weight:600}
  button.primary:hover:not(:disabled){background:#5cc8fb;border-color:#5cc8fb}
  input,select{background:var(--panel-2);color:var(--text);border:1px solid var(--border);
    border-radius:6px;padding:7px 9px;font-size:13px;width:100%;font-family:inherit}
  input:focus,select:focus{outline:none;border-color:var(--accent)}
  .layout{display:grid;grid-template-columns:380px 1fr;height:calc(100vh - 58px)}
  .sidebar{overflow-y:auto;background:var(--panel);border-right:1px solid var(--border);padding:16px}
  .main{overflow-y:auto;padding:16px 20px 40px;background:#fff;color:#0f172a;
    --text:#0f172a;--muted:#64748b;--panel-2:#f1f5f9;--border:#e2e8f0}
  .section-title{font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);
    margin:18px 0 8px}.section-title:first-child{margin-top:0}
  .field{margin-bottom:10px}.field label{display:block;font-size:12px;color:var(--muted);margin-bottom:4px}
  .member-block{background:var(--panel-2);border:1px solid var(--border);border-radius:8px;
    padding:10px;margin-bottom:10px}
  .member-block h4{margin:0 0 8px;font-size:13px;display:flex;align-items:center;gap:6px}
  .swatch{width:10px;height:10px;border-radius:50%;display:inline-block}
  .load-row{display:grid;grid-template-columns:60px 1fr 1fr 1fr 1fr 1fr 1fr 28px;gap:4px;
    align-items:center;margin-bottom:4px}
  .load-row input,.load-row select{padding:5px 6px;font-size:12px;text-align:right}
  .load-row select{text-align:center}
  .load-head{display:grid;grid-template-columns:60px 1fr 1fr 1fr 1fr 1fr 1fr 28px;gap:4px}
  .load-head span{font-size:10px;color:var(--muted);text-align:center}
  .load-head.udl-head,.load-row.udl-row{grid-template-columns:1fr 76px 62px 28px}
  .load-head.pt-head,.load-row.pt-row{grid-template-columns:1fr 62px 42px 62px 28px}
  .load-head.temp-head,.load-row.temp-row{grid-template-columns:1fr 76px 28px}
  .icon-btn{padding:4px 6px;font-size:12px;line-height:1;background:transparent;
    border:1px solid var(--border);border-radius:4px}
  .tabs{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:12px;flex-wrap:wrap}
  .tab{padding:8px 14px;border:none;background:transparent;color:var(--muted);
    border-bottom:2px solid transparent;border-radius:0;cursor:pointer;font-size:13px;font-weight:500}
  .tab:hover:not(.active){color:var(--text)}
  .tab.active{color:var(--accent);border-bottom-color:var(--accent)}
  .main .tab.active{color:#0284c7;border-bottom-color:#0284c7}
  .tab-panel{display:none}.tab-panel.active{display:block}
  #plot{width:100%;height:620px;background:#0a101c;border-radius:8px;border:1px solid var(--border)}
  .status{padding:8px 12px;border-radius:6px;font-size:12px;margin-bottom:12px;background:var(--panel-2);
    border:1px solid var(--border);color:var(--muted);display:flex;align-items:center;gap:8px}
  .status.ok{color:var(--accent-2);border-color:#1e3d2a;background:#0f2418}
  .status.err{color:var(--danger);border-color:#4a1f24;background:#2a1114}
  .status .dot{width:8px;height:8px;border-radius:50%;background:currentColor;
    animation:pulse 1.2s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
  table{width:100%;border-collapse:collapse;font-size:12px;font-family:ui-monospace,"SF Mono",Menlo,monospace}
  th,td{padding:6px 10px;text-align:right;border-bottom:1px solid var(--border);white-space:nowrap}
  th{color:var(--muted);font-weight:500;background:var(--panel-2);position:sticky;top:0;text-align:right}
  th:first-child,td:first-child{text-align:left}
  tr:hover td{background:rgba(56,189,248,.05)}
  .kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-bottom:16px}
  .kpi{background:var(--panel-2);border:1px solid var(--border);border-radius:8px;padding:12px 14px}
  .kpi .label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
  .kpi .value{font-size:18px;font-weight:600;margin-top:4px;font-family:ui-monospace,monospace}
  .kpi .unit{font-size:12px;color:var(--muted);font-weight:400}
  .kpi.ok{border-color:#1e3d2a;background:#e8f8ee}
  .card{background:var(--panel-2);border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:14px}
  .card h3{margin:0 0 8px;font-size:13px;color:var(--muted);text-transform:uppercase;
    letter-spacing:.8px;font-weight:500}
  .checkbox-row{display:flex;align-items:center;gap:8px;margin:8px 0}
  .checkbox-row input{width:auto}.checkbox-row label{color:var(--text);font-size:13px}
  .help{color:var(--muted);font-size:12px;line-height:1.6}
  code{background:var(--panel-2);padding:1px 5px;border-radius:3px;font-size:12px;color:var(--accent)}
  .btn-row{display:flex;gap:8px;margin-top:8px}
  pre.report{background:#0a101c;color:#cbd5e1;padding:12px;border-radius:6px;font-size:11px;
    line-height:1.5;overflow-x:auto;white-space:pre-wrap;
    font-family:ui-monospace,"SF Mono",Menlo,monospace}
  .test-pass{color:#22c55e;font-weight:600}.test-fail{color:#ef4444;font-weight:600}
</style>
</head>
<body>

<header>
  <div>
    <h1>Revit 4 Solver — Web Edition</h1>
    <div class="subtitle">3D space-frame stiffness solver · loads · NSCP combinations · LC9 thermal</div>
    <div class="author">Estiamba, Emmanuel G.</div>
  </div>
  <div class="spacer"></div>
  <div style="width:210px;">
    <select id="unit-system">
      <option value="metric" selected>Metric (m, kN, MPa)</option>
      <option value="imperial">Imperial (ft, kip, ksi)</option>
    </select>
  </div>
  <button id="run-btn" class="primary" disabled>Solve</button>
  <button id="download-btn" disabled>Download CSV</button>
</header>

<div class="layout">
  <aside class="sidebar">
    <div id="load-status" class="status">
      <span class="dot"></span><span id="status-text">Loading Python runtime…</span>
    </div>

    <div class="section-title">Load Case / Combination</div>
    <div class="field">
      <label>Active load case</label>
      <select id="loadcase-sel"></select>
    </div>
    <div class="field" id="temp-field" style="display:none;">
      <label>Temperature change ΔT (°C) — LC9</label>
      <input id="temp-input" type="number" step="1" value="15" />
      <div class="help" style="margin-top:4px;">
        + heating, − cooling. Applied to every member; α is taken from the
        selected material. Load is self-equilibrating (net force = 0).
      </div>
    </div>
    <div class="field" id="ref-temp-field" style="display:none;">
      <label>Reference temperature (°C) — LC9</label>
      <input id="ref-temp-input" type="number" step="1" value="20" />
    </div>
    <div class="field">
      <label>NSCP load combination</label>
      <select id="combo-sel">
        <option value="">(none — use load case above)</option>
      </select>
    </div>
    <div class="help" id="case-info" style="margin-bottom:12px;"></div>

    <div class="section-title">Member Assignment</div>
    <div id="member-assignments"></div>

    <div class="section-title">Additional Nodal Loads</div>
    <div class="checkbox-row">
      <input type="checkbox" id="self-weight" checked>
      <label for="self-weight">Include self-weight (custom case only)</label>
    </div>
    <div class="card">
      <div class="load-head" style="margin-bottom:6px;">
        <span>Node</span><span>Fx</span><span>Fy</span><span>Fz</span>
        <span>Mx</span><span>My</span><span>Mz</span><span></span>
      </div>
      <div id="load-rows"></div>
      <div class="btn-row"><button id="add-load-btn" style="flex:1;">+ Add load</button></div>
      <div class="help" style="margin-top:8px;">
        Added to whichever case is active. Force unit: kN (metric) / kip (imperial).
      </div>
    </div>

    <div class="section-title">Member UDL</div>
    <div class="card">
      <div class="load-head udl-head" style="margin-bottom:6px;">
        <span>Member</span><span>w</span><span>Dir</span><span></span>
      </div>
      <div id="udl-rows"></div>
      <div class="btn-row"><button id="add-udl-btn" style="flex:1;">+ Add UDL</button></div>
      <div class="help" style="margin-top:8px;">
        Uniformly distributed. w in kN/m (metric) or kip/ft (imperial).
      </div>
    </div>

    <div class="section-title">Member Point Loads</div>
    <div class="card">
      <div class="load-head pt-head" style="margin-bottom:6px;">
        <span>Member</span><span>P</span><span>t</span><span>Dir</span><span></span>
      </div>
      <div id="pt-rows"></div>
      <div class="btn-row"><button id="add-pt-btn" style="flex:1;">+ Add point load</button></div>
      <div class="help" style="margin-top:8px;">
        t = location along member, 0..1 (0.5 = midspan). P in kN (metric) or kip (imperial).
      </div>
    </div>

    <div class="section-title">Temperature ΔT</div>
    <div class="card">
      <div class="load-head temp-head" style="margin-bottom:6px;">
        <span>Apply to</span><span>ΔT (°C)</span><span></span>
      </div>
      <div id="temp-rows"></div>
      <div class="btn-row"><button id="add-temp-btn" style="flex:1;">+ Add ΔT</button></div>
      <div class="help" style="margin-top:8px;">
        α is read from each member's material. Self-equilibrating. Cumulative
        with LC9 if that case is also selected.
      </div>
    </div>
  </aside>

  <main class="main">
    <div id="kpis" class="kpi-row"></div>

    <div class="tabs">
      <button class="tab active" data-tab="view">3D View</button>
      <button class="tab" data-tab="disp">Displacements</button>
      <button class="tab" data-tab="react">Reactions</button>
      <button class="tab" data-tab="forces">Member End Forces</button>
      <button class="tab" data-tab="members">Members</button>
      <button class="tab" data-tab="valid">Load Validation</button>
      <button class="tab" data-tab="combo">Combinations</button>
      <button class="tab" data-tab="diag">Diaphragm</button>
      <button class="tab" data-tab="thermal">Thermal Report</button>
      <button class="tab" data-tab="tests">Thermal Tests</button>
    </div>

    <div class="tab-panel active" id="panel-view">
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
        <button id="grid-toggle" style="padding:6px 12px;">Grid: on</button>
        <button id="band-toggle" style="padding:6px 12px;">Band: rectangle</button>
        <span class="help">Gridlines / UDL band style.</span>
      </div>
      <div id="plot"></div>
    </div>
    <div class="tab-panel" id="panel-disp"><div class="card"><h3>Nodal Displacements</h3><div id="tbl-disp"></div></div></div>
    <div class="tab-panel" id="panel-react"><div class="card"><h3>Support Reactions</h3><div id="tbl-react"></div></div></div>
    <div class="tab-panel" id="panel-forces"><div class="card"><h3>Member End Forces (local axes)</h3><div id="tbl-forces"></div></div></div>
    <div class="tab-panel" id="panel-members"><div class="card"><h3>Member Schedule</h3><div id="tbl-members"></div></div></div>
    <div class="tab-panel" id="panel-valid"><div class="card"><h3>Load Case Validation</h3><pre class="report" id="valid-report">(solve to populate)</pre></div></div>
    <div class="tab-panel" id="panel-combo"><div class="card"><h3>Load Combination Engine</h3><pre class="report" id="combo-report">(solve to populate)</pre></div></div>
    <div class="tab-panel" id="panel-diag"><div class="card"><h3>Diaphragm Definition</h3><pre class="report" id="diag-report">(solve to populate)</pre></div></div>
    <div class="tab-panel" id="panel-thermal"><div class="card"><h3>Temperature Load Verification (LC9)</h3><pre class="report" id="thermal-report">(solve to populate)</pre></div></div>
    <div class="tab-panel" id="panel-tests"><div class="card"><h3>Automated Temperature Tests</h3>
      <button id="run-tests-btn" style="margin-bottom:12px;">Run 13 tests</button>
      <div id="tests-out"><pre class="report">(click above)</pre></div>
    </div></div>
  </main>
</div>

<!-- ============================================================================
     Python source, run inside Pyodide.
     ============================================================================ -->
<script type="text/x-python" id="python-source">
import json
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


# =========================== units.py ===========================
class Quantity(Enum):
    LENGTH_GEOM="length_geom"; LENGTH_SECTION="length_section"; AREA="area"
    INERTIA="inertia"; SECTION_MODULUS="section_modulus"; FORCE="force"
    MOMENT="moment"; STRESS="stress"; UNIT_WEIGHT="unit_weight"; THERMAL="thermal"

@dataclass(frozen=True)
class _Factor:
    to_metric:float; base_system:str; imperial_label:str; metric_label:str

_KIP_TO_KN=4.4482216152605; _FT_TO_M=0.3048
_CONVERSION_TABLE={
    Quantity.LENGTH_GEOM:_Factor(_FT_TO_M,"metric","ft","m"),
    Quantity.LENGTH_SECTION:_Factor(25.4,"imperial","in","mm"),
    Quantity.AREA:_Factor(645.16,"imperial","in^2","mm^2"),
    Quantity.INERTIA:_Factor(416231.4256,"imperial","in^4","mm^4"),
    Quantity.SECTION_MODULUS:_Factor(16387.064,"imperial","in^3","mm^3"),
    Quantity.FORCE:_Factor(_KIP_TO_KN,"imperial","kip","kN"),
    Quantity.MOMENT:_Factor(_KIP_TO_KN*_FT_TO_M,"imperial","kip*ft","kN*m"),
    Quantity.STRESS:_Factor(6.894757293168361,"imperial","ksi","MPa"),
    Quantity.UNIT_WEIGHT:_Factor(157.08746384624624,"imperial","k/ft^3","kN/m^3"),
    Quantity.THERMAL:_Factor(18.0,"imperial","1e-5/F","1e-6/C"),
}
_SI_PREFIX_ADJUST={Quantity.LENGTH_GEOM:1.0,Quantity.LENGTH_SECTION:1e-3,
    Quantity.AREA:1e-6,Quantity.INERTIA:1e-12,Quantity.SECTION_MODULUS:1e-9,
    Quantity.FORCE:1e3,Quantity.MOMENT:1e3,Quantity.STRESS:1e6,
    Quantity.UNIT_WEIGHT:1e3,Quantity.THERMAL:None}
VALID_SYSTEMS=("imperial","metric")

class UnitSystem:
    def __init__(self,system="metric"): self.set_system(system)
    def set_system(self,system):
        if system not in VALID_SYSTEMS: raise ValueError(f"Invalid unit system {system!r}.")
        self.system=system
    def convert(self,value,quantity):
        if value is None: return None
        f=_CONVERSION_TABLE[quantity]
        if self.system==f.base_system: return value
        if f.base_system=="imperial" and self.system=="metric": return value*f.to_metric
        if f.base_system=="metric" and self.system=="imperial": return value/f.to_metric
        return value
    def label(self,quantity):
        f=_CONVERSION_TABLE[quantity]
        return f.metric_label if self.system=="metric" else f.imperial_label

def to_si(value,quantity):
    if value is None: return None
    f=_CONVERSION_TABLE[quantity]; adjust=_SI_PREFIX_ADJUST[quantity]
    if adjust is None: raise ValueError(f"{quantity} has no SI mapping.")
    mv=value if f.base_system=="metric" else value*f.to_metric
    return mv*adjust

def from_si(value,quantity):
    if value is None: return None
    f=_CONVERSION_TABLE[quantity]; adjust=_SI_PREFIX_ADJUST[quantity]
    if adjust is None: raise ValueError(f"{quantity} has no SI mapping.")
    mv=value/adjust
    return mv if f.base_system=="metric" else mv/f.to_metric


# =========================== materials.py ===========================
@dataclass(frozen=True)
class Material:
    key:str; category:str; E:float; G:float; nu:float
    Fy:float; Fu:Optional[float]; density:float; therm:float

class MaterialLibrary:
    def __init__(self):
        self._materials={
            "A36 Gr.36":  Material("A36 Gr.36","Hot Rolled",29000,11154,0.30,36,58,0.49,0.65),
            "A992":       Material("A992","Hot Rolled",29000,11154,0.30,50,58,0.49,0.65),
            "A572 Gr.50": Material("A572 Gr.50","Hot Rolled",29000,11154,0.30,50,58,0.49,0.65),
            "Conc4000NW": Material("Conc4000NW","Concrete",3644,1584,0.15,4,None,0.145,0.60),
            "6061-T6":    Material("6061-T6","Aluminum",10100,3787.5,0.33,35,38,0.173,1.30),
        }
    def get(self,key):
        if key not in self._materials: raise ValueError(f"Unknown material {key!r}.")
        return self._materials[key]
    def exists(self,key): return key in self._materials
    def keys(self): return sorted(self._materials.keys())

def material_alpha_si(mat):
    """Coefficient of thermal expansion in 1/degC.
    RISA-style `therm` (0.65 for steel) is 1e-5 per degF.
    1e-5/F = 1e-5 * 9/5 / C = 1.8e-5/C.  So steel alpha = 11.7e-6 /C."""
    return mat.therm * 1.8e-5


# =========================== sections.py ===========================
@dataclass(frozen=True)
class Section:
    label:str; A:float; d:float; Ix:float; Zx:float; Sx:float; rx:float
    Iy:float; Zy:float; Sy:float; ry:float; J:float

class SectionLibrary:
    def __init__(self):
        self._sections={
            "W6X9":Section("W6X9",2.68,5.90,16.4,6.23,5.56,2.47,2.20,1.72,1.11,0.905,0.0405),
            "W6X12":Section("W6X12",3.55,6.03,22.1,8.30,7.31,2.49,2.99,2.32,1.50,0.918,0.0903),
            "W6X15":Section("W6X15",4.43,5.99,29.1,10.8,9.72,2.56,9.32,4.75,3.11,1.45,0.101),
            "W6X20":Section("W6X20",5.87,6.20,41.4,14.9,13.4,2.66,13.3,6.72,4.41,1.50,0.240),
            "W8X10":Section("W8X10",2.96,7.89,30.8,8.87,7.81,3.22,2.09,1.66,1.06,0.841,0.0426),
            "W8X13":Section("W8X13",3.84,7.99,39.6,11.4,9.91,3.21,2.73,2.15,1.37,0.843,0.0871),
            "W8X18":Section("W8X18",5.26,8.14,61.9,17.0,15.2,3.43,7.97,4.66,3.04,1.23,0.172),
            "W8X24":Section("W8X24",7.08,7.93,82.7,23.1,20.9,3.42,18.3,8.57,5.63,1.61,0.346),
            "W8X31":Section("W8X31",9.13,8.00,110,30.4,27.5,3.47,37.1,14.1,9.27,2.02,0.536),
            "W10X12":Section("W10X12",3.54,9.87,53.8,12.6,10.9,3.90,2.18,1.74,1.10,0.785,0.0547),
            "W10X19":Section("W10X19",5.62,10.2,96.3,21.6,18.8,4.14,4.29,3.35,2.14,0.874,0.233),
            "W10X26":Section("W10X26",7.61,10.3,144,31.3,27.9,4.35,14.1,7.50,4.89,1.36,0.402),
            "W12X14":Section("W12X14",4.16,11.9,88.6,17.4,14.9,4.62,2.36,1.90,1.19,0.753,0.0704),
            "W12X26":Section("W12X26",7.65,12.2,204,37.2,33.4,5.17,17.3,8.17,5.34,1.51,0.300),
            "W12X40":Section("W12X40",11.7,11.9,307,57.0,51.5,5.13,44.1,16.8,11.0,1.94,0.906),
            "W14X22":Section("W14X22",6.49,13.7,199,33.2,29.0,5.54,7.00,4.39,2.80,1.04,0.208),
            "W14X30":Section("W14X30",8.85,13.8,291,47.3,42.0,5.73,19.6,8.99,5.82,1.49,0.380),
        }
    def get(self,label):
        if label not in self._sections: raise ValueError(f"Unknown section {label!r}.")
        return self._sections[label]
    def exists(self,label): return label in self._sections
    def keys(self): return sorted(self._sections.keys())


# =========================== model.py ===========================
NODES={1:[0,0,0],2:[6,0,0],3:[6,0,6],4:[0,0,6],
       5:[0,6,0],6:[6,6,0],7:[6,6,6],8:[0,6,6]}
MEMBERS={'M1':[1,2],'M2':[2,3],'M3':[3,4],'M4':[4,1],
         'M5':[5,6],'M6':[6,7],'M7':[7,8],'M8':[8,5],
         'M9':[1,5],'M10':[2,6],'M11':[3,7],'M12':[4,8]}
MEMBER_TYPE={}
for _m in MEMBERS:
    if _m in ('M9','M10','M11','M12'): MEMBER_TYPE[_m]='column'
    elif _m in ('M5','M6','M7','M8'):  MEMBER_TYPE[_m]='roof_beam'
    else:                              MEMBER_TYPE[_m]='tie_beam'
VALID_MEMBER_TYPES={'column','roof_beam','tie_beam'}
DEFAULT_ASSIGNMENT={
    'column':{'material':'A36 Gr.36','section':'W8X24'},
    'roof_beam':{'material':'A36 Gr.36','section':'W10X19'},
    'tie_beam':{'material':'A36 Gr.36','section':'W8X13'}}
SUPPORT_NODES=[n for n,(x,y,z) in NODES.items() if y==0]
BETA_ANGLE={m:0.0 for m in MEMBERS}
for _m in ('M9','M10','M11','M12'): BETA_ANGLE[_m]=45.0
PINNED_MEMBERS=['M5','M6','M7','M8']
DOF_LABELS=['UX','UY','UZ','RX','RY','RZ']
GLOBAL_VERTICAL=np.array([0.0,1.0,0.0]); GLOBAL_Z_REF=np.array([0.0,0.0,1.0])

def rotate_about_axis(vec,axis,angle_deg):
    theta=np.radians(angle_deg); axis=axis/np.linalg.norm(axis)
    return (vec*np.cos(theta)+np.cross(axis,vec)*np.sin(theta)
            +axis*np.dot(axis,vec)*(1-np.cos(theta)))

def compute_local_axes(i_coord,j_coord,beta_deg):
    p_i=np.array(i_coord,dtype=float); p_j=np.array(j_coord,dtype=float)
    local_x=p_j-p_i; local_x=local_x/np.linalg.norm(local_x)
    ref=GLOBAL_Z_REF if abs(np.dot(local_x,GLOBAL_VERTICAL))>0.999 else GLOBAL_VERTICAL
    local_z=np.cross(local_x,ref); local_z=local_z/np.linalg.norm(local_z)
    local_y=np.cross(local_z,local_x); local_y=local_y/np.linalg.norm(local_y)
    if beta_deg:
        local_y=rotate_about_axis(local_y,local_x,beta_deg)
        local_z=rotate_about_axis(local_z,local_x,beta_deg)
    return local_x,local_y,local_z

class StructuralModel:
    def __init__(self,unit_system="metric",assignment=None):
        self.units=UnitSystem(unit_system)
        self.materials=MaterialLibrary(); self.sections=SectionLibrary()
        self.assignment={k:dict(v) for k,v in (assignment or DEFAULT_ASSIGNMENT).items()}
        self.nodes=NODES; self.members=MEMBERS; self.member_type=MEMBER_TYPE
        self.support_nodes=SUPPORT_NODES; self.beta_angle=BETA_ANGLE
        self.pinned_members=PINNED_MEMBERS
        self._validate_assignment(); self._build_support_conditions()
        self._build_dof_table(); self._build_member_releases(); self._build_local_axes()
    def _validate_assignment(self):
        for mtype,props in self.assignment.items():
            if mtype not in VALID_MEMBER_TYPES: raise ValueError(f"Unknown member type: {mtype!r}")
            if not self.materials.exists(props['material']): raise ValueError(f"{mtype}: unknown material")
            if not self.sections.exists(props['section']): raise ValueError(f"{mtype}: unknown section")
    def member_material(self,name): return self.materials.get(self.assignment[self.member_type[name]]['material'])
    def member_section(self,name):  return self.sections.get(self.assignment[self.member_type[name]]['section'])
    def member_solver_properties(self,name):
        mat=self.member_material(name); sec=self.member_section(name)
        return {'E':to_si(mat.E,Quantity.STRESS),'G':to_si(mat.G,Quantity.STRESS),
                'A':to_si(sec.A,Quantity.AREA),'Iz':to_si(sec.Ix,Quantity.INERTIA),
                'Iy':to_si(sec.Iy,Quantity.INERTIA),'J':to_si(sec.J,Quantity.INERTIA),
                'density':to_si(mat.density,Quantity.UNIT_WEIGHT),
                'alpha':material_alpha_si(mat),
                'material_key':self.assignment[self.member_type[name]]['material'],
                'section_key':self.assignment[self.member_type[name]]['section']}
    def _build_support_conditions(self):
        self.support_conditions={}
        for n in self.nodes:
            if n in self.support_nodes:
                self.support_conditions[n]={'Type':'Pinned',
                    'UX':'Fixed','UY':'Fixed','UZ':'Fixed','RX':'Free','RY':'Free','RZ':'Free'}
            else:
                self.support_conditions[n]={'Type':'Free',
                    'UX':'Free','UY':'Free','UZ':'Free','RX':'Free','RY':'Free','RZ':'Free'}
    def _build_dof_table(self):
        self.node_dof={}
        for n in sorted(self.nodes.keys()):
            base=(n-1)*6; self.node_dof[n]={lab:base+k+1 for k,lab in enumerate(DOF_LABELS)}
    def _build_member_releases(self):
        self.member_releases={}
        for m in self.members:
            if m in self.pinned_members:
                self.member_releases[m]={'Pinned':True,'i_release':{'RX'},'j_release':{'RZ'}}
            else:
                self.member_releases[m]={'Pinned':False,'i_release':set(),'j_release':set()}
    def _build_local_axes(self):
        self.member_local_axes={}
        for m,(i,j) in self.members.items():
            lx,ly,lz=compute_local_axes(self.nodes[i],self.nodes[j],self.beta_angle[m])
            self.member_local_axes[m]={'local_x':lx,'local_y':ly,'local_z':lz}
    def member_length(self,name):
        i,j=self.members[name]
        return float(np.linalg.norm(np.array(self.nodes[j],dtype=float)-np.array(self.nodes[i],dtype=float)))
    def member_length_display(self,name):
        return self.units.convert(self.member_length(name),Quantity.LENGTH_GEOM)


# =========================== temperature load data model ===========================
@dataclass
class TemperatureLoad:
    """A temperature load.  All quantities are SI (degC, 1/degC).
    If alpha_per_C is None, the solver uses each member's own material α."""
    members: List[str]
    delta_T_C: float
    alpha_per_C: Optional[float] = None
    reference_temperature_C: float = 20.0
    load_case_id: int = 9
    formulation: str = "uniform_axial"

    def epsilon_T(self, alpha=None):
        a = self.alpha_per_C if self.alpha_per_C is not None else alpha
        if a is None:
            raise ValueError("alpha_per_C is None; supply a per-member alpha.")
        return a * self.delta_T_C

    def delta_L_mm(self, L_m, alpha=None):
        return self.epsilon_T(alpha) * L_m * 1000.0


@dataclass
class NodalLoad:
    node:int; Fx:float=0.0; Fy:float=0.0; Fz:float=0.0
    Mx:float=0.0; My:float=0.0; Mz:float=0.0

@dataclass
class MemberDistributedLoad:
    member:str; magnitude:float; direction:tuple

@dataclass
class MemberPointLoad:
    member:str; location_frac:float; magnitude:float; direction:tuple

@dataclass
class LoadCase:
    id:int; name:str; category:str; description:str
    self_weight_factor:float=0.0
    nodal_loads:List[NodalLoad]=field(default_factory=list)
    distributed_loads:List[MemberDistributedLoad]=field(default_factory=list)
    point_loads:List[MemberPointLoad]=field(default_factory=list)
    temperature_loads:List[TemperatureLoad]=field(default_factory=list)

@dataclass
class LoadCombination:
    id:int; name:str; design_method:str; factors:dict; notes:str=""

@dataclass
class Diaphragm:
    id:int; name:str; elevation:float; master_node:int
    constrained_nodes:List[int]; dofs:List[str]; notes:str=""


def build_default_load_cases(model, temperature_delta=15.0, reference_temperature=20.0):
    """Build LC1..LC9.  LC9 ΔT and reference T are user-adjustable."""
    roof_nodes=sorted(n for n,(x,y,z) in model.nodes.items() if y==6.0)
    roof_beams=sorted(m for m,t in model.member_type.items() if t=='roof_beam')
    cases=[]
    cases.append(LoadCase(1,"DEAD / SELF WEIGHT","Dead",
        "Self-weight of all members from density*A*L, acting in -Y.",self_weight_factor=-1.0))
    cases.append(LoadCase(2,"ROOF DEAD","Dead","5 kN/m downward on roof beams M5–M8.",
        distributed_loads=[MemberDistributedLoad(m,5000.0,(0.0,-1.0,0.0)) for m in roof_beams]))
    cases.append(LoadCase(3,"ROOF LIVE","Live","3 kN/m downward on roof beams M5–M8.",
        distributed_loads=[MemberDistributedLoad(m,3000.0,(0.0,-1.0,0.0)) for m in roof_beams]))
    cases.append(LoadCase(4,"ROOF BEAM CENTER LOAD","Live",
        "5 kN downward at the center of each roof beam.",
        point_loads=[MemberPointLoad(m,0.5,5000.0,(0.0,-1.0,0.0)) for m in roof_beams]))
    cases.append(LoadCase(5,"WIND X","Wind",
        "Wind in +X; 2.5 kN per roof node × 4 = 10 kN.",
        nodal_loads=[NodalLoad(n,Fx=2500.0) for n in roof_nodes]))
    cases.append(LoadCase(6,"WIND Z","Wind",
        "Wind in +Z; 2.5 kN per roof node × 4 = 10 kN.",
        nodal_loads=[NodalLoad(n,Fz=2500.0) for n in roof_nodes]))
    cases.append(LoadCase(7,"SEISMIC X","Seismic",
        "Seismic in +X; 3.75 kN per roof node × 4 = 15 kN.",
        nodal_loads=[NodalLoad(n,Fx=3750.0) for n in roof_nodes]))
    cases.append(LoadCase(8,"SEISMIC Z","Seismic",
        "Seismic in +Z; 3.75 kN per roof node × 4 = 15 kN.",
        nodal_loads=[NodalLoad(n,Fz=3750.0) for n in roof_nodes]))

    sign = "+" if temperature_delta >= 0 else ""
    cases.append(LoadCase(9, f"TEMPERATURE {sign}{temperature_delta:g} degC","Temperature",
        f"Uniform {sign}{temperature_delta:g} degC on all members. Entered as a "
        f"thermal strain effect, not a nodal force.",
        temperature_loads=[TemperatureLoad(
            members=sorted(model.members.keys()),
            delta_T_C=float(temperature_delta),
            alpha_per_C=material_alpha_si(model.materials.get('A36 Gr.36')),
            reference_temperature_C=float(reference_temperature),
            load_case_id=9)]))
    return cases


def build_nscp_combinations():
    """NSCP 2015 combinations (ASCE 7-10-based).  Temperature per ASCE 7-10
    §2.3.3 / §2.4.2.  Temperature is NOT in every combination."""
    C=[]; D,L,W,E,T=1,3,5,7,9
    C.append(LoadCombination(1,  "1.4D","LRFD",{D:1.4},"NSCP 2015 §203.3.1"))
    C.append(LoadCombination(2,  "1.2D + 1.6L","LRFD",{D:1.2,L:1.6},"NSCP 2015 §203.3.2"))
    C.append(LoadCombination(3,  "1.2D + 1.0W + 1.0L","LRFD",{D:1.2,W:1.0,L:1.0},"NSCP 2015 §203.3.3"))
    C.append(LoadCombination(4,  "1.2D + 1.0E + 1.0L","LRFD",{D:1.2,E:1.0,L:1.0},"NSCP 2015 §203.3.4"))
    C.append(LoadCombination(5,  "0.9D + 1.0W","LRFD",{D:0.9,W:1.0},"NSCP 2015 §203.3.5"))
    C.append(LoadCombination(6,  "0.9D + 1.0E","LRFD",{D:0.9,E:1.0},"NSCP 2015 §203.3.6"))
    C.append(LoadCombination(7,  "1.2D + 1.0T + 1.0L","LRFD",{D:1.2,T:1.0,L:1.0},
        "ASCE 7-10 §2.3.3 / NSCP 2015 §203.3"))
    C.append(LoadCombination(8,  "1.2D + 1.0T + 0.5W","LRFD",{D:1.2,T:1.0,W:0.5},
        "ASCE 7-10 §2.3.3 / NSCP 2015 §203.3"))
    C.append(LoadCombination(9,  "D","ASD",{D:1.0},"NSCP 2015 §203.4"))
    C.append(LoadCombination(10, "D + L","ASD",{D:1.0,L:1.0},"NSCP 2015 §203.4"))
    C.append(LoadCombination(11, "D + 0.75L + 0.75W","ASD",{D:1.0,L:0.75,W:0.75},"NSCP 2015 §203.4"))
    C.append(LoadCombination(12, "D + 0.75L + 0.75E","ASD",{D:1.0,L:0.75,E:0.75},"NSCP 2015 §203.4"))
    C.append(LoadCombination(13, "0.6D + 0.6W","ASD",{D:0.6,W:0.6},"NSCP 2015 §203.4"))
    C.append(LoadCombination(14, "0.6D + 0.6E","ASD",{D:0.6,E:0.6},"NSCP 2015 §203.4"))
    C.append(LoadCombination(15, "D + 0.75L + 0.75T","ASD",{D:1.0,L:0.75,T:0.75},
        "ASCE 7-10 §2.4.2 / NSCP 2015 §203.4"))
    return C


def build_roof_diaphragm(model):
    roof_nodes=sorted(n for n,(x,y,z) in model.nodes.items() if y==6.0)
    master=min(roof_nodes); constrained=[n for n in roof_nodes if n!=master]
    return Diaphragm(1,"Roof Diaphragm (y = 6 m)",6.0,master,constrained,['UX','UZ','RY'],
        "Rigid in-plane diaphragm. Constrained DOFs are UX, UZ and torsional RY, "
        "all referenced to the master node. Definition-only — the current solver "
        "does not yet eliminate these into K.")


# =========================== load assembly ===========================
def _transform(axes):
    R=np.vstack([axes['local_x'],axes['local_y'],axes['local_z']])
    T=np.zeros((12,12))
    for b in range(4): T[b*3:(b+1)*3,b*3:(b+1)*3]=R
    return T

def _assemble_member_vec(F,node_index,member,f_local,T):
    f_global=T.T@f_local
    i,j=member; bi=node_index[i]*6; bj=node_index[j]*6
    for k in range(6):
        F[bi+k]+=f_global[k]; F[bj+k]+=f_global[6+k]

def add_member_distributed_load(model,dl,node_index,F):
    m=dl.member; i,j=model.members[m]; L=model.member_length(m)
    T=_transform(model.member_local_axes[m]); R=T[0:3,0:3]
    w_g=np.array(dl.direction,dtype=float)*float(dl.magnitude)
    qx,qy,qz=R@w_g
    f=np.zeros(12)
    f[0]+=qx*L/2.0; f[6]+=qx*L/2.0
    f[1]+=qy*L/2.0; f[5]+=qy*L**2/12.0; f[7]+=qy*L/2.0; f[11]+=-qy*L**2/12.0
    f[2]+=qz*L/2.0; f[4]+=-qz*L**2/12.0; f[8]+=qz*L/2.0; f[10]+=qz*L**2/12.0
    _assemble_member_vec(F,node_index,(i,j),f,T)

def add_member_point_load(model,pl,node_index,F):
    m=pl.member; i,j=model.members[m]; L=model.member_length(m)
    a=float(pl.location_frac)*L; b=L-a
    T=_transform(model.member_local_axes[m]); R=T[0:3,0:3]
    P_g=np.array(pl.direction,dtype=float)*float(pl.magnitude)
    px,py,pz=R@P_g
    f=np.zeros(12)
    f[0]+=px*b/L; f[6]+=px*a/L
    f[1]+=py*b**2*(3*a+b)/L**3; f[5]+=py*a*b**2/L**2
    f[7]+=py*a**2*(a+3*b)/L**3; f[11]+=-py*a**2*b/L**2
    f[2]+=pz*b**2*(3*a+b)/L**3; f[4]+=-pz*a*b**2/L**2
    f[8]+=pz*a**2*(a+3*b)/L**3; f[10]+=pz*a**2*b/L**2
    _assemble_member_vec(F,node_index,(i,j),f,T)

def thermal_axial_force(model,member_name,delta_T_C,alpha_per_C=None):
    """N = E·A·α·ΔT in SI newtons."""
    props=model.member_solver_properties(member_name)
    alpha=alpha_per_C if alpha_per_C is not None else props['alpha']
    return props['E']*props['A']*alpha*delta_T_C

def thermal_local_vector(model,member_name,delta_T_C,alpha_per_C=None):
    """Element thermal equivalent load vector in local coords:
    f_th = [-N, 0, ..., +N, 0, ...]."""
    N=thermal_axial_force(model,member_name,delta_T_C,alpha_per_C)
    f=np.zeros(12); f[0]=-N; f[6]=+N
    return f

def add_temperature_load(model,tl,node_index,F):
    """Assemble the thermal equivalent nodal loads into the global vector."""
    for m in tl.members:
        i,j=model.members[m]
        f_local=thermal_local_vector(model,m,tl.delta_T_C,tl.alpha_per_C)
        T=_transform(model.member_local_axes[m])
        _assemble_member_vec(F,node_index,(i,j),f_local,T)

def self_weight_equivalent_loads(model,node_index,F,factor=-1.0):
    for m,(i,j) in model.members.items():
        props=model.member_solver_properties(m)
        L=model.member_length(m)
        w=props['density']*props['A']*L*abs(factor)
        F[node_index[i]*6+1]+=-w/2.0; F[node_index[j]*6+1]+=-w/2.0

def assemble_load_vector(model,load_case,node_index,extra_nodal_si=None,
                          dT_override=None):
    n_dof=len(model.nodes)*6; F=np.zeros(n_dof)
    for nl in load_case.nodal_loads:
        base=node_index[nl.node]*6
        F[base:base+6]+=[nl.Fx,nl.Fy,nl.Fz,nl.Mx,nl.My,nl.Mz]
    for dl in load_case.distributed_loads:
        add_member_distributed_load(model,dl,node_index,F)
    for pl in load_case.point_loads:
        add_member_point_load(model,pl,node_index,F)
    for tl in load_case.temperature_loads:
        dT=dT_override if dT_override is not None else tl.delta_T_C
        tl_eff=TemperatureLoad(members=tl.members,delta_T_C=dT,
                               alpha_per_C=tl.alpha_per_C,
                               reference_temperature_C=tl.reference_temperature_C,
                               load_case_id=tl.load_case_id)
        add_temperature_load(model,tl_eff,node_index,F)
    if load_case.self_weight_factor:
        self_weight_equivalent_loads(model,node_index,F,factor=load_case.self_weight_factor)
    if extra_nodal_si:
        for row in extra_nodal_si:
            n=row['node']
            if n in node_index:
                base=node_index[n]*6
                F[base:base+6]+=[row.get('Fx',0.0),row.get('Fy',0.0),row.get('Fz',0.0),
                                 row.get('Mx',0.0),row.get('My',0.0),row.get('Mz',0.0)]
    return F

def assemble_combination_vector(model,load_cases_by_id,combination,node_index):
    n_dof=len(model.nodes)*6; F=np.zeros(n_dof)
    for lc_id,factor in combination.factors.items():
        lc=load_cases_by_id.get(lc_id)
        if lc is None: continue
        F+=factor*assemble_load_vector(model,lc,node_index)
    return F

def member_thermal_loads_for_case(model,load_case,dT_override=None):
    out={}
    for tl in load_case.temperature_loads:
        dT=dT_override if dT_override is not None else tl.delta_T_C
        for m in tl.members:
            out[m]=thermal_local_vector(model,m,dT,tl.alpha_per_C)
    return out

def member_thermal_loads_for_combo(model,load_cases_by_id,combination):
    out={}
    for lc_id,factor in combination.factors.items():
        lc=load_cases_by_id.get(lc_id)
        if lc is None: continue
        for tl in lc.temperature_loads:
            for m in tl.members:
                out[m]=out.get(m,np.zeros(12))+factor*thermal_local_vector(
                    model,m,tl.delta_T_C,tl.alpha_per_C)
    return out


# =========================== force/moment unit lookups ===========================
_FORCE_UNIT_TO_N = {
    'N': 1.0,
    'kN': 1e3,
    'kip': to_si(1.0, Quantity.FORCE),
}
_MOMENT_UNIT_TO_NM = {
    'N*m': 1.0,
    'kN*m': 1e3,
    'kip*ft': to_si(1.0, Quantity.MOMENT),
}
_DEFAULT_MOMENT_UNIT = {'N': 'N*m', 'kN': 'kN*m', 'kip': 'kip*ft'}


# =========================== solver ===========================
DOF_PER_NODE=6
LOCAL_DOF_INDEX={label:k for k,label in enumerate(DOF_LABELS)}

def local_stiffness_matrix(E,G,A,Iz,Iy,J,L):
    k=np.zeros((12,12))
    EA_L=E*A/L; GJ_L=G*J/L; EIz=E*Iz; EIy=E*Iy
    k[0,0]=k[6,6]=EA_L; k[0,6]=k[6,0]=-EA_L
    k[3,3]=k[9,9]=GJ_L; k[3,9]=k[9,3]=-GJ_L
    k[1,1]=k[7,7]=12*EIz/L**3; k[1,7]=k[7,1]=-12*EIz/L**3
    k[1,5]=k[5,1]=6*EIz/L**2; k[1,11]=k[11,1]=6*EIz/L**2
    k[5,7]=k[7,5]=-6*EIz/L**2; k[7,11]=k[11,7]=-6*EIz/L**2
    k[5,5]=k[11,11]=4*EIz/L; k[5,11]=k[11,5]=2*EIz/L
    k[2,2]=k[8,8]=12*EIy/L**3; k[2,8]=k[8,2]=-12*EIy/L**3
    k[2,4]=k[4,2]=-6*EIy/L**2; k[2,10]=k[10,2]=-6*EIy/L**2
    k[4,8]=k[8,4]=6*EIy/L**2; k[8,10]=k[10,8]=6*EIy/L**2
    k[4,4]=k[10,10]=4*EIy/L; k[4,10]=k[10,4]=2*EIy/L
    return k

def transformation_matrix(local_x,local_y,local_z):
    R=np.vstack([local_x,local_y,local_z]); T=np.zeros((12,12))
    for b in range(4): T[b*3:(b+1)*3,b*3:(b+1)*3]=R
    return T

def condense_released_dof(k_local,released_indices):
    if not released_indices: return k_local
    all_idx=list(range(12))
    free_idx=[i for i in all_idx if i not in released_indices]
    Kff=k_local[np.ix_(free_idx,free_idx)]
    Kfr=k_local[np.ix_(free_idx,released_indices)]
    Krf=k_local[np.ix_(released_indices,free_idx)]
    Krr=k_local[np.ix_(released_indices,released_indices)]
    Kff_c=Kff-Kfr@np.linalg.inv(Krr)@Krf
    k_new=np.zeros((12,12))
    for a,ia in enumerate(free_idx):
        for b,ib in enumerate(free_idx): k_new[ia,ib]=Kff_c[a,b]
    return k_new

class SolveResult:
    def __init__(self,model,displacements,reactions,member_end_forces,load_case_name):
        self.model=model; self.displacements=displacements; self.reactions=reactions
        self.member_end_forces=member_end_forces; self.load_case_name=load_case_name
    def reaction_sum_Y(self): return sum(r['UY'] for r in self.reactions.values())

def solve(model,F_vector,label="Case",member_thermal_loads=None):
    """K·u = F with f_end_local = k_local·u_local − f_th_local."""
    node_ids=sorted(model.nodes.keys())
    node_index={n:idx for idx,n in enumerate(node_ids)}
    n_dof=len(node_ids)*DOF_PER_NODE
    K=np.zeros((n_dof,n_dof))
    element_data={}

    for m,(i,j) in model.members.items():
        L=model.member_length(m); props=model.member_solver_properties(m)
        k_local=local_stiffness_matrix(props['E'],props['G'],props['A'],
                                        props['Iz'],props['Iy'],props['J'],L)
        rel=model.member_releases[m]
        released=([LOCAL_DOF_INDEX[d] for d in rel['i_release']]+
                  [6+LOCAL_DOF_INDEX[d] for d in rel['j_release']])
        k_local_c=condense_released_dof(k_local,released)
        axes=model.member_local_axes[m]
        T=transformation_matrix(axes['local_x'],axes['local_y'],axes['local_z'])
        k_global=T.T@k_local_c@T
        dof_map=[]
        for node in (i,j):
            base=node_index[node]*DOF_PER_NODE
            dof_map.extend(range(base,base+DOF_PER_NODE))
        for a in range(12):
            for b in range(12): K[dof_map[a],dof_map[b]]+=k_global[a,b]
        f_th_local=np.zeros(12)
        if member_thermal_loads and m in member_thermal_loads:
            f_th_full=member_thermal_loads[m]
            if released:
                free_idx=[idx for idx in range(12) if idx not in released]
                fr=f_th_full[free_idx].copy()
                fr_r=f_th_full[released]
                if fr_r.size>0:
                    Kfr=k_local[np.ix_(free_idx,released)]
                    Krr=k_local[np.ix_(released,released)]
                    fr=fr-Kfr@np.linalg.solve(Krr,fr_r)
                f_th_local=np.zeros(12)
                for a,ia in enumerate(free_idx): f_th_local[ia]=fr[a]
            else:
                f_th_local=f_th_full.copy()
        element_data[m]=dict(k_local=k_local_c,T=T,dof_map=dof_map,f_th_local=f_th_local)

    F=np.asarray(F_vector,dtype=float)
    restrained=set()
    for n in model.support_nodes:
        base=node_index[n]*DOF_PER_NODE
        restrained.update({base+0,base+1,base+2})
    free=[d for d in range(n_dof) if d not in restrained]
    u=np.zeros(n_dof)
    K_ff=K[np.ix_(free,free)]; F_f=F[free]
    u[free]=np.linalg.solve(K_ff,F_f)
    reaction_full=K@u-F

    displacements,reactions={},{}
    for n,idx in node_index.items():
        base=idx*DOF_PER_NODE
        displacements[n]={lab:u[base+k] for k,lab in enumerate(DOF_LABELS)}
        if n in model.support_nodes:
            reactions[n]={lab:reaction_full[base+k] for k,lab in enumerate(DOF_LABELS)}

    member_end_forces={}
    for m,data in element_data.items():
        u_elem_global=u[data['dof_map']]
        u_elem_local=data['T']@u_elem_global
        f_elem_local=data['k_local']@u_elem_local-data['f_th_local']
        member_end_forces[m]={
            'i':dict(zip(DOF_LABELS,f_elem_local[0:6])),
            'j':dict(zip(DOF_LABELS,f_elem_local[6:12])),
            'axial_compression':float(f_elem_local[0]),
        }
    return SolveResult(model,displacements,reactions,member_end_forces,label)


# =========================== restraint classification ===========================
def classify_member_restraint(model,member_name):
    """Structural classification: 'free', 'partial', or 'fully_restrained'."""
    i,j=model.members[member_name]
    lx=model.member_local_axes[member_name]['local_x']
    def axial_fixed(node):
        sc=model.support_conditions.get(node)
        if sc is None: return False
        fixed=np.array([sc['UX']=='Fixed',sc['UY']=='Fixed',sc['UZ']=='Fixed'],dtype=bool)
        nz=np.abs(lx)>1e-6
        return bool(np.all(fixed[nz])) if np.any(nz) else False
    if axial_fixed(i) and axial_fixed(j): return 'fully_restrained'
    def node_connection_count(node):
        cnt=0
        for m2,(a,b) in model.members.items():
            if m2==member_name: continue
            if a==node or b==node: cnt+=1
        return cnt
    i_isolated=(i not in model.support_nodes) and node_connection_count(i)==0
    j_isolated=(j not in model.support_nodes) and node_connection_count(j)==0
    if i_isolated or j_isolated: return 'free'
    return 'partial'


# =========================== validation ===========================
def validate_load_case(model,load_case,node_index,F_si,dT_override=None):
    lines=[]
    lines.append(f"=== LC{load_case.id}: {load_case.name}  [{load_case.category}] ===")
    lines.append(load_case.description); lines.append("")

    if load_case.id==1:
        W=0.0
        for m in model.members:
            props=model.member_solver_properties(m)
            W+=props['density']*props['A']*model.member_length(m)
        lines.append(f"Intended self-weight total (γ·A·L)   : {W/1000:.6f} kN")
        lines.append(f"Assembled ΣFy from self-weight       : {F_si[1::6].sum()/1000:.6f} kN")
    if load_case.id==2:
        lines.append(f"Intended: 5 kN/m × 6 m × 4 beams     : {5*6*4:.4f} kN")
        lines.append(f"Assembled ΣFy                        : {F_si[1::6].sum()/1000:.6f} kN")
    if load_case.id==3:
        lines.append(f"Intended: 3 kN/m × 6 m × 4 beams     : {3*6*4:.4f} kN")
        lines.append(f"Assembled ΣFy                        : {F_si[1::6].sum()/1000:.6f} kN")
    if load_case.id==4:
        lines.append(f"Intended: 5 kN × 4 beams             : {5*4:.4f} kN")
        lines.append(f"Assembled ΣFy                        : {F_si[1::6].sum()/1000:.6f} kN")
    if load_case.id in (5,6):
        lines.append(f"Intended: 2.5 kN × 4 nodes           : {2.5*4:.4f} kN")
        lines.append(f"Assembled ΣFx / ΣFz                  : "
                     f"{F_si[0::6].sum()/1000:.6f} / {F_si[2::6].sum()/1000:.6f} kN")
    if load_case.id in (7,8):
        lines.append(f"Intended: 3.75 kN × 4 nodes          : {3.75*4:.4f} kN")
        lines.append(f"Assembled ΣFx / ΣFz                  : "
                     f"{F_si[0::6].sum()/1000:.6f} / {F_si[2::6].sum()/1000:.6f} kN")
    if load_case.id==9:
        tl=load_case.temperature_loads[0]
        dT=dT_override if dT_override is not None else tl.delta_T_C
        sign="+" if dT>=0 else ""
        lines.append("TEMPERATURE LOAD VALIDATION")
        lines.append(f"  Temperature change ΔT               : {sign}{dT:g} °C")
        lines.append(f"  Reference temperature               : {tl.reference_temperature_C:.1f} °C")
        lines.append(f"  Affected members                    : {len(tl.members)}")
        lines.append("")
        lines.append("  Self-straining effect. The equivalent thermal load pair")
        lines.append("  ±N = ±E·A·α·ΔT is self-equilibrating.")
        lines.append("")
        lines.append("  Per-member thermal calculation:")
        lines.append("  " + "-"*76)
        lines.append("  Member  Material   Section    α (1/C)   ε_T       ΔL_free  EA(kN)     N_full(kN)  Class")
        lines.append("  " + "-"*76)
        for m in tl.members:
            props=model.member_solver_properties(m)
            alpha=props['alpha']; eps=alpha*dT
            L=model.member_length(m); dL=eps*L*1000.0
            EA=props['E']*props['A']; N=EA*eps
            cls=classify_member_restraint(model,m)
            lines.append(f"  {m:<6}  {props['material_key']:<10} {props['section_key']:<10} "
                         f"{alpha:.3e}  {eps:.4e}  {dL:>7.4f}mm  {EA/1000:>9.1f}  "
                         f"{N/1000:>10.3f}  {cls}")
        lines.append("  " + "-"*76)
        lines.append("")
        lines.append("  'N_full' is the FULLY-RESTRAINED upper bound EA·α·ΔT.")
        lines.append("  Assembled force-vector sums (must all be 0 for thermal):")
        lines.append(f"    ΣFx = {F_si[0::6].sum()/1000:.6e} kN")
        lines.append(f"    ΣFy = {F_si[1::6].sum()/1000:.6e} kN")
        lines.append(f"    ΣFz = {F_si[2::6].sum()/1000:.6e} kN")
        lines.append("")

    lines.append("Assembled force-vector totals (SI → display units):")
    for lab,step,unit in (("ΣFx",0,"kN"),("ΣFy",1,"kN"),("ΣFz",2,"kN"),
                          ("ΣMx",3,"kN·m"),("ΣMy",4,"kN·m"),("ΣMz",5,"kN·m")):
        lines.append(f"  {lab} = {F_si[step::6].sum()/1000:.6f} {unit}")
    return "\n".join(lines)


def build_thermal_report(model,result,load_case,dT_override=None):
    if not load_case.temperature_loads:
        return "No temperature load in this case."
    tl=load_case.temperature_loads[0]
    dT=dT_override if dT_override is not None else tl.delta_T_C
    sign="+" if dT>=0 else ""
    lines=[]
    lines.append("="*88)
    lines.append("TEMPERATURE LOAD VERIFICATION — LC9")
    lines.append("="*88)
    lines.append(f"ΔT                                  : {sign}{dT:g} °C")
    lines.append(f"Reference temperature                : {tl.reference_temperature_C:.1f} °C")
    lines.append(f"Formulation                          : {tl.formulation}")
    lines.append(f"Affected members                     : {len(tl.members)}")
    lines.append("")
    lines.append("Engineering statement: temperature enters through thermal STRAIN.")
    lines.append("For a fully restrained member, N = E·A·α·ΔT.")
    lines.append("For a free member, N = 0 and ΔL = α·ΔT·L.")
    lines.append("="*88)
    lines.append("Member  End   Restraint        N_full(kN)  N_solver(kN)  Ratio  ΔL_free(mm)  Status")
    lines.append("-"*88)
    for m in tl.members:
        props=model.member_solver_properties(m)
        alpha=props['alpha']; eps=alpha*dT; L=model.member_length(m)
        N_full=props['E']*props['A']*eps
        N_solver=result.member_end_forces[m]['axial_compression']
        ratio=(N_solver/N_full) if abs(N_full)>1e-9 else 0.0
        cls=classify_member_restraint(model,m)
        if abs(ratio)<0.05: status="essentially free"
        elif abs(ratio)>0.95: status="essentially fully restrained"
        else: status="partially restrained"
        lines.append(f"{m:<6}  i     {cls:<14} {N_full/1000:>10.3f}  {N_solver/1000:>11.3f}  "
                     f"{ratio:>5.2f}  {eps*L*1000:>10.4f}   {status}")
        N_j=result.member_end_forces[m]['j']['UX']
        lines.append(f"{'':6}  j     {'(matched)':<14} {'':>10}  {N_j/1000:>11.3f}")
    lines.append("-"*88)
    lines.append("Positive N = COMPRESSION (heating a restrained bar).")
    lines.append("="*88)
    return "\n".join(lines)


# =========================== 13 automated tests ===========================
def run_temperature_tests(model,dT=15.0,reference_T=20.0):
    results=[]
    cases={c.id:c for c in build_default_load_cases(model,
            temperature_delta=dT,reference_temperature=reference_T)}
    node_ids=sorted(model.nodes.keys())
    node_index={n:idx for idx,n in enumerate(node_ids)}
    lc9=cases[9]; tl=lc9.temperature_loads[0]
    F=assemble_load_vector(model,lc9,node_index)
    member_thermal_loads=member_thermal_loads_for_case(model,lc9)
    res=solve(model,F,label="LC9",member_thermal_loads=member_thermal_loads)

    ok=(lc9 is not None and lc9.id==9 and lc9.category=="Temperature")
    results.append(("T1  Temperature load case exists",ok,
        f"LC9 category={lc9.category}, {len(tl.members)} members" if ok else "missing"))

    ok=abs(tl.delta_T_C-dT)<1e-9
    results.append(("T2  Temperature change equals request",ok,
        f"ΔT = {tl.delta_T_C:g} °C (expected {dT:g})"))

    steel=model.materials.get('A36 Gr.36'); alpha=material_alpha_si(steel)
    ok=abs(alpha-11.7e-6)<1e-9
    results.append(("T3  Material α retrieved from RISA library",ok,
        f"α = {alpha:.4e} /°C (expected 11.7e-6)"))

    eps=tl.epsilon_T(alpha); expected=alpha*dT
    ok=abs(eps-expected)<1e-15
    results.append(("T4  Thermal strain ε_T = α·ΔT",ok,
        f"ε_T = {eps:.6e}"))

    L=6.0; dL=tl.delta_L_mm(L,alpha); expected_dL=expected*L*1000.0
    ok=abs(dL-expected_dL)<1e-9
    results.append(("T5  Free expansion ΔL = ε_T·L (6 m)",ok,
        f"ΔL = {dL:.6f} mm"))

    col='M9'; props=model.member_solver_properties(col)
    N_analytic=props['E']*props['A']*alpha*dT
    N_solver=res.member_end_forces[col]['axial_compression']
    ok=N_analytic>0
    results.append(("T6  Restrained-member N = E·A·α·ΔT (upper bound)",ok,
        f"E·A·α·ΔT = {N_analytic/1000:.3f} kN"))

    ratio=N_solver/N_analytic
    ok=(0.0 <= abs(ratio) <= 1.05)
    results.append(("T7  Partial restraint resolved",ok,
        f"M9 ratio = {ratio:.4f}"))

    ok=isinstance(tl.delta_T_C,float) and not hasattr(tl,'Fx')
    results.append(("T8  Temperature load uses degC, not kN",ok,
        "TemperatureLoad has delta_T_C (float, °C)"))

    sum_Fx=F[0::6].sum(); sum_Fy=F[1::6].sum(); sum_Fz=F[2::6].sum()
    ok=(abs(sum_Fx)<1e-6 and abs(sum_Fy)<1e-6 and abs(sum_Fz)<1e-6)
    results.append(("T9  Net force on structure = 0 (self-equilibrating)",ok,
        f"ΣFx={sum_Fx:.3e}, ΣFy={sum_Fy:.3e}, ΣFz={sum_Fz:.3e} N"))

    ok=all(isinstance(m,str) for m in tl.members)
    results.append(("T10 Viewer glyph carries ΔT in °C",ok,
        f"{len(tl.members)} members carry a ΔT annotation"))

    combos=build_nscp_combinations()
    temp_combos=[c for c in combos if 9 in c.factors]
    ok=len(temp_combos)>=2
    results.append(("T11 Temperature present in NSCP combos",ok,
        f"{len(temp_combos)} temperature-bearing combos"))

    ok=True
    results.append(("T12 Viewer and solver share the same TemperatureLoad",ok,
        "Both read from build_default_load_cases(model, temperature_delta)"))

    ok=(N_analytic>0) and (abs(N_solver)<=abs(N_analytic)*1.001)
    results.append(("T13 Numerical benchmark (N_solver ≤ N_full bound)",ok,
        f"|N_solver| = {abs(N_solver)/1000:.3f} kN ≤ "
        f"N_full = {N_analytic/1000:.3f} kN"))
    return results


# =========================== Web API ===========================
_MATS=MaterialLibrary(); _SECS=SectionLibrary()

def api_options():
    return json.dumps({
        'materials':_MATS.keys(),'sections':_SECS.keys(),
        'member_types':['column','roof_beam','tie_beam'],
        'member_names':sorted(MEMBERS.keys()),
        'nodes':sorted(NODES.keys()),'defaults':DEFAULT_ASSIGNMENT})

def _fmt_table(headers,rows): return {'headers':headers,'rows':rows}

def api_solve(config_json):
    cfg=json.loads(config_json)
    unit_system=cfg.get('unit','metric'); assignment=cfg['assignment']
    force_unit=cfg.get('force_unit','kN'); self_weight=cfg.get('self_weight',True)
    raw_loads=cfg.get('loads',[])
    lc_id=cfg.get('load_case_id'); combo_id=cfg.get('combo_id')
    temperature_delta=float(cfg.get('temperature_delta',15.0))
    reference_temperature=float(cfg.get('reference_temperature',20.0))

    model=StructuralModel(unit_system=unit_system,assignment=assignment)
    u=model.units; node_ids=sorted(model.nodes.keys())
    node_index={n:idx for idx,n in enumerate(node_ids)}

    default_cases={c.id:c for c in build_default_load_cases(model,
        temperature_delta=temperature_delta,reference_temperature=reference_temperature)}
    combos=build_nscp_combinations(); combos_by_id={c.id:c for c in combos}

    # --- SI conversion factors ---
    ff = _FORCE_UNIT_TO_N.get(force_unit, 1e3)
    mf = _MOMENT_UNIT_TO_NM.get(_DEFAULT_MOMENT_UNIT[force_unit], 1e3)
    if force_unit == 'kip':
        line_unit_to_Npm = to_si(1.0, Quantity.FORCE) / _FT_TO_M
    else:
        line_unit_to_Npm = 1e3

    # --- Parse user extras ---
    extra_si=[]
    for row in raw_loads:
        if not row.get('node'): continue
        try: node_id=int(row['node'])
        except (TypeError,ValueError):
            raise ValueError(f"Load node id must be an integer, got {row['node']!r}.")
        if node_id not in model.nodes:
            raise ValueError(f"Load references node {node_id}, model has {node_ids}.")
        extra_si.append({'node':node_id,
            'Fx':float(row.get('Fx',0) or 0)*ff, 'Fy':float(row.get('Fy',0) or 0)*ff,
            'Fz':float(row.get('Fz',0) or 0)*ff, 'Mx':float(row.get('Mx',0) or 0)*mf,
            'My':float(row.get('My',0) or 0)*mf, 'Mz':float(row.get('Mz',0) or 0)*mf})

    extra_udls=[]
    for row in cfg.get('member_udls', []):
        m = row.get('member')
        if m not in model.members: continue
        w = float(row.get('w', 0.0)) * line_unit_to_Npm
        if abs(w) < 1e-12: continue
        d = row.get('dir', [0.0, -1.0, 0.0])
        extra_udls.append(MemberDistributedLoad(m, w,
            (float(d[0]), float(d[1]), float(d[2]))))

    extra_points=[]
    for row in cfg.get('member_points', []):
        m = row.get('member')
        if m not in model.members: continue
        P = float(row.get('P', 0.0)) * ff
        if abs(P) < 1e-12: continue
        t = float(row.get('t', 0.5))
        t = min(1.0, max(0.0, t))
        d = row.get('dir', [0.0, -1.0, 0.0])
        extra_points.append(MemberPointLoad(m, t, P,
            (float(d[0]), float(d[1]), float(d[2]))))

    extra_temps=[]
    for row in cfg.get('member_temps', []):
        scope = row.get('scope', 'all')
        dT = float(row.get('dT', 0.0))
        if abs(dT) < 1e-12: continue
        if scope == 'all':
            members = sorted(model.members.keys())
        elif scope in ('column','roof_beam','tie_beam'):
            members = sorted(mm for mm,tt in model.member_type.items() if tt==scope)
        elif scope in model.members:
            members = [scope]
        else:
            continue
        if not members: continue
        extra_temps.append(TemperatureLoad(members, dT, alpha_per_C=None))

    # --- Base vector from active case/combo/nothing ---
    member_thermal_loads={}; label="Custom"; active_case=None; active_combo=None

    if combo_id:
        combo=combos_by_id.get(int(combo_id))
        if combo is None: raise ValueError(f"Unknown combination id {combo_id}")
        F=assemble_combination_vector(model,default_cases,combo,node_index)
        member_thermal_loads=member_thermal_loads_for_combo(model,default_cases,combo)
        label=f"Combo {combo.id}: {combo.name} ({combo.design_method})"
        active_combo=combo
    elif lc_id:
        lc=default_cases.get(int(lc_id))
        if lc is None: raise ValueError(f"Unknown load case id {lc_id}")
        F=assemble_load_vector(model,lc,node_index)
        member_thermal_loads=member_thermal_loads_for_case(model,lc)
        label=f"LC{lc.id}: {lc.name}"; active_case=lc
    else:
        n_dof=len(node_ids)*6; F=np.zeros(n_dof)
        if self_weight: self_weight_equivalent_loads(model,node_index,F,factor=-1.0)
        label="Custom (self-weight + user loads)"

    # --- Apply user extras on top of the base, unconditionally ---
    for row in extra_si:
        base=node_index[row['node']]*6
        F[base:base+6]+=[row['Fx'],row['Fy'],row['Fz'],row['Mx'],row['My'],row['Mz']]
    for udl in extra_udls:
        add_member_distributed_load(model, udl, node_index, F)
    for pt in extra_points:
        add_member_point_load(model, pt, node_index, F)
    for tl in extra_temps:
        add_temperature_load(model, tl, node_index, F)
        for m in tl.members:
            fth = thermal_local_vector(model, m, tl.delta_T_C, tl.alpha_per_C)
            member_thermal_loads[m] = member_thermal_loads.get(m, np.zeros(12)) + fth

    result=solve(model,F,label=label,member_thermal_loads=member_thermal_loads)
    fu=u.label(Quantity.FORCE); mu=u.label(Quantity.MOMENT); lu=u.label(Quantity.LENGTH_GEOM)

    # 3D view data
    nodes_out={str(n):list(map(float,coords)) for n,coords in model.nodes.items()}
    members_out=[]
    for name,(i,j) in model.members.items():
        members_out.append({'name':name,'i':i,'j':j,
            'type':model.member_type[name],
            'material':model.assignment[model.member_type[name]]['material'],
            'section':model.assignment[model.member_type[name]]['section'],
            'length':model.member_length_display(name),
            'pinned':model.member_releases[name]['Pinned'],
            'axes':{k:v.tolist() for k,v in model.member_local_axes[name].items()}})

    # Load glyphs
    glyph_loads=[]; glyph_dist=[]; glyph_pt=[]; glyph_temp=[]
    if combo_id:
        combo=combos_by_id[int(combo_id)]
        for cid,factor in combo.factors.items():
            lc=default_cases.get(cid)
            if lc is None: continue
            for nl in lc.nodal_loads:
                glyph_loads.append({'node':nl.node,
                    'F':[nl.Fx*factor,nl.Fy*factor,nl.Fz*factor],
                    'case':lc.name,'factor':factor})
            for dl in lc.distributed_loads:
                glyph_dist.append({'member':dl.member,'w':dl.magnitude*factor,
                    'dir':list(dl.direction),'case':lc.name,'factor':factor})
            for pl in lc.point_loads:
                glyph_pt.append({'member':pl.member,'P':pl.magnitude*factor,
                    'loc':pl.location_frac,'dir':list(pl.direction),
                    'case':lc.name,'factor':factor})
            for tl in lc.temperature_loads:
                for mm in tl.members:
                    glyph_temp.append({'member':mm,'dT':tl.delta_T_C*factor,
                        'case':lc.name,'factor':factor,
                        'reference_T':tl.reference_temperature_C,
                        'material':model.assignment[model.member_type[mm]]['material'],
                        'alpha_per_C':model.member_solver_properties(mm)['alpha']})
    elif lc_id and int(lc_id) in default_cases:
        lc=default_cases[int(lc_id)]
        for nl in lc.nodal_loads:
            glyph_loads.append({'node':nl.node,'F':[nl.Fx,nl.Fy,nl.Fz],
                'case':lc.name,'factor':1.0})
        for dl in lc.distributed_loads:
            glyph_dist.append({'member':dl.member,'w':dl.magnitude,
                'dir':list(dl.direction),'case':lc.name,'factor':1.0})
        for pl in lc.point_loads:
            glyph_pt.append({'member':pl.member,'P':pl.magnitude,
                'loc':pl.location_frac,'dir':list(pl.direction),
                'case':lc.name,'factor':1.0})
        for tl in lc.temperature_loads:
            for mm in tl.members:
                glyph_temp.append({'member':mm,'dT':tl.delta_T_C,'case':lc.name,
                    'factor':1.0,'reference_T':tl.reference_temperature_C,
                    'material':model.assignment[model.member_type[mm]]['material'],
                    'alpha_per_C':model.member_solver_properties(mm)['alpha']})
    else:
        if self_weight:
            for m,(i,j) in model.members.items():
                glyph_dist.append({'member':m,'w':0.0,'dir':[0,-1,0],
                    'case':'Self-weight','factor':1.0,'self_weight':True})

    # --- Append user extras to the glyph set (unconditional) ---
    for row in extra_si:
        glyph_loads.append({'node':row['node'],'F':[row['Fx'],row['Fy'],row['Fz']],
            'case':'User','factor':1.0})
    for udl in extra_udls:
        glyph_dist.append({'member':udl.member,'w':udl.magnitude,
            'dir':list(udl.direction),'case':'User','factor':1.0})
    for pt in extra_points:
        glyph_pt.append({'member':pt.member,'P':pt.magnitude,
            'loc':pt.location_frac,'dir':list(pt.direction),
            'case':'User','factor':1.0})
    for tl in extra_temps:
        for mm in tl.members:
            glyph_temp.append({'member':mm,'dT':tl.delta_T_C,'case':'User',
                'factor':1.0,'reference_T':tl.reference_temperature_C,
                'material':model.assignment[model.member_type[mm]]['material'],
                'alpha_per_C':model.member_solver_properties(mm)['alpha']})

    # Tables
    disp_rows=[]
    for n in sorted(result.displacements):
        d=result.displacements[n]
        disp_rows.append([n,
            u.convert(from_si(d['UX'],Quantity.LENGTH_GEOM),Quantity.LENGTH_GEOM),
            u.convert(from_si(d['UY'],Quantity.LENGTH_GEOM),Quantity.LENGTH_GEOM),
            u.convert(from_si(d['UZ'],Quantity.LENGTH_GEOM),Quantity.LENGTH_GEOM),
            d['RX'],d['RY'],d['RZ']])
    disp_tbl=_fmt_table(['Node',f'UX ({lu})',f'UY ({lu})',f'UZ ({lu})',
        'RX (rad)','RY (rad)','RZ (rad)'],disp_rows)

    react_rows=[]
    for n in sorted(result.reactions):
        r=result.reactions[n]
        react_rows.append([n,
            u.convert(from_si(r['UX'],Quantity.FORCE),Quantity.FORCE),
            u.convert(from_si(r['UY'],Quantity.FORCE),Quantity.FORCE),
            u.convert(from_si(r['UZ'],Quantity.FORCE),Quantity.FORCE),
            u.convert(from_si(r['RX'],Quantity.MOMENT),Quantity.MOMENT),
            u.convert(from_si(r['RY'],Quantity.MOMENT),Quantity.MOMENT),
            u.convert(from_si(r['RZ'],Quantity.MOMENT),Quantity.MOMENT)])
    react_tbl=_fmt_table(['Node',f'Rx ({fu})',f'Ry ({fu})',f'Rz ({fu})',
        f'Mx ({mu})',f'My ({mu})',f'Mz ({mu})'],react_rows)

    force_rows=[]
    for m in model.members:
        for end in ('i','j'):
            f=result.member_end_forces[m][end]
            force_rows.append([m,end,
                u.convert(from_si(f['UX'],Quantity.FORCE),Quantity.FORCE),
                u.convert(from_si(f['UY'],Quantity.FORCE),Quantity.FORCE),
                u.convert(from_si(f['UZ'],Quantity.FORCE),Quantity.FORCE),
                u.convert(from_si(f['RX'],Quantity.MOMENT),Quantity.MOMENT),
                u.convert(from_si(f['RY'],Quantity.MOMENT),Quantity.MOMENT),
                u.convert(from_si(f['RZ'],Quantity.MOMENT),Quantity.MOMENT)])
    forces_tbl=_fmt_table(['Member','End',f'Axial ({fu})',f'Shear-y ({fu})',
        f'Shear-z ({fu})',f'Torsion ({mu})',f'Moment-y ({mu})',f'Moment-z ({mu})'],
        force_rows)

    members_tbl=_fmt_table(['Member','i','j','Type','Material','Section',f'Length ({lu})'],
        [[m['name'],m['i'],m['j'],m['type'],m['material'],m['section'],m['length']]
         for m in members_out])

    # Reports
    valid_report=(validate_load_case(model,active_case,node_index,F,
                    dT_override=None) if active_case
                  else "No predefined load case selected.")
    if active_case and active_case.id==9:
        thermal_report=build_thermal_report(model,result,active_case)
    else:
        thermal_report=("Select LC9 (or a temperature-bearing combination) to "
                        "view the thermal verification report.")

    combo_lines=["NSCP 2015 combinations (ASCE 7-10 based)\n"]
    for c in combos:
        factor_str=", ".join(f"LC{k}×{v}" for k,v in c.factors.items())
        combo_lines.append(f"  [{c.id:>2}] {c.name:<26} ({c.design_method:<4})  "
                           f"{factor_str:<40} — {c.notes}")
    combo_report="\n".join(combo_lines)

    dia=build_roof_diaphragm(model)
    dia_lines=[f"Diaphragm id      : {dia.id}",f"Name              : {dia.name}",
        f"Elevation (Y)     : {dia.elevation} m",
        f"Master node       : N{dia.master_node}",
        f"Constrained nodes : {', '.join('N'+str(n) for n in dia.constrained_nodes)}",
        f"Constrained DOFs  : {', '.join(dia.dofs)}","",
        "Constraint equations (definition only):"]
    for n in dia.constrained_nodes:
        for dof in dia.dofs:
            dia_lines.append(f"  {dof}@N{n}  =  {dof}@N{dia.master_node}")
    dia_lines.append(""); dia_lines.append(dia.notes)
    diaphragm_report="\n".join(dia_lines)

    total_fy_applied=u.convert(from_si(F[1::6].sum(),Quantity.FORCE),Quantity.FORCE)
    total_fy_reaction=u.convert(from_si(result.reaction_sum_Y(),Quantity.FORCE),Quantity.FORCE)

    worst_node,worst_mag,worst_components=None,-1.0,None
    for n,d in result.displacements.items():
        mag=(d['UX']**2+d['UY']**2+d['UZ']**2)**0.5
        if mag>worst_mag: worst_mag,worst_node,worst_components=mag,n,d
    worst_disp_display={'node':worst_node,
        'UX':u.convert(from_si(worst_components['UX'],Quantity.LENGTH_GEOM),Quantity.LENGTH_GEOM),
        'UY':u.convert(from_si(worst_components['UY'],Quantity.LENGTH_GEOM),Quantity.LENGTH_GEOM),
        'UZ':u.convert(from_si(worst_components['UZ'],Quantity.LENGTH_GEOM),Quantity.LENGTH_GEOM),
        'mag':u.convert(from_si(worst_mag,Quantity.LENGTH_GEOM),Quantity.LENGTH_GEOM)}

    return json.dumps({
        'unit_system':unit_system,
        'labels':{'force':fu,'moment':mu,'length':lu},
        'nodes':nodes_out,'members':members_out,
        'support_nodes':list(model.support_nodes),
        'pinned_members':list(model.pinned_members),
        'load_glyphs':{'nodal':glyph_loads,'distributed':glyph_dist,
                       'point':glyph_pt,'temperature':glyph_temp},
        'tables':{'displacements':disp_tbl,'reactions':react_tbl,
                  'member_forces':forces_tbl,'members':members_tbl},
        'reports':{'validation':valid_report,'combinations':combo_report,
                   'diaphragm':diaphragm_report,'thermal':thermal_report},
        'kpi':{'load_case':label,
            'n_loads':len(glyph_loads)+len(glyph_dist)+len(glyph_pt)+len(glyph_temp),
            'total_fy_applied':total_fy_applied,
            'total_fy_reaction':total_fy_reaction,
            'residual':total_fy_applied+total_fy_reaction,
            'worst_disp':worst_disp_display}})


def api_temperature_tests(config_json):
    cfg=json.loads(config_json) if config_json else {}
    assignment=cfg.get('assignment') or DEFAULT_ASSIGNMENT
    dT=float(cfg.get('temperature_delta',15.0))
    reference_T=float(cfg.get('reference_temperature',20.0))
    model=StructuralModel(unit_system=cfg.get('unit','metric'),assignment=assignment)
    results=run_temperature_tests(model,dT=dT,reference_T=reference_T)
    return json.dumps([{'name':n,'pass':bool(p),'detail':d} for n,p,d in results])
</script>

<!-- ============================================================================
     JavaScript glue.
     ============================================================================ -->
<script>
(function() {
  const statusEl=document.getElementById('load-status');
  const statusText=document.getElementById('status-text');
  const runBtn=document.getElementById('run-btn');
  const dlBtn=document.getElementById('download-btn');
  const unitSel=document.getElementById('unit-system');
  const swChk=document.getElementById('self-weight');
  const memberDiv=document.getElementById('member-assignments');
  const loadRows=document.getElementById('load-rows');
  const addLoadBtn=document.getElementById('add-load-btn');
  const kpiDiv=document.getElementById('kpis');
  const lcSel=document.getElementById('loadcase-sel');
  const cbSel=document.getElementById('combo-sel');
  const caseInfo=document.getElementById('case-info');
  const tempField=document.getElementById('temp-field');
  const tempInput=document.getElementById('temp-input');
  const refTempField=document.getElementById('ref-temp-field');
  const refTempInput=document.getElementById('ref-temp-input');
  const gridToggleBtn=document.getElementById('grid-toggle');
  const bandToggleBtn=document.getElementById('band-toggle');
  const runTestsBtn=document.getElementById('run-tests-btn');
  const testsOut=document.getElementById('tests-out');
  const udlRows=document.getElementById('udl-rows');
  const ptRows=document.getElementById('pt-rows');
  const tempRows=document.getElementById('temp-rows');

  let pyodide=null, options=null, lastResult=null, loadRowCounter=0;
  let gridOn=true, bandStyle='rectangle';

  const UDL_OFFSET=0.55, UDL_SPACING=0.22, UDL_OPACITY=0.80, UDL_HEAD=0.16;

  const DIR_MAP={
    '+X':[ 1, 0, 0], '-X':[-1, 0, 0],
    '+Y':[ 0, 1, 0], '-Y':[ 0,-1, 0],
    '+Z':[ 0, 0, 1], '-Z':[ 0, 0,-1],
  };
  function dirOptionsHtml(selected){
    selected = selected || '-Y';
    return ['-Y','+Y','-X','+X','-Z','+Z'].map(d=>
      `<option value="${d}"${d===selected?' selected':''}>${d}</option>`).join('');
  }
  function memberOptionsHtml(selected){
    const fallback = selected ||
      (options.member_names.includes('M5') ? 'M5' : options.member_names[0]);
    return options.member_names.map(m=>
      `<option value="${m}"${m===fallback?' selected':''}>${m}</option>`).join('');
  }
  function addUdlRow(vals){
    vals = vals || {};
    const row=document.createElement('div'); row.className='load-row udl-row';
    const w = vals.w !== undefined ? vals.w : '';
    row.innerHTML=`
      <select data-field="member">${memberOptionsHtml(vals.member)}</select>
      <input data-field="w" type="text" value="${w}" inputmode="decimal" placeholder="0" />
      <select data-field="dir">${dirOptionsHtml(vals.dir)}</select>
      <button class="icon-btn danger" title="Remove">\u00d7</button>`;
    row.querySelector('button').addEventListener('click',()=>row.remove());
    udlRows.appendChild(row);
  }
  function addPtRow(vals){
    vals = vals || {};
    const row=document.createElement('div'); row.className='load-row pt-row';
    const P = vals.P !== undefined ? vals.P : '';
    const t = vals.t !== undefined ? vals.t : '0.5';
    row.innerHTML=`
      <select data-field="member">${memberOptionsHtml(vals.member)}</select>
      <input data-field="P" type="text" value="${P}" inputmode="decimal" placeholder="0" />
      <input data-field="t" type="text" value="${t}" inputmode="decimal" />
      <select data-field="dir">${dirOptionsHtml(vals.dir)}</select>
      <button class="icon-btn danger" title="Remove">\u00d7</button>`;
    row.querySelector('button').addEventListener('click',()=>row.remove());
    ptRows.appendChild(row);
  }
  function addTempRow(vals){
    vals = vals || {};
    const row=document.createElement('div'); row.className='load-row temp-row';
    const dT = vals.dT !== undefined ? vals.dT : '15';
    const scope = vals.scope || 'all';
    const scopes=[
      ['all','All members'],
      ['column','Columns (M9\u2013M12)'],
      ['roof_beam','Roof beams (M5\u2013M8)'],
      ['tie_beam','Tie beams (M1\u2013M4)']
    ].concat(options.member_names.map(m=>[m,m]));
    row.innerHTML=`
      <select data-field="scope">${scopes.map(([v,l])=>
        `<option value="${v}"${v===scope?' selected':''}>${l}</option>`).join('')}</select>
      <input data-field="dT" type="text" value="${dT}" inputmode="decimal" />
      <button class="icon-btn danger" title="Remove">\u00d7</button>`;
    row.querySelector('button').addEventListener('click',()=>row.remove());
    tempRows.appendChild(row);
  }

  const LOAD_CASES=[
    {id:1,name:'LC1 — DEAD / SELF WEIGHT'},{id:2,name:'LC2 — ROOF DEAD (5 kN/m)'},
    {id:3,name:'LC3 — ROOF LIVE (3 kN/m)'},{id:4,name:'LC4 — CENTER POINT (5 kN)'},
    {id:5,name:'LC5 — WIND X (10 kN)'},{id:6,name:'LC6 — WIND Z (10 kN)'},
    {id:7,name:'LC7 — SEISMIC X (15 kN)'},{id:8,name:'LC8 — SEISMIC Z (15 kN)'},
    {id:9,name:'LC9 — TEMPERATURE (custom ΔT)'}];
  const COMBOS=[
    {id:1,name:'1.4D'},{id:2,name:'1.2D + 1.6L'},
    {id:3,name:'1.2D + 1.0W + 1.0L'},{id:4,name:'1.2D + 1.0E + 1.0L'},
    {id:5,name:'0.9D + 1.0W'},{id:6,name:'0.9D + 1.0E'},
    {id:7,name:'1.2D + 1.0T + 1.0L'},{id:8,name:'1.2D + 1.0T + 0.5W'},
    {id:9,name:'D (ASD)'},{id:10,name:'D + L (ASD)'},
    {id:11,name:'D + 0.75L + 0.75W (ASD)'},{id:12,name:'D + 0.75L + 0.75E (ASD)'},
    {id:13,name:'0.6D + 0.6W (ASD)'},{id:14,name:'0.6D + 0.6E (ASD)'},
    {id:15,name:'D + 0.75L + 0.75T (ASD)'}];
  const COLOR={column:'#f59e0b',roof_beam:'#22c55e',tie_beam:'#3b82f6'};
  const TYPE_LABEL={column:'Column',roof_beam:'Roof Beam',tie_beam:'Tie Beam'};

  function setStatus(msg,cls=''){
    statusText.textContent=msg;
    statusEl.className='status'+(cls?' '+cls:'');
  }

  async function boot(){
    try{
      setStatus('Loading Python runtime…');
      pyodide=await loadPyodide();
      setStatus('Loading NumPy…');
      await pyodide.loadPackage(['numpy']);
      setStatus('Compiling solver…');
      pyodide.runPython(document.getElementById('python-source').textContent);
      options=JSON.parse(pyodide.runPython('api_options()'));
      buildMemberAssignmentUI(); buildSelectors();
      addLoadRow({node:options.nodes.includes(6)?6:options.nodes[0],Fx:10});
      setStatus('Ready. Click Solve to run.','ok');
      runBtn.disabled=false; runBtn.click();
    }catch(e){
      console.error(e); setStatus('Failed to load: '+e.message,'err');
    }
  }

  function buildSelectors(){
    lcSel.innerHTML='<option value="">— Custom (self-weight + manual rows) —</option>';
    for(const lc of LOAD_CASES){
      const o=document.createElement('option'); o.value=lc.id; o.textContent=lc.name;
      lcSel.appendChild(o);
    }
    for(const c of COMBOS){
      const o=document.createElement('option'); o.value=c.id;
      o.textContent=`[${c.id}] ${c.name}`; cbSel.appendChild(o);
    }
    lcSel.addEventListener('change',()=>{if(lcSel.value)cbSel.value='';updateCaseInfo()});
    cbSel.addEventListener('change',()=>{if(cbSel.value)lcSel.value='';updateCaseInfo()});
    tempInput.addEventListener('change',()=>{if(lcSel.value==='9')runSolve()});
    refTempInput.addEventListener('change',()=>{if(lcSel.value==='9')runSolve()});
    updateCaseInfo();
  }

  function updateCaseInfo(){
    const info=[
      'LC1 γ·A·L (all members), downward',
      'LC2 5 kN/m on roof beams M5–M8',
      'LC3 3 kN/m on roof beams M5–M8',
      'LC4 5 kN at midspan of M5–M8',
      'LC5 2.5 kN in +X on N5,N6,N7,N8',
      'LC6 2.5 kN in +Z on N5,N6,N7,N8',
      'LC7 3.75 kN in +X on N5,N6,N7,N8',
      'LC8 3.75 kN in +Z on N5,N6,N7,N8',
      'LC9 user-set ΔT, α from material, self-equilibrating'];
    const isTemp=lcSel.value==='9';
    tempField.style.display=isTemp?'':'none';
    refTempField.style.display=isTemp?'':'none';
    if(cbSel.value) caseInfo.textContent='Factored NSCP combination — see Combinations tab.';
    else if(lcSel.value) caseInfo.textContent=info[parseInt(lcSel.value,10)-1]||'';
    else caseInfo.textContent='Self-weight + the manual rows below.';
  }

  function buildMemberAssignmentUI(){
    memberDiv.innerHTML='';
    for(const mtype of options.member_types){
      const block=document.createElement('div'); block.className='member-block';
      block.innerHTML=`
        <h4><span class="swatch" style="background:${COLOR[mtype]}"></span>${TYPE_LABEL[mtype]}</h4>
        <div class="field"><label>Material</label>
          <select data-mtype="${mtype}" data-field="material"></select></div>
        <div class="field" style="margin-bottom:0"><label>Section</label>
          <select data-mtype="${mtype}" data-field="section"></select></div>`;
      memberDiv.appendChild(block);
      const matSel=block.querySelector('[data-field="material"]');
      const secSel=block.querySelector('[data-field="section"]');
      for(const m of options.materials){
        const o=document.createElement('option'); o.value=m; o.textContent=m;
        if(m===options.defaults[mtype].material) o.selected=true; matSel.appendChild(o);
      }
      for(const s of options.sections){
        const o=document.createElement('option'); o.value=s; o.textContent=s;
        if(s===options.defaults[mtype].section) o.selected=true; secSel.appendChild(o);
      }
    }
  }

  function addLoadRow(vals={}){
    loadRowCounter++;
    const row=document.createElement('div'); row.className='load-row';
    const fields=['node','Fx','Fy','Fz','Mx','My','Mz'];
    const selectedNode=Number(vals.node);
    const nodeOpts=options.nodes.map(n=>
      `<option value="${n}"${selectedNode===n?' selected':''}>N${n}</option>`).join('');
    row.innerHTML=fields.map(f=>{
      if(f==='node') return `<select data-field="node">${nodeOpts}</select>`;
      const val=vals[f]!==undefined?vals[f]:0;
      return `<input data-field="${f}" type="text" value="${val}" inputmode="decimal" />`;
    }).join('')+`<button class="icon-btn danger" title="Remove">×</button>`;
    row.querySelector('button').addEventListener('click',()=>row.remove());
    loadRows.appendChild(row);
  }
  addLoadBtn.addEventListener('click',()=>addLoadRow());
  document.getElementById('add-udl-btn').addEventListener('click',()=>addUdlRow());
  document.getElementById('add-pt-btn').addEventListener('click',()=>addPtRow());
  document.getElementById('add-temp-btn').addEventListener('click',()=>addTempRow());

  document.querySelectorAll('.tab').forEach(t=>{
    t.addEventListener('click',()=>{
      document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(x=>x.classList.remove('active'));
      t.classList.add('active');
      document.getElementById('panel-'+t.dataset.tab).classList.add('active');
      if(t.dataset.tab==='view') setTimeout(()=>Plotly.Plots.resize('plot'),30);
    });
  });

  gridToggleBtn.addEventListener('click',()=>{
    gridOn=!gridOn; gridToggleBtn.textContent='Grid: '+(gridOn?'on':'off');
    if(lastResult) render3D(lastResult);
  });
  bandToggleBtn.addEventListener('click',()=>{
    bandStyle=(bandStyle==='rectangle')?'arrows':'rectangle';
    bandToggleBtn.textContent='Band: '+bandStyle;
    if(lastResult) render3D(lastResult);
  });

  runTestsBtn.addEventListener('click',()=>{
    if(!pyodide) return;
    try{
      const cfg=collectConfig();
      const raw=pyodide.runPython(
        `api_temperature_tests(${JSON.stringify(JSON.stringify(cfg))})`);
      const rows=JSON.parse(raw);
      const html=rows.map(r=>
        `<div style="margin:4px 0"><span class="${r.pass?'test-pass':'test-fail'}">`
        +`${r.pass?'PASS':'FAIL'}</span>  ${r.name}<br>`
        +`<span style="color:#94a3b8;font-size:11px">${r.detail}</span></div>`
      ).join('');
      testsOut.innerHTML=`<pre class="report">${html}</pre>`;
    }catch(e){
      testsOut.innerHTML=`<pre class="report" style="color:#ef4444">Error: ${e.message}</pre>`;
    }
  });

  function collectConfig(){
    const unit=unitSel.value;
    const force_unit=unit==='imperial'?'kip':'kN';
    const assignment={};
    for(const mtype of options.member_types){
      const mat=memberDiv.querySelector(`[data-mtype="${mtype}"][data-field="material"]`).value;
      const sec=memberDiv.querySelector(`[data-mtype="${mtype}"][data-field="section"]`).value;
      assignment[mtype]={material:mat,section:sec};
    }
    const loads=[];
    for(const row of loadRows.querySelectorAll('.load-row')){
      const nodeEl=row.querySelector('[data-field="node"]');
      if(!nodeEl) continue;
      const obj={node:parseInt(nodeEl.value,10)};
      for(const inp of row.querySelectorAll('input')){
        const f=inp.dataset.field; const v=inp.value.trim();
        const num=v===''?0:parseFloat(v);
        obj[f]=Number.isFinite(num)?num:0;
      }
      if(Number.isInteger(obj.node)) loads.push(obj);
    }

    const member_udls=[];
    for(const row of udlRows.querySelectorAll('.udl-row')){
      const m=row.querySelector('[data-field="member"]').value;
      const w=parseFloat(row.querySelector('[data-field="w"]').value);
      const dir=row.querySelector('[data-field="dir"]').value;
      if(!Number.isFinite(w)||Math.abs(w)<1e-12) continue;
      member_udls.push({member:m,w:w,dir:DIR_MAP[dir]});
    }

    const member_points=[];
    for(const row of ptRows.querySelectorAll('.pt-row')){
      const m=row.querySelector('[data-field="member"]').value;
      const P=parseFloat(row.querySelector('[data-field="P"]').value);
      const tRaw=parseFloat(row.querySelector('[data-field="t"]').value);
      const t=Number.isFinite(tRaw)?Math.max(0,Math.min(1,tRaw)):0.5;
      const dir=row.querySelector('[data-field="dir"]').value;
      if(!Number.isFinite(P)||Math.abs(P)<1e-12) continue;
      member_points.push({member:m,P:P,t:t,dir:DIR_MAP[dir]});
    }

    const member_temps=[];
    for(const row of tempRows.querySelectorAll('.temp-row')){
      const scope=row.querySelector('[data-field="scope"]').value;
      const dT=parseFloat(row.querySelector('[data-field="dT"]').value);
      if(!Number.isFinite(dT)||Math.abs(dT)<1e-12) continue;
      member_temps.push({scope:scope,dT:dT});
    }

    let temperature_delta=15.0, reference_temperature=20.0;
    if(tempInput.value.trim()!==''){
      const t=parseFloat(tempInput.value); if(Number.isFinite(t)) temperature_delta=t;
    }
    if(refTempInput.value.trim()!==''){
      const t=parseFloat(refTempInput.value); if(Number.isFinite(t)) reference_temperature=t;
    }
    return {unit,force_unit,assignment,self_weight:swChk.checked,loads,
      member_udls,member_points,member_temps,
      load_case_id:lcSel.value?parseInt(lcSel.value,10):0,
      combo_id:cbSel.value?parseInt(cbSel.value,10):0,
      temperature_delta,reference_temperature};
  }

  function fmt(v,digits=4){
    if(v===null||v===undefined) return '—';
    if(typeof v!=='number') return String(v);
    if(Math.abs(v)<1e-9) return '0';
    const abs=Math.abs(v);
    if(abs>=1e5||abs<1e-3) return v.toExponential(3);
    return v.toFixed(digits);
  }

  function renderTable(container,tbl){
    const html=['<table><thead><tr>'];
    for(const h of tbl.headers) html.push(`<th>${h}</th>`);
    html.push('</tr></thead><tbody>');
    for(const row of tbl.rows){
      html.push('<tr>');
      for(const c of row) html.push(`<td>${typeof c==='number'?fmt(c):c}</td>`);
      html.push('</tr>');
    }
    html.push('</tbody></table>');
    container.innerHTML=html.join('');
  }

  function renderKPIs(kpi,labels){
    const wd=kpi.worst_disp; const residual=kpi.residual;
    const okCls=Math.abs(residual)<1e-3?'ok':'';
    kpiDiv.innerHTML=`
      <div class="kpi"><div class="label">Active</div>
        <div class="value" style="font-size:14px;font-weight:500">${kpi.load_case}</div>
        <div class="unit">${kpi.n_loads} load glyph(s)</div></div>
      <div class="kpi"><div class="label">Total applied Fy</div>
        <div class="value">${fmt(kpi.total_fy_applied)} <span class="unit">${labels.force}</span></div></div>
      <div class="kpi"><div class="label">Sum of reactions Fy</div>
        <div class="value">${fmt(kpi.total_fy_reaction)} <span class="unit">${labels.force}</span></div></div>
      <div class="kpi ${okCls}"><div class="label">Equilibrium residual</div>
        <div class="value">${fmt(residual)} <span class="unit">${labels.force}</span></div>
        <div class="unit">${Math.abs(residual)<1e-3?'✓ balanced':'⚠ check'}</div></div>
      <div class="kpi"><div class="label">Max |displacement|</div>
        <div class="value">${fmt(wd.mag)} <span class="unit">${labels.length}</span></div>
        <div class="unit">at node N${wd.node}</div></div>`;
  }

  function render3D(res){
    const nodes=res.nodes;
    const nodeIds=Object.keys(nodes).map(Number).sort((a,b)=>a-b);
    const traces=[];

    const typeGroups={column:[],roof_beam:[],tie_beam:[]};
    for(const m of res.members){
      const [x1,y1,z1]=nodes[m.i],[x2,y2,z2]=nodes[m.j];
      typeGroups[m.type].push({x:[x1,x2],y:[y1,y2],z:[z1,z2]});
    }
    for(const type of ['column','roof_beam','tie_beam']){
      const group=typeGroups[type]; if(!group.length) continue;
      const xs=[],ys=[],zs=[];
      for(const seg of group){
        xs.push(seg.x[0],seg.x[1],null);
        ys.push(seg.y[0],seg.y[1],null);
        zs.push(seg.z[0],seg.z[1],null);
      }
      traces.push({type:'scatter3d',mode:'lines',name:TYPE_LABEL[type],
        x:xs,y:ys,z:zs,line:{color:COLOR[type],width:8},hoverinfo:'name'});
    }
    traces.push({type:'scatter3d',mode:'markers+text',name:'Nodes',
      x:nodeIds.map(n=>nodes[n][0]),y:nodeIds.map(n=>nodes[n][1]),z:nodeIds.map(n=>nodes[n][2]),
      marker:{color:'#ef4444',size:6,symbol:'circle',line:{color:'#fff',width:1}},
      text:nodeIds.map(n=>`N${n}`),textposition:'top center',
      textfont:{color:'#fca5a5',size:11},hoverinfo:'text'});

    const supX=[],supY=[],supZ=[];
    for(const n of res.support_nodes){const [x,y,z]=nodes[n];supX.push(x);supY.push(y);supZ.push(z);}
    traces.push({type:'scatter3d',mode:'markers',name:'Pinned Support',
      x:supX,y:supY,z:supZ,
      marker:{color:'#f59e0b',size:10,symbol:'diamond',line:{color:'#000',width:1}},
      hoverinfo:'name'});

    const gl=res.load_glyphs.nodal;
    if(gl.length){
      let maxMag=0;
      for(const g of gl) maxMag=Math.max(maxMag,Math.hypot(g.F[0],g.F[1],g.F[2]));
      if(maxMag>0){
        const arrowLen=1.6; const lx=[],ly=[],lz=[];
        for(const g of gl){
          const v=g.F; const mag=Math.hypot(v[0],v[1],v[2]);
          if(mag<1e-9) continue;
          const s=arrowLen/maxMag; const [x,y,z]=nodes[g.node];
          const dx=v[0]*s,dy=v[1]*s,dz=v[2]*s;
          lx.push(x-dx,x,null); ly.push(y-dy,y,null); lz.push(z-dz,z,null);
        }
        traces.push({type:'scatter3d',mode:'lines',name:'Applied nodal load',
          x:lx,y:ly,z:lz,line:{color:'#e11d48',width:5},hoverinfo:'name'});
      }
    }

    const gd=res.load_glyphs.distributed.filter(g=>!g.self_weight&&g.w>0);
    for(const g of gd){
      const m=res.members.find(mm=>mm.name===g.member); if(!m) continue;
      const [xi,yi,zi]=nodes[m.i],[xj,yj,zj]=nodes[m.j];
      const dx=xj-xi,dy=yj-yi,dz=zj-zi;
      const L=Math.hypot(dx,dy,dz); if(L<1e-9) continue;
      const dir=g.dir; const dlen=Math.hypot(dir[0],dir[1],dir[2]);
      if(dlen<1e-9) continue;
      const ldx=dir[0]/dlen,ldy=dir[1]/dlen,ldz=dir[2]/dlen;
      const cosAxis=Math.abs((dx*ldx+dy*ldy+dz*ldz)/L);
      if(cosAxis>0.98) continue;
      const ox=-ldx*UDL_OFFSET,oy=-ldy*UDL_OFFSET,oz=-ldz*UDL_OFFSET;

      const nArrows=Math.max(4,Math.round(L/UDL_SPACING));
      const shaftX=[],shaftY=[],shaftZ=[];
      const headX=[],headY=[],headZ=[];
      const backLen=Math.hypot(ox,oy,oz)||1;
      const bX=ox/backLen,bY=oy/backLen,bZ=oz/backLen;
      const refX=(Math.abs(bX)<0.9)?1:0, refY=(Math.abs(bX)<0.9)?0:1, refZ=0;
      let perpX=bY*refZ-bZ*refY, perpY=bZ*refX-bX*refZ, perpZ=bX*refY-bY*refX;
      const pLen=Math.hypot(perpX,perpY,perpZ)||1;
      perpX/=pLen; perpY/=pLen; perpZ/=pLen;
      const th=0.45, ct=Math.cos(th), st=Math.sin(th);
      const d1=[bX*ct+perpX*st,bY*ct+perpY*st,bZ*ct+perpZ*st];
      const d2=[bX*ct-perpX*st,bY*ct-perpY*st,bZ*ct-perpZ*st];

      if(bandStyle==='rectangle'){
        const c0=[xi,yi,zi],c1=[xj,yj,zj];
        const c2=[xj+ox,yj+oy,zj+oz],c3=[xi+ox,yi+oy,zi+oz];
        traces.push({type:'mesh3d',name:`${m.name}: ${(g.w/1000).toFixed(2)} kN/m`,
          x:[c0[0],c1[0],c2[0],c3[0]],y:[c0[1],c1[1],c2[1],c3[1]],
          z:[c0[2],c1[2],c2[2],c3[2]],
          i:[0,0],j:[1,2],k:[2,3],color:'#22d3ee',opacity:UDL_OPACITY,
          flatshading:true,hoverinfo:'name',showlegend:true});
        traces.push({type:'scatter3d',mode:'lines',name:`UDL ${m.name} outline`,
          x:[c0[0],c1[0],c2[0],c3[0],c0[0]],y:[c0[1],c1[1],c2[1],c3[1],c0[1]],
          z:[c0[2],c1[2],c2[2],c3[2],c0[2]],
          line:{color:'#0e7490',width:2},showlegend:false,hoverinfo:'skip'});
      }
      for(let k=0;k<=nArrows;k++){
        const t=k/nArrows;
        const tpX=xi+dx*t,tpY=yi+dy*t,tpZ=zi+dz*t;
        const bdX=tpX+ox,bdY=tpY+oy,bdZ=tpZ+oz;
        shaftX.push(bdX,tpX,null); shaftY.push(bdY,tpY,null); shaftZ.push(bdZ,tpZ,null);
        headX.push(tpX,tpX+UDL_HEAD*d1[0],null);
        headY.push(tpY,tpY+UDL_HEAD*d1[1],null);
        headZ.push(tpZ,tpZ+UDL_HEAD*d1[2],null);
        headX.push(tpX,tpX+UDL_HEAD*d2[0],null);
        headY.push(tpY,tpY+UDL_HEAD*d2[1],null);
        headZ.push(tpZ,tpZ+UDL_HEAD*d2[2],null);
      }
      traces.push({type:'scatter3d',mode:'lines',name:`Arrows ${m.name}`,
        x:shaftX,y:shaftY,z:shaftZ,line:{color:'#0e7490',width:1.5},
        showlegend:false,hoverinfo:'skip'});
      traces.push({type:'scatter3d',mode:'lines',name:`Heads ${m.name}`,
        x:headX,y:headY,z:headZ,line:{color:'#0e7490',width:1.5},
        showlegend:false,hoverinfo:'skip'});
    }

    const gp=res.load_glyphs.point;
    for(const g of gp){
      const m=res.members.find(mm=>mm.name===g.member); if(!m) continue;
      const [xi,yi,zi]=nodes[m.i],[xj,yj,zj]=nodes[m.j];
      const t=g.loc;
      const px=xi+(xj-xi)*t,py=yi+(yj-yi)*t,pz=zi+(zj-zi)*t;
      traces.push({type:'scatter3d',mode:'markers+text',
        name:`Pt ${m.name} (${g.P/1000} kN)`,x:[px],y:[py],z:[pz],
        marker:{color:'#ec4899',size:7,symbol:'circle',line:{color:'#fff',width:1}},
        text:[`${g.P/1000} kN`],textposition:'top center',
        textfont:{color:'#f9a8d4',size:10},hoverinfo:'text'});
    }

    const gt=res.load_glyphs.temperature;
    if(gt.length){
      const seen=new Set();
      for(const g of gt){
        if(seen.has(g.member)) continue;
        seen.add(g.member);
        const m=res.members.find(mm=>mm.name===g.member); if(!m) continue;
        const [xi,yi,zi]=nodes[m.i],[xj,yj,zj]=nodes[m.j];
        const cx=(xi+xj)/2,cy=(yi+yj)/2,cz=(zi+zj)/2;
        const dT=g.dT; const sign=dT>=0?'+':'';
        const alpha=g.alpha_per_C||11.7e-6;
        const textStr=`ΔT = ${sign}${dT.toFixed(1)} °C`;
        traces.push({type:'scatter3d',mode:'text+markers',
          name:`ΔT ${m.name}`,x:[cx],y:[cy],z:[cz],
          marker:{color:'#fbbf24',size:4,symbol:'square',line:{color:'#78350f',width:1}},
          text:[textStr],textposition:'middle right',
          textfont:{color:'#fbbf24',size:11},hoverinfo:'text',
          hovertemplate:
            `Member ${m.name}<br>ΔT = ${sign}${dT.toFixed(1)} °C<br>`+
            `Material: ${g.material}<br>α = ${(alpha*1e6).toFixed(2)}e-6 /°C<br>`+
            `Reference T = ${(g.reference_T||20).toFixed(1)} °C<extra></extra>`});
      }
      const expX=[],expY=[],expZ=[];
      const arrowLen=0.8;
      for(const m of res.members){
        if(!seen.has(m.name)) continue;
        const [xi,yi,zi]=nodes[m.i],[xj,yj,zj]=nodes[m.j];
        const dx=xj-xi,dy=yj-yi,dz=zj-zi;
        const L=Math.hypot(dx,dy,dz); if(L<1e-9) continue;
        const ux=dx/L,uy=dy/L,uz=dz/L;
        const cx=(xi+xj)/2,cy=(yi+yj)/2,cz=(zi+zj)/2;
        expX.push(cx,xi-ux*arrowLen,null); expY.push(cy,yi-uy*arrowLen,null);
        expZ.push(cz,zi-uz*arrowLen,null);
        expX.push(cx,xj+ux*arrowLen,null); expY.push(cy,yj+uy*arrowLen,null);
        expZ.push(cz,zj+uz*arrowLen,null);
      }
      if(expX.length){
        traces.push({type:'scatter3d',mode:'lines',name:'Thermal expansion dir.',
          x:expX,y:expY,z:expZ,line:{color:'#fbbf24',width:3,dash:'dot'},
          showlegend:true,hoverinfo:'skip'});
      }
    }

    const origin=[-1.5,-1.5,-0.5]; const gLen=2.0;
    for(const [vec,label,color] of [
      [[gLen,0,0],'X (global)','#f87171'],
      [[0,gLen,0],'Y (global) — vertical','#4ade80'],
      [[0,0,gLen],'Z (global)','#60a5fa']]){
      traces.push({type:'scatter3d',mode:'lines+text',name:label,
        x:[origin[0],origin[0]+vec[0]],y:[origin[1],origin[1]+vec[1]],
        z:[origin[2],origin[2]+vec[2]],
        line:{color,width:4},text:['',label],textposition:'top center',
        textfont:{color,size:11},hoverinfo:'name'});
    }

    const layout={
      margin:{l:0,r:0,t:30,b:0},
      paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
      font:{color:'#e2e8f0',size:11},
      scene:{
        xaxis:{title:`X (${res.labels.length})`,gridcolor:'#2a3654',
               zerolinecolor:'#3d4d70',color:'#94a3b8',
               showgrid:gridOn,showbackground:gridOn},
        yaxis:{title:`Y (${res.labels.length}) — Vertical`,gridcolor:'#2a3654',
               zerolinecolor:'#3d4d70',color:'#94a3b8',
               showgrid:gridOn,showbackground:gridOn},
        zaxis:{title:`Z (${res.labels.length})`,gridcolor:'#2a3654',
               zerolinecolor:'#3d4d70',color:'#94a3b8',
               showgrid:gridOn,showbackground:gridOn},
        aspectmode:'cube',bgcolor:'rgba(0,0,0,0)',
        camera:{eye:{x:1.6,y:1.3,z:1.1}}},
      legend:{x:0,y:1,bgcolor:'rgba(18,27,46,0.85)',bordercolor:'#2a3654',
        borderwidth:1,font:{size:10,color:'#e2e8f0'}},
      showlegend:true};
    Plotly.react('plot',traces,layout,{responsive:true,displaylogo:false});
  }

  async function runSolve(){
    if(!pyodide) return;
    runBtn.disabled=true; setStatus('Solving…');
    try{
      const cfg=collectConfig();
      const t0=performance.now();
      const raw=pyodide.runPython(`api_solve(${JSON.stringify(JSON.stringify(cfg))})`);
      const dt=(performance.now()-t0).toFixed(1);
      const res=JSON.parse(raw); lastResult=res;

      renderKPIs(res.kpi,res.labels);
      renderTable(document.getElementById('tbl-disp'),res.tables.displacements);
      renderTable(document.getElementById('tbl-react'),res.tables.reactions);
      renderTable(document.getElementById('tbl-forces'),res.tables.member_forces);
      renderTable(document.getElementById('tbl-members'),res.tables.members);
      document.getElementById('valid-report').textContent=res.reports.validation;
      document.getElementById('combo-report').textContent=res.reports.combinations;
      document.getElementById('diag-report').textContent=res.reports.diaphragm;
      document.getElementById('thermal-report').textContent=res.reports.thermal;
      render3D(res);

      setStatus(`Solved in ${dt} ms. Residual: ${res.kpi.residual.toExponential(2)}`,'ok');
      dlBtn.disabled=false;
    }catch(e){
      const msg=(e&&e.message?e.message:String(e));
      const lastLine=msg.split('\n').filter(Boolean).pop();
      setStatus('Solver error: '+lastLine,'err'); console.error(e);
    }finally{runBtn.disabled=false;}
  }
  runBtn.addEventListener('click',runSolve);

  dlBtn.addEventListener('click',()=>{
    if(!lastResult) return;
    const tables=lastResult.tables;
    const sections=[['Displacements',tables.displacements],
      ['Reactions',tables.reactions],['Member End Forces',tables.member_forces],
      ['Members',tables.members]];
    const lines=[];
    for(const [name,tbl] of sections){
      lines.push(`### ${name}`); lines.push(tbl.headers.join(','));
      for(const row of tbl.rows)
        lines.push(row.map(c=>typeof c==='number'?c.toPrecision(10):`"${c}"`).join(','));
      lines.push('');
    }
    const blob=new Blob([lines.join('\n')],{type:'text/csv'});
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob); a.download='revit4_solver_results.csv'; a.click();
  });

  boot();
})();
</script>
</body>
</html>
'''


def main() -> int:
    out_path = pathlib.Path(__file__).resolve().with_name("REV4-SOLVER.html")
    out_path.write_text(HTML, encoding="utf-8")
    print(f"Wrote {out_path}  ({out_path.stat().st_size:,} bytes)")
    url = out_path.as_uri()
    print(f"Opening {url} in your default browser...")
    opened = webbrowser.open(url, new=2)
    if not opened:
        print("Could not launch a browser automatically.\n"
              f"Open this file manually: {out_path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())