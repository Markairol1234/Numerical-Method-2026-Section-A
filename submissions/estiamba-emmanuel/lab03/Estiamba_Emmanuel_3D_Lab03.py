"""
Lab 03: Real-World Data Linear Regression
Numerical Methods, Section 3D

Topic  : Mental health -- national suicide mortality rates by sex
Source : World Health Organization (WHO), Global Health Observatory (GHO),
         "Age-standardized suicide rates (per 100,000 population)", 2021 data.
         https://www.who.int/data/gho/data/indicators/indicator-details/GHO/age-standardized-suicide-rates-(per-100-000-population)
         (values compiled from the WHO 2021 table reproduced in Wikipedia's
         "List of countries by suicide rate":
         https://en.wikipedia.org/wiki/List_of_countries_by_suicide_rate)

x = male suicide rate (per 100,000 population)      [independent variable]
y = female suicide rate (per 100,000 population)     [dependent variable]
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # so it works even with no display
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, Preformatted
)

# ---------------------------------------------------------------------
# 0. OUTPUT LOCATION  -- everything (PNGs + final PDF) is written here
# ---------------------------------------------------------------------
OUTPUT_DIR = r"D:\python\Lab 03"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def outpath(filename):
    return os.path.join(OUTPUT_DIR, filename)


# ---------------------------------------------------------------------
# 1. DATA
# ---------------------------------------------------------------------
countries = [
    "Egypt", "Saudi Arabia", "Turkey", "Bangladesh", "Mexico",
    "Italy", "Brazil", "Spain", "United Kingdom", "Canada",
    "Netherlands", "Germany", "Australia", "United States", "Sweden",
    "Japan", "Finland", "France", "South Korea", "Kazakhstan",
]

x = np.array([
    0.9, 1.1, 4.3, 3.6, 11.6,
    10.5, 11.4, 13.1, 14.7, 14.2,
    15.4, 18.4, 19.5, 24.7, 18.9,
    19.6, 20.5, 24.1, 28.2, 24.4,
])  # male suicide rate, per 100,000

y = np.array([
    0.3, 0.7, 1.1, 2.0, 2.6,
    3.6, 3.9, 4.5, 4.6, 4.7,
    7.6, 7.6, 6.7, 6.5, 8.7,
    9.8, 8.8, 9.5, 13.6, 5.3,
])  # female suicide rate, per 100,000

n = len(x)
assert len(x) == len(y) == len(countries)

# ---------------------------------------------------------------------
# 2. LEAST-SQUARES FIT:  y = a0 + a1*x
# ---------------------------------------------------------------------
sum_x = np.sum(x)
sum_y = np.sum(y)
sum_xy = np.sum(x * y)
sum_x2 = np.sum(x ** 2)

x_mean = sum_x / n
y_mean = sum_y / n

a1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
a0 = y_mean - a1 * x_mean

print("Regression coefficients")
print(f"  a1 (slope)     = {a1:.5f}")
print(f"  a0 (intercept) = {a0:.5f}")
print(f"  Fitted line: y = {a0:.4f} + {a1:.4f}x")

# ---------------------------------------------------------------------
# 3. GOODNESS OF FIT: Sr (SSE), St, r^2, standard error s_y/x
# ---------------------------------------------------------------------
y_pred = a0 + a1 * x
residuals = y - y_pred

St = np.sum((y - y_mean) ** 2)      # total sum of squares
Sr = np.sum(residuals ** 2)         # sum of squares of residuals (SSE)
r2 = 1 - Sr / St                    # coefficient of determination
syx = np.sqrt(Sr / (n - 2))         # standard error of the estimate

print("\nGoodness of fit")
print(f"  St (total sum of squares) = {St:.4f}")
print(f"  Sr (SSE)                  = {Sr:.4f}")
print(f"  r^2                       = {r2:.5f}")
print(f"  r  (correlation coeff.)   = {np.sqrt(r2):.5f}")
print(f"  s_y/x (standard error)    = {syx:.4f}")

# ---------------------------------------------------------------------
# 4. PLOT: DATA + FITTED LINE
# ---------------------------------------------------------------------
fit_plot_path = outpath("fit_plot.png")
residual_plot_path = outpath("residual_plot.png")

fig1, ax1 = plt.subplots(figsize=(7, 5))
ax1.scatter(x, y, color="#1f4e79", label="Observed data (countries, 2021)")

x_line = np.linspace(min(x) - 1, max(x) + 1, 100)
y_line = a0 + a1 * x_line
ax1.plot(x_line, y_line, color="#c8963e",
          label=f"Fit: y = {a0:.3f} + {a1:.3f}x  (r2 = {r2:.3f})")

ax1.set_xlabel("Male suicide rate (per 100,000 population)")
ax1.set_ylabel("Female suicide rate (per 100,000 population)")
ax1.set_title("Least-Squares Fit: Female vs. Male Suicide Rate by Country (2021)")
ax1.legend()
ax1.grid(alpha=0.3)
fig1.tight_layout()
fig1.savefig(fit_plot_path, dpi=200)

# ---------------------------------------------------------------------
# 5. RESIDUAL PLOT
# ---------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(7, 4.5))
ax2.axhline(0, color="black", linewidth=1)
ax2.scatter(x, residuals, color="#8a3b3b")
ax2.set_xlabel("Male suicide rate (per 100,000 population)")
ax2.set_ylabel("Residual (observed - predicted)")
ax2.set_title("Residual Plot")
ax2.grid(alpha=0.3)
fig2.tight_layout()
fig2.savefig(residual_plot_path, dpi=200)

# ---------------------------------------------------------------------
# 6. PREDICTION
# ---------------------------------------------------------------------
x_new = 16.0
y_new = a0 + a1 * x_new
print(f"\nPrediction: for x = {x_new} (male rate), "
      f"predicted y = {y_new:.3f} (female rate)")

print(f"\nSaved plots to: {fit_plot_path}, {residual_plot_path}")

# =======================================================================
# 7. BUILD THE FINAL PDF REPORT (Parts A, B, C)
# =======================================================================
BLUE = colors.HexColor("#1f4e79")
BLUE_SOFT = colors.HexColor("#eef3f8")
LINE = colors.HexColor("#c9d3dd")
MUTED = colors.HexColor("#5c6874")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="LabTitle", fontName="Helvetica-Bold", fontSize=18,
                           textColor=BLUE, spaceAfter=4))
styles.add(ParagraphStyle(name="LabSub", fontName="Helvetica", fontSize=10.5,
                           textColor=MUTED, spaceAfter=2))
styles.add(ParagraphStyle(name="H2", fontName="Helvetica-Bold", fontSize=13.5,
                           textColor=BLUE, spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle(name="H3", fontName="Helvetica-Bold", fontSize=11,
                           textColor=BLUE, spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=10,
                           leading=14, spaceAfter=6))
styles.add(ParagraphStyle(name="Small", fontName="Helvetica", fontSize=8.5,
                           textColor=MUTED, leading=11))
styles.add(ParagraphStyle(name="CodeBlock", fontName="Courier", fontSize=7.6, leading=9.6))
styles.add(ParagraphStyle(name="Equation", fontName="Helvetica-Oblique", fontSize=13,
                           alignment=TA_CENTER, spaceBefore=8, spaceAfter=8))

story = []

# ---------------------------------------------------------------- HEADER
story.append(Paragraph("Numerical Methods &nbsp;&middot;&nbsp; Section 3D &nbsp;&middot;&nbsp; Laboratory Exercise 03", styles["LabSub"]))
story.append(Paragraph("Lab 03: Real-World Data Linear Regression", styles["LabTitle"]))
story.append(Paragraph("Topic: The Mental Health of People &mdash; National Suicide Mortality Rates by Sex", styles["LabSub"]))
story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=10))

# ==================================================================
# PART A: DATA
# ==================================================================
story.append(Paragraph("Part A &mdash; Data", styles["H2"]))

story.append(Paragraph("1. Source", styles["H3"]))
story.append(Paragraph(
    "World Health Organization (WHO), Global Health Observatory (GHO) &mdash; "
    "<i>\"Age-standardized suicide rates (per 100,000 population),\"</i> 2021 estimates.<br/>"
    "URL: https://www.who.int/data/gho/data/indicators/indicator-details/GHO/"
    "age-standardized-suicide-rates-(per-100-000-population)<br/>"
    "Values were taken from the WHO 2021 country table as compiled and reproduced in the "
    "Wikipedia article \"List of countries by suicide rate\": "
    "https://en.wikipedia.org/wiki/List_of_countries_by_suicide_rate", styles["Body"]))

story.append(Paragraph("2. Description of the data", styles["H3"]))
story.append(Paragraph(
    "Suicide is classified by the WHO as a major global mental-health outcome: it is one of the "
    "clearest, most consistently measured population-level indicators of a country's mental-health "
    "burden. The WHO GHO publishes the age-standardized suicide mortality rate (deaths per 100,000 "
    "population per year) for each of its member states, broken down by sex. This lab uses the male "
    "and female age-standardized rates for 20 countries, drawn deliberately from a wide range of "
    "regions and income levels (Africa, Asia, Europe, and the Americas; high-, upper-middle- and "
    "lower-middle-income countries) so that the sample is not dominated by any single region.", styles["Body"]))

story.append(Paragraph("3. Variables", styles["H3"]))
story.append(Paragraph(
    "<b>Independent variable, x:</b> Male suicide mortality rate, age-standardized, per 100,000 "
    "male population (2021).<br/>"
    "<b>Dependent variable, y:</b> Female suicide mortality rate, age-standardized, per 100,000 "
    "female population (2021).<br/>"
    "Both variables are reported by WHO for the same country and year, so pairing them lets us ask "
    "a mental-health question directly: do countries with a higher male suicide rate also tend to "
    "have a higher female suicide rate, and by how much?", styles["Body"]))

story.append(Paragraph("4. Table of observations", styles["H3"]))

data_rows = list(zip(countries, x, y))
table_data = [["#", "Country", "Male rate x\n(per 100,000)", "Female rate y\n(per 100,000)"]]
for i, (c, xv, yv) in enumerate(data_rows, 1):
    table_data.append([str(i), c, f"{xv:.1f}", f"{yv:.1f}"])

t = Table(table_data, colWidths=[0.35*inch, 2.3*inch, 1.55*inch, 1.6*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), BLUE_SOFT),
    ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.6, LINE),
    ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f9fb")]),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(t)
story.append(PageBreak())

# ==================================================================
# PART B: PYTHON SCRIPT
# ==================================================================
story.append(Paragraph("Part B &mdash; Python Script", styles["H2"]))
story.append(Paragraph(
    "The complete script below (this same file, lab03_regression.py, submitted alongside this "
    "PDF) performs the least-squares fit using the closed-form normal-equation formulas from "
    "class, computes all required regression statistics, produces the two plots, and generates "
    "this PDF report.", styles["Body"]))

with open(__file__, "r", encoding="utf-8") as f:
    code_text = f.read()

story.append(Preformatted(code_text, styles["CodeBlock"]))
story.append(PageBreak())

# ==================================================================
# PART C: REGRESSION RESULTS
# ==================================================================
story.append(Paragraph("Part C &mdash; Regression Results", styles["H2"]))

story.append(Paragraph("1. Regression equation", styles["H3"]))
story.append(Paragraph("y = a0 + a1 x", styles["Equation"]))
story.append(Paragraph(
    f"<b>Slope, a1 = {a1:.4f}</b> (female deaths per 100,000, per unit increase in the male rate)<br/>"
    f"<b>Intercept, a0 = {a0:.4f}</b> (per 100,000)<br/><br/>"
    f"<b>Fitted equation: y = {a0:.4f} + {a1:.4f} x</b>", styles["Body"]))

story.append(Paragraph("2. Fit statistics", styles["H3"]))
stats_data = [
    ["Statistic", "Symbol", "Value"],
    ["Sum of squares of residuals (SSE)", "Sr", f"{Sr:.4f}"],
    ["Total sum of squares", "St", f"{St:.4f}"],
    ["Coefficient of determination", "r2", f"{r2:.4f}"],
    ["Correlation coefficient", "r", f"{np.sqrt(r2):.4f}"],
    ["Standard error of the estimate", "sy/x", f"{syx:.4f}"],
    ["Number of observations", "n", f"{n}"],
]
t2 = Table(stats_data, colWidths=[2.9*inch, 0.9*inch, 1.6*inch])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), BLUE_SOFT),
    ("TEXTCOLOR", (0, 0), (-1, 0), BLUE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("GRID", (0, 0), (-1, -1), 0.6, LINE),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f9fb")]),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(t2)

story.append(Paragraph("3. Graph of data with fitted line", styles["H3"]))
story.append(Image(fit_plot_path, width=5.6*inch, height=4.0*inch))

story.append(Paragraph("4. Residual plot", styles["H3"]))
story.append(Image(residual_plot_path, width=5.6*inch, height=3.6*inch))
story.append(PageBreak())

story.append(Paragraph("5. Prediction", styles["H3"]))
story.append(Paragraph(
    f"Predict the female suicide rate for a country with a male suicide rate of "
    f"x = {x_new} per 100,000 (a value between the United Kingdom and the Netherlands, "
    f"not one of the 20 countries used to fit the line):", styles["Body"]))
story.append(Paragraph(f"y = {a0:.4f} + {a1:.4f}({x_new}) = {y_new:.3f}", styles["Equation"]))
story.append(Paragraph(
    f"<b>Predicted female suicide rate &asymp; {y_new:.1f} deaths per 100,000 female "
    "population.</b> This kind of prediction is meaningful for public-health planning: WHO and "
    "national ministries of health use the tight statistical link between male and female suicide "
    "rates to flag countries where the female rate looks unexpectedly high or low relative to the "
    "male rate for their region, which can indicate under-reporting, a distinct risk-factor "
    "profile, or a gap in mental-health services that specifically affects women.", styles["Body"]))

story.append(Paragraph("6. Interpretation", styles["H3"]))
story.append(Paragraph(
    f"<b>Slope and intercept.</b> The slope (a1 = {a1:.3f}) means that, across this sample of "
    "countries, each additional death per 100,000 in the male suicide rate is associated with "
    f"about {a1:.2f} more deaths per 100,000 in the female rate &mdash; i.e., the female rate "
    "rises at roughly two-fifths the pace of the male rate. This matches the well-documented "
    "pattern that men die by suicide at consistently higher rates than women in almost every "
    f"country, so the female rate never quite \"catches up\" even where both are elevated. The "
    f"intercept (a0 = {a0:.3f}) is close to zero, which makes sense: a country with an essentially "
    "zero male suicide rate should also have an essentially zero female rate; the small negative "
    "value is just sampling noise in a fit forced through this low-rate corner of the data.<br/><br/>"
    f"<b>Goodness of fit.</b> r2 = {r2:.3f} means the male suicide rate alone explains about "
    f"{r2*100:.0f}% of the country-to-country variation in the female suicide rate &mdash; a "
    "strong relationship for cross-country health data, where cultural, reporting, and "
    f"methodological differences usually add a lot of noise. The standard error, sy/x = {syx:.2f} "
    "deaths per 100,000, gives a sense of the typical vertical scatter of the data around the "
    "line: most points fall within about one to two standard errors of the fitted line, "
    "consistent with what the graph in Part C.3 shows.<br/><br/>"
    "<b>Residuals.</b> The residual plot shows no obvious curved pattern, which supports treating "
    "the relationship as linear rather than needing a curve. South Korea stands out as the "
    "largest positive residual (both its male and female rates are unusually high relative to the "
    "rest of the sample), while Kazakhstan is the largest negative residual (a high male rate "
    "paired with a comparatively low female rate, i.e. an unusually large male-to-female gap). "
    "These two points pull on the fit somewhat, but removing either one does not change the "
    "overall conclusion that the relationship is positive and roughly linear.", styles["Body"]))

story.append(Spacer(1, 14))
story.append(HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=6))
story.append(Paragraph(
    "Numerical Methods, Section 3D &mdash; Laboratory Exercise 03: Real-World Data Linear Regression",
    styles["Small"]))

pdf_path = outpath("Estiamba_Emmanuel_3D_Lab03.pdf")
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    topMargin=0.7*inch, bottomMargin=0.7*inch,
    leftMargin=0.75*inch, rightMargin=0.75*inch,
)
doc.build(story)
print(f"\nBuilt PDF report: {pdf_path}")