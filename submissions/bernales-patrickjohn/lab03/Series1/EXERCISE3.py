# series1_ex3.py
import numpy as np
import matplotlib.pyplot as plt

def taylor_e(x, n_terms):
    """Calculate e^x using Taylor series with n terms"""
    result = 0
    factorial = 1
    term = 1
    for i in range(n_terms):
        if i > 0:
            term *= x / i
        result += term
    return result

# Test for different x values
x_values = np.linspace(-5, 5, 11)
n_terms_list = [1, 2, 5, 10, 20, 50, 100]

# Calculate results
results = np.zeros((len(x_values), len(n_terms_list)))
for i, x in enumerate(x_values):
    for j, n in enumerate(n_terms_list):
        results[i, j] = taylor_e(x, n)

# Find the number of terms needed for convergence at each x
terms_needed = []
for x in x_values:
    true_val = np.exp(x)
    for n in range(1, 10000):
        approx = taylor_e(x, n)
        if abs(approx - true_val) / true_val < 1e-6:
            terms_needed.append(n)
            break
    else:
        terms_needed.append(10000)

# Create visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Convergence for specific x values
x_test = [0.5, 1, 2, 3]
n_range = range(1, 21)
for x_val in x_test:
    errors = []
    for n in n_range:
        approx = taylor_e(x_val, n)
        true = np.exp(x_val)
        errors.append(abs(approx - true)/true)
    ax1.plot(n_range, errors, label=f'x={x_val}')
ax1.set_xlabel('Number of terms')
ax1.set_ylabel('Relative Error')
ax1.set_title('Convergence of Taylor Series for e^x')
ax1.set_yscale('log')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Terms needed for convergence
ax2.bar(range(len(x_values)), terms_needed, color='skyblue', edgecolor='navy')
ax2.set_xlabel('x value')
ax2.set_ylabel('Terms needed for 10^-6 tolerance')
ax2.set_title('Number of terms needed for convergence')
ax2.set_xticks(range(len(x_values)))
ax2.set_xticklabels([f'{x:.1f}' for x in x_values], rotation=45)
ax2.grid(axis='y', alpha=0.3)

# Plot 3: Accuracy for different number of terms
x_range = np.linspace(-3, 3, 100)
for n in [1, 2, 3, 5, 10]:
    approx = [taylor_e(x, n) for x in x_range]
    ax3.plot(x_range, approx, label=f'{n} terms')
ax3.plot(x_range, np.exp(x_range), 'k--', label='True e^x', linewidth=2)
ax3.set_xlabel('x')
ax3.set_ylabel('e^x')
ax3.set_title('Taylor series approximations')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Histogram of terms needed for different x values
ax4.hist(terms_needed, bins=15, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
ax4.set_xlabel('Number of terms needed')
ax4.set_ylabel('Frequency')
ax4.set_title('Distribution of terms needed for convergence')
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('series1_ex3.png', dpi=300)
plt.show()

print("\nExercise 3 Results:")
print("x\t\tTerms needed for 10^-6 tolerance")
for x, terms in zip(x_values, terms_needed):
    print(f"{x:.1f}\t\t{terms}")