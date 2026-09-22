"""
Series 1 - Exercise 2: (a^h - 1)/h settling to ln(a)
Villondo, Angel Rain L. | BSCE-3D | Numerical Solutions
"""
import numpy as np
import matplotlib.pyplot as plt

# Three different bases
bases = [2, np.e, 3]
base_names = ['a = 2', 'a = e', 'a = 3']
ln_values = [np.log(2), np.log(np.e), np.log(3)]

# Values of h shrinking
h_values = [0.1, 0.01, 0.001, 0.0001, 1e-5, 1e-6, 1e-7]

print("=" * 80)
print("Exercise 2: (a^h - 1)/h settling to ln(a)")
print("=" * 80)

# Compute the difference quotient for each base and h
results = {}
for a, name, ln_a in zip(bases, base_names, ln_values):
    print(f"\n--- {name} (ln(a) = {ln_a:.6f}) ---")
    print(f"{'h':<12} {'(a^h - 1)/h':<20} {'Error':<20}")
    print("-" * 50)
    quotients = []
    for h in h_values:
        q = (a**h - 1) / h
        error = abs(q - ln_a)
        quotients.append(q)
        print(f"{h:<12.7f} {q:<20.10f} {error:<20.2e}")
    results[name] = quotients

# Create the plot
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, (a, name, ln_a, quotients) in enumerate(zip(bases, base_names, ln_values, results.values())):
    ax = axes[idx]
    
    # Bar chart of difference quotients
    x_pos = np.arange(len(h_values))
    bars = ax.bar(x_pos, quotients, color='steelblue', edgecolor='black', linewidth=0.5, alpha=0.8)
    
    # Dashed line at ln(a)
    ax.axhline(ln_a, color='red', linestyle='--', linewidth=2, label=f'ln({a}) = {ln_a:.4f}')
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'{h:.0e}' for h in h_values], rotation=45, fontsize=8)
    ax.set_xlabel('h')
    ax.set_ylabel('(a^h - 1)/h')
    ax.set_title(f'{name}\n(ln a = {ln_a:.4f})', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('lab 004/Series1_Exercise2_Output.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nOutput saved to: lab 004/Series1_Exercise2_Output.png")