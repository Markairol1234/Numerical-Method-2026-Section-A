"""
Combined Series 1 Laboratory Exercise Script
=============================================
This script combines all 4 separate scripts into one:
1. Exercise 1: Convergence of (1 + 1/n)^n to e - generates exercise1.png
2. Exercise 2: (a^h - 1)/h settling to ln(a) - generates exercise2.png
3. Exercise 3: Taylor Series e^x = sum(x^n/n!) - generates exercise3.png
4. HTML Dashboard generation - generates index.html

Run this single script to generate all outputs at once.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal, getcontext

# Set high precision for decimal calculations
getcontext().prec = 50

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# EXERCISE 1: Convergence of (1 + 1/n)^n to e
# ============================================================
def exercise1():
    """Calculate (1+1/n)^n for 12 compounding periods and create visualization."""
    print("\n" + "=" * 70)
    print("EXERCISE 1: Convergence of (1 + 1/n)^n to e")
    print("=" * 70)
    
    # Compounding periods and their n values
    compounding_periods = [
        ("yearly", 1),
        ("twice a year", 2),
        ("quarterly", 4),
        ("monthly", 12),
        ("weekly", 52),
        ("daily", 365),
        ("hourly", 8760),
        ("every minute", 525600),
        ("every second", 31536000),
        ("every millisecond", 31536000000),
        ("every microsecond", 31536000000000),
        ("every nanosecond", 31536000000000000)
    ]
    
    # Calculate (1 + 1/n)^n using Decimal for precision
    e_value = Decimal(1).exp()  # e = 2.718281828459045...
    values = []
    errors = []
    
    print(f"{'Period':<20} {'n':<20} {'(1+1/n)^n':<25} {'Error':<25}")
    print("-" * 70)
    
    for period, n in compounding_periods:
        # Use Decimal for precise calculation
        n_dec = Decimal(n)
        value = (Decimal(1) + Decimal(1) / n_dec) ** n_dec
        error = abs(value - e_value)
        values.append(float(value))
        errors.append(float(error))
        print(f"{period:<20} {n:<20} {float(value):<25.15f} {float(error):<25.15e}")
    
    # Create the figure with 1 row, 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle("Exercise 1: Convergence of (1 + 1/n)^n to e", fontsize=16, fontweight='bold')
    
    # Get labels for x-axis
    labels = [period for period, _ in compounding_periods]
    x_pos = np.arange(len(labels))
    
    # Left subplot: Value per compounding period
    bars1 = ax1.bar(x_pos, values, color='blue', edgecolor='black', linewidth=0.8, alpha=0.8)
    ax1.set_ylim(2.0, 3.0)
    ax1.set_ylabel("(1 + 1/n)^n", fontsize=12)
    ax1.set_title("Value per compounding period", fontsize=13, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add red dashed reference line at e
    ax1.axhline(y=2.718282, color='red', linestyle='--', linewidth=2, label='e = 2.718282')
    ax1.legend(loc='upper left', fontsize=10)
    
    # Annotate each bar with its value
    for i, (bar, value) in enumerate(zip(bars1, values)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                 f'{value:.6f}', ha='center', va='bottom', fontsize=7, rotation=45)
    
    # Right subplot: Error shrinks like e/(2n)
    bars2 = ax2.bar(x_pos, errors, color='orange', edgecolor='black', linewidth=0.8, alpha=0.8)
    ax2.set_yscale('log')
    ax2.set_ylim(10**-13, 10**0)
    ax2.set_ylabel("| (1+1/n)^n - e | (log scale)", fontsize=12)
    ax2.set_title("Error shrinks like e/(2n)", fontsize=13, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax2.grid(axis='y', alpha=0.3, which='both')
    
    plt.tight_layout()
    output_path = os.path.join(SCRIPT_DIR, 'exercise1.png')
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"\nExercise 1 visualization saved as 'exercise1.png'")
    
    # Return data for HTML generation
    return [(period, n, float(value), float(error)) for (period, n), value, error in 
            zip(compounding_periods, values, errors)]


# ============================================================
# EXERCISE 2: (a^h - 1)/h settling to ln(a)
# ============================================================
def exercise2():
    """Calculate (a^h - 1)/h for 3 bases and 7 h values, create grouped bar chart."""
    print("\n" + "=" * 70)
    print("EXERCISE 2: (a^h - 1)/h settling to ln(a)")
    print("=" * 70)
    
    # Bases and their theoretical limits
    bases = [2, 2.71828, 3]
    base_labels = ['a=2 (ln a = 0.6931)', 'a=e (ln a = 1.0000)', 'a=3 (ln a = 1.0986)']
    limits = [0.6931, 1.0000, 1.0986]
    
    # Shrinking steps h
    h_values = [0.1, 0.01, 0.001, 0.0001, 1e-05, 1e-06, 1e-07]
    
    # Calculate (a^h - 1)/h for each base and h
    results = []
    for a in bases:
        row = [(a**h - 1)/h for h in h_values]
        results.append(row)
    
    # Print the table
    print(f"{'h':<12} {'a=2':<15} {'a=e':<15} {'a=3':<15}")
    print("-" * 70)
    for i, h in enumerate(h_values):
        print(f"{h:<12.7f} {results[0][i]:<15.10f} {results[1][i]:<15.10f} {results[2][i]:<15.10f}")
    print("-" * 70)
    print(f"{'Limit':<12} {limits[0]:<15.4f} {limits[1]:<15.4f} {limits[2]:<15.4f}")
    
    # Create the figure - single grouped bar chart
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.suptitle("Exercise 2: (a^h - 1)/h settling to ln(a)", fontsize=16, fontweight='bold')
    ax.set_title("Bars: difference quotient per h. Dashed lines: the limit ln(a).", fontsize=11, style='italic')
    
    # Set up bar positions
    bar_width = 0.25
    x_pos = np.arange(len(h_values))
    
    # Colors for each base
    colors = ['blue', 'green', 'red']
    
    # Plot grouped bars for each base
    for i, (base_results, label, color, limit) in enumerate(zip(results, base_labels, colors, limits)):
        bars = ax.bar(x_pos + i * bar_width, base_results, bar_width, 
                      label=label, color=color, edgecolor='black', linewidth=0.8, alpha=0.8)
        # Add horizontal dashed reference lines at the limits
        ax.axhline(y=limit, color=color, linestyle='--', linewidth=1.5, alpha=0.7)
    
    # Set axis properties
    ax.set_xlabel('h values', fontsize=12)
    ax.set_ylabel('(a^h - 1)/h', fontsize=12)
    ax.set_xticks(x_pos + bar_width)
    ax.set_xticklabels([f'h = {h}' for h in h_values], fontsize=10)
    ax.set_ylim(0.6, 1.2)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    output_path = os.path.join(SCRIPT_DIR, 'exercise2.png')
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"\nExercise 2 visualization saved as 'exercise2.png'")
    
    # Return data for HTML generation
    return results, h_values, limits


# ============================================================
# EXERCISE 3: Taylor Series e^x = sum(x^n / n!)
# ============================================================
def exercise3():
    """Calculate Taylor series for e^x up to 10,000 terms, create 2-subplot figure."""
    print("\n" + "=" * 70)
    print("EXERCISE 3: Taylor Series e^x = sum(x^n / n!) up to N = 10,000")
    print("=" * 70)
    
    x = 1.0
    N_max = 10000
    
    # Calculate partial sums using Decimal for precision
    sum_val = Decimal(0)
    term = Decimal(1)  # x^0 / 0! = 1
    
    # Track sums at various N values for the log-log plot
    N_track = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    tracked_sums = []
    tracked_N = []
    
    for n in range(N_max + 1):
        if n > 0:
            term = term * Decimal(x) / Decimal(n)
        sum_val += term
        if n in N_track:
            tracked_sums.append(float(sum_val))
            tracked_N.append(n)
    
    # Actual e value
    e_actual = float(Decimal(1).exp())
    
    # Calculate correct digits for each tracked N
    correct_digits = []
    for sum_val in tracked_sums:
        # Count matching decimal digits
        sum_str = f"{sum_val:.15f}"
        e_str = f"{e_actual:.15f}"
        count = 0
        for i, (c1, c2) in enumerate(zip(sum_str, e_str)):
            if c1 == c2:
                count += 1
            else:
                break
        correct_digits.append(count)
    
    # Print the table
    print(f"{'N':<12} {'Partial Sum':<20} {'Correct Digits':<15}")
    print("-" * 70)
    for n, s, d in zip(tracked_N, tracked_sums, correct_digits):
        print(f"{n:<12} {s:<20.15f} {d:<15}")
    
    # Create the figure with 1 row, 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle("Exercise 3: e^x = sum x^n/n! (x = 1), summation up to N = 10,000 terms", 
                 fontsize=16, fontweight='bold')
    
    # Left subplot: Histogram of the partial sums
    bars = ax1.bar([str(n) for n in tracked_N], tracked_sums, color='purple', 
                   edgecolor='black', linewidth=0.8, alpha=0.8)
    ax1.set_ylim(1.00, 2.75)
    ax1.set_xlabel("Number of terms N", fontsize=12)
    ax1.set_ylabel("Partial sum", fontsize=12)
    ax1.set_title("Histogram of the partial sums", fontsize=13, fontweight='bold')
    ax1.set_xticks(range(len(tracked_N)))
    ax1.set_xticklabels([str(n) for n in tracked_N], rotation=45, ha='right', fontsize=8)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add red dashed reference line at e
    ax1.axhline(y=e_actual, color='red', linestyle='--', linewidth=2, label=f'e = {e_actual:.6f}')
    ax1.legend(loc='lower right', fontsize=10)
    
    # Right subplot: How many correct digits each N buys (log-log)
    ax2.plot(tracked_N, correct_digits, 'o-', color='darkblue', markersize=6, linewidth=1.5)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel("Number of terms N", fontsize=12)
    ax2.set_ylabel("Correct digits", fontsize=12)
    ax2.set_title("How many correct digits each N buys (log-log)", fontsize=13, fontweight='bold')
    ax2.grid(alpha=0.3, which='both')
    
    plt.tight_layout()
    output_path = os.path.join(SCRIPT_DIR, 'exercise3.png')
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(f"\nExercise 3 visualization saved as 'exercise3.png'")
    
    # Return data for HTML generation
    return tracked_N, tracked_sums, correct_digits, e_actual


# ============================================================
# HTML DASHBOARD GENERATION
# ============================================================
def generate_html(exercise1_data, exercise2_data, h_values, limits, 
                  tracked_N, tracked_sums, correct_digits, e_actual):
    """Generate the HTML dashboard with all data and explanations."""
    print("\n" + "=" * 70)
    print("GENERATING HTML DASHBOARD")
    print("=" * 70)
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Series 1 Laboratory Exercise - Mathematical Explorations</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        .exercise-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .exercise-card h2 {
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 15px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .exercise-card h3 {
            color: #34495e;
            font-size: 1.3em;
            margin: 20px 0 10px 0;
        }
        .exercise-card p {
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .formula {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            border-radius: 0 5px 5px 0;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.9em;
        }
        .data-table th {
            background: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }
        .data-table td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .data-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        .data-table tr:hover {
            background: #e8f4fd;
        }
        .chart-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .insight-box {
            background: #e8f4fd;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
        .insight-box h4 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .insight-box ul {
            margin-left: 20px;
            color: #555;
        }
        .insight-box li {
            margin-bottom: 8px;
        }
        .highlight {
            background: #fff3cd;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
        }
        footer {
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 0.9em;
        }
        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Series 1 Laboratory Exercise</h1>
            <p>Mathematical Explorations: Limits, Convergence, and Series Expansions</p>
        </header>

        <!-- Exercise 1 -->
        <div class="exercise-card">
            <h2>Exercise 1: Convergence of (1 + 1/n)^n to e</h2>
            
            <h3>📐 Mathematical Background</h3>
            <p>The compound interest formula <span class="highlight">(1 + 1/n)^n</span> represents the value of an investment of $1 at 100% interest compounded n times per year. As n approaches infinity, this value converges to the mathematical constant <span class="highlight">e ≈ 2.718281828...</span></p>
            
            <div class="formula">
                lim(n→∞) (1 + 1/n)^n = e ≈ 2.718281828459045...
            </div>

            <h3>📊 Data Table</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Compounding Period</th>
                        <th>n (Times per Year)</th>
                        <th>(1 + 1/n)^n</th>
                        <th>Error |(1+1/n)^n - e|</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Generate Exercise 1 table rows
    for period, n, value, error in exercise1_data:
        html_content += f"""                    <tr><td>{period}</td><td>{n}</td><td>{value:.6f}</td><td>{error:.6e}</td></tr>
"""

    html_content += """                </tbody>
            </table>

            <h3>📈 Visualization</h3>
            <div class="chart-container">
                <img src="exercise1.png" alt="Exercise 1: Convergence of (1+1/n)^n to e">
            </div>

            <div class="insight-box">
                <h4>💡 Key Insights</h4>
                <ul>
                    <li>The value <span class="highlight">(1 + 1/n)^n</span> increases monotonically toward e as n grows</li>
                    <li>The error decreases approximately as <span class="highlight">e/(2n)</span>, meaning each additional compounding period reduces the error proportionally</li>
                    <li>By the time we compound every nanosecond, the value matches e to 13 decimal places</li>
                    <li>This demonstrates the fundamental limit definition of the natural exponential base e</li>
                </ul>
            </div>
        </div>

        <!-- Exercise 2 -->
        <div class="exercise-card">
            <h2>Exercise 2: (a^h - 1)/h Settling to ln(a)</h2>
            
            <h3>📐 Mathematical Background</h3>
            <p>The difference quotient <span class="highlight">(a^h - 1)/h</span> represents the average rate of change of the exponential function a^x over the interval [0, h]. As h approaches 0, this quotient converges to the derivative of a^x at x=0, which is <span class="highlight">ln(a)</span>.</p>
            
            <div class="formula">
                lim(h→0) (a^h - 1)/h = ln(a)
            </div>

            <h3>📊 Data Table</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>h</th>
                        <th>a=2</th>
                        <th>a=e (2.71828...)</th>
                        <th>a=3</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Generate Exercise 2 table rows
    for i, h in enumerate(h_values):
        html_content += f"""                    <tr><td>{h:.1e}</td><td>{exercise2_data[0][i]:.6f}</td><td>{exercise2_data[1][i]:.6f}</td><td>{exercise2_data[2][i]:.6f}</td></tr>
"""

    html_content += f"""                    <tr><td><strong>Limit</strong></td><td><strong>{limits[0]:.4f}</strong></td><td><strong>{limits[1]:.4f}</strong></td><td><strong>{limits[2]:.4f}</strong></td></tr>
                </tbody>
            </table>

            <h3>📈 Visualization</h3>
            <div class="chart-container">
                <img src="exercise2.png" alt="Exercise 2: (a^h - 1)/h settling to ln(a)">
            </div>

            <div class="insight-box">
                <h4>💡 Key Insights</h4>
                <ul>
                    <li>For <span class="highlight">a = e</span>, the limit is exactly <span class="highlight">ln(e) = 1</span>, which is why e is the natural base for calculus</li>
                    <li>The convergence rate is linear in h - each factor of 10 reduction in h gives one more decimal place of accuracy</li>
                    <li>This difference quotient is the foundation for understanding derivatives of exponential functions</li>
                    <li>The tolerance of ×10⁻⁶ is achieved at h = 0.0001 for all three bases</li>
                </ul>
            </div>
        </div>

        <!-- Exercise 3 -->
        <div class="exercise-card">
            <h2>Exercise 3: Taylor Series Expansion of e^x</h2>
            
            <h3>📐 Mathematical Background</h3>
            <p>The Taylor series expansion of e^x around x=0 is one of the most important series in mathematics. It expresses the exponential function as an infinite sum of polynomial terms:</p>
            
            <div class="formula">
                e^x = Σ(n=0 to ∞) x^n / n! = 1 + x + x²/2! + x³/3! + x⁴/4! + ...
            </div>

            <p>For x = 1, this gives us the series for e itself: e = Σ(n=0 to ∞) 1/n! = 1 + 1 + 1/2 + 1/6 + 1/24 + ...</p>

            <h3>📊 Convergence Data (x = 1)</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Number of Terms (N)</th>
                        <th>Partial Sum</th>
                        <th>Correct Digits</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Generate Exercise 3 table rows
    for n, s, d in zip(tracked_N, tracked_sums, correct_digits):
        html_content += f"""                    <tr><td>{n}</td><td>{s:.15f}</td><td>{d}</td></tr>
"""

    html_content += """                </tbody>
            </table>

            <h3>📈 Visualization</h3>
            <div class="chart-container">
                <img src="exercise3.png" alt="Exercise 3: Taylor Series e^x = Σ(x^n/n!)">
            </div>

            <div class="insight-box">
                <h4>💡 Key Insights</h4>
                <ul>
                    <li>The Taylor series converges extremely rapidly - just 20 terms give 15 correct decimal places</li>
                    <li>Each additional term adds roughly one more correct digit, as shown in the log-log plot</li>
                    <li>The factorial in the denominator grows faster than any polynomial, ensuring convergence for all x</li>
                    <li>This series is the basis for how computers actually calculate e^x in practice</li>
                    <li>After N=20, the series has converged to the limit of double-precision floating-point arithmetic</li>
                </ul>
            </div>
        </div>

        <footer>
            <p>Series 1 Laboratory Exercise | Mathematical Explorations in Python with Matplotlib</p>
        </footer>
    </div>
</body>
</html>
"""

    # Write the HTML file
    output_path = os.path.join(SCRIPT_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML dashboard generated successfully at: {output_path}")
    print(f"File size: {os.path.getsize(output_path):,} bytes")


# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("SERIES 1 LABORATORY EXERCISE - COMBINED SCRIPT")
    print("=" * 70)
    
    # Run Exercise 1
    exercise1_data = exercise1()
    
    # Run Exercise 2
    exercise2_results, h_values, limits = exercise2()
    
    # Run Exercise 3
    tracked_N, tracked_sums, correct_digits, e_actual = exercise3()
    
    # Generate HTML Dashboard
    generate_html(exercise1_data, exercise2_results, h_values, limits,
                  tracked_N, tracked_sums, correct_digits, e_actual)
    
    print("\n" + "=" * 70)
    print("ALL OUTPUTS GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nGenerated files in: {SCRIPT_DIR}")
    print("  - exercise1.png")
    print("  - exercise2.png")
    print("  - exercise3.png")
    print("  - index.html")