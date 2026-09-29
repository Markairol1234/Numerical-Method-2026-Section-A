# Numerical Solutions Lab — Series 1

**Topic:** three fundamental limits that produce the numbers **e** and **ln(a)**,
implemented in Python and plotted with Matplotlib.

## Files

| File | Purpose |
|------|---------|
| `Series1.pdf` (parent folder) | the original laboratory sheet (2 pages, scanned) |
| `series1_ex1.py` | Exercise 1 — compound interest `(1 + 1/n)^n → e` (yearly … up to nanosecond), table + histogram |
| `series1_ex2.py` | Exercise 2 — difference quotient `(a^h − 1)/h → ln(a)` for `a = 2, e, 3`, table + bars |
| `series1_ex3.py` | Exercise 3 — Taylor series `e^x = Σ x^n/n! (x = 1)` up to `N = 10,000`, partial sums + log-log error |
| `figure1_compound_interest.png` | output figure of Exercise 1 |
| `figure2_difference_quotient.png` | output figure of Exercise 2 |
| `figure3_taylor_series.png` | output figure of Exercise 3 |
| `dashboard.html` | HTML dashboard: explanations, tables, figures, interpretation of every result |
| `build_presentation.py` | builds the PowerPoint deck (concept + answers) |
| `series1_presentation.pptx` | the PowerPoint presentation (8 slides) |

## How to run

```bash
python series1_ex1.py     # prints the (1+1/n)^n table and saves figure1_compound_interest.png
python series1_ex2.py     # prints the (a^h-1)/h table  and saves figure2_difference_quotient.png
python series1_ex3.py     # prints the Taylor partial sums and saves figure3_taylor_series.png
python build_presentation.py   # re-creates series1_presentation.pptx
# then open dashboard.html in any browser
```

Requirements: Python 3.9+, `numpy`, `matplotlib`, and `python-pptx` (only for the slides).
All scripts set the Matplotlib `Agg` backend, so they run headless.

## Answers (summary)

1. `(1 + 1/n)^n`: yearly / twice a year / quarterly → `2.000000 / 2.250000 / 2.441406`,
   tending to **e = 2.718282** as the compounding frequency goes up to a nanosecond;
   error ≈ `e/(2n)`, float64 saturates at `n > 2^53`.
2. `(a^h − 1)/h`: settles at `ln(a)` = `0.693147 / 1.000000 / 1.098612` for `a = 2, e, 3`
   within a `10^-6` tolerance at `h = 10^-6`.
3. `Σ x^n/n!` with `x = 1`: the partial sums converge to **e**; each term buys ~1 correct
   digit and double precision is reached by `N ≈ 20–40` (way before `10,000`).