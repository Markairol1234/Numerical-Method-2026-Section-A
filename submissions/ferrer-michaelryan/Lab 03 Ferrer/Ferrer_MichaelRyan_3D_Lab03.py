import inspect
import os
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# -------------------------------------------------------------------------
# 1. DATASET & LEAST SQUARES CALCULATIONS
# -------------------------------------------------------------------------
regions = [
    "CAR",
    "NCR",
    "NIR",
    "Region I",
    "Region II",
    "Region III",
    "Region IV-A",
    "Region IV-B",
    "Region V",
    "Region VI",
    "Region VII",
    "Region VIII",
    "Region IX",
    "Region X",
    "Region XI",
    "Region XII",
    "Region XIII",
    "BARMM",
]

# x = Total Infrastructure Segments / Bridges / Roads (Count)
x = np.array(
    [
        355,
        307,
        437,
        591,
        522,
        759,
        695,
        661,
        738,
        529,
        435,
        928,
        393,
        469,
        345,
        326,
        466,
        175,
    ],
    dtype=float,
)

# y = Total Infrastructure Length (km)
y = np.array(
    [
        14836.64,
        30932.05,
        17002.91,
        36586.86,
        30479.54,
        39832.49,
        21096.84,
        24990.23,
        25007.43,
        26689.43,
        18873.18,
        37492.87,
        16854.75,
        21040.71,
        17932.10,
        13230.94,
        22533.77,
        6978.95,
    ],
    dtype=float,
)

n = len(x)

sum_x = np.sum(x)
sum_y = np.sum(y)
sum_xy = np.sum(x * y)
sum_x2 = np.sum(x**2)

x_mean = np.mean(x)
y_mean = np.mean(y)

# Slope (a1) and Intercept (a0)
a1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - (sum_x) ** 2)
a0 = y_mean - a1 * x_mean

y_pred = a0 + a1 * x
residuals = y - y_pred

Sr = np.sum(residuals**2)  # SSE
St = np.sum((y - y_mean) ** 2)  # SST
r2 = (St - Sr) / St
sy_x = np.sqrt(Sr / (n - 2))

# Prediction for x = 500 segments
x_target = 500.0
y_predicted = a0 + a1 * x_target

# -------------------------------------------------------------------------
# 2. GENERATE AND SAVE PLOTS (BLACK & BLUE THEME)
# -------------------------------------------------------------------------
plt.figure(figsize=(5.5, 2.7))
plt.scatter(
    x, y, color="#0B2545", label="DPWH Regional Data", zorder=5, s=25, alpha=0.9
)
x_line = np.linspace(min(x), max(x), 100)
plt.plot(
    x_line,
    a0 + a1 * x_line,
    color="#134074",
    linewidth=2,
    label=f"Fit: y = {a0:.1f} + {a1:.1f}x",
)
plt.title(
    "Infrastructure Count vs. Total Length (km)",
    fontsize=9,
    fontweight="bold",
    color="#000814",
)
plt.xlabel("Total Infrastructure Segments (x)", fontsize=7.5, color="#000814")
plt.ylabel("Total Length (y) [km]", fontsize=7.5, color="#000814")
plt.xticks(fontsize=7.5)
plt.yticks(fontsize=7.5)
plt.grid(True, linestyle="--", alpha=0.3, color="#8DA9C4")
plt.legend(fontsize=7.5, frameon=True, facecolor="#EEF4F8")
plt.tight_layout()
plt.savefig("fit_plot.png", dpi=300)
plt.close()

plt.figure(figsize=(5.5, 2.7))
plt.scatter(x, residuals, color="#003566", zorder=5, s=25, alpha=0.9)
plt.axhline(0, color="#000814", linestyle="--", linewidth=1)
plt.title(
    "Residual Plot (y - y_pred)", fontsize=9, fontweight="bold", color="#000814"
)
plt.xlabel("Total Infrastructure Segments (x)", fontsize=7.5, color="#000814")
plt.ylabel("Residuals [km]", fontsize=7.5, color="#000814")
plt.xticks(fontsize=7.5)
plt.yticks(fontsize=7.5)
plt.grid(True, linestyle="--", alpha=0.3, color="#8DA9C4")
plt.tight_layout()
plt.savefig("residual_plot.png", dpi=300)
plt.close()

# -------------------------------------------------------------------------
# 3. REPORTLAB PDF BUILDING
# -------------------------------------------------------------------------
pdf_file = "Surname_Firstname_3D_Lab03.pdf"
doc = SimpleDocTemplate(
    pdf_file,
    pagesize=letter,
    rightMargin=36,
    leftMargin=36,
    topMargin=24,
    bottomMargin=24,
)

styles = getSampleStyleSheet()

# Color Palette: Obsidian Black to Deep Ocean Blue Blends
C_BLACK = colors.HexColor("#000814")
C_NAVY_DARK = colors.HexColor("#0B2545")
C_BLUE_MED = colors.HexColor("#134074")
C_BLUE_ACCENT = colors.HexColor("#003566")
C_SOFT_BLUE = colors.HexColor("#8DA9C4")
C_ICE_BG = colors.HexColor("#EEF4F8")
C_CARD_BG = colors.HexColor("#F6F9FC")
C_BORDER = colors.HexColor("#C3D3E2")
C_TEXT = colors.HexColor("#101820")

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Heading1"],
    fontSize=15,
    leading=18,
    textColor=C_BLACK,
    fontName="Helvetica-Bold",
)
h1_style = ParagraphStyle(
    "PartHeader",
    parent=styles["Heading1"],
    fontSize=12,
    leading=15,
    textColor=C_NAVY_DARK,
    fontName="Helvetica-Bold",
    spaceBefore=6,
    spaceAfter=3,
)
h2_style = ParagraphStyle(
    "SectionHeader",
    parent=styles["Heading2"],
    fontSize=9.5,
    leading=12,
    textColor=C_BLUE_MED,
    fontName="Helvetica-Bold",
    spaceBefore=4,
    spaceAfter=2,
)
body_style = ParagraphStyle(
    "BodyContent",
    parent=styles["Normal"],
    fontSize=8,
    leading=11,
    textColor=C_TEXT,
    spaceAfter=3,
)
meta_style = ParagraphStyle(
    "MetaContent",
    parent=styles["Normal"],
    fontSize=8.5,
    leading=12,
    textColor=C_NAVY_DARK,
)
table_header_style = ParagraphStyle(
    "TableHeaderContent",
    parent=styles["Normal"],
    fontSize=7.5,
    leading=10,
    textColor=colors.white,
    fontName="Helvetica-Bold",
)
code_style = ParagraphStyle(
    "CodeStyle",
    parent=styles["Code"],
    fontSize=5.5,
    leading=7,
    textColor=C_BLACK,
    fontName="Courier",
)

card_num_style = ParagraphStyle(
    "CardNumStyle",
    parent=styles["Normal"],
    fontSize=14,
    leading=16,
    textColor=colors.white,
    fontName="Helvetica-Bold",
    alignment=1,
)
card_title_style = ParagraphStyle(
    "CardTitleStyle",
    parent=styles["Normal"],
    fontSize=7.5,
    leading=9,
    textColor=colors.white,
    fontName="Helvetica-Bold",
    alignment=1,
)
card_text_style = ParagraphStyle(
    "CardTextStyle",
    parent=styles["Normal"],
    fontSize=7,
    leading=9,
    textColor=C_TEXT,
    alignment=1,
)

elements = []

# Metadata Header
elements.append(
    Paragraph("NUMERICAL METHODS: LABORATORY REPORT 03", title_style)
)
elements.append(
    Paragraph(
        "<b>Topic:</b> Real-World Data Linear Regression (DPWH Infrastructure"
        " Data)",
        body_style,
    )
)
elements.append(Spacer(1, 3))

info_data = [[
    Paragraph("<b>Name:</b> Michael Ryan L. Ferrer", meta_style),
    Paragraph("<b>Section:</b> BSCE-3D", meta_style),
    Paragraph("<b>Date:</b> September 07, 2026", meta_style),
]]
info_table = Table(info_data, colWidths=[200, 150, 190])
info_table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ICE_BG),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 1, C_BORDER),
    ])
)
elements.append(info_table)
elements.append(Spacer(1, 4))
elements.append(
    HRFlowable(
        width="100%",
        thickness=1.5,
        color=C_BLUE_MED,
        spaceBefore=2,
        spaceAfter=4,
    )
)

# PART A. DATA
elements.append(Paragraph("PART A. Data", h1_style))
elements.append(
    HRFlowable(
        width="100%",
        thickness=1,
        color=C_SOFT_BLUE,
        spaceBefore=1,
        spaceAfter=4,
    )
)
data_info_text = """
<b>Source & Full URL:</b> Department of Public Works and Highways (DPWH) Regional Infrastructure Summary<br/>
<b>URL:</b> https://www.dpwh.gov.ph/dpwh/gis/stat<br/>
<b>Description:</b> Summary of national road and bridge counts and total lengths (km) across administrative regions in the Philippines.<br/>
<b>Variables:</b> Independent (<i>x</i>) = Total Infrastructure Count | Dependent (<i>y</i>) = Total Length (km)
"""
elements.append(Paragraph(data_info_text, body_style))

obs_headers = [
    Paragraph("Region", table_header_style),
    Paragraph("Total Count (x)", table_header_style),
    Paragraph("Total Length in km (y)", table_header_style),
]
obs_rows = [obs_headers]
for i in range(n):
  obs_rows.append([regions[i], f"{x[i]:.0f}", f"{y[i]:,.2f}"])

obs_table = Table(obs_rows, colWidths=[140, 200, 200])
obs_table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_BLACK),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_ICE_BG]),
    ])
)
elements.append(obs_table)
elements.append(Spacer(1, 6))

# PART B. PYTHON SCRIPT
elements.append(Paragraph("PART B. Python Script", h1_style))
elements.append(
    HRFlowable(
        width="100%",
        thickness=1,
        color=C_SOFT_BLUE,
        spaceBefore=1,
        spaceAfter=4,
    )
)

try:
  current_script_code = inspect.getsource(
      inspect.getmodule(inspect.currentframe())
  )
except Exception:
  current_script_code = (
      "# Script source execution text embedded automatically."
  )

code_snippet = (
    current_script_code[:1350]
    + "\n\n# ... [Script Code Truncated for Page Layout] ..."
)
elements.append(Preformatted(code_snippet, code_style))
elements.append(Spacer(1, 6))

# PART C. REGRESSION RESULTS
elements.append(Paragraph("PART C. Regression Results", h1_style))
elements.append(
    HRFlowable(
        width="100%",
        thickness=1,
        color=C_SOFT_BLUE,
        spaceBefore=1,
        spaceAfter=4,
    )
)

card_1 = [
    [Paragraph("01", card_num_style)],
    [Paragraph("MODEL FIT", card_title_style)],
    [Paragraph(f"<b>y = {a0:.1f} + {a1:.1f}x</b>", card_text_style)],
]
card_2 = [
    [Paragraph("02", card_num_style)],
    [Paragraph("ACCURACY", card_title_style)],
    [Paragraph(f"<b>r² = {r2:.4f}</b>", card_text_style)],
]
card_3 = [
    [Paragraph("03", card_num_style)],
    [Paragraph("ERROR", card_title_style)],
    [Paragraph(f"<b>s<sub>y/x</sub> = {sy_x:,.0f} km</b>", card_text_style)],
]
card_4 = [
    [Paragraph("04", card_num_style)],
    [Paragraph("PREDICTION", card_title_style)],
    [Paragraph(f"<b>{y_predicted:,.1f} km</b>", card_text_style)],
]


def make_card_table(content):
  t = Table(content, colWidths=[125])
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (0, 0), C_BLACK),
          ("BACKGROUND", (0, 1), (0, 1), C_BLUE_MED),
          ("BACKGROUND", (0, 2), (0, 2), C_CARD_BG),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 2),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
          ("BOX", (0, 0), (-1, -1), 1, C_BORDER),
      ])
  )
  return t


cards_table = Table(
    [[
        make_card_table(card_1),
        make_card_table(card_2),
        make_card_table(card_3),
        make_card_table(card_4),
    ]],
    colWidths=[132, 132, 132, 132],
)
cards_table.setStyle(
    TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ])
)
elements.append(cards_table)
elements.append(Spacer(1, 4))

# 1. Regression Equation & Parameters
elements.append(
    Paragraph("1. Regression Equation & Calculated Metrics", h2_style)
)
metrics_table_data = [
    [
        Paragraph("Metric", table_header_style),
        Paragraph("Formula / Notation", table_header_style),
        Paragraph("Calculated Value", table_header_style),
    ],
    ["Fitted Regression Model", "y = a0 + a1 * x", f"y = {a0:.4f} + {a1:.4f}x"],
    ["Intercept (a0)", "a0 = y_bar - a1 * x_bar", f"{a0:,.4f} km"],
    [
        "Slope (a1)",
        "a1 = (n*Σxy - ΣxΣy) / (n*Σx² - (Σx)²)",
        f"{a1:.4f} km / segment",
    ],
    ["Sum of Squared Residuals (SSE)", "Sr = Σ(y - y_pred)²", f"{Sr:,.2f}"],
    ["Coefficient of Determination", "r² = (St - Sr) / St", f"{r2:.4f}"],
    [
        "Standard Error of Estimate",
        "s_y/x = sqrt(Sr / (n - 2))",
        f"{sy_x:,.4f} km",
    ],
]

table = Table(metrics_table_data, colWidths=[165, 185, 190])
table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_NAVY_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, C_ICE_BG]),
    ])
)
elements.append(table)
elements.append(Spacer(1, 4))

# 2. Plots
elements.append(
    Paragraph("2. Graph with Fitted Line & Residual Plot", h2_style)
)
img_table = Table(
    [[
        Image("fit_plot.png", width=260, height=130),
        Image("residual_plot.png", width=260, height=130),
    ]],
    colWidths=[270, 270],
)
img_table.setStyle(
    TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ])
)
elements.append(img_table)
elements.append(Spacer(1, 4))

# 3. Interpretation of Results
elements.append(Paragraph("3. Interpretation of Results", h2_style))
elements.append(
    Paragraph(
        "The simple linear regression model reveals a moderate positive linear"
        " correlation between total infrastructure counts and total network"
        " lengths across DPWH administrative regions.",
        body_style,
    )
)

bullet_interpretation = f"""
• <b>Slope (a1 = {a1:.4f}):</b> Each additional infrastructure segment adds approximately <b>{a1:.2f} km</b> of road/bridge network length.<br/>
• <b>Intercept (a0 = {a0:,.4f}):</b> Represents the baseline regional network span offset when segment count is zero.<br/>
• <b>Coefficient of Determination (r² = {r2:.4f}):</b> <b>{r2 * 100:.2f}%</b> of total regional length variance is explained by the number of segments.<br/>
• <b>Standard Error (s_y/x = {sy_x:,.4f}):</b> Regional predictions deviate by an average of <b>{sy_x:,.2f} km</b>.<br/>
• <b>Residuals Analysis:</b> Shows higher variance in regions like NCR (high density) and BARMM, indicating varying average segment lengths across regions.
"""
elements.append(Paragraph(bullet_interpretation, body_style))
elements.append(Spacer(1, 4))

# 4. Out-of-Sample Prediction
elements.append(Paragraph("4. Out-of-Sample Prediction", h2_style))

pred_box_data = [[
    Paragraph(
        f"<b>Target Segment Count (x):</b> {x_target:.0f} segments |"
        f" <b>Predicted Length (y):</b> <b>{y_predicted:,.2f} km</b><br/>"
        f"<b>Substitution:</b> y = {a0:.4f} + ({a1:.4f} * {x_target:.0f})<br/>"
        f"<b>Significance:</b> Provides baseline linear forecasting for"
        " budgeting and scaling regional infrastructure expansion.",
        body_style,
    )
]]
pred_table = Table(pred_box_data, colWidths=[540])
pred_table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ICE_BG),
        ("BOX", (0, 0), (-1, -1), 1, C_BLUE_MED),
        ("PADDING", (0, 0), (-1, -1), 4),
    ])
)
elements.append(pred_table)

# Build Document
doc.build(elements)

# Clean up image files
if os.path.exists("fit_plot.png"):
  os.remove("fit_plot.png")
if os.path.exists("residual_plot.png"):
  os.remove("residual_plot.png")

print(f"Report successfully compiled to '{pdf_file}'.")