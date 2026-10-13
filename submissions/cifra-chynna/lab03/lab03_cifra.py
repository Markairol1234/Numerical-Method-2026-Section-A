# Numerical Methods - Laboratory 03
# Philippine Regional Population vs. GRDP, 2024

import numpy as np
import matplotlib.pyplot as plt

# Population data
x = np.array([
    14001751, 1808985, 5342453, 3777608, 12989074,
    16933234, 3245446, 6064426, 4861911, 4904944,
    6640875, 4625929, 3943837, 5178326, 5389422,
    4462776, 2865196, 5691583
], dtype=float)

# GRDP data
y = np.array([
    8214308357, 445523963, 877318738, 564165184,
    2892168121, 3723568508, 509501135, 769941504,
    797040847, 806010142, 1491366498, 621904785,
    582571225, 1273436870, 1376650876, 675617883,
    439146876, 386127983
], dtype=float)

# Number of data
n = len(x)

# Get the sums
sum_x = np.sum(x)
sum_y = np.sum(y)
sum_xy = np.sum(x * y)
sum_x2 = np.sum(x ** 2)

# Get the slope
a1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

# Get the intercept
a0 = (sum_y - a1 * sum_x) / n

# Display the results
print("Number of observations:", n)
print("Sum of x:", sum_x)
print("Sum of y:", sum_y)
print("Sum of xy:", sum_xy)
print("Sum of x^2:", sum_x2)

print("\nLeast-Squares Regression Results")
print("a0 (intercept) =", a0)
print("a1 (slope) =", a1)

print("\nRegression equation:")
print(f"y = {a0:.4f} + ({a1:.4f})x")

# Get the fitted y-values
y_fit = a0 + a1 * x

# Get the residuals
residuals = y - y_fit

# Compute St
y_mean = np.mean(y)
St = np.sum((y - y_mean) ** 2)

# Compute Sr
Sr = np.sum(residuals ** 2)

# Compute r^2
r2 = (St - Sr) / St

# Compute the standard error
syx = np.sqrt(Sr / (n - 2))

# Display the Results
print("\nGoodness-of-Fit Statistics")
print("St (total sum of squares) =", St)
print("Sr (SSE, sum of squares of residuals) =", Sr)
print("r^2 (coefficient of determination) =", r2)
print("s(y/x) (standard error of the estimate) =", syx)

# Graph of Data points with the fitted line
plt.figure()
plt.scatter(x, y, label="Data points")         # actual data as dots
plt.plot(x, y_fit, color="red", label="Fitted line")  # our regression line
plt.xlabel("Population")
plt.ylabel("GRDP (in pesos)")
plt.title("Population vs. GRDP with Fitted Regression Line")
plt.legend()
plt.tight_layout()
plt.savefig("fitted_line.png", dpi=150)
plt.show()

# Graph of Residual Plot
plt.figure()
plt.scatter(x, residuals)
plt.axhline(y=0, color="red", linestyle="--")  # zero-error reference line
plt.xlabel("Population")
plt.ylabel("Residual (actual y - predicted y)")
plt.title("Residual Plot")
plt.tight_layout()
plt.savefig("residual_plot.png", dpi=150)
plt.show()
