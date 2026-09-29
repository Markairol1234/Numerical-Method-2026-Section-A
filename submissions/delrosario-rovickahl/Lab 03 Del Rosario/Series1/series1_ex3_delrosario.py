"""
Numerical Solutions Lab -- Series 1 -- Exercise 3
=================================================
Taylor series  e^x = sum_{n=0}^{N} x^n / n!   with x = 1,
summed up to  N = 10,000 terms.

Task from the sheet:
    "3. Do the Python implementation of the following:
        e^x = sum x^n / n!   (x = 1)
        Up to 10,000
    Draw a Histogram in Matplotlib."

The program computes the partial sums S_N = sum_{n=0}^{N} 1/n!,
keeps the running term  x^n/n!  with the recurrence  term *= x/n
(no giant factorials), prints how many correct digits each N buys,
and saves Figure 3:
    * left  : histogram of the partial sums S_N (N = 1 .. 12),
    * right : log-log plot of |e - S_N| versus the number of terms N.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = 2.71828182845904523536028747135266249775724709369995
X = 1.0
NMAX = 10_000


def correct_digits(value: float) -> int:
    """Number of matching decimal digits after the decimal point."""
    s = f"{value:.15f}"
    t = f"{E:.15f}"
    k = 0
    for a, b in zip(s[2:], t[2:]):          # skip the '2.' part
        if a == b:
            k += 1
        else:
            break
    return k


def main() -> None:
    print("=" * 72)
    print("SERIES 1 - EXERCISE 3:  e^x = sum x^n/n!  (x=1), N up to 10,000")
    print("=" * 72)

    # ------------------------------------------------------------------
    # a) accumulate the partial sums (term recurrence, fast & exact)
    # ------------------------------------------------------------------
    S = 1.0                 # term n = 0   (1/0! = 1)
    term = 1.0              # term n = 1   (x/1)
    partials = [S]
    for n in range(1, NMAX + 1):
        term *= X / n
        S += term
        partials.append(S)

    # ------------------------------------------------------------------
    # b) how many correct digits each N buys
    # ------------------------------------------------------------------
    print("\nPartial sums and error  (selected N):")
    print(f"{'N':>7}{'S_N':>18}{'|e - S_N|':>16}{'digits':>8}")
    interesting = list(range(1, 13)) + [20, 25, 30, 40, 60, 100, 1000,
                                        NMAX]
    for N in interesting:
        error = abs(E - partials[N])
        print(f"{N:>7}{partials[N]:>18.12f}{error:>16.2e}"
              f"{correct_digits(partials[N]):>8}")

    if partials[NMAX] == partials[40]:
        print("\nNOTE  S_N has already reached float64 precision by "
              "N ~ 40;")
    else:
        print(f"\nS_{NMAX} = {partials[NMAX]:.15f}")
    print("      the remaining terms (up to 10,000) add nothing in "
          "double precision,")
    print("      which is exactly what a limit 'up to 10,000 terms' "
          "must show.")

    # ------------------------------------------------------------------
    # c) Figure 3: histogram of partial sums + log-log error curve
    # ------------------------------------------------------------------
    plt.close("all")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

    # -- left panel: histogram of the partial sums ----------------------
    ns = np.arange(1, 13)
    ax1.bar(ns, [partials[n] for n in ns], color="#E45756",
            edgecolor="black")
    for n in ns:
        ax1.text(n, partials[n] + 0.02, f"{partials[n]:.3f}",
                 ha="center", fontsize=8, rotation=90)
    ax1.axhline(E, color="k", ls="--", lw=1.3, label=f"e = {E:.6f}")
    ax1.set_xlabel("number of terms N")
    ax1.set_ylabel("partial sum  S_N")
    ax1.set_title("Histogram of the partial sums of sum 1/n!")
    ax1.set_ylim(1.9, 2.85)
    ax1.legend()

    # -- right panel: log-log error -------------------------------------------------
    nn = np.arange(1, 61)
    err = np.array([abs(E - partials[n]) for n in nn])
    ax2.loglog(nn, err, "o-", color="#4C78A8", label="|e - S_N|")
    ax2.set_xlabel("number of terms N in the summation (log scale)")
    ax2.set_ylabel("|e - S_N|")
    ax2.set_title("How many correct digits each N buys (log-log)")
    for mark in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25):
        ax2.plot(mark, err[mark - 1], "kx", ms=6)
    ax2.annotate("each new term adds ~ +1 digit",
                 xy=(13, 1e-10), fontsize=9, style="italic")
    ax2.grid(True, which="both", ls=":", alpha=0.5)

    fig.tight_layout()
    fig.savefig("figure3_taylor_series.png", dpi=150)
    print("\nSaved figure3_taylor_series.png")


if __name__ == "__main__":
    main()