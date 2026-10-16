# Rev3 Build State (recovery source — read at the START of every phase)

> This file is the single source of truth if context is lost to compaction.
> Update it at the END of every phase. Do not proceed past a phase without
> user confirmation.

Project root: `D:\che school 2627\lab02`
Backend model core: `D:\che school 2627\lab02\Rev2\Rev2.py` (imported, NOT copied)
This deliverable:  `D:\che school 2627\lab02\Rev3\Rev3.py`
NSCP source PDF:  `D:\che school 2627\lab02\Loads and Load Combination_260916_200537 (1).pdf`
                   (image-only, 8 pages — edition/factors NOT yet verified from text)

## Axis convention (from Rev2, unchanged)
- Global: X, Z = lateral; Y = vertical (UP). Gravity acts in NEGATIVE global Y.
- Local: L1 = axial, L2/L3 = cross-section axes (Rev2 `local_axes()` returns
  global-coordinate vectors — the hook for projecting global-direction loads).

## Model geometry (Rev2, unchanged) — confirmed node/member tables
Nodes (X,Y,Z metres): 1(0,0,0) 2(6,0,0) 3(6,0,6) 4(0,0,6) [base, pinned]
                       5(0,6,0) 6(6,6,0) 7(6,6,6) 8(0,6,6) [roof, Y=6]
Members: 1-4 base ring (Beams, beta=0); 5-8 ROOF ring (Beams, beta=0);
         9-12 columns 1-5,2-6,3-7,4-8 (Columns, beta=90).
ROOF BEAMS = members 5,6,7,8. ROOF NODES = 5,6,7,8.
Supports: pinned (Ux,Uy,Uz fixed) at nodes 1-4. DOF: 6/node; 48 total / 36 active.
Releases: Beam Mz released at both ends.

## APPROVED DECISIONS
Q1 — Solver scope: LOAD FRAMEWORK + EQUILIBRIUM VALIDATION ONLY.
     No stiffness/FEA solve. Reactions/displacements/member forces DEFERRED to Rev4.
Q2 — Lateral-load nodes (Wind/Seismic): roof nodes 5,6,7,8 (Y=6). 4 nodes each.
Q3 — Diaphragm: master = node 5. Rigid-body kinematics in X-Z plane at Y=6:
       uX_i = uX_m - thetaY*(z_i - z_m)
       uZ_i = uZ_m + thetaY*(x_i - x_m)
       thetaY_i = thetaY_m
     DO NOT force identical translations. uY, rX, rZ remain FREE.
Q4 — Packaging: IMPORT Rev2 (add Rev2 dir to sys.path). Do NOT copy model core.

F1 — ROOF DEAD = 5 kN/m (distributed member line load, global -Y), beams 5-8.
     (interpreted kN/m, NOT kN-m moment; engineering context = beam UDL.)
F2 — ROOF LIVE = 3 kN/m (distributed member line load, global -Y), beams 5-8.
F3 — CENTER LOAD = 5 kN point at member MIDPOINT of beams 5-8, global -Y.
     No new physical node; use consistent/equivalent nodal loads (P/2 per end)
     while preserving conceptual midpoint for the viewer.
F4 — Rev2 has NO solver -> analysis out of scope; validate load totals +
     equilibrium only. Stiffness solve deferred.
F5 — Lateral nodes = 5,6,7,8; exposed as configurable LATERAL_LOAD_NODES list.
F6 — Diaphragm: master node 5, in-plane Ux & Uz (rigid-body) + Ry; uY,rX,rZ free.
F7 — NSCP edition: examples match NSCP 2015 (ASCE 7-10 factors). MUST be verified
     from the PDF before Phase 6; do not invent.

## MATERIAL — A36 Steel (reference-file PRECISE, SI internal) [RISA Materials Library Metric, "Hot Rolled"]
E  = 199,948e6 Pa   (199.948 GPa)
Fy = 248.2e6 Pa     (248.2 MPa)
Fu = 399.9e6 Pa     (399.9 MPa)
rho= 7,848.76 kg/m^3
nu = 0.30
G  = 76,904e6 Pa    (extra)
alpha = 11.7e-6 /C  (extra)

## SECTION — W 100x100 (== W 4x13 imperial) [AISC DB v16.0, row W4X13/W100X19.3]
A  = 2.470e-3 m^2 ; Ix = 4.70e-6 m^4 ; Iy = 1.61e-6 m^4 ; J = 6.29e-8 m^4
d  = 0.106 m ; bf = 0.103 m ; tf = 0.00876 m ; tw = 0.00711 m
Display label: metric "W 100x100" / imperial "W 4x13".

## UNIT CONSTANTS — reuse Rev2 UNITS dict (NIST SP 811, defined once). No inline factors.
(Rev2 exposes: M_TO_MM, MM_TO_IN, M_TO_FT, FT_TO_M, N_TO_KIP, N_PER_KN, PA_PER_MPA,
 MPA_TO_KSI, KG_TO_LB, M2_TO_MM2, MM2_TO_IN2, M4_TO_MM4, MM4_TO_IN4, etc.)

## NSCP factors — STATUS: UNVERIFIED (do NOT hard-code until PDF re-read in Phase 6)
User-provided example LRFD set (to verify): 1.4D; 1.2D+1.6L; 1.2D+1.0W+1.0L;
1.2D+1.0E+1.0L; 0.9D+1.0W; 0.9D+1.0E. ASD = non-factored (D, L, W, E) equivalents.
ACTION: re-read PDF combination page before Phase 6; if ambiguous -> mark edition
UNVERIFIED and ASK user.

## Eight physical load cases (target)
1 DEAD/SELF-WEIGHT (Dead; SW on; global -Y; factor -1; W=rho*Vol*g per member)
2 ROOF DEAD (Dead; 5 kN/m; global -Y; beams 5-8)
3 ROOF LIVE (Live; 3 kN/m; global -Y; beams 5-8)
4 ROOF BEAM CENTER LOAD (Point; 5 kN; global -Y; midpoint of beams 5-8)
5 WIND X (Wind; total 10 kN; global +X; 4 nodes x 2.5 kN)
6 WIND Z (Wind; total 10 kN; global +Z; 4 nodes x 2.5 kN)
7 SEISMIC X (Seismic; total 15 kN; global +X; 4 nodes x 3.75 kN)
8 SEISMIC Z (Seismic; total 15 kN; global +Z; 4 nodes x 3.75 kN)

## FILES CREATED SO FAR
- D:\che school 2627\lab02\Rev3\                      (folder)
- D:\che school 2627\lab02\Rev3\_rev3_state.md        (this file)
- D:\che school 2627\lab02\Rev3\Rev3.py               (skeleton: docstring, Rev2
                                                        import, Phase 2-7 markers)

## PHASE STATUS
- Phase 1 (architecture + this state file): DONE, approved.
- Phase 2 (load-case data model): DONE — implemented + verified, approved.
- Phase 3 (load application): DONE — implemented + verified, approved.
- Phase 4 (diaphragm constraints): DONE — implemented + verified, approved.
- Phase 5 (load viewer): DONE — implemented + verified, awaiting confirmation.
- Phases 6-7: NOT STARTED (TODO placeholders only).

### PHASE 2 DETAIL (completed)
- Rev2 `__main__` guard ADDED (approved). Backup: Rev2/Rev2_pre_main_guard.bak.py.
  * `python Rev2.py` -> still writes cube_model.xlsx + cube_model.html + plt.show() pop-up.
  * `import Rev2` -> SILENT (no files, no output, no pop-up). VERIFIED both ways.
  * Refactor via one-shot script (rev2 kept intact); all defs/constants stay module-level.
- Rev3.py dataclasses implemented (Section 2): NodalLoad, MemberDistributedLoad,
  MemberPointLoad, Diaphragm, LoadCase, LoadCombination — all with type hints,
  docstrings, and __post_init__ validation.
- Unit tags UNIT_FORCE="kN"/UNIT_LINE="kN/m"/UNIT_MOMENT="kN*m" kept distinct
  (spec item 11); _require_unit() rejects incompatible unit tags. VERIFIED.
- 8 physical load cases built from CONFIG constants via _build_load_cases():
  LOAD_CASES (list) + LOAD_CASES_BY_ID (dict). LC1 self-weight (0 explicit loads);
  LC2 5 kN/m x4 beams; LC3 3 kN/m x4; LC4 5 kN point @midspan x4; LC5/6 wind 2.5 kN
  x4; LC7/8 seismic 3.75 kN x4. All SI internally (N, N/m).
- DIAPHRAGMS: 1 roof diaphragm (master=5, constrained 6/7/8, DOF Ux,Uz,Ry). Wired
  as constraint equations in Phase 4 (data object exists now).
- BUG FOUND+FIXED in verification: direction double-negative (dir=-Y AND sign=-1
  gave +Y). Fixed by using reference axis _DIR_POS_Y + sign=-1. LC2/3/4 now correctly
  -Y (down). Lesson: keep applying signed_vector() checks in later phases.
- VERIFIED: py_compile OK; import OK (8 cases, 1 diaphragm); NaN/unit/method guards
  raise ValueError; LC2 vec=(0,-5000,0), LC3=(0,-3000,0), LC4=(0,-5000,0).

## KNOWN BLOCKER (Phase 2 STEP 0) — RESOLVED
Rev2 `__main__` guard added (approved). Rev2 is now import-safe.


### PHASE 3 DETAIL (completed)
- Load application implemented (Section 3). Full-DOF vector length = TOTAL_DOF (48),
  FIXED numbering: index = node_rank*6 + component (sorted nodes, DOF_NAMES order).
- DESIGN DEVIATION (flag to user): vector RETAINS loads at restrained DOFs too
  (does NOT skip them), so total applied force = total weight for equilibrium
  validation. _is_restrained() + _active_dof_indices() exposed for a future
  solver (Rev4) to project onto active DOFs. This preserves physically-complete
  load records; documented in the Section-3 header comment.
- Functions (all SI: N, N/m, N*m):
  * _full_dof_index(node,dof), _is_restrained(node,dof), _active_dof_indices()
  * _member_end_nodes(id), _member_length(id), _member_local_axes(id)
  * _add_global(vec, node, force, moment)
  * _apply_distributed(vec, load): w*L/2 per end (translational) + fixed-end
    moments w*L^2/12 per end about bending axis (L2->L3, L3->L2).
  * _apply_point(vec, load): P*(1-a) / P*a per end + fixed-end moments
    P*a*b^2*L / P*a^2*b*L about bending axis (midspan a=b=0.5 -> PL/8).
  * self_weight_nodal_forces(): W=rho*A*L*g per member, lumped half to each end (-Y).
  * total_self_weight_n(): rho*A*total_length*g.
  * assemble_load_vector(case) -> np.ndarray(TOTAL_DOF); adds self-weight if flagged.
  * validate_load_case(case, tol=1e-6) -> (intended, computed, error); raises if > tol.
- Sign convention documented in docstrings + Section-3 header (uniform w*L/2 +
  wL^2/12; point P*(1-a)/P*a + Pa b^2 L). No new physical node for midpoint loads.
- VERIFIED (all errors EXACTLY 0.0):
  * LC1 self-weight: total = rho*A*L*g = 13688.352 N; vector sum [0,-13688.352,0]; err 0.
  * LC2 roof dead: 5 kN/m * 4 beams * 6 m = 120 kN; vector sum [0,-120000,0] N; err 0.
  * All 8 cases intended==computed, err=0.0 (LC3 -72kN, LC4 -20kN, LC5 +10kN,
    LC6 +10kN, LC7 +15kN, LC8 +15kN).

### PHASE 4 DETAIL (completed) — DIAPHRAGM
- Roof diaphragm at Y=6 over nodes 5,6,7,8. Master = node 5. Constrained (slave)
  nodes = 6,7,8. Constrained DOFs per node = Ux, Uz, Ry (thetaY). Free DOFs =
  Uy, Rx, Rz (NOT forced equal — rigid-body only).
- Functions (Section 4):
  * build_diaphragm_constraints(diaphragm) -> np.ndarray shape (9, 48). Each slave
    adds 3 rows: [uX_i - uX_m + thY_m*(z_i-z_m)=0], [uZ_i - uZ_m - thY_m*(x_i-x_m)=0],
    [thY_i - thY_m=0]. C.u = 0.
  * apply_diaphragm(vec, diaphragm) -> new vector; master DOFs unchanged, slave
    Ux/Uz/Ry overwritten from rigid-body kinematics; slave Uy/Rx/Rz untouched.
  * test_diaphragm_handcheck() -> asserts (embedded in Rev3.py).
- SIGN CONVENTION (UPDATED to right-hand rule per user approval):
     uX_i = uX_m + thY*(z_i - z_m) ; uZ_i = uZ_m - thY*(x_i - x_m) ; thY_i = thY_m.
  thetaY positive = counterclockwise rotation about +Y (right-hand rule), viewed
  from +Y looking toward the origin. Matches RISA/STAAD + Hibbeler/Gere. Documented
  in the Section-4 header and the constraint-function docstring.
- VERIFIED (after flip):
  * test_diaphragm_handcheck() PASSED.
  * Hand-check slave 6 (x=6,z=0), master (0.1,0.2,0.05): uX=0.1 (err 0), uZ=-0.1
    (err 2.78e-17), Ry=0.05 (err 0). All < 1e-9.
  * All slaves: n6 (0.1,-0.1), n7 (0.4,-0.1), n8 (0.4,0.2) — correct CCW about +Y.
  * C shape (9,48); max|C.u| on projected vector = 0.0 (<1e-9); rank(C)=9.
  * Free DOF Uy untouched on all diaphragm nodes.

### PHASE 5 DETAIL (completed) — LOAD VIEWER
- matplotlib 3D viewer (TkAgg for interactive; use Agg if headless — noted in code).
- Functions (Section 5):
  * _plot_pt(x,y,z) -> plot coords (x=X, y=Z, z=Y) in display units (matches Rev2).
  * _draw_cube_base(ax): cube wireframe, nodes+IDs, pinned supports, global X/Y/Z
    triad; fixed axis ranges -1..7 (as required); view elev=20 azim=-60.
  * _draw_diaphragm(ax): roof ring 5-6-7-8 + label "Rigid Diaphragm (master=node 5)".
  * _draw_arrow(ax, tip, vec, color, label): one quiver, tail offset by -vec.
  * _draw_nodal_load / _draw_distributed_load (row of arrows @20/35/50/65/80%) /
    _draw_point_load (arrow at load.location) / _draw_self_weight (-Y at each node).
  * render_load_case(load_case, ax=None, save_path=None) -> Axes. Draws cube +
    diaphragm + THIS case's loads only; title "Load Case <id> — <name> (<category>)";
    legend (Beam/Column/Pinned/<category>/Diaphragm); if save_path -> PNG + close;
    else if GUI -> plt.show() (rotate/zoom/pan via native toolbar).
  * render_all_load_cases(save_dir) -> list of PNG paths; one per case.
- Arrow colors by category: Dead saddlebrown, Live seagreen, Wind dodgerblue,
  Seismic crimson, Member Point Load darkviolet. Magnitude labels in display units
  (kN / kN/m) via to_display_force.
- VERIFIED: py_compile exit 0; rendered all 8 cases to Rev3/load_views/*.png
  (each ~200KB, no errors). LC2 visual confirmed: 5.00 kN/m downward arrows on all
  4 roof beams, node IDs, pinned triangles, diaphragm ring+label, X/Y/Z triad,
  legend, -1..7 ranges. render_load_case(LC2, ax=...) also OK.

## PHASE 6 DETAIL (completed) — NSCP LOAD COMBINATIONS
- EDITION: NSCP 2015 §203.3.1 (LRFD) and §203.4.1 (ASD). UNVERIFIED — the source
  PDF ("Loads and Load Combination_260916_200537 (1).pdf") is HANDWRITTEN and
  image-only (0 extractable text); using standard NSCP 2015 / ASCE 7-10
  combinations CONFIRMED by the user. No factors invented from the PDF.
- Symbolic base patterns _LRFD_BASE / _ASD_BASE ({symbol: factor}); expanded
  programmatically by _build_combinations(). Direction-dependent symbols (W, E)
  expand into X and Z variants (suffix a / b). D maps to cases 1 AND 2
  (self-weight + roof dead); L -> case 3; W -> case 5 (Wx)/6 (Wz);
  E -> case 7 (Ex)/8 (Ez).
- LRFD (6 base -> 10 combos, ids 101-110):
  LRFD-1 1.4 D | LRFD-2 1.2 D + 1.6 L | LRFD-3a/3b 1.2 D + 1.0 Wx/Wz + 1.0 L |
  LRFD-4a/4b 1.2 D + 1.0 Ex/Ez + 1.0 L | LRFD-5a/5b 0.9 D + 1.0 Wx/Wz |
  LRFD-6a/6b 0.9 D + 1.0 Ex/Ez.
- ASD (6 base -> 10 combos, ids 201-210):
  ASD-1 1.0 D | ASD-2 1.0 D + 1.0 L | ASD-3a/3b 1.0 D + 0.75 L + 0.75 Wx/Wz |
  ASD-4a/4b 1.0 D + 0.75 L + 0.75 Ex/Ez | ASD-5a/5b 0.6 D + 0.6 Wx/Wz |
  ASD-6a/6b 0.6 D + 0.7 Ex/Ez.
- Functions (Section 6):
  * _fmt_factor / _sym_label / _needs_variant / _expand_pattern / _build_combinations
    (programmatic expansion; no inline factor tables).
  * LRFD_COMBINATIONS, ASD_COMBINATIONS, LOAD_COMBINATIONS, LOAD_COMBINATIONS_BY_ID.
  * assemble_combination(combo) -> np.ndarray(TOTAL_DOF) = sum(factor * case_vec);
    NO physical load duplication (reuses assemble_load_vector per case).
  * validate_combination(combo, tol=1e-6) -> (intended, computed, error); raises
    if error > tol; also validates each referenced case via validate_load_case.
  * print_combination_summary() -> ID | Method | Name | Factors | Total Force[kN/kip].
- VERIFIED (py_compile exit 0; Rev3.py = 1075 lines):
  * LRFD 10, ASD 10, TOTAL 20 combos; IDs unique (20), names unique (20).
  * max equilibrium error over ALL 20 combos = 2.91e-11 N (< 1e-6). All vectors
    length 48.
  * LRFD-1 (1.4 D): factors {1:1.4, 2:1.4}; total = 1.4*(LC1+LC2) =
    [0, -187.164, 0] kN. Hand-check: 1.4*(-13.6884 + -120) = -187.164 kN. MATCH.
  * X/Z pair LRFD-3a has case 5 (Wx) only; LRFD-3b has case 6 (Wz) only. CORRECT.
  * Summary table printed (downward -Y negative; +X +Z positive). Sample rows:
    LRFD-3a [+10.000, -232.426, 0] ; LRFD-4b [0, -232.426, +15] ;
    ASD-3a [+7.5, -187.688, 0] ; ASD-5a [+6, -80.213, 0].

## NEXT PHASE (Phase 7) TASK LIST — VALIDATION SUMMARY + TESTS + REPORT
1. 11 automated tests (assert-based): T1 self-weight -Y; T2 roof dead 5 kN/m -Y;
   T3 roof live 3 kN/m -Y; T4 center point 5 kN at midpoint -Y; T5 Wind X 4x2.5;
   T6 Wind Z 4x2.5; T7 Seismic X 4x3.75; T8 Seismic Z 4x3.75; T9 diaphragm
   coupling [DONE]; T10 each combination assembles expected vector [Phase 6 core
   done -> formalize]; T11 viewer displays correct type/magnitude/location/direction
   [DONE via render].
2. Verification report distinguishing LOAD-INPUT validation (equilibrium/totals)
   from STRUCTURAL analysis (deferred to Rev4 — no displacements/reactions/member
   forces claimed).
3. Print validation summary per load case (Load Case X / total / nodes / eq error).
4. Update state file; run all tests; STOP for confirmation.

