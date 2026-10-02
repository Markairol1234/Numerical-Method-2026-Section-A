"""
laboratory_exercises.py
=======================

Three classic mathematical-limit exercises implemented with NumPy + Matplotlib.

    Exercise 1:  (1 + 1/n)^n            --->  e          (Euler's compound-interest limit)
    Exercise 2:  (a^h - 1) / h          --->  ln(a)      (difference quotient of a^x at x = 0)
    Exercise 3:  sum_{n=0..N} x^n / n!  --->  e^x        (Taylor series, x = 1, up to N = 10 000)

Every figure is rendered with explicit styling (gridlines, a clean colour
palette, rotated x-tick labels) and saved as a dense PNG file in the
``figures`` folder that sits next to this script.

Run:  python laboratory_exercises.py
"""

from __future__ import annotations

import os

import numpy as np
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# Global constants & styling
# ----------------------------------------------------------------------------
E = np.e                                             # 2.718281828459045235360287...
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Clean, colour-blind friendly palette
C_BLUE = "#1f6fd6"       # a = 2 / main bars
C_GREEN = "#2ca02c"      # a = e
C_RED = "#d62728"        # a = 3
C_PURPLE = "#9467bd"     # errors / Taylor error curve
C_GREY = "#555555"       # references / annotations
C_DARK = "#111111"
EPS64 = np.finfo(float).eps                          # 2.220446e-16 double-precision floor

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": C_DARK,
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "axes.grid.axis": "both",
    "grid.color": "#bbbbbb",
    "grid.linestyle": "--",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.55,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "figure.titlesize": 12.5,
    "figure.titleweight": "bold",
    "legend.fontsize": 9,
    "legend.frameon": True,
    "legend.framealpha": 0.95,
    "legend.edgecolor": "#999999",
    "savefig.bbox": "tight",
    "savefig.dpi": 200,
})


def _style_axis(ax, xlabel: str, ylabel: str, legend_on: bool = True) -> None:
    """Shared axis cosmetics used by every subplot."""
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    if legend_on:
        ax.legend(loc="best", framealpha=0.95)


def _save(fig, name: str) -> str:
    """Save a figure and close it, returning the absolute output path."""
    path = os.path.join(OUT_DIR, name)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print(f"  saved  {os.path.relpath(path)}")
    return path
# ----------------------------------------------------------------------------
# Exercise 1 -- (1 + 1/n)^n --> e
# ----------------------------------------------------------------------------
def exercise1() -> None:
    """Compound-interest limit: bars of (1 + 1/n)^n and log-scaled error bars."""
    intervals = {
        "yearly":        1,
        "half-year":     2,
        "quarterly":     4,
        "monthly":       12,
        "weekly":        52,
        "daily":         365,
        "hourly":        8760,
        "minutely":      525600,
        "secondly":      31536000,
        "millisec":      31536000 * 10 ** 3,
        "microsec":      31536000 * 10 ** 6,
        "nanosec":       31536000 * 10 ** 9,
    }
    labels = list(intervals.keys())
    n = np.array(list(intervals.values()), dtype=float)

    # Numerically stable evaluation: (1 + 1/n)^n = exp(n * ln(1 + 1/n))
    # np.log1p keeps log(1 + h) accurate even when h is tiny.
    values = np.exp(n * np.log1p(1.0 / n))
    errors = np.abs(values - E)
    asymp = E / (2.0 * n)          # leading-order asymptotic error e/(2n)

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(15.5, 6.2))
    fig.suptitle(r"Exercise 1: Convergence of $(1+1/n)^n$ to $e$")
    x = np.arange(len(labels))

    # ---- Left: bar chart of the computed values + dashed reference at e ----
    ax_left.bar(x, values, width=0.62, color=C_BLUE,
                label=r"$(1+1/n)^n$", zorder=3)
    ax_left.axhline(E, color=C_GREY, linestyle="--", linewidth=1.3,
                    label=r"$e \approx 2.718282$", zorder=2)
    ax_left.set_xticks(x)
    ax_left.set_xticklabels(labels)
    ax_left.set_ylim(1.95, 2.85)
    _style_axis(ax_left, "compounding interval", r"$(1+1/n)^n$")
    ax_left.set_title("Value per compounding period")

    # ---- Right: log-scale bar chart of the absolute error ----
    ax_right.bar(x, errors, width=0.62, color=C_PURPLE,
                 label=r"$\left|(1+1/n)^n - e\right|$", zorder=3)
    # reference line: the asymptotic error e/(2n)
    ax_right.plot(x, asymp, marker="o", markersize=3.5, linestyle="--",
                  linewidth=1.1, color=C_GREY,
                  label=r"$e/(2n)$ (asymptotic)", zorder=2)
    ax_right.axhline(EPS64, color=C_RED, linestyle=":", linewidth=1.1,
                     label=r"double-precision floor $\approx 2.2\times10^{-16}$",
                     zorder=2)
    ax_right.set_yscale("log")
    ax_right.set_ylim(1e-17, 1e1)
    ax_right.set_xticks(x)
    ax_right.set_xticklabels(labels)
    _style_axis(ax_right, "compounding interval", "absolute error")
    ax_right.set_title("Log-scale error vs $e/(2n)$")
    ax_right.grid(True, which="minor", axis="y", linestyle=":", linewidth=0.5,
                  alpha=0.4)

    _save(fig, "exercise1_convergence_to_e.png")
# ----------------------------------------------------------------------------
# Exercise 2 -- (a^h - 1)/h --> ln(a)
# ----------------------------------------------------------------------------
def exercise2() -> None:
    """Grouped bar chart of the difference quotient (a^h - 1)/h vs. h."""
    h_vals = np.array([0.1, 0.01, 0.001, 0.0001, 1e-5, 1e-6, 1e-7])
    bases = [
        ("a = 2", 2.0, np.log(2.0), C_BLUE,  r"$\ln\,2 \approx 0.6931$"),
        ("a = e", np.e, 1.0, C_GREEN,        r"$\ln\,e = 1.0000$"),
        ("a = 3", 3.0, np.log(3.0), C_RED,   r"$\ln\,3 \approx 1.0986$"),
    ]

    x = np.arange(len(h_vals))                # group positions
    width = 0.26                              # one bar per base, per group
    fig, ax = plt.subplots(figsize=(12.5, 7.0))
    fig.suptitle(r"Exercise 2: $(a^h - 1)/h$ settling to $\ln(a)$")
    ax.set_title("Bars: difference quotient per $h$.  Dashed lines: the limit $\\ln(a)$.",
                 fontsize=10)

    for i, (name, a, ln_a, colour, _ln_label) in enumerate(bases):
        offset = (i - 1) * width
        # Numerically stable (a^h - 1)/h via expm1 (no catastrophic cancellation)
        quotient = np.expm1(h_vals * np.log(a)) / h_vals
        ax.bar(x + offset, quotient, width=width, color=colour, label=name, zorder=3)
        ax.axhline(ln_a, color=colour, linestyle="--", linewidth=1.3, zorder=2)

    # Legend: bars first, then the dashed limit lines (matching colours).
    bar_handles = [mpatches.Patch(facecolor=colour, label=name)
                   for name, _a, _ln, colour, _lab in bases]
    line_handles = [mlines.Line2D([0], [0], color=colour, linestyle="--",
                                  linewidth=1.3, label=ln_label)
                    for _name, _a, _ln, colour, ln_label in bases]

    # tolerance note: |q(h) - ln(a)| < 1e-6 is reached once h <= 1e-6
    ax.annotate(r"tolerance reached: $\left|(a^h-1)/h - \ln a\right| < 10^{-6}$"
                r"  for  $h \leq 10^{-6}$",
                xy=(0.99, 1.015), xycoords="axes fraction", ha="right", va="bottom",
                fontsize=9, color=C_DARK,
                bbox=dict(boxstyle="round,pad=0.35", fc="#fdf6df",
                          ec="#c9a227", alpha=0.9))

    ax.set_xticks(x)
    ax.set_xticklabels([f"{h:g}" for h in h_vals])
    _style_axis(ax, r"step size $h$", r"difference quotient  $(a^h - 1)/h$",
                legend_on=False)
    ax.set_ylim(0.55, 1.35)
    ax.legend(handles=bar_handles + line_handles, loc="lower right", ncol=2,
              framealpha=0.96)

    _save(fig, "exercise2_quotient_to_ln.png")
# ----------------------------------------------------------------------------
# Exercise 3 -- Taylor series  e^x = sum x^n / n!   (x = 1, N <= 10 000)
# ----------------------------------------------------------------------------
def exercise3() -> None:
    """Taylor partial sums of e^x at x = 1 and the log-log error behaviour."""
    x_val = 1.0
    n_max = 10_000
    chosen = [0, 1, 2, 3, 4, 5, 10, 100, 1000, n_max]

    # Iterative accumulation of the terms x^n / n!  (avoids 171! overflow)
    partial = np.empty(n_max + 1, dtype=float)
    term = 1.0                     # term for n = 0  ->  x^0 / 0! = 1
    partial[0] = term
    for n in range(1, n_max + 1):
        term *= x_val / n
        partial[n] = partial[n - 1] + term

    errors = np.abs(partial - E)
    n_axis = np.arange(1, n_max + 1)          # errors for every N >= 1
    err_axis = errors[1:]
    n_min = int(n_axis[np.argmin(err_axis)])

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(15.5, 6.2))
    fig.suptitle(r"Exercise 3: $e^x = \sum_{n=0}^{N} x^n / n!$  ($x=1$),  "
                 r"summation up to $N = 10\,000$ terms")

    # ---- Left: bar chart of partial sums at selected N ----
    y = partial[chosen]
    ax_left.bar(np.arange(len(chosen)), y, width=0.62, color=C_BLUE, zorder=3,
                label=r"partial sum  $S_N = \sum_{n=0}^{N} 1/n!$")
    ax_left.axhline(E, color=C_GREY, linestyle="--", linewidth=1.3,
                    label=r"$e \approx 2.718282$", zorder=2)
    ax_left.set_xticks(np.arange(len(chosen)))
    ax_left.set_xticklabels(chosen)
    ax_left.set_ylim(0.0, 3.1)
    _style_axis(ax_left, "terms summed  $N$", r"$S_N$")
    ax_left.set_title("Partial sums of $e^1$")

    # ---- Right: log-log plot of |S_N - e| for every N >= 1 ----
    ax_right.plot(n_axis, err_axis, linewidth=1.8, color=C_PURPLE, zorder=3,
                  label=r"$|S_N - e|$")
    ax_right.axhline(EPS64, color=C_RED, linestyle=":", linewidth=1.1,
                     label=r"double-precision floor $\approx 2.2\times10^{-16}$",
                     zorder=2)
    ax_right.set_xscale("log")
    ax_right.set_yscale("log")
    ax_right.set_ylim(1e-17, 2)
    _style_axis(ax_right, "terms summed  $N$", "absolute error")
    ax_right.set_title("Error every term $N$ buys (log-log)")
    ax_right.grid(True, which="minor", axis="both", linestyle=":", linewidth=0.5,
                  alpha=0.4)
    ax_right.annotate(r"machine-precision floor reached at $N \approx %d$" % n_min,
                      xy=(0.55, 0.08), xycoords="axes fraction", fontsize=9,
                      color=C_DARK, ha="center",
                      bbox=dict(boxstyle="round,pad=0.35", fc="#fdf6df",
                                ec="#c9a227", alpha=0.9))

    _save(fig, "exercise3_taylor_series_e.png")


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Generating the three laboratory-exercise figures into: {OUT_DIR}")
    exercise1()
    exercise2()
    exercise3()
    print("Done.")