# Import required libraries
import numpy as np                       # For numerical arrays and math
import matplotlib.pyplot as plt          # For plotting

# Define the function F(x) = x^2
def F(x):
    return x**2                          # Returns x squared

# Define the first derivative analytically: F'(x) = 2x
def dF(x):
    return 2 * x                         # Returns 2 times x

# Define the second derivative analytically: F''(x) = 2
def ddF(x):
    return np.full_like(x, 2)            # Array of 2s, same shape as x

# Create x values from -10 to 10 (400 points for smooth curves)
x = np.linspace(-10, 10, 400)            # Evenly spaced array

# Compute y values for all three functions
y   = F(x)                               # Original function
dy  = dF(x)                              # First derivative
ddy = ddF(x)                             # Second derivative

# Create a figure with 1 row and 3 columns of subplots (side by side)
fig, axes = plt.subplots(1, 3, figsize=(15, 4))   # 15x4 inch figure

# --- Subplot 1: Original function F(x) ---
axes[0].plot(x, y, color='blue')         # Plot x vs F(x)
axes[0].set_title("F(x) = x^2")          # Title
axes[0].set_xlabel("x")                  # X-axis label
axes[0].set_ylabel("F(x)")               # Y-axis label
axes[0].grid(True)                       # Add grid

# --- Subplot 2: First derivative F'(x) ---
axes[1].plot(x, dy, color='green')       # Plot x vs F'(x)
axes[1].set_title("F'(x) = 2x")          # Title
axes[1].set_xlabel("x")                  # X-axis label
axes[1].set_ylabel("F'(x)")              # Y-axis label
axes[1].grid(True)                       # Add grid

# --- Subplot 3: Second derivative F''(x) ---
axes[2].plot(x, ddy, color='red')        # Plot x vs F''(x)
axes[2].set_title("F''(x) = 2")          # Title
axes[2].set_xlabel("x")                  # X-axis label
axes[2].set_ylabel("F''(x)")             # Y-axis label
axes[2].grid(True)                       # Add grid

# Auto-adjust spacing so labels don't overlap
plt.tight_layout()

# Display the figure
plt.show()