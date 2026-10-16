import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons

# ==========================================
# 1. GEOMETRY & DOF DATA
# ==========================================

nodes = {
    1: (0, 0, 0), 2: (6, 0, 0), 3: (6, 6, 0), 4: (0, 6, 0),
    5: (0, 0, 6), 6: (6, 0, 6), 7: (6, 6, 6), 8: (0, 6, 6)
}

node_dofs = {
    1: "DOF 1-6",   2: "DOF 7-12",  3: "DOF 13-18", 4: "DOF 19-24",
    5: "DOF 25-30", 6: "DOF 31-36", 7: "DOF 37-42", 8: "DOF 43-48"
}

members_data = [
    (1, 2, "M1", "β=0°"),   (2, 3, "M2", "β=0°"), 
    (3, 4, "M3", "β=0°"),   (4, 1, "M4", "β=0°"),
    (1, 5, "M9", "β=90°"),  (2, 6, "M10", "β=90°"), 
    (3, 7, "M11", "β=90°"), (4, 8, "M12", "β=90°"),
    (5, 6, "M5", "β=0°"),   (6, 7, "M6", "β=0°"), 
    (7, 8, "M7", "β=0°"),   (8, 5, "M8", "β=0°")
]

pinned_nodes = [1, 2, 3, 4]

# ==========================================
# 2. FIGURE & LAYOUT SETUP
# ==========================================

fig = plt.figure(figsize=(16, 9))

# 3D Plot Area
ax_3d = fig.add_axes([0.01, 0.05, 0.52, 0.88], projection='3d')
ax_3d.view_init(elev=20, azim=-60)

# Text Information Box Area
ax_info = fig.add_axes([0.53, 0.03, 0.26, 0.92])
ax_info.axis('off')

# ==========================================
# 3. DRAW 3D MODEL
# ==========================================

for n1, n2, label, beta in members_data:
    x1, z1, y1 = nodes[n1]
    x2, z2, y2 = nodes[n2]
    
    is_column = "β=90°" in beta
    color = '#005f73' if is_column else '#0077b6'
    
    # Member Line
    ax_3d.plot([x1, x2], [z1, z2], [y1, y2], color=color, linewidth=2)
    
    # Text Placement with offsets to eliminate overlaps
    mx, my, mz = (x1 + x2)/2, (y1 + y2)/2, (z1 + z2)/2
    offset_y = 0.3 if is_column else -0.3
    ax_3d.text(mx, mz, my + offset_y, f"{label} ({beta})", fontsize=6.5,
               bbox=dict(boxstyle="square,pad=0.1", facecolor='white', alpha=0.6, edgecolor='none'))

    # Local Axes Triad (x: purple, y: green, z: red)
    dx, dy, dz = (x2 - x1) * 0.12, (y2 - y1) * 0.12, (z2 - z1) * 0.12
    ax_3d.quiver(mx, mz, my, dx, dz, dy, color='purple', arrow_length_ratio=0.3, linewidth=1.2)
    ax_3d.quiver(mx, mz, my, 0, 0, 0.6, color='green', arrow_length_ratio=0.3, linewidth=1.0)

# Nodes & DOFs
for node_id, (nx, nz, ny) in nodes.items():
    if node_id in pinned_nodes:
        ax_3d.scatter(nx, nz, ny, color='red', s=90, marker='^')
    else:
        ax_3d.scatter(nx, nz, ny, color='green', s=40, marker='o')
        
    ax_3d.text(nx, nz, ny + 0.35, f"N{node_id}\n{node_dofs[node_id]}", 
               fontsize=7, fontweight='bold', ha='center')

# Titles and Labels
ax_3d.set_title("6m x 6m x 6m Cube - Structural Model, Rev. 3\n"
                "Pinned supports at nodes 1-4 | Unit system: Standard Metric", 
                fontsize=11, fontweight='bold', pad=12)

ax_3d.set_xlabel('X (m) - lateral', labelpad=8)
ax_3d.set_ylabel('Z (m) - lateral', labelpad=8)
ax_3d.set_zlabel('Y (m) - vertical', labelpad=8)

# Legend matching reference image
legend_elements = [
    plt.Line2D([0], [0], color='#0077b6', lw=2, label='Beam'),
    plt.Line2D([0], [0], color='purple', lw=1.5, label='Local x axis'),
    plt.Line2D([0], [0], color='green', lw=1.5, label='Local y axis'),
    plt.Line2D([0], [0], color='#005f73', lw=2, label='Column'),
    plt.Line2D([0], [0], marker='^', color='w', label='Supported node (pinned)', markerfacecolor='red', markersize=9),
    plt.Line2D([0], [0], marker='o', color='w', label='Free node', markerfacecolor='green', markersize=7)
]
ax_3d.legend(handles=legend_elements, loc='upper left', fontsize=7)

# ==========================================
# 4. FULL REV3 MODEL DATA TEXT
# ==========================================

data_text = (
    "MODEL DATA - Rev. 3\n\n"
    "Geometry\n"
    "  Cube edge          6.000 m\n"
    "  Nodes              8\n"
    "  Members            12\n"
    "  Vertical axis      global Y\n\n"
    "Unit System\n"
    "  Active             Standard Metric\n"
    "  Source             Units_Imperial_Metric.xlsx\n\n"
    "Material\n"
    "  Selected           A992\n"
    "  Category           Hot Rolled\n"
    "  Source             RISA_Materials_Library.xlsx\n"
    "  E                  1.999e+05 MPa\n"
    "  G                  7.690e+04 MPa\n"
    "  Nu                 0.300\n"
    "  Density            76.97 kN/m³\n"
    "  Yield              344.7 MPa\n"
    "  Fu                 399.9 MPa\n\n"
    "Member Size\n"
    "  Selected           W310X38.7\n"
    "  Source             aisc-shapes-database-v160-2.xlsx\n"
    "  A                  4940 mm²\n"
    "  d                  310 mm\n"
    "  bf                 165 mm\n"
    "  tw                 5.84 mm\n"
    "  tf                 9.65 mm\n"
    "  Ix                 84.90 x 10⁶ mm⁴\n"
    "  Iy                 7.20 x 10⁶ mm⁴\n"
    "  Self-weight        0.3795 kN/m\n\n"
    "Supports\n"
    "  Type               pinned\n"
    "  Nodes              1, 2, 3, 4\n"
    "  Restrained         UX, UY, UZ\n"
    "  Released           RX, RY, RZ\n\n"
    "Degrees of Freedom\n"
    "  DOF per node       6\n"
    "  Total DOF          48\n"
    "  Restrained DOF     12\n"
    "  Active DOF         36\n"
    "  Numbering          (node - 1) x 6 + 1...6\n\n"
    "Beta angles\n"
    "  Base Beam          0 deg\n"
    "  Roof Beam          0 deg\n"
    "  Column             90 deg\n\n"
    "Local axes\n"
    "  local x            start node i -> end node j\n"
    "  local y            in vertical plane, when possible\n"
    "  local z            completes right-handed set\n"
    "  Vertical members:  local z parallel to global Z"
)

ax_info.text(0.0, 1.0, data_text, transform=ax_info.transAxes,
             fontsize=7.2, family='monospace', verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.7", facecolor="#f8f9fa", edgecolor="#cccccc"))

# UI Widgets on Right Margin
ax_unit_widget = fig.add_axes([0.81, 0.75, 0.16, 0.15])
unit_radio = RadioButtons(ax_unit_widget, ('Standard Metric', 'Imperial'), active=0)
ax_unit_widget.set_title("Unit System", fontsize=8.5, fontweight='bold')

ax_mat_widget = fig.add_axes([0.81, 0.58, 0.16, 0.08])
mat_radio = RadioButtons(ax_mat_widget, ('A992',), active=0)
ax_mat_widget.set_title("Material", fontsize=8.5, fontweight='bold')

ax_size_widget = fig.add_axes([0.81, 0.44, 0.16, 0.08])
size_radio = RadioButtons(ax_size_widget, ('W310X38.7',), active=0)
ax_size_widget.set_title("Member Size", fontsize=8.5, fontweight='bold')

plt.show()