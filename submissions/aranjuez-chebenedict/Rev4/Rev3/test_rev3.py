"""Rev3 automated test suite (Phase 7).

Runs 11 engineering tests against the Rev3 load framework. Each test prints
PASS/FAIL with computed vs expected values; an overall summary prints at the
end. Run headless:  python test_rev3.py   (matplotlib uses the Agg backend).

Conventions under test:
  - Global axes: X, Z lateral; Y vertical (UP). Gravity/self-weight acts in -Y.
  - SI internal (N, N/m, N*m); display converts via Rev2's to_display_* helpers.
  - Sign: downward -Y negative; +X positive; +Z positive.
"""
import os
import sys

os.environ["MPLBACKEND"] = "Agg"          # headless: no pop-up during tests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tempfile
import numpy as np
import Rev3 as R

_results = []                              # (id, name, passed, detail)


def _record(tid, name, passed, detail):
    _results.append((tid, name, bool(passed), detail))
    print(f"[{'PASS' if passed else 'FAIL'}] {tid}: {name}\n        {detail}")


def _fy(vec):
    """Global -Y component sum (N) of an assembled vector."""
    return R._sum_components(vec)[1]


# --------------------------------------------------------------------------
def T1_self_weight():
    """Total self-weight = rho * A * L * g, applied in -Y (negative)."""
    lc1 = R.assemble_load_vector(R.LOAD_CASES_BY_ID[1])
    expected = -(R.R2.MATERIAL["rho"] * R.R2.SECTION["A"]
                 * R.R2.TOTAL_MEMBER_LENGTH * R.GRAVITY)   # NEGATIVE: acts -Y
    computed = _fy(lc1)
    ok = abs(computed - expected) < 1e-6 and computed < 0
    _record("T1", "Self-weight total = rho*A*L*g, acting -Y", ok,
            f"expected {expected:.6f} N (down), computed {computed:.6f} N, "
            f"L={R.R2.TOTAL_MEMBER_LENGTH} m")


def T2_roof_dead():
    """Roof dead = 5 kN/m * 4 beams * 6 m = 120 kN downward."""
    vec = R.assemble_load_vector(R.LOAD_CASES_BY_ID[2])
    expected = -R.ROOF_DEAD_KN_M * R.N_PER_KN * len(R.ROOF_BEAM_IDS) * R.R2.L
    computed = _fy(vec)
    ok = abs(computed - expected) < 1e-6
    _record("T2", "Roof dead LC2 = 5 kN/m x 4 x 6 m = 120 kN down", ok,
            f"expected {expected:.1f} N, computed {computed:.1f} N")


def T3_roof_live():
    """Roof live = 3 kN/m * 4 beams * 6 m = 72 kN downward."""
    vec = R.assemble_load_vector(R.LOAD_CASES_BY_ID[3])
    expected = -R.ROOF_LIVE_KN_M * R.N_PER_KN * len(R.ROOF_BEAM_IDS) * R.R2.L
    computed = _fy(vec)
    ok = abs(computed - expected) < 1e-6
    _record("T3", "Roof live LC3 = 3 kN/m x 4 x 6 m = 72 kN down", ok,
            f"expected {expected:.1f} N, computed {computed:.1f} N")


def T4_center_point():
    """Center point load = 5 kN x 4 beams = 20 kN downward, at midspan."""
    lc4 = R.LOAD_CASES_BY_ID[4]
    vec = R.assemble_load_vector(lc4)
    expected = -R.CENTER_LOAD_KN * R.N_PER_KN * len(R.ROOF_BEAM_IDS)
    computed = _fy(vec)
    midpoints_ok = all(
        abs(l.location - 0.5) < 1e-12
        for l in lc4.loads if isinstance(l, R.MemberPointLoad))
    ok = abs(computed - expected) < 1e-6 and midpoints_ok
    _record("T4", "Center point LC4 = 5 kN x 4 = 20 kN down @ midspan", ok,
            f"expected {expected:.1f} N, computed {computed:.1f} N, "
            f"all loads at location 0.5: {midpoints_ok}")


def T5_wind():
    """Wind X (LC5) = +10 kN in X; Wind Z (LC6) = +10 kN in Z; 4 nodes each."""
    fx5, fy5, fz5 = R._sum_components(R.assemble_load_vector(R.LOAD_CASES_BY_ID[5]))
    fx6, fy6, fz6 = R._sum_components(R.assemble_load_vector(R.LOAD_CASES_BY_ID[6]))
    exp_w = R.WIND_TOTAL_KN * R.N_PER_KN
    ok = (abs(fx5 - exp_w) < 1e-6 and abs(fz5) < 1e-6
          and abs(fz6 - exp_w) < 1e-6 and abs(fx6) < 1e-6)
    _record("T5", "Wind LC5 = +10 kN in X; LC6 = +10 kN in Z (4 nodes)", ok,
            f"LC5 [{fx5:.0f},{fy5:.0f},{fz5:.0f}] N, LC6 [{fx6:.0f},{fy6:.0f},{fz6:.0f}] N, "
            f"expected +/-{exp_w:.0f} N")


def T6_seismic():
    """Seismic X (LC7) = +15 kN in X; Seismic Z (LC8) = +15 kN in Z; 4 nodes."""
    fx7, fy7, fz7 = R._sum_components(R.assemble_load_vector(R.LOAD_CASES_BY_ID[7]))
    fx8, fy8, fz8 = R._sum_components(R.assemble_load_vector(R.LOAD_CASES_BY_ID[8]))
    exp_e = R.SEISMIC_TOTAL_KN * R.N_PER_KN
    ok = (abs(fx7 - exp_e) < 1e-6 and abs(fz7) < 1e-6
          and abs(fz8 - exp_e) < 1e-6 and abs(fx8) < 1e-6)
    _record("T6", "Seismic LC7 = +15 kN in X; LC8 = +15 kN in Z (4 nodes)", ok,
            f"LC7 [{fx7:.0f},{fy7:.0f},{fz7:.0f}] N, LC8 [{fx8:.0f},{fy8:.0f},{fz8:.0f}] N, "
            f"expected +/-{exp_e:.0f} N")


def T7_diaphragm():
    """Diaphragm constraints satisfied: max|C.u| < 1e-9 on the projected field."""
    dia = R.DIAPHRAGMS[0]
    C = R.build_diaphragm_constraints(dia)
    u = np.zeros(R.R2.TOTAL_DOF)
    m = dia.master_node
    u[R._full_dof_index(m, "Ux")] = 0.137
    u[R._full_dof_index(m, "Uz")] = -0.221
    u[R._full_dof_index(m, "Ry")] = 0.042
    proj = R.apply_diaphragm(u, dia)
    residual = float(np.max(np.abs(C @ proj)))
    shape_ok = C.shape == (9, R.R2.TOTAL_DOF)
    ok = residual < 1e-9 and shape_ok
    _record("T7", "Diaphragm constraints satisfied (max|C.u| < 1e-9)", ok,
            f"C shape {C.shape}, max|C.u| = {residual:.3e} N")


def T8_lrfd_1():
    """LRFD-1 = 1.4 * (LC1 + LC2) = -187.164 kN."""
    combo = R.LOAD_COMBINATIONS_BY_ID[101]
    vec = R.assemble_combination(combo)
    lc1 = _fy(R.assemble_load_vector(R.LOAD_CASES_BY_ID[1]))
    lc2 = _fy(R.assemble_load_vector(R.LOAD_CASES_BY_ID[2]))
    expected = 1.4 * (lc1 + lc2)
    computed = _fy(vec)
    ok = abs(computed - expected) < 1e-6
    _record("T8", "LRFD-1 = 1.4*(LC1+LC2) = -187.164 kN", ok,
            f"expected {expected/1000:.4f} kN, computed {computed/1000:.4f} kN")


def T9_all_combos():
    """All 20 combinations have equilibrium error < 1e-6."""
    max_err = 0.0
    for c in R.LOAD_COMBINATIONS:
        _, _, err = R.validate_combination(c)
        max_err = max(max_err, err)
    ok = max_err < 1e-6 and len(R.LOAD_COMBINATIONS) == 20
    _record("T9", "All 20 combinations: equilibrium error < 1e-6", ok,
            f"{len(R.LOAD_COMBINATIONS)} combos, max error = {max_err:.3e} N")


def T10_viewer_pngs():
    """Load viewer produces 8 non-empty PNGs.
    FIX: do the size checks INSIDE the tempdir context."""
    ok = False
    detail = ""
    with tempfile.TemporaryDirectory() as d:
        paths = R.render_all_load_cases(d)
        existing = [p for p in paths if os.path.exists(p)]
        nonempty = [p for p in existing if os.path.getsize(p) > 0]
        ok = (len(paths) == 8 and len(existing) == 8 and len(nonempty) == 8)
        sizes = [os.path.getsize(p) for p in nonempty] if nonempty else []
        detail = (f"{len(nonempty)}/8 PNGs written non-empty "
                  f"(min size {min(sizes) if sizes else 0} B, "
                  f"max size {max(sizes) if sizes else 0} B)")
    _record("T10", "Load viewer renders 8 non-empty PNGs", ok, detail)


def T11_unit_system():
    """Switching UNIT_SYSTEM changes display, not internal SI vectors."""
    vec_metric = R.assemble_load_vector(R.LOAD_CASES_BY_ID[2])
    disp_metric = R.R2.to_display_force(_fy(vec_metric))
    len_metric = R.R2.to_display_length(R.R2.L)
    labels_metric = R.R2.get_unit_labels()

    saved = R.R2.UNIT_SYSTEM
    try:
        R.R2.UNIT_SYSTEM = "imperial"
        vec_imperial = R.assemble_load_vector(R.LOAD_CASES_BY_ID[2])
        disp_imperial = R.R2.to_display_force(_fy(vec_imperial))
        len_imperial = R.R2.to_display_length(R.R2.L)
        labels_imperial = R.R2.get_unit_labels()
    finally:
        R.R2.UNIT_SYSTEM = saved

    internals_same = np.allclose(vec_metric, vec_imperial, atol=0.0)
    display_differs = (abs(disp_metric - disp_imperial) > 1e-9
                       and abs(len_metric - len_imperial) > 1e-9
                       and labels_metric != labels_imperial)
    ok = internals_same and display_differs
    _record("T11", "Metric<->Imperial: display changes, internal SI identical", ok,
            f"vectors identical: {internals_same}; display "
            f"{disp_metric:.1f} kN vs {disp_imperial:.3f} kip, "
            f"{len_metric} m vs {len_imperial:.2f} ft, "
            f"labels {labels_metric['force']}->{labels_imperial['force']}")


def main():
    print("=" * 70)
    print("Rev3 TEST SUITE (Phase 7)")
    print("=" * 70)
    for t in (T1_self_weight, T2_roof_dead, T3_roof_live, T4_center_point,
              T5_wind, T6_seismic, T7_diaphragm, T8_lrfd_1, T9_all_combos,
              T10_viewer_pngs, T11_unit_system):
        t()
    n_pass = sum(1 for r in _results if r[2])
    print("-" * 70)
    print(f"SUMMARY: {n_pass}/{len(_results)} tests passed")
    for tid, name, passed, _ in _results:
        if not passed:
            print(f"  FAILED -> {tid}: {name}")
    print("-" * 70)
    return 0 if n_pass == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())