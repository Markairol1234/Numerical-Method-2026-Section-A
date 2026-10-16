# ============================================================
# philippines_population_regression.py
# Simple Linear Regression by Least Squares
# y = a0 + a1 * x
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ------------------------------------------------------------
# 1. PAIRED OBSERVATIONS (2010 to 2025)
#    Source: Macrotrends - Philippines Population [citation:1]
#    x = Year, y = Population (persons)
# ------------------------------------------------------------
x = np.array([2010, 2011, 2012, 2013, 2014, 2015, 2016,
              2017, 2018, 2019, 2020, 2021, 2022, 2023,
              2024, 2025], dtype=float)

y = np.array([94636700, 96337913, 98032317, 99700107,
              101325201, 103031365, 104875266, 106738501,
              108568836, 110380804, 112190977, 113880328,
              115559009, 117337368, 119106224, 120864358],
             dtype=float)

# ------------------------------------------------------------
# 2. LEAST SQUARES FORMULAS
#    a1 = (n*Sxy - Sx*Sy) / (n*Sxx - Sx^2)
#    a0 = y_bar - a1 * x_bar
# ------------------------------------------------------------
n = len(x)
Sx  = np.sum(x)
Sy  = np.sum(y)
Sxy = np.sum(x * y)
Sxx = np.sum(x * x)

a1 = (n * Sxy - Sx * Sy) / (n * Sxx - Sx * Sx)
a0 = (Sy / n) - a1 * (Sx / n)

print(f"Regression equation: y = {a0:.2f} + {a1:.2f} * x")
print(f"Intercept a0 = {a0:,.2f}")
print(f"Slope a1     = {a1:,.2f} persons/year")

# ------------------------------------------------------------
# 3. GOODNESS OF FIT
#    Sr (SSE) = sum((y_i - y_hat_i)^2)
#    St (SST) = sum((y_i - y_bar)^2)
#    r2 = (St - Sr) / St
#    sy/x = sqrt(Sr / (n - 2))
# ------------------------------------------------------------
y_hat = a0 + a1 * x
Sr = np.sum((y - y_hat) ** 2)
St = np.sum((y - np.mean(y)) ** 2)
r2 = (St - Sr) / St
syx = np.sqrt(Sr / (n - 2))

print(f"Sr (SSE)                  = {Sr:,.2f}")
print(f"St (SST)                  = {St:,.2f}")
print(f"r2                        = {r2:.6f}")
print(f"Standard error sy/x       = {syx:,.2f} persons")

# ------------------------------------------------------------
# 4. PREDICTION FOR x NOT IN DATASET
# ------------------------------------------------------------
x_pred = 2030.0
y_pred = a0 + a1 * x_pred
print(f"Prediction at x = {x_pred:.0f}: y = {y_pred:,.0f} persons")

# ------------------------------------------------------------
# 5. RESIDUALS
# ------------------------------------------------------------
residuals = y - y_hat

# ------------------------------------------------------------
# 6. BUILD PDF REPORT
# ------------------------------------------------------------
with PdfPages("philippines_population_regression.pdf") as pdf:

    # --- Page 1: Title + Dataset Table + Regression Summary ---
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.axis("off")

    ax.text(0.5, 0.95, "Simple Linear Regression: Philippines Population",
            ha="center", fontsize=14, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.92, "(2010 - 2025, Least Squares Fit)",
            ha="center", fontsize=11, transform=ax.transAxes)

    # Dataset table
    table_data = [["Year", "Population (persons)"]]
    for xi, yi in zip(x, y):
        table_data.append([f"{int(xi)}", f"{int(yi):,}"])

    table = ax.table(cellText=table_data,
                     loc="upper center",
                     cellLoc="center",
                     bbox=[0.15, 0.45, 0.70, 0.42])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)

    # Regression summary text
    summary = (
        f"Regression Equation:  y = {a0:,.2f} + {a1:,.2f} \u00b7 x\n\n"
        f"Slope a1 = {a1:,.2f} persons/year\n"
        f"Intercept a0 = {a0:,.2f}\n\n"
        f"Sr (SSE) = {Sr:,.2f}\n"
        f"r\u00b2 = {r2:.6f}\n"
        f"Standard error s_y/x = {syx:,.2f} persons\n\n"
        f"Prediction at x = 2030: {y_pred:,.0f} persons"
    )
    ax.text(0.5, 0.38, summary, ha="center", va="top",
            fontsize=10, transform=ax.transAxes,
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="lightyellow",
                      edgecolor="gray"))

    pdf.savefig(fig)
    plt.close(fig)

    # --- Page 2: Data + Fitted Line ---
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.scatter(x, y, color="steelblue", s=50, label="Data points")
    ax.plot(x, y_hat, color="red", linewidth=2,
            label=f"Fitted line: y = {a0:,.0f} + {a1:,.0f}x")

    # Mark the prediction point
    ax.scatter([x_pred], [y_pred], color="green", s=80,
               marker="*", zorder=5,
               label=f"Prediction (2030): {y_pred:,.0f}")

    ax.set_xlabel("Year (x)", fontsize=11)
    ax.set_ylabel("Population (persons)", fontsize=11)
    ax.set_title("Philippines Population vs Year\n(Data points + Least Squares Fitted Line)",
                 fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)

    # --- Page 3: Residual Plot ---
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.scatter(x, residuals, color="purple", s=50)
    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.set_xlabel("Year (x)", fontsize=11)
    ax.set_ylabel("Residual (y - y_hat)  [persons]", fontsize=11)
    ax.set_title("Residual Plot", fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)

print("PDF saved: philippines_population_regression.pdf")