r"""
Rev3.py — 6m x 6m x 6m cube frame model + LOAD-CASE FRAMEWORK (Rev 2 upgrade).

Purpose
-------
Adds a RISA-style load-case / load-visualization framework on top of the
existing Rev2 structural model generator. Rev3 introduces:
  - Load cases with load types/categories
  - Nodal loads, member distributed loads, member point loads, self-weight
  - Diaphragm constraint (roof plane)
  - Load combinations (LRFD/factored + ASD/allowable), assembled — not duplicated
  - A load viewer for visual verification of how loads are applied
  - Automatic load validation (intended vs computed totals, equilibrium)

Axis convention (identical to Rev2, unchanged)
----------------------------------------------
  Global:  X, Z = lateral ;  Y = vertical (UP).  Gravity acts in NEGATIVE global Y.
  Local:   L1 = axial ;  L2/L3 = cross-section axes (Rev2.local_axes()).

Unit system
-----------
  Same switchable UNIT_SYSTEM as Rev2 ("metric" default / "imperial"). Physics is
  stored in SI internally; only display/input converts. All unit factors come from
  the single Rev2.UNITS dict (NIST SP 811) — NO inline magic numbers.

Material / Section (reused from Rev2, unchanged)
------------------------------------------------
  Material: A36 Steel (E=199.948 GPa, Fy=248.2 MPa, Fu=399.9 MPa,
            rho=7848.76 kg/m3, nu=0.30, G=76.904 GPa, alpha=11.7e-6 /C).
  Section:  W 100x100  (metric)  ==  W 4x13  (imperial).
            A=2.470e-3 m2, Ix=4.70e-6 m4, Iy=1.61e-6 m4, J=6.29e-8 m4,
            d=0.106 m, bf=0.103 m, tf=0.00876 m, tw=0.00711 m.

Scope / separation of concerns (do NOT mix)
-------------------------------------------
  load-case definition | load application | (structural analysis = DEFERRED to
  Rev4) | load combination | visualization | validation.  Rev3 does NOT solve a
  stiffness system; it assembles/validates load vectors and reports totals and
  equilibrium. Reactions/displacements/member forces are out of scope (Rev4).

Packaging
---------
  Rev3 IMPORTS the Rev2 model core (does not copy it). See IMPORT below.
  Recovery/state notes: D:\che school 2627\lab02\Rev3\_rev3_state.md
"""

from __future__ import annotations

import os
import sys
import math
import numpy as np
import matplotlib
# Use TkAgg for the interactive pop-up; use Agg if running headless.
_backend = os.environ.get("MPLBACKEND")          # honour an explicit choice (tests set Agg)
if not _backend:
    try:
        import tkinter  # noqa: F401
        _backend = "TkAgg"
    except ImportError:
        _backend = "Agg"
matplotlib.use(_backend)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ============================================================
# 0. IMPORT — bring in the Rev2 model core (do NOT copy it)
# ============================================================
# Rev2 lives in the sibling folder. Add it to sys.path so `import Rev2` works
# regardless of the current working directory.
_REV2_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Rev2"))
if _REV2_DIR not in sys.path:
    sys.path.insert(0, _REV2_DIR)

import Rev2 as R2  # noqa: E402  (model core: nodes, members, MATERIAL, SECTION,
# UNITS, local_axes(), supports, DOF, releases, display helpers, etc.)

# NOTE (blocker, see _rev3_state.md): Rev2 currently runs its writers + plt.show()
# at import time (no `if __name__ == "__main__":` guard). Importing it will trigger
# those side effects. Phase 2 Step 0 proposes adding that guard to Rev2 (the only
# intended Rev2 edit). Until approved, importing Rev3 will run Rev2 top-level code.

# ============================================================
# 1. CONFIG — reuse Rev2 constants; add Rev3 load-scope constants
# ============================================================
UNIT_SYSTEM = R2.UNIT_SYSTEM          # "metric" (default) | "imperial"
UNITS = R2.UNITS                       # single NIST SP 811 factor table (no dupes)
MATERIAL = R2.MATERIAL                 # A36 Steel (SI internal)
SECTION = R2.SECTION                   # W 100x100 (SI internal)

# Roof selection (confirmed model geometry)
ROOF_BEAM_IDS = (5, 6, 7, 8)           # members on the roof ring (Beams)
ROOF_NODE_IDS = (5, 6, 7, 8)           # nodes at Y = 6
LATERAL_LOAD_NODES = ROOF_NODE_IDS     # Wind/Seismic applied here (Q2/F5)
DIAPHRAGM_MASTER_NODE = 5              # Q3: master node

# Direction / gravity
GRAVITY = R2.UNITS.get("GRAVITY_M_S2", 9.80665)   # m/s^2 (SI)
GRAVITY_DIRECTION = (0.0, -1.0, 0.0)  # global -Y (up-positive axis system)

# Load magnitudes (SI internal: Newtons, N/m, Newton-metres). Named constants —
# these are the ONLY numeric load magnitudes; nothing hard-coded elsewhere.
N_PER_KN = R2.UNITS["N_PER_KN"]       # 1000.0  (kN <-> N) [from UNITS, not inline]
ROOF_DEAD_KN_M = 5.0                   # kN/m  (F1: distributed member load)
ROOF_LIVE_KN_M = 3.0                   # kN/m  (F2: distributed member load)
CENTER_LOAD_KN = 5.0                   # kN    (F3: point load at midpoint)
WIND_TOTAL_KN = 10.0                   # kN    (LC5/LC6; split over 4 nodes)
SEISMIC_TOTAL_KN = 15.0                # kN    (LC7/LC8; split over 4 nodes)


# ============================================================
# 2. LOAD-CASE DATA MODEL (dataclasses)
# ============================================================
# Load values are stored in SI: forces -> N ; line loads -> N/m ; moments -> N*m.
# Unit validation keeps kN / kN/m / kN*m distinct (spec item 11): each load
# carries a `unit` tag and _require_unit() refuses incompatible use.

UNIT_FORCE = "kN"        # force tag (stored in N)
UNIT_LINE = "kN/m"       # distributed line-load tag (stored in N/m)
UNIT_MOMENT = "kN*m"     # moment tag (stored in N*m)


def _require_unit(value_unit: str, allowed: Tuple[str, ...]) -> None:
    """Raise ValueError if a load's unit tag is not one of `allowed`."""
    if value_unit not in allowed:
        raise ValueError(
            f"incompatible load unit '{value_unit}'; expected one of {allowed}")


@dataclass
class NodalLoad:
    """A concentrated load/moment at a node (SI: N and N*m)."""
    node_id: int
    fx: float = 0.0
    fy: float = 0.0
    fz: float = 0.0
    mx: float = 0.0
    my: float = 0.0
    mz: float = 0.0

    def __post_init__(self) -> None:
        for name in ("fx", "fy", "fz", "mx", "my", "mz"):
            v = getattr(self, name)
            if not isinstance(v, (int, float)) or not math.isfinite(float(v)):
                raise ValueError(f"NodalLoad.{name} must be a finite number")

    def total_force_magnitude(self) -> float:
        """Euclidean magnitude of the net nodal force (N)."""
        return math.sqrt(self.fx ** 2 + self.fy ** 2 + self.fz ** 2)


@dataclass
class MemberDistributedLoad:
    """A uniform line load along a member (SI: N/m).

    `direction` is a global unit vector; `sign` (+1/-1) orients it.
    `distribution_type` is "uniform" (only supported type in Rev3).
    """
    member_id: int
    direction: Tuple[float, float, float]
    magnitude: float            # N/m (positive)
    sign: int = -1              # default: -direction (e.g. gravity)
    distribution_type: str = "uniform"
    unit: str = UNIT_LINE

    def __post_init__(self) -> None:
        _require_unit(self.unit, (UNIT_LINE,))
        if self.distribution_type != "uniform":
            raise ValueError("only 'uniform' distributed loads are supported")
        if not math.isfinite(self.magnitude) or self.magnitude < 0:
            raise ValueError("magnitude must be a non-negative finite number")
        if self.sign not in (1, -1):
            raise ValueError("sign must be +1 or -1")

    def signed_vector(self) -> Tuple[float, float, float]:
        """Global vector (N/m) = sign * magnitude * direction."""
        dx, dy, dz = self.direction
        return (self.sign * self.magnitude * dx,
                self.sign * self.magnitude * dy,
                self.sign * self.magnitude * dz)


@dataclass
class MemberPointLoad:
    """A concentrated point load on a member (SI: N).

    `location` is the fractional position (0..1); 0.5 = center. `direction` is
    a global unit vector; `sign` (+1/-1) orients it.
    """
    member_id: int
    location: float             # 0..1 along the member
    direction: Tuple[float, float, float]
    magnitude: float            # N (positive)
    sign: int = -1
    unit: str = UNIT_FORCE

    def __post_init__(self) -> None:
        _require_unit(self.unit, (UNIT_FORCE,))
        if not (0.0 <= self.location <= 1.0):
            raise ValueError("location must be within [0,1]")
        if not math.isfinite(self.magnitude) or self.magnitude < 0:
            raise ValueError("magnitude must be a non-negative finite number")
        if self.sign not in (1, -1):
            raise ValueError("sign must be +1 or -1")

    def signed_vector(self) -> Tuple[float, float, float]:
        """Global vector (N) = sign * magnitude * direction."""
        dx, dy, dz = self.direction
        return (self.sign * self.magnitude * dx,
                self.sign * self.magnitude * dy,
                self.sign * self.magnitude * dz)


@dataclass
class Diaphragm:
    """A rigid in-plane diaphragm constraint group (structural, not visual).

    `constrained_nodes` are tied to `master_node` via constraint equations.
    `degrees_of_freedom` lists the global DOF labels constrained (Ux,Uz,Ry).
    """
    id: int
    name: str
    master_node: int
    constrained_nodes: Tuple[int, ...]
    degrees_of_freedom: Tuple[str, ...]

    def __post_init__(self) -> None:
        if self.master_node in self.constrained_nodes:
            raise ValueError("master_node must not also be a constrained node")
        if not self.constrained_nodes:
            raise ValueError("diaphragm needs at least one constrained node")


@dataclass
class LoadCase:
    """A named, categorised load case holding nodal + member loads.

    `category` is a coarse type (Dead/Live/Wind/Seismic/Member Point Load/...).
    `self_weight` flags self-weight generated from model properties (Phase 3).
    """
    id: int
    name: str
    category: str
    description: str = ""
    self_weight: bool = False
    self_weight_factor: float = 1.0
    loads: List[object] = field(default_factory=list)  # Nodal/Member*Load

    def add_load(self, load: object) -> None:
        """Attach a nodal or member load to this case."""
        self.loads.append(load)


@dataclass
class LoadCombination:
    """A factored/allowed combination referencing existing load cases.

    `factors` maps load_case_id -> multiplier; the solver assembles the vector
    from the referenced cases (no physical load duplication).
    """
    id: int
    name: str
    design_method: str                       # "LRFD" | "ASD"
    factors: Dict[int, float] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if self.design_method not in ("LRFD", "ASD"):
            raise ValueError("design_method must be 'LRFD' or 'ASD'")


# ============================================================
# 2b. EIGHT PHYSICAL LOAD CASES + DIAPHRAGM (named constants)
# ============================================================
# Global reference axis directions (axis convention: X,Z lateral, Y up).
# A load's `sign` (-1/+1) orients it along the reference axis, so gravity uses
# direction=+Y with sign=-1 -> acts in -Y (down), matching spec "factor -1".
_DIR_POS_Y = (0.0, 1.0, 0.0)
_DIR_POS_X = (1.0, 0.0, 0.0)
_DIR_POS_Z = (0.0, 0.0, 1.0)


def _build_load_cases() -> List[LoadCase]:
    """Construct the 8 approved load cases from the named magnitude constants.

    All magnitudes come from the CONFIG constants (kN) converted to SI via
    N_PER_KN. No inline magic numbers appear here.
    """
    cases: List[LoadCase] = []

    # 1. DEAD / SELF-WEIGHT — generated from member properties (Phase 3).
    cases.append(LoadCase(
        1, "DEAD", "Dead",
        "Structural self-weight (W = rho*A*L*g per member)",
        self_weight=True, self_weight_factor=1.0))

    # 2. ROOF DEAD — 5 kN/m down on roof beams 5-8 (F1: distributed, not moment).
    lc2 = LoadCase(2, "ROOF DEAD", "Dead", "Roof dead load 5 kN/m (global -Y)")
    for m in ROOF_BEAM_IDS:
        lc2.add_load(MemberDistributedLoad(
            m, _DIR_POS_Y, ROOF_DEAD_KN_M * N_PER_KN, sign=-1))
    cases.append(lc2)

    # 3. ROOF LIVE — 3 kN/m down on roof beams 5-8.
    lc3 = LoadCase(3, "ROOF LIVE", "Live", "Roof live load 3 kN/m (global -Y)")
    for m in ROOF_BEAM_IDS:
        lc3.add_load(MemberDistributedLoad(
            m, _DIR_POS_Y, ROOF_LIVE_KN_M * N_PER_KN, sign=-1))
    cases.append(lc3)

    # 4. ROOF BEAM CENTER LOAD — 5 kN down at each roof-beam midpoint (loc=0.5).
    lc4 = LoadCase(4, "ROOF BEAM CENTER LOAD", "Member Point Load",
                   "5 kN point load at member midpoint (global -Y)")
    for m in ROOF_BEAM_IDS:
        lc4.add_load(MemberPointLoad(
            m, location=0.5, direction=_DIR_POS_Y,
            magnitude=CENTER_LOAD_KN * N_PER_KN, sign=-1))
    cases.append(lc4)

    # 5-6. WIND X / WIND Z — total split equally over LATERAL_LOAD_NODES.
    n_lat = len(LATERAL_LOAD_NODES)
    wind_kn = WIND_TOTAL_KN / n_lat          # kN per node (2.5 for 4 nodes)
    lc5 = LoadCase(5, "WIND X", "Wind",
                   f"Total {WIND_TOTAL_KN} kN in +X, split over {n_lat} nodes")
    for node in LATERAL_LOAD_NODES:
        lc5.add_load(NodalLoad(node, fx=wind_kn * N_PER_KN))
    cases.append(lc5)

    lc6 = LoadCase(6, "WIND Z", "Wind",
                   f"Total {WIND_TOTAL_KN} kN in +Z, split over {n_lat} nodes")
    for node in LATERAL_LOAD_NODES:
        lc6.add_load(NodalLoad(node, fz=wind_kn * N_PER_KN))
    cases.append(lc6)

    # 7-8. SEISMIC X / SEISMIC Z — total split equally over LATERAL_LOAD_NODES.
    seis_kn = SEISMIC_TOTAL_KN / n_lat       # kN per node (3.75 for 4 nodes)
    lc7 = LoadCase(7, "SEISMIC X", "Seismic",
                   f"Total {SEISMIC_TOTAL_KN} kN in +X, split over {n_lat} nodes")
    for node in LATERAL_LOAD_NODES:
        lc7.add_load(NodalLoad(node, fx=seis_kn * N_PER_KN))
    cases.append(lc7)

    lc8 = LoadCase(8, "SEISMIC Z", "Seismic",
                   f"Total {SEISMIC_TOTAL_KN} kN in +Z, split over {n_lat} nodes")
    for node in LATERAL_LOAD_NODES:
        lc8.add_load(NodalLoad(node, fz=seis_kn * N_PER_KN))
    cases.append(lc8)

    return cases


LOAD_CASES: List[LoadCase] = _build_load_cases()
LOAD_CASES_BY_ID: Dict[int, LoadCase] = {lc.id: lc for lc in LOAD_CASES}

# Single roof diaphragm (fully wired as a constraint in Phase 4).
DIAPHRAGMS: List[Diaphragm] = [
    Diaphragm(
        id=1,
        name="Roof diaphragm (Y=6, X-Z plane)",
        master_node=DIAPHRAGM_MASTER_NODE,
        constrained_nodes=tuple(n for n in ROOF_NODE_IDS
                                if n != DIAPHRAGM_MASTER_NODE),
        degrees_of_freedom=("Ux", "Uz", "Ry"),  # in-plane; uY,rX,rZ free (Q3)
    )
]



# ============================================================
# 3. LOAD APPLICATION (nodal + member loads)
# ============================================================
# The assembled vector has length TOTAL_DOF (48) using a FIXED full-DOF
# numbering: index = node_rank*6 + component, over sorted nodes and
# DOF_NAMES order. All applied loads are retained (including at restrained
# DOFs) so the vector is a physically complete record of the applied load —
# this is required for total-force / equilibrium validation (Rev3 scope per
# Q1: framework + equilibrium only, no stiffness solve). A future solver
# (Rev4) can project onto the active DOFs using _is_restrained()/_active_indices.
#
# Sign conventions (documented per spec):
#   Distributed uniform load w (N/m) over length L:
#     * Translational: each member end gets w*L/2 (global), so the two ends
#       sum to the total w*L in the load direction (exact force equilibrium).
#     * Fixed-end moments: from the load components transverse to the member
#       axis (local L2 -> bending about L3; local L3 -> bending about L2).
#       Magnitude w*L^2/12 per end, applied equal-and-opposite about the
#       bending axis (self-equilibrating moment set).
#   Point load P (N) at fractional location a (b = 1-a):
#     * Translational: end i gets P*(1-a), end j gets P*a (sum = P).
#     * Fixed-end moments: end i gets P*a*b^2*L, end j gets P*a^2*b*L about the
#       bending axis, applied equal-and-opposite (at midspan a=b=0.5 -> PL/8).

_NODE_RANK = {n: r for r, n in enumerate(sorted(R2.nodes))}
_DOF_OFFSET = {d: k for k, d in enumerate(R2.DOF_NAMES)}


def _full_dof_index(node_id: int, dof_name: str) -> int:
    """Full 0-based global DOF index (0..TOTAL_DOF-1) for a node/component."""
    return _NODE_RANK[node_id] * 6 + _DOF_OFFSET[dof_name]


def _is_restrained(node_id: int, dof_name: str) -> bool:
    """True if the node/component is a restrained support DOF (Rev2 'R')."""
    return R2.node_dof_numbers[node_id][dof_name] == "R"


def _active_dof_indices() -> List[int]:
    """Full-DOF indices that are active (not restrained) — for a future solver."""
    return [_full_dof_index(n, d)
            for n in sorted(R2.nodes) for d in R2.DOF_NAMES
            if not _is_restrained(n, d)]


def _member_end_nodes(member_id: int) -> Tuple[int, int]:
    """Return the (i, j) end-node ids of a 1-based member id."""
    i, j = R2.member_pairs[member_id - 1]
    return int(i), int(j)


def _member_length(member_id: int) -> float:
    """Member length (m) from node geometry."""
    i, j = _member_end_nodes(member_id)
    return float(np.linalg.norm(
        np.asarray(R2.nodes[j], float) - np.asarray(R2.nodes[i], float)))


def _member_local_axes(member_id: int):
    """Return (L1, L2, L3) global unit vectors for a member as numpy arrays."""
    L1, L2, L3 = R2.member_local_axes[member_id]
    return (np.asarray(L1, float), np.asarray(L2, float), np.asarray(L3, float))


def _add_global(vec: np.ndarray, node_id: int,
                force: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                moment: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> None:
    """Add a global force (N) and moment (N*m) at a node into the full vector."""
    for dof, val in zip(("Ux", "Uy", "Uz"), force):
        if val:
            vec[_full_dof_index(node_id, dof)] += val
    for dof, val in zip(("Rx", "Ry", "Rz"), moment):
        if val:
            vec[_full_dof_index(node_id, dof)] += val


def _apply_distributed(vec: np.ndarray, load: "MemberDistributedLoad") -> None:
    """Apply a uniform member line load as consistent/equivalent nodal loads."""
    i, j = _member_end_nodes(load.member_id)
    L = _member_length(load.member_id)
    w = np.asarray(load.signed_vector(), float)          # global N/m
    half = w * L / 2.0                                    # translational per end
    _add_global(vec, i, tuple(half))
    _add_global(vec, j, tuple(half))
    # Fixed-end moments from transverse components (local projection).
    L1, L2, L3 = _member_local_axes(load.member_id)
    w2 = float(np.dot(w, L2))                            # load along L2
    w3 = float(np.dot(w, L3))                            # load along L3
    Mz = w2 * L * L / 12.0                               # bending about L3
    My = w3 * L * L / 12.0                               # bending about L2
    m_i = Mz * L3 + My * L2                              # global moment vec (end i)
    _add_global(vec, i, moment=tuple(m_i))
    _add_global(vec, j, moment=tuple(-m_i))


def _apply_point(vec: np.ndarray, load: "MemberPointLoad") -> None:
    """Apply a member point load as consistent/equivalent nodal loads.

    location a in [0,1] from end i; b = 1 - a. Translational split P*(1-a) at
    end i and P*a at end j (sum = P). Fixed-end moments about the bending axis:
    end i gets P*a*b^2*L, end j gets P*a^2*b*L (equal-and-opposite). At midspan
    a = b = 0.5 -> P*L/8 per end.
    """
    i, j = _member_end_nodes(load.member_id)
    L = _member_length(load.member_id)
    P = np.asarray(load.signed_vector(), float)            # global N
    a = float(load.location)
    b = 1.0 - a
    _add_global(vec, i, tuple(P * b))
    _add_global(vec, j, tuple(P * a))
    # Fixed-end moments from the transverse (bending) components.
    L1, L2, L3 = _member_local_axes(load.member_id)
    P2 = float(np.dot(P, L2))
    P3 = float(np.dot(P, L3))
    Mz = P2 * a * b * b * L                                # about L3
    My = P3 * a * b * b * L                                # about L2
    m_i = Mz * L3 + My * L2
    _add_global(vec, i, moment=tuple(m_i))
    # end-j fixed-end moment uses a^2*b (differs unless midspan)
    Mz_j = P2 * a * a * b * L
    My_j = P3 * a * a * b * L
    m_j = Mz_j * L3 + My_j * L2
    _add_global(vec, j, moment=tuple(m_j))


def self_weight_nodal_forces() -> np.ndarray:
    """Full-DOF vector of structural self-weight (W = rho*A*L*g per member).

    Each member's weight acts downward (global -Y) at its midpoint; lumped half
    to each end node. Total weight = rho * A * total_length * g (matches Rev2's
    TOTAL_MASS_KG * g). No member-end moments (a lumped-mass self-weight has no
    fixed-end bending for equilibrium of the applied-load record).
    """
    vec = np.zeros(R2.TOTAL_DOF)
    w_member = R2.MATERIAL["rho"] * R2.SECTION["A"] * GRAVITY   # N/m of member
    for mid in range(1, len(R2.member_pairs) + 1):
        i, j = _member_end_nodes(mid)
        L = _member_length(mid)
        half_w = (0.0, -w_member * L / 2.0, 0.0)            # -Y, half to each end
        _add_global(vec, i, half_w)
        _add_global(vec, j, half_w)
    return vec


def total_self_weight_n() -> float:
    """Total structural self-weight in Newtons (rho*A*total_length*g)."""
    return R2.MATERIAL["rho"] * R2.SECTION["A"] * R2.TOTAL_MEMBER_LENGTH * GRAVITY


def assemble_load_vector(load_case: "LoadCase") -> np.ndarray:
    """Assemble the full global-DOF force vector (length TOTAL_DOF) for a case.

    Nodal loads map straight to their node/component. Distributed and point
    member loads are converted to consistent/equivalent nodal loads via
    _apply_distributed / _apply_point. If the case has self_weight enabled, the
    member self-weight (global -Y) is added from model properties.
    """
    vec = np.zeros(R2.TOTAL_DOF)
    for load in load_case.loads:
        if isinstance(load, NodalLoad):
            _add_global(vec, load.node_id,
                        force=(load.fx, load.fy, load.fz),
                        moment=(load.mx, load.my, load.mz))
        elif isinstance(load, MemberDistributedLoad):
            _apply_distributed(vec, load)
        elif isinstance(load, MemberPointLoad):
            _apply_point(vec, load)
        else:
            raise TypeError(f"unsupported load type: {type(load).__name__}")
    if load_case.self_weight:
        vec = vec + self_weight_nodal_forces() * load_case.self_weight_factor
    return vec


def _sum_components(vec: np.ndarray) -> Tuple[float, float, float]:
    """Sum the three global force components over all nodes (N)."""
    fx = sum(vec[_full_dof_index(n, "Ux")] for n in R2.nodes)
    fy = sum(vec[_full_dof_index(n, "Uy")] for n in R2.nodes)
    fz = sum(vec[_full_dof_index(n, "Uz")] for n in R2.nodes)
    return fx, fy, fz


def validate_load_case(load_case: "LoadCase", tol: float = 1e-6):
    """Validate a load case: intended total force vs assembled-vector sum.

    Returns (intended_total_force, computed_vector_sum, equilibrium_error) where
    the two totals are 3-vectors (N) and equilibrium_error is the Euclidean
    norm of their difference. Raises ValueError if it exceeds `tol`.
    """
    vec = assemble_load_vector(load_case)
    computed = np.array(_sum_components(vec), dtype=float)

    # Intended total force = sum over loads of their own global resultant.
    intended = np.zeros(3)
    for load in load_case.loads:
        if isinstance(load, NodalLoad):
            intended += np.array([load.fx, load.fy, load.fz])
        elif isinstance(load, MemberDistributedLoad):
            L = _member_length(load.member_id)
            intended += np.array(load.signed_vector()) * L
        elif isinstance(load, MemberPointLoad):
            intended += np.array(load.signed_vector())
    if load_case.self_weight:
        intended += np.array([0.0, -total_self_weight_n(), 0.0]) \
            * load_case.self_weight_factor

    error = float(np.linalg.norm(intended - computed))
    if error > tol:
        raise ValueError(
            f"load case {load_case.id} ('{load_case.name}') equilibrium error "
            f"{error:.6e} N exceeds tolerance {tol:.1e} N")
    return intended, computed, error




# ============================================================
# 4. DIAPHRAGM CONSTRAINT (roof plane)
# ============================================================
# Rigid in-plane diaphragm at the roof plane Y=6 over nodes 5,6,7,8.
# Master = node 5. For each slave node i in {6,7,8} (per approved Q3):
#     uX_i = uX_m + thetaY*(z_i - z_m)          # sign flipped (right-hand rule)
#     uZ_i = uZ_m - thetaY*(x_i - x_m)          # sign flipped (right-hand rule)
#     thetaY_i = thetaY_m                        # unchanged
# where uX=Ux, uZ=Uz, thetaY=Ry (rotation about global +Y). Free (unconstrained)
# DOFs at every diaphragm node: uY (Uy), rX (Rx), rZ (Rz).
#
# thetaY positive = counterclockwise rotation about +Y (right-hand rule), viewed
# from +Y looking toward the origin. Matches RISA/STAAD and Hibbeler/Gere.
#
# These are REAL master-slave constraint equations (C . u = 0), not a visual
# grouping. Each slave contributes 3 rows -> 3 slaves x 3 rows = 9 rows, each of
# length TOTAL_DOF (48) -> C is 9 x 48.

def build_diaphragm_constraints(diaphragm: "Diaphragm") -> np.ndarray:
    """Build the diaphragm constraint matrix C (C . u = 0).

    Sign convention: thetaY positive = counterclockwise rotation about +Y
    (right-hand rule), viewed from +Y looking toward the origin.

    Returns an array of shape (n_slaves*3, TOTAL_DOF). Each slave node i adds:
      row 1:  uX_i - uX_m - thetaY_m*(z_i - z_m) = 0
      row 2:  uZ_i - uZ_m + thetaY_m*(x_i - x_m) = 0
      row 3:  thetaY_i - thetaY_m = 0
    Master-node DOFs carry the thetaY coefficient; slave translations/rotation
    carry +1. Only Ux/Uz/Ry participate (uY, Rx, Rz are free).
    """
    m = diaphragm.master_node
    xm, _ym, zm = (float(v) for v in R2.nodes[m])
    rows: List[np.ndarray] = []
    for i in diaphragm.constrained_nodes:
        xi, _yi, zi = (float(v) for v in R2.nodes[i])
        r1 = np.zeros(R2.TOTAL_DOF)
        r1[_full_dof_index(i, "Ux")] += 1.0
        r1[_full_dof_index(m, "Ux")] += -1.0
        r1[_full_dof_index(m, "Ry")] += -(zi - zm)
        rows.append(r1)

        r2 = np.zeros(R2.TOTAL_DOF)
        r2[_full_dof_index(i, "Uz")] += 1.0
        r2[_full_dof_index(m, "Uz")] += -1.0
        r2[_full_dof_index(m, "Ry")] += (xi - xm)
        rows.append(r2)

        r3 = np.zeros(R2.TOTAL_DOF)
        r3[_full_dof_index(i, "Ry")] += 1.0
        r3[_full_dof_index(m, "Ry")] += -1.0
        rows.append(r3)
    return np.array(rows)


def apply_diaphragm(vec: np.ndarray, diaphragm: "Diaphragm") -> np.ndarray:
    """Project a displacement vector onto the diaphragm constraint manifold.

    thetaY positive = counterclockwise rotation about +Y (right-hand rule),
    viewed from +Y looking toward the origin.

    Master-node DOFs pass through unchanged. Each slave's Ux/Uz/Ry are OVERWRITTEN
    with the rigid-body values implied by the master; slave uY/rX/rZ are left
    untouched (free). Returns a new vector (input is not modified).
    """
    out = np.array(vec, dtype=float).copy()
    m = diaphragm.master_node
    xm, _ym, zm = (float(v) for v in R2.nodes[m])
    uXm = out[_full_dof_index(m, "Ux")]
    uZm = out[_full_dof_index(m, "Uz")]
    thYm = out[_full_dof_index(m, "Ry")]
    for i in diaphragm.constrained_nodes:
        xi, _yi, zi = (float(v) for v in R2.nodes[i])
        out[_full_dof_index(i, "Ux")] = uXm + thYm * (zi - zm)
        out[_full_dof_index(i, "Uz")] = uZm - thYm * (xi - xm)
        out[_full_dof_index(i, "Ry")] = thYm
    return out


def test_diaphragm_handcheck() -> None:
    """Independent hand-check of the diaphragm kinematics (asserts < 1e-9).

    thetaY positive = CCW about +Y (right-hand rule) viewed from +Y toward origin.
    Master (node 5) given uX=0.1 m, uZ=0.2 m, thetaY=0.05 rad. Slave node 6 is
    at (x=6, z=0); master at (x=0, z=0). Expected:
        uX_6 = 0.1 + 0.05*(0-0) = 0.1
        uZ_6 = 0.2 - 0.05*(6-0) = -0.1
        thetaY_6 = 0.05
    Also checks C . u = 0 for the projected vector.
    """
    dia = DIAPHRAGMS[0]
    u = np.zeros(R2.TOTAL_DOF)
    m = dia.master_node
    u[_full_dof_index(m, "Ux")] = 0.1
    u[_full_dof_index(m, "Uz")] = 0.2
    u[_full_dof_index(m, "Ry")] = 0.05
    # a free-DOF value that must be preserved on the slave
    u[_full_dof_index(6, "Uy")] = 0.037

    u2 = apply_diaphragm(u, dia)
    exp_uX6, exp_uZ6, exp_thY6 = 0.1, -0.1, 0.05
    assert abs(u2[_full_dof_index(6, "Ux")] - exp_uX6) < 1e-9
    assert abs(u2[_full_dof_index(6, "Uz")] - exp_uZ6) < 1e-9
    assert abs(u2[_full_dof_index(6, "Ry")] - exp_thY6) < 1e-9
    # free DOF untouched
    assert abs(u2[_full_dof_index(6, "Uy")] - 0.037) < 1e-12

    C = build_diaphragm_constraints(dia)
    resid = float(np.max(np.abs(C @ u2)))
    assert resid < 1e-9, f"diaphragm constraint residual {resid}"



# ============================================================
# 5. LOAD VIEWER (per-case visual verification)
# ============================================================
# matplotlib 3D viewer that overlays the loads of ONE load case on the cube.
# Plot axes follow Rev2: (x=X, y=Z, z=Y). Arrow direction uses the load's global
# signed vector so +X/-X/+Y/-Y/+Z/-Z is visually obvious. Rotate/zoom/pan via the
# native matplotlib toolbar (interactive when a GUI backend is active).

_LOAD_COLORS = {
    "Dead": "saddlebrown",
    "Live": "seagreen",
    "Wind": "dodgerblue",
    "Seismic": "crimson",
    "Member Point Load": "darkviolet",
}


def _plot_pt(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Map global (X,Y,Z) to Rev2 plot coords (x=X, y=Z, z=Y) in display units."""
    return (R2.to_display_length(x), R2.to_display_length(z), R2.to_display_length(y))


def _draw_cube_base(ax) -> None:
    """Draw the cube wireframe, nodes, IDs, supports, and global axes (Rev2-style)."""
    for i, j, mtype in R2.members:
        p_i = _plot_pt(*R2.nodes[i])
        p_j = _plot_pt(*R2.nodes[j])
        color = "darkorange" if mtype == "Column" else "steelblue"
        ax.plot([p_i[0], p_j[0]], [p_i[1], p_j[1]], [p_i[2], p_j[2]],
                color=color, linewidth=2, alpha=0.8)
    for n, (x, y, z) in R2.nodes.items():
        px, py, pz = _plot_pt(x, y, z)
        ax.scatter([px], [py], [pz], color="red", s=40, depthshade=True)
        ax.text(px, py, pz, f" {n}", color="black", fontsize=9, fontweight="bold")
    for n in R2.BASE_NODES:
        px, py, pz = _plot_pt(*R2.nodes[n])
        ax.scatter([px], [py], [pz], marker="^", color="black", s=140, zorder=5)
    a = R2.to_display_length(R2.L * 0.4)
    ax.quiver(0, 0, 0, a, 0, 0, color="black", arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, 0, a, 0, color="black", arrow_length_ratio=0.15)
    ax.quiver(0, 0, 0, 0, 0, a, color="black", arrow_length_ratio=0.15)
    ax.text(a * 1.05, 0, 0, "X", fontsize=9, fontweight="bold")
    ax.text(0, a * 1.05, 0, "Z", fontsize=9, fontweight="bold")
    ax.text(0, 0, a * 1.05, "Y", fontsize=9, fontweight="bold")
    ax.set_xlim(R2.to_display_length(-1), R2.to_display_length(7))
    ax.set_ylim(R2.to_display_length(-1), R2.to_display_length(7))
    ax.set_zlim(R2.to_display_length(-1), R2.to_display_length(7))
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=20, azim=-60)


def _draw_diaphragm(ax) -> None:
    """Shade the roof diaphragm ring (nodes 5-6-7-8) and label the master node."""
    if not DIAPHRAGMS:
        return
    dia = DIAPHRAGMS[0]
    ring = [5, 6, 7, 8, 5]
    pts = [_plot_pt(*R2.nodes[n]) for n in ring]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts],
            color="mediumpurple", linewidth=1.5, alpha=0.6)
    cx = sum(p[0] for p in pts[:-1]) / 4
    cy = sum(p[1] for p in pts[:-1]) / 4
    cz = sum(p[2] for p in pts[:-1]) / 4
    ax.text(cx, cy, cz, f"Rigid Diaphragm\n(master = node {dia.master_node})",
            color="mediumpurple", fontsize=8, fontweight="bold", ha="center")

def _draw_arrow(ax, tip_xyz, vec_xyz, color, label=None) -> None:
    """Draw one load arrow whose tail is offset back from the tip by -vec."""
    tip = _plot_pt(*tip_xyz)
    dv = np.asarray(vec_xyz, float)
    dv_plot = (R2.to_display_length(dv[0]), R2.to_display_length(dv[2]),
               R2.to_display_length(dv[1]))
    ax.quiver(tip[0] - dv_plot[0], tip[1] - dv_plot[1], tip[2] - dv_plot[2],
              dv_plot[0], dv_plot[1], dv_plot[2],
              color=color, linewidth=2, arrow_length_ratio=0.25)
    if label:
        ax.text(tip[0], tip[1], tip[2], label, color=color, fontsize=7,
                fontweight="bold")


def _magnitude_label(kn: float, kind: str) -> str:
    """Human label for a load magnitude in display units (kN or kN/m)."""
    disp = R2.to_display_force(kn * N_PER_KN)
    if kind == "line":
        return f"{disp:.2f} kN/m"
    return f"{disp:.2f} kN"


def _draw_nodal_load(ax, load: "NodalLoad", color: str) -> None:
    """Draw a nodal load arrow at its node (global vector)."""
    vec = np.array([load.fx, load.fy, load.fz], float)
    if not np.any(vec):
        return
    mag_kn = float(np.linalg.norm(vec)) / N_PER_KN
    unit = vec / (np.linalg.norm(vec) + 1e-12)
    tip = np.asarray(R2.nodes[load.node_id], float)
    _draw_arrow(ax, tip, unit, color,
                label=f"{_magnitude_label(mag_kn, 'force')}\n@N{load.node_id}")


def _draw_distributed_load(ax, load: "MemberDistributedLoad", color: str) -> None:
    """Draw a row of small arrows along a member for a uniform line load."""
    i, j = _member_end_nodes(load.member_id)
    p_i = np.asarray(R2.nodes[i], float)
    p_j = np.asarray(R2.nodes[j], float)
    w = np.asarray(load.signed_vector(), float)
    mag_kn = float(np.linalg.norm(w)) / N_PER_KN
    unit = w / (np.linalg.norm(w) + 1e-12)
    for frac in (0.2, 0.35, 0.5, 0.65, 0.8):
        pt = p_i + (p_j - p_i) * frac
        lbl = None
        if abs(frac - 0.5) < 1e-9:
            lbl = f"{_magnitude_label(mag_kn, 'line')}\nM{load.member_id}"
        _draw_arrow(ax, pt, unit, color, label=lbl)


def _draw_point_load(ax, load: "MemberPointLoad", color: str) -> None:
    """Draw a point load arrow at its fractional location along the member."""
    i, j = _member_end_nodes(load.member_id)
    p_i = np.asarray(R2.nodes[i], float)
    p_j = np.asarray(R2.nodes[j], float)
    pt = p_i + (p_j - p_i) * load.location
    P = np.asarray(load.signed_vector(), float)
    mag_kn = float(np.linalg.norm(P)) / N_PER_KN
    unit = P / (np.linalg.norm(P) + 1e-12)
    _draw_arrow(ax, pt, unit, color,
                label=f"{_magnitude_label(mag_kn, 'force')}\nM{load.member_id} "
                      f"@a={load.location:.2f}")


def _draw_self_weight(ax) -> None:
    """Draw small -Y self-weight arrows at every node (LC1)."""
    for n in R2.nodes:
        pt = np.asarray(R2.nodes[n], float)
        _draw_arrow(ax, pt, (0.0, -1.0, 0.0), "saddlebrown")
    pt = np.asarray(R2.nodes[5], float)
    ax.text(R2.to_display_length(pt[0]), R2.to_display_length(pt[2]),
            R2.to_display_length(pt[1]) - R2.to_display_length(0.3),
            f"Self-weight {R2.to_display_force(total_self_weight_n()):.1f} kN total",
            color="saddlebrown", fontsize=8, fontweight="bold")


def render_load_case(load_case: "LoadCase", ax=None, save_path: Optional[str] = None):
    """Render the cube with ONLY this load case's loads overlaid.

    If ax is None a new 3D figure is created. Distributed loads draw a row of
    arrows along the member; point loads draw one arrow at their location; nodal
    loads draw one arrow at the node; self-weight draws -Y arrows at every node.
    The roof diaphragm ring is always indicated. If save_path is given the figure
    is saved (PNG) and closed; otherwise, in a GUI session, plt.show() is called
    for interactive rotate/zoom/pan. Returns the matplotlib Axes.
    """
    if ax is None:
        fig = plt.figure(figsize=(11, 10))
        ax = fig.add_subplot(111, projection="3d")
    _draw_cube_base(ax)
    _draw_diaphragm(ax)

    color = _LOAD_COLORS.get(load_case.category, "black")
    for load in load_case.loads:
        if isinstance(load, NodalLoad):
            _draw_nodal_load(ax, load, color)
        elif isinstance(load, MemberDistributedLoad):
            _draw_distributed_load(ax, load, color)
        elif isinstance(load, MemberPointLoad):
            _draw_point_load(ax, load, color)
    if load_case.self_weight:
        _draw_self_weight(ax)

    ax.set_title(
        f"Load Case {load_case.id} — {load_case.name} ({load_case.category})\n"
        f"Units: {UNIT_SYSTEM}  |  arrows show global direction (+X/-X/+Y/-Y/+Z/-Z)",
        fontsize=10, fontweight="bold")
    legend_elems = [
        Line2D([0], [0], color="steelblue", lw=2, label="Beam"),
        Line2D([0], [0], color="darkorange", lw=2, label="Column"),
        Line2D([0], [0], marker="^", color="black", lw=0, markersize=10,
               label="Pinned support"),
        Line2D([0], [0], color=color, lw=2, label=f"{load_case.category} load"),
        Line2D([0], [0], color="mediumpurple", lw=1.5, label="Rigid diaphragm"),
    ]
    ax.legend(handles=legend_elems, loc="upper left", fontsize=8)

    if save_path is not None:
        fig = ax.get_figure()
        fig.savefig(save_path, dpi=130, bbox_inches="tight")
        plt.close(fig)
    elif ax.get_figure().canvas.manager is not None:
        plt.show()
    return ax


def render_all_load_cases(save_dir: str) -> List[str]:
    """Render every load case to its own PNG in save_dir; return the file paths.

    Filenames: lc_01_dead.png, lc_02_roof_dead.png, ... (id + snake_case name).
    """
    os.makedirs(save_dir, exist_ok=True)
    paths: List[str] = []
    for lc in LOAD_CASES:
        slug = lc.name.lower().replace(" ", "_").replace("/", "-")
        fname = f"lc_{lc.id:02d}_{slug}.png"
        path = os.path.join(save_dir, fname)
        render_load_case(lc, ax=None, save_path=path)
        paths.append(path)
    return paths





# ============================================================
# 6. LOAD COMBINATIONS (NSCP LRFD + ASD)
# ============================================================
# Combinations follow NSCP 2015 §203.3.1 (LRFD) and §203.4.1 (ASD).
# UNVERIFIED — PDF is handwritten and image-only; using standard
# NSCP 2015 / ASCE 7-10 combinations confirmed by the user.
#
# Symbolic load-type map to the 8 physical cases (per approved decisions):
#   D = LC1 (self-weight) + LC2 (roof dead)  -> both get the D factor
#   L = LC3 (roof live)                       W = LC5 (Wx) / LC6 (Wz)
#   E = LC7 (Ex) / LC8 (Ez)
# Any combination containing W or E is expanded into X and Z variants
# (suffix a / b). No physical load is duplicated: assemble_combination
# sums factor * assemble_load_vector(case) over the referenced cases only.

# Ordered symbolic patterns {symbol: factor}. Order defines the display name.
_LRFD_BASE = [
    ("1", {"D": 1.4}),
    ("2", {"D": 1.2, "L": 1.6}),
    ("3", {"D": 1.2, "W": 1.0, "L": 1.0}),
    ("4", {"D": 1.2, "E": 1.0, "L": 1.0}),
    ("5", {"D": 0.9, "W": 1.0}),
    ("6", {"D": 0.9, "E": 1.0}),
]
_ASD_BASE = [
    ("1", {"D": 1.0}),
    ("2", {"D": 1.0, "L": 1.0}),
    ("3", {"D": 1.0, "L": 0.75, "W": 0.75}),
    ("4", {"D": 1.0, "L": 0.75, "E": 0.75}),
    ("5", {"D": 0.6, "W": 0.6}),
    ("6", {"D": 0.6, "E": 0.7}),
]


def _fmt_factor(f: float) -> str:
    """Format a load factor: at least one decimal, trailing zeros stripped."""
    s = f"{f:.2f}".rstrip("0")
    return s + "0" if s.endswith(".") else s


def _sym_label(sym: str, variant: str) -> str:
    """Return the display label for a load symbol, applying the X/Z variant."""
    if sym == "W":
        return "Wx" if variant == "X" else "Wz"
    if sym == "E":
        return "Ex" if variant == "X" else "Ez"
    return sym  # D, L


def _needs_variant(pattern: Dict[str, float]) -> bool:
    """True if the symbolic pattern contains a direction-dependent symbol (W/E)."""
    return "W" in pattern or "E" in pattern


def _expand_pattern(pattern: Dict[str, float], variant: str):
    """Turn a symbolic pattern into (display_name_body, factors{case_id:factor}).

    `variant` is None, "X", or "Z". D maps to cases 1 and 2; L to 3; W to 5/6;
    E to 7/8 depending on variant.
    """
    terms, factors = [], {}
    for sym, f in pattern.items():
        terms.append(f"{_fmt_factor(f)} {_sym_label(sym, variant)}")
        if sym == "D":
            factors[1] = f
            factors[2] = f
        elif sym == "L":
            factors[3] = f
        elif sym == "W":
            factors[5 if variant == "X" else 6] = f
        elif sym == "E":
            factors[7 if variant == "X" else 8] = f
    return " + ".join(terms), factors


def _build_combinations(method: str, prefix: str, base_id: int,
                        base_list: List) -> List[LoadCombination]:
    """Expand one symbolic base list into LoadCombination instances."""
    combos: List[LoadCombination] = []
    cid = base_id
    for tag, pattern in base_list:
        variants = (("X", "a"), ("Z", "b")) if _needs_variant(pattern) \
            else ((None, ""),)
        for variant, letter in variants:
            body, factors = _expand_pattern(pattern, variant)
            combos.append(LoadCombination(
                id=cid, name=f"{prefix}-{tag}{letter}: {body}",
                design_method=method, factors=factors,
                description=f"NSCP 2015 {method} — {body} (D = LC1 + LC2)"))
            cid += 1
    return combos


LRFD_COMBINATIONS: List[LoadCombination] = _build_combinations(
    "LRFD", "LRFD", 101, _LRFD_BASE)
ASD_COMBINATIONS: List[LoadCombination] = _build_combinations(
    "ASD", "ASD", 201, _ASD_BASE)
LOAD_COMBINATIONS: List[LoadCombination] = LRFD_COMBINATIONS + ASD_COMBINATIONS
LOAD_COMBINATIONS_BY_ID: Dict[int, LoadCombination] = {
    c.id: c for c in LOAD_COMBINATIONS}


def assemble_combination(combo: LoadCombination) -> np.ndarray:
    """Assemble the full global-DOF vector (length TOTAL_DOF) for a combination.

    Sums factor * assemble_load_vector(case) over the referenced cases only —
    no physical load is duplicated. Result is in SI (N, N*m).
    """
    vec = np.zeros(R2.TOTAL_DOF)
    for case_id, factor in combo.factors.items():
        if case_id not in LOAD_CASES_BY_ID:
            raise KeyError(f"combination {combo.id} references unknown case {case_id}")
        vec += factor * assemble_load_vector(LOAD_CASES_BY_ID[case_id])
    return vec


def validate_combination(combo: LoadCombination, tol: float = 1e-6):
    """Validate a combination: intended total force vs assembled-vector sum.

    intended = sum(factor * case intended total). Returns (intended, computed,
    equilibrium_error); raises ValueError if the error exceeds `tol`. Each
    referenced case is itself validated via validate_load_case.
    """
    vec = assemble_combination(combo)
    computed = np.array(_sum_components(vec), dtype=float)
    intended = np.zeros(3)
    for case_id, factor in combo.factors.items():
        case_intended, _, _ = validate_load_case(LOAD_CASES_BY_ID[case_id])
        intended += factor * case_intended
    error = float(np.linalg.norm(intended - computed))
    if error > tol:
        raise ValueError(
            f"combination {combo.id} ('{combo.name}') equilibrium error "
            f"{error:.6e} N exceeds tolerance {tol:.1e} N")
    return intended, computed, error


def print_combination_summary() -> None:
    """Print ID | Method | Name | Factors | Total Force table for all combos."""
    funit = "kN" if R2.UNIT_SYSTEM == "metric" else "kip"
    head = (f"{'ID':>4}  {'Method':<5} {'Name':<32} "
            f"{'Factors (case*factor)':<24} Total Force [{funit}]")
    print(head)
    print("-" * len(head))
    for combo in LOAD_COMBINATIONS:
        fx, fy, fz = _sum_components(assemble_combination(combo))
        fac = ", ".join(f"{cid}*{_fmt_factor(f)}"
                        for cid, f in sorted(combo.factors.items()))
        total = (f"[{R2.to_display_force(fx):+8.3f}, "
                 f"{R2.to_display_force(fy):+9.3f}, "
                 f"{R2.to_display_force(fz):+8.3f}]")
        print(f"{combo.id:>4}  {combo.design_method:<5} {combo.name:<32} "
              f"{fac:<24} {total}")
    print("Sign convention: downward -Y negative; +X positive; +Z positive.")


# ============================================================
# 7. VALIDATION + TESTS + VERIFICATION REPORT        [Phase 7 — TODO]
# ============================================================
# TODO(Phase 7): validate_load_case() summary (intended vs computed, equilibrium
#   error); 11 automated tests (see _rev3_state.md); verification report that
#   distinguishes LOAD-INPUT validation from STRUCTURAL analysis (deferred Rev4).


# ============================================================
# NOTES (state) — see D:\che school 2627\lab02\Rev3\_rev3_state.md
# ============================================================
# Approved: Q1 (framework+equilibrium only, no FEA), Q2 (nodes 5-8), Q3 (master 5,
# rigid X-Z plane, uY/rX/rZ free), Q4 (import Rev2). F1-F7 approved.
# Phase 2 Step 0 BLOCKER: Rev2 runs at import (no __main__ guard) — awaiting
# approval to add the guard before wiring the full import/run.
# ============================================================
# 8. INTERACTIVE 3D DASHBOARD (replaces the static PNG report)
# ============================================================
# Generates rev3_load_report.html: a self-contained, offline 3D dashboard (all 8
# load cases, tables, CSV export). Logic lives in rev3_dashboard.py and
# rev3_dashboard_template.html (keep both next to this file). The dashboard only
# displays quantities already computed above; nothing is re-derived.

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "rev3_load_report.html")


def build_dashboard(out_html: str = OUT_HTML) -> str:
    """Write the interactive dashboard HTML and return its path."""
    import rev3_dashboard
    return rev3_dashboard.write_dashboard(sys.modules[__name__], out_html)


if __name__ == "__main__":
    _path = build_dashboard()
    print(f"Wrote: {_path}")
    print(f"Dashboard contains {len(LOAD_CASES)} load cases and "
          f"{len(LOAD_COMBINATIONS)} load combinations.")
