"""
Exercise 1: Convergence of (1 + 1/n)^n to e
============================================
Study the classic compound-interest limit: as the number of compounding
periods n increases, the value (1 + 1/n)^n approaches Euler's number e.
This script reproduces the table from Series 1 (Figure 1) and draws
a histogram in Matplotlib showing how the values converge to e.

Reference Table:
    Period          n       (1 + 1/n)^n
    Yearly          1       2.000000
    Twice a year    2       2.250000
    Quarterly       4       2.441406
    ...             ...     ...
    Continuous      inf     e = 2.718281828...
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 1. COMPUTE THE CONVERGING SEQUENCE
# ---------------------------------------------------------------
# Number of compounding periods (n values used in the exercise)
compounding_periods = [1, 2, 4, 12, 52, 365, 1000, 10000]

values = []
for n in compounding_periods:
    val = (1.0 + 1.0 / n) ** n
    values.append(val)

e_const = np.e  # 2.718281828...

# ---------------------------------------------------------------
# 2. PRINT THE TABLE (matching the exercise sheet)
# ---------------------------------------------------------------
print("=" * 58)
print("Exercise 1: Convergence of (1 + 1/n)^n to e")
print("=" * 58)
print(f"{'Compounding':<18} {'n':<12} {'(1 + 1/n)^n':<15} {'|e - value|':<15}")
print("-" * 58)
for n, val in zip(compounding_periods, values):
    print(f"{'Period':<18} {n:<12} {val:<15.6f} {abs(e_const - val):<15.6e}")
print("-" * 58)
print(f"{'Continuous':<18} {'inf':<12} {e_const:<15.6f} {'0.000000e+00':<15}")
print(f"\nSettles at e = {e_const:.10f}")
print()

# ---------------------------------------------------------------
# 3. CREATE THE HISTOGRAM (as required by the exercise sheet)
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

# Different spacing for clearer visualisation
x_pos = np.arange(len(compounding_periods))
colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(compounding_periods)))

# Bar chart of values per compounding period (effectively a histogram
# of the value distribution as n increases)
bars = ax.bar(x_pos, values, color=colors, edgecolor='black', linewidth=0.8,
              alpha=0.85, label='(1 + 1/n)^n values')

# Reference line for e
ax.axhline(e_const, color='red', linestyle='--', linewidth=2,
           label=f'e = {e_const:.6f}')

# Value labels on top of each bar
for i, (n, val) in enumerate(zip(compounding_periods, values)):
    ax.text(i, val + 0.02, f'{val:.4f}', ha='center', va='bottom',
            fontsize=8, fontweight='bold', color='#1a1a2e')

ax.set_xticks(x_pos)
ax.set_xticklabels([f'n={n}' for n in compounding_periods], fontsize=9)
ax.set_xlabel('Number of Compounding Periods (n)', fontsize=11, fontweight='bold')
ax.set_ylabel('Value of (1 + 1/n)$^n$', fontsize=11, fontweight='bold')
ax.set_title('Exercise 1: Convergence of (1 + 1/n)$^n$ to Euler\'s Number e',
             fontsize=13, fontweight='bold')
ax.set_ylim(1.9, 2.85)
ax.grid(True, axis='y', linestyle='--', alpha=0.4)
ax.legend(loc='lower right', fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('exercise1_histogram.png', dpi=300, bbox_inches='tight')
plt.close()

print("Histogram saved: exercise1_histogram.png")

# ---------------------------------------------------------------
# 4. ERROR ANALYSIS: Error shrinks like e/(2n)
# ---------------------------------------------------------------
errors = np.abs(e_const - np.array(values))
print("\nError Analysis (Error shrinks like e/(2n)):")
print(f"{'n':<10} {'|e - (1+1/n)^n|':<20} {'e/(2n)':<15} {'Ratio':<12}")
for n, err in zip(compounding_periods, errors):
    e_over_2n = e_const / (2 * n)
    ratio = err / e_over_2n if e_over_2n > 0 else float('inf')
    print(f"{n:<10} {err:<20.6e} {e_over_2n:<15.6e} {ratio:<12.4f}")