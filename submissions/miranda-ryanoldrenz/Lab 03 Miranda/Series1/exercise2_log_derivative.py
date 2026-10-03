"""
Exercise 2: (a^h - 1)/h settling to ln(a)
==========================================
Study the difference quotient (a^h - 1)/h as h shrinks toward zero.
For three different bases a = 2, a = e, and a = 3, the quotient
converges to the natural logarithm ln(a).

Reference Table (from Series 1):
    h       a=2         a=e         a=3
    0.1     0.7177      1.0517      1.1612
    0.01    0.6956      1.0050      1.1047
    0.001   0.6934      1.0005      1.0992
    0.0001  0.6932      1.00005     1.0987
    ...     ...         ...         ...
    -> 0    ln(2)=0.6931  ln(e)=1.0000  ln(3)=1.0986
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 1. COMPUTE THE DIFFERENCE QUOTIENT FOR SHRINKING h
# ---------------------------------------------------------------
bases = [2.0, np.e, 3.0]
base_labels = ['a = 2', 'a = e', 'a = 3']
h_values = [0.1, 0.01, 0.001, 0.0001, 1e-5, 1e-6, 1e-7]

# Store results: results[base_idx][h_idx]
results = np.zeros((len(bases), len(h_values)))

for i, a in enumerate(bases):
    for j, h in enumerate(h_values):
        results[i, j] = (a**h - 1.0) / h

# ---------------------------------------------------------------
# 2. PRINT THE TABLE (matching the exercise sheet)
# ---------------------------------------------------------------
print("=" * 60)
print("Exercise 2: (a^h - 1)/h settling to ln(a)")
print("=" * 60)
print(f"{'h':<12} {'a=2':<15} {'a=e':<15} {'a=3':<15}")
print("-" * 60)
for j, h in enumerate(h_values):
    print(f"{h:<12.0e} {results[0,j]:<15.4f} {results[1,j]:<15.4f} {results[2,j]:<15.4f}")
print("-" * 60)
print(f"{'-> 0':<12} {np.log(2):<15.4f} {np.log(np.e):<15.4f} {np.log(3):<15.4f}")
print(f"\nLimits: ln(2) = {np.log(2):.4f}, ln(e) = {np.log(np.e):.4f}, ln(3) = {np.log(3):.4f}")
print()

# ---------------------------------------------------------------
# 3. CREATE THE HISTOGRAM (as required by the exercise sheet)
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300, sharey=True)

colors = ['#1B365D', '#D90429', '#2A9D8F']

for idx, (a, label, color) in enumerate(zip(bases, base_labels, colors)):
    ax = axes[idx]
    x_pos = np.arange(len(h_values))

    # Bar chart of difference quotient values per h
    bars = ax.bar(x_pos, results[idx], color=color, edgecolor='black',
                  linewidth=0.6, alpha=0.8, width=0.7)

    # Dashed line at the limit ln(a)
    limit_val = np.log(a)
    ax.axhline(limit_val, color='red', linestyle='--', linewidth=2,
               label=f'ln({a:.0f}) = {limit_val:.4f}' if a != np.e else f'ln(e) = {limit_val:.4f}')

    # Value labels
    for i, val in enumerate(results[idx]):
        ax.text(i, val + 0.01, f'{val:.4f}', ha='center', va='bottom',
                fontsize=7, fontweight='bold', color='#333333')

    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{h:.0e}' for h in h_values], fontsize=8, rotation=45)
    ax.set_xlabel('h (step size)', fontsize=10, fontweight='bold')
    ax.set_title(f'{label}  →  ln(a) = {limit_val:.4f}', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', linestyle='--', alpha=0.4)
    ax.legend(fontsize=8, loc='lower right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

axes[0].set_ylabel('(a$^h$ - 1) / h', fontsize=11, fontweight='bold')
fig.suptitle('Exercise 2: Difference Quotient (a$^h$ - 1)/h Settling to ln(a) as h Shrinks',
             fontsize=13, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('exercise2_histogram.png', dpi=300, bbox_inches='tight')
plt.close()

print("Histogram saved: exercise2_histogram.png")

# ---------------------------------------------------------------
# 4. ERROR ANALYSIS: How close to ln(a) does each h get?
# ---------------------------------------------------------------
print("\nError Analysis (|(a^h - 1)/h - ln(a)|):")
print(f"{'h':<12} {'a=2 error':<15} {'a=e error':<15} {'a=3 error':<15}")
for j, h in enumerate(h_values):
    errs = [abs(results[i, j] - np.log(bases[i])) for i in range(3)]
    print(f"{h:<12.0e} {errs[0]:<15.6e} {errs[1]:<15.6e} {errs[2]:<15.6e}")