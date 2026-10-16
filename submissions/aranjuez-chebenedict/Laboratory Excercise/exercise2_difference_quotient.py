"""
Exercise 2: The difference quotient  (a^h - 1) / h  settling to ln(a)
"Create the Python implementation of the table" for three bases as h shrinks,
and draw a histogram in Matplotlib.

Concept
-------
The derivative of f(a) = a^x at x = 0 is f'(0) = ln(a).  The forward
difference quotient
        (a^h - 1) / h
is a numerical estimate of that derivative.  As the step h -> 0 the estimate
converges to ln(a):

        a = 2        -> ln(2)  = 0.693147...
        a = e        -> ln(e)  = 1.000000
        a = 3        -> ln(3)  = 1.098612...

Numerical Note
--------------
For very small h the naive form (a**h - 1)/h loses precision because a**h is
extremely close to 1 (catastrophic cancellation).  The stable identity is
        a^h - 1 = expm1(h * ln(a))  =: e^{h*ln a} - 1
so we evaluate  expm1(h * ln(a)) / h, which stays accurate all the way down to
h = 1e-7 and beyond.
"""

import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASES = [("a=2", 2.0), ("a=e", math.e), ("a=3", 3.0)]
H_VALUES = [0.1, 0.01, 0.001, 0.0001, 1e-05, 1e-06, 1e-07]


def difference_quotient(a: float, h: float) -> float:
    """Numerically stable (a^h - 1)/h using expm1."""
    return math.expm1(h * math.log(a)) / h


def main() -> None:
    # Compute the table.
    table = {name: [difference_quotient(a, h) for h in H_VALUES]
             for name, a in BASES}
    limits = {name: math.log(a) for name, a in BASES}

    # Print the reference table.
    print("Exercise 2: (a^h - 1)/h settling to ln(a)")
    print(f"{'h':>10}", *[f"{name:>12}" for name, _ in BASES])
    for i, h in enumerate(H_VALUES):
        row = "".join(f"{table[name][i]:>12.4f}" for name, _ in BASES)
        print(f"{h:>10g}{row}")
    settles = "".join(f"{limits[name]:>12.4f}" for name, _ in BASES)
    print(f"{'settles at':>10}{settles}")

    fig, ax = plt.subplots(figsize=(12, 5.5))
    n_groups = len(H_VALUES)
    x = list(range(n_groups))
    width = 0.25
    colors = ["#4472C4", "#70AD47", "#C00000"]

    for k, (name, _a) in enumerate(BASES):
        offset = (k - 1) * width
        bars = ax.bar([xi + offset for xi in x], table[name],
                      width=width, label=f"{name}  (ln a = {limits[name]:.4f})",
                      color=colors[k], edgecolor="white")
        # Dashed line marking the analytic limit ln(a).
        ax.axhline(limits[name], color=colors[k], linestyle="--",
                   linewidth=1.2, alpha=0.8)
        for bar, v in zip(bars, table[name]):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.008,
                    f"{v:.4f}", ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels([f"h = {h:g}" for h in H_VALUES])
    ax.set_ylabel("(a^h - 1)/h")
    ax.set_title("Exercise 2: (a^h - 1)/h settling to ln(a)\n"
                 "Bars: difference quotient per h.  Dashed lines: the limit ln(a).")
    ax.set_ylim(0.6, 1.2)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.4)

    fig.tight_layout()
    fig.savefig(r"d:\che school 2627\lab04\exercise2_output.png", dpi=150)
    print("\nSaved exercise2_output.png")


if __name__ == "__main__":
    main()
