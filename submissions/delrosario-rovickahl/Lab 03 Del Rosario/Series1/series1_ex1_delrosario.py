"""
Numerical Solutions Lab -- Series 1 -- Exercise 1
=================================================
Convergence of the compound-interest sequence (1 + 1/n)^n  ->  e.

Task from the sheet:
    "1. Do the Python implementation up to nanosecond."
        How often |  value of (1 + 1/n)^n
        yearly       2.000000
        twice a year 2.250000
        quarterly    2.441406
    "Draw a Histogram in Matplotlib."

The program:
    * builds the table for every compounding frequency from yearly up to
      "per nanosecond",
    * times each computation with time.perf_counter_ns(),
    * prints the intermediate results and the deviation from e,
    * saves Figure 1 (a histogram of the values + the convergence curve
      on a logarithmic n axis with the exact value of e drawn as a dashed
      line).
"""

import time

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# 0. exact reference value of e
# ----------------------------------------------------------------------
E = 2.71828182845904523536028747135266249775724709369995
NAMES = {
    1: "yearly",
    2: "twice a year",
    4: "quarterly",
    12: "monthly",
    52: "weekly",
    365: "daily",
    8_760: "hourly",
    525_600: "per minute",
    31_536_000: "per second",
    31_536_000_000: "per millisecond",
    31_536_000_000_000: "per microsecond",
    31_536_000_000_000_000: "per nanosecond",
}


def compound(n: float) -> float:
    """The sequence value for a fixed compounding frequency n."""
    return (1.0 + 1.0 / n) ** n


def main() -> None:
    print("=" * 72)
    print("SERIES 1 - EXERCISE 1:  Convergence of (1 + 1/n)^n  to  e")
    print("=" * 72)

    # ------------------------------------------------------------------
    # a) the rows that appear on the laboratory sheet
    # ------------------------------------------------------------------
    sheet_ns = [1, 2, 4]
    print("\nTable from the sheet (How often -> (1 + 1/n)^n):")
    print(f"{'How often':<16}{'n':>8}{'value':>16}")
    for n in sheet_ns:
        print(f"{NAMES[n]:<16}{n:>8}{compound(n):>16.6f}")

    # ------------------------------------------------------------------
    # b) extend the implementation 'up to nanosecond'
    # ------------------------------------------------------------------
    print("\nExtended implementation up to nanosecond (with timing in ns):")
    print(f"{'How often':<16}{'n':>18}{'(1+1/n)^n':>16}{'time(ns)':>12}")
    rows = []
    for n in [1, 2, 4, 12, 52, 365, 8_760, 525_600, 31_536_000,
              31_536_000_000, 31_536_000_000_000, 31_536_000_000_000_000]:
        t0 = time.perf_counter_ns()
        v = compound(n)
        dt = time.perf_counter_ns() - t0
        rows.append((n, v, dt))
        print(f"{NAMES[n]:<16}{n:>14}{v:>16.6f}{dt:>12}")

    # ------------------------------------------------------------------
    # c) the error analysis: |e - (1+1/n)^n|  ~=  e / (2n)
    # ------------------------------------------------------------------
    print("\nError vs the prediction e/(2n):")
    print(f"{'n':>14}{'value':>16}{'|e-value|':>14}{'e/(2n)':>12}")
    for n, v, _dt in rows[:8]:
        print(f"{n:>14}{v:>16.10f}{abs(E - v):>14.3e}{E / (2 * n):>12.3e}")

    # float64 warning at the nanosecond row
    print("\nNOTE  float64: 1 + 1/n rounds to 1 when n > 2**53 =",
          2**53)
    print("      therefore the per-nanosecond row returns 1.0 'exactly' "
          "-- the limit is invisible there.")

    # ------------------------------------------------------------------
    # d) Figure 1 (histogram + convergence curve), saved as PNG
    # ------------------------------------------------------------------
    plt.close("all")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    # -- panel A: histogram (bar chart) of the first frequencies --------
    cats = ["yearly", "twice\na year", "quarterly", "monthly",
            "weekly", "daily"]
    vals = [compound(1), compound(2), compound(4), compound(12),
            compound(52), compound(365)]
    bars = ax1.bar(cats, vals, color="#4C78A8", edgecolor="black")
    for b, v in zip(bars, vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.4f}",
                 ha="center", fontsize=9)
    ax1.axhline(E, color="#E45756", ls="--", lw=1.6,
                label=f"e = {E:.6f}")
    ax1.set_title("Histogram: (1 + 1/n)^n per compounding period")
    ax1.set_ylabel("value of (1 + 1/n)^n")
    ax1.set_ylim(1.9, 2.85)
    ax1.legend(loc="lower right", fontsize=9)

    # -- panel B : convergence on log n, up to microsecond --------------
    ns = np.logspace(0, 13, 600)
    vs = (1.0 + 1.0 / ns) ** ns
    ax2.semilogx(ns, vs, lw=2, color="#4C78A8",
                 label="(1 + 1/n)^n")
    ax2.axhline(E, color="#E74E56", ls="--", lw=1.4,
                label=f"e = {E:.6f}")
    ax2.scatter([1, 2, 4], [compound(1), compound(2), compound(4)],
                color="k", zorder=5)
    ax2.annotate("yearly 2.000000", (1, compound(1)),
                 textcoords="offset points", xytext=(6, -14), fontsize=8)
    ax2.annotate("quarterly 2.441406", (4, compound(4)),
                 textcoords="offset points", xytext=(6, -14), fontsize=8)
    ax2.set_xlabel("compounding periods per year (log scale)")
    ax2.set_ylabel("(1 + 1/n)^n")
    ax2.set_title("Convergence of (1 + 1/n)^n to e  (log n)")
    ax2.set_ylim(2.55, 2.73)
    ax2.legend(loc="lower right", fontsize=9)
    ax2.text(0.99, 0.02, "error shrinks like e/(2n)",
             transform=ax2.transAxes, ha="right", fontsize=9,
             style="italic")

    fig.tight_layout()
    fig.savefig("figure1_compound_interest.png", dpi=150)
    print("\nSaved figure1_compound_interest.png")


if __name__ == "__main__":
    main()