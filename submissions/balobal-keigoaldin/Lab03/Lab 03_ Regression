"""
Lab 03: Real-World Data Linear Regression
Data: NOAA Mauna Loa Observatory annual mean atmospheric CO2 concentration
Source: NOAA Global Monitoring Laboratory
        https://gml.noaa.gov/ccgg/trends/  (data file: co2_annmean_mlo.csv)
x = Year
y = Annual mean atmospheric CO2 concentration (ppm)

This script computes a simple linear least-squares regression
(y = a0 + a1*x) "by hand" using the standard formulas, without calling
a built-in regression function, then reports the standard statistics
required for the lab and produces the two required plots.
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 1. Data
# ---------------------------------------------------------------
year = np.array([2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015,
                  2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])

co2 = np.array([382.09, 384.02, 385.83, 387.64, 390.10, 391.85, 394.06, 396.74,
                 398.81, 401.01, 404.41, 406.76, 408.72, 411.65, 414.21, 416.41,
                 418.53, 421.08, 424.61, 427.35])

n = len(year)

# ---------------------------------------------------------------
# 2. Least-squares coefficients (standard formulas)
#    a1 = ( n*sum(xy) - sum(x)*sum(y) ) / ( n*sum(x^2) - (sum(x))^2 )
#    a0 = ybar - a1*xbar
# ---------------------------------------------------------------
sum_x = np.sum(year)
sum_y = np.sum(co2)
sum_xy = np.sum(year * co2)
sum_x2 = np.sum(year ** 2)

a1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
a0 = (sum_y - a1 * sum_x) / n

print(f"Slope (a1)     = {a1:.5f}  ppm/year")
print(f"Intercept (a0) = {a0:.5f}  ppm")

# ---------------------------------------------------------------
# 3. Goodness of fit: Sr (SSE), r^2, standard error of the estimate
# ---------------------------------------------------------------
y_pred = a0 + a1 * year
residuals = co2 - y_pred

St = np.sum((co2 - np.mean(co2)) ** 2)   # total sum of squares
Sr = np.sum(residuals ** 2)              # residual sum of squares (SSE)

r2 = 1 - Sr / St
syx = np.sqrt(Sr / (n - 2))              # standard error of the estimate

print(f"Sr (SSE)       = {Sr:.5f}")
print(f"r^2            = {r2:.6f}")
print(f"s_y/x          = {syx:.5f}  ppm")

# ---------------------------------------------------------------
# 4. Prediction for a year not in the dataset
# ---------------------------------------------------------------
x_new = 2030
y_new = a0 + a1 * x_new
print(f"Predicted CO2 in {x_new}: {y_new:.2f} ppm")

# ---------------------------------------------------------------
# 5. Plots
# ---------------------------------------------------------------
plt.figure(figsize=(7, 5))
plt.scatter(year, co2, color="tab:blue", label="Observed annual mean CO2")
plt.plot(year, y_pred, color="tab:red",
         label=f"Fit: y = {a0:.2f} + {a1:.3f}x")
plt.xlabel("Year")
plt.ylabel("Atmospheric CO2 concentration (ppm)")
plt.title("Mauna Loa Annual Mean CO2 vs. Year")
plt.legend()
plt.tight_layout()
plt.savefig("fit_plot.png", dpi=150)
plt.close()

plt.figure(figsize=(7, 4))
plt.axhline(0, color="black", linewidth=1)
plt.scatter(year, residuals, color="tab:green")
plt.xlabel("Year")
plt.ylabel("Residual (ppm)")
plt.title("Residual Plot")
plt.tight_layout()
plt.savefig("residual_plot.png", dpi=150)
plt.close()
