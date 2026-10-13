"""
app_pyqt.py  --  Cube Solver Rev 3 · PyQt6 Native Desktop Dashboard

Rewritten from the Streamlit app.py. The calculation, load application,
result helpers, and 3D rendering follow app.py; only the UI layer is PyQt6.

Requirements:
    pip install PyQt6 PyQt6-WebEngine plotly numpy pandas

Place this file in the SAME folder as your solver .py (ANY filename; it is
auto-detected). The solver resolves its Excel workbooks relative to its own
file location, so keep those beside the solver as usual.

Run with:  python app_pyqt.py
           python app_pyqt.py path/to/any_solver_name.py   (explicit solver)
"""

import html as _html
import math
import os
import shutil
import sys
import tempfile

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QComboBox, QFileDialog,
    QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QSplitter, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

# ==============================================================================
# FLEXIBLE SOLVER LOADER (works with any solver filename)
# ==============================================================================
import importlib.util

# Names the dashboard needs from the solver module.
REQUIRED_SOLVER_NAMES = (
    "build_rev3_reference_model", "build_rev3_diaphragm",
    "build_all_rev3_load_cases", "build_all_nscp_combinations",
    "NodalLoad", "MemberDistributedLoad", "MemberPointLoad", "TemperatureLoad",
    "_parse_direction", "DEFAULT_MATERIAL_LABEL", "DEFAULT_DESIGNATION",
)
# A .py file is treated as "the solver" if it defines all of these.
_SOLVER_SIGNATURE_DEFS = (
    "def build_rev3_reference_model", "def build_rev3_diaphragm",
    "def build_all_rev3_load_cases", "def build_all_nscp_combinations",
)


def find_solver_file() -> str:
    """Finds the solver file. Priority:
    1) path given on the command line:  python app_pyqt.py path/to/solver.py
    2) CUBE_SOLVER_PATH environment variable
    3) auto-detect: any other .py in this folder that defines the solver
       functions (any filename). If several match, the most recently
       modified one is used and the others are listed in the console.
    """
    here = os.path.dirname(os.path.abspath(__file__))

    explicit = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CUBE_SOLVER_PATH")
    if explicit:
        path = os.path.abspath(explicit)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Solver file not found: {path}")
        return path

    this_file = os.path.abspath(__file__)
    candidates = []
    for name in os.listdir(here):
        full = os.path.join(here, name)
        if not name.lower().endswith(".py") or os.path.abspath(full) == this_file:
            continue
        try:
            with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue
        if all(sig in text for sig in _SOLVER_SIGNATURE_DEFS):
            candidates.append(full)

    if not candidates:
        raise FileNotFoundError(
            f"No solver file found in: {here}\n"
            "Put your solver .py beside app_pyqt.py (any filename), or run:\n"
            "    python app_pyqt.py path/to/your_solver.py")

    candidates.sort(key=os.path.getmtime, reverse=True)
    if len(candidates) > 1:
        print("[app_pyqt] Multiple solver files found; using the newest:", file=sys.stderr)
        for c in candidates:
            print(f"    {'->' if c == candidates[0] else '  '} {os.path.basename(c)}",
                  file=sys.stderr)
        print("[app_pyqt] To pick another: python app_pyqt.py <solver_file.py>",
              file=sys.stderr)
    return candidates[0]


def load_solver_module(path: str):
    """Loads the solver from a file path and checks it has everything needed."""
    solver_dir = os.path.dirname(path)
    if solver_dir not in sys.path:
        sys.path.insert(0, solver_dir)      # lets the solver import its own helpers
    spec = importlib.util.spec_from_file_location("cube_solver_dynamic", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cube_solver_dynamic"] = mod    # needed by dataclasses inside the solver
    spec.loader.exec_module(mod)
    missing = [n for n in REQUIRED_SOLVER_NAMES if not hasattr(mod, n)]
    if missing:
        raise ImportError(
            f"{os.path.basename(path)} is missing names the dashboard needs: "
            + ", ".join(missing))
    return mod


SOLVER_PATH = find_solver_file()
_solver = load_solver_module(SOLVER_PATH)

build_rev3_reference_model = _solver.build_rev3_reference_model
build_rev3_diaphragm = _solver.build_rev3_diaphragm
build_all_rev3_load_cases = _solver.build_all_rev3_load_cases
build_all_nscp_combinations = _solver.build_all_nscp_combinations
NodalLoad = _solver.NodalLoad
MemberDistributedLoad = _solver.MemberDistributedLoad
MemberPointLoad = _solver.MemberPointLoad
TemperatureLoad = _solver.TemperatureLoad
_parse_direction = _solver._parse_direction
DEFAULT_MATERIAL_LABEL = _solver.DEFAULT_MATERIAL_LABEL
DEFAULT_DESIGNATION = _solver.DEFAULT_DESIGNATION

# ==============================================================================
# CONSTANTS (Rev 3 "Earthy Luxe" palette, same as app.py)
# ==============================================================================
PALETTE = {
    "canvas": "#FAF6E9",
    "canvas_alt": "#F5EEDB",
    "card": "#FFFDF7",
    "border": "#E0D4BA",
    "sidebar": "#F3ECD8",
    "primary": "#2F3B20",     # Forest Olive
    "primary_alt": "#4A6B22",
    "accent": "#C86A28",      # Warm Terracotta
    "muted": "#7A6F5A",
    "row_alt": "#FAF6E9",
    "grid_line": "#EFE7D1",
}

# 3D viewport colors
COLUMN_CLR = "#2F3B20"
BEAM_CLR = "#C86A28"
NODE_CLR = "#4E5D2A"
SUPPORT_CLR = "#E29D52"
DIAPHRAGM_CLR = "#2B5B7E"
LOAD_PURPLE = "#7B3FA0"
LOAD_BAND = "#C86A28"
LOCAL_X_CLR = "#B83A1B"       # local x (terracotta)
LOCAL_Y_CLR = "#4A6B22"       # local y (olive)
LOCAL_Z_CLR = "#2B5B7E"       # local z (slate)
GRID_CLR = PALETTE["border"]
GRID_BG = "rgba(224, 212, 186, 0.35)"
TEXT_CLR = PALETTE["primary"]

# Output is always metric (kN, mm, MPa) regardless of the unit toggle.
OUTPUT_LENGTH_LABEL = "m"
KN_TO_N = 1e3
DOF_NAMES = ["UX", "UY", "UZ", "RX", "RY", "RZ"]
EQUILIBRIUM_TOL_KN = 1e-3

QSS = f"""
QMainWindow {{ background-color: {PALETTE['canvas']}; }}
QWidget {{
    font-family: Georgia, 'Times New Roman', serif;
    color: {PALETTE['primary']};
    font-size: 13px;
}}
QWidget#Canvas {{ background-color: {PALETTE['canvas']}; }}
QWidget#ScrollInner {{ background-color: transparent; }}
QLabel {{ background: transparent; border: none; }}
QLabel#AppTitle {{ font-size: 24px; font-weight: bold; }}
QLabel#AppSubtitle {{ color: {PALETTE['muted']}; font-size: 12px; }}
QLabel#ModelChip {{
    background-color: {PALETTE['primary']}; color: {PALETTE['canvas']};
    border-radius: 10px; padding: 3px 10px; font-size: 12px;
}}
QLabel#StatusChip {{
    background-color: {PALETTE['sidebar']}; border: 1px solid {PALETTE['border']};
    border-radius: 10px; padding: 5px 12px; font-weight: bold;
}}
QLabel#SectionTitle {{ font-size: 14px; font-weight: bold; }}
QLabel#CardTitle {{
    color: {PALETTE['muted']}; font-size: 11px; letter-spacing: 1px;
}}
QLabel#Note {{ color: {PALETTE['muted']}; font-size: 12px; }}
QLabel#Caption {{ color: {PALETTE['muted']}; font-size: 12px; }}
QLabel#KPIValue {{ font-size: 20px; font-weight: 600; }}
QLabel#KPIValueAccent {{ font-size: 20px; font-weight: 600; color: {PALETTE['accent']}; }}

QFrame#Card {{
    background-color: {PALETTE['card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
}}
QFrame#KPICard {{
    background-color: {PALETTE['card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
}}
QFrame#KPISway {{
    background-color: #F6E3D2;
    border: 1px solid {PALETTE['border']};
    border-left: 4px solid {PALETTE['accent']};
    border-radius: 8px;
}}

QPushButton#RunButton {{
    background-color: {PALETTE['primary']}; color: {PALETTE['canvas']};
    border: none; border-radius: 8px; padding: 12px;
    font-size: 15px; font-weight: bold;
}}
QPushButton#RunButton:hover {{ background-color: {PALETTE['accent']}; }}
QPushButton#RunButton:disabled {{ background-color: {PALETTE['muted']}; }}
QPushButton#SecondaryButton {{
    background-color: transparent; color: {PALETTE['primary']};
    border: 1px solid {PALETTE['primary']}; border-radius: 8px;
    padding: 8px 14px; font-weight: bold;
}}
QPushButton#SecondaryButton:hover {{ background-color: {PALETTE['sidebar']}; }}

QComboBox, QLineEdit {{
    background-color: {PALETTE['card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 6px; padding: 6px 8px; color: {PALETTE['primary']};
}}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{
    background-color: {PALETTE['card']};
    selection-background-color: {PALETTE['sidebar']};
    selection-color: {PALETTE['primary']};
    border: 1px solid {PALETTE['border']};
}}

QCheckBox {{ color: {PALETTE['primary']}; spacing: 8px; padding: 2px 0px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border: 1px solid {PALETTE['muted']};
    border-radius: 4px; background-color: {PALETTE['card']};
}}
QCheckBox::indicator:checked {{
    background-color: {PALETTE['primary_alt']}; border-color: {PALETTE['primary_alt']};
}}

QScrollArea {{ border: none; background: transparent; }}

QTabWidget::pane {{
    border: 1px solid {PALETTE['border']};
    background-color: {PALETTE['card']}; border-radius: 8px;
}}
QTabBar::tab {{
    background-color: {PALETTE['sidebar']}; color: {PALETTE['muted']};
    border: 1px solid {PALETTE['border']};
    padding: 8px 16px; margin-right: 4px;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background-color: {PALETTE['card']}; color: {PALETTE['primary']};
    font-weight: bold; border-bottom-color: {PALETTE['card']};
}}

QTableWidget {{
    background-color: {PALETTE['card']};
    alternate-background-color: {PALETTE['row_alt']};
    gridline-color: {PALETTE['grid_line']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
    color: {PALETTE['primary']};
}}
QHeaderView::section {{
    background-color: {PALETTE['sidebar']}; color: {PALETTE['primary']};
    padding: 6px 10px; border: none;
    border-bottom: 1px solid {PALETTE['border']}; font-weight: bold;
}}

QSplitter::handle {{ background-color: {PALETTE['border']}; }}
QSplitter::handle:horizontal {{ width: 6px; }}
QSplitter::handle:vertical {{ height: 6px; }}

QToolTip {{
    background-color: {PALETTE['card']}; color: {PALETTE['primary']};
    border: 1px solid {PALETTE['border']}; padding: 6px;
}}
"""


# ==============================================================================
# SOLVER HELPERS (identical logic to app.py)
# ==============================================================================
def _check_load_types(case) -> None:
    """Guards against objects that do not match the solver's load classes."""
    for nl in case.nodal_loads:
        if not isinstance(nl, NodalLoad):
            raise TypeError(f"LC{case.id}: nodal load has unexpected type {type(nl).__name__}")
    for dl in case.distributed_loads:
        if not isinstance(dl, MemberDistributedLoad):
            raise TypeError(f"LC{case.id}: distributed load has unexpected type {type(dl).__name__}")
    for pl in case.point_loads:
        if not isinstance(pl, MemberPointLoad):
            raise TypeError(f"LC{case.id}: point load has unexpected type {type(pl).__name__}")
    for tl in case.temperature_loads:
        if not isinstance(tl, TemperatureLoad):
            raise TypeError(f"LC{case.id}: temperature load has unexpected type {type(tl).__name__}")


def _dir_vec(direction: str) -> np.ndarray:
    """Global unit vector for a direction string such as 'X', '-Y', 'Z'."""
    axis, sign = _parse_direction(direction)
    v = np.zeros(3)
    v[axis] = sign
    return v


def _member_geom(model, mid):
    m = model.members[mid]
    pi = model.nodes[m["i"]]
    pj = model.nodes[m["j"]]
    L = float(np.linalg.norm(pj - pi))
    t = (pj - pi) / L
    return m, pi, pj, L, t


def _add_node_vector(model, nid, F, M=(0.0, 0.0, 0.0)):
    """Adds a force (N) and moment (N·m) vector to a node in global axes."""
    model.add_node_load(nid, F[0], F[1], F[2], M[0], M[1], M[2])


def _apply_distributed(model, dl, factor):
    """Uniform member load w (kN/m, global direction) converted to consistent
    fixed-end nodal loads: F = w·L/2 at each end; M_i = (L²/12)·(t × w),
    M_j = -M_i (with t the unit vector from node i to node j)."""
    m, pi, pj, L, t = _member_geom(model, dl.member_id)
    w_vec = _dir_vec(dl.direction) * dl.magnitude_kNm * KN_TO_N * factor   # N/m
    F_end = w_vec * (L / 2.0)
    M_i = (L ** 2 / 12.0) * np.cross(t, w_vec)
    _add_node_vector(model, m["i"], F_end, M_i)
    _add_node_vector(model, m["j"], F_end, -M_i)


def _apply_point(model, pl, factor):
    """Point load P at fraction a of the span. The transverse part uses the
    solver's MemberPointLoad.equivalent_nodal_loads(); the axial part is split
    linearly (P·(1-a) at i, P·a at j)."""
    m, pi, pj, L, t = _member_geom(model, pl.member_id)
    P_vec = _dir_vec(pl.direction) * pl.magnitude_kN * KN_TO_N * factor   # N
    a = pl.location_fraction

    P_ax = float(np.dot(P_vec, t))
    P_tr = P_vec - P_ax * t
    F_i = P_ax * (1.0 - a) * t
    F_j = P_ax * a * t
    M_i = np.zeros(3)
    M_j = np.zeros(3)

    P_tr_kN = float(np.linalg.norm(P_tr)) / KN_TO_N
    if P_tr_kN > 0.0:
        u = P_tr / np.linalg.norm(P_tr)
        transverse = MemberPointLoad(pl.member_id, a, pl.direction, P_tr_kN)
        Fi, Mi, Fj, Mj = transverse.equivalent_nodal_loads(L)   # kN, kN·m
        tu = np.cross(t, u)
        F_i = F_i + Fi * KN_TO_N * u
        F_j = F_j + Fj * KN_TO_N * u
        M_i = M_i + Mi * KN_TO_N * tu
        M_j = M_j - Mj * KN_TO_N * tu

    _add_node_vector(model, m["i"], F_i, M_i)
    _add_node_vector(model, m["j"], F_j, M_j)


def _apply_thermal(model, tl, factor, material_cfg):
    """Self-equilibrating axial thermal pair from TemperatureLoad, scaled by the
    combination factor (ΔT·factor), applied along the member axis."""
    m, pi, pj, L, t = _member_geom(model, tl.member_id)
    alpha = tl.alpha_perC if tl.alpha_perC is not None else material_cfg.therm_coeff_perC
    Fi_kN, Fj_kN = tl.fe_thermal_load_vector_kN(m["E"], m["A"], alpha_per_C=alpha)
    _add_node_vector(model, m["i"], (Fi_kN * KN_TO_N * factor) * t)
    _add_node_vector(model, m["j"], (Fj_kN * KN_TO_N * factor) * t)


def apply_contributions_to_model(model, contributions, material_cfg) -> None:
    """Clears model.loads, then applies the net load of all contributing cases.
    Each case's loads are multiplied by its factor (1.0 for a single load case)."""
    model.loads = {}
    for case, factor in contributions:
        for nl in case.nodal_loads:
            vec = np.array([nl.fx, nl.fy, nl.fz]) * KN_TO_N * factor
            mom = np.array([nl.mx, nl.my, nl.mz]) * KN_TO_N * factor
            _add_node_vector(model, nl.node_id, vec, mom)
        for dl in case.distributed_loads:
            _apply_distributed(model, dl, factor)
        for pl in case.point_loads:
            _apply_point(model, pl, factor)
        for tl in case.temperature_loads:
            _apply_thermal(model, tl, factor, material_cfg)


def node_dofs(res, nid):
    idx = res["node_map"][nid] * 6
    return res["U_global"][idx:idx + 6]


def node_reactions(res, nid):
    idx = res["node_map"][nid] * 6
    return res["Reactions"][idx:idx + 6]


def support_nodes(model):
    return sorted(model.supports.keys())


def compute_kpis(model, res):
    sup = support_nodes(model)
    sum_fx = sum(node_reactions(res, n)[0] for n in sup) / KN_TO_N
    sum_fy = sum(node_reactions(res, n)[1] for n in sup) / KN_TO_N
    sum_fz = sum(node_reactions(res, n)[2] for n in sup) / KN_TO_N

    # Sway = horizontal translation (X–Z plane); Y is vertical in this solver.
    best_nid, best_sway = None, -1.0
    for nid in model.nodes:
        u = node_dofs(res, nid)
        horiz = math.hypot(u[0], u[2])
        if horiz > best_sway:
            best_sway, best_nid = horiz, nid

    return {
        "sum_fx": sum_fx, "sum_fy": sum_fy, "sum_fz": sum_fz,
        "max_sway_mm": best_sway * 1e3, "max_sway_node": best_nid,
    }


def equilibrium_residual_kN(model, res) -> float:
    """Σ applied forces + Σ all-node reactions. Should be ≈ 0 for a valid solve."""
    applied = np.zeros(3)
    for vec in model.loads.values():
        applied += np.asarray(vec)[:3]
    reac = np.zeros(3)
    for nid in model.nodes:
        reac += node_reactions(res, nid)[:3]
    return float(np.linalg.norm(applied + reac)) / KN_TO_N


def build_displacement_df(model, res) -> pd.DataFrame:
    rows = []
    for nid in sorted(model.nodes):
        u = node_dofs(res, nid)
        rows.append({
            "Node": f"N{nid}",
            "Restraint": "Pinned" if nid in model.supports else "Free",
            "UX (mm)": f"{u[0] * 1e3:.4f}",
            "UY (mm)": f"{u[1] * 1e3:.4f}",
            "UZ (mm)": f"{u[2] * 1e3:.4f}",
            "RX (rad)": f"{u[3]:.6e}",
            "RY (rad)": f"{u[4]:.6e}",
            "RZ (rad)": f"{u[5]:.6e}",
        })
    return pd.DataFrame(rows)


def build_reaction_df(model, res) -> pd.DataFrame:
    rows = []
    for nid in support_nodes(model):
        r = node_reactions(res, nid)
        restrained = ", ".join(DOF_NAMES[d] for d, flag in enumerate(model.supports[nid]) if flag)
        rows.append({
            "Support Node": f"N{nid}",
            "Restrained DOFs": restrained,
            "FX (kN)": f"{r[0] / KN_TO_N:,.3f}",
            "FY (kN)": f"{r[1] / KN_TO_N:,.3f}",
            "FZ (kN)": f"{r[2] / KN_TO_N:,.3f}",
            "MX (kN·m)": f"{r[3] / KN_TO_N:,.3f}",
            "MY (kN·m)": f"{r[4] / KN_TO_N:,.3f}",
            "MZ (kN·m)": f"{r[5] / KN_TO_N:,.3f}",
        })
    return pd.DataFrame(rows)


def build_member_actions_df(model, res) -> pd.DataFrame:
    rows = []
    for mid in sorted(model.members):
        m = model.members[mid]
        f = res["MemberForces"][mid]
        rows.append({
            "Member": f"M{mid}",
            "Type": m["type"],
            "Node i": f"N{m['i']}",
            "P_i (kN)": f"{f[0] / KN_TO_N:,.3f}",
            "Vy_i (kN)": f"{f[1] / KN_TO_N:,.3f}",
            "Vz_i (kN)": f"{f[2] / KN_TO_N:,.3f}",
            "T_i (kN·m)": f"{f[3] / KN_TO_N:,.3f}",
            "My_i (kN·m)": f"{f[4] / KN_TO_N:,.3f}",
            "Mz_i (kN·m)": f"{f[5] / KN_TO_N:,.3f}",
            "Node j": f"N{m['j']}",
            "P_j (kN)": f"{f[6] / KN_TO_N:,.3f}",
            "Vy_j (kN)": f"{f[7] / KN_TO_N:,.3f}",
            "Vz_j (kN)": f"{f[8] / KN_TO_N:,.3f}",
            "T_j (kN·m)": f"{f[9] / KN_TO_N:,.3f}",
            "My_j (kN·m)": f"{f[10] / KN_TO_N:,.3f}",
            "Mz_j (kN·m)": f"{f[11] / KN_TO_N:,.3f}",
        })
    return pd.DataFrame(rows)


def member_length(model, mid) -> float:
    m = model.members[mid]
    return float(np.linalg.norm(model.nodes[m["j"]] - model.nodes[m["i"]]))


# ==============================================================================
# PLOTLY 3D RENDERING (identical logic to app.py, sized for QWebEngineView)
# ==============================================================================
def _to_plotly(v):
    """Solver (X, Y-up, Z) -> Plotly (x, y, z). Solver Y maps to Plotly z."""
    return float(v[0]), float(v[2]), float(v[1])


def model_span(model) -> float:
    pts = np.array([_to_plotly(c) for c in model.nodes.values()])
    return float(np.ptp(pts, axis=0).max()) or 1.0


def _pyramid_mesh(apex, half_base, height):
    ax_, ay_, az_ = apex
    bz = az_ - height
    base = [
        (ax_ - half_base, ay_ - half_base, bz),
        (ax_ + half_base, ay_ - half_base, bz),
        (ax_ + half_base, ay_ + half_base, bz),
        (ax_ - half_base, ay_ + half_base, bz),
    ]
    verts = [apex] + base
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 2, 3), (1, 3, 4)]
    return verts, faces


def _unique_ticks(values):
    ticks = sorted({round(float(v), 6) for v in values})
    return ticks, [f"{t:g}" for t in ticks]


def _axis_style(title, ticks, labels, show_grid):
    return dict(
        title=dict(text=title, font=dict(color=TEXT_CLR, size=12)),
        tickvals=ticks,
        ticktext=labels,
        tickfont=dict(color=TEXT_CLR, size=11),
        showgrid=show_grid,
        gridcolor=GRID_CLR,
        gridwidth=1,
        showline=True,
        linecolor=GRID_CLR,
        zeroline=False,
        showbackground=show_grid,
        backgroundcolor=GRID_BG,
        showspikes=False,
    )


def build_load_glyphs(model, contributions, show_nodal, show_uniform, show_point, show_thermal):
    """Converts the active selection into plot-ready geometry (Plotly coordinates).
    Only load types whose toggle is on are included. Does not touch model.loads."""
    span = model_span(model)
    raw_arrows, raw_bands, raw_thermal = [], [], []

    for case, f in contributions:
        if show_nodal:
            for nl in case.nodal_loads:
                vec = np.array([nl.fx, nl.fy, nl.fz]) * f
                mag = float(np.linalg.norm(vec))
                if mag > 1e-9:
                    raw_arrows.append({
                        "pos": model.nodes[nl.node_id], "vec": vec, "mag": mag,
                        "text": f"Nodal load at N{nl.node_id}: {mag:,.2f} kN",
                    })

        if show_point:
            for pl in case.point_loads:
                m = model.members[pl.member_id]
                pi, pj = model.nodes[m["i"]], model.nodes[m["j"]]
                pos = pi + pl.location_fraction * (pj - pi)
                vec = _dir_vec(pl.direction) * pl.magnitude_kN * f
                mag = float(np.linalg.norm(vec))
                if mag > 1e-9:
                    raw_arrows.append({
                        "pos": pos, "vec": vec, "mag": mag,
                        "text": f"Point load on M{pl.member_id}: {mag:,.2f} kN",
                    })

        if show_uniform:
            for dl in case.distributed_loads:
                m = model.members[dl.member_id]
                w = dl.magnitude_kNm * f
                if abs(w) > 1e-9:
                    raw_bands.append({
                        "pi": model.nodes[m["i"]], "pj": model.nodes[m["j"]],
                        "dir": _dir_vec(dl.direction), "w": w,
                        "text": f"Uniform load on M{dl.member_id}: {w:+,.2f} kN/m",
                    })

        if show_thermal:
            for tl in case.temperature_loads:
                m = model.members[tl.member_id]
                dT = tl.delta_T * f
                raw_thermal.append({
                    "pi": model.nodes[m["i"]], "pj": model.nodes[m["j"]],
                    "dT": dT, "text": f"ΔT on M{tl.member_id}: {dT:+.2f} °C",
                })

    # Arrows: length scaled by magnitude (min 35% of base length for visibility)
    arrow_base = 0.22 * span
    max_force = max([a["mag"] for a in raw_arrows] or [1.0])
    arrows = []
    for a in raw_arrows:
        unit_plot = _to_plotly(a["vec"] / a["mag"])
        length = arrow_base * (0.35 + 0.65 * a["mag"] / max_force)
        arrows.append({
            "tip": _to_plotly(a["pos"]),
            "unit": unit_plot,
            "length": length,
            "text": a["text"],
        })

    # Uniform bands: offset along the load direction, sign follows the factor
    band_base = 0.18 * span
    max_w = max([abs(b["w"]) for b in raw_bands] or [1.0])
    bands = []
    for b in raw_bands:
        h = band_base * (0.35 + 0.65 * abs(b["w"]) / max_w)
        direction = b["dir"] * np.sign(b["w"])
        bands.append({
            "p1": _to_plotly(b["pi"]),
            "p2": _to_plotly(b["pj"]),
            "offset": tuple(np.array(_to_plotly(direction)) * h),
            "text": b["text"],
        })

    thermal = []
    for t in raw_thermal:
        p1, p2 = _to_plotly(t["pi"]), _to_plotly(t["pj"])
        mid = tuple((np.array(p1) + np.array(p2)) / 2.0)
        thermal.append({"p1": p1, "p2": p2, "mid": mid, "text": t["text"],
                        "label": f"ΔT {t['dT']:+.1f} °C"})

    return {"arrows": arrows, "bands": bands, "thermal": thermal, "span": span}


def _add_load_traces(fig, glyphs):
    # --- Nodal and point load arrows (purple) ---------------------------------
    arrows = glyphs["arrows"]
    if arrows:
        lx, ly, lz = [], [], []
        cx, cy, cz, cu, cv, cw, ct = [], [], [], [], [], [], []
        for a in arrows:
            tip = np.array(a["tip"])
            unit = np.array(a["unit"])
            tail = tip - unit * a["length"]
            lx += [tail[0], tip[0], None]
            ly += [tail[1], tip[1], None]
            lz += [tail[2], tip[2], None]
            cx.append(tip[0]); cy.append(tip[1]); cz.append(tip[2])
            cu.append(unit[0]); cv.append(unit[1]); cw.append(unit[2])
            ct.append(a["text"])
        fig.add_trace(go.Scatter3d(
            x=lx, y=ly, z=lz, mode="lines",
            line=dict(color=LOAD_PURPLE, width=6),
            name="Applied forces", hoverinfo="skip",
        ))
        fig.add_trace(go.Cone(
            x=cx, y=cy, z=cz, u=cu, v=cv, w=cw,
            anchor="tip", sizemode="absolute", sizeref=0.07 * glyphs["span"],
            colorscale=[[0, LOAD_PURPLE], [1, LOAD_PURPLE]],
            cmin=0, cmax=1, showscale=False,
            hovertext=ct, hoverinfo="text", showlegend=False,
        ))

    # --- Uniform load bands (terracotta) --------------------------------------
    bands = glyphs["bands"]
    if bands:
        vx, vy, vz, fi, fj, fk = [], [], [], [], [], []
        ex, ey, ez = [], [], []
        for b in bands:
            p1, p2 = np.array(b["p1"]), np.array(b["p2"])
            off = np.array(b["offset"])
            base = len(vx)
            for p in (p1, p2, p2 + off, p1 + off):
                vx.append(p[0]); vy.append(p[1]); vz.append(p[2])
            fi += [base, base]
            fj += [base + 1, base + 2]
            fk += [base + 2, base + 3]
            for a_pt, b_pt in ((p1, p2), (p1 + off, p2 + off)):
                ex += [a_pt[0], b_pt[0], None]
                ey += [a_pt[1], b_pt[1], None]
                ez += [a_pt[2], b_pt[2], None]
        fig.add_trace(go.Mesh3d(
            x=vx, y=vy, z=vz, i=fi, j=fj, k=fk,
            color=LOAD_BAND, opacity=0.4, flatshading=True,
            name="Uniform loads", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter3d(
            x=ex, y=ey, z=ez, mode="lines",
            line=dict(color=LOAD_BAND, width=4),
            hoverinfo="skip", showlegend=False,
        ))

    # --- Thermal overlays (terracotta dashed member + ΔT label) ---------------
    thermal = glyphs["thermal"]
    if thermal:
        tx, ty, tz = [], [], []
        mx, my, mz, mt = [], [], [], []
        for t in thermal:
            tx += [t["p1"][0], t["p2"][0], None]
            ty += [t["p1"][1], t["p2"][1], None]
            tz += [t["p1"][2], t["p2"][2], None]
            mx.append(t["mid"][0]); my.append(t["mid"][1]); mz.append(t["mid"][2])
            mt.append(t["label"])
        fig.add_trace(go.Scatter3d(
            x=tx, y=ty, z=tz, mode="lines",
            line=dict(color=LOAD_BAND, width=5, dash="dash"),
            name="Thermal loads", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter3d(
            x=mx, y=my, z=mz, mode="text", text=mt,
            textfont=dict(color=LOAD_BAND, size=11),
            hoverinfo="skip", showlegend=False,
        ))


def _local_axes_traces(model, mid):
    """Local x/y/z triad at the midpoint of a selected member.

    Directions come directly from the solver:
        R, L, cx, cy, cz = model.compute_local_axes(mid)
    The rows of R are the global direction vectors of the local x, y, z axes
    (solver coordinates, Y-up), so they are converted with _to_plotly.
    cx, cy, cz are the member's direction cosines (not coordinates) and are
    not used for placement; the origin is the midpoint of nodes i and j.
    The triad length is a visual proportion of the model span (0.12 * span).
    """
    try:
        R, _L, _cx, _cy, _cz = model.compute_local_axes(mid)
    except Exception:
        return []

    R = np.asarray(R, dtype=float)
    span = model_span(model)
    m = model.members[mid]
    origin = (model.nodes[m["i"]] + model.nodes[m["j"]]) / 2.0
    length = 0.12 * span
    o = _to_plotly(origin)

    traces = []
    for k, (name, clr) in enumerate((("x", LOCAL_X_CLR),
                                     ("y", LOCAL_Y_CLR),
                                     ("z", LOCAL_Z_CLR))):
        d = R[k] / np.linalg.norm(R[k])
        p = _to_plotly(origin + d * length)
        traces.append(go.Scatter3d(
            x=[o[0], p[0]], y=[o[1], p[1]], z=[o[2], p[2]],
            mode="lines+text", text=["", f"{name}'"],
            line=dict(color=clr, width=7),
            textfont=dict(color=clr, size=12),
            textposition="top center",
            name=f"Local {name}", hoverinfo="skip", showlegend=False,
        ))
    return traces


def draw_3d_model(model, show_nodes=True, show_members=True, show_grid=True,
                  show_supports=True, show_diaphragm=False, diaphragm=None,
                  load_glyphs=None, local_member=None) -> go.Figure:
    fig = go.Figure()

    if show_members:
        for mtype, color, legend in (("Column", COLUMN_CLR, "Columns"),
                                     ("Beam", BEAM_CLR, "Beams")):
            xs, ys, zs, hover = [], [], [], []
            for mid, m in model.members.items():
                if m["type"] != mtype:
                    continue
                for nid in (m["i"], m["j"]):
                    x, y, z = _to_plotly(model.nodes[nid])
                    xs.append(x); ys.append(y); zs.append(z)
                    hover.append(f"M{mid} · {mtype}")
                xs.append(None); ys.append(None); zs.append(None); hover.append(None)
            if xs:
                fig.add_trace(go.Scatter3d(
                    x=xs, y=ys, z=zs, mode="lines",
                    line=dict(color=color, width=8), name=legend,
                    hovertext=hover, hoverinfo="text",
                ))

    pinned_ids = {n for n, r in model.supports.items() if any(r[:3])}
    free_ids = [n for n in model.nodes if n not in pinned_ids]

    if show_nodes and free_ids:
        pts = np.array([_to_plotly(model.nodes[n]) for n in free_ids])
        fig.add_trace(go.Scatter3d(
            x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
            mode="markers+text",
            marker=dict(size=6, color=NODE_CLR, line=dict(color=PALETTE["canvas"], width=1)),
            text=[f"N{n}" for n in free_ids],
            textposition="top center",
            textfont=dict(color=TEXT_CLR, size=11),
            name="Free nodes",
            hovertemplate="%{text}<extra></extra>",
        ))

    if show_supports and pinned_ids:
        pinned = sorted(pinned_ids)
        pts = np.array([_to_plotly(model.nodes[n]) for n in pinned])
        span = model_span(model)
        half_base, height = 0.06 * span, 0.12 * span
        all_v, all_i, all_j, all_k = [], [], [], []
        for apex in pts:
            verts, faces = _pyramid_mesh(tuple(apex), half_base, height)
            offset = len(all_v)
            all_v.extend(verts)
            for a, b, c in faces:
                all_i.append(offset + a); all_j.append(offset + b); all_k.append(offset + c)
        all_v = np.array(all_v)
        fig.add_trace(go.Mesh3d(
            x=all_v[:, 0], y=all_v[:, 1], z=all_v[:, 2],
            i=all_i, j=all_j, k=all_k,
            color=SUPPORT_CLR, flatshading=True,
            name="Pinned supports", hoverinfo="skip", showscale=False,
        ))

    if show_diaphragm and diaphragm is not None:
        d_nodes = [diaphragm.master_node] + list(diaphragm.slave_nodes)
        pts = np.array([_to_plotly(model.nodes[n]) for n in d_nodes])
        cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
        order = sorted(range(len(d_nodes)),
                       key=lambda idx: math.atan2(pts[idx, 1] - cy, pts[idx, 0] - cx))
        ring = order + [order[0]]
        fig.add_trace(go.Scatter3d(
            x=pts[ring, 0], y=pts[ring, 1], z=pts[ring, 2],
            mode="lines", line=dict(color=DIAPHRAGM_CLR, width=4, dash="dash"),
            name="Diaphragm perimeter", hoverinfo="skip",
        ))
        slave_idx = list(range(1, len(d_nodes)))
        fig.add_trace(go.Scatter3d(
            x=pts[slave_idx, 0], y=pts[slave_idx, 1], z=pts[slave_idx, 2],
            mode="markers+text",
            marker=dict(size=9, color=DIAPHRAGM_CLR, symbol="square",
                        line=dict(color=PALETTE["canvas"], width=1)),
            text=[f"N{n}" for n in diaphragm.slave_nodes],
            textposition="top center",
            textfont=dict(color=DIAPHRAGM_CLR, size=11),
            name="Diaphragm slaves",
            hovertemplate="Slave %{text}<extra></extra>",
        ))
        mx, my, mz = pts[0]
        fig.add_trace(go.Scatter3d(
            x=[mx], y=[my], z=[mz], mode="markers+text",
            marker=dict(size=13, color=DIAPHRAGM_CLR, symbol="diamond",
                        line=dict(color=PALETTE["canvas"], width=1.5)),
            text=[f"Master N{diaphragm.master_node}"],
            textposition="top center",
            textfont=dict(color=DIAPHRAGM_CLR, size=12),
            name="Diaphragm master",
            hovertemplate="%{text}<extra></extra>",
        ))

    if load_glyphs:
        _add_load_traces(fig, load_glyphs)

    if local_member is not None and local_member in model.members:
        for tr in _local_axes_traces(model, local_member):
            fig.add_trace(tr)

    all_pts = np.array([_to_plotly(c) for c in model.nodes.values()])
    x_t, x_l = _unique_ticks(all_pts[:, 0])
    y_t, y_l = _unique_ticks(all_pts[:, 1])
    z_t, z_l = _unique_ticks(all_pts[:, 2])
    unit = OUTPUT_LENGTH_LABEL

    fig.update_layout(
        scene=dict(
            xaxis=_axis_style(f"X ({unit})", x_t, x_l, show_grid),
            yaxis=_axis_style(f"Z ({unit})", y_t, y_l, show_grid),
            zaxis=_axis_style(f"Y ({unit}) · Vertical", z_t, z_l, show_grid),
            aspectmode="data",
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.5, y=-1.6, z=0.9)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Georgia, serif", color=TEXT_CLR),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0.0,
            bgcolor="rgba(255,253,247,0.85)", bordercolor=GRID_CLR, borderwidth=1,
            font=dict(color=TEXT_CLR, size=11),
        ),
        margin=dict(l=0, r=0, t=36, b=0),
        hoverlabel=dict(bgcolor=PALETTE["card"], bordercolor=GRID_CLR,
                        font=dict(color=TEXT_CLR)),
        showlegend=True,
    )
    return fig


# ==============================================================================
# TABLE HELPERS (locked: no edit, no drag, no sort, auto-sized columns)
# ==============================================================================
def make_locked_table() -> QTableWidget:
    t = QTableWidget()
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setDragEnabled(False)
    t.setAcceptDrops(False)
    t.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
    t.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
    t.setSortingEnabled(False)
    t.setAlternatingRowColors(True)
    t.setWordWrap(False)
    t.verticalHeader().setVisible(False)
    h = t.horizontalHeader()
    h.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    h.setStretchLastSection(False)
    h.setSectionsMovable(False)
    t.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    t.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    return t


def set_table_df(table: QTableWidget, df) -> None:
    table.setUpdatesEnabled(False)
    table.clearContents()
    table.setRowCount(0)
    table.setColumnCount(0)
    if df is None or df.empty:
        table.setUpdatesEnabled(True)
        return
    table.setRowCount(len(df))
    table.setColumnCount(len(df.columns))
    table.setHorizontalHeaderLabels([str(c) for c in df.columns])
    for r, row in enumerate(df.itertuples(index=False)):
        for c, val in enumerate(row):
            item = QTableWidgetItem(str(val))
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)   # read-only
            table.setItem(r, c, item)
    table.setUpdatesEnabled(True)


# ==============================================================================
# MAIN WINDOW
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Cube Solver Rev 3  ·  {os.path.basename(SOLVER_PATH)}")
        self.resize(1480, 920)
        self.setStyleSheet(QSS)

        self.unit_system = "Metric"
        self.model = None
        self.material_cfg = None
        self.section_cfg = None
        self.diaphragm = None
        self.load_cases = None
        self.load_combinations = None
        self.model_unit = None
        self.res = None
        self.res_key = None
        self._disp_df = None

        self._plot_dir = tempfile.mkdtemp(prefix="cube_rev3_")
        self._write_plotlyjs()

        self.ensure_model(self.unit_system)
        self._build_ui()
        self.populate_selection_combo()
        self.populate_member_combo()
        self.refresh_results()
        self.update_plot()

    # ------------------------------------------------------------------ setup
    def _write_plotlyjs(self):
        with open(os.path.join(self._plot_dir, "plotly.min.js"), "w", encoding="utf-8") as fh:
            fh.write(get_plotlyjs())

    def ensure_model(self, unit_system: str) -> None:
        """Builds the reference model, its diaphragm, and all load data.
        Called at session start and whenever the unit system changes."""
        solver, material_cfg, _units_cfg, section_cfg = build_rev3_reference_model(unit_system)
        self.model = solver
        self.material_cfg = material_cfg
        self.section_cfg = section_cfg
        self.diaphragm = build_rev3_diaphragm(solver)
        self.load_cases = build_all_rev3_load_cases(solver, material_cfg)
        self.load_combinations = build_all_nscp_combinations()
        self.model_unit = unit_system
        self.res = None
        self.res_key = None

    def _card(self, title=None, object_name="Card"):
        frame = QFrame()
        frame.setObjectName(object_name)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)
        if title:
            lbl = QLabel(title)
            lbl.setObjectName("SectionTitle")
            lay.addWidget(lbl)
        return frame, lay

    def _kpi(self, label, note, sway=False):
        frame = QFrame()
        frame.setObjectName("KPISway" if sway else "KPICard")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        title = QLabel(label.upper())
        title.setObjectName("CardTitle")
        val = QLabel("–")
        val.setObjectName("KPIValueAccent" if sway else "KPIValue")
        note_lbl = QLabel(note)
        note_lbl.setObjectName("Note")
        note_lbl.setWordWrap(True)
        lay.addWidget(title)
        lay.addWidget(val)
        lay.addWidget(note_lbl)
        return frame, val, note_lbl

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("Canvas")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 14, 16, 12)
        root.setSpacing(10)

        root.addLayout(self._build_header())

        v_split = QSplitter(Qt.Orientation.Vertical)
        h_split = QSplitter(Qt.Orientation.Horizontal)
        h_split.addWidget(self._build_left_panel())
        h_split.addWidget(self._build_viewport())
        h_split.addWidget(self._build_right_panel())
        h_split.setSizes([290, 830, 360])
        h_split.setStretchFactor(1, 1)
        v_split.addWidget(h_split)
        v_split.addWidget(self._build_bottom_tabs())
        v_split.setSizes([580, 280])
        root.addWidget(v_split, 1)

        self.statusBar().showMessage(
            f"Solver: {os.path.basename(SOLVER_PATH)}  |  "
            "Ready. Select a load case, then Run Analysis.")

    def _build_header(self):
        hdr = QHBoxLayout()
        hdr.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        lbl_title = QLabel("Cube Solver Rev 3")
        lbl_title.setObjectName("AppTitle")
        sub_row = QHBoxLayout()
        sub = QLabel("3D Space Frame Analysis · Direct Stiffness Method")
        sub.setObjectName("AppSubtitle")
        self.lbl_model = QLabel("Reference Model (Rev 3)")
        self.lbl_model.setObjectName("ModelChip")
        sub_row.addWidget(sub)
        sub_row.addWidget(self.lbl_model)
        sub_row.addStretch()
        title_col.addWidget(lbl_title)
        title_col.addLayout(sub_row)
        hdr.addLayout(title_col)
        hdr.addStretch()

        self.lbl_status = QLabel("Not solved")
        self.lbl_status.setObjectName("StatusChip")
        hdr.addWidget(self.lbl_status)

        unit_col = QVBoxLayout()
        unit_col.setSpacing(0)
        lbl_unit = QLabel("Unit System")
        lbl_unit.setObjectName("CardTitle")
        self.cb_unit = QComboBox()
        self.cb_unit.addItems(["Metric", "Imperial"])
        self.cb_unit.setToolTip("Input unit system. Results are always shown in metric (kN, mm, MPa).")
        self.cb_unit.currentTextChanged.connect(self.on_unit_changed)
        unit_col.addWidget(lbl_unit)
        unit_col.addWidget(self.cb_unit)
        hdr.addLayout(unit_col)

        self.btn_export = QPushButton("Export Report")
        self.btn_export.setObjectName("SecondaryButton")
        self.btn_export.clicked.connect(self.export_report)
        hdr.addWidget(self.btn_export, alignment=Qt.AlignmentFlag.AlignBottom)
        return hdr

    def _build_left_panel(self):
        inner = QWidget()
        inner.setObjectName("ScrollInner")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 6, 0)
        lay.setSpacing(10)

        # Model properties
        card, cl = self._card("Model Properties")
        cl.addWidget(QLabel("Material"))
        self.cb_material = QComboBox()
        self.cb_material.addItem(DEFAULT_MATERIAL_LABEL)
        self.cb_material.setToolTip(DEFAULT_MATERIAL_LABEL)
        cl.addWidget(self.cb_material)
        cl.addWidget(QLabel("Section"))
        self.cb_section = QComboBox()
        self.cb_section.addItem(DEFAULT_DESIGNATION)
        self.cb_section.setToolTip(DEFAULT_DESIGNATION)
        cl.addWidget(self.cb_section)
        lay.addWidget(card)

        # Load cases & combinations
        card, cl = self._card("Load Cases & Combinations")
        self.cb_load = QComboBox()
        self.cb_load.currentIndexChanged.connect(self.on_selection_changed)
        cl.addWidget(self.cb_load)
        self.lbl_load_caption = QLabel("")
        self.lbl_load_caption.setObjectName("Caption")
        self.lbl_load_caption.setWordWrap(True)
        cl.addWidget(self.lbl_load_caption)
        lay.addWidget(card)

        # Visualization controls
        card, cl = self._card("Visualization Controls")
        self.chk_nodes = QCheckBox("Nodes"); self.chk_nodes.setChecked(True)
        self.chk_members = QCheckBox("Members"); self.chk_members.setChecked(True)
        self.chk_supports = QCheckBox("Supports"); self.chk_supports.setChecked(True)
        self.chk_diaphragm = QCheckBox("Show Diaphragm"); self.chk_diaphragm.setChecked(False)
        self.chk_grid = QCheckBox("Show Grid"); self.chk_grid.setChecked(True)
        self.chk_nodal = QCheckBox("Nodal Loads"); self.chk_nodal.setChecked(True)
        self.chk_uniform = QCheckBox("Uniform Loads"); self.chk_uniform.setChecked(True)
        self.chk_point = QCheckBox("Point Loads"); self.chk_point.setChecked(True)
        self.chk_thermal = QCheckBox("Thermal Loads"); self.chk_thermal.setChecked(True)
        for chk in (self.chk_nodes, self.chk_members, self.chk_supports, self.chk_diaphragm,
                    self.chk_grid, self.chk_nodal, self.chk_uniform, self.chk_point,
                    self.chk_thermal):
            cl.addWidget(chk)
            chk.toggled.connect(lambda *_: self.update_plot())
        lay.addWidget(card)

        lay.addStretch()

        self.btn_run = QPushButton("▶  Run Analysis")
        self.btn_run.setObjectName("RunButton")
        self.btn_run.clicked.connect(self.run_analysis)
        lay.addWidget(self.btn_run)

        return self._scroll(inner)

    def _build_viewport(self):
        frame, lay = self._card(None)
        head = QHBoxLayout()
        title = QLabel("3D Viewport")
        title.setObjectName("SectionTitle")
        head.addWidget(title)
        head.addStretch()
        lay.addLayout(head)

        self.lbl_overlay = QLabel("")
        self.lbl_overlay.setObjectName("Caption")
        lay.addWidget(self.lbl_overlay)

        self.web_view = QWebEngineView()
        self.web_view.page().setBackgroundColor(QColor(PALETTE["card"]))
        self.web_view.setMinimumSize(420, 320)
        lay.addWidget(self.web_view, 1)
        return frame

    def _build_right_panel(self):
        inner = QWidget()
        inner.setObjectName("ScrollInner")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(6, 0, 0, 0)
        lay.setSpacing(10)

        results_title = QLabel("Key Results")
        results_title.setObjectName("SectionTitle")
        lay.addWidget(results_title)

        fx_card, self.kpi_fx, _ = self._kpi("Σ Support Reaction · FX", "Sum over pinned supports")
        fy_card, self.kpi_fy, _ = self._kpi("Σ Support Reaction · FY", "Sum over pinned supports")
        fz_card, self.kpi_fz, _ = self._kpi("Σ Support Reaction · FZ", "Sum over pinned supports")
        sw_card, self.kpi_sway, self.kpi_sway_note = self._kpi(
            "Maximum Sway", "Horizontal (X–Z)", sway=True)
        eq_card, self.kpi_eq, self.kpi_eq_note = self._kpi(
            "Equilibrium residual",
            "Σ applied + Σ reactions; ≈ 0 means global force balance holds.")
        for w in (fx_card, fy_card, fz_card, sw_card, eq_card):
            lay.addWidget(w)

        # Member inspector
        insp_card, il = self._card("Member Inspector")
        self.cb_member = QComboBox()
        self.cb_member.currentIndexChanged.connect(self.on_member_changed)
        il.addWidget(self.cb_member)

        cross_lbl = QLabel("Cross-section & material")
        cross_lbl.setObjectName("Caption")
        il.addWidget(cross_lbl)
        self.tbl_section = make_locked_table()
        self.tbl_section.setFixedHeight(230)
        il.addWidget(self.tbl_section)

        forces_lbl = QLabel("Local end forces")
        forces_lbl.setObjectName("Caption")
        il.addWidget(forces_lbl)
        self.tbl_forces = make_locked_table()
        self.tbl_forces.setFixedHeight(120)
        il.addWidget(self.tbl_forces)

        self.lbl_forces_note = QLabel("Local end forces appear after Run Analysis.")
        self.lbl_forces_note.setObjectName("Note")
        self.lbl_forces_note.setWordWrap(True)
        il.addWidget(self.lbl_forces_note)

        lay.addWidget(insp_card)
        lay.addStretch()
        return self._scroll(inner)

    def _build_bottom_tabs(self):
        self.tabs = QTabWidget()

        self.tbl_actions = make_locked_table()
        self.tabs.addTab(self.tbl_actions, "Member End Actions")

        disp_wrap = QWidget()
        dl = QVBoxLayout(disp_wrap)
        dl.setContentsMargins(8, 8, 8, 8)
        self.disp_filter = QLineEdit()
        self.disp_filter.setPlaceholderText("Filter by node (e.g. N5)")
        self.disp_filter.setClearButtonEnabled(True)
        self.disp_filter.textChanged.connect(self.filter_displacements)
        dl.addWidget(self.disp_filter)
        self.tbl_disp = make_locked_table()
        dl.addWidget(self.tbl_disp, 1)
        self.tabs.addTab(disp_wrap, "Nodal Displacements")

        self.tbl_reac = make_locked_table()
        self.tabs.addTab(self.tbl_reac, "Reactions")
        return self.tabs

    def _scroll(self, inner: QWidget) -> QScrollArea:
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setFrameShape(QFrame.Shape.NoFrame)
        sa.setWidget(inner)
        return sa

    # ----------------------------------------------------- population helpers
    def selection_options(self):
        return ([("LC", cid) for cid in sorted(self.load_cases)]
                + [("COMB", cid) for cid in sorted(self.load_combinations)])

    def selection_label(self, sel) -> str:
        kind, idx = sel
        if kind == "LC":
            text = f"LC{idx} · {self.load_cases[idx].name}"
        else:
            text = f"Comb {idx} · {self.load_combinations[idx].name}"
        return text if len(text) <= 48 else text[:47] + "…"

    def selection_tooltip(self, sel):
        """Returns (full_text, tooltip_text) for the caption and combo tooltips."""
        kind, idx = sel
        if kind == "LC":
            case = self.load_cases[idx]
            return f"LC{idx} · {case.name}", case.description or case.category or ""
        combo = self.load_combinations[idx]
        terms = ", ".join(f"LC{cid} × {f:g}" for cid, f in combo.factors.items())
        return (f"Comb {idx} · {combo.name} [{combo.method}]",
                f"Factors: {terms}")

    def resolve_selection(self, sel):
        """Returns contributions = [(LoadCase, factor), ...].
        A single load case is [(case, 1.0)]; a combination uses its factors dict."""
        kind, idx = sel
        cases = self.load_cases
        if kind == "LC":
            contributions = [(cases[idx], 1.0)]
        else:
            combo = self.load_combinations[idx]
            contributions = [(cases[cid], float(f)) for cid, f in combo.factors.items()]
        for case, _ in contributions:
            _check_load_types(case)
        return contributions

    def populate_selection_combo(self):
        self.cb_load.blockSignals(True)
        self.cb_load.clear()
        for sel in self.selection_options():
            self.cb_load.addItem(self.selection_label(sel), sel)
            full, tip = self.selection_tooltip(sel)
            self.cb_load.setItemData(self.cb_load.count() - 1,
                                     f"{full}\n{tip}", Qt.ItemDataRole.ToolTipRole)
        self.cb_load.blockSignals(False)
        self.refresh_selection_caption()

    def populate_member_combo(self):
        current = self.cb_member.currentData()
        self.cb_member.blockSignals(True)
        self.cb_member.clear()
        for mid in sorted(self.model.members):
            self.cb_member.addItem(f"M{mid} · {self.model.members[mid]['type']}", mid)
        if current is not None:
            idx = self.cb_member.findData(current)
            if idx >= 0:
                self.cb_member.setCurrentIndex(idx)
        self.cb_member.blockSignals(False)

    def current_selection(self):
        return self.cb_load.currentData()

    # ------------------------------------------------------------ UI updates
    def refresh_selection_caption(self):
        sel = self.current_selection()
        if sel is None:
            return
        full, tip = self.selection_tooltip(sel)
        self.lbl_load_caption.setText(f"ⓘ {full}")
        self.lbl_load_caption.setToolTip(tip)
        self.lbl_overlay.setText(f"Overlay: {full}")

    def on_selection_changed(self, *_):
        self.refresh_selection_caption()
        self.refresh_status()
        self.update_plot()

    def on_member_changed(self, *_):
        self.update_member_panel()
        self.update_plot()

    def on_unit_changed(self, text: str):
        if text == self.unit_system:
            return
        self.unit_system = text
        self.ensure_model(text)
        self.populate_member_combo()
        self.refresh_results()
        self.update_plot()
        self.statusBar().showMessage(f"Rebuilt reference model in {text} units. Results cleared.", 5000)

    def refresh_status(self):
        if self.res is None:
            text = "Not solved"
        elif self.res_key != self.current_selection():
            text = "Stale · run analysis again"
        else:
            residual = equilibrium_residual_kN(self.model, self.res)
            text = "Equilibrium OK" if residual < EQUILIBRIUM_TOL_KN else "Check equilibrium"
        self.lbl_status.setText(text)

    def update_plot(self):
        sel = self.current_selection()
        try:
            contributions = self.resolve_selection(sel)
            glyphs = build_load_glyphs(
                self.model, contributions,
                show_nodal=self.chk_nodal.isChecked(),
                show_uniform=self.chk_uniform.isChecked(),
                show_point=self.chk_point.isChecked(),
                show_thermal=self.chk_thermal.isChecked(),
            )
        except Exception:
            glyphs = None

        local_mid = self.cb_member.currentData()
        fig = draw_3d_model(
            self.model,
            show_nodes=self.chk_nodes.isChecked(),
            show_members=self.chk_members.isChecked(),
            show_grid=self.chk_grid.isChecked(),
            show_supports=self.chk_supports.isChecked(),
            show_diaphragm=self.chk_diaphragm.isChecked(),
            diaphragm=self.diaphragm,
            load_glyphs=glyphs,
            local_member=local_mid,
        )
        path = os.path.join(self._plot_dir, "viewport.html")
        fig.write_html(
            path,
            include_plotlyjs="plotly.min.js",
            full_html=True,
            default_width="100%",
            default_height="100%",
            config={"displaylogo": False, "scrollZoom": True, "responsive": True},
        )
        self.web_view.load(QUrl.fromLocalFile(path))

    def refresh_results(self):
        """Refreshes KPIs, inspector, and all tables from self.res (or clears them)."""
        res = self.res
        if res is None:
            for lbl in (self.kpi_fx, self.kpi_fy, self.kpi_fz, self.kpi_sway, self.kpi_eq):
                lbl.setText("–")
            self.kpi_sway_note.setText("Horizontal (X–Z)")
            self.kpi_eq_note.setText("Σ applied + Σ reactions; ≈ 0 means global force balance holds.")
            set_table_df(self.tbl_actions, None)
            set_table_df(self.tbl_disp, None)
            set_table_df(self.tbl_reac, None)
            self._disp_df = None
            self.update_member_panel()
            self.refresh_status()
            return

        kpi = compute_kpis(self.model, res)
        self.kpi_fx.setText(f"{kpi['sum_fx']:,.3f} kN")
        self.kpi_fy.setText(f"{kpi['sum_fy']:,.3f} kN")
        self.kpi_fz.setText(f"{kpi['sum_fz']:,.3f} kN")
        self.kpi_sway.setText(f"{kpi['max_sway_mm']:,.3f} mm")
        self.kpi_sway_note.setText(f"Horizontal (X–Z) at N{kpi['max_sway_node']}")
        residual = equilibrium_residual_kN(self.model, res)
        self.kpi_eq.setText(f"{residual:.3e} kN")

        set_table_df(self.tbl_actions, build_member_actions_df(self.model, res))
        self._disp_df = build_displacement_df(self.model, res)
        self.filter_displacements(self.disp_filter.text())
        set_table_df(self.tbl_reac, build_reaction_df(self.model, res))

        self.update_member_panel()
        self.refresh_status()

    def filter_displacements(self, text: str):
        if self._disp_df is None:
            set_table_df(self.tbl_disp, None)
            return
        q = text.strip().lower()
        df = self._disp_df
        if q:
            df = df[df["Node"].str.lower().str.contains(q, regex=False)]
        set_table_df(self.tbl_disp, df)

    def update_member_panel(self):
        mid = self.cb_member.currentData()
        if mid is None:
            set_table_df(self.tbl_section, None)
            set_table_df(self.tbl_forces, None)
            return
        m = self.model.members[mid]

        sec_df = pd.DataFrame([
            {"Property": "Nodes", "Value": f"N{m['i']} → N{m['j']}"},
            {"Property": "Length (m)", "Value": f"{member_length(self.model, mid):.3f}"},
            {"Property": "Beta angle (°)", "Value": f"{m['beta_deg']:.1f}"},
            {"Property": "A (mm²)", "Value": f"{m['A'] * 1e6:,.1f}"},
            {"Property": "Iy (mm⁴)", "Value": f"{m['Iy'] * 1e12:,.0f}"},
            {"Property": "Iz (mm⁴)", "Value": f"{m['Iz'] * 1e12:,.0f}"},
            {"Property": "J (mm⁴)", "Value": f"{m['J'] * 1e12:,.0f}"},
            {"Property": "E (MPa)", "Value": f"{m['E'] / 1e6:,.0f}"},
            {"Property": "G (MPa)", "Value": f"{m['G'] / 1e6:,.0f}"},
        ])
        set_table_df(self.tbl_section, sec_df)

        if self.res is None:
            set_table_df(self.tbl_forces, None)
            self.lbl_forces_note.setText("Local end forces appear after Run Analysis.")
            self.lbl_forces_note.show()
            return

        f = self.res["MemberForces"][mid]
        force_df = pd.DataFrame([
            {"End": f"i · N{m['i']}",
             "P (kN)": f"{f[0] / KN_TO_N:,.3f}", "Vy (kN)": f"{f[1] / KN_TO_N:,.3f}",
             "Vz (kN)": f"{f[2] / KN_TO_N:,.3f}", "T (kN·m)": f"{f[3] / KN_TO_N:,.3f}",
             "My (kN·m)": f"{f[4] / KN_TO_N:,.3f}", "Mz (kN·m)": f"{f[5] / KN_TO_N:,.3f}"},
            {"End": f"j · N{m['j']}",
             "P (kN)": f"{f[6] / KN_TO_N:,.3f}", "Vy (kN)": f"{f[7] / KN_TO_N:,.3f}",
             "Vz (kN)": f"{f[8] / KN_TO_N:,.3f}", "T (kN·m)": f"{f[9] / KN_TO_N:,.3f}",
             "My (kN·m)": f"{f[10] / KN_TO_N:,.3f}", "Mz (kN·m)": f"{f[11] / KN_TO_N:,.3f}"},
        ])
        set_table_df(self.tbl_forces, force_df)
        self.lbl_forces_note.hide()

    # ---------------------------------------------------------------- actions
    def run_analysis(self):
        sel = self.current_selection()
        try:
            contributions = self.resolve_selection(sel)
            apply_contributions_to_model(self.model, contributions, self.material_cfg)
            self.res = self.model.solve()
            self.res_key = sel
        except np.linalg.LinAlgError:
            self.res = None
            self.res_key = None
            self.refresh_results()
            QMessageBox.critical(
                self, "Solver Error",
                "Singular stiffness matrix: the reduced matrix is singular.\n"
                "Check supports and member releases.",
            )
            return
        except Exception as exc:
            self.res = None
            self.res_key = None
            self.refresh_results()
            QMessageBox.critical(self, "Analysis Failed", f"Analysis failed:\n{exc}")
            return

        self.refresh_results()
        self.update_plot()
        self.statusBar().showMessage("Analysis complete.", 5000)

    def export_report(self):
        if self.res is None:
            QMessageBox.information(self, "Export Report", "Run an analysis first, then export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "cube_solver_rev3_report.html", "HTML files (*.html)")
        if not path:
            return

        sel = self.res_key
        full, _tip = self.selection_tooltip(sel)
        kpi = compute_kpis(self.model, self.res)
        residual = equilibrium_residual_kN(self.model, self.res)

        def tbl(df):
            return df.to_html(index=False, border=0, classes="t")

        report = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Cube Solver Rev 3 Report</title>
<style>
body {{ font-family: Georgia, serif; background:{PALETTE['canvas']}; color:{PALETTE['primary']}; padding:24px; }}
h1,h2 {{ color:{PALETTE['primary']}; }}
.kpi {{ display:inline-block; background:{PALETTE['card']}; border:1px solid {PALETTE['border']};
        border-radius:8px; padding:12px 16px; margin:6px; min-width:200px; }}
.kpi b {{ color:{PALETTE['accent']}; font-size:18px; }}
table.t {{ border-collapse:collapse; background:{PALETTE['card']}; margin-bottom:20px; font-size:13px; }}
table.t th {{ background:{PALETTE['sidebar']}; padding:6px 10px; text-align:left; border-bottom:1px solid {PALETTE['border']}; }}
table.t td {{ padding:5px 10px; border-bottom:1px solid {PALETTE['grid_line']}; white-space:nowrap; }}
</style></head><body>
<h1>Cube Solver Rev 3 · Analysis Report</h1>
<p>Model: {_html.escape(self.lbl_model.text())} &nbsp;|&nbsp; Units (input): {self.unit_system} &nbsp;|&nbsp;
Load selection: {_html.escape(full)}</p>
<div>
  <div class="kpi">Σ Reaction FX<br><b>{kpi['sum_fx']:,.3f} kN</b></div>
  <div class="kpi">Σ Reaction FY<br><b>{kpi['sum_fy']:,.3f} kN</b></div>
  <div class="kpi">Σ Reaction FZ<br><b>{kpi['sum_fz']:,.3f} kN</b></div>
  <div class="kpi">Maximum Sway<br><b>{kpi['max_sway_mm']:,.3f} mm</b> (N{kpi['max_sway_node']})</div>
  <div class="kpi">Equilibrium residual<br><b>{residual:.3e} kN</b></div>
</div>
<h2>Member End Actions</h2>{tbl(build_member_actions_df(self.model, self.res))}
<h2>Nodal Displacements</h2>{tbl(build_displacement_df(self.model, self.res))}
<h2>Reactions</h2>{tbl(build_reaction_df(self.model, self.res))}
</body></html>"""
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(report)
            self.statusBar().showMessage(f"Report saved to {path}", 6000)
        except OSError as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))

    def closeEvent(self, event):
        shutil.rmtree(self._plot_dir, ignore_errors=True)
        super().closeEvent(event)


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
