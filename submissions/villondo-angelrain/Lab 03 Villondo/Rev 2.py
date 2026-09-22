import os
import webbrowser

html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rev 3 Solver Transformation - Adaptive Dynamic Visual Structural Solver</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { display: flex; height: 100vh; background-color: #12151c; color: #fff; overflow: hidden; }
        
        /* Sidebar Control Panel */
        #sidebar { width: 440px; background: #1a1e29; border-right: 1px solid #2d3345; display: flex; flex-direction: column; z-index: 10; }
        .header { padding: 14px; background: #0f121a; border-bottom: 1px solid #2d3345; text-align: center; }
        .header h2 { font-size: 14px; color: #4ec9b0; text-transform: uppercase; letter-spacing: 1px; }
        .header .student-info { font-size: 10.5px; color: #e5c07b; margin-top: 4px; line-height: 1.4; font-family: 'Consolas', monospace; }
        .header p { font-size: 10px; color: #8a94a6; margin-top: 2px; }
        .content { padding: 12px; overflow-y: auto; flex: 1; }
        
        .section { margin-bottom: 14px; background: #222736; padding: 10px; border-radius: 6px; border: 1px solid #2d3345; }
        .section h3 { font-size: 11.5px; color: #61afef; margin-bottom: 8px; border-bottom: 1px solid #2d3345; padding-bottom: 4px; }
        .form-group { margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between; }
        label { font-size: 11px; color: #abb2bf; }
        input, select { background: #181b24; border: 1px solid #3b4254; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; width: 55%; }
        button { width: 100%; background: #2c68ad; color: white; border: none; padding: 8px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px; margin-top: 4px; }
        button:hover { background: #3b7ed0; }
        
        /* Toggle Switch Styling */
        .toggle-group { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; padding: 2px 0; border-bottom: 1px solid #282d3c; }
        .toggle-label { font-size: 10.5px; color: #dcdcaa; font-weight: 500; }
        .switch { position: relative; display: inline-block; width: 32px; height: 16px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #3b4254; transition: .3s; border-radius: 16px; }
        .slider:before { position: absolute; content: ""; height: 10px; width: 10px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; }
        input:checked + .slider { background-color: #28a745; }
        input:checked + .slider:before { transform: translateX(16px); }

        #viewport { flex: 1; position: relative; }
        #canvas-container { width: 100%; height: 100%; }
        
        /* Model Data Box */
        #model-data-overlay { position: absolute; top: 20px; right: 20px; background: rgba(26, 30, 41, 0.94); backdrop-filter: blur(6px); border: 1px solid #3b4254; padding: 14px; border-radius: 8px; width: 340px; font-family: 'Consolas', monospace; font-size: 11px; color: #abb2bf; box-shadow: 0 4px 20px rgba(0,0,0,0.5); max-height: 92vh; overflow-y: auto; }
        #model-data-overlay h4 { color: #e5c07b; margin-bottom: 8px; font-size: 11.5px; border-bottom: 1px solid #3b4254; padding-bottom: 4px; text-transform: uppercase; }
        .data-group { margin-bottom: 8px; }
        .data-title { color: #61afef; font-weight: bold; margin-bottom: 2px; }
        .data-row { display: flex; justify-content: space-between; margin-left: 8px; line-height: 1.4; }
        .data-val { color: #98c379; font-weight: bold; }

        /* 2D Canvas for Text Labels Overlay */
        #labels-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
    </style>
    <!-- Three.js & OrbitControls -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="sidebar">
        <div class="header">
            <h2>Rev 3 Solver Transformation</h2>
            <div class="student-info">
                Name: Villondo, Angel Rain L.<br>
                Section: BSCE-3D | Course: Numerical Solution Laboratory
            </div>
            <p>Adaptive Auto-Scaling 3D Matrix Structural Engine</p>
        </div>

        <div class="content">
            <!-- Unit System Selection -->
            <div class="section">
                <h3>Unit Configuration</h3>
                <div class="form-group">
                    <label>Unit System</label>
                    <select id="unitSystem" onchange="updateUnits()">
                        <option value="Metric">Standard Metric (m, kN, mm, kNm)</option>
                        <option value="Imperial">Imperial (ft, kips, in, kip-ft)</option>
                    </select>
                </div>
            </div>

            <!-- 1. 3D View Layer Controls -->
            <div class="section">
                <h3>3D View Layer Controls</h3>
                
                <div class="toggle-group">
                    <span class="toggle-label">Display Mode</span>
                    <select id="viewStyle" style="width:48%; font-size:10px;" onchange="renderScene()">
                        <option value="solid">3D Solid Extrusions</option>
                        <option value="wireframe">Line Diagram</option>
                    </select>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">1. Nodes</span>
                    <label class="switch"><input type="checkbox" id="showNodes" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">2. Boundary Supports (X-Z Ground)</span>
                    <label class="switch"><input type="checkbox" id="showSupports" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">3. Degrees of Freedom (DOFs)</span>
                    <label class="switch"><input type="checkbox" id="showDOFs" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">4. Member Properties & Local Axes</span>
                    <label class="switch"><input type="checkbox" id="showProps" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">5. Member Labels (IDs)</span>
                    <label class="switch"><input type="checkbox" id="showMemberLabels" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">6. Section Labels (b x h)</span>
                    <label class="switch"><input type="checkbox" id="showSectionLabels" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">7. Material Labels (Steel E)</span>
                    <label class="switch"><input type="checkbox" id="showMaterialLabels" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">8. Solved Displacements (Deflection)</span>
                    <label class="switch"><input type="checkbox" id="showDisp" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
                <div class="toggle-group">
                    <span class="toggle-label">9. Member Internal Forces</span>
                    <label class="switch"><input type="checkbox" id="showForces" checked onchange="renderScene()"><span class="slider"></span></label>
                </div>
            </div>

            <!-- 2. Section Dimensions -->
            <div class="section">
                <h3>Adjustable Section Dimensions</h3>
                <div class="form-group"><label id="lblBeamW">Beam Width (b_b)</label><input type="number" id="beamW" value="0.25" step="0.05" onchange="updateSectionProperties()"></div>
                <div class="form-group"><label id="lblBeamH">Beam Height (h_b)</label><input type="number" id="beamH" value="0.40" step="0.05" onchange="updateSectionProperties()"></div>
                <div class="form-group"><label id="lblColW">Column Width (b_c)</label><input type="number" id="colW" value="0.30" step="0.05" onchange="updateSectionProperties()"></div>
                <div class="form-group"><label id="lblColH">Column Depth (h_c)</label><input type="number" id="colH" value="0.30" step="0.05" onchange="updateSectionProperties()"></div>
            </div>

            <!-- 3. Cube Geometry & Auto-Scaling -->
            <div class="section">
                <h3>Cube Geometry & Scaling Parameters</h3>
                <div class="form-group"><label>Cube Edge (L)</label><input type="number" id="cubeSize" value="6.0" step="1.0" onchange="buildCubeModel()"></div>
                <div class="form-group"><label>Elastic Modulus (E)</label><input type="number" id="propE" value="200000"></div>
                <div class="form-group"><label>Beam Area (A_b)</label><input type="number" id="propAb" value="100000" readonly></div>
                <div class="form-group"><label>Column Area (A_c)</label><input type="number" id="propAc" value="90000" readonly></div>
            </div>

            <!-- 4. Applied Loads -->
            <div class="section">
                <h3>Applied Point Loads</h3>
                <div class="form-group"><label>Target Load Node</label><input type="number" id="loadNode" value="5"></div>
                <div class="form-group"><label id="lblFx">Force Fx (kN)</label><input type="number" id="loadFx" value="50"></div>
                <div class="form-group"><label id="lblFy">Force Fy (kN)</label><input type="number" id="loadFy" value="-100"></div>
                <div class="form-group"><label id="lblFz">Force Fz (kN)</label><input type="number" id="loadFz" value="20"></div>
                <div class="form-group"><label>Deformation Magnifier</label><input type="number" id="scaleDisp" value="50" step="10" onchange="renderScene()"></div>
                <button onclick="solve3DFrame()">SOLVE & DISPLAY ON CUBE</button>
            </div>
        </div>
    </div>

    <div id="viewport">
        <div id="canvas-container"></div>
        <canvas id="labels-canvas"></canvas>

        <!-- MODEL DATA OVERLAY -->
        <div id="model-data-overlay">
            <h4>MODEL DATA - REV 3</h4>
            
            <div class="data-group">
                <div class="data-title">Geometry & Scale Factor</div>
                <div class="data-row"><span>Cube Edge (L)</span><span class="data-val" id="dispCubeEdge">6.0 m</span></div>
                <div class="data-row"><span>Visual Scale Factor</span><span class="data-val" id="dispScaleFactor">1.00x</span></div>
                <div class="data-row"><span>Node Sphere Radius</span><span class="data-val" id="dispNodeRadius">0.18 m</span></div>
                <div class="data-row"><span>Support Cone Height</span><span class="data-val" id="dispSupportSize">0.50 m</span></div>
            </div>

            <div class="data-group">
                <div class="data-title">Section Dimensions</div>
                <div class="data-row"><span>Beam Size</span><span class="data-val" id="dispBeamDim">0.25 x 0.40 m</span></div>
                <div class="data-row"><span>Column Size</span><span class="data-val" id="dispColDim">0.30 x 0.30 m</span></div>
            </div>

            <h4 style="margin-top:10px;">ANALYSIS RESULTS</h4>
            <div class="data-row"><span>Max Deflection</span><span class="data-val" id="resDisp">0.000 mm</span></div>
            <div class="data-row"><span>Max Axial Force</span><span class="data-val" id="resAxial">0.00 kN</span></div>
            <div class="data-row"><span>Status</span><span class="data-val" id="resStatus">Ready</span></div>
        </div>
    </div>

    <script>
        let L = 6.0;
        let scaleFactor = 1.0;
        let nodes = {}, elements = [], supports = { 1:'pinned', 2:'pinned', 3:'pinned', 4:'pinned' };
        let pointLoads = {};
        let solvedU = [], solvedForces = [];
        let labelItems = [];

        const container = document.getElementById('canvas-container');
        const canvas2d = document.getElementById('labels-canvas');
        const ctx2d = canvas2d.getContext('2d');

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x12151c);

        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 2000);
        camera.position.set(16, 12, 18);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(3, 3, 3);

        scene.add(new THREE.AmbientLight(0xffffff, 0.8));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
        dirLight.position.set(10, 20, 15);
        scene.add(dirLight);

        let gridHelper = new THREE.GridHelper(20, 20, 0x2d3345, 0x1f2430);
        gridHelper.position.set(3, 0, 3);
        scene.add(gridHelper);

        const structureGroup = new THREE.Group();
        scene.add(structureGroup);

        function resizeCanvas() {
            canvas2d.width = container.clientWidth;
            canvas2d.height = container.clientHeight;
        }
        window.addEventListener('resize', resizeCanvas);

        function updateUnits() {
            const sys = document.getElementById('unitSystem').value;
            if (sys === 'Imperial') {
                document.getElementById('cubeSize').value = 20.0;
                document.getElementById('beamW').value = 10.0;
                document.getElementById('beamH').value = 16.0;
                document.getElementById('colW').value = 12.0;
                document.getElementById('colH').value = 12.0;
                document.getElementById('propE').value = 29000;
                document.getElementById('lblBeamW').innerText = "Beam Width (in)";
                document.getElementById('lblBeamH').innerText = "Beam Height (in)";
                document.getElementById('lblColW').innerText = "Column Width (in)";
                document.getElementById('lblColH').innerText = "Column Depth (in)";
                document.getElementById('lblFx').innerText = "Force Fx (kips)";
                document.getElementById('lblFy').innerText = "Force Fy (kips)";
                document.getElementById('lblFz').innerText = "Force Fz (kips)";
                document.getElementById('loadFx').value = 10;
                document.getElementById('loadFy').value = -25;
                document.getElementById('loadFz').value = 5;
            } else {
                document.getElementById('cubeSize').value = 6.0;
                document.getElementById('beamW').value = 0.25;
                document.getElementById('beamH').value = 0.40;
                document.getElementById('colW').value = 0.30;
                document.getElementById('colH').value = 0.30;
                document.getElementById('propE').value = 200000;
                document.getElementById('lblBeamW').innerText = "Beam Width (m)";
                document.getElementById('lblBeamH').innerText = "Beam Height (m)";
                document.getElementById('lblColW').innerText = "Column Width (m)";
                document.getElementById('lblColH').innerText = "Column Depth (m)";
                document.getElementById('lblFx').innerText = "Force Fx (kN)";
                document.getElementById('lblFy').innerText = "Force Fy (kN)";
                document.getElementById('lblFz').innerText = "Force Fz (kN)";
                document.getElementById('loadFx').value = 50;
                document.getElementById('loadFy').value = -100;
                document.getElementById('loadFz').value = 20;
            }
            updateSectionProperties();
        }

        function updateSectionProperties() {
            const sys = document.getElementById('unitSystem').value;
            const bw = parseFloat(document.getElementById('beamW').value);
            const bh = parseFloat(document.getElementById('beamH').value);
            const cw = parseFloat(document.getElementById('colW').value);
            const ch = parseFloat(document.getElementById('colH').value);

            const unitLabel = (sys === 'Metric') ? ' m' : ' in';
            document.getElementById('dispBeamDim').innerText = `${bw} x ${bh}${unitLabel}`;
            document.getElementById('dispColDim').innerText = `${cw} x ${ch}${unitLabel}`;

            const areaFactor = (sys === 'Metric') ? 1e6 : 1.0;
            const Ab = bw * bh * areaFactor;
            const Ac = cw * ch * areaFactor;

            document.getElementById('propAb').value = Ab.toFixed(0);
            document.getElementById('propAc').value = Ac.toFixed(0);

            buildCubeModel();
        }

        function buildCubeModel() {
            L = parseFloat(document.getElementById('cubeSize').value);
            const sys = document.getElementById('unitSystem').value;
            
            scaleFactor = Math.max(0.2, L / 6.0);
            
            document.getElementById('dispCubeEdge').innerText = L.toFixed(1) + (sys === 'Metric' ? " m" : " ft");
            document.getElementById('dispScaleFactor').innerText = scaleFactor.toFixed(2) + "x";

            controls.target.set(L / 2, L / 2, L / 2);
            camera.position.set(L * 2.5, L * 2.0, L * 2.8);
            controls.update();

            scene.remove(gridHelper);
            const gridExtent = Math.ceil(L * 3.0);
            gridHelper = new THREE.GridHelper(gridExtent, 20, 0x2d3345, 0x1f2430);
            gridHelper.position.set(L / 2, 0, L / 2);
            scene.add(gridHelper);

            nodes = {
                1: [0, 0, 0], 2: [L, 0, 0], 3: [L, 0, L], 4: [0, 0, L],
                5: [0, L, 0], 6: [L, L, 0], 7: [L, L, L], 8: [0, L, L]
            };

            elements = [
                { id: 'M1', n1: 1, n2: 2, beta: 0, type: 'Beam' },
                { id: 'M2', n1: 2, n2: 3, beta: 0, type: 'Beam' },
                { id: 'M3', n1: 3, n2: 4, beta: 0, type: 'Beam' },
                { id: 'M4', n1: 4, n2: 1, beta: 0, type: 'Beam' },
                { id: 'M9', n1: 1, n2: 5, beta: 90, type: 'Column' },
                { id: 'M10', n1: 2, n2: 6, beta: 90, type: 'Column' },
                { id: 'M11', n1: 3, n2: 7, beta: 90, type: 'Column' },
                { id: 'M12', n1: 4, n2: 8, beta: 90, type: 'Column' },
                { id: 'M5', n1: 5, n2: 6, beta: 0, type: 'Beam' },
                { id: 'M6', n1: 6, n2: 7, beta: 0, type: 'Beam' },
                { id: 'M7', n1: 7, n2: 8, beta: 0, type: 'Beam' },
                { id: 'M8', n1: 8, n2: 5, beta: 0, type: 'Beam' }
            ];

            solve3DFrame();
        }

        function createExtrudedMemberMesh(p1, p2, width, height, colorHex) {
            const v1 = new THREE.Vector3(p1[0], p1[1], p1[2]);
            const v2 = new THREE.Vector3(p2[0], p2[1], p2[2]);
            const dir = new THREE.Vector3().subVectors(v2, v1);
            const len = dir.length();

            const shape = new THREE.Shape();
            const w2 = width / 2, h2 = height / 2;
            shape.moveTo(-w2, -h2); shape.lineTo(w2, -h2);
            shape.lineTo(w2, h2);   shape.lineTo(-w2, h2);
            shape.closePath();

            const extrudeSettings = { depth: len, bevelEnabled: false };
            const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
            const material = new THREE.MeshPhongMaterial({ color: colorHex, shininess: 60 });
            const mesh = new THREE.Mesh(geometry, material);

            mesh.position.copy(v1);
            mesh.lookAt(v2);

            return mesh;
        }

        function renderScene() {
            while(structureGroup.children.length > 0) structureGroup.remove(structureGroup.children[0]);
            labelItems = [];

            const showNodes = document.getElementById('showNodes').checked;
            const showSupports = document.getElementById('showSupports').checked;
            const showDOFs = document.getElementById('showDOFs').checked;
            const showProps = document.getElementById('showProps').checked;
            const showMemberLabels = document.getElementById('showMemberLabels').checked;
            const showSectionLabels = document.getElementById('showSectionLabels').checked;
            const showMaterialLabels = document.getElementById('showMaterialLabels').checked;
            const showDisp = document.getElementById('showDisp').checked;
            const showForces = document.getElementById('showForces').checked;
            const viewStyle = document.getElementById('viewStyle').value;
            const scaleDisp = parseFloat(document.getElementById('scaleDisp').value);
            const sys = document.getElementById('unitSystem').value;
            
            const bw = parseFloat(document.getElementById('beamW').value);
            const bh = parseFloat(document.getElementById('beamH').value);
            const cw = parseFloat(document.getElementById('colW').value);
            const ch = parseFloat(document.getElementById('colH').value);
            const E_val = document.getElementById('propE').value;

            const forceUnit = (sys === 'Metric') ? 'kN' : 'kips';

            const nodeRadius = 0.18 * scaleFactor;
            const coneRadius = 0.40 * scaleFactor;
            const coneHeight = 0.50 * scaleFactor;
            const plateSize = 0.60 * scaleFactor;
            const plateThick = 0.06 * scaleFactor;

            document.getElementById('dispNodeRadius').innerText = (nodeRadius).toFixed(2) + " m";
            document.getElementById('dispSupportSize').innerText = (coneHeight).toFixed(2) + " m";

            const nodeKeys = Object.keys(nodes).map(Number).sort((a,b)=>a-b);
            const nodeMap = {}; nodeKeys.forEach((k, i) => nodeMap[k] = i);

            for (let id in nodes) {
                const p = nodes[id];
                const isPinned = (supports[id] === 'pinned');
                
                if (showNodes) {
                    const nGeo = new THREE.SphereGeometry(nodeRadius, 16, 16);
                    const nMat = new THREE.MeshBasicMaterial({ color: isPinned ? 0xff4444 : 0xff6b6b });
                    const nMesh = new THREE.Mesh(nGeo, nMat);
                    nMesh.position.set(p[0], p[1], p[2]);
                    structureGroup.add(nMesh);

                    labelItems.push({ pos: new THREE.Vector3(p[0], p[1] + (0.35 * scaleFactor), p[2]), text: `N${id}`, color: '#61afef' });
                }

                if (showSupports && isPinned) {
                    const coneGeo = new THREE.ConeGeometry(coneRadius, coneHeight, 4);
                    const coneMat = new THREE.MeshBasicMaterial({ color: 0xff00ff });
                    const coneMesh = new THREE.Mesh(coneGeo, coneMat);
                    coneMesh.position.set(p[0], -coneHeight / 2.0, p[2]);
                    structureGroup.add(coneMesh);

                    const plateGeo = new THREE.BoxGeometry(plateSize, plateThick, plateSize);
                    const plateMat = new THREE.MeshBasicMaterial({ color: 0x888888 });
                    const plateMesh = new THREE.Mesh(plateGeo, plateMat);
                    plateMesh.position.set(p[0], -coneHeight - (plateThick / 2.0), p[2]);
                    structureGroup.add(plateMesh);
                }

                if (showDOFs) {
                    const dofBase = (id - 1) * 6;
                    labelItems.push({ pos: new THREE.Vector3(p[0], p[1] - (0.35 * scaleFactor), p[2]), text: `DOF ${dofBase+1}-${dofBase+6}`, color: '#e5c07b' });
                }
            }

            elements.forEach((e, idx) => {
                const p1 = nodes[e.n1], p2 = nodes[e.n2];
                if(p1 && p2) {
                    const isBeam = (e.type === 'Beam');
                    const colorHex = isBeam ? 0x007acc : 0x28a745;

                    if (viewStyle === 'solid') {
                        const w = isBeam ? bw : cw;
                        const h = isBeam ? bh : ch;
                        const solidMesh = createExtrudedMemberMesh(p1, p2, w, h, colorHex);
                        structureGroup.add(solidMesh);
                    } else {
                        const v1 = new THREE.Vector3(p1[0], p1[1], p1[2]);
                        const v2 = new THREE.Vector3(p2[0], p2[1], p2[2]);
                        const geo = new THREE.BufferGeometry().setFromPoints([v1, v2]);
                        structureGroup.add(new THREE.Line(geo, new THREE.LineBasicMaterial({ color: colorHex, linewidth: 3 })));
                    }

                    const mid = new THREE.Vector3((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2);

                    if (showProps) {
                        const dirX = new THREE.Vector3().subVectors(new THREE.Vector3(...p2), new THREE.Vector3(...p1)).normalize();
                        structureGroup.add(new THREE.ArrowHelper(dirX, mid, 0.6 * scaleFactor, 0xe06c75, 0.15 * scaleFactor, 0.1 * scaleFactor));
                    }

                    // CLEARLY STAGGERED VERTICAL DIRECTIONS FOR ALL LABELS
                    if (showMemberLabels) {
                        labelItems.push({ pos: new THREE.Vector3(mid.x, mid.y + (0.35 * scaleFactor), mid.z), text: `${e.id} [${e.type}]`, color: '#61afef' });
                    }

                    if (showSectionLabels) {
                        const secText = isBeam ? `Beam: ${bw}x${bh}` : `Col: ${cw}x${ch}`;
                        labelItems.push({ pos: new THREE.Vector3(mid.x, mid.y + (0.12 * scaleFactor), mid.z), text: secText, color: '#98c379' });
                    }

                    if (showMaterialLabels) {
                        labelItems.push({ pos: new THREE.Vector3(mid.x, mid.y - (0.12 * scaleFactor), mid.z), text: `Steel (E=${E_val})`, color: '#d19a66' });
                    }

                    if (showForces && solvedForces.length > 0) {
                        const forceData = solvedForces[idx];
                        if (forceData) {
                            labelItems.push({ pos: new THREE.Vector3(mid.x, mid.y - (0.35 * scaleFactor), mid.z), text: `P:${forceData.axial.toFixed(1)}${forceUnit}`, color: '#e5c07b' });
                        }
                    }
                }
            });

            if (showDisp && solvedU.length > 0) {
                const defNodes = {};

                nodeKeys.forEach(nid => {
                    const idx = nodeMap[nid] * 6;
                    const ux = solvedU[idx] || 0, uy = solvedU[idx+1] || 0, uz = solvedU[idx+2] || 0;
                    const orig = nodes[nid];
                    
                    defNodes[nid] = [
                        orig[0] + (ux * scaleDisp / 1000.0),
                        orig[1] + (uy * scaleDisp / 1000.0),
                        orig[2] + (uz * scaleDisp / 1000.0)
                    ];
                });

                elements.forEach(e => {
                    const p1 = defNodes[e.n1], p2 = defNodes[e.n2];
                    if (p1 && p2) {
                        const v1 = new THREE.Vector3(p1[0], p1[1], p1[2]);
                        const v2 = new THREE.Vector3(p2[0], p2[1], p2[2]);
                        const geo = new THREE.BufferGeometry().setFromPoints([v1, v2]);
                        const mat = new THREE.LineDashedMaterial({ color: 0xe5c07b, dashSize: 0.2 * scaleFactor, gapSize: 0.1 * scaleFactor });
                        const line = new THREE.Line(geo, mat);
                        line.computeLineDistances();
                        structureGroup.add(line);
                    }
                });
            }
        }

        function solve3DFrame() {
            const sys = document.getElementById('unitSystem').value;
            const E = parseFloat(document.getElementById('propE').value);
            const Ab = parseFloat(document.getElementById('propAb').value);
            const Ac = parseFloat(document.getElementById('propAc').value);

            const bw = parseFloat(document.getElementById('beamW').value);
            const bh = parseFloat(document.getElementById('beamH').value);
            const cw = parseFloat(document.getElementById('colW').value);
            const ch = parseFloat(document.getElementById('colH').value);

            const factor = (sys === 'Metric') ? 1e12 : 1.0;
            const Ixb = (bw * Math.pow(bh, 3) / 12.0) * factor;
            const Ixc = (cw * Math.pow(ch, 3) / 12.0) * factor;

            const targetNode = parseInt(document.getElementById('loadNode').value);
            pointLoads = {};
            pointLoads[targetNode] = [
                parseFloat(document.getElementById('loadFx').value),
                parseFloat(document.getElementById('loadFy').value),
                parseFloat(document.getElementById('loadFz').value)
            ];

            const nodeKeys = Object.keys(nodes).map(Number).sort((a,b)=>a-b);
            const nodeMap = {}; nodeKeys.forEach((k, i) => nodeMap[k] = i);
            const numDofs = nodeKeys.length * 6;

            let K = Array(numDofs).fill(0).map(() => Array(numDofs).fill(0));
            let P = Array(numDofs).fill(0);

            for (let nid in pointLoads) {
                if (nodeMap[nid] !== undefined) {
                    const idx = nodeMap[nid] * 6, load = pointLoads[nid];
                    P[idx] += load[0] * 1000; P[idx+1] += load[1] * 1000; P[idx+2] += load[2] * 1000;
                }
            }

            let elemData = [];
            elements.forEach(elem => {
                const ni = elem.n1, nj = elem.n2, p1 = nodes[ni], p2 = nodes[nj];
                const scale = (sys === 'Metric') ? 1000.0 : 12.0;
                const dx = (p2[0] - p1[0]) * scale, dy = (p2[1] - p1[1]) * scale, dz = (p2[2] - p1[2]) * scale;
                const L_elem = Math.sqrt(dx*dx + dy*dy + dz*dz);

                const isBeam = (elem.type === 'Beam');
                const A_elem = isBeam ? Ab : Ac;
                const Ix_elem = isBeam ? Ixb : Ixc;

                let k_local = Array(12).fill(0).map(() => Array(12).fill(0));
                const EA_L = E * A_elem / L_elem;
                const EIz_L3 = 12 * E * Ix_elem / Math.pow(L_elem, 3);

                k_local[0][0] = EA_L; k_local[0][6] = -EA_L; k_local[6][0] = -EA_L; k_local[6][6] = EA_L;
                k_local[1][1] = EIz_L3; k_local[1][7] = -EIz_L3; k_local[7][1] = -EIz_L3; k_local[7][7] = EIz_L3;

                const idx1 = nodeMap[ni]*6, idx2 = nodeMap[nj]*6;
                const dofs = [...Array(6).keys()].map(i=>idx1+i).concat([...Array(6).keys()].map(i=>idx2+i));

                for(let r=0; r<12; r++) {
                    for(let c=0; c<12; c++) K[dofs[r]][dofs[c]] += k_local[r][c];
                }
                elemData.push({ id: elem.id, ni: ni, nj: nj, L: L_elem, EA_L: EA_L, EIz_L3: EIz_L3, dofs: dofs });
            });

            let active = Array(numDofs).fill(true);
            for(let nid in supports) {
                if(nodeMap[nid] !== undefined) {
                    const base = nodeMap[nid]*6;
                    active[base] = false; active[base+1] = false; active[base+2] = false;
                }
            }

            let activeIndices = [];
            active.forEach((act, i) => { if(act) activeIndices.push(i); });

            let K_red = activeIndices.map(r => activeIndices.map(c => K[r][c]));
            let P_red = activeIndices.map(r => P[r]);

            let U_red = solveLinearSystem(K_red, P_red);
            solvedU = Array(numDofs).fill(0);
            activeIndices.forEach((idx, i) => solvedU[idx] = U_red[i]);

            let maxDisp = 0;
            nodeKeys.forEach(nid => {
                const idx = nodeMap[nid]*6;
                const ux = solvedU[idx], uy = solvedU[idx+1], uz = solvedU[idx+2];
                const mag = Math.sqrt(ux*ux + uy*uy + uz*uz);
                if(mag > maxDisp) maxDisp = mag;
            });

            solvedForces = [];
            let maxAxial = 0;
            elemData.forEach(e => {
                const u1_x = solvedU[e.dofs[0]], u2_x = solvedU[e.dofs[6]];
                const u1_y = solvedU[e.dofs[1]], u2_y = solvedU[e.dofs[7]];
                
                const axialP = (e.EA_L * (u2_x - u1_x)) / 1000.0;
                const shearV = (e.EIz_L3 * (u1_y - u2_y)) / 1000.0;
                const momentM = shearV * (e.L / ((sys === 'Metric') ? 1000.0 : 12.0));

                if(Math.abs(axialP) > maxAxial) maxAxial = Math.abs(axialP);
                solvedForces.push({ axial: axialP, shear: shearV, moment: momentM });
            });

            const dispUnit = (sys === 'Metric') ? 'mm' : 'in';
            const forceUnit = (sys === 'Metric') ? 'kN' : 'kips';
            document.getElementById('resDisp').innerText = maxDisp.toFixed(3) + ' ' + dispUnit;
            document.getElementById('resAxial').innerText = maxAxial.toFixed(2) + ' ' + forceUnit;
            document.getElementById('resStatus').innerText = 'Solved Matrix OK';

            renderScene();
        }

        function solveLinearSystem(A, b) {
            let n = b.length;
            for (let i = 0; i < n; i++) {
                let maxEl = Math.abs(A[i][i]), maxRow = i;
                for (let k = i + 1; k < n; k++) {
                    if (Math.abs(A[k][i]) > maxEl) { maxEl = Math.abs(A[k][i]); maxRow = k; }
                }
                for (let k = i; k < n; k++) { let tmp = A[maxRow][k]; A[maxRow][k] = A[i][k]; A[i][k] = tmp; }
                let tmp = b[maxRow]; b[maxRow] = b[i]; b[i] = tmp;

                for (let k = i + 1; k < n; k++) {
                    let c = -A[k][i] / A[i][i];
                    for (let j = i; j < n; j++) {
                        if (i === j) A[k][j] = 0;
                        else A[k][j] += c * A[i][j];
                    }
                    b[k] += c * b[i];
                }
            }
            let x = Array(n).fill(0);
            for (let i = n - 1; i >= 0; i--) {
                let sum = 0;
                for (let k = i + 1; k < n; k++) sum += A[i][k] * x[k];
                x[i] = (b[i] - sum) / A[i][i];
            }
            return x;
        }

        function drawOverlayLabels() {
            resizeCanvas();
            ctx2d.clearRect(0, 0, canvas2d.width, canvas2d.height);
            ctx2d.font = "bold 10px Consolas, monospace";

            labelItems.forEach(item => {
                const vec = item.pos.clone();
                vec.project(camera);

                if (vec.z < 1) {
                    const x = (vec.x * .5 + .5) * canvas2d.width;
                    const y = (-(vec.y * .5) + .5) * canvas2d.height;

                    ctx2d.fillStyle = "rgba(18, 21, 28, 0.75)";
                    const textWidth = ctx2d.measureText(item.text).width;
                    ctx2d.fillRect(x - textWidth/2 - 3, y - 10, textWidth + 6, 14);

                    ctx2d.fillStyle = item.color;
                    ctx2d.textAlign = "center";
                    ctx2d.fillText(item.text, x, y);
                }
            });
        }

        window.onload = () => { updateSectionProperties(); resizeCanvas(); };
        function animate() { 
            requestAnimationFrame(animate); 
            renderer.render(scene, camera); 
            drawOverlayLabels(); 
        }
        animate();
    </script>
</body>
</html>
"""

# Write updated script to file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_code)

abs_path = os.path.abspath("index.html")
webbrowser.open(f"file://{abs_path}")
print("Rev 3 Solver Transformation regenerated with directional label staggering.")
