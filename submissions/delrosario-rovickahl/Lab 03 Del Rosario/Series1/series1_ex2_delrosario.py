"""
Numerical Solutions Lab -- Series 1 -- Exercise 2
=================================================
Difference quotient  (a^h - 1)/h   ->>   ln(a)   when h -> 0.

Task from the sheet:
    "2. Create the Python implementation of the table:
        Here is (a^h - 1)/h for three different bases as h shrinks.
          a=2        a=e=2.71828...      a=3
        h = 0.1      0.7177              1.0517              1.1612
        h = 0.01     0.6956              1.0050              1.1047
        h = 0.001    0.6934              1.0005              1.0992
        h = 0.0001   0.6932              1.00005             1.0987
        settles at:  ln(2)=0.6931        ln(e)=1.0000        ln(3)=1.0986
        Tolerance x 10^-6
    Draw a Histogram in Matplotlib."

The program computes (a^h - 1)/h for a in {2, e, 3} and h = 0.1, 10^-2,
10^-3, ... down to 10^-7, stops as soon as the value agrees with ln(a)
within the tolerance 10^-6, prints the table and saves Figure 2
(grouped bars = difference quotient per h; dashed lines = the limit
ln(a)).
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = 2.71828182845904523536028747135266249775724709369995
BASES = [("a = 2", 2.0), ("a = e = 2.71828...", E), ("a = 3", 3.0)]
HS = [10.0 ** (-k) for k in range(1, 8)]           # 0.1 ... 1e-7
TOL = 1.0e-6                                        # "Tolerance x 10^-6"


def main() -> None:
    print("=" * 72)
    print("SERIES 1 - EXERCISE 2:  (a^h - 1)/h  ->  ln(a)")
    print("=" * 72)

    # ------------------------------------------------------------------
    # a) the table
    # ------------------------------------------------------------------
    header = "h".rjust(10) + "".join(b.rjust(16) for b, _ in BASES)
    print("\n" + header)
    print("-" * len(header))

    data = {b: [] for b, _ in BASES}               # D-values per base
    conv_h = {}                                     # h where tol is met
    for a_name, a in BASES:
        limit = np.log(a)
        for h in HS:
            d = (a ** h - 1.0) / h
            data[a_name].append(d)
            if abs(d - limit) <= TOL and a_name not in conv_h:
                conv_h[a_name] = h

    for h, row in zip(HS, zip(*data.values())):
        print(f"{h:>10g}" + "".join(f"{v:>16.4f}" for v in row))

    # the 'settles at' row
    print("-" * len(header))
    settles = "settles at".rjust(10)
    for _name, a in BASES:
        settles += f"{np.log(a):>16.6f}"
    print(settles)
    print("\nTrue limits:  ln(2)=0.693147..., ln(e)=1.000000..., "
          "ln(3)=1.098612...")
    print("\nTolerance |(a^h-1)/h - ln(a)| <= 1e-6 reached at h =",
          {k: conv_h[k] for k in conv_h})

    # interpretation
    d2 = [(np.log(a) ** 2) * h / 2.0 for h in HS]
    print("\nCheck: (a^h-1)/h = ln(a) + (ln a)^2 * h/2 + ...  "
          "(error ~ (ln a)^2 h / 2)")

    # ------------------------------------------------------------------
    # b) Figure 2: grouped bars + dashed limit lines
    # ------------------------------------------------------------------
    plt.close("all")
    x = np.arange(len(HS))                          # 7 h-values on x
    width = 0.26
    colours = ["#4C78A8", "#E45756", "#54A24B"]
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, ((a_name, a), colour) in enumerate(zip(BASES, colours)):
        vals = data[a_name]
        pos = x + (i - 1) * width
        ax.bar(pos, vals, width, label=f"{a_name}  (ln a = {np.log(a):.4f})",
               color=colour, edgecolor="black")
        ax.axhline(np.log(a), color=colour, ls="--", lw=1.4)

    ax.set_xticks(x)
    ax.set_xticklabels([f"$10^{{{-k}}}$" for k in range(1, 8)])
    ax.set_xlabel("step size h  (logarithmic spacing)")
    ax.set_ylabel("difference quotient  (a^h - 1)/h")
    ax.set_title("Exercise 2:  (a^h - 1)/h  settling to  ln(a)")
    ax.text(0.985, 0.03,
            "Bars: difference quotient per h.\n"
            "Dashed lines: the limit ln(a).",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9)
    ax.legend(loc="lower left", fontsize=9)
    ax.set_ylim(0.55, 1.25)

    fig.tight_layout()
    fig.savefig("figure2_difference_quotient.png", dpi=150)
    print("\nSaved figure2_difference_quotient.png")


if __name__ == "__main__":
    main()