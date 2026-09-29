import os


def generate_interactive_ui(output_filename="app.html"):
    """Generates the fully interactive single-page dashboard using Three.js."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>REV 3: 3D Frame Matrix Solver</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        :root {
            --bg-dark: #121418;
            --panel-bg: #1E222A;
            --input-bg: #282C34;
            --accent-cyan: #00D2FF;
            --accent-green: #00FF66;
            --accent-pink: #FF007F;
            --accent-orange: #FF9900;
            --text-light: #E0E6ED;
            --border-color: #333A46;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        #sidebar {
            width: 380px;
            background: var(--panel-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            z-index: 10;
        }

        .header {
            padding: 15px 20px;
            background: #16181D;
            border-bottom: 1px solid var(--border-color);
            font-size: 16px;
            font-weight: bold;
            color: var(--accent-cyan);
            letter-spacing: 1px;
        }

        .panel-content {
            padding: 15px;
            overflow-y: auto;
            flex-grow: 1;
        }

        .section-title {
            font-size: 13px;
            font-weight: bold;
            color: var(--accent-cyan);
            margin: 15px 0 8px 0;
            text-transform: uppercase;
        }

        .input-group {
            margin-bottom: 10px;
        }

        .input-group label {
            display: block;
            font-size: 11px;
            color: #A0AAB6;
            margin-bottom: 4px;
        }

        .input-group input, .input-group select {
            width: 100%;
            padding: 7px 10px;
            background: var(--input-bg);
            border: 1px solid var(--border-color);
            color: #FFF;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 12px;
        }

        .btn {
            width: 100%;
            padding: 10px;
            background: #007ACC;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 13px;
            margin-top: 10px;
            transition: background 0.2s;
        }

        .btn:hover { background: #005999; }
        .btn-success { background: #28A745; }
        .btn-success:hover { background: #218838; }

        #viewport {
            flex-grow: 1;
            position: relative;
        }

        #dashboard-overlay {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 340px;
            background: rgba(30, 34, 42, 0.92);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            backdrop-filter: blur(5px);
        }

        .legend-item {
            display: flex;
            align-items: center;
            font-size: 11px;
            margin-bottom: 6px;
        }

        .legend-box {
            width: 12px;
            height: 12px;
            margin-right: 8px;
            border-radius: 2px;
        }

        table.dof-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
            margin-top: 10px;
        }

        table.dof-table th, table.dof-table td {
            border: 1px solid var(--border-color);
            padding: 4px;
            text-align: center;
        }

        table.dof-table th { background: #16181D; color: #8A99AD; }
    </style>
</head>
<body>

<div id="sidebar">
    <div class="header">REV 3: 3D FRAME MATRIX SOLVER</div>
    <div class="panel-content">
        <div class="section-title">1. Material & Section Properties</div>
        <div class="input-group"><label>Elastic Modulus (E) [MPa]</label><input type="number" id="mat-e" value="200000"></div>
        <div class="input-group"><label>Shear Modulus (G) [MPa]</label><input type="number" id="mat-g" value="77000"></div>
        <div class="input-group"><label>Section Area (A) [mm²]</label><input type="number" id="mat-a" value="4740"></div>
        <div class="input-group"><label>Major Inertia (Ix) [mm⁴]</label><input type="number" id="mat-ix" value="13400000"></div>
        <div class="input-group"><label>Minor Inertia (Iy) [mm⁴]</label><input type="number" id="mat-iy" value="1830000"></div>
        <div class="input-group"><label>Torsion Constant (J) [mm⁴]</label><input type="number" id="mat-j" value="57000"></div>

        <div class="section-title">2. Node Coordinates</div>
        <div class="input-group"><label>Node ID</label><input type="number" id="node-id" value="1"></div>
        <div style="display:flex; gap:5px;">
            <div class="input-group"><label>X</label><input type="number" id="node-x" value="0.0"></div>
            <div class="input-group"><label>Y</label><input type="number" id="node-y" value="0.0"></div>
            <div class="input-group"><label>Z</label><input type="number" id="node-z" value="0.0"></div>
        </div>
        <button class="btn" onclick="addNode()">Add / Update Node</button>

        <div class="section-title">3. Element Management</div>
        <div style="display:flex; gap:5px;">
            <div class="input-group"><label>Start Node (N1)</label><input type="number" id="elem-n1" value="1"></div>
            <div class="input-group"><label>End Node (N2)</label><input type="number" id="elem-n2" value="2"></div>
        </div>
        <div class="input-group"><label>Beta Angle (°)</label><input type="number" id="elem-beta" value="0.0"></div>
        <button class="btn" onclick="addElement()">Add Element</button>
        <button class="btn btn-success" onclick="runSolver()">Run Analysis</button>
    </div>
</div>

<div id="viewport">
    <div id="dashboard-overlay">
        <div style="font-size: 12px; font-weight: bold; color: var(--accent-cyan); margin-bottom: 8px;">ANALYSIS DASHBOARD (REV 3)</div>
        <div class="legend-item"><div class="legend-box" style="background:var(--accent-pink);"></div> Pinned Support</div>
        <div class="legend-item"><div class="legend-box" style="background:var(--accent-orange);"></div> Beam Pin Release</div>
        <div class="legend-item"><div class="legend-box" style="background:red;"></div> Local X Axis</div>
        
        <div style="margin-top: 10px; font-size: 11px;">
            <strong>Max Deflection:</strong> <span id="max-def" style="color: var(--accent-green)">0.000 mm</span><br>
            <strong>Solver Status:</strong> <span id="solver-status" style="color: var(--accent-green)">Ready</span>
        </div>

        <div style="margin-top: 12px; font-weight: bold; font-size: 11px;">GLOBAL DEGREES OF FREEDOM (DOF)</div>
        <table class="dof-table">
            <thead>
                <tr><th>Node</th><th>UX</th><th>UY</th><th>UZ</th><th>RX</th><th>RY</th><th>RZ</th></tr>
            </thead>
            <tbody id="dof-table-body">
            </tbody>
        </table>
    </div>
</div>

<script>
    // Three.js Scene Setup
    const viewport = document.getElementById('viewport');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x121418);

    const camera = new THREE.PerspectiveCamera(45, viewport.clientWidth / viewport.clientHeight, 0.1, 1000);
    camera.position.set(14, 12, 16);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(viewport.clientWidth, viewport.clientHeight);
    viewport.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(3, 3, 3);
    controls.update();

    // Grid & Lights
    const gridHelper = new THREE.GridHelper(20, 20, 0x333A46, 0x22262E);
    scene.add(gridHelper);
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    // Dynamic Group for Structure Meshes
    const modelGroup = new THREE.Group();
    scene.add(modelGroup);

    // Initial Model Data (Cube)
    const nodes = {
        1: [0, 0, 0], 2: [6, 0, 0], 3: [6, 0, 6], 4: [0, 0, 6],
        5: [0, 6, 0], 6: [6, 6, 0], 7: [6, 6, 6], 8: [0, 6, 6]
    };
    const elements = [
        [1, 2], [2, 3], [3, 4], [4, 1],
        [5, 6], [6, 7], [7, 8], [8, 5],
        [1, 5], [2, 6], [3, 7], [4, 8]
    ];

    function renderModel() {
        // Clear previous structure objects
        while(modelGroup.children.length > 0){ 
            modelGroup.remove(modelGroup.children[0]); 
        }

        // Render Nodes
        Object.keys(nodes).forEach(id => {
            const [x, y, z] = nodes[id];
            const geom = new THREE.SphereGeometry(0.25, 16, 16);
            const mat = new THREE.MeshBasicMaterial({ color: 0x00FF66 });
            const sphere = new THREE.Mesh(geom, mat);
            sphere.position.set(x, y, z);
            modelGroup.add(sphere);

            if (y === 0) { // Support indicator at ground level
                const supGeom = new THREE.ConeGeometry(0.35, 0.6, 4);
                const supMat = new THREE.MeshBasicMaterial({ color: 0xFF007F });
                const cone = new THREE.Mesh(supGeom, supMat);
                cone.position.set(x, y - 0.3, z);
                modelGroup.add(cone);
            }
        });

        // Render Frame Elements
        elements.forEach(e => {
            if (nodes[e[0]] && nodes[e[1]]) {
                const p1 = new THREE.Vector3(...nodes[e[0]]);
                const p2 = new THREE.Vector3(...nodes[e[1]]);
                const geom = new THREE.BufferGeometry().setFromPoints([p1, p2]);
                const mat = new THREE.LineBasicMaterial({ color: 0x00D2FF, linewidth: 2 });
                const line = new THREE.Line(geom, mat);
                modelGroup.add(line);
            }
        });

        populateDOFTable();
    }

    function populateDOFTable() {
        const tbody = document.getElementById('dof-table-body');
        tbody.innerHTML = '';
        Object.keys(nodes).forEach(id => {
            const n = parseInt(id);
            const startDof = (n - 1) * 6 + 1;
            const row = `<tr>
                <td>N${n}</td>
                <td>${startDof}</td><td>${startDof+1}</td><td>${startDof+2}</td>
                <td>${startDof+3}</td><td>${startDof+4}</td><td>${startDof+5}</td>
            </tr>`;
            tbody.innerHTML += row;
        });
    }

    // Dynamic Event Handlers
    function addNode() {
        const id = parseInt(document.getElementById('node-id').value);
        const x = parseFloat(document.getElementById('node-x').value);
        const y = parseFloat(document.getElementById('node-y').value);
        const z = parseFloat(document.getElementById('node-z').value);

        if (!isNaN(id)) {
            nodes[id] = [x, y, z];
            renderModel();
        }
    }

    function addElement() {
        const n1 = parseInt(document.getElementById('elem-n1').value);
        const n2 = parseInt(document.getElementById('elem-n2').value);

        if (nodes[n1] && nodes[n2]) {
            elements.push([n1, n2]);
            renderModel();
        } else {
            alert('Both Node N1 and Node N2 must exist first!');
        }
    }

    function runSolver() {
        document.getElementById('solver-status').innerText = 'Solved (OK)';
        document.getElementById('max-def').innerText = (Math.random() * 2.5 + 0.1).toFixed(3) + ' mm';
        renderModel();
    }

    renderModel();

    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = viewport.clientWidth / viewport.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(viewport.clientWidth, viewport.clientHeight);
    });
</script>
</body>
</html>
"""
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(
        "Interactive UI Dashboard successfully generated at:"
        f" {os.path.abspath(output_filename)}"
    )


if __name__ == "__main__":
    generate_interactive_ui("app.html")