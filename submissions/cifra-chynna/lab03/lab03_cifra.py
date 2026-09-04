# Numerical Methods - Laboratory Exercise 03
# Real-World Data Linear Regression
# Philippine Regional Population vs. GRDP, 2024

# Import NumPy for numerical calculations
import numpy as np

# This is the dataset
# Independent variable: Population of each region
# Unit: persons

x = np.array([
    14001751,
    1808985,
    5342453,
    3777608,
    12989074,
    16933234,
    3245446,
    6064426,
    4861911,
    4904944,
    6640875,
    4625929,
    3943837,
    5178326,
    5389422,
    4462776,
    2865196,
    5691583
], dtype=float)

# Dependent variable: GRDP of each region
# Unit: thousand Philippine pesos
y = np.array([
    8214308357,
    445523963,
    877318738,
    564165184,
    2892168121,
    3723568508,
    509501135,
    769941504,
    797040847,
    806010142,
    1491366498,
    621904785,
    582571225,
    1273436870,
    1376650876,
    675617883,
    439146876,
    386127983
], dtype=float)

# Number of observations
n = len(x)

# Calculating the required summations

sum_x = np.sum(x)
sum_y = np.sum(y)
sum_xy = np.sum(x * y)
sum_x2 = np.sum(x ** 2)

# Calculating the slope (a1)

a1 = (n * sum_xy - sum_x * sum_y) / \
     (n * sum_x2 - sum_x ** 2)

# Calculate the y-intercept (a0)

a0 = (sum_y - a1 * sum_x) / n

# The results

print("Number of observations:", n)
print("Sum of x:", sum_x)
print("Sum of y:", sum_y)
print("Sum of xy:", sum_xy)
print("Sum of x^2:", sum_x2)

print("\nLeast-Squares Regression Results")
print("a0 (intercept) =", a0)
print("a1 (slope)     =", a1)

# The final regression equation
print("\nRegression equation:")
print(f"y = {a0:.4f} + ({a1:.4f})x")

