import numpy as np
import matplotlib.pyplot as plt

# Annual780, >}</analysis code parameter values from NOAA
years = np.array([
    2005, 2006, 2007, 2008, 2009,
    2010, 2011, 2012, 2013, 2014,
    2015, 2016, 2017, 2018, 2019,
    2020, 2021, 2022, 2023, 2024
], dtype=float)

co2 = np.array([
    379.98, 382.09, 384.02, 385.83, 387.64,
    390.10, 391.85, 394.06, 396.74, 398.81,
    401.01, 404.41, 406.76, 408.72, 411.65,
    414.21, 416.41, 418.53, 421.08, 424.61
], dtype=float)

# x represents the number of years since 2005
x = years - 2005
y = co2
n = len(x)

print("Number of observations:", n)
print("x values:", x)
print("y values:", y)

# Calculate the summations needed for least squares
sum_x = np.sum(x)
sum_y = np.sum(y)
sum_xy = np.sum(x * y)
sum_x_squared = np.sum(x ** 2)

print("\nREQUIRED SUMS")
print("Sum of x:", sum_x)
print("Sum of y:", sum_y)
print("Sum of xy:", sum_xy)
print("Sum of x squared:", sum_x_squared)

# Calculate the slope using the least-squares formula
a1 = (
    n * sum_xy - sum_x * sum_y
) / (
    n * sum_x_squared - sum_x ** 2
)

print("\nSlope, a1:", a1)

# Calculate the intercept
mean_x = np.mean(x)
mean_y = np.mean(y)

a0 = mean_y - a1 * mean_x

print("Intercept, a0:", a0)
print(f"Regression equation: y = {a0:.4f} + {a1:.4f}x")

# Calculate the fitted CO2 values
y_predicted = a0 + a1 * x

# Residual = measured value - fitted value
residuals = y - y_predicted

print("\nFitted values:")
print(y_predicted)

print("\nResiduals:")
print(residuals)

# Sum of squared residuals or SSE
Sr = np.sum(residuals ** 2)

# Total sum of squares
St = np.sum((y - mean_y) ** 2)

# Coefficient of determination
r_squared = 1 - (Sr / St)

# Standard error of estimate
standard_error = np.sqrt(Sr / (n - 2))

print("\nREGRESSION STATISTICS")
print(f"SSE, Sr: {Sr:.4f}")
print(f"Total sum of squares, St: {St:.4f}")
print(f"r squared: {r_squared:.4f}")
print(f"Standard error: {standard_error:.4f} ppm")

# Predict the annual mean CO2 for 2025
prediction_year = 2025
prediction_x = prediction_year - 2005

prediction_co2 = a0 + a1 * prediction_x

print("\nPREDICTION")
print(f"x = {prediction_year} - 2005")
print(f"x = {prediction_x}")
print(
    f"y = {a0:.4f} + "
    f"({a1:.4f})({prediction_x})"
)
print(
    f"Predicted CO2 for {prediction_year}: "
    f"{prediction_co2:.2f} ppm")

# Plot the measurements and fitted regression line
plt.figure(figsize=(8, 5))

plt.scatter(
    years,
    y,
    color="royalblue",
    label="Measured CO2"
)

plt.plot(
    years,
    y_predicted,
    color="darkred",
    linewidth=2,
    label="Fitted line"
)

plt.xlabel("Year")
plt.ylabel("Annual Mean CO2 (ppm)")
plt.title("Annual Mean Atmospheric CO2 at Mauna Loa")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig("regression_graph.png", dpi=300)
plt.show()

# Plot the residuals
plt.figure(figsize=(8, 5))

plt.scatter(
    years,
    residuals,
    color="darkgreen"
)

plt.axhline(
    y=0,
    color="black",
    linestyle="--",
    linewidth=1
)

plt.xlabel("Year")
plt.ylabel("Residual (ppm)")
plt.title("Residual Plot for the CO2 Regression")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig("residual_plot.png", dpi=300)
plt.show()