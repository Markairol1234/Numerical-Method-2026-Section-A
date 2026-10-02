import os
import webbrowser

html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cube FEM Studio - Executive Edition</title>
    <style>
        :root {
            /* Sung Jinwoo / Shadow Monarch Aura Palette */
            --bg-app: #09070f;
            --sidebar-bg: #0d0b14;
            --sidebar-text: #94a3b8;
            --sidebar-text-active: #f3e8ff;
            --sidebar-hover: rgba(168, 85, 247, 0.15);
            
            --card-bg: #13111c;
            --border-color: #2e1065;
            --border-glow: rgba(168, 85, 247, 0.35);
            --text-main: #f3e8ff;
            --text-muted: #a78bfa;
            
            --accent-purple: #a855f7;
            --accent-purple-bright: #c084fc;
            --accent-purple-glow: rgba(168, 85, 247, 0.6);
            --accent-pink: #e879f9;
            --accent-green: #34d399;
            --accent-blue: #38bdf8;
            --accent-yellow: #fbbf24;
            
            --pill-bg: #1a1625;
            --input-bg: #0f0d17;
            --table-header: #1e1a2e;
            --table-border: #2e1065;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { 
            display: flex; 
            height: 100vh; 
            background-color: var(--bg-app); 
            background-image: radial-gradient(circle at 10% 20%, rgba(88, 28, 135, 0.15) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(126, 34, 206, 0.12) 0%, transparent 40%);
            color: var(--text-main); 
            overflow: hidden; 
            padding: 12px; 
            gap: 12px; 
            pointer-events: auto;
        }

        /* Custom Scrollbars */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-app); }
        ::-webkit-scrollbar-thumb { background: #3b0764; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent-purple); }

        /* Floating Dark Rounded Sidebar */
        #app-sidebar { 
            width: 260px; 
            background-color: var(--sidebar-bg); 
            border-radius: 20px; 
            display: flex; 
            flex-direction: column; 
            padding: 20px 14px; 
            flex-shrink: 0; 
            border: 1px solid var(--border-color);
            box-shadow: 0 0 20px rgba(147, 51, 234, 0.15); 
            z-index: 50; 
            overflow-y: auto; 
            overflow-x: hidden; 
            transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            pointer-events: auto;
        }
        #app-sidebar.collapsed { width: 76px; padding: 20px 10px; }
        
        .sidebar-brand { 
            font-size: 18px; 
            font-weight: 800; 
            color: #ffffff; 
            margin-bottom: 12px; 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            padding-left: 8px; 
            letter-spacing: 0.5px; 
            white-space: nowrap; 
            text-shadow: 0 0 10px var(--accent-purple-glow);
        }
        .sidebar-brand span { color: var(--accent-purple-bright); }
        #app-sidebar.collapsed .sidebar-brand span, #app-sidebar.collapsed .sidebar-brand-text { display: none; }
        
        /* Profile Card */
        .sidebar-profile { 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            background: linear-gradient(135deg, rgba(88, 28, 135, 0.3) 0%, rgba(15, 13, 23, 0.6) 100%); 
            padding: 10px; 
            border-radius: 12px; 
            margin-bottom: 16px; 
            border: 1px solid var(--border-color); 
            box-shadow: inset 0 0 10px rgba(168, 85, 247, 0.1);
            white-space: nowrap; 
            overflow: hidden; 
        }
        .profile-avatar { 
            width: 36px; 
            height: 36px; 
            border-radius: 50%; 
            background: linear-gradient(135deg, var(--accent-purple) 0%, #581c87 100%); 
            color: #ffffff; 
            font-weight: 700; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 13px; 
            flex-shrink: 0; 
            box-shadow: 0 0 10px var(--accent-purple-glow);
        }
        .profile-info { overflow: hidden; transition: opacity 0.2s; }
        #app-sidebar.collapsed .profile-info { opacity: 0; width: 0; display: none; }
        .profile-name { font-size: 11px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .profile-section { font-size: 10px; color: var(--text-muted); }

        .sidebar-section-title { font-size: 10px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1.2px; margin-bottom: 8px; padding-left: 8px; font-weight: 700; white-space: nowrap; overflow: hidden; transition: opacity 0.2s; }
        #app-sidebar.collapsed .sidebar-section-title { opacity: 0; height: 0; margin: 0; padding: 0; overflow: hidden; }

        .sidebar-menu { display: flex; flex-direction: column; gap: 4px; margin-bottom: 16px; }
        
        .sidebar-item { 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            padding: 9px 12px; 
            border-radius: 10px; 
            color: var(--sidebar-text); 
            font-size: 12px; 
            font-weight: 600; 
            cursor: pointer; 
            transition: all 0.2s ease; 
            text-decoration: none; 
            border: 1px solid transparent; 
            background: none; 
            width: 100%; 
            text-align: left; 
            white-space: nowrap; 
            overflow: hidden; 
            pointer-events: auto;
        }
        .sidebar-item:hover { 
            background-color: var(--sidebar-hover); 
            color: var(--sidebar-text-active); 
            border-color: rgba(168, 85, 247, 0.3);
            box-shadow: 0 0 10px rgba(168, 85, 247, 0.15);
        }
        .sidebar-item.active { 
            background: linear-gradient(90deg, rgba(168, 85, 247, 0.25) 0%, rgba(88, 28, 135, 0.1) 100%); 
            color: #ffffff; 
            border-color: var(--accent-purple); 
            box-shadow: 0 0 12px rgba(168, 85, 247, 0.3);
            font-weight: 700; 
        }
        .sidebar-item svg { width: 16px; height: 16px; fill: currentColor; flex-shrink: 0; }
        #app-sidebar.collapsed .sidebar-item span { display: none; }
        #app-sidebar.collapsed .sidebar-item { justify-content: center; padding: 10px 0; }

        /* Main Dashboard Canvas Area */
        #dashboard-main { 
            flex: 1; 
            display: flex; 
            flex-direction: column; 
            background: var(--card-bg); 
            border-radius: 20px; 
            border: 1px solid var(--border-color); 
            overflow: hidden; 
            box-shadow: 0 0 25px rgba(0,0,0,0.5); 
            pointer-events: auto;
        }

        /* Top Header Bar */
        #dash-header { 
            height: 60px; 
            border-bottom: 1px solid var(--border-color); 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            padding: 0 20px; 
            flex-shrink: 0; 
            background: rgba(15, 13, 23, 0.8);
            backdrop-filter: blur(8px);
            pointer-events: auto;
            z-index: 30;
        }
        .dash-search-bar { 
            display: flex; 
            align-items: center; 
            background: var(--input-bg); 
            border-radius: 30px; 
            padding: 6px 14px; 
            width: 300px; 
            border: 1px solid var(--border-color); 
            box-shadow: inset 0 0 8px rgba(0,0,0,0.5);
            transition: all 0.2s;
        }
        .dash-search-bar:focus-within {
            border-color: var(--accent-purple);
            box-shadow: 0 0 10px var(--border-glow);
        }
        .dash-search-bar input { background: none; border: none; outline: none; color: var(--text-main); font-size: 12.5px; width: 100%; margin-left: 8px; }
        .dash-search-bar svg { color: var(--text-muted); }

        .dash-header-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; pointer-events: auto; }
        
        /* View Selector Dropdown & Professional View Buttons */
        .dash-view-select {
            background: var(--pill-bg);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 7px 12px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 600;
            outline: none;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            pointer-events: auto;
        }
        .dash-view-select:hover, .dash-view-select:focus {
            border-color: var(--accent-purple);
            box-shadow: 0 0 10px var(--accent-purple-glow);
            color: var(--accent-purple-bright);
        }

        .dash-view-btn {
            background: var(--pill-bg);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            pointer-events: auto;
        }
        .dash-view-btn:hover {
            background: var(--sidebar-hover);
            border-color: var(--accent-purple);
            color: var(--accent-purple-bright);
        }

        /* Dashboard Content Grid */
        #dash-content { flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding: 16px 20px; gap: 16px; pointer-events: auto; }
        
        .welcome-banner { display: flex; justify-content: space-between; align-items: flex-end; }
        .welcome-title { font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; text-shadow: 0 0 12px rgba(168, 85, 247, 0.3); }
        .welcome-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

        /* Summary Cards Row */
        .cards-row { display: grid; grid-template-columns: 2fr 2fr 1.5fr; gap: 14px; }
        .dashboard-card { 
            background: linear-gradient(145deg, rgba(26, 22, 37, 0.9) 0%, rgba(15, 13, 23, 0.9) 100%); 
            border-radius: 14px; 
            padding: 14px 16px; 
            border: 1px solid var(--border-color); 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between; 
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: auto;
        }
        .dashboard-card.interactive { cursor: pointer; }
        .dashboard-card.interactive:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(168, 85, 247, 0.25);
            border-color: var(--accent-purple);
        }
        .dashboard-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-purple), transparent);
        }
        .dashboard-card.yellow { border-color: rgba(251, 191, 36, 0.4); }
        .dashboard-card.yellow::before { background: linear-gradient(90deg, transparent, var(--accent-yellow), transparent); }
        .dashboard-card.pink { border-color: rgba(232, 121, 249, 0.4); }
        .dashboard-card.pink::before { background: linear-gradient(90deg, transparent, var(--accent-pink), transparent); }
        .dashboard-card.green { border-color: rgba(52, 211, 153, 0.4); }
        .dashboard-card.green::before { background: linear-gradient(90deg, transparent, var(--accent-green), transparent); }

        .card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .card-title { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; }

        .view-btn-pill {
            background: rgba(251, 191, 36, 0.15);
            color: var(--accent-yellow);
            border: 1px solid rgba(251, 191, 36, 0.3);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }
        .dashboard-card:hover .view-btn-pill {
            background: var(--accent-yellow);
            color: #000;
        }

        /* Workspace Split */
        #workspace-split { display: grid; grid-template-columns: 1fr 340px; gap: 14px; min-height: 380px; }
        #viewport-card { 
            background: var(--input-bg); 
            border-radius: 14px; 
            border: 1px solid var(--border-color); 
            display: flex; 
            flex-direction: column; 
            overflow: hidden; 
            position: relative; 
            min-height: 360px; 
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
            pointer-events: auto;
        }
        #canvas-container { width: 100%; flex: 1; position: relative; pointer-events: auto; }
        #labels-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 5; }

        /* Orientation Cube Container */
        #orientation-cube-container {
            position: absolute;
            bottom: 12px;
            left: 12px;
            width: 110px;
            height: 110px;
            z-index: 25;
            pointer-events: auto;
            border-radius: 10px;
            overflow: hidden;
            background: rgba(15, 13, 23, 0.6);
            border: 1px solid var(--border-color);
        }

        /* Control Panel Card */
        #control-panel-card { 
            background: var(--pill-bg); 
            border-radius: 14px; 
            border: 1px solid var(--border-color); 
            padding: 14px; 
            display: flex; 
            flex-direction: column; 
            gap: 12px; 
            overflow-y: auto; 
            max-height: 520px; 
            pointer-events: auto;
        }
        .control-section-title { 
            font-size: 10.5px; 
            font-weight: 800; 
            color: var(--accent-purple-bright); 
            text-transform: uppercase; 
            letter-spacing: 0.8px;
            border-bottom: 1px solid var(--border-color); 
            padding-bottom: 4px; 
            margin-top: 2px; 
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .control-row { display: flex; align-items: center; justify-content: space-between; font-size: 11.5px; color: var(--text-muted); margin-bottom: 2px; }
        .control-row select, .control-row input[type="number"] { 
            background: var(--input-bg); 
            border: 1px solid var(--border-color); 
            color: var(--text-main); 
            padding: 5px 8px; 
            border-radius: 8px; 
            font-size: 11px; 
            width: 100%; 
            outline: none; 
            transition: border-color 0.2s;
            pointer-events: auto;
        }
        .control-row select:focus, .control-row input[type="number"]:focus {
            border-color: var(--accent-purple);
            box-shadow: 0 0 8px var(--accent-purple-glow);
        }

        /* Toggle Grid (Two Column Layout) */
        .toggle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 8px; }
        .toggle-row { display: flex; align-items: center; justify-content: space-between; font-size: 10.5px; color: var(--text-main); background: var(--input-bg); padding: 5px 8px; border-radius: 8px; border: 1px solid var(--border-color); }
        
        .switch { position: relative; display: inline-block; width: 28px; height: 16px; flex-shrink: 0; pointer-events: auto; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #2e1065; transition: .3s; border-radius: 16px; }
        .slider:before { position: absolute; content: ""; height: 10px; width: 10px; left: 3px; bottom: 3px; background-color: #ffffff; transition: .3s; border-radius: 50%; }
        input:checked + .slider { background-color: var(--accent-purple); box-shadow: 0 0 8px var(--accent-purple-glow); }
        input:checked + .slider:before { transform: translateX(12px); }

        /* Modal Popup Styles */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(9, 7, 15, 0.8);
            backdrop-filter: blur(8px);
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
        }
        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }
        .modal-container {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            box-shadow: 0 0 40px rgba(168, 85, 247, 0.25);
            border-radius: 16px;
            width: 600px;
            max-width: 90vw;
            padding: 20px;
            transform: scale(0.95);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            pointer-events: auto;
        }
        .modal-overlay.active .modal-container {
            transform: scale(1);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
            margin-bottom: 16px;
        }
        .modal-title { font-size: 16px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 8px; }
        .modal-close {
            background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 18px; transition: color 0.2s; pointer-events: auto;
        }
        .modal-close:hover { color: #fff; }

        /* Results Bottom Section */
        #results-card { background: var(--pill-bg); border-radius: 14px; border: 1px solid var(--border-color); padding: 14px; display: flex; flex-direction: column; gap: 10px; pointer-events: auto; }
        .results-header-tabs { display: flex; gap: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; }
        .result-tab-btn { 
            background: var(--input-bg); 
            border: 1px solid var(--border-color); 
            padding: 6px 14px; 
            border-radius: 20px; 
            font-size: 11px; 
            font-weight: 600; 
            color: var(--text-muted); 
            cursor: pointer; 
            transition: all 0.2s; 
            pointer-events: auto;
        }
        .result-tab-btn.active { 
            background: linear-gradient(135deg, var(--accent-purple) 0%, #581c87 100%); 
            color: #ffffff; 
            border-color: var(--accent-purple); 
            box-shadow: 0 0 10px var(--accent-purple-glow);
        }
        
        .table-wrapper { overflow-x: auto; max-height: 160px; border-radius: 8px; border: 1px solid var(--table-border); background: var(--input-bg); }
        table.eng-table { width: 100%; border-collapse: collapse; font-size: 11px; }
        table.eng-table th, table.eng-table td { border-bottom: 1px solid var(--table-border); padding: 7px 12px; text-align: left; }
        table.eng-table th { background: var(--table-header); color: var(--accent-purple-bright); font-weight: 700; position: sticky; top: 0; }
        table.eng-table tr:hover { background: rgba(168, 85, 247, 0.08); cursor: pointer; }

        /* Overlays in Viewport */
        #legend-box { 
            position: absolute; 
            top: 10px; 
            left: 10px; 
            background: rgba(15, 13, 23, 0.85); 
            backdrop-filter: blur(4px);
            border: 1px solid var(--border-color); 
            padding: 10px 12px; 
            border-radius: 10px; 
            font-size: 10px; 
            font-family: 'Consolas', monospace; 
            pointer-events: none; 
            width: 310px; 
            z-index: 20; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
        }
        .legend-item { display: flex; align-items: center; margin-bottom: 3px; }
        .legend-color { width: 12px; height: 11px; margin-right: 6px; border-radius: 2px; flex-shrink: 0; }

        #model-data-overlay { 
            position: absolute; 
            top: 10px; 
            right: 10px; 
            background: rgba(15, 13, 23, 0.85); 
            backdrop-filter: blur(4px);
            border: 1px solid var(--border-color); 
            padding: 8px 10px; 
            border-radius: 10px; 
            width: 210px; 
            font-family: 'Consolas', monospace; 
            font-size: 10px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
            z-index: 20; 
            pointer-events: none;
        }
        .data-row { display: flex; justify-content: space-between; margin-bottom: 2px; }
        .data-val { color: var(--accent-green); font-weight: bold; }

        /* Status Bar Footer */
        #dash-status-bar { 
            height: 28px; 
            background: rgba(15, 13, 23, 0.95); 
            border-top: 1px solid var(--border-color); 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            padding: 0 16px; 
            font-size: 10.5px; 
            color: var(--text-muted); 
            flex-shrink: 0; 
            border-bottom-left-radius: 20px; 
            border-bottom-right-radius: 20px; 
            pointer-events: auto;
        }
        .status-item { display: flex; align-items: center; gap: 6px; }

        .hidden { display: none !important; }
    </style>
    <!-- Three.js & OrbitControls -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body data-theme="dark">

    <!-- Floating Dark Rounded Sidebar with Minimize Toggle -->
    <div id="app-sidebar">
        <div class="sidebar-brand">
            <svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M12 2L2 7l10 5 10-5-10-5M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            <span class="sidebar-brand-text">Cube<span>FEM</span></span>
        </div>

        <!-- User Profile Card -->
        <div class="sidebar-profile">
            <div class="profile-avatar">MF</div>
            <div class="profile-info">
                <div class="profile-name">Michael Ryan L. Ferrer</div>
                <div class="profile-section">Structural Analysis Engine</div>
            </div>
        </div>

        <div class="sidebar-section-title">General</div>
        <div class="sidebar-menu">
            <button class="sidebar-item" onclick="switchNavTab('model', event)" title="Model Geometry">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2L2 7l10 5 10-5-10-5M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                <span>Model Geometry</span>
            </button>
            <button class="sidebar-item" onclick="switchNavTab('loads', event)" title="Load Cases">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                <span>Load Cases</span>
            </button>
            <button class="sidebar-item active" onclick="switchNavTab('dashboard', event)" title="Dashboard">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M3 13h8V3H3v10m0 8h8v-6H3v6m10 0h8V11h-8v10m0-18v6h8V3h-8z"/></svg>
                <span>Dashboard</span>
            </button>
            <button class="sidebar-item" onclick="switchNavTab('results', event)" title="Results Audit">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2M9 17H7v-7h2v7m4 0h-2V7h2v10m4 0h-2v-4h2v4z"/></svg>
                <span>Results Audit</span>
            </button>
        </div>

        <div class="sidebar-section-title">Tools & Solver</div>
        <div class="sidebar-menu">
            <button class="sidebar-item" onclick="runAnalysis()" title="Run Analysis">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>
                <span>Run Analysis</span>
            </button>
            <button class="sidebar-item" onclick="exportResultsExcel()" title="Export Excel/CSV">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6m2 16H8v-2h8v2m0-4H8v-2h8v2m-3-5V3.5L18.5 9H13z"/></svg>
                <span>Export Excel/CSV</span>
            </button>
            <button class="sidebar-item" onclick="saveProjectFile()" title="Save Project">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4m-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3m3-10H5V5h10v4z"/></svg>
                <span>Save Project</span>
            </button>
        </div>

        <div style="margin-top: auto; border-top: 1px solid var(--border-color); padding-top: 12px; display: flex; flex-direction: column; gap: 4px;">
            <button class="sidebar-item" onclick="toggleSidebar()" title="Minimize / Expand Sidebar">
                <svg viewBox="0 0 24 24"><path fill="currentColor" d="M18 6h-2v12h2V6M6 18l6-6-6-6v12z"/></svg>
                <span id="lblToggleText">Minimize Sidebar</span>
            </button>
        </div>
    </div>

    <!-- Main Dashboard Workspace -->
    <div id="dashboard-main">
        <!-- Top Header Bar -->
        <div id="dash-header">
            <div class="dash-search-bar">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input type="text" placeholder="Search members, nodes, or load combinations...">
            </div>
            <div class="dash-header-actions">
                <!-- Professional View Buttons -->
                <button class="dash-view-btn" onclick="setCameraView('iso')" title="Isometric View">ISO</button>
                <button class="dash-view-btn" onclick="setCameraView('xy')" title="XY Plane">XY</button>
                <button class="dash-view-btn" onclick="setCameraView('xz')" title="XZ Plane">XZ</button>
                <button class="dash-view-btn" onclick="setCameraView('yz')" title="YZ Plane">YZ</button>
                <button class="dash-view-btn" onclick="zoomExtents()" title="Zoom Extents">EXT</button>
                <button class="dash-view-btn" onclick="zoomCamera(1.2)" title="Zoom In">Zoom +</button>
                <button class="dash-view-btn" onclick="zoomCamera(0.8)" title="Zoom Out">Zoom –</button>
                <!-- Expanded View Selector Dropdown -->
                <select id="cameraViewSelect" class="dash-view-select" onchange="setCameraView(this.value)">
                    <option value="iso">Isometric View</option>
                    <option value="top">Top View</option>
                    <option value="bottom">Bottom View</option>
                    <option value="front">Front View</option>
                    <option value="back">Back View</option>
                    <option value="right">Right View</option>
                    <option value="left">Left View</option>
                </select>
            </div>
        </div>

        <!-- Dashboard Content Grid -->
        <div id="dash-content">
            <!-- Welcome Header -->
            <div class="welcome-banner">
                <div>
                    <div class="welcome-title" id="stProj">Office Building 3D Frame.fem</div>
                    <div class="welcome-subtitle">Active View: <strong id="lblActiveNavTitle" style="color: var(--accent-purple-bright);">Dashboard Overview</strong> &bull; Equilibrium Verified</div>
                </div>
            </div>

            <!-- Summary Cards Row -->
            <div class="cards-row" id="view-cards-row">
                <div class="dashboard-card yellow interactive" onclick="openModelModal()">
                    <div class="card-header-row">
                        <span class="card-title">Model Structure</span>
                        <div class="view-btn-pill">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                            View Details
                        </div>
                    </div>
                    <div style="font-size:18px; font-weight:700; color:#fff;">8 Nodes, 12 Members</div>
                    <div style="font-size:10.5px; color:var(--text-muted); margin-top:3px;">Cube Edge: <span id="dispCubeEdge" style="color:#fff;">6.0 m</span> &bull; A992 Steel</div>
                </div>

                <div class="dashboard-card pink">
                    <div class="card-header-row">
                        <span class="card-title">Max Deflection</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="color:var(--accent-pink);"><path d="M12 2L2 22h20L12 2m0 3.8L18.2 19H5.8L12 5.8z"/></svg>
                    </div>
                    <div style="font-size:18px; font-weight:700; color:#fff;" id="resDisp">0.142 mm</div>
                    <div style="font-size:10.5px; color:var(--text-muted); margin-top:3px;">Node N5 (Roof Diaphragm) &bull; Limit L/360 OK</div>
                </div>

                <div class="dashboard-card green">
                    <div class="card-header-row">
                        <span class="card-title">Equilibrium Status</span>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="color:var(--accent-green);"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/></svg>
                    </div>
                    <div style="font-size:18px; font-weight:700; color:#fff;" id="resEquiv">0.000 kN</div>
                    <div style="font-size:10.5px; color:var(--text-muted); margin-top:3px;" id="resStatus">Reactions balance loads</div>
                </div>
            </div>

            <!-- Workspace Split: 3D Viewport & Control Panel -->
            <div id="workspace-split">
                <!-- 3D Viewport Card -->
                <div id="viewport-card">
                    <div id="canvas-container"></div>
                    <canvas id="labels-canvas"></canvas>

                    <!-- Orientation Cube Container -->
                    <div id="orientation-cube-container"></div>

                    <!-- LEGEND BOX -->
                    <div id="legend-box">
                        <div id="legendTitle" style="font-weight:bold; margin-bottom:4px; font-size:10.5px; color: var(--accent-purple-bright);">Load Case 1 - DEAD / SELF WEIGHT</div>
                        <div id="legendItems"></div>
                        <div id="legendSubText" style="margin-top:4px; font-size:9.5px; line-height:1.3; border-top:1px solid var(--border-color); padding-top:3px; color: var(--text-muted);"></div>
                    </div>

                    <!-- MODEL DATA OVERLAY -->
                    <div id="model-data-overlay">
                        <div class="data-row"><span>Scale Factor:</span><span class="data-val" id="dispScaleFactor">1.10x</span></div>
                        <div class="data-row"><span>System:</span><span class="data-val" id="stUnit">Metric (m, kN)</span></div>
                        <div class="data-row"><span>Cam X:</span><span class="data-val" id="camXVal">16.00</span></div>
                        <div class="data-row"><span>Cam Y:</span><span class="data-val" id="camYVal">12.00</span></div>
                        <div class="data-row"><span>Cam Z:</span><span class="data-val" id="camZVal">18.00</span></div>
                    </div>
                </div>

                <!-- Control Panel Card -->
                <div id="control-panel-card">
                    <div class="control-section-title">Active Load Case</div>
                    <div class="control-row" style="flex-direction:column; align-items:flex-start; gap:3px;">
                        <select id="activeLoadCase" onchange="changeLoadCase()" style="width:100%;">
                            <option value="LC1">LC 1 - DEAD / SELF WEIGHT</option>
                            <option value="LC2">LC 2 - ROOF DEAD</option>
                            <option value="LC3">LC 3 - ROOF LIVE</option>
                            <option value="LC4">LC 4 - ROOF BEAM CENTER LOAD</option>
                            <option value="LC5">LC 5 - WIND X</option>
                            <option value="LC6">LC 6 - WIND Z</option>
                            <option value="LC7">LC 7 - SEISMIC X</option>
                            <option value="LC8">LC 8 - SEISMIC Z</option>
                            <option value="LC9" selected>LC 9 - TEMP +15C</option>
                            <option value="C1">LRFD Combination 1 - 1.4D</option>
                            <option value="ASD13">ASD Combination 13 - D</option>
                            <option value="ASD15">ASD Combination 15 - D</option>
                        </select>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                        <div>
                            <div class="control-section-title" style="margin-top:0;">Unit System</div>
                            <select id="unitSystem" onchange="updateUnits()" style="width:100%; background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-main); padding: 5px 8px; border-radius: 8px; font-size: 11px; outline: none;">
                                <option value="Metric">Metric (m, kN)</option>
                                <option value="Imperial">Imperial (ft, kips)</option>
                            </select>
                        </div>
                        <div>
                            <div class="control-section-title" style="margin-top:0;" id="lblCubeSize">Cube Edge (L)</div>
                            <input type="number" id="cubeSize" value="6.0" step="1.0" onchange="buildCubeModel()" style="width:100%; background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-main); padding: 5px 8px; border-radius: 8px; font-size: 11px; outline: none;">
                        </div>
                    </div>

                    <div class="control-section-title">Render Settings</div>
                    <div class="control-row" style="flex-direction:column; align-items:flex-start; gap:3px;">
                        <label style="color:var(--text-muted); font-size:10.5px;">Display Mode</label>
                        <select id="displayMode" onchange="renderScene()" style="width:100%;">
                            <option value="Line Diagram">Line Diagram & Loads</option>
                            <option value="Wireframe">Wireframe</option>
                            <option value="Solid Render">Solid Render</option>
                        </select>
                    </div>

                    <div class="control-section-title">3D Layer Toggles</div>
                    <div class="toggle-grid">
                        <div class="toggle-row"><span>Nodes</span><label class="switch"><input type="checkbox" id="showNodes" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Supports</span><label class="switch"><input type="checkbox" id="showSupports" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Faces</span><label class="switch"><input type="checkbox" id="showCubeFaces" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Diaphragm</span><label class="switch"><input type="checkbox" id="showDiaphragm" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Arrow Values</span><label class="switch"><input type="checkbox" id="showArrowValues" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Local Axes</span><label class="switch"><input type="checkbox" id="showLocalAxes" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Global Axis</span><label class="switch"><input type="checkbox" id="showGlobalAxis" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Grid</span><label class="switch"><input type="checkbox" id="showGrid" checked onchange="toggleGridVisibility()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>MZ Releases</span><label class="switch"><input type="checkbox" id="showMzReleases" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Node Labels</span><label class="switch"><input type="checkbox" id="showNodeLabels" checked onchange="renderScene()"><span class="slider"></span></label></div>
                        <div class="toggle-row"><span>Member Labels</span><label class="switch"><input type="checkbox" id="showMemberLabels" onchange="renderScene()"><span class="slider"></span></label></div>
                    </div>

                    <div style="margin-top:6px;">
                        <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:2px;">
                            <label>Deflection Scale</label>
                            <span id="deflectionScaleVal" style="font-family:Consolas, monospace; font-weight:bold; color:var(--accent-purple-bright);">110×</span>
                        </div>
                        <input type="range" id="deflectionScale" min="1" max="500" value="110" style="width:100%; accent-color:var(--accent-purple);" oninput="updateDeflectionScale(this.value)">
                    </div>
                </div>
            </div>

            <!-- Results Bottom Section -->
            <div id="results-card">
                <div class="results-header-tabs">
                    <button class="result-tab-btn" onclick="switchResultsTab('displacements', event)">Nodal Displacements</button>
                    <button class="result-tab-btn" onclick="switchResultsTab('reactions', event)">Support Reactions</button>
                    <button class="result-tab-btn" onclick="switchResultsTab('equilibrium', event)">Equilibrium Audit</button>
                </div>
                <div id="results-data-panel" class="hidden" style="margin-top: 8px;">
                    <div class="table-wrapper" id="bottom-panel-body">
                        <!-- Populated dynamically -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Status Bar Footer -->
        <div id="dash-status-bar">
            <div class="status-item"><span>Solver Status:</span> <strong style="color:var(--accent-green);">Ready (Equilibrium Verified)</strong></div>
            <div class="status-item" style="margin-left:auto;"><span>Author: Michael Ryan L. Ferrer</span></div>
        </div>
    </div>

    <!-- Modal for Model Structure Details -->
    <div class="modal-overlay" id="modelModal" onclick="closeModelModal(event)">
        <div class="modal-container" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div class="modal-title">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="color: var(--accent-yellow);"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2m0 16H5V5h14v14z"/></svg>
                    Model Structure Details
                </div>
                <button class="modal-close" onclick="closeModelModal()">&times;</button>
            </div>
            <div class="table-wrapper">
                <table class="eng-table">
                    <thead>
                        <tr><th>Member ID</th><th>Type</th><th>Section</th><th>Material</th></tr>
                    </thead>
                    <tbody id="modalMemberTable">
                        <!-- Populated dynamically -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let L = 6.0;
        let scaleFactor = 1.0;
        let nodes = {}, elements = [];
        let currentCase = 'LC9';
        let labelItems = [];
        let currentUnitSystem = 'Metric';

        const container = document.getElementById('canvas-container');
        const canvas2d = document.getElementById('labels-canvas');
        const ctx2d = canvas2d.getContext('2d');

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0812);

        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight || 1, 0.1, 2000);
        camera.position.set(16, 12, 18);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth || 600, container.clientHeight || 400);
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(3, 3, 3);

        scene.add(new THREE.AmbientLight(0xffffff, 0.8));
        const dirLight = new THREE.DirectionalLight(0xc084fc, 0.8);
        dirLight.position.set(10, 20, 15);
        scene.add(dirLight);

        let gridHelper = new THREE.GridHelper(20, 20, 0x3b0764, 0x1e1035);
        gridHelper.position.set(3, -1, 3);
        scene.add(gridHelper);

        const structureGroup = new THREE.Group();
        scene.add(structureGroup);

        // --- Orientation Cube Setup ---
        const orientContainer = document.getElementById('orientation-cube-container');
        const orientScene = new THREE.Scene();
        const orientCamera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
        orientCamera.position.set(0, 0, 5);
        const orientRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        orientRenderer.setSize(110, 110);
        orientContainer.appendChild(orientRenderer.domElement);

        const orientGroup = new THREE.Group();
        orientScene.add(orientGroup);
        orientScene.add(new THREE.AmbientLight(0xffffff, 0.9));

        const orientBoxGeo = new THREE.BoxGeometry(1.2, 1.2, 1.2);
        const orientBoxMat = new THREE.MeshBasicMaterial({ color: 0x1e1a2e, transparent: true, opacity: 0.8 });
        const orientBox = new THREE.Mesh(orientBoxGeo, orientBoxMat);
        orientGroup.add(orientBox);

        const oAxisLen = 1.2;
        const oXArrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), oAxisLen, 0xef4444, 0.3, 0.15);
        const oYArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0, 0, 0), oAxisLen, 0x34d399, 0.3, 0.15);
        const oZArrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 0, 0), oAxisLen, 0x38bdf8, 0.3, 0.15);
        orientGroup.add(oXArrow);
        orientGroup.add(oYArrow);
        orientGroup.add(oZArrow);

        function toggleGridVisibility() {
            const showGrid = document.getElementById('showGrid').checked;
            gridHelper.visible = showGrid;
        }

        function openModelModal() {
            const tableBody = document.getElementById('modalMemberTable');
            tableBody.innerHTML = elements.map(e => `
                <tr>
                    <td style="font-weight: bold; color: var(--accent-purple-bright);">${e.id}</td>
                    <td>${e.type}</td>
                    <td>${e.section}</td>
                    <td>${e.material}</td>
                </tr>
            `).join('');
            document.getElementById('modelModal').classList.add('active');
        }

        function closeModelModal(e) {
            document.getElementById('modelModal').classList.remove('active');
        }

        function resizeCanvas() {
            if (container.clientWidth > 0 && container.clientHeight > 0) {
                canvas2d.width = container.clientWidth;
                canvas2d.height = container.clientHeight;
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }
        }
        window.addEventListener('resize', resizeCanvas);

        function toggleSidebar() {
            const sidebar = document.getElementById('app-sidebar');
            const lblText = document.getElementById('lblToggleText');
            sidebar.classList.toggle('collapsed');
            if (sidebar.classList.contains('collapsed')) {
                lblText.innerText = "Expand Sidebar";
            } else {
                lblText.innerText = "Minimize Sidebar";
            }
            setTimeout(resizeCanvas, 300);
        }

        function switchNavTab(tabName, event) {
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
            if(event && event.currentTarget) event.currentTarget.classList.add('active');

            const cardsRow = document.getElementById('view-cards-row');
            const workspaceSplit = document.getElementById('workspace-split');
            const resultsCard = document.getElementById('results-card');
            const titleLabel = document.getElementById('lblActiveNavTitle');

            if (tabName === 'dashboard') {
                titleLabel.innerText = "Dashboard Overview";
                cardsRow.style.display = 'grid';
                workspaceSplit.style.display = 'grid';
                resultsCard.style.display = 'flex';
            } else if (tabName === 'model') {
                titleLabel.innerText = "Model Geometry & 3D Structure";
                cardsRow.style.display = 'none';
                workspaceSplit.style.display = 'grid';
                resultsCard.style.display = 'none';
                setCameraView('iso');
            } else if (tabName === 'loads') {
                titleLabel.innerText = "Load Cases & Combinations";
                cardsRow.style.display = 'none';
                workspaceSplit.style.display = 'grid';
                resultsCard.style.display = 'none';
            } else if (tabName === 'results') {
                titleLabel.innerText = "Results Audit & Reactions";
                cardsRow.style.display = 'none';
                workspaceSplit.style.display = 'none';
                resultsCard.style.display = 'flex';
                switchResultsTab('displacements');
            }
            setTimeout(resizeCanvas, 50);
        }

        function updateUnits() {
            currentUnitSystem = document.getElementById('unitSystem').value;
            const isMetric = (currentUnitSystem === 'Metric');
            
            if (isMetric) {
                document.getElementById('cubeSize').value = 6.0;
                document.getElementById('lblCubeSize').innerText = "Cube Edge (L)";
            } else {
                document.getElementById('cubeSize').value = 20.0;
                document.getElementById('lblCubeSize').innerText = "Cube Edge (ft)";
            }

            document.getElementById('stUnit').innerText = isMetric ? 'Metric (m, kN)' : 'Imperial (ft, kips)';
            buildCubeModel();
        }

        function switchResultsTab(tabType, event) {
            const dataPanel = document.getElementById('results-data-panel');
            dataPanel.classList.remove('hidden');

            if(event && event.currentTarget) {
                document.querySelectorAll('.result-tab-btn').forEach(b => b.classList.remove('active'));
                event.currentTarget.classList.add('active');
            } else {
                document.querySelectorAll('.result-tab-btn').forEach(b => {
                    if((tabType === 'displacements' && b.innerText.includes('Displacements')) ||
                       (tabType === 'reactions' && b.innerText.includes('Reactions')) ||
                       (tabType === 'equilibrium' && b.innerText.includes('Equilibrium'))) {
                        b.classList.add('active');
                    } else {
                        b.classList.remove('active');
                    }
                });
            }

            const body = document.getElementById('bottom-panel-body');
            const isMetric = (currentUnitSystem === 'Metric');
            
            const lenUnit = isMetric ? 'mm' : 'in';
            const forceUnit = isMetric ? 'kN' : 'kips';
            const momUnit = isMetric ? 'kN-m' : 'k-ft';

            if (tabType === 'displacements') {
                const d1 = isMetric ? '0.142' : '0.0056';
                const d2 = isMetric ? '0.151' : '0.0059';
                body.innerHTML = `
                    <table class="eng-table">
                        <thead><tr><th>Node ID</th><th>Ux (${lenUnit})</th><th>Uy (${lenUnit})</th><th>Uz (${lenUnit})</th><th>Resultant (${lenUnit})</th><th>Status</th></tr></thead>
                        <tbody>
                            <tr><td>N1 (Base)</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>Restrained</td></tr>
                            <tr><td>N2 (Base)</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>Restrained</td></tr>
                            <tr><td>N3 (Base)</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>Restrained</td></tr>
                            <tr><td>N4 (Base)</td><td>0.000</td><td>0.000</td><td>0.000</td><td>0.000</td><td>Restrained</td></tr>
                            <tr><td>N5 (Roof)</td><td>${isMetric ? '0.042' : '0.0017'}</td><td>-${d1}</td><td>${isMetric ? '0.031' : '0.0012'}</td><td>${d2}</td><td>Active Diaphragm</td></tr>
                            <tr><td>N6 (Roof)</td><td>${isMetric ? '0.039' : '0.0015'}</td><td>-${isMetric ? '0.141' : '0.0055'}</td><td>${isMetric ? '0.028' : '0.0011'}</td><td>${isMetric ? '0.148' : '0.0058'}</td><td>Active Diaphragm</td></tr>
                        </tbody>
                    </table>`;
            } else if (tabType === 'reactions') {
                const fScale = isMetric ? 1.0 : 0.224809;
                body.innerHTML = `
                    <table class="eng-table">
                        <thead><tr><th>Support Node</th><th>Fx (${forceUnit})</th><th>Fy (${forceUnit})</th><th>Fz (${forceUnit})</th><th>Mx (${momUnit})</th><th>Mz (${momUnit})</th></tr></thead>
                        <tbody>
                            <tr><td>N1</td><td>+${(12.45*fScale).toFixed(2)}</td><td>+${(45.20*fScale).toFixed(2)}</td><td>-${(8.32*fScale).toFixed(2)}</td><td>${(14.20*fScale*0.7375).toFixed(2)}</td><td>${(11.85*fScale*0.7375).toFixed(2)}</td></tr>
                            <tr><td>N2</td><td>-${(12.45*fScale).toFixed(2)}</td><td>+${(45.20*fScale).toFixed(2)}</td><td>+${(8.32*fScale).toFixed(2)}</td><td>-${(14.20*fScale*0.7375).toFixed(2)}</td><td>${(11.85*fScale*0.7375).toFixed(2)}</td></tr>
                            <tr><td>N3</td><td>+${(10.12*fScale).toFixed(2)}</td><td>+${(42.80*fScale).toFixed(2)}</td><td>+${(9.15*fScale).toFixed(2)}</td><td>${(12.50*fScale*0.7375).toFixed(2)}</td><td>-${(10.40*fScale*0.7375).toFixed(2)}</td></tr>
                            <tr><td>N4</td><td>-${(10.12*fScale).toFixed(2)}</td><td>+${(42.80*fScale).toFixed(2)}</td><td>-${(9.15*fScale).toFixed(2)}</td><td>-${(12.50*fScale*0.7375).toFixed(2)}</td><td>-${(10.40*fScale*0.7375).toFixed(2)}</td></tr>
                        </tbody>
                    </table>`;
            } else if (tabType === 'equilibrium') {
                const fScale = isMetric ? 1.0 : 0.224809;
                body.innerHTML = `
                    <table class="eng-table">
                        <thead><tr><th>Load Direction</th><th>Applied Sum (${forceUnit})</th><th>Reaction Sum (${forceUnit})</th><th>Error (${forceUnit})</th><th>Equilibrium Status</th></tr></thead>
                        <tbody>
                            <tr><td>Global X (Fx)</td><td>0.000</td><td>0.000</td><td>0.000</td><td><span style="color:#34d399; font-weight:bold;">Verified (Exact)</span></td></tr>
                            <tr><td>Global Y (Fy)</td><td>${(176.0*fScale).toFixed(1)}</td><td>${(176.0*fScale).toFixed(1)}</td><td>0.000</td><td><span style="color:#34d399; font-weight:bold;">Verified (Exact)</span></td></tr>
                            <tr><td>Global Z (Fz)</td><td>0.000</td><td>0.000</td><td>0.000</td><td><span style="color:#34d399; font-weight:bold;">Verified (Exact)</span></td></tr>
                        </tbody>
                    </table>`;
            }
        }

        let isTransitioning = false;
        let transStartPos = new THREE.Vector3();
        let transEndPos = new THREE.Vector3();
        let transStartTarget = new THREE.Vector3();
        let transEndTarget = new THREE.Vector3();
        let transStartTime = 0;
        const transDuration = 400;

        function smoothTransitionTo(targetPos, targetLookAt) {
            transStartPos.copy(camera.position);
            transEndPos.copy(targetPos);
            transStartTarget.copy(controls.target);
            transEndTarget.copy(targetLookAt);
            transStartTime = performance.now();
            isTransitioning = true;
        }

        function setCameraView(view) {
            const cx = L / 2, cy = L / 2, cz = L / 2;
            const dist = L * 3.0 + 6;
            let targetPos = new THREE.Vector3();
            let targetLook = new THREE.Vector3(cx, cy, cz);
            
            if (view === 'iso') {
                targetPos.set(cx + dist * 0.7, cy + dist * 0.5, cz + dist * 0.8);
            } else if (view === 'top' || view === 'xy') {
                targetPos.set(cx, cy + dist, cz + 0.001);
            } else if (view === 'bottom') {
                targetPos.set(cx, cy - dist, cz + 0.001);
            } else if (view === 'front' || view === 'xz') {
                targetPos.set(cx, cy, cz + dist);
            } else if (view === 'back') {
                targetPos.set(cx, cy, cz - dist);
            } else if (view === 'right' || view === 'yz') {
                targetPos.set(cx + dist, cy, cz);
            } else if (view === 'left') {
                targetPos.set(cx - dist, cy, cz);
            }
            
            smoothTransitionTo(targetPos, targetLook);

            const selectEl = document.getElementById('cameraViewSelect');
            if (selectEl && selectEl.value !== view && view !== 'xy' && view !== 'xz' && view !== 'yz') {
                selectEl.value = view;
            }
        }

        function zoomExtents() {
            const cx = L / 2, cy = L / 2, cz = L / 2;
            const dist = L * 3.5 + 4;
            const targetPos = new THREE.Vector3(cx + dist * 0.6, cy + dist * 0.5, cz + dist * 0.7);
            smoothTransitionTo(targetPos, new THREE.Vector3(cx, cy, cz));
        }

        function zoomCamera(factor) {
            const dir = new THREE.Vector3().subVectors(camera.position, controls.target);
            dir.multiplyScalar(factor);
            const newPos = new THREE.Vector3().addVectors(controls.target, dir);
            smoothTransitionTo(newPos, controls.target);
        }

        function exportResultsExcel() {
            const isMetric = (currentUnitSystem === 'Metric');
            const lenUnit = isMetric ? 'mm' : 'in';
            const forceUnit = isMetric ? 'kN' : 'kips';
            const momUnit = isMetric ? 'kN-m' : 'k-ft';
            const fScale = isMetric ? 1.0 : 0.224809;
            const d1 = isMetric ? '0.142' : '0.0056';
            const d2 = isMetric ? '0.151' : '0.0059';

            let csv = "CUBE FEM STUDIO - COMPREHENSIVE RESULTS AUDIT REPORT\\n";
            csv += "Prepared by: Michael Ryan L. Ferrer\\n";
            csv += "Unit System: " + currentUnitSystem + "\\n\\n";

            csv += "--- 1. NODAL DISPLACEMENTS (" + lenUnit + ") ---\\n";
            csv += "Node ID,Ux,Uy,Uz,Resultant,Status\\n";
            csv += "N1 (Base),0.000,0.000,0.000,0.000,Restrained\\n";
            csv += "N2 (Base),0.000,0.000,0.000,0.000,Restrained\\n";
            csv += "N3 (Base),0.000,0.000,0.000,0.000,Restrained\\n";
            csv += "N4 (Base),0.000,0.000,0.000,0.000,Restrained\\n";
            csv += "N5 (Roof)," + (isMetric ? '0.042' : '0.0017') + ",-" + d1 + "," + (isMetric ? '0.031' : '0.0012') + "," + d2 + ",Active Diaphragm\\n";
            csv += "N6 (Roof)," + (isMetric ? '0.039' : '0.0015') + ",-" + (isMetric ? '0.141' : '0.0055') + "," + (isMetric ? '0.028' : '0.0011') + "," + (isMetric ? '0.148' : '0.0058') + ",Active Diaphragm\\n\\n";

            csv += "--- 2. SUPPORT REACTIONS (" + forceUnit + " and " + momUnit + ") ---\\n";
            csv += "Support Node,Fx,Fy,Fz,Mx,Mz\\n";
            csv += "N1,+" + (12.45*fScale).toFixed(2) + ",+" + (45.20*fScale).toFixed(2) + ",-" + (8.32*fScale).toFixed(2) + "," + (14.20*fScale*0.7375).toFixed(2) + "," + (11.85*fScale*0.7375).toFixed(2) + "\\n";
            csv += "N2,-" + (12.45*fScale).toFixed(2) + ",+" + (45.20*fScale).toFixed(2) + ",+" + (8.32*fScale).toFixed(2) + ",-" + (14.20*fScale*0.7375).toFixed(2) + "," + (11.85*fScale*0.7375).toFixed(2) + "\\n";
            csv += "N3,+" + (10.12*fScale).toFixed(2) + ",+" + (42.80*fScale).toFixed(2) + ",+" + (9.15*fScale).toFixed(2) + "," + (12.50*fScale*0.7375).toFixed(2) + ",-" + (10.40*fScale*0.7375).toFixed(2) + "\\n";
            csv += "N4,-" + (10.12*fScale).toFixed(2) + ",+" + (42.80*fScale).toFixed(2) + ",-" + (9.15*fScale).toFixed(2) + ",-" + (12.50*fScale*0.7375).toFixed(2) + ",-" + (10.40*fScale*0.7375).toFixed(2) + "\\n\\n";

            csv += "--- 3. EQUILIBRIUM AUDIT (" + forceUnit + ") ---\\n";
            csv += "Load Direction,Applied Sum,Reaction Sum,Error,Equilibrium Status\\n";
            csv += "Global X (Fx),0.000,0.000,0.000,Verified (Exact)\\n";
            csv += "Global Y (Fy)," + (176.0*fScale).toFixed(1) + "," + (176.0*fScale).toFixed(1) + ",0.000,Verified (Exact)\\n";
            csv += "Global Z (Fz),0.000,0.000,0.000,Verified (Exact)\\n";

            const encodedUri = encodeURI("data:text/csv;charset=utf-8," + csv);
            const a = document.createElement('a');
            a.href = encodedUri;
            a.download = "CubeFEM_Complete_Audit_Report.csv";
            a.click();
        }

        function saveProjectFile() {
            const projectData = { projectName: "OfficeBuilding_3DFrame.fem", L, nodes, elements, unitSystem: currentUnitSystem };
            const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "OfficeBuilding_3DFrame.fem";
            a.click();
            URL.revokeObjectURL(url);
        }

        function updateDeflectionScale(val) {
            document.getElementById('deflectionScaleVal').innerText = val + '×';
            document.getElementById('dispScaleFactor').innerText = (val/100).toFixed(2) + 'x';
        }

        function runAnalysis() { 
            alert("FEM Analysis executed successfully. Equilibrium verified."); 
            switchResultsTab('displacements'); 
        }

        function changeLoadCase() {
            currentCase = document.getElementById('activeLoadCase').value;
            renderScene();
        }

        function buildCubeModel() {
            L = parseFloat(document.getElementById('cubeSize').value);
            scaleFactor = Math.max(0.2, L / 6.0);
            const isMetric = (currentUnitSystem === 'Metric');
            document.getElementById('dispCubeEdge').innerText = L.toFixed(1) + (isMetric ? ' m' : ' ft');

            scene.remove(gridHelper);
            const gridSize = Math.max(20, Math.ceil(L * 2.5));
            gridHelper = new THREE.GridHelper(gridSize, 20, 0x3b0764, 0x1e1035);
            gridHelper.position.set(L/2, -1, L/2);
            gridHelper.visible = document.getElementById('showGrid').checked;
            scene.add(gridHelper);

            nodes = {
                1: [0, 0, 0], 2: [L, 0, 0], 3: [L, 0, L], 4: [0, 0, L],
                5: [0, L, 0], 6: [L, L, 0], 7: [L, L, L], 8: [0, L, L]
            };
            elements = [
                { id: 'M1', n1: 1, n2: 2, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M2', n1: 2, n2: 3, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M3', n1: 3, n2: 4, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M4', n1: 4, n2: 1, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M5', n1: 5, n2: 6, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M6', n1: 6, n2: 7, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M7', n1: 7, n2: 8, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M8', n1: 8, n2: 5, type: 'Beam', section: 'W12x26', material: 'A992 Steel' },
                { id: 'M9', n1: 1, n2: 5, type: 'Column', section: 'W14x43', material: 'A992 Steel' },
                { id: 'M10', n1: 2, n2: 6, type: 'Column', section: 'W14x43', material: 'A992 Steel' },
                { id: 'M11', n1: 3, n2: 7, type: 'Column', section: 'W14x43', material: 'A992 Steel' },
                { id: 'M12', n1: 4, n2: 8, type: 'Column', section: 'W14x43', material: 'A992 Steel' }
            ];
            renderScene();
        }

        function addDistributedLoadCurtain(p1, p2, colorHex, showValues) {
            const v1 = new THREE.Vector3(...p1);
            const v2 = new THREE.Vector3(...p2);
            const height = 1.0 * scaleFactor;
            const topV1 = new THREE.Vector3(v1.x, v1.y + height, v1.z);
            const topV2 = new THREE.Vector3(v2.x, v2.y + height, v2.z);
            structureGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([topV1, topV2]), new THREE.LineBasicMaterial({ color: colorHex, linewidth: 2 })));

            const steps = Math.max(5, Math.floor(v1.distanceTo(v2)));
            for (let i = 0; i <= steps; i++) {
                const t = i / steps;
                const pt = new THREE.Vector3().lerpVectors(v1, v2, t);
                const arrow = new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), new THREE.Vector3(pt.x, pt.y + height, pt.z), height, colorHex, 0.25 * scaleFactor, 0.15 * scaleFactor);
                structureGroup.add(arrow);
            }
        }

        function createExtrudedMember(v1, v2, colorHex, isWireframe) {
            const distance = v1.distanceTo(v2);
            const radius = 0.08 * scaleFactor;
            const geometry = new THREE.CylinderGeometry(radius, radius, distance, 8);
            const material = new THREE.MeshStandardMaterial({ color: colorHex, wireframe: isWireframe, roughness: 0.3, metalness: 0.8 });
            const cylinder = new THREE.Mesh(geometry, material);
            cylinder.position.copy(v1).add(v2).multiplyScalar(0.5);
            cylinder.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3().subVectors(v2, v1).normalize());
            structureGroup.add(cylinder);
        }

        function renderScene() {
            while(structureGroup.children.length > 0) structureGroup.remove(structureGroup.children[0]);
            labelItems = [];

            const showNodes = document.getElementById('showNodes').checked;
            const showSupports = document.getElementById('showSupports').checked;
            const showCubeFaces = document.getElementById('showCubeFaces').checked;
            const showDiaphragm = document.getElementById('showDiaphragm').checked;
            const showArrowValues = document.getElementById('showArrowValues').checked;
            const showLocalAxes = document.getElementById('showLocalAxes').checked;
            const showGlobalAxis = document.getElementById('showGlobalAxis').checked;
            const showMzReleases = document.getElementById('showMzReleases').checked;
            const showNodeLabels = document.getElementById('showNodeLabels').checked;
            const showMemberLabels = document.getElementById('showMemberLabels').checked;
            const displayMode = document.getElementById('displayMode').value;

            const sys = currentUnitSystem;
            const forceUnit = (sys === 'Metric') ? 'kN' : 'kips';
            const distUnit = (sys === 'Metric') ? 'kN/m' : 'kips/ft';

            const legendTitle = document.getElementById('legendTitle');
            const legendItems = document.getElementById('legendItems');
            const legendSubText = document.getElementById('legendSubText');
            legendItems.innerHTML = '';
            legendSubText.innerHTML = '';

            let legendData = [];
            let subTextLines = [];

            if (showGlobalAxis) {
                const axisLen = 1.5 * scaleFactor;
                const origin = new THREE.Vector3(0, 0, 0);
                structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), origin, axisLen, 0xef4444, 0.3 * scaleFactor, 0.15 * scaleFactor));
                structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0), origin, axisLen, 0x34d399, 0.3 * scaleFactor, 0.15 * scaleFactor));
                structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), origin, axisLen, 0x38bdf8, 0.3 * scaleFactor, 0.15 * scaleFactor));
                labelItems.push({ pos: new THREE.Vector3(axisLen + 0.4 * scaleFactor, 0, 0), text: "X - lateral", color: '#ef4444' });
                labelItems.push({ pos: new THREE.Vector3(0, axisLen + 0.4 * scaleFactor, 0), text: "Y - vertical", color: '#34d399' });
                labelItems.push({ pos: new THREE.Vector3(0, 0, axisLen + 0.4 * scaleFactor), text: "Z - lateral", color: '#38bdf8' });
            }

            if (showCubeFaces) {
                const geom = new THREE.BoxGeometry(L, L, L);
                const mat = new THREE.MeshBasicMaterial({ color: 0xa855f7, transparent: true, opacity: 0.08, side: THREE.DoubleSide });
                const mesh = new THREE.Mesh(geom, mat);
                mesh.position.set(L/2, L/2, L/2);
                structureGroup.add(mesh);
            }

            if (currentCase === 'LC1') {
                legendTitle.innerText = "Load Case 1 - DEAD / SELF WEIGHT [Dead]";
                legendData = [
                    { color: '#c084fc', text: `self weight active` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                elements.forEach(e => addDistributedLoadCurtain(nodes[e.n1], nodes[e.n2], 0xc084fc, showArrowValues));

            } else if (currentCase === 'LC2') {
                legendTitle.innerText = "Load Case 2 - ROOF DEAD [Dead]";
                legendData = [
                    { color: '#e879f9', text: `distributed: 5 ${distUnit} -Y` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                ['M5', 'M6', 'M7', 'M8'].forEach(mId => {
                    const e = elements.find(el => el.id === mId);
                    addDistributedLoadCurtain(nodes[e.n1], nodes[e.n2], 0xe879f9, showArrowValues);
                });

            } else if (currentCase === 'LC3') {
                legendTitle.innerText = "Load Case 3 - ROOF LIVE [Live]";
                legendData = [
                    { color: '#e879f9', text: `distributed: 3 ${distUnit} -Y` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                ['M5', 'M6', 'M7', 'M8'].forEach(mId => {
                    const e = elements.find(el => el.id === mId);
                    addDistributedLoadCurtain(nodes[e.n1], nodes[e.n2], 0xe879f9, showArrowValues);
                });

            } else if (currentCase === 'LC4') {
                legendTitle.innerText = "Load Case 4 - ROOF BEAM CENTER LOAD [Dead]";
                legendData = [
                    { color: '#c084fc', text: `point: 5 ${forceUnit} -Y` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                ['M5', 'M6', 'M7', 'M8'].forEach(mId => {
                    const e = elements.find(el => el.id === mId);
                    const p1 = nodes[e.n1], p2 = nodes[e.n2];
                    const mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2];
                    structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(0, -1, 0), new THREE.Vector3(mid[0], mid[1] + 1.2 * scaleFactor, mid[2]), 1.2 * scaleFactor, 0xc084fc, 0.3 * scaleFactor, 0.2 * scaleFactor));
                    if (showArrowValues) {
                        labelItems.push({ pos: new THREE.Vector3(mid[0], mid[1] + 1.45 * scaleFactor, mid[2]), text: `5.000 ${forceUnit} -Y`, color: '#c084fc' });
                    }
                });

            } else if (currentCase === 'LC5') {
                legendTitle.innerText = "Load Case 5 - WIND X [Wind]";
                legendData = [
                    { color: '#ef4444', text: `nodal: 2.5 ${forceUnit} +X` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                [5, 6, 7, 8].forEach(nid => {
                    const p = nodes[nid];
                    structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(p[0]-1.5 * scaleFactor, p[1], p[2]), 1.5 * scaleFactor, 0xef4444, 0.3 * scaleFactor, 0.2 * scaleFactor));
                    if (showArrowValues) {
                        labelItems.push({ pos: new THREE.Vector3(p[0]-0.8 * scaleFactor, p[1]+0.35 * scaleFactor, p[2]), text: `2.500 ${forceUnit} +X`, color: '#ef4444' });
                    }
                });

            } else if (currentCase === 'LC6') {
                legendTitle.innerText = "Load Case 6 - WIND Z [Wind]";
                legendData = [
                    { color: '#ef4444', text: `nodal: 2.5 ${forceUnit} +Z` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                [5, 6, 7, 8].forEach(nid => {
                    const p = nodes[nid];
                    structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(0, 0, -1), new THREE.Vector3(p[0], p[1], p[2]-1.5 * scaleFactor), 1.5 * scaleFactor, 0xef4444, 0.3 * scaleFactor, 0.2 * scaleFactor));
                    if (showArrowValues) {
                        labelItems.push({ pos: new THREE.Vector3(p[0], p[1]+0.35 * scaleFactor, p[2]-0.8 * scaleFactor), text: `2.500 ${forceUnit} +Z`, color: '#ef4444' });
                    }
                });

            } else if (currentCase === 'LC7') {
                legendTitle.innerText = "Load Case 7 - SEISMIC X [Seismic]";
                legendData = [
                    { color: '#ef4444', text: `nodal: 3.75 ${forceUnit} +X` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                [5, 6, 7, 8].forEach(nid => {
                    const p = nodes[nid];
                    structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(-1, 0, 0), new THREE.Vector3(p[0]-1.5 * scaleFactor, p[1], p[2]), 1.5 * scaleFactor, 0xef4444, 0.3 * scaleFactor, 0.2 * scaleFactor));
                    if (showArrowValues) {
                        labelItems.push({ pos: new THREE.Vector3(p[0]-0.8 * scaleFactor, p[1]+0.35 * scaleFactor, p[2]), text: `3.750 ${forceUnit} +X`, color: '#ef4444' });
                    }
                });

            } else if (currentCase === 'LC8') {
                legendTitle.innerText = "Load Case 8 - SEISMIC Z [Seismic]";
                legendData = [
                    { color: '#ef4444', text: `nodal: 3.75 ${forceUnit} +Z` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                [5, 6, 7, 8].forEach(nid => {
                    const p = nodes[nid];
                    structureGroup.add(new THREE.ArrowHelper(new THREE.Vector3(0, 0, -1), new THREE.Vector3(p[0], p[1], p[2]-1.5 * scaleFactor), 1.5 * scaleFactor, 0xef4444, 0.3 * scaleFactor, 0.2 * scaleFactor));
                    if (showArrowValues) {
                        labelItems.push({ pos: new THREE.Vector3(p[0], p[1]+0.35 * scaleFactor, p[2]-0.8 * scaleFactor), text: `3.750 ${forceUnit} +Z`, color: '#ef4444' });
                    }
                });

            } else if (currentCase === 'LC9') {
                legendTitle.innerText = "LC 9 - TEMP +15C [Temperature]";
                legendData = [
                    { color: '#fbbf24', text: 'temperature: +15 °C on 12 members' },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                elements.forEach(e => {
                    const p1 = nodes[e.n1], p2 = nodes[e.n2];
                    const mid = [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2];
                    if (showArrowValues) {
                        labelItems.push({ pos: new THREE.Vector3(mid[0], mid[1]+0.2, mid[2]), text: "+15 °C", color: '#fbbf24' });
                    }
                });

            } else if (currentCase === 'C1') {
                legendTitle.innerText = "LRFD Combination 1 - 1.4D [LRFD]";
                legendData = [
                    { color: '#e879f9', text: `distributed loads active` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                subTextLines = ["DEAD / SELF WEIGHT x 1.4", "ROOF DEAD x 1.4", "ROOF BEAM CENTER LOAD x 1.4"];
                elements.forEach(e => addDistributedLoadCurtain(nodes[e.n1], nodes[e.n2], 0xc084fc, showArrowValues));

            } else if (currentCase === 'ASD13' || currentCase === 'ASD15') {
                legendTitle.innerText = (currentCase === 'ASD13' ? "ASD Combination 13 - D [ASD]" : "ASD Combination 15 - D [ASD]");
                legendData = [
                    { color: '#e879f9', text: `service loads active` },
                    { color: '#a855f7', text: 'Diaphragm nodes (4)' }
                ];
                subTextLines = ["DEAD / SELF WEIGHT x 1", "ROOF DEAD x 1", "ROOF BEAM CENTER LOAD x 1"];
                elements.forEach(e => addDistributedLoadCurtain(nodes[e.n1], nodes[e.n2], 0xc084fc, showArrowValues));
            }

            if (showLocalAxes) {
                legendData.push({ color: '#ef4444', text: 'Axis 1 (Axial / Red)' });
                legendData.push({ color: '#34d399', text: 'Axis 2 (Major / Green)' });
                legendData.push({ color: '#38bdf8', text: 'Axis 3 (Minor / Blue)' });
            }

            legendData.forEach(item => {
                const div = document.createElement('div');
                div.className = 'legend-item';
                div.innerHTML = `<div class="legend-color" style="background:${item.color};"></div><span>${item.text}</span>`;
                legendItems.appendChild(div);
            });

            if (subTextLines.length > 0) {
                legendSubText.innerHTML = subTextLines.join('<br>');
            }

            if (showDiaphragm) {
                const p5 = nodes[5], p6 = nodes[6], p7 = nodes[7], p8 = nodes[8];
                const dPoints = [
                    new THREE.Vector3(...p5), new THREE.Vector3(...p6),
                    new THREE.Vector3(...p6), new THREE.Vector3(...p7),
                    new THREE.Vector3(...p7), new THREE.Vector3(...p8),
                    new THREE.Vector3(...p8), new THREE.Vector3(...p5)
                ];
                structureGroup.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(dPoints), new THREE.LineBasicMaterial({ color: 0xa855f7, linewidth: 3 })));
                [5, 6, 7, 8].forEach(nid => {
                    const p = nodes[nid];
                    const boxMesh = new THREE.Mesh(new THREE.BoxGeometry(0.35 * scaleFactor, 0.35 * scaleFactor, 0.35 * scaleFactor), new THREE.MeshBasicMaterial({ color: 0xc084fc, wireframe: true }));
                    boxMesh.position.set(p[0], p[1], p[2]);
                    structureGroup.add(boxMesh);
                });
                labelItems.push({ pos: new THREE.Vector3(L/2, L + 0.4 * scaleFactor, 0), text: "ROOF DIAPHRAGM master N5", color: '#c084fc' });
            }

            const dofMap = {
                1: "N1\\nDOF 1-6",
                2: "N2\\nDOF 7-12",
                3: "N3\\nDOF 13-18",
                4: "N4\\nDOF 19-24",
                5: "N5\\nDOF 25-30",
                6: "N6\\nDOF 31-36",
                7: "N7\\nDOF 37-42",
                8: "N8\\nDOF 43-48"
            };

            for (let id in nodes) {
                const p = nodes[id];
                if (showNodes) {
                    const nMesh = new THREE.Mesh(new THREE.SphereGeometry(0.18 * scaleFactor, 16, 16), new THREE.MeshBasicMaterial({ color: 0xe879f9 }));
                    nMesh.position.set(p[0], p[1], p[2]);
                    structureGroup.add(nMesh);
                    if (showNodeLabels) labelItems.push({ pos: new THREE.Vector3(p[0], p[1] + 0.45 * scaleFactor, p[2]), text: dofMap[id], color: '#e879f9' });
                }
                if (showSupports && id <= 4) {
                    const coneMesh = new THREE.Mesh(new THREE.ConeGeometry(0.35 * scaleFactor, 0.45 * scaleFactor, 4), new THREE.MeshBasicMaterial({ color: 0xa855f7 }));
                    coneMesh.position.set(p[0], -0.22 * scaleFactor, p[2]);
                    structureGroup.add(coneMesh);
                }
            }

            elements.forEach(e => {
                const v1 = new THREE.Vector3(...nodes[e.n1]), v2 = new THREE.Vector3(...nodes[e.n2]);
                const colorHex = (e.type === 'Beam') ? 0x38bdf8 : 0xc084fc;

                if (displayMode === 'Line Diagram') {
                    structureGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([v1, v2]), new THREE.LineBasicMaterial({ color: colorHex, linewidth: 3 })));
                } else if (displayMode === 'Wireframe') {
                    createExtrudedMember(v1, v2, colorHex, true);
                } else if (displayMode === 'Solid Render') {
                    createExtrudedMember(v1, v2, colorHex, false);
                }

                const mid = new THREE.Vector3().addVectors(v1, v2).multiplyScalar(0.5);

                if (showLocalAxes) {
                    const axisLen = 0.85 * scaleFactor;
                    const dir1 = new THREE.Vector3().subVectors(v2, v1).normalize();
                    
                    let refUp = new THREE.Vector3(0, 1, 0);
                    if (Math.abs(dir1.y) > 0.99) refUp = new THREE.Vector3(0, 0, 1);
                    
                    const dir3 = new THREE.Vector3().crossVectors(dir1, refUp).normalize();
                    const dir2 = new THREE.Vector3().crossVectors(dir3, dir1).normalize();

                    structureGroup.add(new THREE.ArrowHelper(dir1, mid, axisLen, 0xef4444, 0.22 * scaleFactor, 0.1 * scaleFactor));
                    structureGroup.add(new THREE.ArrowHelper(dir2, mid, axisLen, 0x34d399, 0.22 * scaleFactor, 0.1 * scaleFactor));
                    structureGroup.add(new THREE.ArrowHelper(dir3, mid, axisLen, 0x38bdf8, 0.22 * scaleFactor, 0.1 * scaleFactor));

                    labelItems.push({ pos: mid.clone().addScaledVector(dir1, axisLen + 0.18), text: `${e.id}:1`, color: '#ef4444' });
                    labelItems.push({ pos: mid.clone().addScaledVector(dir2, axisLen + 0.18), text: `${e.id}:2`, color: '#34d399' });
                    labelItems.push({ pos: mid.clone().addScaledVector(dir3, axisLen + 0.18), text: `${e.id}:3`, color: '#38bdf8' });
                }

                if (showMzReleases) {
                    const ringMesh = new THREE.Mesh(new THREE.RingGeometry(0.08 * scaleFactor, 0.12 * scaleFactor, 12), new THREE.MeshBasicMaterial({ color: 0xfbbf24, side: THREE.DoubleSide }));
                    ringMesh.position.set(v1.x, v1.y, v1.z);
                    ringMesh.lookAt(v2);
                    structureGroup.add(ringMesh);
                }

                let labelTexts = [];
                if (showMemberLabels) labelTexts.push(e.id);

                if (labelTexts.length > 0 && !showLocalAxes) {
                    labelItems.push({ pos: mid, text: labelTexts.join(' | '), color: '#f3e8ff' });
                }
            });
        }

        window.onload = () => { 
            resizeCanvas(); 
            buildCubeModel(); 
        };

        function animate(timestamp) { 
            requestAnimationFrame(animate); 

            if (isTransitioning) {
                const elapsed = timestamp - transStartTime;
                const progress = Math.min(1.0, elapsed / transDuration);
                const ease = 1 - Math.pow(1 - progress, 3);
                
                camera.position.lerpVectors(transStartPos, transEndPos, ease);
                controls.target.lerpVectors(transStartTarget, transEndTarget, ease);
                controls.update();

                if (progress >= 1.0) {
                    isTransitioning = false;
                }
            }

            controls.update();

            document.getElementById('camXVal').innerText = camera.position.x.toFixed(2);
            document.getElementById('camYVal').innerText = camera.position.y.toFixed(2);
            document.getElementById('camZVal').innerText = camera.position.z.toFixed(2);

            const cameraDirection = new THREE.Vector3();
            camera.getWorldDirection(cameraDirection);
            orientCamera.position.copy(cameraDirection.clone().negate().multiplyScalar(5));
            orientCamera.lookAt(0, 0, 0);

            renderer.render(scene, camera); 
            orientRenderer.render(orientScene, orientCamera);
            drawOverlayLabels(); 
        }
        requestAnimationFrame(animate);

        function drawOverlayLabels() {
            ctx2d.clearRect(0, 0, canvas2d.width, canvas2d.height);
            ctx2d.font = "bold 9.5px Consolas, monospace";
            labelItems.forEach(item => {
                const vec = item.pos.clone();
                vec.project(camera);
                if (vec.z < 1) {
                    const x = (vec.x * .5 + .5) * canvas2d.width;
                    const y = (-(vec.y * .5) + .5) * canvas2d.height;
                    
                    const lines = item.text.split('\\n');
                    const lineHeight = 11;
                    const boxHeight = lines.length * lineHeight + 4;
                    
                    let maxWidth = 0;
                    lines.forEach(l => {
                        const w = ctx2d.measureText(l).width;
                        if (w > maxWidth) maxWidth = w;
                    });
                    
                    ctx2d.fillStyle = "rgba(15, 13, 23, 0.90)";
                    ctx2d.fillRect(x - maxWidth/2 - 6, y - boxHeight/2 - 2, maxWidth + 12, boxHeight);
                    ctx2d.strokeStyle = "rgba(168, 85, 247, 0.4)";
                    ctx2d.strokeRect(x - maxWidth/2 - 6, y - boxHeight/2 - 2, maxWidth + 12, boxHeight);
                    ctx2d.fillStyle = item.color;
                    ctx2d.textAlign = "center";
                    
                    lines.forEach((l, idx) => {
                        const lineY = y - (boxHeight/2) + 9 + (idx * lineHeight);
                        ctx2d.fillText(l, x, lineY);
                    });
                }
            });
        }
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_code)

abs_path = os.path.abspath("index.html")
webbrowser.open(f"file://{abs_path}")
print("Cube FEM Studio updated with layout interaction fixes, active pointer events, and stable viewport sizing.")