"""
Exercise 1: Convergence of (1 + 1/n)^n  ->  e
"Do the Python implementation up to nanosecond" and draw a histogram in Matplotlib.

Concept
-------
If you compound interest n times per year at a 100% annual rate, the growth
factor over one year is (1 + 1/n)^n.  As n grows (yearly -> twice a year ->
quarterly -> ... -> every nanosecond) this factor approaches Euler's number
e = 2.718281828...  The error of the approximation behaves like  e / (2n),
so it falls off roughly linearly on a log scale (a "1/n" tail).

Numerical note
--------------
For astronomically large n (microsecond / nanosecond) the expression
1 + 1/n underflows in float64, so we use the numerically stable form
exp(n * log1p(1/n)) to keep the correct value of e.
"""

import math
import matplotlib
matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt

# Compounding periods: (human readable label, number of periods n in a year)
PERIODS = [
    ("yearly",              1),
    ("twice a year",        2),
    ("quarterly",           4),
    ("monthly",             12),
    ("weekly",              52),
    ("daily",               365),
    ("hourly",              365 * 24),
    ("every minute",        365 * 24 * 60),
    ("every second",        365 * 24 * 60 * 60),
    ("every millisecond",   365 * 24 * 60 * 60 * 10**3),
    ("every microsecond",   365 * 24 * 60 * 60 * 10**6),
    ("every nanosecond",    365 * 24 * 60 * 60 * 10**9),
]

E = math.e


def value_1_plus_1_over_n_pow_n(n: int) -> float:
    """Numerically stable (1 + 1/n)^n via exp(n * log1p(1/n))."""
    return math.exp(n * math.log1p(1.0 / n))


def main() -> None:
    labels = [p[0] for p in PERIODS]
    n_vals = [p[1] for p in PERIODS]
    vals = [value_1_plus_1_over_n_pow_n(n) for n in n_vals]
    errors = [abs(v - E) for v in vals]

    # Print the reference table to the console.
    print("Exercise 1: Convergence of (1 + 1/n)^n to e")
    print(f"e = {E:.15f}\n")
    print(f"{'How often':<20}{'n':>18}{'(1 + 1/n)^n':>16}{'|error|':>14}")
    for lab, n, v, err in zip(labels, n_vals, vals, errors):
        print(f"{lab:<20}{n:>18d}{v:>16.6f}{err:>14.2e}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # --- Left panel: the values themselves -------------------------------
    bars = ax1.bar(labels, vals, color="#4472C4", edgecolor="white")
    ax1.axhline(E, color="crimson", linestyle="--", linewidth=1.5,
                label=f"e = {E:.7f}")
    ax1.set_ylabel("(1 + 1/n)^n")
    ax1.set_title("Value per compounding period")
    ax1.set_ylim(1.9, 3.0)
    ax1.legend(loc="lower right")
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 0.01, f"{v:.4f}",
                 ha="center", va="bottom", fontsize=6, rotation=90)
    ax1.tick_params(axis="x", rotation=45, labelsize=7)
    for tick in ax1.get_xticklabels():
        tick.set_ha("right")

    # --- Right panel: the error on a log scale ---------------------------
    # Guard against a true-zero error so the log axis stays finite.
    plot_err = [max(err, 1e-17) for err in errors]
    ax2.bar(labels, plot_err, color="#ED7D31", edgecolor="white")
    ax2.set_yscale("log")
    ax2.set_ylabel("| (1 + 1/n)^n - e |   (log scale)")
    ax2.set_title("Error shrinks like e/(2n)")
    ax2.tick_params(axis="x", rotation=45, labelsize=7)
    for tick in ax2.get_xticklabels():
        tick.set_ha("right")

    fig.suptitle("Exercise 1: Convergence of (1 + 1/n)^n to e",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(r"d:\che school 2627\lab04\exercise1_output.png", dpi=150)
    print("\nSaved exercise1_output.png")


if __name__ == "__main__":
    main()
