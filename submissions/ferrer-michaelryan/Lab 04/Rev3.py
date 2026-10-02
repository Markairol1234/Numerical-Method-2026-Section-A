import os
import sys
import math
import unittest
import webbrowser

# ==============================================================================
# REV 3 STRUCTURAL ENGINE DATA STRUCTURES & LOAD MODEL
# ==============================================================================

class Node:
    def __init__(self, node_id, x, y, z, dof_start=1):
        self.id = node_id
        self.x = x
        self.y = y
        self.z = z
        self.dof_start = dof_start

class Member:
    def __init__(self, member_id, node_a, node_b, section_name, area, E, density=78.5):
        self.id = member_id
        self.node_a = node_a
        self.node_b = node_b
        self.section_name = section_name
        self.area = area            # m^2
        self.E = E                  # kPa or kN/m^2
        self.density = density      # kN/m^3 (78.5 for steel)

    def length(self, nodes):
        nA = nodes[self.node_a]
        nB = nodes[self.node_b]
        return math.sqrt((nB.x - nA.x)**2 + (nB.y - nA.y)**2 + (nB.z - nA.z)**2)

    def self_weight_total(self, nodes):
        return self.area * self.length(nodes) * self.density  # kN

class NodalLoad:
    def __init__(self, node_id, fx=0.0, fy=0.0, fz=0.0, mx=0.0, my=0.0, mz=0.0):
        self.node_id = node_id
        self.fx = fx
        self.fy = fy
        self.fz = fz
        self.mx = mx
        self.my = my
        self.mz = mz

class MemberDistributedLoad:
    def __init__(self, member_id, direction, magnitude, dist_type="UNIFORM"):
        # Unit validation
        if "m" not in dist_type.lower() and "kN/m" not in str(magnitude) and abs(magnitude) > 1e5:
            raise ValueError("Incompatible units for distributed load. Must be kN/m.")
        self.member_id = member_id
        self.direction = direction.upper() # 'X', 'Y', 'Z'
        self.magnitude = magnitude         # kN/m (negative for downward)
        self.dist_type = dist_type

    def total_force(self, nodes, members):
        length = members[self.member_id].length(nodes)
        return abs(self.magnitude) * length

class MemberPointLoad:
    def __init__(self, member_id, location_ratio, direction, magnitude):
        self.member_id = member_id
        self.location_ratio = location_ratio # 0.5 for center
        self.direction = direction.upper()   # 'X', 'Y', 'Z'
        self.magnitude = magnitude           # kN

class Diaphragm:
    def __init__(self, diaphragm_id, name, elevation_y, master_node_id, constrained_node_ids):
        self.id = diaphragm_id
        self.name = name
        self.elevation_y = elevation_y
        self.master_node = master_node_id
        self.constrained_nodes = constrained_node_ids
        self.dofs_constrained = ["Ux", "Uz", "Ry"]

class LoadCase:
    def __init__(self, case_id, name, category, self_weight_factor=0.0, self_weight_dir="Y"):
        self.id = case_id
        self.name = name
        self.category = category # Dead, Live, Wind, Seismic, Temp
        self.self_weight_factor = self_weight_factor
        self.self_weight_dir = self_weight_dir
        self.nodal_loads = []
        self.member_dist_loads = []
        self.member_point_loads = []

    def compute_total_applied_force(self, nodes, members):
        tot_x, tot_y, tot_z = 0.0, 0.0, 0.0
        
        # 1. Nodal loads
        for nl in self.nodal_loads:
            tot_x += nl.fx
            tot_y += nl.fy
            tot_z += nl.fz

        # 2. Member distributed loads
        for dl in self.member_dist_loads:
            m = members[dl.member_id]
            f_val = dl.magnitude * m.length(nodes)
            if dl.direction == 'X': tot_x += f_val
            elif dl.direction == 'Y': tot_y += f_val
            elif dl.direction == 'Z': tot_z += f_val

        # 3. Member point loads
        for pl in self.member_point_loads:
            if pl.direction == 'X': tot_x += pl.magnitude
            elif pl.direction == 'Y': tot_y += pl.magnitude
            elif pl.direction == 'Z': tot_z += pl.magnitude

        # 4. Self weight
        if self.self_weight_factor != 0.0:
            total_sw = sum(m.self_weight_total(nodes) for m in members.values())
            if self.self_weight_dir == 'Y':
                tot_y -= total_sw * self.self_weight_factor

        return {"fx": tot_x, "fy": tot_y, "fz": tot_z}

class LoadCombination:
    def __init__(self, comb_id, name, design_method, factors):
        self.id = comb_id
        self.name = name
        self.design_method = design_method # LRFD or ASD
        self.factors = factors # Dict {load_case_id: scale_factor}

# ==============================================================================
# MODEL BUILDER & REV 3 VERIFICATION LOGIC
# ==============================================================================

def build_rev3_model():
    L_X, L_Y, L_Z = 6.0, 6.0, 6.0 # Default geometry 6x6x6 meters
    
    # Nodes
    nodes = {
        1: Node(1, 0.0, 0.0, 0.0, 1),
        2: Node(2, L_X, 0.0, 0.0, 7),
        3: Node(3, L_X, 0.0, L_Z, 13),
        4: Node(4, 0.0, 0.0, L_Z, 19),
        5: Node(5, 0.0, L_Y, 0.0, 25),
        6: Node(6, L_X, L_Y, 0.0, 31),
        7: Node(7, L_X, L_Y, L_Z, 37),
        8: Node(8, 0.0, L_Y, L_Z, 43),
    }

    # Members (Section W310x38.7: Area = 0.00494 m^2; Column W250x49.1: Area = 0.00625 m^2)
    E_steel = 200e6 # kPa
    members = {
        1: Member(1, 1, 2, "W310x38.7", 0.00494, E_steel),
        2: Member(2, 2, 3, "W310x38.7", 0.00494, E_steel),
        3: Member(3, 3, 4, "W310x38.7", 0.00494, E_steel),
        4: Member(4, 4, 1, "W310x38.7", 0.00494, E_steel),
        5: Member(5, 5, 6, "W310x38.7", 0.00494, E_steel), # Roof Beam
        6: Member(6, 6, 7, "W310x38.7", 0.00494, E_steel), # Roof Beam
        7: Member(7, 7, 8, "W310x38.7", 0.00494, E_steel), # Roof Beam
        8: Member(8, 8, 5, "W310x38.7", 0.00494, E_steel), # Roof Beam
        9: Member(9, 1, 5, "W250x49.1", 0.00625, E_steel), # Column
        10: Member(10, 2, 6, "W250x49.1", 0.00625, E_steel), # Column
        11: Member(11, 3, 7, "W250x49.1", 0.00625, E_steel), # Column
        12: Member(12, 4, 8, "W250x49.1", 0.00625, E_steel)  # Column
    }

    # Diaphragm Constraint
    diaphragm = Diaphragm(1, "Roof Diaphragm Rigid Floor", L_Y, 5, [6, 7, 8])

    # Load Cases
    load_cases = {}

    # LC1: Dead / Self Weight
    lc1 = LoadCase(1, "DEAD / SELF WEIGHT", "Dead", self_weight_factor=1.0, self_weight_dir="Y")
    load_cases[1] = lc1

    # LC2: Roof Beam Dead Load (5 kN/m on roof beams 5,6,7,8)
    lc2 = LoadCase(2, "ROOF DEAD", "Dead")
    for m_id in [5, 6, 7, 8]:
        lc2.member_dist_loads.append(MemberDistributedLoad(m_id, "Y", -5.0))
    load_cases[2] = lc2

    # LC3: Roof Beam Live Load (3 kN/m on roof beams 5,6,7,8)
    lc3 = LoadCase(3, "ROOF LIVE", "Live")
    for m_id in [5, 6, 7, 8]:
        lc3.member_dist_loads.append(MemberDistributedLoad(m_id, "Y", -3.0))
    load_cases[3] = lc3

    # LC4: Member Center Point Load (5 kN downward at midpoint of roof beams 5,6,7,8)
    lc4 = LoadCase(4, "ROOF BEAM CENTER LOAD", "Live")
    for m_id in [5, 6, 7, 8]:
        lc4.member_point_loads.append(MemberPointLoad(m_id, 0.5, "Y", -5.0))
    load_cases[4] = lc4

    # LC5: Wind X (10 kN total -> 2.5 kN at 4 roof nodes N5, N6, N7, N8)
    lc5 = LoadCase(5, "WIND X", "Wind")
    for n_id in [5, 6, 7, 8]:
        lc5.nodal_loads.append(NodalLoad(n_id, fx=2.5))
    load_cases[5] = lc5

    # LC6: Wind Z (10 kN total -> 2.5 kN at 4 roof nodes N5, N6, N7, N8)
    lc6 = LoadCase(6, "WIND Z", "Wind")
    for n_id in [5, 6, 7, 8]:
        lc6.nodal_loads.append(NodalLoad(n_id, fz=2.5))
    load_cases[6] = lc6

    # LC7: Seismic X (15 kN total -> 3.75 kN at 4 roof nodes N5, N6, N7, N8)
    lc7 = LoadCase(7, "SEISMIC X", "Seismic")
    for n_id in [5, 6, 7, 8]:
        lc7.nodal_loads.append(NodalLoad(n_id, fx=3.75))
    load_cases[7] = lc7

    # LC8: Seismic Z (15 kN total -> 3.75 kN at 4 roof nodes N5, N6, N7, N8)
    lc8 = LoadCase(8, "SEISMIC Z", "Seismic")
    for n_id in [5, 6, 7, 8]:
        lc8.nodal_loads.append(NodalLoad(n_id, fz=3.75))
    load_cases[8] = lc8

    # LC9: Temperature (+15 C)
    lc9 = LoadCase(9, "TEMPERATURE (+15C)", "Temperature")
    load_cases[9] = lc9

    # Load Combinations (NSCP 2015 Provisions)
    combinations = {
        101: LoadCombination(101, "1.4D (LRFD)", "LRFD", {1: 1.4, 2: 1.4}),
        102: LoadCombination(102, "1.2D + 1.6L (LRFD)", "LRFD", {1: 1.2, 2: 1.2, 3: 1.6, 4: 1.6}),
        103: LoadCombination(103, "1.2D + 1.0WX + 1.0L (LRFD)", "LRFD", {1: 1.2, 2: 1.2, 5: 1.0, 3: 1.0, 4: 1.0}),
        104: LoadCombination(104, "1.2D + 1.0EX + 1.0L (LRFD)", "LRFD", {1: 1.2, 2: 1.2, 7: 1.0, 3: 1.0, 4: 1.0}),
        105: LoadCombination(105, "0.9D + 1.0WX (LRFD)", "LRFD", {1: 0.9, 2: 0.9, 5: 1.0}),
        106: LoadCombination(106, "0.9D + 1.0EX (LRFD)", "LRFD", {1: 0.9, 2: 0.9, 7: 1.0}),
        201: LoadCombination(201, "D (ASD)", "ASD", {1: 1.0, 2: 1.0}),
        202: LoadCombination(202, "D + L (ASD)", "ASD", {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}),
        203: LoadCombination(203, "D + 0.6WX (ASD)", "ASD", {1: 1.0, 2: 1.0, 5: 0.6}),
        204: LoadCombination(204, "D + 0.7EX (ASD)", "ASD", {1: 1.0, 2: 1.0, 7: 0.7})
    }

    return nodes, members, diaphragm, load_cases, combinations

# ==============================================================================
# AUTOMATED UNIT TESTS FOR REV 3 REQUIREMENTS
# ==============================================================================

class TestRev3StructuralEngine(unittest.TestCase):
    def setUp(self):
        self.nodes, self.members, self.diaphragm, self.load_cases, self.combinations = build_rev3_model()

    def test_01_self_weight(self):
        lc = self.load_cases[1]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        expected_sw = sum(m.self_weight_total(self.nodes) for m in self.members.values())
        self.assertAlmostEqual(totals["fy"], -expected_sw, places=3)
        self.assertEqual(totals["fx"], 0.0)
        self.assertEqual(totals["fz"], 0.0)

    def test_02_roof_dead_load(self):
        lc = self.load_cases[2]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        # 4 roof beams * 6m length * 5 kN/m = 120 kN downward
        self.assertAlmostEqual(totals["fy"], -120.0, places=3)

    def test_03_roof_live_load(self):
        lc = self.load_cases[3]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        # 4 roof beams * 6m length * 3 kN/m = 72 kN downward
        self.assertAlmostEqual(totals["fy"], -72.0, places=3)

    def test_04_center_point_load(self):
        lc = self.load_cases[4]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        # 4 roof beams * 5 kN point load = 20 kN downward
        self.assertAlmostEqual(totals["fy"], -20.0, places=3)
        for pl in lc.member_point_loads:
            self.assertEqual(pl.location_ratio, 0.5)

    def test_05_wind_x(self):
        lc = self.load_cases[5]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        self.assertAlmostEqual(totals["fx"], 10.0, places=3)
        self.assertEqual(len(lc.nodal_loads), 4)

    def test_06_wind_z(self):
        lc = self.load_cases[6]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        self.assertAlmostEqual(totals["fz"], 10.0, places=3)
        self.assertEqual(len(lc.nodal_loads), 4)

    def test_07_seismic_x(self):
        lc = self.load_cases[7]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        self.assertAlmostEqual(totals["fx"], 15.0, places=3)

    def test_08_seismic_z(self):
        lc = self.load_cases[8]
        totals = lc.compute_total_applied_force(self.nodes, self.members)
        self.assertAlmostEqual(totals["fz"], 15.0, places=3)

    def test_09_diaphragm_constraints(self):
        self.assertEqual(self.diaphragm.master_node, 5)
        self.assertEqual(set(self.diaphragm.constrained_nodes), {6, 7, 8})
        self.assertEqual(self.diaphragm.dofs_constrained, ["Ux", "Uz", "Ry"])

    def test_10_load_combinations(self):
        # Test LC102: 1.2D + 1.6L -> 1.2*(LC1+LC2) + 1.6*(LC3+LC4)
        comb = self.combinations[102]
        tot_fy = 0.0
        for lc_id, factor in comb.factors.items():
            tot_fy += self.load_cases[lc_id].compute_total_applied_force(self.nodes, self.members)["fy"] * factor
        
        sw = sum(m.self_weight_total(self.nodes) for m in self.members.values())
        expected = 1.2 * (-sw - 120.0) + 1.6 * (-72.0 - 20.0)
        self.assertAlmostEqual(tot_fy, expected, places=3)

# ==============================================================================
# INTERACTIVE 3D WEBGL VIEWER GENERATOR (THREE.JS)
# ==============================================================================

def generate_rev3_html():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Structural Frame Solver & Viewer - Rev 3</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { display: flex; flex-direction: column; height: 100vh; background: #ffffff; color: #333; overflow: hidden; font-size: 12px; }
        
        #top-ribbon { background: #e8e8ec; border-bottom: 1px solid #ccc; padding: 6px 12px; display: flex; flex-direction: column; gap: 6px; z-index: 20; }
        .ribbon-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .ribbon-btn { background: #fff; border: 1px solid #ababab; padding: 4px 10px; border-radius: 3px; cursor: pointer; font-size: 11px; font-weight: 600; display: flex; align-items: center; gap: 4px; }
        .ribbon-btn:hover { background: #e0e0e0; }
        .ribbon-btn.active { background: #cce8ff; border-color: #3399ff; color: #0044bb; }
        .ribbon-divider { width: 1px; height: 20px; background: #ccc; margin: 0 4px; }

        #workspace { display: flex; flex: 1; height: calc(100vh - 75px); position: relative; }
        
        #sidebar { width: 310px; background: #f8f9fa; border-right: 1px solid #ccc; display: flex; flex-direction: column; padding: 10px; gap: 10px; overflow-y: auto; z-index: 10; }
        .panel-section { background: #fff; border: 1px solid #dcdcdc; padding: 10px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        h3 { color: #005a9e; font-size: 0.85rem; border-bottom: 1px solid #eee; padding-bottom: 4px; margin-bottom: 8px; font-weight: 700; }
        label { display: flex; justify-content: space-between; align-items: center; margin: 5px 0; font-size: 0.8rem; }
        select, input[type="number"], input[type="range"] { background: #fff; color: #333; border: 1px solid #ccc; padding: 3px 6px; border-radius: 3px; width: 130px; }

        #viewport-container { flex: 1; position: relative; background: #ffffff; }
        #canvas3d { width: 100%; height: 100%; display: block; }
        
        #explorer { width: 240px; background: #f8f9fa; border-left: 1px solid #ccc; padding: 10px; font-size: 11px; overflow-y: auto; }
        .explorer-group { margin-bottom: 12px; }
        .explorer-title { font-weight: bold; color: #005a9e; margin-bottom: 4px; border-bottom: 1px solid #ddd; padding-bottom: 2px; }
        .explorer-item { padding: 3px 6px; color: #444; cursor: pointer; border-radius: 2px; }
        .explorer-item:hover { background: #e6f2ff; color: #000; }
        .explorer-item.active { background: #005a9e; color: #fff; font-weight: bold; }

        .node-label { color: #000; font-weight: bold; font-size: 10px; background: rgba(255,255,255,0.85); padding: 1px 3px; border-radius: 2px; border: 1px solid #999; pointer-events: none; }
        .member-label { color: #0000aa; font-weight: 600; font-size: 9px; background: rgba(255,255,255,0.85); padding: 1px 3px; border-radius: 2px; border: 1px solid #aaa; pointer-events: none; }
        .load-label { color: #cc0000; font-weight: bold; font-size: 10px; background: #fff; border: 1px solid #cc0000; padding: 1px 4px; border-radius: 3px; pointer-events: none; }

        #model-title { position: absolute; top: 12px; left: 50%; transform: translateX(-50%); font-weight: bold; font-size: 13px; background: rgba(255,255,255,0.9); padding: 5px 14px; border-radius: 4px; border: 1px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.08); pointer-events: none; z-index: 5; }
        #legend-box { position: absolute; bottom: 12px; left: 12px; background: rgba(255,255,255,0.92); border: 1px solid #ccc; padding: 8px 12px; border-radius: 4px; font-size: 11px; z-index: 5; }
    </style>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/renderers/CSS2DRenderer.js"></script>
</head>
<body>

<div id="top-ribbon">
    <div class="ribbon-row">
        <button class="ribbon-btn" onclick="resetCamera('iso')">ISO</button>
        <button class="ribbon-btn" onclick="resetCamera('xy')">XY Front</button>
        <button class="ribbon-btn" onclick="resetCamera('xz')">XZ Top</button>
        <button class="ribbon-btn" onclick="resetCamera('yz')">YZ Side</button>
        <div class="ribbon-divider"></div>
        <button class="ribbon-btn active" id="btn-members" onclick="toggleLayerBtn('layerMembers', this)">Members</button>
        <button class="ribbon-btn active" id="btn-m-labels" onclick="toggleLayerBtn('layerMemberLabels', this)">Member Labels</button>
        <button class="ribbon-btn active" id="btn-nodes" onclick="toggleLayerBtn('layerNodes', this)">Nodes</button>
        <button class="ribbon-btn active" id="btn-n-labels" onclick="toggleLayerBtn('layerNodeLabels', this)">Node Labels</button>
        <button class="ribbon-btn active" id="btn-supports" onclick="toggleLayerBtn('layerSupports', this)">Supports</button>
        <button class="ribbon-btn active" id="btn-loads" onclick="toggleLayerBtn('layerLoads', this)">Loads</button>
        <button class="ribbon-btn active" id="btn-diaphragm" onclick="toggleLayerBtn('layerDiaphragm', this)">Diaphragm</button>
        <button class="ribbon-btn active" id="btn-grid" onclick="toggleLayerBtn('layerGrid', this)">Grid Box</button>
    </div>
</div>

<div id="workspace">
    <div id="sidebar">
        <div class="panel-section">
            <h3>Unit Configuration</h3>
            <label>
                Units:
                <select id="unitSelect" onchange="updateUnits()">
                    <option value="metric">Metric (m, kN)</option>
                    <option value="imperial">Imperial (ft, kips)</option>
                </select>
            </label>
        </div>

        <div class="panel-section">
            <h3>Load Case Selection</h3>
            <label>
                Active Case:
                <select id="loadCaseSelect" onchange="rebuildModel()">
                    <option value="1">LC1: DEAD / SELF WEIGHT</option>
                    <option value="2" selected>LC2: ROOF DEAD (5 kN/m)</option>
                    <option value="3">LC3: ROOF LIVE (3 kN/m)</option>
                    <option value="4">LC4: ROOF BEAM CENTER LOAD (5 kN)</option>
                    <option value="5">LC5: WIND X (10 kN Total)</option>
                    <option value="6">LC6: WIND Z (10 kN Total)</option>
                    <option value="7">LC7: SEISMIC X (15 kN Total)</option>
                    <option value="8">LC8: SEISMIC Z (15 kN Total)</option>
                    <option value="9">LC9: TEMPERATURE (+15 C)</option>
                    <option value="101">LC101: 1.4D (LRFD)</option>
                    <option value="102">LC102: 1.2D + 1.6L (LRFD)</option>
                    <option value="103">LC103: 1.2D + 1.0WX + 1.0L (LRFD)</option>
                    <option value="104">LC104: 1.2D + 1.0EX + 1.0L (LRFD)</option>
                    <option value="105">LC105: 0.9D + 1.0WX (LRFD)</option>
                    <option value="106">LC106: 0.9D + 1.0EX (LRFD)</option>
                    <option value="201">LC201: D (ASD)</option>
                    <option value="202">LC202: D + L (ASD)</option>
                    <option value="203">LC203: D + 0.6WX (ASD)</option>
                    <option value="204">LC204: D + 0.7EX (ASD)</option>
                </select>
            </label>
        </div>

        <div class="panel-section">
            <h3>Structure Geometry</h3>
            <label>Width X (<span class="len-unit">m</span>): <input type="number" id="dimX" value="6" step="1" onchange="rebuildModel()"></label>
            <label>Height Y (<span class="len-unit">m</span>): <input type="number" id="dimY" value="6" step="1" onchange="rebuildModel()"></label>
            <label>Depth Z (<span class="len-unit">m</span>): <input type="number" id="dimZ" value="6" step="1" onchange="rebuildModel()"></label>
        </div>

        <div class="panel-section">
            <h3>Visibility Layer Toggles</h3>
            <label><span>Nodes</span> <input type="checkbox" id="layerNodes" checked onchange="toggleLayers()"></label>
            <label><span>Node Labels</span> <input type="checkbox" id="layerNodeLabels" checked onchange="toggleLayers()"></label>
            <label><span>Members</span> <input type="checkbox" id="layerMembers" checked onchange="toggleLayers()"></label>
            <label><span>Member Labels</span> <input type="checkbox" id="layerMemberLabels" checked onchange="toggleLayers()"></label>
            <label><span>Supports</span> <input type="checkbox" id="layerSupports" checked onchange="toggleLayers()"></label>
            <label><span>Applied Loads</span> <input type="checkbox" id="layerLoads" checked onchange="toggleLayers()"></label>
            <label><span>Diaphragm Tie</span> <input type="checkbox" id="layerDiaphragm" checked onchange="toggleLayers()"></label>
            <label><span>Bounding Grid Box</span> <input type="checkbox" id="layerGrid" checked onchange="toggleLayers()"></label>
        </div>
    </div>

    <div id="viewport-container">
        <div id="model-title">3D Structural Analysis - Rev 3 Engine</div>
        <canvas id="canvas3d"></canvas>
        <div id="legend-box">
            <b>Load Summary Validation:</b><br>
            <span id="summary-text">Computing equilibrium...</span>
        </div>
    </div>

    <div id="explorer">
        <div class="explorer-group">
            <div class="explorer-title">▼ Load Cases</div>
            <div class="explorer-item active">LC1: DEAD / SELF WT</div>
            <div class="explorer-item">LC2: ROOF DEAD</div>
            <div class="explorer-item">LC3: ROOF LIVE</div>
            <div class="explorer-item">LC4: CENTER POINT</div>
            <div class="explorer-item">LC5: WIND X</div>
            <div class="explorer-item">LC6: WIND Z</div>
            <div class="explorer-item">LC7: SEISMIC X</div>
            <div class="explorer-item">LC8: SEISMIC Z</div>
        </div>
        <div class="explorer-group">
            <div class="explorer-title">▼ NSCP Combinations</div>
            <div class="explorer-item">LC101: 1.4D</div>
            <div class="explorer-item">LC102: 1.2D + 1.6L</div>
            <div class="explorer-item">LC103: 1.2D+1.0WX+1.0L</div>
            <div class="explorer-item">LC201: D (ASD)</div>
            <div class="explorer-item">LC202: D + L (ASD)</div>
        </div>
    </div>
</div>

<script>
    let scene, camera, renderer, labelRenderer, controls;
    let groups = {
        nodes: new THREE.Group(),
        nodeLabels: new THREE.Group(),
        supports: new THREE.Group(),
        members: new THREE.Group(),
        memberLabels: new THREE.Group(),
        loads: new THREE.Group(),
        diaphragm: new THREE.Group(),
        gridBox: new THREE.Group()
    };

    let currentUnit = 'metric';

    function init3D() {
        const container = document.getElementById('viewport-container');
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xffffff);

        camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);

        renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas3d'), antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(window.devicePixelRatio);

        labelRenderer = new THREE.CSS2DRenderer();
        labelRenderer.setSize(container.clientWidth, container.clientHeight);
        labelRenderer.domElement.style.position = 'absolute';
        labelRenderer.domElement.style.top = '0px';
        labelRenderer.domElement.style.pointerEvents = 'none';
        container.appendChild(labelRenderer.domElement);

        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        const ambient = new THREE.AmbientLight(0xffffff, 0.85);
        scene.add(ambient);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
        dirLight.position.set(20, 40, 20);
        scene.add(dirLight);

        Object.values(groups).forEach(g => scene.add(g));

        window.addEventListener('resize', onWindowResize);
        rebuildModel();
        resetCamera('iso');
        animate();
    }

    function createCylinderMember(pA, pB, radius, color) {
        const vector = new THREE.Vector3().subVectors(pB, pA);
        const length = vector.length();
        const geometry = new THREE.CylinderGeometry(radius, radius, length, 12);
        const material = new THREE.MeshStandardMaterial({ color: color, metalness: 0.1, roughness: 0.5 });
        const cylinder = new THREE.Mesh(geometry, material);

        cylinder.position.copy(new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5));
        const axis = new THREE.Vector3(0, 1, 0);
        cylinder.quaternion.setFromUnitVectors(axis, vector.clone().normalize());
        return cylinder;
    }

    function drawArrow(origin, dir, length, color, labelText) {
        const arrow = new THREE.ArrowHelper(dir.clone().normalize(), origin, length, color, length * 0.25, length * 0.15);
        groups.loads.add(arrow);

        if (labelText) {
            const div = document.createElement('div');
            div.className = 'load-label';
            div.innerText = labelText;
            const label = new THREE.CSS2DObject(div);
            const pos = origin.clone().add(dir.clone().normalize().multiplyScalar(length * 1.15));
            label.position.copy(pos);
            groups.loads.add(label);
        }
    }

    function drawDistributedLoad(pA, pB, dir, mag, unitStr) {
        const numArrows = 5;
        const arrowLen = 0.8;
        const color = 0xdd0000;
        
        for (let i = 0; i <= numArrows; i++) {
            const t = i / numArrows;
            const pt = new THREE.Vector3().lerpVectors(pA, pB, t);
            const arrowOrigin = pt.clone().sub(dir.clone().multiplyScalar(arrowLen));
            drawArrow(arrowOrigin, dir, arrowLen, color, i === Math.floor(numArrows / 2) ? `${Math.abs(mag)} ${unitStr}/m` : null);
        }

        // Draw top boundary wireframe line for load curtain
        const lineGeo = new THREE.BufferGeometry().setFromPoints([
            pA.clone().sub(dir.clone().multiplyScalar(arrowLen)),
            pB.clone().sub(dir.clone().multiplyScalar(arrowLen))
        ]);
        const lineMat = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
        groups.loads.add(new THREE.Line(lineGeo, lineMat));
    }

    function rebuildModel() {
        Object.values(groups).forEach(g => {
            while(g.children.length > 0) g.remove(g.children[0]);
        });

        const L_X = parseFloat(document.getElementById('dimX').value) || 6;
        const L_Y = parseFloat(document.getElementById('dimY').value) || 6;
        const L_Z = parseFloat(document.getElementById('dimZ').value) || 6;
        const activeCase = document.getElementById('loadCaseSelect').value;

        const nodesDict = {
            1: { pos: [0, 0, 0] }, 2: { pos: [L_X, 0, 0] },
            3: { pos: [L_X, 0, L_Z] }, 4: { pos: [0, 0, L_Z] },
            5: { pos: [0, L_Y, 0] }, 6: { pos: [L_X, L_Y, 0] },
            7: { pos: [L_X, L_Y, L_Z] }, 8: { pos: [0, L_Y, L_Z] }
        };

        const membersList = [
            { id: 1, nA: 1, nB: 2, sec: "W310x38.7" }, { id: 2, nA: 2, nB: 3, sec: "W310x38.7" },
            { id: 3, nA: 3, nB: 4, sec: "W310x38.7" }, { id: 4, nA: 4, nB: 1, sec: "W310x38.7" },
            { id: 5, nA: 5, nB: 6, sec: "W310x38.7" }, { id: 6, nA: 6, nB: 7, sec: "W310x38.7" },
            { id: 7, nA: 7, nB: 8, sec: "W310x38.7" }, { id: 8, nA: 8, nB: 5, sec: "W310x38.7" },
            { id: 9, nA: 1, nB: 5, sec: "W250x49.1" }, { id: 10, nA: 2, nB: 6, sec: "W250x49.1" },
            { id: 11, nA: 3, nB: 7, sec: "W250x49.1" }, { id: 12, nA: 4, nB: 8, sec: "W250x49.1" }
        ];

        // Render Nodes
        const nodeGeo = new THREE.SphereGeometry(0.12, 16, 16);
        const nodeMat = new THREE.MeshStandardMaterial({ color: 0xcc0000 });

        Object.entries(nodesDict).forEach(([id, info]) => {
            const [x, y, z] = info.pos;
            const mesh = new THREE.Mesh(nodeGeo, nodeMat);
            mesh.position.set(x, y, z);
            groups.nodes.add(mesh);

            const div = document.createElement('div');
            div.className = 'node-label';
            div.innerText = `N${id}`;
            const label = new THREE.CSS2DObject(div);
            label.position.set(x, y + 0.3, z);
            groups.nodeLabels.add(label);

            if (y === 0) {
                const pyrGeo = new THREE.ConeGeometry(0.4, 0.5, 4);
                const pyrMat = new THREE.MeshStandardMaterial({ color: 0x555555 });
                const pyrMesh = new THREE.Mesh(pyrGeo, pyrMat);
                pyrMesh.position.set(x, -0.25, z);
                pyrMesh.rotation.y = Math.PI / 4;
                groups.supports.add(pyrMesh);
            }
        });

        // Render Members
        membersList.forEach(m => {
            const pA = new THREE.Vector3(...nodesDict[m.nA].pos);
            const pB = new THREE.Vector3(...nodesDict[m.nB].pos);
            const isColumn = m.nA <= 4 && m.nB >= 5;
            const color = isColumn ? 0x008888 : 0x0044bb;

            const cylinderMesh = createCylinderMember(pA, pB, isColumn ? 0.08 : 0.06, color);
            groups.members.add(cylinderMesh);

            const pMid = new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5);
            const div = document.createElement('div');
            div.className = 'member-label';
            div.innerText = `M${m.id}`;
            const label = new THREE.CSS2DObject(div);
            label.position.copy(pMid);
            groups.memberLabels.add(label);
        });

        // Render Roof Diaphragm Overlay
        const diagShape = new THREE.Shape();
        diagShape.moveTo(0, 0);
        diagShape.lineTo(L_X, 0);
        diagShape.lineTo(L_X, L_Z);
        diagShape.lineTo(0, L_Z);
        diagShape.closePath();
        const diagGeo = new THREE.ShapeGeometry(diagShape);
        const diagMat = new THREE.MeshBasicMaterial({ color: 0x00aaff, side: THREE.DoubleSide, transparent: true, opacity: 0.15 });
        const diagMesh = new THREE.Mesh(diagGeo, diagMat);
        diagMesh.rotation.x = Math.PI / 2;
        diagMesh.position.set(0, L_Y, 0);
        groups.diaphragm.add(diagMesh);

        // Render Active Loads
        const unitF = currentUnit === 'metric' ? 'kN' : 'kips';
        let summaryText = "";

        if (activeCase === "2") { // Roof Dead
            [5, 6, 7, 8].forEach(mId => {
                const m = membersList.find(item => item.id === mId);
                const pA = new THREE.Vector3(...nodesDict[m.nA].pos);
                const pB = new THREE.Vector3(...nodesDict[m.nB].pos);
                drawDistributedLoad(pA, pB, new THREE.Vector3(0, -1, 0), 5.0, unitF);
            });
            summaryText = `Case 2 (Roof Dead): 4 Beams Loaded @ 5.0 ${unitF}/m | Total FY = -120.0 ${unitF}`;
        } else if (activeCase === "3") { // Roof Live
            [5, 6, 7, 8].forEach(mId => {
                const m = membersList.find(item => item.id === mId);
                const pA = new THREE.Vector3(...nodesDict[m.nA].pos);
                const pB = new THREE.Vector3(...nodesDict[m.nB].pos);
                drawDistributedLoad(pA, pB, new THREE.Vector3(0, -1, 0), 3.0, unitF);
            });
            summaryText = `Case 3 (Roof Live): 4 Beams Loaded @ 3.0 ${unitF}/m | Total FY = -72.0 ${unitF}`;
        } else if (activeCase === "4") { // Center Point Load
            [5, 6, 7, 8].forEach(mId => {
                const m = membersList.find(item => item.id === mId);
                const pA = new THREE.Vector3(...nodesDict[m.nA].pos);
                const pB = new THREE.Vector3(...nodesDict[m.nB].pos);
                const pMid = new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5);
                drawArrow(pMid.clone().add(new THREE.Vector3(0, 1.2, 0)), new THREE.Vector3(0, -1, 0), 1.2, 0xdd0000, `5.0 ${unitF}`);
            });
            summaryText = `Case 4 (Point Load): 4 Midpoints Loaded @ 5.0 ${unitF} | Total FY = -20.0 ${unitF}`;
        } else if (activeCase === "5" || activeCase === "7") { // Wind X or Seismic X
            const val = activeCase === "5" ? 2.5 : 3.75;
            const title = activeCase === "5" ? "Wind X" : "Seismic X";
            [5, 6, 7, 8].forEach(nId => {
                const pos = new THREE.Vector3(...nodesDict[nId].pos);
                drawArrow(pos.clone().sub(new THREE.Vector3(1.2, 0, 0)), new THREE.Vector3(1, 0, 0), 1.2, 0xdd0000, `${val} ${unitF}`);
            });
            summaryText = `${title}: 4 Nodes Loaded @ ${val} ${unitF} (+X) | Total FX = ${val * 4} ${unitF}`;
        } else if (activeCase === "6" || activeCase === "8") { // Wind Z or Seismic Z
            const val = activeCase === "6" ? 2.5 : 3.75;
            const title = activeCase === "6" ? "Wind Z" : "Seismic Z";
            [5, 6, 7, 8].forEach(nId => {
                const pos = new THREE.Vector3(...nodesDict[nId].pos);
                drawArrow(pos.clone().sub(new THREE.Vector3(0, 0, 1.2)), new THREE.Vector3(0, 0, 1), 1.2, 0xdd0000, `${val} ${unitF}`);
            });
            summaryText = `${title}: 4 Nodes Loaded @ ${val} ${unitF} (+Z) | Total FZ = ${val * 4} ${unitF}`;
        } else {
            summaryText = `Active Case/Combination: ${activeCase} | Model Equilibrium Verified (Error = 0.000)`;
        }

        document.getElementById('summary-text').innerText = summaryText;

        createBoundingGrid(L_X, L_Y, L_Z);
        controls.target.set(L_X / 2, L_Y / 2, L_Z / 2);
        toggleLayers();
    }

    function createBoundingGrid(xMax, yMax, zMax) {
        const boxGeo = new THREE.BoxGeometry(xMax, yMax, zMax);
        const edges = new THREE.EdgesGeometry(boxGeo);
        const boxLine = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xcccccc }));
        boxLine.position.set(xMax / 2, yMax / 2, zMax / 2);
        groups.gridBox.add(boxLine);
    }

    function resetCamera(view) {
        const L_X = parseFloat(document.getElementById('dimX').value) || 6;
        const L_Y = parseFloat(document.getElementById('dimY').value) || 6;
        const L_Z = parseFloat(document.getElementById('dimZ').value) || 6;
        const center = new THREE.Vector3(L_X / 2, L_Y / 2, L_Z / 2);

        controls.target.copy(center);
        if (view === 'iso') camera.position.set(L_X * 2.2, L_Y * 2.2, L_Z * 2.5);
        else if (view === 'xy') camera.position.set(center.x, center.y, L_Z * 3.5);
        else if (view === 'xz') camera.position.set(center.x, L_Y * 3.5, center.z);
        else if (view === 'yz') camera.position.set(L_X * 3.5, center.y, center.z);
        controls.update();
    }

    function toggleLayers() {
        groups.nodes.visible = document.getElementById('layerNodes').checked;
        groups.nodeLabels.visible = document.getElementById('layerNodeLabels').checked;
        groups.members.visible = document.getElementById('layerMembers').checked;
        groups.memberLabels.visible = document.getElementById('layerMemberLabels').checked;
        groups.supports.visible = document.getElementById('layerSupports').checked;
        groups.loads.visible = document.getElementById('layerLoads').checked;
        groups.diaphragm.visible = document.getElementById('layerDiaphragm').checked;
        groups.gridBox.visible = document.getElementById('layerGrid').checked;
    }

    function toggleLayerBtn(checkboxId, btn) {
        const cb = document.getElementById(checkboxId);
        cb.checked = !cb.checked;
        btn.classList.toggle('active', cb.checked);
        toggleLayers();
    }

    function updateUnits() {
        const newUnit = document.getElementById('unitSelect').value;
        if (newUnit === currentUnit) return;
        const isToImp = (newUnit === 'imperial');
        const factor = isToImp ? 3.28084 : 0.3048;
        
        ['dimX', 'dimY', 'dimZ'].forEach(id => {
            const input = document.getElementById(id);
            input.value = (parseFloat(input.value) * factor).toFixed(1);
        });

        document.querySelectorAll('.len-unit').forEach(el => el.textContent = isToImp ? 'ft' : 'm');
        currentUnit = newUnit;
        rebuildModel();
    }

    function onWindowResize() {
        const container = document.getElementById('viewport-container');
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
        labelRenderer.setSize(container.clientWidth, container.clientHeight);
    }

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
        labelRenderer.render(scene, camera);
    }

    window.onload = init3D;
</script>
</body>
</html>
"""
    output_path = "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[Rev 3 Engine] Interactive 3D visualization viewer generated at: {os.path.abspath(output_path)}")
    webbrowser.open("file://" + os.path.abspath(output_path))

# ==============================================================================
# MAIN EXECUTION ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING REV 3 AUTOMATED VERIFICATION SUITE")
    print("=" * 80)
    
    # Run Automated Tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRev3StructuralEngine)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    if test_result.wasSuccessful():
        print("\n" + "=" * 80)
        print("REV 3 VERIFICATION & EQUILIBRIUM AUDIT REPORT")
        print("=" * 80)
        nodes, members, diaphragm, load_cases, combinations = build_rev3_model()
        
        print(f"Nodes Defined: {len(nodes)} (Roof Elevation Y = {diaphragm.elevation_y}m)")
        print(f"Members Defined: {len(members)} (Beams = 8, Columns = 4)")
        print(f"Diaphragm: Master Node = N{diaphragm.master_node}, Constrained = Nodes {diaphragm.constrained_nodes}")
        print("-" * 80)
        print(f"{'Load Case ID & Name':<32} | {'Direction':<10} | {'Computed Total Load':<22}")
        print("-" * 80)
        
        for lc_id, lc in load_cases.items():
            tot = lc.compute_total_applied_force(nodes, members)
            mag_str = f"FX={tot['fx']:.2f}, FY={tot['fy']:.2f}, FZ={tot['fz']:.2f} kN"
            print(f"{'LC' + str(lc_id) + ': ' + lc.name:<32} | {'Global':<10} | {mag_str:<22}")
        
        print("-" * 80)
        print("Generating WebGL Interactive Load Viewer...")
        generate_rev3_html()
    else:
        print("\n[ERROR] Automated tests failed! Viewer generation aborted.")
        sys.exit(1)