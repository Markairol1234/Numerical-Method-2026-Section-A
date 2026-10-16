# ============================================================
# lab02_aranjuez.py
# Reads Depth vs Timestamp from an Excel workbook, computes
# forward / backward / centered finite differences, writes them
# back to columns G/H/I, generates a self-contained HTML report
# (lab02_aranjuez.html) with base64-embedded charts, AND opens
# a matplotlib window showing the three derivative series.
#
# Run:
#   python "D:\che school 2627\lab02\lab02_aranjuez.py"
# ============================================================

# ---------------- imports ----------------
import base64
import datetime as dt
import io

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")           # GUI backend — enables plt.show() pop-up
import matplotlib.pyplot as plt
import openpyxl

# ============================================================
# CONFIG — change these paths if needed
# ============================================================
FILE_PATH = r"D:\che school 2627\Data 01.xlsx"
OUT_HTML  = r"D:\che school 2627\lab02\lab02_aranjuez.html"

# ============================================================
# 1. Load the workbook (auto-detect sheet + header row)
# ============================================================
xl = pd.ExcelFile(FILE_PATH)
print("Sheets in workbook:", xl.sheet_names)
sheet_name = xl.sheet_names[0]
print(f"Using sheet: '{sheet_name}'")

# --- read with no header to find the real header row ---
raw = pd.read_excel(FILE_PATH, sheet_name=sheet_name, header=None)
header_row = None
for r in range(min(15, len(raw))):
    joined = " ".join(str(v).lower() for v in raw.iloc[r].tolist())
    if "timestamp" in joined and "depth" in joined:
        header_row = r
        break
if header_row is None:
    raise ValueError("Could not find a header row containing 'Timestamp' and 'Depth'.")

print(f"Detected header at Excel row {header_row + 1}")

# --- re-read using that header row ---
df = pd.read_excel(FILE_PATH, sheet_name=sheet_name, header=header_row)
df.columns = df.columns.astype(str).str.strip()
print("Columns found:", df.columns.tolist())

# --- locate the two columns case-insensitively ---
ts_col    = next((c for c in df.columns
                  if c.lower().replace(" ", "") in ("timestamp", "time", "datetime")), None)
depth_col = next((c for c in df.columns if "depth" in c.lower()), None)
if ts_col is None or depth_col is None:
    raise ValueError(f"Required columns not found. Available: {df.columns.tolist()}")

print(f"Using timestamp column: '{ts_col}'")
print(f"Using depth column:     '{depth_col}'")

timestamps = pd.to_datetime(df[ts_col], errors="coerce")
depth      = pd.to_numeric(df[depth_col], errors="coerce").to_numpy(dtype=float)

# ============================================================
# 2. Finite differences (forward / backward / centered)
# ============================================================
dt_sec   = timestamps.diff().dt.total_seconds().to_numpy()
first_dt = dt_sec[~np.isnan(dt_sec)][0] if np.any(~np.isnan(dt_sec)) else 1.0
dt_fill  = np.where(np.isnan(dt_sec), first_dt, dt_sec)
n        = len(depth)

fwd = np.full(n, np.nan)
bwd = np.full(n, np.nan)
ctr = np.full(n, np.nan)

for i in range(n - 1):
    fwd[i] = (depth[i + 1] - depth[i]) / dt_fill[i + 1]
for i in range(1, n):
    bwd[i] = (depth[i] - depth[i - 1]) / dt_fill[i]
for i in range(1, n - 1):
    ctr[i] = (depth[i + 1] - depth[i - 1]) / (dt_fill[i] + dt_fill[i + 1])

# ============================================================
# 3. Write results back to Excel (columns G, H, I)
# ============================================================
wb = openpyxl.load_workbook(FILE_PATH)
ws = wb[sheet_name]

hdr_excel  = header_row + 1                 # 1-based Excel row of the header
data_excel = hdr_excel + 1                  # first data row

ws.cell(row=hdr_excel, column=7, value="Forward Diff (m/s)")
ws.cell(row=hdr_excel, column=8, value="Backward Diff (m/s)")
ws.cell(row=hdr_excel, column=9, value="Centered Diff (m/s)")

for i in range(n):
    r = data_excel + i
    ws.cell(row=r, column=7, value=None if np.isnan(fwd[i]) else float(fwd[i]))
    ws.cell(row=r, column=8, value=None if np.isnan(bwd[i]) else float(bwd[i]))
    ws.cell(row=r, column=9, value=None if np.isnan(ctr[i]) else float(ctr[i]))

wb.save(FILE_PATH)
print(f"Results saved to columns G, H, I of '{sheet_name}'.")

# ============================================================
# 4. Helper: matplotlib figure -> base64 <img> tag
# ============================================================
def fig_to_img_tag(fig, alt="chart"):
    """Save fig to a PNG buffer, base64-encode, and close it.
    NOTE: this consumes the figure, so use a *copy* for the pop-up."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    return f'<img class="chart" src="data:image/png;base64,{b64}" alt="{alt}">'

# ============================================================
# 5. Build the three charts for the HTML report
#    (we also keep a copy of the biggest one for the pop-up)
# ============================================================

# --- (a) original series ---
fig_a, ax = plt.subplots(figsize=(11, 4))
ax.plot(timestamps, depth, color="tab:blue", linewidth=1)
ax.set_title("Depth vs Timestamp (raw series)")
ax.set_xlabel("Timestamp")
ax.set_ylabel("Depth (m)")
ax.grid(True)
ax.tick_params(axis="x", rotation=45)
img_series = fig_to_img_tag(fig_a, "raw series")
plt.close(fig_a)

# --- (b) forward / backward / centered side-by-side-by-side ---
fig_b, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
axes[0].plot(timestamps, fwd, color="tab:blue",  linewidth=1)
axes[0].set_title("Forward Difference")
axes[1].plot(timestamps, bwd, color="tab:green", linewidth=1)
axes[1].set_title("Backward Difference")
axes[2].plot(timestamps, ctr, color="tab:red",   linewidth=1)
axes[2].set_title("Centered Difference")
for axx in axes:
    axx.set_xlabel("Timestamp")
    axx.grid(True)
    axx.tick_params(axis="x", rotation=45)
axes[0].set_ylabel("d(Depth)/dt  (m/s)")
fig_b.suptitle("Finite Difference Approximations of Depth vs Time", fontsize=14)
fig_b.tight_layout()
img_diffs = fig_to_img_tag(fig_b, "finite differences")
plt.close(fig_b)

# --- (c) histogram of centered differences ---
fig_c, ax = plt.subplots(figsize=(9, 4))
valid = ctr[~np.isnan(ctr)]
if valid.size:
    ax.hist(valid, bins=40, color="tab:purple", edgecolor="white")
ax.set_title("Distribution of centered differences")
ax.set_xlabel("d(Depth)/dt  (m/s)")
ax.set_ylabel("count")
ax.grid(True, alpha=0.3)
img_hist = fig_to_img_tag(fig_c, "histogram")
plt.close(fig_c)

# ============================================================
# 6. Summary statistics
# ============================================================
def safe_stats(arr):
    v = arr[~np.isnan(arr)]
    if v.size == 0:
        return dict(n=0, mean=np.nan, std=np.nan, mn=np.nan, mx=np.nan)
    return dict(n=int(v.size), mean=float(v.mean()), std=float(v.std()),
                mn=float(v.min()), mx=float(v.max()))

sf, sb, sc = safe_stats(fwd), safe_stats(bwd), safe_stats(ctr)

t_start    = timestamps.dropna().iloc[0]
t_end      = timestamps.dropna().iloc[-1]
duration_h = (t_end - t_start).total_seconds() / 3600.0

def row_html(name, s):
    return (f"<tr><td>{name}</td><td>{s['n']}</td>"
            f"<td>{s['mean']:.6g}</td><td>{s['std']:.6g}</td>"
            f"<td>{s['mn']:.6g}</td><td>{s['mx']:.6g}</td></tr>")

table_rows = (row_html("Forward",  sf) +
              row_html("Backward", sb) +
              row_html("Centered", sc))

# ============================================================
# 7. HTML report — CSS as plain string + .format() template
# ============================================================
generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

CSS = """
:root {
  --ink:#0b2531; --muted:#5b7180; --line:#d7e3e6;
  --teal:#0e7c86; --teal-dark:#0b4f6c; --amber:#ffb238;
}
* { box-sizing: border-box; }
body {
  margin:0; font-family:'Segoe UI', Arial, sans-serif; color:var(--ink);
  background:#f2fafa; line-height:1.55;
}
header.hero {
  background:linear-gradient(135deg,#0e7c86 0%, #0b4f6c 100%);
  color:#fff; padding:32px 28px 60px 28px; position:relative;
}
header.hero .kicker {
  display:inline-block; background:rgba(255,255,255,0.15); padding:4px 10px;
  border-radius:20px; font-size:11px; letter-spacing:0.08em; text-transform:uppercase;
}
header.hero h1 { margin:12px 0 6px 0; font-size:32px; }
header.hero .sub { opacity:0.85; font-size:14px; }
.wave { position:absolute; left:0; right:0; bottom:-2px; height:60px; }
.wave svg { width:100%; height:100%; display:block; }
main { max-width:1100px; margin:0 auto; padding:24px 20px 40px; }
section.panel {
  background:#fff; border-radius:16px; padding:22px 24px; margin-bottom:22px;
  box-shadow:0 6px 24px rgba(11,79,108,0.08);
}
h2 { margin:0 0 12px 0; color:var(--teal-dark); font-size:20px; }
h3.label {
  font-size:11px; letter-spacing:0.08em; text-transform:uppercase;
  color:var(--muted); margin:18px 0 8px 0; font-weight:700;
}
.chart { max-width:100%; height:auto; border-radius:10px; display:block; }
table { border-collapse:collapse; width:100%; font-size:13px; margin:10px 0; }
th, td { border-bottom:1px solid var(--line); padding:9px 10px; text-align:left; }
th {
  background:#effaf9; color:var(--teal-dark); text-transform:uppercase;
  font-size:10.5px; letter-spacing:0.05em;
}
tr:last-child td { border-bottom:none; }
.stat-grid {
  display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
  gap:14px; margin:14px 0;
}
.stat-card {
  border-radius:14px; padding:12px 14px; background:#f7fcfc;
  border-left:5px solid var(--teal); box-shadow:0 4px 14px rgba(11,79,108,0.06);
}
.stat-card .label {
  font-size:10.5px; text-transform:uppercase; color:var(--muted);
  font-weight:700; letter-spacing:0.06em;
}
.stat-card .value { font-size:20px; font-weight:800; color:var(--ink); margin-top:4px; }
footer { text-align:center; color:var(--muted); font-size:11.5px; padding:14px; }
code.eq {
  display:block; background:var(--teal-dark); color:#eafbf8;
  padding:12px 14px; border-radius:10px;
  font-family:'Courier New',monospace; font-size:12.5px;
  margin:10px 0; overflow-x:auto;
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab 02 &mdash; Finite Differences of Reservoir Depth</title>
<style>
{css}
</style>
</head>
<body>

<header class="hero">
  <span class="kicker">Lab Activity 02 &middot; lab02_aranjuez.py</span>
  <h1>Finite Differences of Reservoir Depth</h1>
  <div class="sub">
    Forward, backward, and centered derivatives of Depth vs Timestamp &middot;
    workbook: {file_path} &middot; sheet: {sheet_name} &middot;
    generated {generated}
  </div>
  <div class="wave">
    <svg viewBox="0 0 1200 60" preserveAspectRatio="none">
      <path d="M0,32 C150,60 350,0 600,28 C850,56 1050,8 1200,30 L1200,60 L0,60 Z"
            fill="#f2fafa"/>
    </svg>
  </div>
</header>

<main>

  <section class="panel">
    <h2>1. Raw time series</h2>
    <p>
      Depth measurements from the source workbook, plotted against the
      corresponding timestamps. Record spans
      <strong>{duration_h:.2f} hours</strong>
      ({t_start} &rarr; {t_end}) with <strong>{n}</strong> data points.
    </p>
    <div class="stat-grid">
      <div class="stat-card"><div class="label">Points</div><div class="value">{n}</div></div>
      <div class="stat-card"><div class="label">Duration</div><div class="value">{duration_h:.2f} h</div></div>
      <div class="stat-card"><div class="label">Mean &Delta;t</div><div class="value">{first_dt:.1f} s</div></div>
    </div>
    {img_series}
  </section>

  <section class="panel">
    <h2>2. Finite differences</h2>
    <p>Three numerical derivatives computed from the sampled data:</p>
    <code class="eq">Forward  : f'(t_i) &asymp; (y[i+1] &minus; y[i])   / &Delta;t
Backward : f'(t_i) &asymp; (y[i]   &minus; y[i-1]) / &Delta;t
Centered : f'(t_i) &asymp; (y[i+1] &minus; y[i-1]) / (&Delta;t_i + &Delta;t_i+1)</code>
    {img_diffs}
  </section>

  <section class="panel">
    <h2>3. Summary statistics</h2>
    <p>NaN edges (first/last rows where the formula can't be applied) are excluded.</p>
    <table>
      <tr>
        <th>Method</th><th>Count</th><th>Mean</th>
        <th>Std</th><th>Min</th><th>Max</th>
      </tr>
      {table_rows}
    </table>
    <h3 class="label">Distribution of centered differences</h3>
    {img_hist}
  </section>

  <section class="panel">
    <h2>4. Where the results live</h2>
    <p>
      All three derivative columns have been written back into the source workbook
      <code>{file_path}</code> in sheet <code>{sheet_name}</code>:
    </p>
    <table>
      <tr><th>Column</th><th>Contents</th></tr>
      <tr><td>G</td><td>Forward Diff (m/s)</td></tr>
      <tr><td>H</td><td>Backward Diff (m/s)</td></tr>
      <tr><td>I</td><td>Centered Diff (m/s)</td></tr>
    </table>
    <p style="color:var(--muted);font-size:12.5px;">
      Header written on Excel row {header_excel} and data begins at row {data_excel},
      matching the original layout.
    </p>
  </section>

</main>

<footer>
  Generated by <code>lab02_aranjuez.py</code> &mdash;
  every number above was computed in Python; the page contains no live computation.
</footer>

</body>
</html>
"""

html = HTML_TEMPLATE.format(
    css=CSS,
    file_path=FILE_PATH.replace("\\", "/"),
    sheet_name=sheet_name,
    generated=generated,
    duration_h=duration_h,
    t_start=t_start,
    t_end=t_end,
    n=n,
    first_dt=first_dt,
    img_series=img_series,
    img_diffs=img_diffs,
    img_hist=img_hist,
    table_rows=table_rows,
    header_excel=hdr_excel,
    data_excel=data_excel,
)

# ============================================================
# 8. Write the HTML file
# ============================================================
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML report written to: {OUT_HTML}")

# ============================================================
# 9. POP-UP WINDOW — show the three derivative series live
# ============================================================
fig_show, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)

axes[0].plot(timestamps, fwd, color="tab:blue",  linewidth=1)
axes[0].set_title("Forward Difference")
axes[1].plot(timestamps, bwd, color="tab:green", linewidth=1)
axes[1].set_title("Backward Difference")
axes[2].plot(timestamps, ctr, color="tab:red",   linewidth=1)
axes[2].set_title("Centered Difference")

for axx in axes:
    axx.set_xlabel("Timestamp")
    axx.grid(True)
    axx.tick_params(axis="x", rotation=45)

axes[0].set_ylabel("d(Depth)/dt  (m/s)")
fig_show.suptitle("Finite Difference Approximations of Depth vs Time", fontsize=14)
fig_show.tight_layout()

print("Opening plot window — close it to exit the script.")
plt.show()