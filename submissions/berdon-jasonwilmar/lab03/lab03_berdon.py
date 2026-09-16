import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


# 1. Data
data = {
    'Year': [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999,
              2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
              2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
              2020, 2021, 2022, 2023],
    'LifeExpectancy': [64.382, 64.622, 65.353, 65.661, 66.000, 66.311, 66.691, 66.994, 67.212, 67.503,
                        67.789, 67.829, 67.886, 68.049, 68.301, 68.423, 68.172, 68.549, 68.643, 68.631,
                        68.883, 69.096, 69.237, 69.283, 69.311, 69.450, 69.490, 69.966, 69.761, 69.680,
                        70.097, 66.675, 69.472, 69.833]
}

df = pd.DataFrame(data)


# 2. Simple linear regression 
def simple_linear_regression(X, y):
    model = LinearRegression()
    model.fit(X, y)
    print("Simple Linear Regression Coefficients:")
    print("Slope (Coefficient):", model.coef_[0])
    print("Intercept:", model.intercept_)
    print(f"Y = {model.intercept_:,.4f} + {model.coef_[0]:,.4f}X")
    print("------------------------------")
    return model


X = df[['Year']]
y = df['LifeExpectancy']

model = simple_linear_regression(X, y)
a1 = model.coef_[0]          # slope
a0 = model.intercept_        # intercept

y_pred = model.predict(X)


# 3. Goodness-of-fit statistics: Sr (SSE), r^2, standard error sy/x
n = len(df)
residuals = y.values - y_pred

Sr = np.sum(residuals ** 2)                      # sum of squares of residuals (SSE)
St = np.sum((y.values - y.mean()) ** 2)          # total sum of squares
r2 = 1 - (Sr / St)                               # coefficient of determination
syx = np.sqrt(Sr / (n - 2))                      # standard error of the estimate

print(f"Sr (SSE)        = {Sr:,.4f}")
print(f"r^2             = {r2:,.4f}")
print(f"Standard error (sy/x) = {syx:,.4f}")
print("------------------------------")



# 4. Prediction for a year not in the dataset
year_new = 2027
pred_new = model.predict(pd.DataFrame({'Year': [year_new]}))[0]
print(f"Predicted life expectancy for {year_new}: {pred_new:,.2f} years")
print(f"Y = {a0:,.4f} + {a1:,.4f}({year_new}) = {pred_new:,.4f}")
print("------------------------------")


# 5. Plot: data points with fitted line
plt.figure(figsize=(8, 5))
plt.scatter(df['Year'], df['LifeExpectancy'], color='#1f4e79', label='Observed data')
plt.plot(df['Year'], y_pred, color='#c8963e', linewidth=2, label='Fitted line')
plt.xlabel('Year')
plt.ylabel('Life expectancy at birth (years)')
plt.title('Philippines Life Expectancy vs. Year (1990-2023)')
plt.legend()
plt.tight_layout()
plt.savefig('fit_plot.png', dpi=150)
plt.show()


# 6. Residual Plot
plt.figure(figsize=(8, 5))
plt.scatter(df['Year'], residuals, color='#1f4e79')
plt.axhline(0, color='#c8963e', linewidth=2)
plt.xlabel('Year')
plt.ylabel('Residual (years)')
plt.title('Residual Plot')
plt.tight_layout()
plt.savefig('residual_plot.png', dpi=150)
plt.show()