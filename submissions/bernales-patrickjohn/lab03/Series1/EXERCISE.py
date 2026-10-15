# series1_ex1.py
import numpy as np
import matplotlib.pyplot as plt

# Calculate (1 + 1/n)^n for different n values
n_values = np.array([1, 2, 4, 12, 52, 365, 1000, 10000, 100000, 1000000])
results = (1 + 1/n_values)**n_values

# Create the histogram
plt.figure(figsize=(12, 6))
bars = plt.bar(range(len(n_values)), results, color='skyblue', edgecolor='navy', alpha=0.7)

# Add value labels on top of bars
for i, v in enumerate(results):
    plt.text(i, v + 0.001, f'{v:.6f}', ha='center', va='bottom', fontsize=9)

plt.xlabel('n (frequency)', fontsize=12)
plt.ylabel('(1 + 1/n)^n', fontsize=12)
plt.title('Convergence of (1 + 1/n)^n to e', fontsize=14)
plt.xticks(range(len(n_values)), [str(n) for n in n_values], rotation=45)
plt.axhline(y=np.e, color='red', linestyle='--', label=f'e = {np.e:.6f}')
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('series1_ex1.png', dpi=300)
plt.show()

print("Exercise 1 Results:")
print("n\t\t(1 + 1/n)^n")
for n, val in zip(n_values, results):
    print(f"{n}\t\t{val:.10f}")
print(f"\nConverges to e = {np.e:.10f}")