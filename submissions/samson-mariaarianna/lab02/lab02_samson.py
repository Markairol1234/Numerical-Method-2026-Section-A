"""
NM-Lab02 - Fitting a Curve to the Dam
Complete laboratory script

Requirements covered:
- Reads the raw reservoir stage log from Excel.
- Converts timestamps to elapsed hours.
- Recomputes first finite differences:
    * forward difference at the first point
    * central difference at interior points
    * backward difference at the last point
- Computes the second finite difference.
- Fits the four-parameter logistic model using scipy.optimize.curve_fit
  with Levenberg-Marquardt (method="lm") and maxfev=20000.
- Computes residuals, SSE, SST, R^2, standard error of estimate,
  parameter standard errors, t statistics, and two-tailed p-values.
- Computes analytical first and second derivatives of the fitted curve.
- Finds the maximum continuous filling rate.
- Integrates the fitted curve using scipy.integrate.quad.
- Cross-checks the area using np.trapezoid on the raw readings.
- Generates a standalone HTML dashboard.
- JavaScript is used only for dashboard tab/display behavior.
  All numerical calculations are performed in Python.

Run:
    python lab02_samson.py

or:
    python lab02_samson.py "C:\\path\\to\\Data 01.xlsx"
"""

from __future__ import annotations

import base64
import io
import sys
from pathlib import Path
from html import escape

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
from scipy.integrate import quad


# ============================================================
# 1. FILE LOCATIONS AND DATA LOADING
# ============================================================

def find_input_workbook() -> Path:
    """
    Find the Excel dataset without requiring the user to edit
    a path inside the source code.

    Priority:
    1. Path supplied on the command line.
    2. Data 01.xlsx beside this Python file.
    3. Data 01.xlsx in the current working directory.
    4. Data 01.xlsx in the user's Downloads folder.
    """
    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1]).expanduser()
        if candidate.exists():
            return candidate.resolve()
        raise FileNotFoundError(
            f"The Excel file supplied on the command line was not found:\n"
            f"{candidate}"
        )

    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "Data 01.xlsx",
        Path.cwd() / "Data 01.xlsx",
        Path.home() / "Downloads" / "Data 01.xlsx",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    raise FileNotFoundError(
        "Could not find 'Data 01.xlsx'. Put the workbook beside this "
        "Python script, put it in your Downloads folder, or run:\n\n"
        'python lab02_samson.py "C:\\path\\to\\Data 01.xlsx"'
    )


def normalize_text(value) -> str:
    """Convert a cell to normalized text for header detection."""
    if pd.isna(value):
        return ""
    return str(value).strip().lower().replace("\n", " ")


def find_data_sheet_and_header(xlsx_path: Path) -> tuple[str, int]:
    """
    Inspect all worksheets and find a row containing timestamp and
    reservoir-stage/depth headers. This avoids assuming that the first
    Excel row is the header row.
    """
    workbook = pd.ExcelFile(xlsx_path)

    timestamp_words = ("timestamp", "date time", "datetime", "date/time")
    stage_words = ("depth (m)", "depth", "stage", "reservoir stage")

    for sheet_name in workbook.sheet_names:
        raw = pd.read_excel(
            xlsx_path,
            sheet_name=sheet_name,
            header=None,
            nrows=30,
        )

        for row_number in range(len(raw)):
            cells = [normalize_text(v) for v in raw.iloc[row_number].tolist()]

            has_timestamp = any(
                any(word in cell for word in timestamp_words)
                for cell in cells
                if cell
            )
            has_stage = any(
                any(word in cell for word in stage_words)
                for cell in cells
                if cell
            )

            if has_timestamp and has_stage:
                return sheet_name, row_number

    raise ValueError(
        "Could not identify a worksheet/header row containing both "
        "a timestamp column and a reservoir stage/depth column."
    )


def identify_columns(columns) -> tuple[str, str]:
    """
    Identify timestamp and raw stage/depth columns from the detected
    header row. Existing derivative columns are deliberately ignored.
    """
    timestamp_col = None
    stage_col = None

    for col in columns:
        text = normalize_text(col)

        if timestamp_col is None and any(
            word in text
            for word in ("timestamp", "date time", "datetime", "date/time")
        ):
            timestamp_col = col

        # Prefer the raw depth/stage column and avoid derivative columns.
        if stage_col is None:
            if text in ("depth (m)", "depth", "stage"):
                stage_col = col
            elif "reservoir stage" in text and "rate" not in text:
                stage_col = col

    if timestamp_col is None or stage_col is None:
        raise ValueError(
            "Could not identify the required timestamp and raw stage/depth "
            f"columns. Columns found: {list(columns)}"
        )

    return timestamp_col, stage_col


def load_raw_data(xlsx_path: Path) -> tuple[pd.DataFrame, str, int, str, str]:
    """
    Load the worksheet after dynamically locating its header row.
    """
    sheet_name, header_row = find_data_sheet_and_header(xlsx_path)

    df = pd.read_excel(
        xlsx_path,
        sheet_name=sheet_name,
        header=header_row,
    )

    timestamp_col, stage_col = identify_columns(df.columns)

    data = pd.DataFrame({
        "Timestamp": pd.to_datetime(
            df[timestamp_col],
            errors="coerce",
        ),
        "Depth (m)": pd.to_numeric(
            df[stage_col],
            errors="coerce",
        ),
    })

    # Keep only actual readings.
    data = data.dropna(subset=["Timestamp", "Depth (m)"]).copy()
    data = data.sort_values("Timestamp").reset_index(drop=True)

    # Lab 02 uses the 96-reading, one-day stage log. If the workbook
    # contains additional days/readings, carry forward only the first
    # 96 valid readings required by the activity.
    if len(data) < 96:
        raise ValueError(
            f"Only {len(data)} valid reservoir readings were found; "
            "Lab 02 requires 96 readings."
        )

    data = data.iloc[:96].copy().reset_index(drop=True)

    return data, sheet_name, header_row, timestamp_col, stage_col


# ============================================================
# 2. TIME AXIS
# ============================================================

def make_elapsed_time(data: pd.DataFrame) -> np.ndarray:
    """
    Convert timestamps to hours elapsed from the first reading.
    """
    t = (
        (data["Timestamp"] - data["Timestamp"].iloc[0])
        .dt.total_seconds()
        .to_numpy()
        / 3600.0
    )

    dt = np.diff(t)

    if not np.allclose(dt, 0.25, atol=1e-10):
        raise ValueError(
            "The dataset is not sampled consistently at 0.25 hour. "
            f"Observed interval(s): {np.unique(np.round(dt, 10))}"
        )

    return t


# ============================================================
# 3. FINITE-DIFFERENCE DERIVATIVES
# ============================================================

def finite_difference_derivatives(
    t: np.ndarray,
    h: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Recompute the derivatives from the raw log.

    First derivative:
        first point  -> forward difference
        interior     -> central difference
        last point   -> backward difference

    Second derivative:
        interior points -> central second difference
        endpoints       -> NaN because centered second differences
                           cannot be evaluated there without extra data.
    """
    n = len(h)
    dt = 0.25

    first = np.full(n, np.nan, dtype=float)
    second = np.full(n, np.nan, dtype=float)

    # First derivative: first point, forward difference.
    first[0] = (h[1] - h[0]) / dt

    # First derivative: interior points, central difference.
    first[1:-1] = (h[2:] - h[:-2]) / (2.0 * dt)

    # First derivative: last point, backward difference.
    first[-1] = (h[-1] - h[-2]) / dt

    # Second derivative: central second difference.
    second[1:-1] = (
        h[2:] - 2.0 * h[1:-1] + h[:-2]
    ) / (dt ** 2)

    return first, second


# ============================================================
# 4. FOUR-PARAMETER LOGISTIC MODEL
# ============================================================

def logistic(
    t: np.ndarray | float,
    c: float,
    a: float,
    k: float,
    t0: float,
) -> np.ndarray | float:
    """
    Four-parameter logistic model:

        h(t) = c + a / [1 + exp(-k(t - t0))]
    """
    with np.errstate(over="ignore"):
        return c + a / (
            1.0 + np.exp(-k * (np.asarray(t) - t0))
        )


def build_initial_guess(
    t: np.ndarray,
    h: np.ndarray,
    first_derivative: np.ndarray,
) -> tuple[np.ndarray, dict]:
    """
    Construct an initial guess from the actual dataset.

    c0:
        observed minimum stage.

    a0:
        observed stage range.

    t0_0:
        time of the observed stage closest to the midpoint of the
        observed range.

    k0:
        estimated from the central finite-difference slope near the
        midpoint. For a logistic curve, maximum slope = a*k/4,
        so k ≈ 4*slope/a.
    """
    h_min = float(np.min(h))
    h_max = float(np.max(h))

    c0 = h_min
    a0 = h_max - h_min

    h_mid = h_min + 0.5 * a0
    midpoint_index = int(np.argmin(np.abs(h - h_mid)))
    t0_0 = float(t[midpoint_index])

    # Estimate slope around the midpoint from the actual observations.
    if 0 < midpoint_index < len(h) - 1:
        local_slope = abs(
            (h[midpoint_index + 1] - h[midpoint_index - 1])
            / (2.0 * 0.25)
        )
    else:
        local_slope = float(np.nanmax(np.abs(first_derivative)))

    # Avoid a zero starting value for k.
    if not np.isfinite(local_slope) or local_slope <= 0:
        local_slope = max(a0 / (t[-1] - t[0]), 1e-6)

    k0 = 4.0 * local_slope / max(a0, 1e-12)

    # Keep the starting value numerically reasonable.
    k0 = max(k0, 1e-6)

    p0 = np.array([c0, a0, k0, t0_0], dtype=float)

    basis = {
        "c0": c0,
        "a0": a0,
        "k0": k0,
        "t0_0": t0_0,
        "h_min": h_min,
        "h_max": h_max,
        "h_mid": h_mid,
        "local_slope": local_slope,
        "midpoint_index": midpoint_index,
    }

    return p0, basis


# ============================================================
# 5. FIT THE CONTINUOUS FUNCTION
# ============================================================

def fit_logistic(
    t: np.ndarray,
    h: np.ndarray,
    p0: np.ndarray,
):
    """
    Required Lab 02 Levenberg-Marquardt fit.

    No bounds are used because method='lm' does not accept bounds.
    """
    popt, pcov = curve_fit(
        logistic,
        t,
        h,
        p0=p0,
        method="lm",
        maxfev=20000,
    )

    return popt, pcov


# ============================================================
# 6. STATISTICS
# ============================================================

def calculate_statistics(
    h: np.ndarray,
    h_fit: np.ndarray,
    popt: np.ndarray,
    pcov: np.ndarray,
) -> dict:
    """
    Calculate all statistics required by the activity.
    """
    resid = h - h_fit

    n = len(h)
    p = len(popt)
    df_error = n - p

    # SSE = sum(e_i^2)
    sse = np.sum(resid ** 2)

    # SST = sum((h_i - mean(h))^2)
    sst = np.sum((h - h.mean()) ** 2)

    # R^2 = 1 - SSE/SST
    r2 = 1.0 - sse / sst

    # s = sqrt(SSE/(n-p))
    s = np.sqrt(sse / df_error)

    # SE(b_j) = sqrt(diag(pcov)_j)
    with np.errstate(invalid="ignore"):
        se = np.sqrt(np.diag(pcov))

    # t_j = b_j / SE(b_j)
    with np.errstate(divide="ignore", invalid="ignore"):
        t_stat = popt / se

    # Two-tailed p-value:
    # 2 * [1 - F_t(|t_j|, n-p)]
    with np.errstate(invalid="ignore"):
        p_values = 2.0 * stats.t.sf(
            np.abs(t_stat),
            df_error,
        )

    return {
        "resid": resid,
        "n": n,
        "p": p,
        "df": df_error,
        "sse": float(sse),
        "sst": float(sst),
        "r2": float(r2),
        "s": float(s),
        "se": se,
        "t_stat": t_stat,
        "p_values": p_values,
    }


# ============================================================
# 7. ANALYTICAL DERIVATIVES OF THE FITTED FUNCTION
# ============================================================

def logistic_first_derivative(
    t: np.ndarray | float,
    c: float,
    a: float,
    k: float,
    t0: float,
) -> np.ndarray | float:
    """
    Analytical derivative:

        dh/dt =
        a*k*exp[-k(t-t0)] / [1 + exp[-k(t-t0)]]^2
    """
    x = np.asarray(t)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        e = np.exp(-k * (x - t0))
        result = a * k * e / (1.0 + e) ** 2
    return result


def logistic_second_derivative(
    t: np.ndarray | float,
    c: float,
    a: float,
    k: float,
    t0: float,
) -> np.ndarray | float:
    """
    Analytical second derivative:

        d²h/dt² =
        a*k²*exp[-k(t-t0)]*[exp[-k(t-t0)] - 1]
        / [1 + exp[-k(t-t0)]]^3
    """
    x = np.asarray(t)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        e = np.exp(-k * (x - t0))
        result = (
            a * k ** 2 * e * (e - 1.0)
            / (1.0 + e) ** 3
        )
    return result


def calculate_fitted_derivatives(
    t: np.ndarray,
    popt: np.ndarray,
) -> dict:
    """
    Calculate the continuous derivatives and the exact logistic
    maximum filling rate.
    """
    dhdt = logistic_first_derivative(t, *popt)
    d2hdt2 = logistic_second_derivative(t, *popt)

    c, a, k, t0 = popt

    # For a positive logistic a and k, maximum dh/dt occurs at t=t0.
    exact_max_time = float(t0)
    exact_max_rate = float(a * k / 4.0)

    # Numerical check on the evaluated reading grid.
    grid_index = int(np.argmax(dhdt))

    return {
        "dhdt": np.asarray(dhdt, dtype=float),
        "d2hdt2": np.asarray(d2hdt2, dtype=float),
        "max_time": exact_max_time,
        "max_rate": exact_max_rate,
        "grid_max_time": float(t[grid_index]),
        "grid_max_rate": float(dhdt[grid_index]),
        "second_at_max": float(
            logistic_second_derivative(t0, *popt)
        ),
    }


# ============================================================
# 8. INTEGRATION
# ============================================================

def calculate_area(
    t: np.ndarray,
    h: np.ndarray,
    popt: np.ndarray,
) -> dict:
    """
    Integrate the fitted continuous function with scipy.integrate.quad
    and cross-check using np.trapezoid on the raw readings.
    """
    area_quad, quad_error = quad(
        lambda x: float(logistic(x, *popt)),
        float(t[0]),
        float(t[-1]),
    )

    area_trapezoid = np.trapezoid(h, x=t)

    difference = area_quad - area_trapezoid

    return {
        "area_quad": float(area_quad),
        "quad_error": float(quad_error),
        "area_trapezoid": float(area_trapezoid),
        "difference": float(difference),
        "absolute_difference": float(abs(difference)),
    }


# ============================================================
# 9. RESIDUAL DIAGNOSTICS
# ============================================================

def analyze_residuals(
    t: np.ndarray,
    h: np.ndarray,
    h_fit: np.ndarray,
    resid: np.ndarray,
) -> dict:
    """
    Analyze centering, consecutive sign runs, spread by fitted level,
    and comparison with the logger's 0.01 m resolution.
    """
    mean_resid = float(np.mean(resid))
    median_resid = float(np.median(resid))

    midpoint = len(resid) // 2
    first_half_mean = float(np.mean(resid[:midpoint]))
    second_half_mean = float(np.mean(resid[midpoint:]))

    # Consecutive positive/negative runs.
    signs = np.sign(resid)
    runs = []

    start = 0
    previous = signs[0]

    for i in range(1, len(signs)):
        if signs[i] != previous:
            runs.append((previous, start, i - 1, i - start))
            start = i
            previous = signs[i]

    runs.append(
        (previous, start, len(signs) - 1, len(signs) - start)
    )

    positive_runs = [r for r in runs if r[0] > 0]
    negative_runs = [r for r in runs if r[0] < 0]

    longest_positive = max(
        positive_runs,
        key=lambda r: r[3],
        default=(1, 0, 0, 0),
    )
    longest_negative = max(
        negative_runs,
        key=lambda r: r[3],
        default=(-1, 0, 0, 0),
    )

    # Largest residual.
    largest_index = int(np.argmax(np.abs(resid)))
    largest_abs = float(abs(resid[largest_index]))
    logger_resolution = 0.01
    excess = largest_abs - logger_resolution

    # Residual spread at low, middle, and high fitted levels.
    q1, q2 = np.quantile(h_fit, [1 / 3, 2 / 3])

    spread_groups = []

    for label, lo, hi in [
        ("Low fitted level", -np.inf, q1),
        ("Middle fitted level", q1, q2),
        ("High fitted level", q2, np.inf),
    ]:
        mask = (h_fit > lo) & (h_fit <= hi)

        spread_groups.append({
            "label": label,
            "min_fit": float(np.min(h_fit[mask])),
            "max_fit": float(np.max(h_fit[mask])),
            "n": int(np.sum(mask)),
            "mean": float(np.mean(resid[mask])),
            "std": float(np.std(resid[mask])),
            "max_abs": float(np.max(np.abs(resid[mask]))),
        })

    return {
        "mean": mean_resid,
        "median": median_resid,
        "first_half_mean": first_half_mean,
        "second_half_mean": second_half_mean,
        "longest_positive": longest_positive,
        "longest_negative": longest_negative,
        "largest_index": largest_index,
        "largest_abs": largest_abs,
        "largest_time": float(t[largest_index]),
        "largest_raw": float(h[largest_index]),
        "largest_fit": float(h_fit[largest_index]),
        "logger_resolution": logger_resolution,
        "excess": float(excess),
        "spread_groups": spread_groups,
    }


# ============================================================
# 10. WRITTEN INTERPRETATIONS
# ============================================================

def build_interpretations(
    residual_info: dict,
    derivative_info: dict,
    area_info: dict,
) -> dict:
    """
    Build report-ready interpretations from calculated values.
    """
    longest_pos = residual_info["longest_positive"]
    longest_neg = residual_info["longest_negative"]

    pos_start = longest_pos[1] * 0.25
    pos_end = longest_pos[2] * 0.25

    neg_start = longest_neg[1] * 0.25
    neg_end = longest_neg[2] * 0.25

    if residual_info["excess"] > 0:
        resolution_text = (
            f"The largest absolute residual is "
            f"{residual_info['largest_abs']:.4f} m, which exceeds the "
            f"logger's 0.01 m resolution by "
            f"{residual_info['excess']:.4f} m."
        )
    else:
        resolution_text = (
            f"The largest absolute residual is "
            f"{residual_info['largest_abs']:.4f} m, which does not "
            f"exceed the logger's 0.01 m resolution."
        )

    residual_summary = (
        f"The residuals are centered around zero overall "
        f"(mean = {residual_info['mean']:.6f} m), but there are "
        f"runs of {longest_pos[3]} consecutive positive residuals "
        f"from {pos_start:.2f} to {pos_end:.2f} h and "
        f"{longest_neg[3]} consecutive negative residuals from "
        f"{neg_start:.2f} to {neg_end:.2f} h. "
        f"The residual spread does not increase as fitted level rises; "
        f"the standard deviations for low, middle, and high fitted "
        f"levels are "
        f"{residual_info['spread_groups'][0]['std']:.4f}, "
        f"{residual_info['spread_groups'][1]['std']:.4f}, and "
        f"{residual_info['spread_groups'][2]['std']:.4f} m, respectively. "
        f"{resolution_text}"
    )

    second_derivative_sentence = (
        "The second derivative is positive before the inflection point "
        "and negative afterward, indicating that the filling rate first "
        "increases, reaches its maximum at the inflection time, and then "
        "decreases as the reservoir level approaches the settling level."
    )

    area_sentence = (
        "The fitted-function integral represents accumulated reservoir "
        "stage over time in meter-hours; it is not a water volume because "
        "no reservoir surface-area/depth-to-volume relationship is being "
        "applied."
    )

    crosscheck_sentence = (
        "The quad and trapezoidal values differ slightly because quad "
        "integrates the smooth fitted logistic function, whereas "
        "np.trapezoid integrates straight-line segments between the "
        "discrete raw readings."
    )

    return {
        "residual": residual_summary,
        "second_derivative": second_derivative_sentence,
        "area": area_sentence,
        "crosscheck": crosscheck_sentence,
    }


# ============================================================
# 11. CHART GENERATION
# ============================================================

def figure_to_svg(fig) -> str:
    """Convert a Matplotlib figure to inline SVG for the dashboard."""
    buffer = io.StringIO()
    fig.savefig(
        buffer,
        format="svg",
        bbox_inches="tight",
    )
    plt.close(fig)

    svg = buffer.getvalue()

    # Remove XML/DOCTYPE lines so the SVG can be embedded directly.
    lines = [
        line for line in svg.splitlines()
        if not line.startswith("<?xml")
        and not line.startswith("<!DOCTYPE")
    ]

    return "\n".join(lines)


def make_charts(
    data: pd.DataFrame,
    t: np.ndarray,
    h: np.ndarray,
    h_fit: np.ndarray,
    fd_first: np.ndarray,
    fd_second: np.ndarray,
    fitted_dhdt: np.ndarray,
    fitted_d2hdt2: np.ndarray,
    popt: np.ndarray,
    max_time: float,
    finite_max_time: float,
    finite_max_rate: float,
) -> dict:
    """Create all dashboard charts as inline SVG."""

    smooth_t = np.linspace(t[0], t[-1], 600)
    smooth_h = logistic(smooth_t, *popt)
    smooth_dhdt = logistic_first_derivative(
        smooth_t, *popt
    )
    smooth_d2hdt2 = logistic_second_derivative(
        smooth_t, *popt
    )

    # --------------------------------------------------------
    # Raw stage log
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(t, h, marker="o", markersize=3, linewidth=1.2)
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("Reservoir stage/depth (m)")
    ax.set_title("Raw Reservoir Stage Log")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    raw_stage_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Finite-difference first derivative
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        t,
        fd_first,
        marker="o",
        markersize=2.5,
        linewidth=1.0,
        label="Finite-difference dh/dt",
    )
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.axvline(
        finite_max_time,
        linestyle=":",
        linewidth=1.5,
        label="Maximum finite-difference rate",
    )
    ax.scatter(
        [finite_max_time],
        [finite_max_rate],
        s=50,
        zorder=3,
        label="Maximum dh/dt",
    )
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("dh/dt (m/h)")
    ax.set_title("First Finite-Difference Derivative")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    finite_first_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Finite-difference second derivative
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        t,
        fd_second,
        marker="o",
        markersize=2.5,
        linewidth=1.0,
    )
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("d²h/dt² (m/h²)")
    ax.set_title("Second Finite-Difference Derivative")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    finite_second_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Fitted curve
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.scatter(
        t,
        h,
        s=22,
        label="Raw stage",
    )
    ax.plot(
        smooth_t,
        smooth_h,
        linewidth=2,
        label="Four-parameter logistic fit",
    )
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("Reservoir stage/depth (m)")
    ax.set_title("Raw Stage and Fitted Logistic Curve")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fitted_curve_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Fitted first derivative
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        smooth_t,
        smooth_dhdt,
        linewidth=2,
        label="Fitted dh/dt",
    )
    ax.axvline(
        max_time,
        linestyle=":",
        linewidth=1.5,
        label="Maximum rate",
    )
    ax.scatter(
        [max_time],
        [float(logistic_first_derivative(max_time, *popt))],
        s=50,
        zorder=3,
        label="Maximum dh/dt",
    )
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("dh/dt (m/h)")
    ax.set_title("First Derivative of Fitted Logistic Function")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fitted_dhdt_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Fitted second derivative
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        smooth_t,
        smooth_d2hdt2,
        linewidth=2,
    )
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.axvline(
        max_time,
        linestyle=":",
        linewidth=1.5,
    )
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("d²h/dt² (m/h²)")
    ax.set_title("Second Derivative of Fitted Logistic Function")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fitted_d2hdt2_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Residuals vs time
    # --------------------------------------------------------
    residuals = h - h_fit

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.scatter(t, residuals, s=24)
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("Residual (m)")
    ax.set_title("Residuals vs. Time")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    residual_time_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Residuals vs fitted values
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.scatter(h_fit, residuals, s=24)
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_xlabel("Fitted reservoir stage (m)")
    ax.set_ylabel("Residual (m)")
    ax.set_title("Residuals vs. Fitted Values")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    residual_fitted_svg = figure_to_svg(fig)

    # --------------------------------------------------------
    # Area under fitted curve
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        smooth_t,
        smooth_h,
        linewidth=2,
        label="Fitted h(t)",
    )

    # Shade to the x-axis between the actual integration limits.
    ax.fill_between(
        smooth_t,
        smooth_h,
        0,
        alpha=0.25,
    )

    ax.set_xlim(t[0], t[-1])
    ax.set_xlabel("Elapsed time (h)")
    ax.set_ylabel("Reservoir stage/depth (m)")
    ax.set_title("Area Under the Fitted Reservoir-Level Curve")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    area_svg = figure_to_svg(fig)

    return {
        "raw_stage": raw_stage_svg,
        "finite_first": finite_first_svg,
        "finite_second": finite_second_svg,
        "fitted_curve": fitted_curve_svg,
        "fitted_dhdt": fitted_dhdt_svg,
        "fitted_d2hdt2": fitted_d2hdt2_svg,
        "residual_time": residual_time_svg,
        "residual_fitted": residual_fitted_svg,
        "area": area_svg,
    }


# ============================================================
# 12. HTML DASHBOARD
# ============================================================

def fmt(value, decimals=6) -> str:
    """Format a finite number for display."""
    if value is None:
        return "N/A"

    try:
        if not np.isfinite(value):
            return "N/A"
    except TypeError:
        return "N/A"

    return f"{value:.{decimals}f}"


def build_dashboard(
    output_path: Path,
    data: pd.DataFrame,
    t: np.ndarray,
    h: np.ndarray,
    fd_first: np.ndarray,
    fd_second: np.ndarray,
    h_fit: np.ndarray,
    fitted_derivatives: dict,
    popt: np.ndarray,
    statistics: dict,
    residual_info: dict,
    area_info: dict,
    interpretations: dict,
    charts: dict,
    sheet_name: str,
    timestamp_col: str,
    stage_col: str,
    initial_guess: np.ndarray,
    initial_basis: dict,
    finite_max_time: float,
    finite_max_rate: float,
) -> None:
    """Write a standalone HTML dashboard. JavaScript only switches tabs."""

    parameter_names = ["c", "a", "k", "t0"]
    parameter_units = ["m", "m", "1/h", "h"]

    parameter_rows = []

    for name, unit, value, se, tv, pv in zip(
        parameter_names,
        parameter_units,
        popt,
        statistics["se"],
        statistics["t_stat"],
        statistics["p_values"],
    ):
        if np.isfinite(pv) and pv < 0.05:
            conclusion = "Statistically significant at α = 0.05"
        elif np.isfinite(pv):
            conclusion = "Not statistically significant at α = 0.05"
        else:
            conclusion = "P-value unavailable"

        parameter_rows.append(
            "<tr>"
            f"<td>{escape(name)}</td>"
            f"<td>{fmt(value, 8)}</td>"
            f"<td>{escape(unit)}</td>"
            f"<td>{fmt(se, 8)}</td>"
            f"<td>{fmt(tv, 5)}</td>"
            f"<td>{fmt(pv, 8)}</td>"
            f"<td>{escape(conclusion)}</td>"
            "</tr>"
        )

    derivative_rows = []

    for timestamp, hh, fd1, fd2, smooth1, smooth2 in zip(
        data["Timestamp"].dt.strftime("%Y-%m-%d %H:%M"),
        h,
        fd_first,
        fd_second,
        fitted_derivatives["dhdt"],
        fitted_derivatives["d2hdt2"],
    ):
        derivative_rows.append(
            "<tr>"
            f"<td>{escape(timestamp)}</td>"
            f"<td>{fmt(hh, 4)}</td>"
            f"<td>{fmt(fd1, 6)}</td>"
            f"<td>{fmt(fd2, 6)}</td>"
            f"<td>{fmt(smooth1, 6)}</td>"
            f"<td>{fmt(smooth2, 6)}</td>"
            "</tr>"
        )

    # Small raw-data table for transparency.
    raw_rows = []
    for timestamp, time_value, stage in zip(
        data["Timestamp"].dt.strftime("%Y-%m-%d %H:%M"),
        t,
        h,
    ):
        raw_rows.append(
            "<tr>"
            f"<td>{escape(timestamp)}</td>"
            f"<td>{fmt(time_value, 2)}</td>"
            f"<td>{fmt(stage, 4)}</td>"
            "</tr>"
        )

    # Spread table.
    spread_rows = []
    for group in residual_info["spread_groups"]:
        spread_rows.append(
            "<tr>"
            f"<td>{escape(group['label'])}</td>"
            f"<td>{fmt(group['min_fit'], 4)}–{fmt(group['max_fit'], 4)}</td>"
            f"<td>{group['n']}</td>"
            f"<td>{fmt(group['mean'], 6)}</td>"
            f"<td>{fmt(group['std'], 6)}</td>"
            f"<td>{fmt(group['max_abs'], 6)}</td>"
            "</tr>"
        )

    equation = (
        "h(t) = c + a / [1 + exp(-k(t − t₀))]"
    )

    max_rate = fitted_derivatives["max_rate"]
    max_time = fitted_derivatives["max_time"]

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NM Lab 02 — Fitting a Curve to the Dam</title>

<style>
body {{
    font-family: Arial, Helvetica, sans-serif;
    margin: 0;
    background: #f3f5f7;
    color: #17202a;
}}

header {{
    background: #17202a;
    color: white;
    padding: 28px 5%;
}}

header h1 {{
    margin: 0 0 8px;
}}

header p {{
    margin: 5px 0;
}}

main {{
    width: 90%;
    max-width: 1300px;
    margin: 24px auto;
}}

.card {{
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}

.metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
}}

.metric {{
    background: #f7f7f7;
    padding: 14px;
    border-radius: 8px;
}}

.metric .label {{
    font-size: 13px;
    color: #5f6b73;
    margin-bottom: 6px;
}}

.metric .value {{
    font-size: 21px;
    font-weight: bold;
}}

.equation {{
    background: #f7f7f7;
    padding: 15px;
    border-left: 4px solid #17202a;
    font-family: "Courier New", monospace;
    overflow-x: auto;
}}

.tabs {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}}

.tab-button {{
    border: 1px solid #ccd3d8;
    background: white;
    padding: 10px 15px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
}}

.tab-button.active {{
    background: #17202a;
    color: white;
}}

.tab {{
    display: none;
}}

.tab.active {{
    display: block;
}}

.chart {{
    overflow-x: auto;
    text-align: center;
}}

.chart svg {{
    max-width: 100%;
    height: auto;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    background: white;
}}

th, td {{
    border: 1px solid #dfe4e8;
    padding: 8px;
    text-align: right;
    white-space: nowrap;
}}

th {{
    background: #eef1f3;
    text-align: center;
}}

.table-scroll {{
    overflow-x: auto;
    max-height: 600px;
}}

.note {{
    background: #f8f9fa;
    border-left: 4px solid #7b8790;
    padding: 12px 15px;
    line-height: 1.5;
}}

.warning {{
    background: #fff8e1;
    border-left: 4px solid #c69214;
    padding: 12px 15px;
    line-height: 1.5;
}}

footer {{
    text-align: center;
    color: #68737c;
    font-size: 13px;
    padding: 20px;
}}
</style>
</head>

<body>

<header>
    <h1>Numerical Methods — Laboratory Activity 02</h1>
    <p><strong>Fitting a Curve to the Dam</strong></p>
    <p>Levenberg–Marquardt, residuals, derivatives, and area under the level</p>
    <p>Prepared by: Samson</p>
</header>

<main>

<!-- RAW STAGE LOG IS ALWAYS VISIBLE -->
<section class="card">
    <h2>Raw Stage Log Time Series</h2>

    <p>
        Raw reservoir stage/depth from the Excel dataset.
        Time is measured in elapsed hours from the first reading.
        The sampling interval is 0.25 h.
    </p>

    <div class="metrics">
        <div class="metric">
            <div class="label">Readings (n)</div>
            <div class="value">{statistics["n"]}</div>
        </div>

        <div class="metric">
            <div class="label">Time step</div>
            <div class="value">0.25 h</div>
        </div>

        <div class="metric">
            <div class="label">First logged time</div>
            <div class="value">{fmt(t[0], 2)} h</div>
        </div>

        <div class="metric">
            <div class="label">Last logged time</div>
            <div class="value">{fmt(t[-1], 2)} h</div>
        </div>
    </div>

    <div class="chart">
        {charts["raw_stage"]}
    </div>

    <h3>Raw Data Used</h3>
    <div class="table-scroll">
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Elapsed time (h)</th>
                    <th>Depth (m)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(raw_rows)}
            </tbody>
        </table>
    </div>
</section>

<div class="tabs">
    <button class="tab-button active" onclick="showTab('derivatives', this)">
        Tab 1 — Derivatives
    </button>
    <button class="tab-button" onclick="showTab('fit', this)">
        Tab 2 — Fitted Curve & Residuals
    </button>
    <button class="tab-button" onclick="showTab('area', this)">
        Tab 3 — Area Under Curve
    </button>
</div>

<!-- ====================================================== -->
<!-- TAB 1 -->
<!-- ====================================================== -->

<section id="derivatives" class="tab active">

<div class="card">
    <h2>Finite-Difference Derivatives</h2>

    <p>
        First derivative: forward difference at the first point,
        central differences at interior points, and backward difference
        at the last point. The second derivative uses the central
        second-difference formula at interior points.
    </p>

    <div class="metrics">
        <div class="metric">
            <div class="label">Maximum finite-difference dh/dt</div>
            <div class="value">{fmt(finite_max_rate, 6)} m/h</div>
        </div>

        <div class="metric">
            <div class="label">Time of maximum finite dh/dt</div>
            <div class="value">{fmt(finite_max_time, 4)} h</div>
        </div>

        <div class="metric">
            <div class="label">Maximum fitted dh/dt</div>
            <div class="value">{fmt(max_rate, 6)} m/h</div>
        </div>

        <div class="metric">
            <div class="label">Time of maximum fitted dh/dt</div>
            <div class="value">{fmt(max_time, 4)} h</div>
        </div>

        <div class="metric">
            <div class="label">Second derivative at t₀</div>
            <div class="value">{fmt(fitted_derivatives["second_at_max"], 8)} m/h²</div>
        </div>
    </div>

    <div class="chart">
        {charts["finite_first"]}
    </div>

    <div class="chart">
        {charts["finite_second"]}
    </div>

    <h3>Finite-Difference and Fitted Derivative Values</h3>
    <div class="table-scroll">
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>h (m)</th>
                    <th>Finite dh/dt (m/h)</th>
                    <th>Finite d²h/dt² (m/h²)</th>
                    <th>Fitted dh/dt (m/h)</th>
                    <th>Fitted d²h/dt² (m/h²)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(derivative_rows)}
            </tbody>
        </table>
    </div>
</div>

<div class="card">
    <h2>Analytical Derivatives of the Fitted Function</h2>

    <p>
        The first derivative of the logistic curve gives the continuous
        filling rate. Its maximum occurs at the logistic inflection point
        t₀.
    </p>

    <div class="equation">
        dh/dt = a k exp[-k(t − t₀)] / [1 + exp(-k(t − t₀))]²
    </div>

    <div class="chart">
        {charts["fitted_dhdt"]}
    </div>

    <div class="equation">
        d²h/dt² =
        a k² exp[-k(t − t₀)] [exp(-k(t − t₀)) − 1]
        / [1 + exp(-k(t − t₀))]³
    </div>

    <div class="chart">
        {charts["fitted_d2hdt2"]}
    </div>

    <div class="note">
        <strong>Interpretation:</strong>
        {escape(interpretations["second_derivative"])}
    </div>
</div>

</section>

<!-- ====================================================== -->
<!-- TAB 2 -->
<!-- ====================================================== -->

<section id="fit" class="tab">

<div class="card">
    <h2>Selected Model</h2>

    <div class="equation">
        {escape(equation)}
    </div>

    <p>
        The four-parameter logistic was selected because the raw reservoir
        record represents a single filling event with a gradual transition
        toward a higher level, making a sigmoidal model with one inflection
        point physically reasonable. The data do not show clear evidence
        requiring two separate filling pulses, while a cubic polynomial is
        only a mathematical baseline rather than a physically motivated
        reservoir model.
    </p>

    <h3>Initial Guess</h3>

    <table>
        <thead>
            <tr>
                <th>Parameter</th>
                <th>Initial value</th>
                <th>Basis from actual data</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>c</td>
                <td>{fmt(initial_guess[0], 6)} m</td>
                <td>Observed minimum stage</td>
            </tr>
            <tr>
                <td>a</td>
                <td>{fmt(initial_guess[1], 6)} m</td>
                <td>Observed maximum minus observed minimum</td>
            </tr>
            <tr>
                <td>k</td>
                <td>{fmt(initial_guess[2], 6)} 1/h</td>
                <td>
                    4 × local midpoint slope / observed stage range;
                    local slope = {fmt(initial_basis["local_slope"], 6)} m/h
                </td>
            </tr>
            <tr>
                <td>t₀</td>
                <td>{fmt(initial_guess[3], 6)} h</td>
                <td>
                    Time of observation closest to midpoint stage
                    ({fmt(initial_basis["h_mid"], 4)} m)
                </td>
            </tr>
        </tbody>
    </table>

    <p class="note">
        The fit uses scipy.optimize.curve_fit with method="lm" and
        maxfev=20000. No parameter bounds are used because
        Levenberg–Marquardt does not accept bounds.
    </p>

    <h3>Fitted Curve</h3>
    <div class="chart">
        {charts["fitted_curve"]}
    </div>
</div>

<div class="card">
    <h2>Fitted Parameters and Statistical Results</h2>

    <table>
        <thead>
            <tr>
                <th>Parameter</th>
                <th>Estimate</th>
                <th>Unit</th>
                <th>Standard error</th>
                <th>t statistic</th>
                <th>Two-tailed p-value</th>
                <th>Conclusion</th>
            </tr>
        </thead>
        <tbody>
            {"".join(parameter_rows)}
        </tbody>
    </table>

    <br>

    <div class="metrics">
        <div class="metric">
            <div class="label">SSE</div>
            <div class="value">{fmt(statistics["sse"], 8)}</div>
        </div>

        <div class="metric">
            <div class="label">SST</div>
            <div class="value">{fmt(statistics["sst"], 8)}</div>
        </div>

        <div class="metric">
            <div class="label">R²</div>
            <div class="value">{fmt(statistics["r2"], 8)}</div>
        </div>

        <div class="metric">
            <div class="label">Standard error s</div>
            <div class="value">{fmt(statistics["s"], 8)} m</div>
        </div>

        <div class="metric">
            <div class="label">n</div>
            <div class="value">{statistics["n"]}</div>
        </div>

        <div class="metric">
            <div class="label">p</div>
            <div class="value">{statistics["p"]}</div>
        </div>

        <div class="metric">
            <div class="label">Degrees of freedom</div>
            <div class="value">{statistics["df"]}</div>
        </div>
    </div>
</div>

<div class="card">
    <h2>Residuals vs. Time</h2>
    <div class="chart">
        {charts["residual_time"]}
    </div>
</div>

<div class="card">
    <h2>Residuals vs. Fitted Values</h2>
    <div class="chart">
        {charts["residual_fitted"]}
    </div>
</div>

<div class="card">
    <h2>Residual Analysis</h2>

    <p>
        {escape(interpretations["residual"])}
    </p>

    <h3>Residual Spread by Fitted-Level Range</h3>

    <table>
        <thead>
            <tr>
                <th>Group</th>
                <th>Fitted-level range (m)</th>
                <th>n</th>
                <th>Mean residual (m)</th>
                <th>Residual SD (m)</th>
                <th>Maximum |residual| (m)</th>
            </tr>
        </thead>
        <tbody>
            {"".join(spread_rows)}
        </tbody>
    </table>
</div>

</section>

<!-- ====================================================== -->
<!-- TAB 3 -->
<!-- ====================================================== -->

<section id="area" class="tab">

<div class="card">
    <h2>Area Under the Fitted Reservoir-Level Curve</h2>

    <p>
        The fitted continuous function is integrated from the first
        logged time to the last logged time using scipy.integrate.quad.
    </p>

    <div class="metrics">
        <div class="metric">
            <div class="label">Integration start</div>
            <div class="value">{fmt(t[0], 2)} h</div>
        </div>

        <div class="metric">
            <div class="label">Integration end</div>
            <div class="value">{fmt(t[-1], 2)} h</div>
        </div>

        <div class="metric">
            <div class="label">Area from quad</div>
            <div class="value">{fmt(area_info["area_quad"], 6)} m·h</div>
        </div>

        <div class="metric">
            <div class="label">quad absolute error</div>
            <div class="value">{area_info["quad_error"]:.4e} m·h</div>
        </div>

        <div class="metric">
            <div class="label">Raw trapezoid cross-check</div>
            <div class="value">{fmt(area_info["area_trapezoid"], 6)} m·h</div>
        </div>

        <div class="metric">
            <div class="label">Absolute difference</div>
            <div class="value">{fmt(area_info["absolute_difference"], 8)} m·h</div>
        </div>
    </div>

    <div class="chart">
        {charts["area"]}
    </div>

    <div class="note">
        <strong>Units and meaning:</strong>
        {escape(interpretations["area"])}
    </div>

    <div class="note">
        <strong>Cross-check explanation:</strong>
        {escape(interpretations["crosscheck"])}
    </div>
</div>

</section>

<div class="card">
    <h2>Data and Calculation Provenance</h2>
    <p>
        Workbook: <strong>{escape(str(data.attrs.get("source_file", "")))}</strong>
    </p>
    <p>
        Worksheet: <strong>{escape(sheet_name)}</strong>
    </p>
    <p>
        Timestamp column: <strong>{escape(str(timestamp_col))}</strong>
    </p>
    <p>
        Raw stage/depth column: <strong>{escape(str(stage_col))}</strong>
    </p>
    <p>
        All fitting, statistics, derivatives, and integration were
        performed by Python before this HTML file was written.
        JavaScript in this dashboard only controls tab visibility.
    </p>
</div>

</main>

<footer>
    NM Lab 02 — Python computes; HTML displays.
</footer>

<script>
function showTab(tabId, button) {{
    document.querySelectorAll('.tab').forEach(function(tab) {{
        tab.classList.remove('active');
    }});

    document.querySelectorAll('.tab-button').forEach(function(btn) {{
        btn.classList.remove('active');
    }});

    document.getElementById(tabId).classList.add('active');
    button.classList.add('active');
}}
</script>

</body>
</html>
"""

    output_path.write_text(
        html,
        encoding="utf-8",
    )


# ============================================================
# 13. CONSOLE REPORT
# ============================================================

def print_report(
    input_path: Path,
    sheet_name: str,
    header_row: int,
    timestamp_col: str,
    stage_col: str,
    p0: np.ndarray,
    initial_basis: dict,
    popt: np.ndarray,
    statistics: dict,
    fitted_derivatives: dict,
    residual_info: dict,
    area_info: dict,
    dashboard_path: Path,
    finite_max_time: float,
    finite_max_rate: float,
) -> None:
    """Print the important numerical results to the terminal."""

    print("\n" + "=" * 78)
    print("NM LAB 02 — COMPLETE RESULTS")
    print("=" * 78)

    print("\nDATA")
    print("-" * 78)
    print(f"Workbook:             {input_path}")
    print(f"Worksheet:            {sheet_name}")
    print(f"Header row:            {header_row + 1}")
    print(f"Timestamp column:      {timestamp_col}")
    print(f"Raw stage column:      {stage_col}")
    print(f"Number of readings:    {statistics['n']}")
    print("Sampling interval:     0.25 h")
    print("Elapsed time:          0.00 to 23.75 h")

    print("\nINITIAL GUESS")
    print("-" * 78)
    print(f"c0  = {p0[0]:.8f} m")
    print(f"a0  = {p0[1]:.8f} m")
    print(f"k0  = {p0[2]:.8f} 1/h")
    print(f"t00 = {p0[3]:.8f} h")
    print(f"Observed minimum:      {initial_basis['h_min']:.6f} m")
    print(f"Observed maximum:      {initial_basis['h_max']:.6f} m")
    print(f"Midpoint stage:        {initial_basis['h_mid']:.6f} m")
    print(f"Midpoint local slope:  {initial_basis['local_slope']:.6f} m/h")

    print("\nFITTED PARAMETERS")
    print("-" * 78)
    names = ["c", "a", "k", "t0"]
    units = ["m", "m", "1/h", "h"]

    for name, value, unit in zip(names, popt, units):
        print(f"{name:>3} = {value:.10f} {unit}")

    print("\nMODEL STATISTICS")
    print("-" * 78)
    print(f"SSE = {statistics['sse']:.10f}")
    print(f"SST = {statistics['sst']:.10f}")
    print(f"R^2 = {statistics['r2']:.10f}")
    print(f"s   = {statistics['s']:.10f} m")
    print(f"n   = {statistics['n']}")
    print(f"p   = {statistics['p']}")
    print(f"df  = n - p = {statistics['df']}")

    print("\nPARAMETER INFERENCE")
    print("-" * 78)
    print(
        f"{'Parameter':<12}"
        f"{'Estimate':>15}"
        f"{'SE':>15}"
        f"{'t':>15}"
        f"{'p-value':>15}"
    )
    print("-" * 72)

    for name, value, se, tv, pv in zip(
        names,
        popt,
        statistics["se"],
        statistics["t_stat"],
        statistics["p_values"],
    ):
        print(
            f"{name:<12}"
            f"{value:>15.8f}"
            f"{se:>15.8f}"
            f"{tv:>15.6f}"
            f"{pv:>15.8f}"
        )

    print("\nFINITE-DIFFERENCE MAXIMUM")
    print("-" * 78)
    print(f"Maximum finite dh/dt:     {finite_max_rate:.10f} m/h")
    print(f"Time of finite maximum:   {finite_max_time:.10f} h")

    print("\nFITTED DERIVATIVES")
    print("-" * 78)
    print(
        f"Maximum continuous dh/dt: "
        f"{fitted_derivatives['max_rate']:.10f} m/h"
    )
    print(
        f"Time of maximum dh/dt: "
        f"{fitted_derivatives['max_time']:.10f} h"
    )
    print(
        f"d²h/dt² at t0: "
        f"{fitted_derivatives['second_at_max']:.10e} m/h²"
    )

    print("\nRESIDUAL ANALYSIS")
    print("-" * 78)
    print(f"Mean residual:           {residual_info['mean']:.10f} m")
    print(f"Median residual:         {residual_info['median']:.10f} m")
    print(
        f"Longest positive run:    {residual_info['longest_positive'][3]} readings"
    )
    print(
        f"Longest negative run:    {residual_info['longest_negative'][3]} readings"
    )
    print(
        f"Largest |residual|:      {residual_info['largest_abs']:.10f} m"
    )
    print(
        f"Time of largest residual: {residual_info['largest_time']:.2f} h"
    )
    print(
        f"Logger resolution:       {residual_info['logger_resolution']:.4f} m"
    )
    print(
        f"Excess over resolution:  {residual_info['excess']:.10f} m"
    )

    print("\nINTEGRATION")
    print("-" * 78)
    print(
        f"quad area:               "
        f"{area_info['area_quad']:.10f} m·h"
    )
    print(
        f"quad absolute error:     "
        f"{area_info['quad_error']:.10e} m·h"
    )
    print(
        f"np.trapezoid area:       "
        f"{area_info['area_trapezoid']:.10f} m·h"
    )
    print(
        f"Absolute difference:     "
        f"{area_info['absolute_difference']:.10f} m·h"
    )

    print("\nOUTPUT")
    print("-" * 78)
    print(f"Dashboard: {dashboard_path}")

    print("\n" + "=" * 78)
    print("LAB 02 CALCULATION COMPLETE")
    print("=" * 78)


# ============================================================
# 14. MAIN PROGRAM
# ============================================================

def main() -> None:

    # --------------------------------------------------------
    # Load workbook and identify actual data columns.
    # --------------------------------------------------------
    input_path = find_input_workbook()

    data, sheet_name, header_row, timestamp_col, stage_col = (
        load_raw_data(input_path)
    )

    data.attrs["source_file"] = str(input_path)

    # Raw stage values.
    h = data["Depth (m)"].to_numpy(dtype=float)

    # Elapsed time in hours.
    t = make_elapsed_time(data)

    # --------------------------------------------------------
    # Recompute finite differences from raw readings.
    # --------------------------------------------------------
    fd_first, fd_second = finite_difference_derivatives(
        t,
        h,
    )

    finite_max_index = int(np.argmax(fd_first))
    finite_max_rate = float(fd_first[finite_max_index])
    finite_max_time = float(t[finite_max_index])

    # --------------------------------------------------------
    # Build actual-data initial guess.
    # --------------------------------------------------------
    p0, initial_basis = build_initial_guess(
        t,
        h,
        fd_first,
    )

    # --------------------------------------------------------
    # Levenberg-Marquardt fit.
    # --------------------------------------------------------
    popt, pcov = fit_logistic(
        t,
        h,
        p0,
    )

    # --------------------------------------------------------
    # Fitted level and residuals/statistics.
    # --------------------------------------------------------
    h_fit = logistic(t, *popt)

    statistics = calculate_statistics(
        h,
        h_fit,
        popt,
        pcov,
    )

    # --------------------------------------------------------
    # Continuous analytical derivatives.
    # --------------------------------------------------------
    fitted_derivatives = calculate_fitted_derivatives(
        t,
        popt,
    )

    # --------------------------------------------------------
    # Integration.
    # --------------------------------------------------------
    area_info = calculate_area(
        t,
        h,
        popt,
    )

    # --------------------------------------------------------
    # Residual diagnostics.
    # --------------------------------------------------------
    residual_info = analyze_residuals(
        t,
        h,
        h_fit,
        statistics["resid"],
    )

    # --------------------------------------------------------
    # Written interpretations generated from actual results.
    # --------------------------------------------------------
    interpretations = build_interpretations(
        residual_info,
        fitted_derivatives,
        area_info,
    )

    # --------------------------------------------------------
    # Create all dashboard charts.
    # --------------------------------------------------------
    charts = make_charts(
        data,
        t,
        h,
        h_fit,
        fd_first,
        fd_second,
        fitted_derivatives["dhdt"],
        fitted_derivatives["d2hdt2"],
        popt,
        fitted_derivatives["max_time"],
        finite_max_time,
        finite_max_rate,
    )

    # --------------------------------------------------------
    # Generate the required HTML dashboard.
    # --------------------------------------------------------
    output_dir = Path(__file__).resolve().parent
    dashboard_path = output_dir / "lab02_samson.html"

    build_dashboard(
        dashboard_path,
        data,
        t,
        h,
        fd_first,
        fd_second,
        h_fit,
        fitted_derivatives,
        popt,
        statistics,
        residual_info,
        area_info,
        interpretations,
        charts,
        sheet_name,
        timestamp_col,
        stage_col,
        p0,
        initial_basis,
        finite_max_time,
        finite_max_rate,
    )

    # --------------------------------------------------------
    # Print final results.
    # --------------------------------------------------------
    print_report(
        input_path,
        sheet_name,
        header_row,
        timestamp_col,
        stage_col,
        p0,
        initial_basis,
        popt,
        statistics,
        fitted_derivatives,
        residual_info,
        area_info,
        dashboard_path,
        finite_max_time,
        finite_max_rate,
    )


if __name__ == "__main__":
    main()
