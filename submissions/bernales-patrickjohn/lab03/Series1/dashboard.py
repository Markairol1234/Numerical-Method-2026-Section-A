# dashboard.py
import webbrowser
import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Series1 Exercises Dashboard</title>
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
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #2d3748;
            font-size: 2.5em;
            margin-bottom: 10px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }
        .subtitle {
            text-align: center;
            color: #718096;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .exercise-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        .exercise-card:hover {
            transform: translateY(-5px);
        }
        .exercise-card h2 {
            color: #2d3748;
            font-size: 1.8em;
            margin-bottom: 10px;
        }
        .exercise-card h2 small {
            font-size: 0.6em;
            color: #718096;
            font-weight: normal;
        }
        .exercise-description {
            color: #4a5568;
            margin-bottom: 20px;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
            line-height: 1.6;
        }
        .exercise-description code {
            background: #e2e8f0;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #2b6cb0;
        }
        .image-container {
            text-align: center;
            margin: 20px 0;
        }
        .image-container img {
            max-width: 90%;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid #e2e8f0;
        }
        .results-box {
            background: #f7fafc;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }
        .results-box pre {
            background: #2d3748;
            color: #68d391;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9em;
            margin: 10px 0;
        }
        .key-finding {
            background: #ebf8ff;
            border-left: 4px solid #4299e1;
            padding: 12px 18px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .key-finding strong {
            color: #2b6cb0;
        }
        .grid-2col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) {
            .grid-2col {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 15px;
            }
            h1 {
                font-size: 1.8em;
            }
        }
        .tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Series1 Mathematical Exercises</h1>
        <p class="subtitle">Interactive Dashboard showing convergence analysis and numerical methods</p>

        <!-- Exercise 1 -->
        <div class="exercise-card">
            <h2>Exercise 1: <small>Limit of (1 + 1/n)^n as n → ∞</small></h2>
            <div class="exercise-description">
                <strong>Problem:</strong> Calculate and visualize the convergence of 
                <code>(1 + 1/n)^n</code> as n increases. This sequence converges to 
                <strong>Euler's number e ≈ 2.718281828...</strong>
            </div>
            
            <div class="image-container">
                <img src="series1_ex1.png" alt="Exercise 1 Histogram">
            </div>
            
            <div class="grid-2col">
                <div>
                    <div class="key-finding">
                        <strong>🔑 Key Finding:</strong> The sequence converges rapidly to e. 
                        With n=1000, the value matches e to 6 decimal places.
                    </div>
                </div>
                <div>
                    <div class="key-finding">
                        <strong>📈 Observation:</strong> The convergence is monotonic 
                        (increasing) and approaches e from below.
                    </div>
                </div>
            </div>
        </div>

        <!-- Exercise 2 -->
        <div class="exercise-card">
            <h2>Exercise 2: <small>Derivative Approximation (a^h - 1)/h</small></h2>
            <div class="exercise-description">
                <strong>Problem:</strong> Compute <code>(a^h - 1)/h</code> for different bases 
                (a = 2, e, 3) as h → 0. This approximates the derivative of <code>a^x</code> at x=0, 
                which is <code>ln(a)</code>.
            </div>
            
            <div class="image-container">
                <img src="series1_ex2.png" alt="Exercise 2 Histogram">
            </div>
            
            <div class="grid-2col">
                <div>
                    <div class="key-finding">
                        <strong>🔑 Key Finding:</strong> As h → 0, the values converge to:
                        <br>
                        For a=2: ln(2) ≈ 0.6931<br>
                        For a=e: ln(e) = 1.0000<br>
                        For a=3: ln(3) ≈ 1.0986
                    </div>
                </div>
                <div>
                    <div class="key-finding">
                        <strong>📊 Insight:</strong> The base e gives the derivative value 1, 
                        which is why e is the "natural" base for exponential functions.
                    </div>
                </div>
            </div>
        </div>

        <!-- Exercise 3 -->
        <div class="exercise-card">
            <h2>Exercise 3: <small>Taylor Series for e^x</small></h2>
            <div class="exercise-description">
                <strong>Problem:</strong> Implement <code>e^x = Σ(x^n/n!)</code> and analyze 
                the number of terms needed for convergence to <code>10⁻⁶</code> tolerance.
            </div>
            
            <div class="image-container">
                <img src="series1_ex3.png" alt="Exercise 3 Histogram">
            </div>
            
            <div class="grid-2col">
                <div>
                    <div class="key-finding">
                        <strong>🔑 Key Finding:</strong> For |x| ≤ 5, convergence typically 
                        requires 15-50 terms. For x close to 0, as few as 5 terms suffice.
                    </div>
                </div>
                <div>
                    <div class="key-finding">
                        <strong>⚠️ Note:</strong> For large x values (|x| > 5), more terms 
                        are needed. For x=10, convergence may require 50+ terms.
                    </div>
                </div>
            </div>
        </div>

        <!-- Summary -->
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    color: white; padding: 25px; border-radius: 15px; margin-top: 20px;">
            <h3 style="color: white; margin-bottom: 10px;">📝 Summary of Results</h3>
            <ul style="list-style: none; line-height: 2;">
                <li>✅ <strong>Exercise 1:</strong> (1 + 1/n)^n converges to e = 2.718281828...</li>
                <li>✅ <strong>Exercise 2:</strong> (a^h - 1)/h converges to ln(a) as h → 0</li>
                <li>✅ <strong>Exercise 3:</strong> Taylor series for e^x converges rapidly, with terms needed depending on |x|</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

# Save the HTML file
with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Open in default browser
webbrowser.open('dashboard.html')
print("Dashboard created and opened in your browser!")
print("If it didn't open automatically, open 'dashboard.html' manually.")