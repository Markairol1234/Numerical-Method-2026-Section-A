"""
Exercise 3: e = sum(x^n / n!) for x = 1, up to N = 10,000 terms
================================================================
Study the Maclaurin (Taylor) series expansion of e^x evaluated at x = 1,
which yields Euler's number e as an infinite sum of reciprocal factorials:

    e = sum_{n=0}^{N} x^n / n!   (with x = 1)

This script computes partial sums up to N = 10,000 terms, counts how many
correct digits each N buys, and draws histograms for visualisation.
"""

import numpy as np
import matplotlib.pyplot as plt
from math import factorial

# ---------------------------------------------------------------
# 1. COMPUTE PARTIAL SUMS OF e = sum(x^n / n!) with x = 1
# ---------------------------------------------------------------
x = 1.0
e_const = np.e

# We'll sample partial sums at logarithmically-spaced N values
n_samples = [0, 1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]

partial_sum = 0.0
term = 1.0  # n = 0 term: x^0 / 0! = 1
partial_sums_dict = {}

for n in range(0, max(n_samples) + 1):
    if n == 0:
        term = 1.0  # x^0 / 0! = 1
    else:
        term = term * x / n  # iterative: x^n / n! = previous * x / n

    partial_sum += term

    if n in n_samples:
        partial_sums_dict[n] = partial_sum

# ---------------------------------------------------------------
# 2. PRINT THE TABLE OF PARTIAL SUMS
# ---------------------------------------------------------------
print("=" * 65)
print("Exercise 3: e = sum(x^n / n!) for x = 1, up to N = 10,000")
print("=" * 65)
print(f"{'N (terms)':<12} {'Partial Sum S_N':<22} {'|e - S_N|':<15} {'Correct Digits':<15}")
print("-" * 65)
for n in n_samples:
    s_n = partial_sums_dict[n]
    error = abs(e_const - s_n)
    # Count correct digits: if error > 0, digits = -log10(error)
    correct_digits = 0
    if error > 0:
        correct_digits = int(-np.log10(error)) if error < 1 else 0
    print(f"{n:<12} {s_n:<22.15f} {error:<15.6e} {correct_digits:<15}")
print("-" * 65)
print(f"{'10,000':<12} {partial_sums_dict[10000]:<22.15f} {'(machine ε)':<15}")
print(f"\nTrue e = {e_const:.15f}")
print()

# ---------------------------------------------------------------
# 3. CREATE THE HISTOGRAMS (as required by the exercise sheet)
# ---------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

# --- Left panel: Histogram of partial sums ---
n_vals = list(partial_sums_dict.keys())
s_vals = list(partial_sums_dict.values())

bar_colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(n_vals)))
bars = ax1.bar(range(len(n_vals)), s_vals, color=bar_colors, edgecolor='black',
               linewidth=0.5, alpha=0.85)

ax1.axhline(e_const, color='red', linestyle='--', linewidth=2,
            label=f'e = {e_const:.6f}')

for i, (n, s) in enumerate(zip(n_vals, s_vals)):
    ax1.text(i, s + 0.002, f'{s:.4f}', ha='center', va='bottom',
             fontsize=6, fontweight='bold', color='#333333', rotation=45)

ax1.set_xticks(range(len(n_vals)))
ax1.set_xticklabels([f'N={n}' for n in n_vals], fontsize=7, rotation=45)
ax1.set_xlabel('Number of Terms N in the Summation', fontsize=10, fontweight='bold')
ax1.set_ylabel('Partial Sum S$_N$ = Σ x$^n$/n!', fontsize=10, fontweight='bold')
ax1.set_title('Histogram of the Partial Sums', fontsize=12, fontweight='bold')
ax1.grid(True, axis='y', linestyle='--', alpha=0.4)
ax1.legend(fontsize=8, loc='lower right')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# --- Right panel: How many correct digits each N buys (log-log) ---
errors = [abs(e_const - partial_sums_dict[n]) for n in n_vals]

ax2.loglog(n_vals, errors, 'o-', color='#1B365D', linewidth=2,
           markersize=6, markerfacecolor='#D90429', markeredgecolor='black')

# Reference bands
ax2.axhline(1e-2, color='green', linestyle='--', linewidth=1.5,
            label='Accuracy band: err > 1e-2')
ax2.axhline(1e-4, color='orange', linestyle='--', linewidth=1.5,
            label='Accuracy band: err > 1e-4')
ax2.axhline(1e-14, color='purple', linestyle='--', linewidth=1.5,
            label='Machine precision ~ 1e-14')

ax2.set_xlabel('Number of Terms N in the Summation (log scale)', fontsize=10, fontweight='bold')
ax2.set_ylabel('|e - S$_N$| (log scale)', fontsize=10, fontweight='bold')
ax2.set_title('How Many Correct Digits Each N Buys (log-log)', fontsize=12, fontweight='bold')
ax2.grid(True, which='both', linestyle='--', alpha=0.3)
ax2.legend(fontsize=8, loc='upper right')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Annotate convergence rate: error drops factorially
ax2.annotate('Error drops ~1/N!  →  super-exponential convergence',
             xy=(200, errors[n_vals.index(200)]), xytext=(5, 1e-1),
             arrowprops=dict(arrowstyle='->', color='#666666'),
             fontsize=8, fontweight='bold', color='#495057')

fig.suptitle('Exercise 3: e = Σ x$^n$/n! (x = 1) — Partial Sums Converge to e Rapidly',
             fontsize=13, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('exercise3_histogram.png', dpi=300, bbox_inches='tight')
plt.close()

print("Histogram saved: exercise3_histogram.png")

# ---------------------------------------------------------------
# 4. ACCURACY ANALYSIS
# ---------------------------------------------------------------
print("\nAccuracy Analysis:")
print("After just N=10 terms, the partial sum matches e to:", end=" ")
s_10 = partial_sums_dict[10]
err_10 = abs(e_const - s_10)
print(f"{int(-np.log10(err_10))} correct digits (error = {err_10:.2e})")

print("After N=100 terms, the partial sum matches e to:", end=" ")
s_100 = partial_sums_dict[100]
err_100 = abs(e_const - s_100)
if err_100 > 0:
    print(f"{int(-np.log10(err_100))} correct digits (error = {err_100:.2e})")
else:
    print("full machine precision (error = 0.0)")

print("\nThis demonstrates that the factorial series for e converges")
print("super-exponentially — by the time we reach N=20, we already have")
print("more than 14 correct decimal digits!")