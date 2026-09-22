"""
Series 1 - Exercise 3: e^x = sum(x^n/n!) for x=1, up to N=10,000 terms
Villondo, Angel Rain L. | BSCE-3D | Numerical Solutions
"""
import numpy as np
import matplotlib.pyplot as plt

# Compute e^x using the Taylor series: e^x = sum_{n=0}^{N} x^n / n!
x = 1.0
N_max = 10000

# Compute partial sums
partial_sums = []
term = 1.0  # x^0 / 0! = 1
partial_sum = 0.0

for n in range(N_max + 1):
    if n > 0:
        term *= x / n  # term_n = term_{n-1} * x/n
    partial_sum += term
    partial_sums.append(partial_sum)

e_true = np.e  # 2.718281828459045...

print("=" * 80)
print("Exercise 3: e^x = sum(x^n/n!) for x = 1, up to N = 10,000 terms")
print("=" * 80)
print(f"True value of e = {e_true:.15f}")
print(f"Partial sum at N=10,000 = {partial_sums[-1]:.15f}")
print(f"Error at N=10,000 = {abs(e_true - partial_sums[-1]):.2e}")

# How many correct digits each partial sum gives
# Correct digits = -log10(|e - partial_sum|)
correct_digits = []
for s in partial_sums:
    error = abs(e_true - s)
    if error > 0:
        correct_digits.append(-np.log10(error))
    else:
        correct_digits.append(16)  # machine precision limit

# Create the plots
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Histogram of partial sums
ax1 = axes[0]
# Show first 50 partial sums as histogram
n_show = 50
ax1.bar(range(n_show + 1), partial_sums[:n_show + 1], color='steelblue', 
        edgecolor='black', linewidth=0.3, alpha=0.8)
ax1.axhline(e_true, color='red', linestyle='--', linewidth=2, label=f'e = {e_true:.6f}')
ax1.set_xlabel('Number of terms (N)')
ax1.set_ylabel('Partial sum')
ax1.set_title('Histogram of Partial Sums\n(e^x = sum(x^n/n!), x = 1)', fontsize=10)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Right: Correct digits vs N (log-log)
ax2 = axes[1]
# Show up to N=10000 on log scale
n_vals = np.arange(1, N_max + 1)
cd_vals = np.array(correct_digits[1:])  # skip n=0

ax2.loglog(n_vals, cd_vals, 'b-', linewidth=1.5)
ax2.set_xlabel('Number of terms (N) [log scale]')
ax2.set_ylabel('Correct digits [log scale]')
ax2.set_title('How Many Correct Digits Each Partial Sum Gives\n(log-log)', fontsize=10)
ax2.grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.savefig('lab 004/Series1_Exercise3_Output.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nOutput saved to: lab 004/Series1_Exercise3_Output.png")