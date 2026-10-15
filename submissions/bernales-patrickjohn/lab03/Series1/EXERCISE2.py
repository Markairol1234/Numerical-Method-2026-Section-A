# series1_ex2.py
import numpy as np
import matplotlib.pyplot as plt

# Define the data
h_values = np.array([0.1, 0.01, 0.001, 0.0001])
a_values = [2, np.e, 3]
a_labels = ['a = 2', 'a = e (2.71828...)', 'a = 3']

# Calculate (a^h - 1)/h for each combination
results = np.zeros((len(h_values), len(a_values)))
for i, h in enumerate(h_values):
    for j, a in enumerate(a_values):
        results[i, j] = (a**h - 1) / h

# Create grouped bar chart
x = np.arange(len(h_values))
width = 0.25

fig, ax = plt.subplots(figsize=(12, 6))
for i in range(len(a_values)):
    ax.bar(x + i*width, results[:, i], width, label=a_labels[i])

ax.set_xlabel('h (shrinking values)', fontsize=12)
ax.set_ylabel('(a^h - 1)/h', fontsize=12)
ax.set_title('Derivative approximation using different bases', fontsize=14)
ax.set_xticks(x + width)
ax.set_xticklabels([f'{h}' for h in h_values])
ax.legend()
ax.grid(axis='y', alpha=0.3)

# Add value labels
for i in range(len(h_values)):
    for j in range(len(a_values)):
        ax.text(i + j*width, results[i, j] + 0.001, f'{results[i, j]:.4f}', 
                ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('series1_ex2.png', dpi=300)
plt.show()

print("\nExercise 2 Results:")
print("h\t\ta=2\t\ta=e\t\ta=3")
for i, h in enumerate(h_values):
    print(f"{h}\t\t{results[i,0]:.4f}\t\t{results[i,1]:.4f}\t\t{results[i,2]:.4f}")
print("\nNote: The derivative of a^x at x=0 is ln(a)")
print(f"ln(2) = {np.log(2):.4f}")
print(f"ln(e) = {np.log(np.e):.4f}")
print(f"ln(3) = {np.log(3):.4f}")