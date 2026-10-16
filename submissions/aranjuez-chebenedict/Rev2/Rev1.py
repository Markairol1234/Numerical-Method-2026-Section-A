# ============================================================
# Rev1.py  —  Rev. 1
# 6m x 6m x 6m Cube Structural Model Generator
# Beta default: beams = 0°, columns = 90°  (RISA/STAAD convention)
# ============================================================

import os
import base64
import datetime as dt
import io

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

# ------------------------------------------------------------
# 0. Paths
# ------------------------------------------------------------
OUT_DIR    = r"D:\che school 2627\lab02"
EXCEL_PATH = os.path.join(OUT_DIR, "cube_model.xlsx")
HTML_PATH  = os.path.join(OUT_DIR, "cube_model.html")
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------
# 1. Cube geometry
# ------------------------------------------------------------
L = 6.0

nodes = {
    1: (0.0, 0.0, 0.0),
    2: (L,   0.0, 0.0),
    3: (L,   0.0, L),
    4: (0.0, 0.0, L),
    5: (0.0, L,   0.0),
    6: (L,   L,   0.0),
    7: (L,   L,   L),
    8: (0.0, L,   L),
}

BASE_NODES = (1, 2, 3, 4)

member_pairs = [
    (1, 2), (2, 3), (3, 4), (4, 1),
    (5, 6), (6, 7), (7, 8), (8, 5),
    (1, 5), (2, 6), (3, 7), (4, 8),
]

def classify_member(i, j):
    xi, yi, zi = nodes[i]
    xj, yj, zj = nodes[j]
    if xi == xj and zi == zj and yi != yj:
        return "Column"
    return "Beam"

members = [(i, j, classify_member(i, j)) for i, j in member_pairs]

# ------------------------------------------------------------
# BETA — default 90° for columns, 0° for beams
# ------------------------------------------------------------
# <<<< CHANGED: default beta depends on member type
BETA_DEG = {
    idx: (90.0 if mtype == "Column" else 0.0)
    for idx, (i, j, mtype) in enumerate(members, start=1)
}
# ------------------------------------------------------------

# ------------------------------------------------------------
# 2a. Supports
# ------------------------------------------------------------
DOF_NAMES = ["Ux", "Uy", "Uz", "Rx", "Ry", "Rz"]

def get_support(node):
    if node in BASE_NODES:
        return {"Ux": True, "Uy": True, "Uz": True,
                "Rx": False, "Ry": False, "Rz": False}
    return {d: False for d in DOF_NAMES}

supports = {n: get_support(n) for n in nodes}

# ------------------------------------------------------------
# 2b. Nodal DOF numbering
# ------------------------------------------------------------
node_dof_numbers = {}
_active_counter = 0
for n in sorted(nodes):
    dof_map = {}
    for d in DOF_NAMES:
        if supports[n][d]:
            dof_map[d] = "R"
        else:
            _active_counter += 1
            dof_map[d] = _active_counter
    node_dof_numbers[n] = dof_map

TOTAL_DOF      = len(nodes) * 6
ACTIVE_DOF     = _active_counter
RESTRAINED_DOF = TOTAL_DOF - ACTIVE_DOF

# ------------------------------------------------------------
# 2c. Local axes
# <<<< CHANGED: reference is always Global Y; for vertical members,
#      add 90° to beta internally so beta=90° in Excel produces the
#      same physical axes as the old "use Global X for verticals"
#      convention.
# ------------------------------------------------------------
def local_axes(i, j, beta_deg=0.0):
    p_i = np.array(nodes[i], dtype=float)
    p_j = np.array(nodes[j], dtype=float)
    vec = p_j - p_i
    length = np.linalg.norm(vec)
    local_1 = vec / length

    global_y = np.array([0.0, 1.0, 0.0])
    global_x = np.array([1.0, 0.0, 0.0])

    if abs(np.dot(local_1, global_y)) > 0.9999:
        ref = global_x
        beta_deg += 90.0            # internal compensation
    else:
        ref = global_y

    local_3 = np.cross(local_1, ref)
    local_3 /= np.linalg.norm(local_3)
    local_2 = np.cross(local_3, local_1)
    local_2 /= np.linalg.norm(local_2)

    beta = np.radians(beta_deg)
    local_2_rot = (local_2 * np.cos(beta)
                   + np.cross(local_1, local_2) * np.sin(beta)
                   + local_1 * np.dot(local_1, local_2) * (1 - np.cos(beta)))
    local_2_rot /= np.linalg.norm(local_2_rot)
    local_3_rot = np.cross(local_1, local_2_rot)
    local_3_rot /= np.linalg.norm(local_3_rot)

    return local_1, local_2_rot, local_3_rot

member_local_axes = {
    idx: local_axes(i, j, BETA_DEG[idx])
    for idx, (i, j, _t) in enumerate(members, start=1)
}

# ------------------------------------------------------------
# 2d. Member end releases
# ------------------------------------------------------------
LOCAL_DOF_NAMES = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]

def default_release(mtype):
    end = {d: False for d in LOCAL_DOF_NAMES}
    if mtype == "Beam":
        end["Mz"] = True
    return end

member_releases = {
    idx: {"i": default_release(mtype), "j": default_release(mtype)}
    for idx, (i, j, mtype) in enumerate(members, start=1)
}

# ------------------------------------------------------------
# 3. Excel workbook
# ------------------------------------------------------------
wb = openpyxl.Workbook()
header_font = Font(name="Arial", bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
body_font   = Font(name="Arial")
center      = Alignment(horizontal="center")

def style_header(ws, headers):
    ws.append(headers)
    for col in range(1, len(headers) + 1):
        c = ws.cell(row=1, column=col)
        c.font = header_font; c.fill = header_fill; c.alignment = center

def style_body(ws, ncols):
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=ncols):
        for cell in row:
            cell.font = body_font; cell.alignment = center

ws_nodes = wb.active; ws_nodes.title = "Nodes"
style_header(ws_nodes, ["Node", "X (m)", "Y (m)", "Z (m)"])
for n, (x, y, z) in nodes.items():
    ws_nodes.append([n, x, y, z])
style_body(ws_nodes, 4)

ws_mem = wb.create_sheet("Member Incidences")
style_header(ws_mem, ["Member", "i (Start Node)", "j (End Node)", "Type", "Beta (deg)"])
for idx, (i, j, mtype) in enumerate(members, start=1):
    ws_mem.append([idx, i, j, mtype, BETA_DEG[idx]])
style_body(ws_mem, 5)

ws_sup = wb.create_sheet("Supports")
style_header(ws_sup, ["Node", "Support Type", "Ux", "Uy", "Uz", "Rx", "Ry", "Rz"])
for n in sorted(nodes):
    stype = "Pinned" if n in BASE_NODES else "Free"
    row = [n, stype] + ["Fixed" if supports[n][d] else "Free" for d in DOF_NAMES]
    ws_sup.append(row)
style_body(ws_sup, 8)

ws_dof = wb.create_sheet("Node DOF")
style_header(ws_dof, ["Node"] + DOF_NAMES)
for n in sorted(nodes):
    ws_dof.append([n] + [node_dof_numbers[n][d] for d in DOF_NAMES])
style_body(ws_dof, 7)
ws_dof.append([])
ws_dof.append(["Total DOF:", TOTAL_DOF])
ws_dof.append(["Active DOF:", ACTIVE_DOF])
ws_dof.append(["Restrained DOF:", RESTRAINED_DOF])

ws_axes = wb.create_sheet("Member Local Axes")
style_header(ws_axes, ["Member", "i", "j", "Beta (deg)",
                       "Local-1 X", "Local-1 Y", "Local-1 Z",
                       "Local-2 X", "Local-2 Y", "Local-2 Z",
                       "Local-3 X", "Local-3 Y", "Local-3 Z"])
for idx, (i, j, mtype) in enumerate(members, start=1):
    l1, l2, l3 = member_local_axes[idx]
    ws_axes.append([idx, i, j, BETA_DEG[idx],
                    round(l1[0], 3), round(l1[1], 3), round(l1[2], 3),
                    round(l2[0], 3), round(l2[1], 3), round(l2[2], 3),
                    round(l3[0], 3), round(l3[1], 3), round(l3[2], 3)])
style_body(ws_axes, 13)

ws_rel = wb.create_sheet("Member Releases")
style_header(ws_rel, ["Member", "End", "Fx", "Fy", "Fz", "Mx", "My", "Mz"])
for idx, (i, j, mtype) in enumerate(members, start=1):
    for end_label, node_ref in (("i", i), ("j", j)):
        rel = member_releases[idx][end_label]
        row = [idx, f"{end_label} (Node {node_ref})"] + \
              ["Released" if rel[d] else "Fixed" for d in LOCAL_DOF_NAMES]
        ws_rel.append(row)
style_body(ws_rel, 8)

ws_sum = wb.create_sheet("Summary")
style_header(ws_sum, ["Item", "Value"])
ws_sum.append(["Cube side length (m)", L])
ws_sum.append(["Nodes", len(nodes)])
ws_sum.append(["Members", len(members)])
ws_sum.append(["Pinned supports", len(BASE_NODES)])
ws_sum.append(["Total DOF", TOTAL_DOF])
ws_sum.append(["Active DOF", ACTIVE_DOF])
ws_sum.append(["Restrained DOF", RESTRAINED_DOF])
style_body(ws_sum, 2)

wb.save(EXCEL_PATH)
print(f"Saved Excel: {EXCEL_PATH}")

# ------------------------------------------------------------
# 4. Diagram
# ------------------------------------------------------------
def build_cube_figure():
    fig = plt.figure(figsize=(11, 10))
    ax  = fig.add_subplot(111, projection="3d")

    for i, j, mtype in members:
        x_vals = [nodes[i][0], nodes[j][0]]
        z_vals = [nodes[i][2], nodes[j][2]]
        y_vals = [nodes[i][1], nodes[j][1]]
        color = "darkorange" if mtype == "Column" else "steelblue"
        ax.plot(x_vals, z_vals, y_vals, color=color, linewidth=2)

    for n, (x, y, z) in nodes.items():
        ax.scatter([x], [z], [y], color="red", s=60, depthshade=True)
        ax.text(x, z, y, f"  {n}", color="black",
                fontsize=11, fontweight="bold")

        dof_map = node_dof_numbers[n]
        dof_str = "\n".join([
            f"Ux:{dof_map['Ux']} Uy:{dof_map['Uy']} Uz:{dof_map['Uz']}",
            f"Rx:{dof_map['Rx']} Ry:{dof_map['Ry']} Rz:{dof_map['Rz']}",
        ])
        ax.text(x, z, y - 0.35, dof_str,
                color="darkgreen", fontsize=7, fontweight="bold")

    for n in BASE_NODES:
        x, y, z = nodes[n]
        ax.scatter([x], [z], [y], marker="^", color="black", s=200, zorder=5)

    for idx, (i, j, mtype) in enumerate(members, start=1):
        mx = (nodes[i][0] + nodes[j][0]) / 2
        mz = (nodes[i][2] + nodes[j][2]) / 2
        my = (nodes[i][1] + nodes[j][1]) / 2
        l1, l2, l3 = member_local_axes[idx]
        s = 0.6

        ax.quiver(mx, mz, my, l1[0], l1[2], l1[1],
                  length=s, color="red",   linewidth=1.2)
        ax.quiver(mx, mz, my, l2[0], l2[2], l2[1],
                  length=s, color="green", linewidth=1.2)
        ax.quiver(mx, mz, my, l3[0], l3[2], l3[1],
                  length=s, color="blue",  linewidth=1.2)

        ax.text(mx + l1[0]*s*1.15, mz + l1[2]*s*1.15, my + l1[1]*s*1.15,
                "L1", color="red",   fontsize=8, fontweight="bold")
        ax.text(mx + l2[0]*s*1.15, mz + l2[2]*s*1.15, my + l2[1]*s*1.15,
                "L2", color="green", fontsize=8, fontweight="bold")
        ax.text(mx + l3[0]*s*1.15, mz + l3[2]*s*1.15, my + l3[1]*s*1.15,
                "L3", color="blue",  fontsize=8, fontweight="bold")

        ax.text(mx, mz, my + 0.35,
                f"β={BETA_DEG[idx]:.0f}°",
                color="purple", fontsize=8, fontweight="bold")

    axis_len = L * 0.4
    ax.quiver(0, 0, 0, axis_len, 0, 0, color="black", linewidth=2, arrow_length_ratio=0.12)
    ax.quiver(0, 0, 0, 0, axis_len, 0, color="black", linewidth=2, arrow_length_ratio=0.12)
    ax.quiver(0, 0, 0, 0, 0, axis_len, color="black", linewidth=2, arrow_length_ratio=0.12)
    ax.text(axis_len * 1.05, 0, 0, "Global X", fontsize=9, fontweight="bold")
    ax.text(0, axis_len * 1.05, 0, "Global Z", fontsize=9, fontweight="bold")
    ax.text(0, 0, axis_len * 1.05, "Global Y", fontsize=9, fontweight="bold")

    ax.set_xlabel("X (m) - Lateral",  fontsize=11, labelpad=10)
    ax.set_ylabel("Z (m) - Lateral",  fontsize=11, labelpad=10)
    ax.set_zlabel("Y (m) - Vertical", fontsize=11, labelpad=10)

    ax.set_title("6m x 6m x 6m Cube Model (Rev. 1)\n"
                 "β = beta angle (beams=0°, columns=90°)  |  "
                 "L1/L2/L3 = Local axes  |  ▲ = Pinned",
                 fontsize=10, fontweight="bold")

    ax.set_xlim(-1.5, L + 1.5)
    ax.set_ylim(-1.5, L + 1.5)
    ax.set_zlim(-1.0, L + 1.0)
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=20, azim=-60)

    legend_elems = [
        Line2D([0], [0], color="steelblue",  lw=2, label="Beam (β=0°)"),
        Line2D([0], [0], color="darkorange", lw=2, label="Column (β=90°)"),
        Line2D([0], [0], marker="^", color="black", lw=0,
               markersize=10, label="Pinned Support"),
        Line2D([0], [0], color="red",   lw=1, label="Local-1 (axial)"),
        Line2D([0], [0], color="green", lw=1, label="Local-2"),
        Line2D([0], [0], color="blue",  lw=1, label="Local-3"),
    ]
    ax.legend(handles=legend_elems, loc="upper left", fontsize=8)

    fig.tight_layout()
    return fig

fig_embed = build_cube_figure()
buf = io.BytesIO()
fig_embed.savefig(buf, format="png", dpi=150, bbox_inches="tight")
plt.close(fig_embed)
buf.seek(0)
IMG_B64 = base64.b64encode(buf.read()).decode("ascii")

# ------------------------------------------------------------
# 5. HTML
# ------------------------------------------------------------
generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

node_rows = "".join(
    f"<tr><td>{n}</td><td>{x:.1f}</td><td>{y:.1f}</td><td>{z:.1f}</td></tr>"
    for n, (x, y, z) in nodes.items()
)

member_rows = ""
for idx, (i, j, mtype) in enumerate(members, start=1):
    cls = "col-beam" if mtype == "Beam" else "col-column"
    member_rows += (f"<tr><td>{idx}</td><td>{i}</td><td>{j}</td>"
                    f"<td class='{cls}'>{mtype}</td><td>{BETA_DEG[idx]:.1f}</td></tr>")

support_rows = ""
for n in sorted(nodes):
    stype = "Pinned" if n in BASE_NODES else "Free"
    cells = "".join(f"<td>{'Fixed' if supports[n][d] else 'Free'}</td>" for d in DOF_NAMES)
    support_rows += f"<tr><td>{n}</td><td>{stype}</td>{cells}</tr>"

dof_rows = ""
for n in sorted(nodes):
    vals = "".join(f"<td>{node_dof_numbers[n][d]}</td>" for d in DOF_NAMES)
    dof_rows += f"<tr><td>{n}</td>{vals}</tr>"

CSS = """
:root { --ink:#0b2531; --muted:#5b7180; --line:#d7e3e6;
        --teal:#0e7c86; --teal-dark:#0b4f6c; }
* { box-sizing: border-box; }
body { margin:0; font-family:'Segoe UI', Arial, sans-serif;
       color:var(--ink); background:#f2fafa; line-height:1.55; }
header.hero { background:linear-gradient(135deg,#0e7c86 0%, #0b4f6c 100%);
              color:#fff; padding:32px 28px 60px 28px; position:relative; }
header.hero .kicker { display:inline-block;
       background:rgba(255,255,255,0.15); padding:4px 10px;
       border-radius:20px; font-size:11px; letter-spacing:0.08em;
       text-transform:uppercase; }
header.hero h1 { margin:12px 0 6px 0; font-size:32px; }
header.hero .sub { opacity:0.85; font-size:14px; }
main { max-width:1200px; margin:0 auto; padding:24px 20px 40px; }
section.panel { background:#fff; border-radius:16px; padding:22px 24px;
                margin-bottom:22px; box-shadow:0 6px 24px rgba(11,79,108,0.08); }
h2 { margin:0 0 12px 0; color:var(--teal-dark); font-size:20px; }
.chart { max-width:100%; height:auto; border-radius:10px;
         display:block; margin:0 auto; }
table { border-collapse:collapse; width:100%; font-size:13px; margin:10px 0; }
th, td { border-bottom:1px solid var(--line); padding:9px 10px; text-align:left; }
th { background:#effaf9; color:var(--teal-dark);
     text-transform:uppercase; font-size:10.5px; letter-spacing:0.05em; }
tr:last-child td { border-bottom:none; }
.col-beam   { color:#2a7de1; font-weight:700; }
.col-column { color:#c25e00; font-weight:700; }
footer { text-align:center; color:var(--muted); font-size:11.5px; padding:14px; }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>6m Cube Model &mdash; Rev. 1</title>
<style>
{css}
</style>
</head>
<body>
<header class="hero">
  <span class="kicker">Rev. 1</span>
  <h1>6 m &times; 6 m &times; 6 m Cube Frame</h1>
  <div class="sub">Supports &middot; Beta (beams 0°, columns 90°) &middot; Local axes &middot;
    DOF &middot; Releases &middot; generated {generated}</div>
</header>
<main>
  <section class="panel">
    <h2>3D Diagram</h2>
    <img class="chart" src="data:image/png;base64,{img_b64}" alt="cube Rev1">
  </section>
  <section class="panel"><h2>Nodes</h2>
    <table><tr><th>Node</th><th>X (m)</th><th>Y (m)</th><th>Z (m)</th></tr>
    {node_rows}</table></section>
  <section class="panel"><h2>Member Incidences</h2>
    <table><tr><th>Member</th><th>i</th><th>j</th><th>Type</th><th>β (°)</th></tr>
    {member_rows}</table></section>
  <section class="panel"><h2>Supports</h2>
    <table><tr><th>Node</th><th>Type</th><th>Ux</th><th>Uy</th><th>Uz</th>
    <th>Rx</th><th>Ry</th><th>Rz</th></tr>{support_rows}</table></section>
  <section class="panel"><h2>Node DOF</h2>
    <table><tr><th>Node</th><th>Ux</th><th>Uy</th><th>Uz</th>
    <th>Rx</th><th>Ry</th><th>Rz</th></tr>{dof_rows}</table></section>
</main>
<footer>Generated by <code>Rev1.py</code></footer>
</body>
</html>
"""

html = HTML_TEMPLATE.format(
    css=CSS, generated=generated, img_b64=IMG_B64,
    node_rows=node_rows, member_rows=member_rows,
    support_rows=support_rows, dof_rows=dof_rows,
)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved HTML:  {HTML_PATH}")

# ------------------------------------------------------------
# 6. Pop-up
# ------------------------------------------------------------
fig_show = build_cube_figure()
print("Opening cube plot window — close it to exit.")
plt.show()