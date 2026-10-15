# Lab 03 - Linear Regression by Least Squares
# Numerical Methods, Section 3D

import numpy as np
import matplotlib.pyplot as plt

# ---------- 1. Data (replace with your verified values) ----------
x = np.array([2008, 2009, 2010, 2011, 2012, 2013, 2014,
              2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], dtype=float)
y = np.array([1959.292, 1864.45, 2162.914, 2383.919, 2614.616, 2781.28, 2866.838,
              2909.858, 2985.196, 3038.121, 3168.51, 3400.789, 3227.579, 3484.386, 3548.069], dtype=float)

n = len(x)

# ---------- 2. Least squares formulas ----------
# a1 = (n*sum(xy) - sum(x)*sum(y)) / (n*sum(x^2) - (sum(x))^2)
# a0 = mean(y) - a1*mean(x)
sum_x  = np.sum(x)
sum_y  = np.sum(y)
sum_xy = np.sum(x * y)
sum_x2 = np.sum(x ** 2)

a1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
a0 = (sum_y / n) - a1 * (sum_x / n)

print(f"a0 (intercept) = {a0:.4f}")
print(f"a1 (slope)     = {a1:.4f}")

# ---------- 3. Fit statistics ----------
y_hat = a0 + a1 * x                 # predicted values
Sr    = np.sum((y - y_hat) ** 2)    # SSE
St    = np.sum((y - np.mean(y)) ** 2)
r2    = (St - Sr) / St
syx   = np.sqrt(Sr / (n - 2))       # standard error of estimate

print(f"Sr (SSE)       = {Sr:.4f}")
print(f"r^2            = {r2:.4f}")
print(f"s_y/x          = {syx:.4f}")

# ---------- 4. Prediction ----------
x_new = 2025
y_new = a0 + a1 * x_new
print(f"Prediction for {x_new}: {y_new:.2f} US$")

# ---------- 5. Graph: data + fitted line ----------
plt.figure()
plt.scatter(x, y, label="Data")
plt.plot(x, y_hat, color="red", label=f"y = {a0:.1f} + {a1:.1f}x")
plt.xlabel("Year")
plt.ylabel("GDP per capita (current US$)")
plt.title("Philippines GDP per capita vs Year")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("fit.png", dpi=150)

# ---------- 6. Residual plot ----------
residuals = y - y_hat
plt.figure()
plt.axhline(0, color="black", linewidth=0.8)
plt.scatter(x, residuals)
plt.xlabel("Year")
plt.ylabel("Residual (y - y_hat)")
plt.title("Residual Plot")
plt.grid(True)
plt.tight_layout()
plt.savefig("residuals.png", dpi=150)

plt.show()