"""
Series 1 - Exercise 1: Convergence of (1 + 1/n)^n to e
Villondo, Angel Rain L. | BSCE-3D | Numerical Solutions
"""
import numpy as np
import matplotlib.pyplot as plt

# Compounding periods: how often interest is compounded per year
periods = [
    "yearly", "twice a year", "quarterly", "monthly", "weekly",
    "daily", "hourly", "minute", "second", "millisecond",
    "microsecond", "nanosecond"
]

# Number of compounding periods per year (n)
n_values = [
    1, 2, 4, 12, 52,
    365, 365 * 24, 365 * 24 * 60, 365 * 24 * 60 * 60,
    365 * 24 * 60 * 60 * 1000,
    365 * 24 * 60 * 60 * 1000 * 1000,
    365 * 24 * 60 * 60 * 1000 * 1000 * 1000
]

# Compute (1 + 1/n)^n for each compounding period
values = [(1 + 1.0 / n) ** n for n in n_values]

e = np.e  # Euler's number = 2.718281828459045...

print("=" * 70)
print("Exercise 1: Convergence of (1 + 1/n)^n to e")
print("=" * 70)
print(f"{'How often':<20} {'n':<25} {'(1 + 1/n)^n':<20} {'Error':<20}")
print("-" * 70)
for period, n, val in zip(periods, n_values, values):
    error = abs(e - val)
    print(f"{period:<20} {n:<25} {val:<20.10f} {error:<20.2e}")

print(f"\nEuler's number e = {e:.10f}")

# Create the histogram plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Histogram of (1 + 1/n)^n values
x_pos = np.arange(len(periods))
colors = plt.cm.viridis(np.linspace(0, 1, len(periods)))
bars = ax1.bar(x_pos, values, color=colors, edgecolor='black', linewidth=0.5)
ax1.axhline(e, color='red', linestyle='--', linewidth=2, label=f'e = {e:.6f}')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
ax1.set_ylabel('(1 + 1/n)^n')
ax1.set_title('Convergence of (1 + 1/n)^n to e\nValue per Compounding Period', fontsize=10)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Right: Error on log scale
errors = [abs(e - v) for v in values]
ax2.semilogy(x_pos, errors, 'o-', color='blue', markersize=6)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
ax2.set_ylabel('|e - (1 + 1/n)^n|')
ax2.set_title('Error Shrinks Like e/(2n)', fontsize=10)
ax2.grid(True, alpha=0.3, which='both')

# Add theoretical error line e/(2n)
n_theory = np.array(n_values, dtype=float)
theory_error = e / (2 * n_theory)
ax2.semilogy(x_pos, theory_error, 'r--', linewidth=1.5, label='e/(2n)')
ax2.legend()

plt.tight_layout()
plt.savefig('lab 004/Series1_Exercise1_Output.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nOutput saved to: lab 004/Series1_Exercise1_Output.png")