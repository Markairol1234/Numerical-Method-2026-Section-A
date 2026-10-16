"""
Exercise 3: The exponential series  e^x = sum_{n=0}^{inf} x^n / n!
"Do the Python implementation of the following" with x = 1, summed up to
N = 10,000 terms, and draw a histogram in Matplotlib.

Concept
-------
The Taylor (Maclaurin) series for the exponential function is
        e^x = sum_{n=0}^{inf} x^n / n!  =  1 + x + x^2/2! + x^3/3! + ...
For x = 1 this becomes the famous series for Euler's number:
        e = 1 + 1 + 1/2! + 1/3! + 1/4! + ...
The partial sums S_N converge to e extremely fast because n! grows faster
than any exponential: the terms 1/n! collapse to zero by about n = 20, so the
partial sum reaches double-precision (machine) accuracy after only ~18-20
terms.  Adding more terms does nothing once the terms fall below machine
epsilon (~2.2e-16), which is why the error curve flattens out.

This script shows two things:
  * Left : the partial sums S_N climbing toward the dashed line e.
  * Right: a log-log view of the absolute error |S_N - e| versus N, annotated
           with how many correct decimal digits each N buys.
"""

import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = math.e
X = 1.0
N_MAX = 10_000
# A readable subset of N to display on the histograms.
DISPLAY_N = [1, 2, 3, 5, 10, 15, 20, 30, 50, 100, 200, 500, 1000, 5000, 10000]


def partial_sum(N: int) -> float:
    """Return S_N = sum_{n=0}^{N} x^n / n!  evaluated by an incremental term."""
    total = 0.0
    term = 1.0  # n = 0 term  (x^0 / 0! = 1)
    for n in range(N + 1):
        total += term
        term *= X / (n + 1)  # term_{n+1} = term_n * x / (n+1)
    return total


def correct_digits(err: float) -> float:
    """Number of correct decimal digits implied by an absolute error."""
    if err <= 0:
        return 16.0  # capped at double precision
    return min(-math.log10(err), 16.0)


def main() -> None:
    partials = [partial_sum(N) for N in DISPLAY_N]
    errors = [abs(partial_sum(N) - E) for N in DISPLAY_N]
    digits = [correct_digits(err) for err in errors]

    print("Exercise 3: e^x = sum x^n/n!  (x = 1), summation up to N = 10,000")
    print(f"e = {E:.15f}\n")
    print(f"{'N':>7}{'S_N':>18}{'|S_N - e|':>14}{'digits':>9}")
    for N, s, err, dg in zip(DISPLAY_N, partials, errors, digits):
        print(f"{N:>7}{s:>18.15f}{err:>14.2e}{dg:>9.2f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # --- Left panel: partial sums climbing to e --------------------------
    ax1.bar([str(N) for N in DISPLAY_N], partials,
            color="#7030A0", edgecolor="white")
    ax1.axhline(E, color="crimson", linestyle="--", linewidth=1.5,
                label=f"e = {E:.7f}")
    ax1.set_ylim(1.0, 3.0)
    ax1.set_xlabel("number of terms N in the summation")
    ax1.set_ylabel("S_N = sum_{n=0}^{N} x^n / n!")
    ax1.set_title("Histogram of the partial sums")
    ax1.legend(loc="lower right")
    for i, s in enumerate(partials):
        ax1.text(i, s + 0.01, f"{s:.4f}", ha="center", va="bottom",
                 fontsize=6, rotation=90)
    ax1.tick_params(axis="x", labelsize=7)

    # --- Right panel: error on log-log, digits each N buys --------------
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.plot(DISPLAY_N, [max(e, 1e-17) for e in errors],
             marker="o", color="#0070C0", linewidth=1.5)

    # Accuracy band shading for context.
    ax2.axhspan(1e-16, 1e-2, color="#C00000", alpha=0.05)
    ax2.axhspan(1e-16, 1e-6, color="#70AD47", alpha=0.06)

    for N, err, dg in zip(DISPLAY_N, errors, digits):
        ax2.annotate(f"{dg:.0f} digits",
                     xy=(N, max(err, 1e-17)),
                     xytext=(6, 6), textcoords="offset points",
                     fontsize=7, color="#0070C0")

    ax2.set_xlabel("number of terms N in the summation  (log scale)")
    ax2.set_ylabel("|S_N - e|  (log scale)")
    ax2.set_title("How many correct digits each N buys (log-log)")
    ax2.grid(True, which="both", linestyle=":", alpha=0.4)

    fig.suptitle("Exercise 3: e^x = sum x^n/n!  (x = 1), summation up to "
                 "N = 10,000 terms", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(r"d:\che school 2627\lab04\exercise3_output.png", dpi=150)
    print("\nSaved exercise3_output.png")


if __name__ == "__main__":
    main()
