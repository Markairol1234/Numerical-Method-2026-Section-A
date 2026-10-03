import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# ==========================================
# IMPLEMENTATION NOTE: MANUAL SERIES SUMMATION VIA PYTHON LOOPS
# ==========================================

def compute_factorial(n):
    """Computes factorial iteratively using custom loops."""
    val = 1
    for i in range(2, n + 1):
        val *= i
    return val

def custom_maclaurin_sin(theta, terms_count):
    """Computes Maclaurin series expansion for sin(theta) using explicit loops."""
    approximation = 0.0
    for n in range(terms_count):
        sign_factor = (-1) ** n
        power_val = 2 * n + 1
        term = sign_factor * (theta ** power_val) / compute_factorial(power_val)
        approximation += term
    return approximation

def custom_taylor_sin(theta, center_theta, terms_count):
    """Computes Taylor series expansion for sin(theta) around center point 'a' using loops."""
    approximation = 0.0
    dtheta = theta - center_theta
    for n in range(terms_count):
        derivative_mod = n % 4
        if derivative_mod == 0:
            coef = np.sin(center_theta)
        elif derivative_mod == 1:
            coef = np.cos(center_theta)
        elif derivative_mod == 2:
            coef = -np.sin(center_theta)
        else:
            coef = -np.cos(center_theta)
            
        term = coef * (dtheta ** n) / compute_factorial(n)
        approximation += term
    return approximation


# ==========================================
# 1. GENERATE NUMERICAL TABLES DATA (L = 20m)
# ==========================================
L = 20.0  # structural length in meters[cite: 2]
angles_deg = [1, 2, 5, 10, 15, 20, 30]
term_counts = [1, 2, 3, 4]

table_rows_html = ""
for deg in angles_deg:
    theta_rad = np.radians(deg)
    exact_y = L * np.sin(theta_rad)
    for terms in term_counts:
        approx_sin = custom_maclaurin_sin(theta_rad, terms)
        approx_y = L * approx_sin
        abs_error = abs(exact_y - approx_y)
        pct_error = (abs_error / abs(exact_y)) * 100 if exact_y != 0 else 0
        
        table_rows_html += f"""
        <tr>
            <td>{deg}°</td>
            <td>{terms}</td>
            <td>{exact_y:.4f} m</td>
            <td>{approx_y:.4f} m</td>
            <td>{abs_error:.6f} m</td>
            <td>{pct_error:.4f}%</td>
        </tr>
        """


# ==========================================
# 2, 3, 4. GENERATE THE 4 DASHBOARD PLOTS & ENCODE TO BASE64
# ==========================================
angle_domain_deg = np.linspace(0, 35, 150)
angle_domain_rad = np.radians(angle_domain_deg)
exact_y_domain = L * np.sin(angle_domain_rad)

fig, axes = plt.subplots(2, 2, figsize=(15, 11))
fig.suptitle("Civil Engineering Series Exercise - Analytical Dashboard (L = 20m)", fontsize=16, fontweight='bold', color='#1e293b')

# --- Plot 2: Convergence Plot ---
ax_conv = axes[0, 0]
term_steps = range(1, 7)
for deg in [2, 10, 20, 30]:
    rad_val = np.radians(deg)
    truth = np.sin(rad_val)
    err_list = [abs((truth - custom_maclaurin_sin(rad_val, t)) / truth) * 100 for t in term_steps]
    ax_conv.plot(term_steps, err_list, marker='o', linestyle='-', label=f'Angle = {deg}°')
ax_conv.set_title("2. Convergence Plot (Maclaurin Error vs. Terms)", fontsize=12, fontweight='bold')
ax_conv.set_xlabel("Number of Terms (N)")
ax_conv.set_ylabel("Percentage Error (%) [Log Scale]")
ax_conv.set_yscale('log')
ax_conv.grid(True, which="both", linestyle="--")
ax_conv.legend(loc='upper right')

# --- Plot 3: Function Comparison Plot ---
ax_func = axes[0, 1]
ax_func.plot(angle_domain_deg, exact_y_domain, 'k-', linewidth=2.5, label='Exact y = L sin(θ)')
ax_func.plot(angle_domain_deg, [L * custom_maclaurin_sin(r, 1) for r in angle_domain_rad], 'r--', label='Maclaurin (1 Term)')
ax_func.plot(angle_domain_deg, [L * custom_maclaurin_sin(r, 3) for r in angle_domain_rad], 'b-.', label='Maclaurin (3 Terms)')
ax_func.set_title("3. Function Comparison Plot (Exact vs. Maclaurin)", fontsize=12, fontweight='bold')
ax_func.set_xlabel("Angle (Degrees)")
ax_func.set_ylabel("Vertical Component y (m)")
ax_func.grid(True, linestyle="--")
ax_func.legend(loc='lower left')

# --- Plot 4: Error Comparison Plot ---
ax_err = axes[1, 0]
taylor_center_deg = 10
taylor_center_rad = np.radians(taylor_center_deg)

mac_err_profile = [
    abs((np.sin(r) - custom_maclaurin_sin(r, 3)) / np.sin(r)) * 100 if abs(np.sin(r)) > 1e-12 else 1e-12 
    for r in angle_domain_rad
]
tay_err_profile = [
    abs((np.sin(r) - custom_taylor_sin(r, taylor_center_rad, 3)) / np.sin(r)) * 100 if abs(r - taylor_center_rad) > 1e-10 and abs(np.sin(r)) > 1e-12 else 1e-12 
    for r in angle_domain_rad
]

ax_err.plot(angle_domain_deg, mac_err_profile, 'r-', linewidth=1.8, label='Maclaurin (3 Terms) % Error')
ax_err.plot(angle_domain_deg, tay_err_profile, 'b-', linewidth=1.8, label='Taylor Center 10° (3 Terms) % Error')
ax_err.axvline(x=taylor_center_deg, color='darkgray', linestyle=':', label='Expansion Center (10°)')
ax_err.set_title("4. Error Comparison Plot (Maclaurin vs. Taylor)", fontsize=12, fontweight='bold')
ax_err.set_xlabel("Angle (Degrees)")
ax_err.set_ylabel("Percentage Error (%) [Log Scale]")
ax_err.set_yscale('log')
ax_err.grid(True, which="both", linestyle="--")
ax_err.legend(loc='upper right')

# Extra Subplot: Taylor Function Comparison (Centered at 10°)
ax_extra = axes[1, 1]
ax_extra.plot(angle_domain_deg, exact_y_domain, 'k-', linewidth=2.5, label='Exact y = L sin(θ)')
ax_extra.plot(angle_domain_deg, [L * custom_taylor_sin(r, taylor_center_rad, 2) for r in angle_domain_rad], 'g--', label='Taylor @ 10° (2 Terms)')
ax_extra.plot(angle_domain_deg, [L * custom_taylor_sin(r, taylor_center_rad, 4) for r in angle_domain_rad], 'purple', linestyle=':', label='Taylor @ 10° (4 Terms)')
ax_extra.axvline(x=taylor_center_deg, color='gray', linestyle=':', label='Taylor Center (10°)')
ax_extra.set_title("Taylor Series Behavior (Centered at 10°)", fontsize=12, fontweight='bold')
ax_extra.set_xlabel("Angle (Degrees)")
ax_extra.set_ylabel("Vertical Component y (m)")
ax_extra.grid(True, linestyle="--")
ax_extra.legend(loc='lower left')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save plot to base64 string
buffer = io.BytesIO()
plt.savefig(buffer, format='png', dpi=150)
buffer.seek(0)
plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
plt.close()


# ==========================================
# 5. COMPILE AND EXPORT HTML DASHBOARD FILE (RAW F-STRING TO AVOID ESCAPE WARNINGS)
# ==========================================
html_content = rf"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Civil Engineering Series Exercise Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8fafc;
            color: #334155;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1250px;
            margin: 0 auto;
            background: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            color: #0f172a;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #64748b;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        h2 {{
            color: #1e293b;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-top: 40px;
        }}
        .table-container {{
            overflow-x: auto;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            text-align: left;
        }}
        th, td {{
            padding: 10px 14px;
            border: 1px solid #cbd5e1;
            font-size: 0.95em;
        }}
        th {{
            background-color: #f1f5f9;
            color: #1e293b;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        .dashboard-image {{
            text-align: center;
            margin: 30px 0;
        }}
        .dashboard-image img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .recommendation-box {{
            background-color: #f0fdf4;
            border-left: 5px solid #22c55e;
            padding: 20px;
            border-radius: 4px;
            margin-top: 20px;
            line-height: 1.6;
        }}
        .qa-section {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .qa-section h3 {{
            margin-top: 0;
            color: #0f172a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Civil Engineering Series Exercise - Analytical Dashboard</h1>
        <div class="subtitle">Approximating Structural Geometry (y = L sin(&theta;) where L = 20m) using Infinite Series</div>
        
        <!-- Deliverable 1 -->
        <h2>1. Numerical Tables</h2>
        <p>Exact vertical component values (y), loop-computed approximations, absolute errors, and percentage errors across angles (1° to 30°) and term counts (N = 1 to 4):</p>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Angle (deg)</th>
                        <th>Terms (N)</th>
                        <th>Exact Value (y)</th>
                        <th>Approximation</th>
                        <th>Absolute Error</th>
                        <th>Percentage Error (%)</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>
        </div>

        <!-- Deliverables 2, 3, 4 (Visual Dashboard) -->
        <h2>2, 3, & 4. Visual Analytics Dashboards</h2>
        <div class="dashboard-image">
            <img src="data:image/png;base64,{plot_base64}" alt="Visual Analytics Dashboard">
        </div>

        <!-- Deliverable 5 & Engineering Questions -->
        <h2>5. Written Recommendation & Engineering Analysis</h2>
        <div class="recommendation-box">
            <p><strong>Final Engineering Decision & Recommendation:</strong></p>
            <ul>
                <li><strong>Number of Terms Required:</strong> For angles within 1° - 10°, a 1 to 2-term Maclaurin series satisfies the strict 0.1% error tolerance. For wider spans up to 30°, a 3 to 4-term expansion or localized Taylor series is required.</li>
                <li><strong>Percentage Error Achieved:</strong> Truncation error remains below 0.01% when utilizing 3–4 terms across the entire operational envelope (1° - 30°).</li>
                <li><strong>Convergence Behavior:</strong> The convergence plot confirms that percentage error decreases logarithmically/exponentially as terms are added via manual loops.</li>
                <li><strong>Computational Simplicity vs. Accuracy:</strong> Maclaurin series provide minimal computational complexity near zero, while shifting to a Taylor expansion centered at 10° optimizes accuracy for structures operating around that specific inclination region.</li>
                <li><strong>Valid Angle Range:</strong> Fully reliable across 0° to 30° for structural vertical component estimations (L = 20 m).</li>
            </ul>
        </div>

        <div class="qa-section">
            <h3>Key Exercise Discussion Summary</h3>
            <ul>
                <li><strong>Small Angle Limit:</strong> The small-angle approximation sin(&theta;) &approx; &theta; maintains high fidelity (&le; 0.1% error) up to approximately 4° - 5°. Beyond this threshold, higher-order terms become non-negligible.</li>
                <li><strong>Error Growth Mechanism:</strong> Maclaurin error grows monotonically as the angle increases because polynomial divergence accelerates further from the origin (&theta; = 0°). Centering a Taylor series locally around 10° successfully suppresses this error accumulation in that neighborhood.</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

output_filename = "Series_Analysis_Dashboard.html"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated HTML Dashboard: {output_filename}")