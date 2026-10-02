import os
import webbrowser

html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Structural Frame Solver & Viewer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { display: flex; flex-direction: column; height: 100vh; background: #f0f0f0; color: #333; overflow: hidden; font-size: 12px; }
        
        /* Top Ribbon / Toolbar */
        #top-ribbon { background: #e8e8ec; border-bottom: 1px solid #ccc; padding: 4px 10px; display: flex; flex-direction: column; gap: 4px; z-index: 20; }
        .ribbon-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .ribbon-btn { background: #fff; border: 1px solid #ababab; padding: 3px 8px; border-radius: 3px; cursor: pointer; font-size: 11px; display: flex; align-items: center; gap: 4px; }
        .ribbon-btn:hover { background: #e0e0e0; }
        .ribbon-btn.active { background: #cce8ff; border-color: #3399ff; }
        .ribbon-divider { width: 1px; height: 18px; background: #ccc; margin: 0 4px; }

        /* Main Workspace Layout */
        #workspace { display: flex; flex: 1; height: calc(100vh - 65px); position: relative; }
        
        /* Left Sidebar: Controls */
        #sidebar { width: 280px; background: #f8f9fa; border-right: 1px solid #ccc; display: flex; flex-direction: column; padding: 10px; gap: 10px; overflow-y: auto; z-index: 10; }
        .panel-section { background: #fff; border: 1px solid #dcdcdc; padding: 8px; border-radius: 4px; }
        h3 { color: #005a9e; font-size: 0.85rem; border-bottom: 1px solid #eee; padding-bottom: 3px; margin-bottom: 6px; }
        label { display: flex; justify-content: space-between; align-items: center; margin: 4px 0; font-size: 0.8rem; }
        select, input[type="number"], input[type="range"] { background: #fff; color: #333; border: 1px solid #ccc; padding: 2px 5px; border-radius: 3px; width: 90px; }
        input[type="range"] { padding: 0; cursor: pointer; }

        /* Viewport Container */
        #viewport-container { flex: 1; position: relative; background: #ffffff; }
        #canvas3d { width: 100%; height: 100%; display: block; }
        
        /* Right Sidebar: Data Entry & Explorer */
        #explorer { width: 220px; background: #f8f9fa; border-left: 1px solid #ccc; padding: 10px; font-size: 11px; overflow-y: auto; }
        .explorer-group { margin-bottom: 12px; }
        .explorer-title { font-weight: bold; color: #005a9e; margin-bottom: 4px; display: flex; justify-content: space-between; cursor: pointer; }
        .explorer-item { padding: 2px 8px; color: #555; cursor: pointer; }
        .explorer-item:hover { background: #e6f2ff; color: #000; }
        .explorer-item.active { background: #cce8ff; font-weight: bold; }

        /* 2D HTML Labels on 3D Canvas */
        .node-label { color: #000; font-weight: bold; font-size: 10px; text-shadow: 1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff; pointer-events: none; }
        .member-label { color: #0000aa; font-weight: 600; font-size: 9px; text-shadow: 1px 1px 0 #fff, -1px -1px 0 #fff; pointer-events: none; }
        .axis-label { color: #333; font-weight: bold; font-size: 11px; }

        /* Title Overlay */
        #model-title { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); font-weight: bold; font-size: 14px; background: rgba(255,255,255,0.8); padding: 4px 12px; border-radius: 4px; border: 1px solid #ccc; pointer-events: none; }
    </style>
    
    <!-- Three.js, OrbitControls & CSS2DRenderer -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/renderers/CSS2DRenderer.js"></script>
</head>
<body>

<!-- Top Ribbon Toolbar -->
<div id="top-ribbon">
    <div class="ribbon-row">
        <button class="ribbon-btn" onclick="resetCamera('iso')"><b>ISO</b></button>
        <button class="ribbon-btn" onclick="resetCamera('xy')">XY</button>
        <button class="ribbon-btn" onclick="resetCamera('xz')">XZ</button>
        <button class="ribbon-btn" onclick="resetCamera('yz')">YZ</button>
        <div class="ribbon-divider"></div>
        <button class="ribbon-btn active" id="btn-members" onclick="toggleLayerBtn('layerMembers', this)">Members</button>
        <button class="ribbon-btn active" id="btn-m-labels" onclick="toggleLayerBtn('layerMemberLabels', this)">Member labels</button>
        <button class="ribbon-btn active" id="btn-nodes" onclick="toggleLayerBtn('layerNodes', this)">Nodes</button>
        <button class="ribbon-btn active" id="btn-n-labels" onclick="toggleLayerBtn('layerNodeLabels', this)">Node labels</button>
        <button class="ribbon-btn active" id="btn-supports" onclick="toggleLayerBtn('layerSupports', this)">Supports</button>
        <button class="ribbon-btn active" id="btn-axes" onclick="toggleLayerBtn('layerLocalAxes', this)">Local axes</button>
        <button class="ribbon-btn active" id="btn-grid" onclick="toggleLayerBtn('layerGrid', this)">Grid Box</button>
    </div>
</div>

<div id="workspace">
    <!-- Left Sidebar: Controls -->
    <div id="sidebar">
        <div class="panel-section">
            <h3>Unit System</h3>
            <label>
                Units:
                <select id="unitSelect" onchange="updateUnits()">
                    <option value="metric">Metric (m, kN)</option>
                    <option value="imperial">Imperial (ft, kips)</option>
                </select>
            </label>
        </div>

        <div class="panel-section">
            <h3>Structure Dimensions</h3>
            <label>Width X (<span class="len-unit">m</span>): <input type="number" id="dimX" value="6" step="1" onchange="rebuildModel()"></label>
            <label>Height Y (<span class="len-unit">m</span>): <input type="number" id="dimY" value="6" step="1" onchange="rebuildModel()"></label>
            <label>Depth Z (<span class="len-unit">m</span>): <input type="number" id="dimZ" value="6" step="1" onchange="rebuildModel()"></label>
            <label>Column Beta (°): <input type="number" id="betaAngle" value="90" step="15" onchange="rebuildModel()"></label>
        </div>

        <!-- NEW: Member Thickness Controls -->
        <div class="panel-section">
            <h3>Member Thickness (Cross-Section)</h3>
            <label>Column Thick: <input type="range" id="colThickness" min="0.02" max="0.30" step="0.01" value="0.10" oninput="rebuildModel()"></label>
            <label>Beam Thick: <input type="range" id="beamThickness" min="0.02" max="0.30" step="0.01" value="0.08" oninput="rebuildModel()"></label>
        </div>

        <div class="panel-section">
            <h3>Visibility Toggles</h3>
            <label><span>Nodes</span> <input type="checkbox" id="layerNodes" checked onchange="toggleLayers()"></label>
            <label><span>Node Labels</span> <input type="checkbox" id="layerNodeLabels" checked onchange="toggleLayers()"></label>
            <label><span>Members</span> <input type="checkbox" id="layerMembers" checked onchange="toggleLayers()"></label>
            <label><span>Member Labels</span> <input type="checkbox" id="layerMemberLabels" checked onchange="toggleLayers()"></label>
            <label><span>Supports</span> <input type="checkbox" id="layerSupports" checked onchange="toggleLayers()"></label>
            <label><span>Local Axes</span> <input type="checkbox" id="layerLocalAxes" checked onchange="toggleLayers()"></label>
            <label><span>Bounding Grid Box</span> <input type="checkbox" id="layerGrid" checked onchange="toggleLayers()"></label>
        </div>
    </div>

    <!-- 3D Viewport -->
    <div id="viewport-container">
        <div id="model-title">Structural model - cube_nodes_6m_rev2.xlsx</div>
        <canvas id="canvas3d"></canvas>
    </div>

    <!-- Right Sidebar: Explorer Menu -->
    <div id="explorer">
        <div class="explorer-group">
            <div class="explorer-title">▼ Data Entry</div>
            <div class="explorer-item">Project Grid</div>
            <div class="explorer-item">Materials</div>
            <div class="explorer-item">Section Sets</div>
            <div class="explorer-item active">Node Coordinates</div>
            <div class="explorer-item">Boundary Conditions</div>
            <div class="explorer-item">Members</div>
        </div>
        <div class="explorer-group">
            <div class="explorer-title">▼ Results | Env | Batch</div>
            <div class="explorer-item">Node Reactions</div>
            <div class="explorer-item">Node Deflections</div>
            <div class="explorer-item">Member Forces</div>
            <div class="explorer-item">Member Stresses</div>
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
        localAxes: new THREE.Group(),
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

        const ambient = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambient);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
        dirLight.position.set(20, 40, 20);
        scene.add(dirLight);

        Object.values(groups).forEach(g => scene.add(g));

        window.addEventListener('resize', onWindowResize);
        rebuildModel();
        resetCamera('iso');
        animate();
    }

    function createCylinderMember(pA, pB, radius, color, betaDeg) {
        const vector = new THREE.Vector3().subVectors(pB, pA);
        const length = vector.length();

        const geometry = new THREE.CylinderGeometry(radius, radius, length, 12);
        const material = new THREE.MeshStandardMaterial({ color: color, metalness: 0.2, roughness: 0.4 });
        const cylinder = new THREE.Mesh(geometry, material);

        // Position cylinder at mid-point
        const pMid = new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5);
        cylinder.position.copy(pMid);

        // Align cylinder axis with vector direction
        const axis = new THREE.Vector3(0, 1, 0);
        const quaternion = new THREE.Quaternion();
        quaternion.setFromUnitVectors(axis, vector.clone().normalize());
        cylinder.quaternion.copy(quaternion);

        // Apply Beta angle rotation around the local long axis if specified
        if (betaDeg) {
            cylinder.rotateOnAxis(axis, THREE.MathUtils.degToRad(betaDeg));
        }

        return cylinder;
    }

    function rebuildModel() {
        Object.values(groups).forEach(g => {
            while(g.children.length > 0) g.remove(g.children[0]);
        });

        const L_X = parseFloat(document.getElementById('dimX').value) || 6;
        const L_Y = parseFloat(document.getElementById('dimY').value) || 6;
        const L_Z = parseFloat(document.getElementById('dimZ').value) || 6;
        const beta = parseFloat(document.getElementById('betaAngle').value) || 0;

        const rCol = parseFloat(document.getElementById('colThickness').value) || 0.10;
        const rBeam = parseFloat(document.getElementById('beamThickness').value) || 0.08;

        const nodesDict = {
            1: { pos: [0, 0, 0], dof: "1-6" },
            2: { pos: [L_X, 0, 0], dof: "7-12" },
            3: { pos: [L_X, 0, L_Z], dof: "13-18" },
            4: { pos: [0, 0, L_Z], dof: "19-24" },
            5: { pos: [0, L_Y, 0], dof: "25-30" },
            6: { pos: [L_X, L_Y, 0], dof: "31-36" },
            7: { pos: [L_X, L_Y, L_Z], dof: "37-42" },
            8: { pos: [0, L_Y, L_Z], dof: "43-48" }
        };

        const membersList = [
            { id: 1, nA: 1, nB: 2, sec: "W310x38.7 - A992", pin: "[Mz]" },
            { id: 2, nA: 2, nB: 3, sec: "W310x38.7 - A992", pin: "" },
            { id: 3, nA: 3, nB: 4, sec: "W310x38.7 - A992", pin: "[Mz]" },
            { id: 4, nA: 4, nB: 1, sec: "W310x38.7 - A992", pin: "" },
            { id: 5, nA: 5, nB: 6, sec: "W310x38.7 - A992", pin: "" },
            { id: 6, nA: 6, nB: 7, sec: "W310x38.7 - A992", pin: "" },
            { id: 7, nA: 7, nB: 8, sec: "W310x38.7 - A992", pin: "" },
            { id: 8, nA: 8, nB: 5, sec: "W310x38.7 - A992", pin: "" },
            { id: 9, nA: 1, nB: 5, sec: "W250x49.1 - A992", pin: `(β=${beta}°)` },
            { id: 10, nA: 2, nB: 6, sec: "W250x49.1 - A992", pin: `(β=${beta}°)` },
            { id: 11, nA: 3, nB: 7, sec: "W250x49.1 - A992", pin: `(β=${beta}°)` },
            { id: 12, nA: 4, nB: 8, sec: "W250x49.1 - A992", pin: `(β=${beta}°)` }
        ];

        const nodeGeo = new THREE.SphereGeometry(Math.max(rCol, rBeam) * 1.5, 16, 16);
        const nodeMat = new THREE.MeshStandardMaterial({ color: 0xcc0000 });

        Object.entries(nodesDict).forEach(([id, info]) => {
            const [x, y, z] = info.pos;

            const mesh = new THREE.Mesh(nodeGeo, nodeMat);
            mesh.position.set(x, y, z);
            groups.nodes.add(mesh);

            const div = document.createElement('div');
            div.className = 'node-label';
            div.innerHTML = `N${id}<br>DOF ${info.dof}`;
            const label = new THREE.CSS2DObject(div);
            label.position.set(x, y + 0.35, z);
            groups.nodeLabels.add(label);

            if (y === 0) {
                const suppGroup = new THREE.Group();
                const pyrGeo = new THREE.ConeGeometry(0.45, 0.5, 4);
                const pyrMat = new THREE.MeshStandardMaterial({ color: 0x555555, flatShading: true });
                const pyrMesh = new THREE.Mesh(pyrGeo, pyrMat);
                pyrMesh.position.set(x, -0.25, z);
                pyrMesh.rotation.y = Math.PI / 4;
                suppGroup.add(pyrMesh);

                const plateGeo = new THREE.BoxGeometry(0.6, 0.05, 0.6);
                const plateMat = new THREE.MeshBasicMaterial({ color: 0x333333 });
                const plateMesh = new THREE.Mesh(plateGeo, plateMat);
                plateMesh.position.set(x, -0.5, z);
                suppGroup.add(plateMesh);

                groups.supports.add(suppGroup);
            }
        });

        membersList.forEach(m => {
            const pA = new THREE.Vector3(...nodesDict[m.nA].pos);
            const pB = new THREE.Vector3(...nodesDict[m.nB].pos);
            const isColumn = m.nA <= 4 && m.nB >= 5;
            const color = isColumn ? 0x008888 : 0x0044bb;
            const thickness = isColumn ? rCol : rBeam;

            // Render volumetric 3D cylinders instead of thin 1D lines
            const cylinderMesh = createCylinderMember(pA, pB, thickness, color, isColumn ? beta : 0);
            groups.members.add(cylinderMesh);

            const pMid = new THREE.Vector3().addVectors(pA, pB).multiplyScalar(0.5);
            const div = document.createElement('div');
            div.className = 'member-label';
            div.innerHTML = `M${m.id} ${m.pin}<br>${m.sec}`;
            const label = new THREE.CSS2DObject(div);
            label.position.copy(pMid);
            groups.memberLabels.add(label);

            const dirX = new THREE.Vector3().subVectors(pB, pA).normalize();
            let dirY = new THREE.Vector3(0, 1, 0);
            if (Math.abs(dirX.y) > 0.99) dirY.set(0, 0, 1);
            let dirZ = new THREE.Vector3().crossVectors(dirX, dirY).normalize();
            dirY.crossVectors(dirZ, dirX).normalize();

            const arrowLen = 0.6;
            groups.localAxes.add(new THREE.ArrowHelper(dirX, pMid, arrowLen, 0xff0000));
            groups.localAxes.add(new THREE.ArrowHelper(dirY, pMid, arrowLen, 0x00aa00));
            groups.localAxes.add(new THREE.ArrowHelper(dirZ, pMid, arrowLen, 0xaa00aa));
        });

        createBoundingGrid(L_X, L_Y, L_Z);
        controls.target.set(L_X / 2, L_Y / 2, L_Z / 2);
        toggleLayers();
    }

    function createBoundingGrid(xMax, yMax, zMax) {
        const boxGeo = new THREE.BoxGeometry(xMax, yMax, zMax);
        const edges = new THREE.EdgesGeometry(boxGeo);
        const boxLine = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xbbbbbb }));
        boxLine.position.set(xMax / 2, yMax / 2, zMax / 2);
        groups.gridBox.add(boxLine);

        const addAxisTitle = (text, pos) => {
            const div = document.createElement('div');
            div.className = 'axis-label';
            div.innerText = text;
            const label = new THREE.CSS2DObject(div);
            label.position.set(...pos);
            groups.gridBox.add(label);
        };

        addAxisTitle("X (m) - lateral", [xMax / 2, -0.8, zMax + 0.5]);
        addAxisTitle("Y (m) - vertical", [-0.8, yMax / 2, -0.5]);
        addAxisTitle("Z (m) - lateral", [xMax + 0.8, -0.8, zMax / 2]);
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
        groups.localAxes.visible = document.getElementById('layerLocalAxes').checked;
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

# Save temporary HTML file and open in browser
output_path = "index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_code)

webbrowser.open("file://" + os.path.abspath(output_path))