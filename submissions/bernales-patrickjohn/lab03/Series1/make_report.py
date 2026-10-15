# create_ppt.py
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os

# Create presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Color scheme
DARK_BLUE = RGBColor(0x2D, 0x37, 0x48)
PURPLE = RGBColor(0x66, 0x7E, 0xEA)
LIGHT_BG = RGBColor(0xF7, 0xFA, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x38, 0xA1, 0x69)
RED = RGBColor(0xE5, 0x3E, 0x3E)


def add_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # Background
    bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = PURPLE
    bg.line.fill.background()

    # Title
    tb = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11.3), Inches(1.5))
    tf = tb.text_frame
    tf.text = title
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Subtitle
    tb2 = slide.shapes.add_textbox(Inches(1), Inches(4.2), Inches(11.3), Inches(1))
    tf2 = tb2.text_frame
    tf2.text = subtitle
    p2 = tf2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(24)
    p2.font.color.rgb = WHITE
    return slide


def add_content_slide(prs, title, bullets):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # Top bar
    bar = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.2))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PURPLE
    bar.line.fill.background()

    # Title
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12.3), Inches(0.9))
    tf = tb.text_frame
    tf.text = title
    p = tf.paragraphs[0]
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Body
    body = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(12), Inches(5.5))
    tf2 = body.text_frame
    tf2.word_wrap = True

    for i, (text, level) in enumerate(bullets):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        p.text = text
        p.level = level
        p.font.size = Pt(20) if level == 0 else Pt(16)
        p.font.color.rgb = DARK_BLUE
        p.space_after = Pt(10)
    return slide


def add_image_slide(prs, title, img_path, caption=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # Top bar
    bar = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.0))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PURPLE
    bar.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(12.3), Inches(0.8))
    tf = tb.text_frame
    tf.text = title
    p = tf.paragraphs[0]
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Add image if it exists
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(1.5), Inches(1.3), width=Inches(10))
    else:
        tb2 = slide.shapes.add_textbox(Inches(1.5), Inches(3), Inches(10), Inches(1))
        tf2 = tb2.text_frame
        tf2.text = f"[Image not found: {img_path}]"
        tf2.paragraphs[0].font.size = Pt(20)
        tf2.paragraphs[0].font.color.rgb = RED

    if caption:
        tb3 = slide.shapes.add_textbox(Inches(1), Inches(6.8), Inches(11.3), Inches(0.5))
        tf3 = tb3.text_frame
        tf3.text = caption
        p3 = tf3.paragraphs[0]
        p3.alignment = PP_ALIGN.CENTER
        p3.font.size = Pt(14)
        p3.font.italic = True
        p3.font.color.rgb = DARK_BLUE
    return slide


# ---------- BUILD SLIDES ----------

# Slide 1: Title
add_title_slide(prs,
    "Numerical Analysis of Series1",
    "Convergence Studies: e, Derivatives & Taylor Series")

# Slide 2: Overview
add_content_slide(prs, "Overview", [
    ("Three key mathematical concepts explored:", 0),
    ("1. Limit definition of e:  (1 + 1/n)^n → e", 1),
    ("2. Derivative approximation:  (a^h − 1)/h → ln(a)", 1),
    ("3. Taylor series expansion:  e^x = Σ (x^n / n!)", 1),
    ("", 0),
    ("Goals:", 0),
    ("• Implement each in Python", 1),
    ("• Analyze convergence behavior", 1),
    ("• Visualize results with Matplotlib histograms", 1),
])

# Slide 3: Exercise 1 - Concept
add_content_slide(prs, "Exercise 1: The Limit of e", [
    ("Formula:  (1 + 1/n)^n  as  n → ∞", 0),
    ("", 0),
    ("Progression of values:", 0),
    ("n=1   → 2.000000", 1),
    ("n=2   → 2.250000", 1),
    ("n=4   → 2.441406", 1),
    ("n=1000 → 2.716924", 1),
    ("n=10^6 → 2.718280", 1),
    ("", 0),
    ("Converges to Euler's number:  e ≈ 2.718281828...", 0),
])

# Slide 4: Exercise 1 - Result Image
add_image_slide(prs, "Exercise 1: Convergence Visualization",
    "series1_ex1.png",
    "Bar chart showing monotonic convergence of (1+1/n)^n toward e")

# Slide 5: Exercise 1 - Analysis
add_content_slide(prs, "Exercise 1: Key Findings", [
    ("Convergence is monotonic (increasing)", 0),
    ("Approaches e from below", 0),
    ("Error decreases as O(1/n)", 0),
    ("Reaches 6 decimal places by n ≈ 10^6", 0),
    ("", 0),
    ("Why it matters:", 0),
    ("• Foundation for compound interest calculations", 1),
    ("• Defines the natural exponential base e", 1),
    ("• Demonstrates limit-based numerical convergence", 1),
])

# Slide 6: Exercise 2 - Concept
add_content_slide(prs, "Exercise 2: Derivative Approximation", [
    ("Formula:  (a^h − 1) / h  as  h → 0", 0),
    ("", 0),
    ("Approximates derivative of a^x at x = 0:", 0),
    ("d/dx(a^x) at x=0 = ln(a)", 1),
    ("", 0),
    ("Convergence values:", 0),
    ("a = 2  →  ln(2) ≈ 0.6931", 1),
    ("a = e  →  ln(e) = 1.0000", 1),
    ("a = 3  →  ln(3) ≈ 1.0986", 1),
    ("", 0),
    ("Tolerance target: ×10⁻⁶", 0),
])

# Slide 7: Exercise 2 - Result Image
add_image_slide(prs, "Exercise 2: Convergence Visualization",
    "series1_ex2.png",
    "Grouped bar chart showing (a^h − 1)/h converging to ln(a) as h shrinks")

# Slide 8: Exercise 2 - Analysis
add_content_slide(prs, "Exercise 2: Key Findings", [
    ("As h → 0, values converge to ln(a)", 0),
    ("First-order finite difference method", 0),
    ("Error scales as O(h)", 0),
    ("For base e, result is exactly 1", 0),
    ("", 0),
    ("Why base e is special:", 0),
    ("• Only base where derivative of a^x at 0 equals 1", 1),
    ("• This property makes e the 'natural' base", 1),
    ("• Foundation of calculus and exponential growth", 1),
])

# Slide 9: Exercise 3 - Concept
add_content_slide(prs, "Exercise 3: Taylor Series for e^x", [
    ("Formula:  e^x = Σ (x^n / n!)  for n = 0 to ∞", 0),
    ("", 0),
    ("Expanded form:", 0),
    ("e^x = 1 + x + x²/2! + x³/3! + x⁴/4! + ...", 1),
    ("", 0),
    ("Implementation details:", 0),
    ("• Up to 10,000 terms supported", 1),
    ("• Tolerance: 10⁻⁶ relative error", 1),
    ("• Tested for x from −5 to +5", 1),
])

# Slide 10: Exercise 3 - Result Image
add_image_slide(prs, "Exercise 3: Convergence Visualization",
    "series1_ex3.png",
    "Four-panel plot: convergence, terms needed, approximations, distribution")

# Slide 11: Exercise 3 - Analysis
add_content_slide(prs, "Exercise 3: Key Findings", [
    ("Convergence depends strongly on |x|", 0),
    ("For |x| ≤ 5: 15–50 terms typically needed", 0),
    ("For x near 0: as few as 5 terms suffice", 0),
    ("For large |x|: more terms required", 0),
    ("", 0),
    ("Observations:", 0),
    ("• Factorial growth in denominator ensures fast convergence", 1),
    ("• Accuracy improves dramatically with each added term", 1),
    ("• Series diverges in term count but converges in value", 1),
])

# Slide 12: Summary Comparison
add_content_slide(prs, "Summary: Comparison of Methods", [
    ("Method 1: (1 + 1/n)^n", 0),
    ("→ Computes e  |  Convergence: O(1/n)", 1),
    ("", 0),
    ("Method 2: (a^h − 1)/h", 0),
    ("→ Computes ln(a)  |  Convergence: O(h)", 1),
    ("", 0),
    ("Method 3: Σ (x^n / n!)", 0),
    ("→ Computes e^x  |  Convergence: factorial (fastest)", 1),
    ("", 0),
    ("All three demonstrate numerical techniques for fundamental constants.", 0),
])

# Slide 13: Applications
add_content_slide(prs, "Real-World Applications", [
    ("Scientific Computing", 0),
    ("• Numerical integration and differentiation", 1),
    ("", 0),
    ("Financial Mathematics", 0),
    ("• Compound interest (continuous vs periodic)", 1),
    ("", 0),
    ("Machine Learning", 0),
    ("• Softmax and sigmoid activation functions", 1),
    ("", 0),
    ("Physics & Engineering", 0),
    ("• Radioactive decay, RC circuits, population growth", 1),
])

# Slide 14: Key Takeaways
add_content_slide(prs, "Key Takeaways", [
    ("✔  Different numerical approaches reveal the same fundamental constants", 0),
    ("", 0),
    ("✔  Convergence rate depends on the method used", 0),
    ("", 0),
    ("✔  Taylor series offers fastest convergence for e^x", 0),
    ("", 0),
    ("✔  Python + Matplotlib provides an effective platform for numerical visualization", 0),
    ("", 0),
    ("✔  Understanding convergence is essential for reliable numerical computing", 0),
])

# Slide 15: Thank You
add_title_slide(prs, "Thank You", "Questions?")

# Save
output_file = "Series1_Presentation.pptx"
prs.save(output_file)
print(f"✅ Presentation saved as '{output_file}'")
print(f"   Total slides: {len(prs.slides)}")
print(f"   Location: {os.path.abspath(output_file)}")